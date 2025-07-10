from app.extensions import db
from datetime import datetime
import uuid

class Vessel(db.Model):
    __tablename__ = 'vessels'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Informações básicas da embarcação
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # Iate, Lancha, Veleiro, etc.
    brand = db.Column(db.String(100))  # Marca/Fabricante
    model = db.Column(db.String(100))  # Modelo
    year = db.Column(db.Integer)  # Ano de fabricação
    
    # Dimensões
    length = db.Column(db.Float)  # Comprimento em metros
    width = db.Column(db.Float)   # Largura em metros
    height = db.Column(db.Float)  # Altura em metros
    draft = db.Column(db.Float)   # Calado em metros
    
    # Características técnicas
    engine_type = db.Column(db.String(50))  # Motor interno, externo, etc.
    engine_power = db.Column(db.String(50))  # Potência do motor
    fuel_type = db.Column(db.String(30))  # Tipo de combustível
    fuel_capacity = db.Column(db.Float)  # Capacidade de combustível
    
    # Documentação
    registration_number = db.Column(db.String(50))  # Número de registro
    registration_expiry = db.Column(db.Date)  # Data de expiração do registro
    insurance_number = db.Column(db.String(50))  # Número do seguro
    insurance_expiry = db.Column(db.Date)  # Data de expiração do seguro
    
    # Fotos da embarcação (JSON array de URLs)
    photos = db.Column(db.Text)  # JSON array de URLs das fotos
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')  # active, maintenance, sold, etc.
    
    # Informações adicionais
    description = db.Column(db.Text)
    notes = db.Column(db.Text)  # Notas do usuário
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    user = db.relationship('User', backref='vessels')
    
    @property
    def full_name(self):
        """Nome completo da embarcação"""
        if self.brand and self.model:
            return f"{self.name} - {self.brand} {self.model}"
        return self.name
    
    @property
    def dimensions_str(self):
        """Dimensões formatadas"""
        if self.length and self.width:
            return f"{self.length}m x {self.width}m"
        return "Não informado"
    
    @property
    def is_registration_expired(self):
        """Verifica se o registro expirou"""
        if not self.registration_expiry:
            return False
        return datetime.utcnow().date() > self.registration_expiry
    
    @property
    def is_insurance_expired(self):
        """Verifica se o seguro expirou"""
        if not self.insurance_expiry:
            return False
        return datetime.utcnow().date() > self.insurance_expiry
    
    @property
    def days_until_registration_expiry(self):
        """Dias até a expiração do registro"""
        if not self.registration_expiry:
            return None
        delta = self.registration_expiry - datetime.utcnow().date()
        return delta.days
    
    @property
    def days_until_insurance_expiry(self):
        """Dias até a expiração do seguro"""
        if not self.insurance_expiry:
            return None
        delta = self.insurance_expiry - datetime.utcnow().date()
        return delta.days
    
    @property
    def photos_list(self):
        """Retorna a lista de fotos como array Python"""
        import json
        if self.photos:
            try:
                return json.loads(self.photos)
            except:
                return []
        return []
    
    def add_photo(self, photo_url):
        """Adiciona uma foto à embarcação"""
        import json
        photos = self.photos_list
        photos.append(photo_url)
        self.photos = json.dumps(photos)
    
    def remove_photo(self, photo_url):
        """Remove uma foto da embarcação"""
        import json
        photos = self.photos_list
        if photo_url in photos:
            photos.remove(photo_url)
            self.photos = json.dumps(photos)
    
    def __repr__(self):
        return f'<Vessel {self.name} - {self.user_id}>' 