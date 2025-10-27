"""
Agente de IA para reservas en restaurantes
Maneja reservas, disponibilidad y gestión de mesas
"""

import re
import json
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
import calendar


class AvailabilityManager:
    """Gestor de disponibilidad de restaurantes"""
    
    def __init__(self):
        # Simulación de horarios de restaurantes
        self.restaurant_schedules = {
            'resto_1': {
                'name': 'La Bella Italiana',
                'capacity': 50,
                'hours': {
                    'monday': ('12:00', '23:00'),
                    'tuesday': ('12:00', '23:00'),
                    'wednesday': ('12:00', '23:00'),
                    'thursday': ('12:00', '23:00'),
                    'friday': ('12:00', '24:00'),
                    'saturday': ('12:00', '24:00'),
                    'sunday': ('12:00', '22:00')
                },
                'time_slots': ['12:00', '12:30', '13:00', '13:30', '14:00', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30']
            },
            'resto_2': {
                'name': 'Sakura Sushi',
                'capacity': 30,
                'hours': {
                    'monday': ('18:00', '23:00'),
                    'tuesday': ('18:00', '23:00'),
                    'wednesday': ('18:00', '23:00'),
                    'thursday': ('18:00', '23:00'),
                    'friday': ('18:00', '24:00'),
                    'saturday': ('18:00', '24:00'),
                    'sunday': ('18:00', '22:00')
                },
                'time_slots': ['18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30']
            },
            'resto_3': {
                'name': 'El Asador Criollo',
                'capacity': 80,
                'hours': {
                    'monday': ('19:00', '24:00'),
                    'tuesday': ('19:00', '24:00'),
                    'wednesday': ('19:00', '24:00'),
                    'thursday': ('19:00', '24:00'),
                    'friday': ('19:00', '02:00'),
                    'saturday': ('19:00', '02:00'),
                    'sunday': 'closed'
                },
                'time_slots': ['19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00', '22:30']
            }
        }
        
        # Simulación de reservas existentes
        self.reservations = {}
        self._initialize_sample_reservations()
    
    def _initialize_sample_reservations(self):
        """Inicializa algunas reservas de ejemplo"""
        today = date.today()
        for i in range(7):  # Próximos 7 días
            current_date = today + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            self.reservations[date_str] = {}
            
            for resto_id in self.restaurant_schedules:
                self.reservations[date_str][resto_id] = {}
                
                # Agregar algunas reservas aleatorias
                import random
                for time_slot in random.sample(self.restaurant_schedules[resto_id]['time_slots'], 
                                             random.randint(2, 5)):
                    self.reservations[date_str][resto_id][time_slot] = random.randint(10, 30)
    
    def check_availability(self, restaurant_id: str, date_str: str, time: str, party_size: int) -> bool:
        """Verifica disponibilidad en el restaurante"""
        if restaurant_id not in self.restaurant_schedules:
            return False
        
        restaurant = self.restaurant_schedules[restaurant_id]
        
        # Verificar si el día está abierto
        day_name = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A').lower()
        if day_name not in restaurant['hours'] or restaurant['hours'][day_name] == 'closed':
            return False
        
        # Verificar horario de funcionamiento
        if time not in restaurant['time_slots']:
            return False
        
        # Verificar capacidad
        if date_str not in self.reservations:
            self.reservations[date_str] = {}
        
        if restaurant_id not in self.reservations[date_str]:
            self.reservations[date_str][restaurant_id] = {}
        
        current_reservations = self.reservations[date_str][restaurant_id].get(time, 0)
        available_capacity = restaurant['capacity'] - current_reservations
        
        return available_capacity >= party_size
    
    def make_reservation(self, restaurant_id: str, date_str: str, time: str, party_size: int) -> bool:
        """Hace una reserva"""
        if self.check_availability(restaurant_id, date_str, time, party_size):
            if date_str not in self.reservations:
                self.reservations[date_str] = {}
            if restaurant_id not in self.reservations[date_str]:
                self.reservations[date_str][restaurant_id] = {}
            
            current = self.reservations[date_str][restaurant_id].get(time, 0)
            self.reservations[date_str][restaurant_id][time] = current + party_size
            return True
        return False
    
    def get_alternative_times(self, restaurant_id: str, date_str: str, party_size: int) -> List[str]:
        """Obtiene horarios alternativos disponibles"""
        alternatives = []
        restaurant = self.restaurant_schedules.get(restaurant_id, {})
        
        for time_slot in restaurant.get('time_slots', []):
            if self.check_availability(restaurant_id, date_str, time_slot, party_size):
                alternatives.append(time_slot)
        
        return alternatives
    
    def get_restaurant_info(self, restaurant_id: str) -> Dict[str, Any]:
        """Obtiene información del restaurante"""
        return self.restaurant_schedules.get(restaurant_id, {})


class RestaurantReservationAgent:
    """Agente principal para reservas en restaurantes"""
    
    def __init__(self):
        self.availability_manager = AvailabilityManager()
        self.reservation_history = []
        self.current_session = {}
        
        # Prompts del agente
        self.prompts = {
            "welcome": "¡Hola! Soy tu asistente para reservas de restaurantes. ¿En qué puedo ayudarte?",
            "reservation_confirmed": "¡Excelente! Tu reserva ha sido confirmada para {party_size} personas en {restaurant} el {date} a las {time}.",
            "no_availability": "Lo siento, no hay disponibilidad para {party_size} personas el {date} a las {time}. ¿Te gustaría ver horarios alternativos?",
            "alternative_times": "Tengo disponibilidad en los siguientes horarios para {restaurant} el {date}:",
            "missing_info": "Necesito más información para hacer tu reserva. Por favor proporciona: {missing_fields}",
            "restaurant_info": "Te cuento sobre {restaurant}: Capacidad para {capacity} personas, horarios: {hours}"
        }
    
    def handle_reservation_request(self, request: str) -> Dict[str, Any]:
        """Maneja solicitudes de reserva"""
        # Extraer entidades del texto
        entities = self.extract_entities(request)
        
        # Verificar si tenemos toda la información necesaria
        missing_fields = self.validate_entities(entities)
        
        if missing_fields:
            return {
                'response': self.prompts['missing_info'].format(missing_fields=', '.join(missing_fields)),
                'action': 'request_info',
                'missing_fields': missing_fields,
                'extracted_entities': entities
            }
        
        # Procesar la reserva
        return self.process_reservation(entities)
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extrae entidades clave del texto del usuario"""
        entities = {}
        text_lower = text.lower()
        
        # Extraer fecha
        entities['date'] = self.extract_date(text)
        
        # Extraer hora
        entities['time'] = self.extract_time(text)
        
        # Extraer número de personas
        entities['party_size'] = self.extract_party_size(text)
        
        # Extraer nombre del restaurante
        entities['restaurant'] = self.extract_restaurant_name(text)
        
        # Extraer preferencias especiales
        entities['special_requests'] = self.extract_special_requests(text)
        
        return entities
    
    def extract_date(self, text: str) -> Optional[str]:
        """Extrae fecha del texto"""
        text_lower = text.lower()
        today = date.today()
        
        # Palabras clave para fechas relativas
        if 'hoy' in text_lower:
            return today.strftime('%Y-%m-%d')
        elif 'mañana' in text_lower:
            tomorrow = today + timedelta(days=1)
            return tomorrow.strftime('%Y-%m-%d')
        elif 'pasado mañana' in text_lower:
            day_after = today + timedelta(days=2)
            return day_after.strftime('%Y-%m-%d')
        
        # Días de la semana
        days_map = {
            'lunes': 0, 'martes': 1, 'miércoles': 2, 'miercoles': 2,
            'jueves': 3, 'viernes': 4, 'sábado': 5, 'sabado': 5, 'domingo': 6
        }
        
        for day_name, day_num in days_map.items():
            if day_name in text_lower:
                days_ahead = (day_num - today.weekday()) % 7
                if days_ahead == 0:  # Si es el mismo día, asumir la próxima semana
                    days_ahead = 7
                target_date = today + timedelta(days=days_ahead)
                return target_date.strftime('%Y-%m-%d')
        
        # Patrón de fecha DD/MM o DD-MM
        date_pattern = r'(\d{1,2})[/-](\d{1,2})'
        match = re.search(date_pattern, text)
        if match:
            day, month = int(match.group(1)), int(match.group(2))
            try:
                year = today.year
                target_date = date(year, month, day)
                if target_date < today:  # Si la fecha ya pasó, asumir el próximo año
                    target_date = date(year + 1, month, day)
                return target_date.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        return None
    
    def extract_time(self, text: str) -> Optional[str]:
        """Extrae hora del texto"""
        # Patrones de hora
        time_patterns = [
            r'(\d{1,2}):(\d{2})',  # HH:MM
            r'(\d{1,2}) horas?',   # X horas
            r'(\d{1,2})hs?',       # Xhs
            r'(\d{1,2}) ?(am|pm)', # X am/pm
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text.lower())
            if match:
                if ':' in match.group(0):
                    hour, minute = match.groups()
                    return f"{int(hour):02d}:{int(minute):02d}"
                else:
                    hour = match.group(1)
                    if 'pm' in match.group(0) and int(hour) < 12:
                        hour = str(int(hour) + 12)
                    return f"{int(hour):02d}:00"
        
        # Palabras clave para horarios típicos
        time_keywords = {
            'mediodía': '12:00',
            'mediodia': '12:00',
            'tarde': '19:00',
            'noche': '20:00',
            'cena': '20:30'
        }
        
        for keyword, time_value in time_keywords.items():
            if keyword in text.lower():
                return time_value
        
        return None
    
    def extract_party_size(self, text: str) -> Optional[int]:
        """Extrae número de personas del texto"""
        # Patrones numéricos
        number_patterns = [
            r'(\d+) personas?',
            r'para (\d+)',
            r'somos (\d+)',
            r'mesa para (\d+)',
            r'(\d+) comensales?'
        ]
        
        for pattern in number_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        # Números escritos
        number_words = {
            'una': 1, 'un': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5,
            'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9, 'diez': 10
        }
        
        for word, num in number_words.items():
            if word + ' persona' in text.lower() or word + ' comens' in text.lower():
                return num
        
        return None
    
    def extract_restaurant_name(self, text: str) -> Optional[str]:
        """Extrae nombre del restaurante del texto"""
        restaurants = self.availability_manager.restaurant_schedules
        
        for resto_id, resto_info in restaurants.items():
            resto_name = resto_info['name'].lower()
            resto_words = resto_name.split()
            
            # Buscar coincidencias en palabras clave del nombre
            if any(word in text.lower() for word in resto_words if len(word) > 3):
                return resto_id
        
        return None
    
    def extract_special_requests(self, text: str) -> List[str]:
        """Extrae solicitudes especiales del texto"""
        special_requests = []
        text_lower = text.lower()
        
        request_keywords = {
            'vegetariano': ['vegetariano', 'vegano', 'sin carne'],
            'celebración': ['cumpleaños', 'aniversario', 'celebración', 'fiesta'],
            'terraza': ['terraza', 'afuera', 'exterior'],
            'ventana': ['ventana', 'vista'],
            'accesibilidad': ['silla de ruedas', 'accesible', 'discapacidad']
        }
        
        for category, keywords in request_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                special_requests.append(category)
        
        return special_requests
    
    def validate_entities(self, entities: Dict[str, Any]) -> List[str]:
        """Valida que tengamos todas las entidades necesarias"""
        required_fields = ['date', 'time', 'party_size', 'restaurant']
        missing_fields = []
        
        for field in required_fields:
            if not entities.get(field):
                field_names = {
                    'date': 'fecha',
                    'time': 'hora',
                    'party_size': 'número de personas',
                    'restaurant': 'restaurante'
                }
                missing_fields.append(field_names[field])
        
        return missing_fields
    
    def process_reservation(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la reserva con las entidades extraídas"""
        restaurant_id = entities['restaurant']
        date_str = entities['date']
        time = entities['time']
        party_size = entities['party_size']
        
        # Verificar disponibilidad
        available = self.availability_manager.check_availability(
            restaurant_id, date_str, time, party_size
        )
        
        if available:
            # Hacer la reserva
            success = self.availability_manager.make_reservation(
                restaurant_id, date_str, time, party_size
            )
            
            if success:
                return self.confirm_reservation(entities)
            else:
                return self.handle_reservation_error(entities)
        else:
            return self.suggest_alternatives(entities)
    
    def confirm_reservation(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Confirma una reserva exitosa"""
        restaurant_info = self.availability_manager.get_restaurant_info(entities['restaurant'])
        restaurant_name = restaurant_info.get('name', 'Restaurante')
        
        # Generar ID de reserva
        reservation_id = f"RES-{len(self.reservation_history) + 1:04d}"
        
        # Guardar reserva
        reservation = {
            'id': reservation_id,
            'restaurant_id': entities['restaurant'],
            'restaurant_name': restaurant_name,
            'date': entities['date'],
            'time': entities['time'],
            'party_size': entities['party_size'],
            'special_requests': entities.get('special_requests', []),
            'timestamp': datetime.now(),
            'status': 'confirmed'
        }
        
        self.reservation_history.append(reservation)
        
        response = self.prompts['reservation_confirmed'].format(
            party_size=entities['party_size'],
            restaurant=restaurant_name,
            date=entities['date'],
            time=entities['time']
        )
        
        return {
            'response': response,
            'action': 'reservation_confirmed',
            'reservation': reservation
        }
    
    def suggest_alternatives(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Sugiere horarios alternativos"""
        restaurant_id = entities['restaurant']
        date_str = entities['date']
        party_size = entities['party_size']
        
        alternatives = self.availability_manager.get_alternative_times(
            restaurant_id, date_str, party_size
        )
        
        restaurant_info = self.availability_manager.get_restaurant_info(restaurant_id)
        restaurant_name = restaurant_info.get('name', 'Restaurante')
        
        if alternatives:
            response = self.prompts['alternative_times'].format(
                restaurant=restaurant_name,
                date=date_str
            )
            
            return {
                'response': response,
                'action': 'show_alternatives',
                'alternatives': alternatives,
                'original_request': entities
            }
        else:
            return {
                'response': f"Lo siento, {restaurant_name} no tiene disponibilidad para {party_size} personas el {date_str}. ¿Te gustaría intentar con otra fecha?",
                'action': 'no_availability',
                'suggestion': 'try_different_date'
            }
    
    def handle_reservation_error(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja errores en el proceso de reserva"""
        return {
            'response': "Hubo un problema al procesar tu reserva. Por favor intenta nuevamente.",
            'action': 'error',
            'error_type': 'reservation_failed'
        }
    
    def get_restaurant_list(self) -> Dict[str, Any]:
        """Obtiene lista de restaurantes disponibles"""
        restaurants = []
        for resto_id, resto_info in self.availability_manager.restaurant_schedules.items():
            restaurants.append({
                'id': resto_id,
                'name': resto_info['name'],
                'capacity': resto_info['capacity'],
                'cuisine_type': self._get_cuisine_type(resto_info['name'])
            })
        
        return {
            'response': "Aquí tienes nuestros restaurantes disponibles:",
            'action': 'show_restaurants',
            'restaurants': restaurants
        }
    
    def _get_cuisine_type(self, restaurant_name: str) -> str:
        """Determina el tipo de cocina basado en el nombre"""
        name_lower = restaurant_name.lower()
        if 'italiana' in name_lower:
            return 'Italiana'
        elif 'sushi' in name_lower or 'sakura' in name_lower:
            return 'Japonesa'
        elif 'asador' in name_lower or 'criollo' in name_lower:
            return 'Argentina'
        else:
            return 'Internacional'


# Función de demostración
def demo_reservation_agent():
    """Demuestra la funcionalidad del agente de reservas"""
    agent = RestaurantReservationAgent()
    
    print("=== DEMO: AGENTE DE RESERVAS ===\n")
    
    # Caso 1: Reserva completa
    print("Usuario: 'Necesito reservar para 4 personas en La Bella Italiana el viernes a las 8 PM'")
    response1 = agent.handle_reservation_request(
        "Necesito reservar para 4 personas en La Bella Italiana el viernes a las 8 PM"
    )
    print(f"Agente: {response1['response']}")
    if response1.get('reservation'):
        print(f"ID de Reserva: {response1['reservation']['id']}")
    print()
    
    # Caso 2: Información incompleta
    print("Usuario: 'Quiero reservar para mañana'")
    response2 = agent.handle_reservation_request("Quiero reservar para mañana")
    print(f"Agente: {response2['response']}")
    if response2.get('missing_fields'):
        print(f"Información faltante: {response2['missing_fields']}")
    print()
    
    # Caso 3: Buscar alternativas
    print("Usuario: 'Para 20 personas en Sakura Sushi el sábado a las 19:00'")
    response3 = agent.handle_reservation_request(
        "Para 20 personas en Sakura Sushi el sábado a las 19:00"
    )
    print(f"Agente: {response3['response']}")
    if response3.get('alternatives'):
        print("Horarios alternativos:")
        for alt_time in response3['alternatives']:
            print(f"  - {alt_time}")
    print()
    
    # Caso 4: Lista de restaurantes
    print("Usuario solicita ver restaurantes disponibles:")
    response4 = agent.get_restaurant_list()
    print(f"Agente: {response4['response']}")
    for restaurant in response4['restaurants']:
        print(f"  - {restaurant['name']} ({restaurant['cuisine_type']}) - Capacidad: {restaurant['capacity']} personas")
    print()


if __name__ == "__main__":
    demo_reservation_agent()