from app.extensions import db
from datetime import datetime
import uuid

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informações do documento
    document_type = db.Column(db.String(50), nullable=False)  # cnh_nautica, registro_embarcacao, etc.
    document_number = db.Column(db.String(50))
    document_name = db.Column(db.String(100), nullable=False)
    
    # Arquivo
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Tamanho em bytes
    file_type = db.Column(db.String(50))  # MIME type
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, expired
    is_verified = db.Column(db.Boolean, default=False)
    
    # Datas
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    
    # Informações adicionais
    description = db.Column(db.Text)
    admin_notes = db.Column(db.Text)  # Notas do administrador
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_expired(self):
        """Verifica se o documento expirou"""
        if not self.expiry_date:
            return False
        return datetime.utcnow().date() > self.expiry_date
    
    @property
    def days_until_expiry(self):
        """Retorna os dias até a expiração"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - datetime.utcnow().date()
        return delta.days
    
    @property
    def status_color(self):
        """Retorna a cor do status para exibição"""
        if self.status == 'approved':
            return 'success'
        elif self.status == 'rejected':
            return 'danger'
        elif self.status == 'expired':
            return 'warning'
        else:
            return 'secondary'
    
    def approve(self, admin_notes=None):
        """Aprova o documento"""
        self.status = 'approved'
        self.is_verified = True
        if admin_notes:
            self.admin_notes = admin_notes
    
    def reject(self, admin_notes=None):
        """Rejeita o documento"""
        self.status = 'rejected'
        self.is_verified = True
        if admin_notes:
            self.admin_notes = admin_notes
    
    def mark_as_expired(self):
        """Marca o documento como expirado"""
        self.status = 'expired'
    
    def __repr__(self):
        return f'<Document {self.document_type} - {self.user_id}>' 