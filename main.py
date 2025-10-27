"""
Script principal de demostración de agentes de IA
Integra y demuestra todos los agentes desarrollados
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, Any

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports de agentes
from agents.delivery_agent import DeliveryAgent, demo_delivery_agent
from agents.reservation_agent import RestaurantReservationAgent, demo_reservation_agent
from agents.room_design_agent import RoomDesignAgent, demo_room_design_agent
from agents.api_generation_agent import APIGenerationAgent, demo_api_generation_agent

# Imports de sistemas core
from core.prompt_manager import PromptManager, PromptCategory, PromptType, demo_prompt_manager
from core.execution_monitor import ExecutionMonitor, ExecutionStatus, monitor_execution


class AgentOrchestrator:
    """Orquestador principal que coordina todos los agentes"""
    
    def __init__(self):
        # Inicializar sistemas core
        self.prompt_manager = PromptManager()
        self.execution_monitor = ExecutionMonitor()
        
        # Inicializar agentes
        self.delivery_agent = DeliveryAgent()
        self.reservation_agent = RestaurantReservationAgent()
        self.design_agent = RoomDesignAgent()
        self.api_agent = APIGenerationAgent()
        
        # Configurar monitoreo
        self._setup_monitoring()
        
        print("🤖 Orquestador de Agentes inicializado correctamente")
        print(f"📊 Sistemas activos: {len(self._get_active_systems())}")
    
    def _setup_monitoring(self):
        """Configura el monitoreo para todos los agentes"""
        def log_execution(record):
            if record.status == ExecutionStatus.ERROR:
                print(f"❌ Error en {record.agent_name}: {record.error_message}")
            elif record.execution_time and record.execution_time > 5:
                print(f"⚠️  Respuesta lenta en {record.agent_name}: {record.execution_time:.2f}s")
        
        self.execution_monitor.add_listener(log_execution)
    
    def _get_active_systems(self) -> list:
        """Obtiene lista de sistemas activos"""
        return [
            "Delivery Agent",
            "Reservation Agent", 
            "Room Design Agent",
            "API Generation Agent",
            "Prompt Manager",
            "Execution Monitor"
        ]
    
    def process_user_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Procesa una solicitud de usuario y la dirige al agente apropiado"""
        
        # Aplicar monitoreo manualmente
        execution_id = self.execution_monitor.start_execution(
            "orchestrator", "coordination", {"request": request[:200]}
        )
        
        try:
            result = self._internal_process_request(request, context)
            self.execution_monitor.end_execution(
                execution_id, {"response_type": type(result).__name__}, 
                ExecutionStatus.SUCCESS
            )
            return result
        except Exception as e:
            self.execution_monitor.end_execution(
                execution_id, None, ExecutionStatus.ERROR, str(e)
            )
            raise
    
    def _internal_process_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Lógica interna de procesamiento de solicitudes"""
        request_lower = request.lower()
        context = context or {}
        
        # Clasificar tipo de solicitud
        if any(keyword in request_lower for keyword in ['delivery', 'comida', 'pedir', 'restaurante', 'entrega']):
            return self._handle_delivery_request(request, context)
        
        elif any(keyword in request_lower for keyword in ['reserva', 'mesa', 'reservar', 'cena']):
            return self._handle_reservation_request(request, context)
        
        elif any(keyword in request_lower for keyword in ['diseño', 'habitación', 'decorar', 'muebles', 'diseñar']):
            return self._handle_design_request(request, context)
        
        elif any(keyword in request_lower for keyword in ['api', 'código', 'programar', 'desarrollar', 'generar']):
            return self._handle_api_request(request, context)
        
        else:
            return self._handle_general_request(request, context)
    
    def _handle_delivery_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja solicitudes de delivery"""
        execution_id = self.execution_monitor.start_execution(
            "delivery_agent", "delivery", {"request": request[:200]}
        )
        
        try:
            response = self.delivery_agent.process_delivery_request(request)
            
            # Enriquecer respuesta con prompt contextual
            if response.get('action') == 'show_restaurants':
                prompt_context = {
                    "cuisine_type": context.get('cuisine_preference', 'variada'),
                    "restaurant_list": self.prompt_manager.format_restaurant_list(
                        response.get('restaurants', [])
                    )
                }
                enhanced_response = self.prompt_manager.get_prompt(
                    "delivery_restaurant_suggestions", prompt_context
                )
                response['enhanced_message'] = enhanced_response
            
            self.execution_monitor.end_execution(
                execution_id, response, ExecutionStatus.SUCCESS
            )
            
            return {
                'agent': 'delivery',
                'response': response,
                'suggestions': ['Ver menú', 'Filtrar por precio', 'Rastrear pedido']
            }
            
        except Exception as e:
            self.execution_monitor.end_execution(
                execution_id, None, ExecutionStatus.ERROR, str(e)
            )
            return {
                'agent': 'delivery',
                'error': str(e),
                'response': {'response': 'Lo siento, hubo un problema con el servicio de delivery.'}
            }
    
    def _handle_reservation_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja solicitudes de reservas"""
        execution_id = self.execution_monitor.start_execution(
            "reservation_agent", "reservation", {"request": request[:200]}
        )
        
        try:
            response = self.reservation_agent.handle_reservation_request(request)
            
            # Enriquecer con prompts contextuales
            if response.get('action') == 'reservation_confirmed':
                reservation = response.get('reservation', {})
                prompt_context = {
                    "restaurant_name": reservation.get('restaurant_name', 'Restaurante'),
                    "party_size": reservation.get('party_size', 0),
                    "date": reservation.get('date', ''),
                    "time": reservation.get('time', ''),
                    "reservation_id": reservation.get('id', ''),
                    "special_requests_text": "🎉 Sin solicitudes especiales.\n" if not reservation.get('special_requests') else ""
                }
                enhanced_response = self.prompt_manager.get_prompt(
                    "reservation_confirmed", prompt_context
                )
                response['enhanced_message'] = enhanced_response
            
            self.execution_monitor.end_execution(
                execution_id, response, ExecutionStatus.SUCCESS
            )
            
            return {
                'agent': 'reservation',
                'response': response,
                'suggestions': ['Modificar reserva', 'Cancelar reserva', 'Ver restaurantes']
            }
            
        except Exception as e:
            self.execution_monitor.end_execution(
                execution_id, None, ExecutionStatus.ERROR, str(e)
            )
            return {
                'agent': 'reservation',
                'error': str(e),
                'response': {'response': 'Lo siento, hubo un problema con el servicio de reservas.'}
            }
    
    def _handle_design_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja solicitudes de diseño"""
        execution_id = self.execution_monitor.start_execution(
            "design_agent", "design", {"request": request[:200]}
        )
        
        try:
            # Parsear parámetros básicos del request
            room_type = context.get('room_type', 'dormitorio_grande')
            dimensions = context.get('dimensions', '4x5m')
            style = context.get('style', 'moderno')
            budget = context.get('budget', 3000)
            
            response = self.design_agent.generate_design(
                room_type=room_type,
                room_dimensions=dimensions,
                style_preference=style,
                budget=budget
            )
            
            # Enriquecer con prompts contextuales si fue exitoso
            if 'error' not in response:
                prompt_context = {
                    "style": response.get('style', style),
                    "room_type": response.get('room_type', room_type),
                    "dimensions": response.get('dimensions', {}).get('width', 0),
                    "design_concept": "Diseño optimizado para funcionalidad y estética",
                    "total_cost": response.get('total_cost', 0),
                    "budget": response.get('budget_remaining', 0) + response.get('total_cost', 0),
                    "remaining": response.get('budget_remaining', 0),
                    "efficiency": response.get('area_efficiency', 0),
                    "furniture_list": self.prompt_manager.format_furniture_list(
                        response.get('shopping_list', [])[:5]  # Top 5 items
                    ),
                    "recommendations": '\n'.join([f"• {rec}" for rec in response.get('recommendations', [])[:3]])
                }
                enhanced_response = self.prompt_manager.get_prompt(
                    "design_proposal", prompt_context
                )
                response['enhanced_message'] = enhanced_response
            
            self.execution_monitor.end_execution(
                execution_id, response, ExecutionStatus.SUCCESS
            )
            
            return {
                'agent': 'design',
                'response': response,
                'suggestions': ['Ajustar presupuesto', 'Cambiar estilo', 'Ver alternativas']
            }
            
        except Exception as e:
            self.execution_monitor.end_execution(
                execution_id, None, ExecutionStatus.ERROR, str(e)
            )
            return {
                'agent': 'design',
                'error': str(e),
                'response': {'error': 'Lo siento, hubo un problema con el servicio de diseño.'}
            }
    
    def _handle_api_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja solicitudes de generación de APIs"""
        execution_id = self.execution_monitor.start_execution(
            "api_agent", "api_generation", {"request": request[:200]}
        )
        
        try:
            # Usar especificación de ejemplo si no se proporciona
            specification = context.get('specification', request)
            framework = context.get('framework', 'fastapi')
            
            response = self.api_agent.generate_api(
                specification=specification,
                framework=framework,
                format_type='natural'
            )
            
            # Enriquecer con prompts contextuales si fue exitoso
            if 'error' not in response:
                prompt_context = {
                    "generation_id": response.get('generation_id', 'API-DEMO'),
                    "framework": response.get('framework', framework),
                    "files_count": len(response.get('generated_code', {})),
                    "models_count": response.get('models_count', 0),
                    "endpoints_count": response.get('endpoints_count', 0),
                    "main_files": '\n'.join([f"• {filename}" for filename in list(response.get('generated_code', {}).keys())[:5]]),
                    "next_steps": "1. Revisar código generado\n2. Instalar dependencias\n3. Ejecutar aplicación"
                }
                enhanced_response = self.prompt_manager.get_prompt(
                    "api_generation_complete", prompt_context
                )
                response['enhanced_message'] = enhanced_response
            
            self.execution_monitor.end_execution(
                execution_id, response, ExecutionStatus.SUCCESS
            )
            
            return {
                'agent': 'api_generation',
                'response': response,
                'suggestions': ['Analizar código', 'Cambiar framework', 'Generar tests']
            }
            
        except Exception as e:
            self.execution_monitor.end_execution(
                execution_id, None, ExecutionStatus.ERROR, str(e)
            )
            return {
                'agent': 'api_generation',
                'error': str(e),
                'response': {'error': 'Lo siento, hubo un problema con la generación de API.'}
            }
    
    def _handle_general_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja solicitudes generales"""
        clarification_points = [
            "¿Necesitas ayuda con delivery de comida?",
            "¿Quieres hacer una reserva en un restaurante?", 
            "¿Buscas diseñar una habitación?",
            "¿Necesitas generar una API?"
        ]
        
        prompt_context = {
            "clarification_points": '\n'.join([f"{i+1}. {point}" for i, point in enumerate(clarification_points)])
        }
        
        response_message = self.prompt_manager.get_prompt(
            "general_clarification", prompt_context
        )
        
        return {
            'agent': 'general',
            'response': {'response': response_message},
            'suggestions': ['Delivery', 'Reservas', 'Diseño', 'API']
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene estado del sistema"""
        overview = self.execution_monitor.get_system_overview(hours=1)
        prompt_stats = self.prompt_manager.get_usage_statistics()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'active_agents': len(self._get_active_systems()),
            'total_executions': overview.get('total_executions', 0),
            'success_rate': overview.get('overall_success_rate', 0),
            'avg_response_time': overview.get('avg_response_time', 0),
            'prompt_templates': prompt_stats.get('templates_registered', 0),
            'prompt_usage': prompt_stats.get('total_prompts_used', 0),
            'most_active_agent': overview.get('most_active_agent'),
            'system_health': 'healthy' if overview.get('overall_success_rate', 0) > 0.8 else 'degraded'
        }


def run_interactive_demo():
    """Ejecuta demo interactivo con el usuario"""
    orchestrator = AgentOrchestrator()
    
    print("\n" + "="*60)
    print("🚀 DEMO INTERACTIVO - AGENTES DE IA")
    print("="*60)
    print("\nComandos disponibles:")
    print("1. 'delivery' - Probar agente de delivery")
    print("2. 'reserva' - Probar agente de reservas") 
    print("3. 'diseño' - Probar agente de diseño")
    print("4. 'api' - Probar agente de API")
    print("5. 'status' - Ver estado del sistema")
    print("6. 'exit' - Salir")
    print("\nO escribe cualquier solicitud en lenguaje natural...")
    print("-"*60)
    
    while True:
        try:
            user_input = input("\n🤖 Ingresa tu solicitud: ").strip()
            
            if user_input.lower() in ['exit', 'salir', 'quit']:
                print("👋 ¡Hasta luego!")
                break
            
            if user_input.lower() == 'status':
                status = orchestrator.get_system_status()
                print(f"\n📊 Estado del Sistema:")
                print(f"  🟢 Agentes activos: {status['active_agents']}")
                print(f"  📈 Ejecuciones totales: {status['total_executions']}")
                print(f"  ✅ Tasa de éxito: {status['success_rate']:.1%}")
                print(f"  ⏱️  Tiempo promedio: {status['avg_response_time']:.2f}s")
                print(f"  💬 Prompts utilizados: {status['prompt_usage']}")
                print(f"  🏆 Agente más activo: {status['most_active_agent']}")
                print(f"  🔋 Salud del sistema: {status['system_health']}")
                continue
            
            if not user_input:
                continue
            
            print(f"\n🔄 Procesando solicitud...")
            start_time = time.time()
            
            # Procesar solicitud
            result = orchestrator.process_user_request(user_input)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Mostrar resultado
            print(f"\n🤖 Agente: {result['agent']}")
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                response = result['response']
                
                # Mostrar mensaje mejorado si existe
                if response.get('enhanced_message'):
                    print(f"💬 Respuesta:\n{response['enhanced_message']}")
                else:
                    print(f"💬 Respuesta: {response.get('response', 'Sin respuesta')}")
                
                # Mostrar información adicional según el tipo
                if result['agent'] == 'delivery' and response.get('restaurants'):
                    print(f"\n🏪 Restaurantes encontrados: {len(response['restaurants'])}")
                
                elif result['agent'] == 'reservation' and response.get('reservation'):
                    reservation = response['reservation']
                    print(f"\n📋 ID de reserva: {reservation.get('id', 'N/A')}")
                
                elif result['agent'] == 'design' and response.get('total_cost'):
                    print(f"\n💰 Costo total: ${response['total_cost']:.0f}")
                    print(f"📐 Eficiencia del espacio: {response.get('area_efficiency', 0):.1f}%")
                
                elif result['agent'] == 'api_generation' and response.get('generated_code'):
                    print(f"\n📁 Archivos generados: {len(response['generated_code'])}")
                    print(f"🔧 Framework: {response.get('framework', 'N/A')}")
                
                # Mostrar sugerencias
                if result.get('suggestions'):
                    print(f"\n💡 Sugerencias:")
                    for suggestion in result['suggestions']:
                        print(f"  • {suggestion}")
            
            print(f"\n⏱️  Tiempo de procesamiento: {processing_time:.2f}s")
            print("-"*60)
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")


def run_complete_demo():
    """Ejecuta demostración completa de todos los componentes"""
    print("🚀 DEMOSTRACIÓN COMPLETA DE AGENTES DE IA")
    print("="*60)
    
    # Demo individual de cada agente
    print("\n1️⃣  AGENTE DE DELIVERY")
    print("-" * 30)
    demo_delivery_agent()
    
    print("\n2️⃣  AGENTE DE RESERVAS")
    print("-" * 30)
    demo_reservation_agent()
    
    print("\n3️⃣  AGENTE DE DISEÑO")
    print("-" * 30)
    demo_room_design_agent()
    
    print("\n4️⃣  AGENTE DE GENERACIÓN DE APIs")
    print("-" * 30)
    demo_api_generation_agent()
    
    print("\n5️⃣  SISTEMA DE PROMPTS")
    print("-" * 30)
    demo_prompt_manager()
    
    print("\n6️⃣  SISTEMA DE MONITOREO")
    print("-" * 30)
    from core.execution_monitor import demo_execution_monitor
    demo_execution_monitor()
    
    print("\n7️⃣  ORQUESTADOR INTEGRADO")
    print("-" * 30)
    
    # Demo del orquestador
    orchestrator = AgentOrchestrator()
    
    test_requests = [
        "Quiero pedir comida italiana para 2 personas",
        "Necesito reservar mesa para 4 personas el viernes",
        "Quiero diseñar mi dormitorio de 4x5m con presupuesto de $3000",
        "Necesito generar una API para gestión de productos"
    ]
    
    for request in test_requests:
        print(f"\n📝 Solicitud: {request}")
        result = orchestrator.process_user_request(request)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"🤖 Agente: {result['agent']}")
            response = result['response']
            if response.get('enhanced_message'):
                print(f"💬 Respuesta: {response['enhanced_message'][:200]}...")
            else:
                print(f"💬 Respuesta: {response.get('response', 'Sin respuesta')[:200]}...")
    
    # Estado final del sistema
    print("\n📊 ESTADO FINAL DEL SISTEMA")
    print("-" * 30)
    status = orchestrator.get_system_status()
    for key, value in status.items():
        print(f"{key}: {value}")


def main():
    """Función principal"""
    print("🤖 SISTEMA DE AGENTES DE IA PARA CASOS REALES")
    print("=" * 50)
    print("\nSelecciona el modo de demostración:")
    print("1. Demo interactivo (recomendado)")
    print("2. Demo completo automático")
    print("3. Salir")
    
    while True:
        try:
            choice = input("\nSelecciona una opción (1-3): ").strip()
            
            if choice == "1":
                run_interactive_demo()
                break
            elif choice == "2":
                run_complete_demo()
                break
            elif choice == "3":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida. Por favor selecciona 1, 2 o 3.")
                
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break


if __name__ == "__main__":
    main()