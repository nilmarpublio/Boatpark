from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import Vessel, User
from app.extensions import db
from datetime import datetime
import json

bp = Blueprint('vessels', __name__, url_prefix='/vessels')

@bp.route('/')
@login_required
def index():
    """Lista de embarcações do usuário"""
    vessels = Vessel.query.filter_by(user_id=current_user.id).all()
    return render_template('vessels/index.html', vessels=vessels)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """Nova embarcação"""
    if request.method == 'POST':
        # Processar fotos
        photos_text = request.form.get('photos', '')
        photos = [url.strip() for url in photos_text.split('\n') if url.strip()]
        
        vessel = Vessel(
            user_id=current_user.id,
            name=request.form['name'],
            type=request.form['type'],
            brand=request.form.get('brand'),
            model=request.form.get('model'),
            year=int(request.form['year']) if request.form['year'] else None,
            length=float(request.form['length']) if request.form['length'] else None,
            width=float(request.form['width']) if request.form['width'] else None,
            height=float(request.form['height']) if request.form['height'] else None,
            draft=float(request.form['draft']) if request.form['draft'] else None,
            engine_type=request.form.get('engine_type'),
            engine_power=request.form.get('engine_power'),
            fuel_type=request.form.get('fuel_type'),
            fuel_capacity=float(request.form['fuel_capacity']) if request.form['fuel_capacity'] else None,
            registration_number=request.form.get('registration_number'),
            registration_expiry=datetime.strptime(request.form['registration_expiry'], '%Y-%m-%d').date() if request.form['registration_expiry'] else None,
            insurance_number=request.form.get('insurance_number'),
            insurance_expiry=datetime.strptime(request.form['insurance_expiry'], '%Y-%m-%d').date() if request.form['insurance_expiry'] else None,
            description=request.form.get('description'),
            notes=request.form.get('notes'),
            photos=json.dumps(photos)
        )
        
        db.session.add(vessel)
        db.session.commit()
        
        flash('Embarcação cadastrada com sucesso!', 'success')
        return redirect(url_for('vessels.index'))
    
    return render_template('vessels/form.html', vessel=None)

@bp.route('/<int:vessel_id>')
@login_required
def detail(vessel_id):
    """Detalhes da embarcação"""
    vessel = Vessel.query.filter_by(id=vessel_id, user_id=current_user.id).first_or_404()
    return render_template('vessels/detail.html', vessel=vessel)

@bp.route('/<int:vessel_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(vessel_id):
    """Editar embarcação"""
    vessel = Vessel.query.filter_by(id=vessel_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        # Processar fotos
        photos_text = request.form.get('photos', '')
        photos = [url.strip() for url in photos_text.split('\n') if url.strip()]
        
        vessel.name = request.form['name']
        vessel.type = request.form['type']
        vessel.brand = request.form.get('brand')
        vessel.model = request.form.get('model')
        vessel.year = int(request.form['year']) if request.form['year'] else None
        vessel.length = float(request.form['length']) if request.form['length'] else None
        vessel.width = float(request.form['width']) if request.form['width'] else None
        vessel.height = float(request.form['height']) if request.form['height'] else None
        vessel.draft = float(request.form['draft']) if request.form['draft'] else None
        vessel.engine_type = request.form.get('engine_type')
        vessel.engine_power = request.form.get('engine_power')
        vessel.fuel_type = request.form.get('fuel_type')
        vessel.fuel_capacity = float(request.form['fuel_capacity']) if request.form['fuel_capacity'] else None
        vessel.registration_number = request.form.get('registration_number')
        vessel.registration_expiry = datetime.strptime(request.form['registration_expiry'], '%Y-%m-%d').date() if request.form['registration_expiry'] else None
        vessel.insurance_number = request.form.get('insurance_number')
        vessel.insurance_expiry = datetime.strptime(request.form['insurance_expiry'], '%Y-%m-%d').date() if request.form['insurance_expiry'] else None
        vessel.description = request.form.get('description')
        vessel.notes = request.form.get('notes')
        vessel.photos = json.dumps(photos)
        
        db.session.commit()
        
        flash('Embarcação atualizada com sucesso!', 'success')
        return redirect(url_for('vessels.detail', vessel_id=vessel.id))
    
    return render_template('vessels/form.html', vessel=vessel)

@bp.route('/<int:vessel_id>/delete', methods=['POST'])
@login_required
def delete(vessel_id):
    """Excluir embarcação"""
    vessel = Vessel.query.filter_by(id=vessel_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(vessel)
    db.session.commit()
    
    flash('Embarcação excluída com sucesso!', 'success')
    return redirect(url_for('vessels.index')) 