from app.extensions import db
from datetime import datetime
import uuid
import json

class Marina(db.Model):
    __tablename__ = 'marinas'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zip_code = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    
    # Coordenadas geográficas para mapa
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    map_zoom = db.Column(db.Integer, default=15)  # Zoom level para o mapa
    
    # Configurações
    is_active = db.Column(db.Boolean, default=True)
    total_berths = db.Column(db.Integer, default=0)  # Número total de vagas configurado
    max_berths = db.Column(db.Integer, default=0)    # Vagas criadas no sistema
    available_berths = db.Column(db.Integer, default=0)  # Vagas disponíveis
    
    # Horários de funcionamento (JSON)
    opening_hours = db.Column(db.Text)  # JSON string com horários
    services = db.Column(db.Text)  # Lista de serviços oferecidos
    
    # Galeria de fotos (JSON array de URLs)
    photos = db.Column(db.Text)  # JSON array de URLs das fotos
    
    # Imagens principais
    logo_url = db.Column(db.String(200))
    banner_url = db.Column(db.String(200))
    cover_photo_url = db.Column(db.String(200))
    
    # Informações adicionais
    amenities = db.Column(db.Text)  # JSON array de comodidades
    rules = db.Column(db.Text)  # Regras da marina
    contact_person = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    berths = db.relationship('Berth', backref='marina', lazy=True)
    
    @property
    def occupancy_rate(self):
        """Taxa de ocupação da marina"""
        max_berths = self.max_berths or 0
        available_berths = self.available_berths or 0
        
        if max_berths == 0:
            return 0
        occupied = max_berths - available_berths
        return (occupied / max_berths) * 100
    
    @property
    def full_address(self):
        """Endereço completo da marina"""
        return f"{self.address}, {self.city} - {self.state}"
    
    @property
    def photos_list(self):
        """Retorna a lista de fotos como array Python"""
        if self.photos:
            try:
                return json.loads(self.photos)
            except:
                return []
        return []
    
    @property
    def opening_hours_dict(self):
        """Retorna os horários como dicionário Python"""
        if self.opening_hours:
            try:
                return json.loads(self.opening_hours)
            except:
                return {}
        return {}
    
    @property
    def services_list(self):
        """Retorna a lista de serviços como array Python"""
        if self.services:
            try:
                return json.loads(self.services)
            except:
                return []
        return []
    
    @property
    def amenities_list(self):
        """Retorna a lista de comodidades como array Python"""
        if self.amenities:
            try:
                return json.loads(self.amenities)
            except:
                return []
        return []
    
    @property
    def berth_types_summary(self):
        """Resumo dos tipos de vagas disponíveis"""
        types = {}
        for berth in self.berths:
            berth_type = berth.berth_type
            if berth_type not in types:
                types[berth_type] = {'total': 0, 'available': 0}
            types[berth_type]['total'] += 1
            if berth.is_available:
                types[berth_type]['available'] += 1
        return types
    
    def update_berth_count(self):
        """Atualiza a contagem de vagas disponíveis"""
        berths_list = list(self.berths) if self.berths else []
        created_berths = len(berths_list)
        available_berths = len([b for b in berths_list if b.is_available])
        
        self.max_berths = created_berths
        self.available_berths = available_berths
    
    def get_berth_status_summary(self):
        """Retorna resumo do status das vagas"""
        berths_list = list(self.berths) if self.berths else []
        summary = {
            'total_configured': self.total_berths,
            'total_created': len(berths_list),
            'available': len([b for b in berths_list if b.status == 'available']),
            'occupied': len([b for b in berths_list if b.status == 'occupied']),
            'maintenance': len([b for b in berths_list if b.status == 'maintenance']),
            'reserved': len([b for b in berths_list if b.status == 'reserved'])
        }
        return summary
    
    def add_photo(self, photo_url):
        """Adiciona uma foto à galeria"""
        photos = self.photos_list
        photos.append(photo_url)
        self.photos = json.dumps(photos)
    
    def remove_photo(self, photo_url):
        """Remove uma foto da galeria"""
        photos = self.photos_list
        if photo_url in photos:
            photos.remove(photo_url)
            self.photos = json.dumps(photos)
    
    def __repr__(self):
        return f'<Marina {self.name}>' 