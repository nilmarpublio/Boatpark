# Importar todos os modelos
from .user import User
from .marina import Marina
from .berth import Berth
from .berth_occupancy_history import BerthOccupancyHistory
from .subscription_plan import SubscriptionPlan
from .subscription import Subscription
from .payment import Payment
from .document import Document
from .notification import Notification
from .marina_service import MarinaService, UserServiceSelection
from .service_request import ServiceRequest
from .system_config import SystemConfig
from .audit_log import AuditLog
from .vessel import Vessel

__all__ = [
    'User',
    'Marina', 
    'Berth',
    'BerthOccupancyHistory',
    'SubscriptionPlan',
    'Subscription',
    'Payment',
    'Document',
    'Notification',
    'MarinaService',
    'UserServiceSelection',
    'ServiceRequest',
    'SystemConfig',
    'AuditLog',
    'Vessel'
] 