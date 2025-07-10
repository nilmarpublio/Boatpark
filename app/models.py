# Importar todos os modelos
from app.models.user import User
from app.models.marina import Marina
from app.models.berth import Berth
from app.models.subscription_plan import SubscriptionPlan
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.document import Document
from app.models.notification import Notification

# Manter compatibilidade com código existente
__all__ = [
    'User',
    'Marina', 
    'Berth',
    'SubscriptionPlan',
    'Subscription',
    'Payment',
    'Document',
    'Notification'
]
