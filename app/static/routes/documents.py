from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Document, User
from app.extensions import db
from datetime import datetime

bp = Blueprint('documents', __name__, url_prefix='/documents')

@bp.route('/')
@login_required
def index():
    """Lista de documentos do usuário"""
    documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.created_at.desc()).all()
    return render_template('documents/index.html', documents=documents)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Novo documento"""
    if request.method == 'POST':
        # Criar documento no banco
        document = Document(
            user_id=current_user.id,
            document_type=request.form['type'],
            document_number=request.form.get('number'),
            document_name=request.form['title'],
            file_path=request.form.get('file_url', ''),
            file_size=0,
            file_type='url',
            issue_date=datetime.strptime(request.form['issue_date'], '%Y-%m-%d').date() if request.form['issue_date'] else None,
            expiry_date=datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date() if request.form['expiry_date'] else None,
            description=request.form.get('description'),
            status=request.form.get('status', 'Ativo')
        )
        
        db.session.add(document)
        db.session.commit()
        
        flash('Documento cadastrado com sucesso!', 'success')
        return redirect(url_for('documents.index'))
    
    return render_template('documents/form.html', document=None)

@bp.route('/<int:document_id>')
@login_required
def detail(document_id):
    """Detalhes do documento"""
    document = Document.query.filter_by(id=document_id, user_id=current_user.id).first_or_404()
    return render_template('documents/detail.html', document=document)

@bp.route('/<int:document_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(document_id):
    """Editar documento"""
    document = Document.query.filter_by(id=document_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        document.document_type = request.form['type']
        document.document_number = request.form.get('number')
        document.document_name = request.form['title']
        document.issue_date = datetime.strptime(request.form['issue_date'], '%Y-%m-%d').date() if request.form['issue_date'] else None
        document.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date() if request.form['expiry_date'] else None
        document.description = request.form.get('description')
        document.file_path = request.form.get('file_url', '')
        document.status = request.form.get('status', 'Ativo')
        
        db.session.commit()
        
        flash('Documento atualizado com sucesso!', 'success')
        return redirect(url_for('documents.detail', document_id=document.id))
    
    return render_template('documents/form.html', document=document)

@bp.route('/<int:document_id>/delete', methods=['POST'])
@login_required
def delete(document_id):
    """Excluir documento"""
    document = Document.query.filter_by(id=document_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(document)
    db.session.commit()
    
    flash('Documento excluído com sucesso!', 'success')
    return redirect(url_for('documents.index'))

 