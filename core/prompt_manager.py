"""
Sistema de gestión de prompts contextualizados para agentes de IA
Centraliza y gestiona todos los prompts para diferentes tipos de agentes
"""

import json
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum


class PromptType(Enum):
    """Tipos de prompts disponibles"""
    WELCOME = "welcome"
    CONFIRMATION = "confirmation"
    ERROR = "error"
    REQUEST_INFO = "request_info"
    SUGGESTION = "suggestion"
    INSTRUCTION = "instruction"
    CLARIFICATION = "clarification"
    SUCCESS = "success"
    WARNING = "warning"


class PromptCategory(Enum):
    """Categorías de prompts por dominio"""
    DELIVERY = "delivery"
    RESERVATION = "reservation"
    DESIGN = "design"
    API_GENERATION = "api_generation"
    GENERAL = "general"


class PromptTemplate:
    """Representa una plantilla de prompt"""
    
    def __init__(self, template_id: str, category: PromptCategory, prompt_type: PromptType,
                 template: str, variables: List[str] = None, context_requirements: List[str] = None,
                 language: str = "es", priority: int = 1):
        self.template_id = template_id
        self.category = category
        self.prompt_type = prompt_type
        self.template = template
        self.variables = variables or []
        self.context_requirements = context_requirements or []
        self.language = language
        self.priority = priority
        self.usage_count = 0
        self.created_at = datetime.now()
    
    def render(self, context: Dict[str, Any]) -> str:
        """Renderiza el template con el contexto proporcionado"""
        try:
            # Validar que todas las variables requeridas estén presentes
            missing_vars = [var for var in self.variables if var not in context]
            if missing_vars:
                raise ValueError(f"Variables faltantes: {missing_vars}")
            
            # Renderizar template
            rendered = self.template.format(**context)
            self.usage_count += 1
            return rendered
            
        except KeyError as e:
            raise ValueError(f"Variable no encontrada en contexto: {e}")
        except Exception as e:
            raise ValueError(f"Error al renderizar template: {e}")


class PromptManager:
    """Gestor principal de prompts contextualizados"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self.prompt_history: List[Dict[str, Any]] = []
        self.context_cache: Dict[str, Any] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Inicializa templates por defecto para todos los agentes"""
        
        # === PROMPTS PARA DELIVERY ===
        delivery_templates = [
            PromptTemplate(
                "delivery_welcome",
                PromptCategory.DELIVERY,
                PromptType.WELCOME,
                "¡Hola! Soy tu asistente de delivery. ¿Qué te gustaría ordenar hoy? Puedo ayudarte a buscar restaurantes, hacer pedidos y rastrear entregas.",
                language="es"
            ),
            PromptTemplate(
                "delivery_restaurant_suggestions",
                PromptCategory.DELIVERY,
                PromptType.SUGGESTION,
                "Basado en tus preferencias de {cuisine_type}, te recomiendo estos restaurantes:\n\n{restaurant_list}\n\n¿Te gustaría ver el menú de alguno o necesitas más opciones?",
                ["cuisine_type", "restaurant_list"],
                language="es"
            ),
            PromptTemplate(
                "delivery_order_confirmation",
                PromptCategory.DELIVERY,
                PromptType.CONFIRMATION,
                "¡Perfecto! Has ordenado:\n{order_items}\n\nRestaurante: {restaurant_name}\nTiempo estimado: {delivery_time} minutos\nTotal: ${total_cost}\n\n¿Confirmas tu pedido?",
                ["order_items", "restaurant_name", "delivery_time", "total_cost"],
                language="es"
            ),
            PromptTemplate(
                "delivery_tracking_update",
                PromptCategory.DELIVERY,
                PromptType.INSTRUCTION,
                "Tu pedido #{order_id} está {status}.\n\n📍 Estado: {detailed_status}\n🚗 Repartidor: {driver_name}\n⏰ Tiempo estimado de llegada: {eta} minutos\n\n{additional_info}",
                ["order_id", "status", "detailed_status", "driver_name", "eta", "additional_info"],
                language="es"
            ),
            PromptTemplate(
                "delivery_no_restaurants",
                PromptCategory.DELIVERY,
                PromptType.WARNING,
                "Lo siento, no encontré restaurantes que coincidan con tus criterios:\n{search_criteria}\n\n¿Te gustaría:\n1. Ajustar tus preferencias\n2. Ver todas las opciones disponibles\n3. Buscar en una zona diferente",
                ["search_criteria"],
                language="es"
            ),
            PromptTemplate(
                "delivery_menu_inquiry",
                PromptCategory.DELIVERY,
                PromptType.INSTRUCTION,
                "El menú de {restaurant_name} incluye:\n\n{menu_items}\n\n💰 Rango de precios: {price_range}\n⭐ Calificación: {rating}/5\n🚚 Tiempo de entrega: {delivery_time} min\n\n¿Qué te gustaría ordenar?",
                ["restaurant_name", "menu_items", "price_range", "rating", "delivery_time"],
                language="es"
            )
        ]
        
        # === PROMPTS PARA RESERVAS ===
        reservation_templates = [
            PromptTemplate(
                "reservation_welcome",
                PromptCategory.RESERVATION,
                PromptType.WELCOME,
                "¡Bienvenido! Soy tu asistente para reservas de restaurantes. Puedo ayudarte a encontrar mesa en los mejores restaurantes de la ciudad. ¿Para cuándo necesitas la reserva?",
                language="es"
            ),
            PromptTemplate(
                "reservation_confirmed",
                PromptCategory.RESERVATION,
                PromptType.SUCCESS,
                "¡Excelente! Tu reserva ha sido confirmada:\n\n🏪 Restaurante: {restaurant_name}\n👥 Mesa para: {party_size} personas\n📅 Fecha: {date}\n🕐 Hora: {time}\n📋 Código de reserva: {reservation_id}\n\n{special_requests_text}Por favor llega 10 minutos antes de tu hora reservada.",
                ["restaurant_name", "party_size", "date", "time", "reservation_id", "special_requests_text"],
                language="es"
            ),
            PromptTemplate(
                "reservation_no_availability",
                PromptCategory.RESERVATION,
                PromptType.WARNING,
                "Lo siento, {restaurant_name} no tiene disponibilidad para {party_size} personas el {date} a las {time}.\n\n¿Te gustaría que te muestre horarios alternativos o prefieres intentar con otro restaurante?",
                ["restaurant_name", "party_size", "date", "time"],
                language="es"
            ),
            PromptTemplate(
                "reservation_alternatives",
                PromptCategory.RESERVATION,
                PromptType.SUGGESTION,
                "Tengo disponibilidad en {restaurant_name} para {party_size} personas el {date} en los siguientes horarios:\n\n{alternative_times}\n\n¿Alguno de estos horarios te conviene?",
                ["restaurant_name", "party_size", "date", "alternative_times"],
                language="es"
            ),
            PromptTemplate(
                "reservation_missing_info",
                PromptCategory.RESERVATION,
                PromptType.REQUEST_INFO,
                "Para completar tu reserva necesito la siguiente información:\n\n{missing_fields_list}\n\nPor favor proporciona estos datos para continuar.",
                ["missing_fields_list"],
                language="es"
            ),
            PromptTemplate(
                "reservation_restaurant_info",
                PromptCategory.RESERVATION,
                PromptType.INSTRUCTION,
                "Te cuento sobre {restaurant_name}:\n\n🍽️ Tipo de cocina: {cuisine_type}\n👥 Capacidad: {capacity} personas\n🕐 Horarios: {operating_hours}\n⭐ Calificación: {rating}/5\n💰 Rango de precios: {price_range}\n📍 Ubicación: {location}\n\n¿Te gustaría hacer una reserva aquí?",
                ["restaurant_name", "cuisine_type", "capacity", "operating_hours", "rating", "price_range", "location"],
                language="es"
            )
        ]
        
        # === PROMPTS PARA DISEÑO ===
        design_templates = [
            PromptTemplate(
                "design_welcome",
                PromptCategory.DESIGN,
                PromptType.WELCOME,
                "¡Hola! Soy tu asistente de diseño de interiores. Puedo ayudarte a crear el diseño perfecto para tu espacio. ¿Qué tipo de habitación quieres diseñar?",
                language="es"
            ),
            PromptTemplate(
                "design_proposal",
                PromptCategory.DESIGN,
                PromptType.SUGGESTION,
                "He creado un diseño {style} para tu {room_type} de {dimensions}:\n\n💡 **Concepto:** {design_concept}\n💰 **Presupuesto:** ${total_cost} de ${budget} (${remaining} restante)\n📐 **Eficiencia del espacio:** {efficiency}%\n\n**Muebles incluidos:**\n{furniture_list}\n\n**Recomendaciones:**\n{recommendations}\n\n¿Te gusta esta propuesta o prefieres que ajuste algo?",
                ["style", "room_type", "dimensions", "design_concept", "total_cost", "budget", "remaining", "efficiency", "furniture_list", "recommendations"],
                language="es"
            ),
            PromptTemplate(
                "design_budget_exceeded",
                PromptCategory.DESIGN,
                PromptType.WARNING,
                "El diseño propuesto excede tu presupuesto:\n\n💰 Costo estimado: ${total_cost}\n🎯 Tu presupuesto: ${budget}\n📊 Exceso: ${excess}\n\n¿Te gustaría que:\n1. Ajuste el diseño para cumplir con tu presupuesto\n2. Te muestre opciones más económicas\n3. Priorice los muebles más importantes",
                ["total_cost", "budget", "excess"],
                language="es"
            ),
            PromptTemplate(
                "design_style_suggestions",
                PromptCategory.DESIGN,
                PromptType.SUGGESTION,
                "Para tu {room_type} de {dimensions} con presupuesto de ${budget}, te recomiendo estos estilos:\n\n{style_options}\n\nCada opción incluye estimación de costos y nivel de complejidad. ¿Cuál te interesa más?",
                ["room_type", "dimensions", "budget", "style_options"],
                language="es"
            ),
            PromptTemplate(
                "design_space_optimization",
                PromptCategory.DESIGN,
                PromptType.INSTRUCTION,
                "Análisis de tu espacio de {dimensions}:\n\n📐 **Área total:** {total_area} m²\n✅ **Área utilizada:** {used_area} m² ({efficiency}%)\n\n**Optimizaciones sugeridas:**\n{optimization_tips}\n\n**Zonas funcionales recomendadas:**\n{functional_zones}",
                ["dimensions", "total_area", "used_area", "efficiency", "optimization_tips", "functional_zones"],
                language="es"
            )
        ]
        
        # === PROMPTS PARA GENERACIÓN DE APIs ===
        api_templates = [
            PromptTemplate(
                "api_welcome",
                PromptCategory.API_GENERATION,
                PromptType.WELCOME,
                "¡Hola! Soy tu asistente para generación de APIs. Puedo ayudarte a crear APIs REST completas basadas en tus especificaciones. ¿Qué tipo de API necesitas desarrollar?",
                language="es"
            ),
            PromptTemplate(
                "api_analysis_complete",
                PromptCategory.API_GENERATION,
                PromptType.INSTRUCTION,
                "He analizado tu especificación:\n\n📊 **Complejidad:** {complexity_score}/10\n🔧 **Modelos detectados:** {models_count}\n🌐 **Endpoints detectados:** {endpoints_count}\n⚙️ **Framework recomendado:** {recommended_framework}\n⏱️ **Tiempo estimado:** {estimated_hours} horas\n\n**Elementos detectados:**\n{detected_elements}\n\n{missing_elements_warning}¿Procedo con la generación?",
                ["complexity_score", "models_count", "endpoints_count", "recommended_framework", "estimated_hours", "detected_elements", "missing_elements_warning"],
                language="es"
            ),
            PromptTemplate(
                "api_generation_complete",
                PromptCategory.API_GENERATION,
                PromptType.SUCCESS,
                "¡API generada exitosamente! 🎉\n\n**Detalles del proyecto:**\n📋 ID: {generation_id}\n⚙️ Framework: {framework}\n📁 Archivos generados: {files_count}\n📊 Modelos: {models_count}\n🌐 Endpoints: {endpoints_count}\n\n**Archivos principales:**\n{main_files}\n\n**Siguiente paso:** {next_steps}",
                ["generation_id", "framework", "files_count", "models_count", "endpoints_count", "main_files", "next_steps"],
                language="es"
            ),
            PromptTemplate(
                "api_specification_clarification",
                PromptCategory.API_GENERATION,
                PromptType.CLARIFICATION,
                "Necesito aclarar algunos puntos sobre tu especificación:\n\n{clarification_points}\n\nPor favor proporciona más detalles sobre estos aspectos para generar una API más precisa.",
                ["clarification_points"],
                language="es"
            ),
            PromptTemplate(
                "api_framework_comparison",
                PromptCategory.API_GENERATION,
                PromptType.SUGGESTION,
                "Comparación de frameworks para tu proyecto:\n\n{framework_comparison}\n\n**Recomendación:** {recommendation}\n**Razón:** {reason}\n\n¿Con qué framework prefieres continuar?",
                ["framework_comparison", "recommendation", "reason"],
                language="es"
            )
        ]
        
        # === PROMPTS GENERALES ===
        general_templates = [
            PromptTemplate(
                "general_error",
                PromptCategory.GENERAL,
                PromptType.ERROR,
                "Ocurrió un error inesperado: {error_message}\n\nPor favor intenta nuevamente. Si el problema persiste, puedes:\n1. Reformular tu solicitud\n2. Proporcionar más información\n3. Contactar soporte técnico",
                ["error_message"],
                language="es"
            ),
            PromptTemplate(
                "general_clarification",
                PromptCategory.GENERAL,
                PromptType.CLARIFICATION,
                "No estoy seguro de entender tu solicitud. ¿Podrías ser más específico sobre:\n\n{clarification_points}\n\nEsto me ayudará a asistirte mejor.",
                ["clarification_points"],
                language="es"
            ),
            PromptTemplate(
                "general_multiple_options",
                PromptCategory.GENERAL,
                PromptType.SUGGESTION,
                "Veo que tienes varias opciones disponibles:\n\n{options_list}\n\n¿Cuál prefieres o necesitas más información sobre alguna?",
                ["options_list"],
                language="es"
            ),
            PromptTemplate(
                "general_session_summary",
                PromptCategory.GENERAL,
                PromptType.INSTRUCTION,
                "Resumen de nuestra sesión:\n\n{session_summary}\n\n¿Hay algo más en lo que pueda ayudarte?",
                ["session_summary"],
                language="es"
            )
        ]
        
        # Registrar todos los templates
        all_templates = (delivery_templates + reservation_templates + 
                        design_templates + api_templates + general_templates)
        
        for template in all_templates:
            self.register_template(template)
    
    def register_template(self, template: PromptTemplate):
        """Registra un nuevo template"""
        self.templates[template.template_id] = template
    
    def get_prompt(self, template_id: str, context: Dict[str, Any] = None) -> str:
        """Obtiene prompt renderizado"""
        if template_id not in self.templates:
            raise ValueError(f"Template no encontrado: {template_id}")
        
        template = self.templates[template_id]
        context = context or {}
        
        # Agregar contexto por defecto
        default_context = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user': context.get('user', 'Usuario'),
            'agent': context.get('agent', 'Asistente')
        }
        
        # Combinar contextos
        full_context = {**default_context, **context}
        
        # Renderizar y registrar uso
        rendered_prompt = template.render(full_context)
        
        self.prompt_history.append({
            'template_id': template_id,
            'context': context,
            'rendered_prompt': rendered_prompt,
            'timestamp': datetime.now(),
            'category': template.category.value,
            'prompt_type': template.prompt_type.value
        })
        
        return rendered_prompt
    
    def get_contextual_prompt(self, category: PromptCategory, prompt_type: PromptType, 
                            context: Dict[str, Any]) -> str:
        """Obtiene prompt basado en categoría y tipo con contexto"""
        # Buscar templates que coincidan con categoría y tipo
        matching_templates = [
            t for t in self.templates.values() 
            if t.category == category and t.prompt_type == prompt_type
        ]
        
        if not matching_templates:
            # Fallback a prompts generales
            matching_templates = [
                t for t in self.templates.values() 
                if t.category == PromptCategory.GENERAL and t.prompt_type == prompt_type
            ]
        
        if not matching_templates:
            return "Lo siento, no puedo procesar tu solicitud en este momento."
        
        # Seleccionar template con mayor prioridad
        template = max(matching_templates, key=lambda t: t.priority)
        
        return self.get_prompt(template.template_id, context)
    
    def generate_dynamic_prompt(self, scenario: str, context_vars: Dict[str, Any]) -> str:
        """Genera prompt dinámico basado en escenario"""
        scenario_templates = {
            'delivery_order_multiple_items': """
            Tu pedido incluye {item_count} artículos:
            
            {items_list}
            
            Restaurante: {restaurant_name}
            Subtotal: ${subtotal}
            Delivery: ${delivery_fee}
            Total: ${total}
            
            ¿Confirmas tu pedido?
            """,
            
            'reservation_group_large': """
            Para grupos de {party_size} personas, recomiendo:
            
            {restaurant_suggestions}
            
            💡 Tip: Para grupos grandes es mejor llamar directamente al restaurante.
            """,
            
            'design_budget_optimization': """
            Optimizando tu presupuesto de ${budget}:
            
            Esenciales (60%): ${essential_budget}
            {essential_items}
            
            Complementarios (40%): ${complementary_budget}
            {complementary_items}
            
            Esta distribución maximiza el impacto visual de tu inversión.
            """
        }
        
        template = scenario_templates.get(scenario)
        if template:
            return template.format(**context_vars)
        
        return self.get_contextual_prompt(
            PromptCategory.GENERAL, 
            PromptType.INSTRUCTION, 
            context_vars
        )
    
    def format_list_items(self, items: List[str], style: str = "bullet") -> str:
        """Formatea listas para prompts"""
        if style == "bullet":
            return '\n'.join(f"• {item}" for item in items)
        elif style == "numbered":
            return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))
        elif style == "emoji_bullet":
            return '\n'.join(f"🔸 {item}" for item in items)
        else:
            return '\n'.join(items)
    
    def format_restaurant_list(self, restaurants: List[Dict[str, Any]]) -> str:
        """Formatea lista de restaurantes"""
        formatted_items = []
        for resto in restaurants:
            item = f"🏪 **{resto['name']}**"
            if resto.get('cuisine'):
                item += f" ({resto['cuisine']})"
            if resto.get('rating'):
                item += f" ⭐ {resto['rating']}"
            if resto.get('delivery_time'):
                item += f" 🚚 {resto['delivery_time']} min"
            if resto.get('price'):
                item += f" 💰 {resto['price']}"
            formatted_items.append(item)
        
        return '\n'.join(formatted_items)
    
    def format_menu_items(self, menu_items: List[Dict[str, Any]]) -> str:
        """Formatea lista de items del menú"""
        formatted_items = []
        for item in menu_items:
            formatted_item = f"🍽️ **{item['name']}**"
            if item.get('price'):
                formatted_item += f" - ${item['price']}"
            if item.get('description'):
                formatted_item += f"\n   {item['description']}"
            formatted_items.append(formatted_item)
        
        return '\n\n'.join(formatted_items)
    
    def format_furniture_list(self, furniture_items: List[Dict[str, Any]]) -> str:
        """Formatea lista de muebles"""
        formatted_items = []
        for item in furniture_items:
            formatted_item = f"🪑 **{item['name']}**"
            if item.get('quantity', 1) > 1:
                formatted_item += f" (x{item['quantity']})"
            if item.get('total_price'):
                formatted_item += f" - ${item['total_price']}"
            formatted_items.append(formatted_item)
        
        return '\n'.join(formatted_items)
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso de prompts"""
        stats = {
            'total_prompts_used': len(self.prompt_history),
            'templates_registered': len(self.templates),
            'most_used_template': None,
            'usage_by_category': {},
            'usage_by_type': {},
            'recent_activity': []
        }
        
        # Calcular template más usado
        if self.templates:
            most_used = max(self.templates.values(), key=lambda t: t.usage_count)
            stats['most_used_template'] = {
                'id': most_used.template_id,
                'usage_count': most_used.usage_count
            }
        
        # Estadísticas por categoría
        for prompt in self.prompt_history:
            category = prompt['category']
            stats['usage_by_category'][category] = stats['usage_by_category'].get(category, 0) + 1
        
        # Estadísticas por tipo
        for prompt in self.prompt_history:
            prompt_type = prompt['prompt_type']
            stats['usage_by_type'][prompt_type] = stats['usage_by_type'].get(prompt_type, 0) + 1
        
        # Actividad reciente (últimos 10)
        stats['recent_activity'] = self.prompt_history[-10:] if len(self.prompt_history) > 10 else self.prompt_history
        
        return stats
    
    def search_templates(self, query: str) -> List[PromptTemplate]:
        """Busca templates por contenido"""
        results = []
        query_lower = query.lower()
        
        for template in self.templates.values():
            if (query_lower in template.template.lower() or 
                query_lower in template.template_id.lower() or
                any(query_lower in var.lower() for var in template.variables)):
                results.append(template)
        
        return results


# Función de demostración
def demo_prompt_manager():
    """Demuestra la funcionalidad del gestor de prompts"""
    manager = PromptManager()
    
    print("=== DEMO: SISTEMA DE GESTIÓN DE PROMPTS ===\n")
    
    # Caso 1: Prompt de bienvenida para delivery
    print("1. Prompt de bienvenida para delivery:")
    welcome_prompt = manager.get_prompt("delivery_welcome")
    print(welcome_prompt)
    print("\n" + "="*50 + "\n")
    
    # Caso 2: Sugerencias de restaurantes con contexto
    print("2. Sugerencias de restaurantes:")
    restaurants = [
        {"name": "Pizza Palace", "cuisine": "Italiana", "rating": 4.5, "delivery_time": 30, "price": "$$"},
        {"name": "Sushi Zen", "cuisine": "Japonesa", "rating": 4.8, "delivery_time": 40, "price": "$$$"}
    ]
    
    context = {
        "cuisine_type": "italiana",
        "restaurant_list": manager.format_restaurant_list(restaurants)
    }
    
    suggestion_prompt = manager.get_prompt("delivery_restaurant_suggestions", context)
    print(suggestion_prompt)
    print("\n" + "="*50 + "\n")
    
    # Caso 3: Confirmación de reserva
    print("3. Confirmación de reserva:")
    reservation_context = {
        "restaurant_name": "La Bella Italiana",
        "party_size": 4,
        "date": "2024-12-15",
        "time": "20:00",
        "reservation_id": "RES-0001",
        "special_requests_text": "🎂 Celebración de cumpleaños incluida.\n"
    }
    
    confirmation_prompt = manager.get_prompt("reservation_confirmed", reservation_context)
    print(confirmation_prompt)
    print("\n" + "="*50 + "\n")
    
    # Caso 4: Propuesta de diseño
    print("4. Propuesta de diseño:")
    furniture_items = [
        {"name": "Cama King", "quantity": 1, "total_price": 1200},
        {"name": "Mesa de Noche", "quantity": 2, "total_price": 360},
        {"name": "Armario", "quantity": 1, "total_price": 800}
    ]
    
    design_context = {
        "style": "moderno",
        "room_type": "dormitorio",
        "dimensions": "4x5m",
        "design_concept": "Minimalista y funcional",
        "total_cost": 2360,
        "budget": 3000,
        "remaining": 640,
        "efficiency": 75.2,
        "furniture_list": manager.format_furniture_list(furniture_items),
        "recommendations": "• Agregar iluminación LED\n• Considerar alfombra para mayor calidez"
    }
    
    design_prompt = manager.get_prompt("design_proposal", design_context)
    print(design_prompt)
    print("\n" + "="*50 + "\n")
    
    # Caso 5: Prompt contextual dinámico
    print("5. Prompt contextual usando categoría y tipo:")
    contextual_prompt = manager.get_contextual_prompt(
        PromptCategory.API_GENERATION,
        PromptType.SUCCESS,
        {
            "generation_id": "API-0001",
            "framework": "FastAPI",
            "files_count": 5,
            "models_count": 3,
            "endpoints_count": 8,
            "main_files": "• main.py\n• models.py\n• schemas.py",
            "next_steps": "Instalar dependencias con 'pip install -r requirements.txt'"
        }
    )
    print(contextual_prompt)
    print("\n" + "="*50 + "\n")
    
    # Caso 6: Estadísticas de uso
    print("6. Estadísticas de uso:")
    stats = manager.get_usage_statistics()
    print(f"Templates registrados: {stats['templates_registered']}")
    print(f"Prompts utilizados: {stats['total_prompts_used']}")
    if stats['most_used_template']:
        print(f"Template más usado: {stats['most_used_template']['id']} ({stats['most_used_template']['usage_count']} veces)")
    
    print("\nUso por categoría:")
    for category, count in stats['usage_by_category'].items():
        print(f"  - {category}: {count}")
    
    print("\nUso por tipo:")
    for prompt_type, count in stats['usage_by_type'].items():
        print(f"  - {prompt_type}: {count}")


if __name__ == "__main__":
    demo_prompt_manager()