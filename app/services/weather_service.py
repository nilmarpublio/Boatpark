import requests
import json
from datetime import datetime
from flask import current_app
import os

class WeatherService:
    """Serviço para obter informações de previsão do tempo"""
    
    def __init__(self):
        # Usar API gratuita do OpenWeatherMap
        self.api_key = os.getenv('OPENWEATHER_API_KEY', 'demo_key')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Coordenadas padrão para São Paulo (pode ser configurável)
        self.default_lat = -23.5505
        self.default_lon = -46.6333
        self.default_city = "São Paulo"
    
    def get_current_weather(self, lat=None, lon=None, city=None):
        """
        Obtém a previsão do tempo atual
        
        Args:
            lat (float): Latitude
            lon (float): Longitude  
            city (str): Nome da cidade
            
        Returns:
            dict: Dados do tempo formatados
        """
        try:
            # Se não tiver API key, retornar dados mock
            if self.api_key == 'demo_key':
                return self._get_mock_weather()
            
            # Construir URL da API
            if city:
                url = f"{self.base_url}/weather"
                params = {
                    'q': f"{city},BR",
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'pt_br'
                }
            else:
                url = f"{self.base_url}/weather"
                params = {
                    'lat': lat or self.default_lat,
                    'lon': lon or self.default_lon,
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'pt_br'
                }
            
            # Fazer requisição
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_weather_data(data)
            
        except requests.RequestException as e:
            current_app.logger.error(f"Erro ao buscar dados do tempo: {e}")
            return self._get_mock_weather()
        except Exception as e:
            current_app.logger.error(f"Erro inesperado no serviço de tempo: {e}")
            return self._get_mock_weather()
    
    def get_forecast(self, lat=None, lon=None, city=None, days=5):
        """
        Obtém previsão para os próximos dias
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            city (str): Nome da cidade
            days (int): Número de dias (máx 5)
            
        Returns:
            list: Lista de previsões
        """
        try:
            # Se não tiver API key, retornar dados mock
            if self.api_key == 'demo_key':
                return self._get_mock_forecast(days)
            
            # Construir URL da API
            if city:
                url = f"{self.base_url}/forecast"
                params = {
                    'q': f"{city},BR",
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'pt_br'
                }
            else:
                url = f"{self.base_url}/forecast"
                params = {
                    'lat': lat or self.default_lat,
                    'lon': lon or self.default_lon,
                    'appid': self.api_key,
                    'units': 'metric',
                    'lang': 'pt_br'
                }
            
            # Fazer requisição
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return self._format_forecast_data(data, days)
            
        except requests.RequestException as e:
            current_app.logger.error(f"Erro ao buscar previsão do tempo: {e}")
            return self._get_mock_forecast(days)
        except Exception as e:
            current_app.logger.error(f"Erro inesperado na previsão do tempo: {e}")
            return self._get_mock_forecast(days)
    
    def _format_weather_data(self, data):
        """Formata os dados do tempo da API"""
        try:
            weather = {
                'city': data.get('name', 'São Paulo'),
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # m/s para km/h
                'wind_direction': data['wind'].get('deg', 0),
                'visibility': data.get('visibility', 10000) / 1000,  # metros para km
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                'updated_at': datetime.now().strftime('%H:%M')
            }
            
            # Adicionar classe CSS baseada na temperatura
            if weather['temperature'] >= 30:
                weather['temp_class'] = 'text-danger'
                weather['temp_icon'] = 'fas fa-thermometer-full'
            elif weather['temperature'] >= 20:
                weather['temp_class'] = 'text-warning'
                weather['temp_icon'] = 'fas fa-thermometer-half'
            elif weather['temperature'] >= 10:
                weather['temp_class'] = 'text-info'
                weather['temp_icon'] = 'fas fa-thermometer-quarter'
            else:
                weather['temp_class'] = 'text-primary'
                weather['temp_icon'] = 'fas fa-thermometer-empty'
            
            return weather
            
        except Exception as e:
            current_app.logger.error(f"Erro ao formatar dados do tempo: {e}")
            return self._get_mock_weather()
    
    def _format_forecast_data(self, data, days):
        """Formata os dados da previsão"""
        try:
            forecasts = []
            daily_data = {}
            current_time = datetime.now()
            
            # Filtrar apenas dados futuros e agrupar por dia
            for item in data['list']:
                item_time = datetime.fromtimestamp(item['dt'])
                
                # Pular dados passados
                if item_time <= current_time:
                    continue
                    
                date = item_time.strftime('%Y-%m-%d')
                if date not in daily_data:
                    daily_data[date] = []
                daily_data[date].append(item)
            
            # Processar cada dia (apenas dados futuros)
            for i, (date, items) in enumerate(list(daily_data.items())[:days]):
                if i >= days:
                    break
                    
                # Calcular médias
                temps = [item['main']['temp'] for item in items]
                humidities = [item['main']['humidity'] for item in items]
                
                # Usar a data correta do item
                item_date = datetime.fromtimestamp(items[0]['dt'])
                
                forecast = {
                    'date': item_date.strftime('%d/%m'),
                    'day_name': item_date.strftime('%a'),
                    'temp_min': round(min(temps)),
                    'temp_max': round(max(temps)),
                    'humidity': round(sum(humidities) / len(humidities)),
                    'description': items[0]['weather'][0]['description'].title(),
                    'icon': items[0]['weather'][0]['icon']
                }
                
                forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            current_app.logger.error(f"Erro ao formatar previsão: {e}")
            return self._get_mock_forecast(days)
    
    def _get_mock_weather(self):
        """Retorna dados mock do tempo para demonstração"""
        return {
            'city': 'São Paulo',
            'temperature': 25,
            'feels_like': 27,
            'humidity': 65,
            'pressure': 1013,
            'description': 'Parcialmente Nublado',
            'icon': '02d',
            'wind_speed': 12.5,
            'wind_direction': 180,
            'visibility': 10.0,
            'sunrise': '06:30',
            'sunset': '17:45',
            'updated_at': datetime.now().strftime('%H:%M'),
            'temp_class': 'text-warning',
            'temp_icon': 'fas fa-thermometer-half'
        }
    
    def _get_mock_forecast(self, days):
        """Retorna previsão mock para demonstração"""
        from datetime import datetime, timedelta
        
        forecasts = []
        current_date = datetime.now()
        
        for i in range(days):
            # Calcular data futura
            future_date = current_date + timedelta(days=i+1)
            
            forecast = {
                'date': future_date.strftime('%d/%m'),
                'day_name': future_date.strftime('%a'),
                'temp_min': 18 + i,
                'temp_max': 25 + i,
                'humidity': 60 + (i * 2),
                'description': 'Ensolarado',
                'icon': '01d'
            }
            forecasts.append(forecast)
        return forecasts 