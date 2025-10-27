"""
Agente de IA para solicitudes de delivery
Maneja pedidos de comida, búsqueda de restaurantes y seguimiento de entregas
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class DeliveryFilters:
    """Sistema de filtros para restaurantes y comida"""
    
    def __init__(self):
        self.filters = {
            'price_range': ['económico', 'medio', 'premium'],
            'cuisine_type': ['italiana', 'china', 'mexicana', 'vegetariana', 'japonesa', 'americana'],
            'delivery_time': ['rápido', 'estándar', 'sin_prisa'],
            'rating': ['3.0+', '4.0+', '4.5+', '5.0']
        }
        
        # Base de datos simulada de restaurantes
        self.restaurants = [
            {
                'id': 1,
                'name': 'Pizza Italiana Deluxe',
                'cuisine': ['italiana'],
                'price': 'medio',
                'rating': 4.5,
                'delivery_time': 30,
                'menu': ['Pizza Margherita', 'Pasta Carbonara', 'Lasagna'],
                'location': 'Centro'
            },
            {
                'id': 2,
                'name': 'Wok Express',
                'cuisine': ['china'],
                'price': 'económico',
                'rating': 4.0,
                'delivery_time': 25,
                'menu': ['Arroz Frito', 'Pollo Agridulce', 'Chow Mein'],
                'location': 'Norte'
            },
            {
                'id': 3,
                'name': 'Tacos El Mariachi',
                'cuisine': ['mexicana'],
                'price': 'económico',
                'rating': 4.3,
                'delivery_time': 20,
                'menu': ['Tacos al Pastor', 'Quesadillas', 'Burritos'],
                'location': 'Sur'
            },
            {
                'id': 4,
                'name': 'Green Garden',
                'cuisine': ['vegetariana'],
                'price': 'medio',
                'rating': 4.7,
                'delivery_time': 35,
                'menu': ['Buddha Bowl', 'Ensalada César Vegana', 'Hamburguesa de Quinoa'],
                'location': 'Centro'
            },
            {
                'id': 5,
                'name': 'Sushi Zen',
                'cuisine': ['japonesa'],
                'price': 'premium',
                'rating': 4.8,
                'delivery_time': 40,
                'menu': ['Sushi Variado', 'Ramen', 'Tempura'],
                'location': 'Norte'
            }
        ]
    
    def get_restaurants(self) -> List[Dict]:
        """Retorna lista completa de restaurantes"""
        return self.restaurants
    
    def apply_filters(self, user_preferences: Dict) -> List[Dict]:
        """Aplica filtros basados en preferencias del usuario"""
        filtered_restaurants = self.restaurants.copy()
        
        if 'price_range' in user_preferences:
            filtered_restaurants = [
                r for r in filtered_restaurants 
                if r['price'] == user_preferences['price_range']
            ]
        
        if 'cuisine_type' in user_preferences:
            filtered_restaurants = [
                r for r in filtered_restaurants 
                if user_preferences['cuisine_type'] in r['cuisine']
            ]
        
        if 'max_delivery_time' in user_preferences:
            filtered_restaurants = [
                r for r in filtered_restaurants 
                if r['delivery_time'] <= user_preferences['max_delivery_time']
            ]
        
        if 'min_rating' in user_preferences:
            filtered_restaurants = [
                r for r in filtered_restaurants 
                if r['rating'] >= user_preferences['min_rating']
            ]
        
        return filtered_restaurants


class DeliveryAgent:
    """Agente principal para manejo de deliveries"""
    
    def __init__(self):
        self.user_preferences = {}
        self.order_history = []
        self.current_orders = {}
        self.filters = DeliveryFilters()
        
        # Prompts del agente
        self.prompts = {
            "welcome": "¡Hola! Soy tu asistente de delivery. ¿Qué te gustaría ordenar hoy?",
            "restaurant_suggestions": "Basado en tus preferencias de {cuisine}, te recomiendo estos restaurantes:",
            "order_confirmation": "¡Perfecto! Has ordenado {item} de {restaurant}. Tiempo estimado de entrega: {time} minutos",
            "tracking_update": "Tu pedido está {status}. El repartidor {driver} llegará en aproximadamente {eta} minutos",
            "no_restaurants": "Lo siento, no encontré restaurantes que coincidan con tus criterios. ¿Te gustaría ajustar tus preferencias?"
        }
    
    def process_delivery_request(self, user_input: str) -> Dict[str, Any]:
        """Procesa solicitudes de delivery"""
        intent = self.classify_intent(user_input)
        
        if intent == "new_order":
            return self.handle_new_order(user_input)
        elif intent == "track_order":
            return self.handle_tracking(user_input)
        elif intent == "restaurant_search":
            return self.handle_restaurant_search(user_input)
        elif intent == "menu_inquiry":
            return self.handle_menu_inquiry(user_input)
        else:
            return {
                'response': self.prompts['welcome'],
                'action': 'clarify_intent',
                'suggestions': ['Hacer un pedido', 'Buscar restaurantes', 'Rastrear pedido']
            }
    
    def classify_intent(self, text: str) -> str:
        """Clasifica la intención del usuario usando NLP básico"""
        text = text.lower()
        
        # Palabras clave para diferentes intenciones
        order_keywords = ['pedir', 'ordenar', 'quiero', 'delivery', 'entrega', 'comida']
        track_keywords = ['seguimiento', 'dónde', 'track', 'estado', 'pedido', 'orden']
        search_keywords = ['restaurante', 'buscar', 'encontrar', 'recomendar', 'sugerir']
        menu_keywords = ['menú', 'carta', 'que tienen', 'opciones', 'platillos']
        
        if any(word in text for word in order_keywords):
            return "new_order"
        elif any(word in text for word in track_keywords):
            return "track_order"
        elif any(word in text for word in search_keywords):
            return "restaurant_search"
        elif any(word in text for word in menu_keywords):
            return "menu_inquiry"
        
        return "unknown"
    
    def handle_new_order(self, user_input: str) -> Dict[str, Any]:
        """Maneja nuevos pedidos"""
        # Extraer preferencias del usuario
        preferences = self.extract_preferences(user_input)
        
        # Buscar restaurantes que coincidan
        matching_restaurants = self.filters.apply_filters(preferences)
        
        if not matching_restaurants:
            return {
                'response': self.prompts['no_restaurants'],
                'action': 'adjust_preferences',
                'restaurants': []
            }
        
        # Sugerir los mejores restaurantes
        sorted_restaurants = sorted(matching_restaurants, key=lambda x: x['rating'], reverse=True)
        top_restaurants = sorted_restaurants[:3]
        
        return {
            'response': f"He encontrado {len(matching_restaurants)} restaurantes que coinciden con tus preferencias:",
            'action': 'show_restaurants',
            'restaurants': top_restaurants,
            'preferences': preferences
        }
    
    def handle_tracking(self, user_input: str) -> Dict[str, Any]:
        """Maneja seguimiento de pedidos"""
        # Simular estados de pedidos
        order_statuses = [
            "confirmado - el restaurante está preparando tu pedido",
            "en preparación - tu comida está siendo cocinada",
            "listo para recoger - el repartidor está en camino al restaurante",
            "en camino - el repartidor está yendo hacia tu dirección"
        ]
        
        import random
        status = random.choice(order_statuses)
        eta = random.randint(10, 45)
        driver = random.choice(["Carlos", "María", "José", "Ana", "Luis"])
        
        response = self.prompts['tracking_update'].format(
            status=status,
            driver=driver,
            eta=eta
        )
        
        return {
            'response': response,
            'action': 'tracking_info',
            'status': status,
            'eta': eta,
            'driver': driver
        }
    
    def handle_restaurant_search(self, user_input: str) -> Dict[str, Any]:
        """Maneja búsqueda de restaurantes"""
        preferences = self.extract_preferences(user_input)
        matching_restaurants = self.filters.apply_filters(preferences)
        
        if preferences.get('cuisine_type'):
            response = self.prompts['restaurant_suggestions'].format(
                cuisine=preferences['cuisine_type']
            )
        else:
            response = "Aquí tienes algunos restaurantes disponibles:"
        
        return {
            'response': response,
            'action': 'show_restaurants',
            'restaurants': matching_restaurants[:5]  # Mostrar top 5
        }
    
    def handle_menu_inquiry(self, user_input: str) -> Dict[str, Any]:
        """Maneja consultas sobre menús"""
        # Buscar si mencionan un restaurante específico
        restaurant_name = self.extract_restaurant_name(user_input)
        
        if restaurant_name:
            restaurant = next((r for r in self.filters.restaurants if restaurant_name.lower() in r['name'].lower()), None)
            if restaurant:
                return {
                    'response': f"El menú de {restaurant['name']} incluye:",
                    'action': 'show_menu',
                    'restaurant': restaurant,
                    'menu': restaurant['menu']
                }
        
        # Si no se especifica restaurante, mostrar menús populares
        popular_dishes = []
        for restaurant in self.filters.restaurants:
            popular_dishes.extend(restaurant['menu'][:2])  # Top 2 de cada restaurante
        
        return {
            'response': "Aquí tienes algunos platillos populares disponibles:",
            'action': 'show_popular_dishes',
            'dishes': popular_dishes[:8]
        }
    
    def extract_preferences(self, text: str) -> Dict[str, Any]:
        """Extrae preferencias del usuario del texto"""
        text = text.lower()
        preferences = {}
        
        # Detectar tipo de cocina
        cuisine_map = {
            'italiana': ['italiana', 'pizza', 'pasta', 'italiano'],
            'china': ['china', 'chino', 'wok', 'arroz frito'],
            'mexicana': ['mexicana', 'tacos', 'mexicano', 'burrito'],
            'vegetariana': ['vegetariana', 'vegana', 'vegetariano', 'vegano'],
            'japonesa': ['japonesa', 'sushi', 'japonés', 'ramen']
        }
        
        for cuisine, keywords in cuisine_map.items():
            if any(keyword in text for keyword in keywords):
                preferences['cuisine_type'] = cuisine
                break
        
        # Detectar rango de precio
        if any(word in text for word in ['barato', 'económico', 'precio bajo']):
            preferences['price_range'] = 'económico'
        elif any(word in text for word in ['caro', 'premium', 'elegante', 'fino']):
            preferences['price_range'] = 'premium'
        elif any(word in text for word in ['medio', 'moderado']):
            preferences['price_range'] = 'medio'
        
        # Detectar tiempo de entrega
        if any(word in text for word in ['rápido', 'urgente', 'pronto']):
            preferences['max_delivery_time'] = 25
        elif any(word in text for word in ['sin prisa', 'cuando pueda']):
            preferences['max_delivery_time'] = 60
        
        # Detectar rating mínimo
        if any(word in text for word in ['mejor', 'excelente', 'top']):
            preferences['min_rating'] = 4.5
        elif any(word in text for word in ['bueno', 'recomendado']):
            preferences['min_rating'] = 4.0
        
        return preferences
    
    def extract_restaurant_name(self, text: str) -> Optional[str]:
        """Extrae nombre de restaurante del texto"""
        text = text.lower()
        for restaurant in self.filters.restaurants:
            restaurant_words = restaurant['name'].lower().split()
            if any(word in text for word in restaurant_words):
                return restaurant['name']
        return None
    
    def confirm_order(self, restaurant_id: int, items: List[str], user_info: Dict) -> Dict[str, Any]:
        """Confirma un pedido"""
        restaurant = next((r for r in self.filters.restaurants if r['id'] == restaurant_id), None)
        
        if not restaurant:
            return {'error': 'Restaurante no encontrado'}
        
        order = {
            'id': len(self.order_history) + 1,
            'restaurant': restaurant,
            'items': items,
            'user_info': user_info,
            'timestamp': datetime.now(),
            'status': 'confirmado',
            'estimated_delivery': datetime.now() + timedelta(minutes=restaurant['delivery_time'])
        }
        
        self.order_history.append(order)
        self.current_orders[order['id']] = order
        
        response = self.prompts['order_confirmation'].format(
            item=', '.join(items),
            restaurant=restaurant['name'],
            time=restaurant['delivery_time']
        )
        
        return {
            'response': response,
            'action': 'order_confirmed',
            'order': order
        }
    
    def get_order_summary(self, order_id: int) -> Dict[str, Any]:
        """Obtiene resumen de un pedido"""
        if order_id in self.current_orders:
            order = self.current_orders[order_id]
            return {
                'order_id': order_id,
                'restaurant': order['restaurant']['name'],
                'items': order['items'],
                'status': order['status'],
                'estimated_delivery': order['estimated_delivery'].strftime('%H:%M')
            }
        return {'error': 'Pedido no encontrado'}


# Función de demostración
def demo_delivery_agent():
    """Demuestra la funcionalidad del agente de delivery"""
    agent = DeliveryAgent()
    
    print("=== DEMO: AGENTE DE DELIVERY ===\n")
    
    # Caso 1: Búsqueda de comida italiana
    print("Usuario: 'Quiero pedir comida italiana para 2 personas'")
    response1 = agent.process_delivery_request("Quiero pedir comida italiana para 2 personas")
    print(f"Agente: {response1['response']}")
    if response1.get('restaurants'):
        for restaurant in response1['restaurants']:
            print(f"  - {restaurant['name']} (Rating: {restaurant['rating']}, Tiempo: {restaurant['delivery_time']} min)")
    print()
    
    # Caso 2: Búsqueda con precio específico
    print("Usuario: 'Busco restaurantes económicos y rápidos'")
    response2 = agent.process_delivery_request("Busco restaurantes económicos y rápidos")
    print(f"Agente: {response2['response']}")
    if response2.get('restaurants'):
        for restaurant in response2['restaurants']:
            print(f"  - {restaurant['name']} ({restaurant['cuisine'][0]}, ${restaurant['price']}, {restaurant['delivery_time']} min)")
    print()
    
    # Caso 3: Consulta de menú
    print("Usuario: '¿Qué tiene Pizza Italiana Deluxe?'")
    response3 = agent.process_delivery_request("¿Qué tiene Pizza Italiana Deluxe?")
    print(f"Agente: {response3['response']}")
    if response3.get('menu'):
        for item in response3['menu']:
            print(f"  - {item}")
    print()
    
    # Caso 4: Seguimiento de pedido
    print("Usuario: '¿Dónde está mi pedido?'")
    response4 = agent.process_delivery_request("¿Dónde está mi pedido?")
    print(f"Agente: {response4['response']}")
    print()


if __name__ == "__main__":
    demo_delivery_agent()