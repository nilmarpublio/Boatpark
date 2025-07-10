#!/usr/bin/env python3
"""
Script para inicializar o banco de dados com dados de exemplo
"""

from app import create_app, db
from app.models import MarinaService, ServiceRequest, Subscription, SubscriptionPlan, User, Marina, Berth, Payment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Criar dados de exemplo para o sistema"""
    app = create_app()
    
    with app.app_context():
        # Limpar dados existentes (exceto admin)
        print("Limpando dados existentes...")
        ServiceRequest.query.delete()
        MarinaService.query.delete()
        Berth.query.delete()
        Marina.query.delete()
        SubscriptionPlan.query.delete()
        User.query.filter(User.is_admin == False).delete()
        
        # Manter apenas o usuário admin
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("Criando usuário administrador...")
            admin_user = User(
                first_name='Administrador',
                last_name='Sistema',
                email='admin@boathouse.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                is_active=True,
                phone='(11) 99999-9999',
                cpf='123.456.789-00'
            )
            db.session.add(admin_user)
            db.session.commit()
        
        # Criar usuários de exemplo
        print("Criando usuários de exemplo...")
        users = []
        user_names = [
            ('João', 'Silva'),
            ('Maria', 'Santos'),
            ('Pedro', 'Oliveira'),
            ('Ana', 'Costa'),
            ('Carlos', 'Ferreira')
        ]
        for i, (first_name, last_name) in enumerate(user_names):
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=f'usuario{i+1}@example.com',
                password_hash=generate_password_hash('123456'),
                is_admin=False,
                is_active=True,
                phone=f'(11) 99999-{1000+i:04d}',
                cpf=f'123.456.789-{i+1:02d}'
            )
            users.append(user)
            db.session.add(user)
        
        # Criar marinas
        print("Criando marinas...")
        marinas = []
        marina_data = [
            {
                'name': 'Marina Santos',
                'description': 'Marina moderna no porto de Santos',
                'address': 'Av. Beira Mar, 1000',
                'city': 'Santos',
                'state': 'SP',
                'zip_code': '11000-000',
                'phone': '(13) 3333-3333',
                'email': 'contato@marinasantos.com',
                'website': 'https://marinasantos.com'
            },
            {
                'name': 'Marina Angra',
                'description': 'Marina exclusiva em Angra dos Reis',
                'address': 'Rua do Porto, 500',
                'city': 'Angra dos Reis',
                'state': 'RJ',
                'zip_code': '23900-000',
                'phone': '(24) 4444-4444',
                'email': 'info@marinaangra.com',
                'website': 'https://marinaangra.com'
            },
            {
                'name': 'Marina Paraty',
                'description': 'Marina histórica em Paraty',
                'address': 'Rua da Praia, 200',
                'city': 'Paraty',
                'state': 'RJ',
                'zip_code': '23970-000',
                'phone': '(24) 5555-5555',
                'email': 'contato@marinaparaty.com',
                'website': 'https://marinaparaty.com'
            }
        ]
        
        for data in marina_data:
            marina = Marina(**data)
            marinas.append(marina)
            db.session.add(marina)
        
        db.session.commit()
        
        # Criar planos de assinatura
        print("Criando planos de assinatura...")
        plans = []
        plan_data = [
            {
                'name': 'teste',
                'display_name': 'Plano Teste',
                'description': 'Plano gratuito para teste do sistema. Apenas navegação, sem gravações.',
                'monthly_price': 0.00,
                'yearly_price': 0.00,
                'max_berths': 0,
                'max_services_per_month': 0,
                'max_documents': 0,
                'can_create_services': False,
                'can_upload_documents': False,
                'can_make_payments': False,
                'can_view_reports': False,
                'can_access_api': False,
                'is_test_plan': True,
                'is_active': True,
                'is_featured': False
            },
            {
                'name': 'cobre',
                'display_name': 'Plano Cobre',
                'description': 'Plano básico com funcionalidades essenciais.',
                'monthly_price': 29.90,
                'yearly_price': 299.00,
                'max_berths': 1,
                'max_services_per_month': 2,
                'max_documents': 3,
                'can_create_services': True,
                'can_upload_documents': True,
                'can_make_payments': True,
                'can_view_reports': False,
                'can_access_api': False,
                'is_test_plan': False,
                'is_active': True,
                'is_featured': False
            },
            {
                'name': 'prata',
                'display_name': 'Plano Prata',
                'description': 'Plano intermediário com mais funcionalidades.',
                'monthly_price': 59.90,
                'yearly_price': 599.00,
                'max_berths': 2,
                'max_services_per_month': 5,
                'max_documents': 10,
                'can_create_services': True,
                'can_upload_documents': True,
                'can_make_payments': True,
                'can_view_reports': True,
                'can_access_api': False,
                'is_test_plan': False,
                'is_active': True,
                'is_featured': True
            },
            {
                'name': 'gold',
                'display_name': 'Plano Gold',
                'description': 'Plano premium com todas as funcionalidades.',
                'monthly_price': 99.90,
                'yearly_price': 999.00,
                'max_berths': 5,
                'max_services_per_month': -1,  # Ilimitado
                'max_documents': -1,  # Ilimitado
                'can_create_services': True,
                'can_upload_documents': True,
                'can_make_payments': True,
                'can_view_reports': True,
                'can_access_api': True,
                'is_test_plan': False,
                'is_active': True,
                'is_featured': False
            }
        ]
        
        for data in plan_data:
            plan = SubscriptionPlan(**data)
            plans.append(plan)
            db.session.add(plan)
        
        db.session.commit()
        
        # Criar vagas para cada marina
        print("Criando vagas...")
        berths = []
        for marina in marinas:
            for i in range(1, 11):  # 10 vagas por marina
                berth = Berth(
                    marina_id=marina.id,
                    berth_number=f'{marina.name[:3].upper()}-{i:02d}',
                    berth_type=random.choice(['flutuante', 'píer', 'box']),
                    length=random.uniform(8, 20),
                    width=random.uniform(3, 8),
                    depth=random.uniform(2, 5),
                    max_boat_length=random.uniform(10, 25),
                    status=random.choice(['available', 'occupied', 'maintenance']),
                    is_active=True,
                    daily_rate=random.uniform(50, 200),
                    monthly_rate=random.uniform(500, 2000),
                    yearly_rate=random.uniform(5000, 20000),
                    description=f'Vaga {i} da {marina.name}'
                )
                berths.append(berth)
                db.session.add(berth)
        
        db.session.commit()
        
        # Criar tipos de serviços
        print("Criando tipos de serviços...")
        services = []
        service_data = [
            {
                'marina_id': marinas[0].id,
                'name': 'Limpeza de Casco',
                'description': 'Limpeza completa do casco da embarcação, incluindo remoção de algas e incrustações',
                'category': 'Limpeza',
                'price': 500.00,
                'price_type': 'fixed',
                'is_active': True,
                'requires_approval': False,
                'max_duration_hours': 2
            },
            {
                'marina_id': marinas[0].id,
                'name': 'Manutenção de Motor',
                'description': 'Revisão completa do motor, troca de óleo e filtros',
                'category': 'Manutenção',
                'price': 800.00,
                'price_type': 'fixed',
                'is_active': True,
                'requires_approval': True,
                'max_duration_hours': 3
            },
            {
                'marina_id': marinas[0].id,
                'name': 'Lavagem Completa',
                'description': 'Lavagem externa e interna da embarcação',
                'category': 'Limpeza',
                'price': 300.00,
                'price_type': 'fixed',
                'is_active': True,
                'requires_approval': False,
                'max_duration_hours': 1
            },
            {
                'marina_id': marinas[1].id,
                'name': 'Reparo Elétrico',
                'description': 'Diagnóstico e reparo de sistemas elétricos',
                'category': 'Manutenção',
                'price': 600.00,
                'price_type': 'hourly',
                'is_active': True,
                'requires_approval': True,
                'max_duration_hours': 4
            },
            {
                'marina_id': marinas[1].id,
                'name': 'Instalação de Equipamentos',
                'description': 'Instalação de GPS, rádio, sonar e outros equipamentos',
                'category': 'Instalação',
                'price': 400.00,
                'price_type': 'fixed',
                'is_active': True,
                'requires_approval': False,
                'max_duration_hours': 2
            }
        ]
        
        for data in service_data:
            service = MarinaService(**data)
            services.append(service)
            db.session.add(service)
        
        db.session.commit()
        
        # Criar algumas solicitações de serviço
        print("Criando solicitações de serviço...")
        vessel_names = ['Sea Dream', 'Ocean Explorer', 'Blue Horizon', 'Wave Rider', 'Star Cruiser']
        vessel_types = ['Iate', 'Lancha', 'Veleiro', 'Jet Ski', 'Barco a Motor']
        
        # Criar assinaturas para os usuários (necessário para solicitar serviços)
        print("Criando assinaturas para usuários...")
        
        # Atribuir planos diferentes para cada usuário
        plan_assignments = ['cobre', 'prata', 'gold']
        
        for i, user in enumerate(users[:3]):  # Apenas 3 usuários com solicitações
            # Pegar o plano correspondente
            plan_name = plan_assignments[i % len(plan_assignments)]
            plan = SubscriptionPlan.query.filter_by(name=plan_name).first()
            
            if not plan:
                continue
                
            # Pegar uma vaga disponível da primeira marina
            available_berth = Berth.query.filter_by(marina_id=marinas[0].id, status='available').first()
            if available_berth:
                # Criar assinatura para o usuário
                subscription = Subscription(
                    user_id=user.id,
                    marina_id=marinas[0].id,
                    berth_id=available_berth.id,
                    plan_id=plan.id,
                    plan_type='monthly',
                    plan_name=plan.display_name,
                    amount=plan.monthly_price,
                    status='active',
                    is_active=True,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=30),
                    next_billing_date=datetime.utcnow() + timedelta(days=30),
                    billing_cycle='monthly',
                    auto_renew=True
                )
                db.session.add(subscription)
                
                # Marcar a vaga como ocupada
                available_berth.status = 'occupied'
                
                # Criar solicitação de serviço
                service = services[i % len(services)]
                preferred_date = datetime.utcnow() + timedelta(days=random.randint(1, 30))
                
                service_request = ServiceRequest(
                    user_id=user.id,
                    marina_service_id=service.id,
                    marina_id=service.marina_id,
                    berth_id=available_berth.id,
                    vessel_name=vessel_names[i % len(vessel_names)],
                    vessel_type=vessel_types[i % len(vessel_types)],
                    vessel_length=random.uniform(8, 15),
                    preferred_date=preferred_date.date(),
                    preferred_time=datetime.strptime('09:00', '%H:%M').time(),
                    notes=f'Solicitação de teste para {service.name}',
                    status='requested',
                    payment_status='pending',
                    original_price=service.price,
                    final_price=service.price
                )
                db.session.add(service_request)
        
        db.session.commit()
        print("Dados de exemplo criados com sucesso!")
        print(f"- {len(users)} usuários criados")
        print(f"- {len(marinas)} marinas criadas")
        print(f"- {len(plans)} planos de assinatura criados")
        print(f"- {len(berths)} vagas criadas")
        print(f"- {len(services)} tipos de serviços criados")
        print(f"- Solicitações de serviço criadas")
        print("\nPlanos de assinatura criados:")
        for plan in plans:
            print(f"  - {plan.display_name}: R$ {plan.monthly_price}/mês")
        print("\nCredenciais do admin:")
        print("Email: admin@boathouse.com")
        print("Senha: admin123")

if __name__ == '__main__':
    create_sample_data() 