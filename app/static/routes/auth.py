from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.extensions import db
from app.services.email_service import EmailService
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import secrets
import uuid

bp = Blueprint('auth', __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        if not email or not password:
            flash("Por favor, preencha todos os campos.", "error")
            return render_template("login.html")
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            # Verificação de email temporariamente desabilitada
            # if not user.is_admin and not user.email_verified:
            #     flash("Por favor, verifique seu email antes de fazer login. Verifique sua caixa de entrada ou solicite um novo email de verificação.", "warning")
            #     return render_template("login.html")
            
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard.index"))
        else:
            flash("Email ou senha incorretos.", "error")
    
    return render_template("login.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("auth.login"))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        
        # Validações
        if not email or not password or not confirm_password:
            flash("Por favor, preencha todos os campos obrigatórios.", "error")
            return render_template("register.html")
        
        if not first_name or not last_name:
            flash("Por favor, preencha seu nome completo.", "error")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return render_template("register.html")
        
        if len(password) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "error")
            return render_template("register.html")
        
        # Verificar se o usuário já existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Este email já está cadastrado.", "error")
            return render_template("register.html")
        
        # Gerar token de verificação
        verification_token = secrets.token_urlsafe(32)
        
        # Criar novo usuário
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=False,
            email_verified=True,  # Temporariamente marcado como verificado
            email_verification_token=verification_token
        )
        new_user.password = password  # Usar o setter para hash da senha
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Email de verificação temporariamente desabilitado
            # try:
            #     email_service = EmailService()
            #     verification_url = url_for('auth.verify_email', token=verification_token, _external=True)
            #     email_service.send_verification_email(new_user, verification_url)
            #     flash("Usuário cadastrado com sucesso! Verifique seu email para ativar sua conta.", "success")
            # except Exception as e:
            #     current_app.logger.error(f"Erro ao enviar email de verificação: {e}")
            #     flash("Usuário cadastrado com sucesso! Mas houve um problema ao enviar o email de verificação. Entre em contato com o suporte.", "warning")
            flash("Usuário cadastrado com sucesso! Você já pode fazer login.", "success")
            
            return redirect(url_for("auth.login"))
        except Exception as e:
            db.session.rollback()
            flash("Erro ao cadastrar usuário. Tente novamente.", "error")
    
    return render_template("register.html")

@bp.route("/verify-email/<token>")
def verify_email(token):
    """Verifica o email do usuário usando o token"""
    user = User.query.filter_by(email_verification_token=token).first()
    
    if not user:
        flash("Token de verificação inválido ou expirado.", "error")
        return redirect(url_for("auth.login"))
    
    # Verificar se o token não expirou (24 horas)
    if user.created_at < datetime.utcnow() - timedelta(hours=24):
        flash("Token de verificação expirado. Solicite um novo email de verificação.", "error")
        return redirect(url_for("auth.login"))
    
    # Marcar email como verificado
    user.email_verified = True
    user.email_verification_token = None
    db.session.commit()
    
    flash("Email verificado com sucesso! Agora você pode fazer login.", "success")
    return redirect(url_for("auth.login"))

@bp.route("/resend-verification", methods=["GET", "POST"])
def resend_verification():
    """Reenvia o email de verificação"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        
        if not email:
            flash("Por favor, informe seu email.", "error")
            return render_template("resend_verification.html")
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash("Email não encontrado.", "error")
            return render_template("resend_verification.html")
        
        if user.email_verified:
            flash("Este email já foi verificado.", "info")
            return redirect(url_for("auth.login"))
        
        # Gerar novo token
        verification_token = secrets.token_urlsafe(32)
        user.email_verification_token = verification_token
        user.created_at = datetime.utcnow()  # Reset do tempo de expiração
        db.session.commit()
        
        # Email de verificação temporariamente desabilitado
        # try:
        #     email_service = EmailService()
        #     verification_url = url_for('auth.verify_email', token=verification_token, _external=True)
        #     email_service.send_verification_email(user, verification_url)
        #     flash("Email de verificação reenviado com sucesso! Verifique sua caixa de entrada.", "success")
        # except Exception as e:
        #     current_app.logger.error(f"Erro ao reenviar email de verificação: {e}")
        #     flash("Erro ao reenviar email de verificação. Tente novamente mais tarde.", "error")
        flash("Email de verificação temporariamente desabilitado. Entre em contato com o suporte.", "info")
        
        return redirect(url_for("auth.login"))
    
    return render_template("resend_verification.html")

@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Solicita redefinição de senha"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        
        if not email:
            flash("Por favor, informe seu email.", "error")
            return render_template("forgot_password.html")
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Gerar token de reset
            reset_token = secrets.token_urlsafe(32)
            user.reset_password_token = reset_token
            user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hora de validade
            db.session.commit()
            
            # Email de reset temporariamente desabilitado
            # try:
            #     email_service = EmailService()
            #     reset_url = url_for('auth.reset_password', token=reset_token, _external=True)
            #     email_service.send_password_reset_email(user, reset_url)
            #     flash("Email de redefinição de senha enviado! Verifique sua caixa de entrada.", "success")
            # except Exception as e:
            #     current_app.logger.error(f"Erro ao enviar email de reset: {e}")
            #     flash("Erro ao enviar email de redefinição. Tente novamente mais tarde.", "error")
            flash("Redefinição de senha temporariamente desabilitada. Entre em contato com o suporte.", "info")
        else:
            # Por segurança, não informar se o email existe ou não
            flash("Se o email estiver cadastrado, você receberá as instruções de redefinição.", "info")
        
        return redirect(url_for("auth.login"))
    
    return render_template("forgot_password.html")

@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Redefine a senha usando o token"""
    user = User.query.filter_by(reset_password_token=token).first()
    
    if not user:
        flash("Token de redefinição inválido ou expirado.", "error")
        return redirect(url_for("auth.login"))
    
    # Verificar se o token não expirou
    if user.reset_password_expires and user.reset_password_expires < datetime.utcnow():
        flash("Token de redefinição expirado. Solicite um novo.", "error")
        return redirect(url_for("auth.forgot_password"))
    
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if not password or not confirm_password:
            flash("Por favor, preencha todos os campos.", "error")
            return render_template("reset_password.html", token=token)
        
        if password != confirm_password:
            flash("As senhas não coincidem.", "error")
            return render_template("reset_password.html", token=token)
        
        if len(password) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "error")
            return render_template("reset_password.html", token=token)
        
        # Atualizar senha
        user.password_hash = generate_password_hash(password)
        user.reset_password_token = None
        user.reset_password_expires = None
        db.session.commit()
        
        flash("Senha redefinida com sucesso! Faça login com sua nova senha.", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("reset_password.html", token=token)
