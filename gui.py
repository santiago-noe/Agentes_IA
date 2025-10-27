"""
Interfaz gráfica para el sistema de agentes de IA
Proporciona una GUI sencilla para interactuar con todos los agentes
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
from datetime import datetime
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports de agentes
from agents.delivery_agent import DeliveryAgent
from agents.reservation_agent import RestaurantReservationAgent
from agents.room_design_agent import RoomDesignAgent
from agents.api_generation_agent import APIGenerationAgent

# Imports de sistemas core
from core.prompt_manager import PromptManager, PromptCategory, PromptType
from core.execution_monitor import ExecutionMonitor, ExecutionStatus


class AgentGUI:
    """Interfaz gráfica principal para los agentes de IA"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Sistema de Agentes de IA")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Inicializar sistemas
        self.prompt_manager = PromptManager()
        self.execution_monitor = ExecutionMonitor()
        
        # Inicializar agentes
        self.delivery_agent = DeliveryAgent()
        self.reservation_agent = RestaurantReservationAgent()
        self.design_agent = RoomDesignAgent()
        self.api_agent = APIGenerationAgent()
        
        # Variable para almacenar historial
        self.conversation_history = []
        
        # Crear interfaz
        self.create_widgets()
        
        # Configurar monitoreo
        self.setup_monitoring()
    
    def setup_monitoring(self):
        """Configura el monitoreo de agentes"""
        def log_execution(record):
            if record.status == ExecutionStatus.ERROR:
                self.add_system_message(f"❌ Error en {record.agent_name}: {record.error_message}")
            elif record.execution_time and record.execution_time > 3:
                self.add_system_message(f"⚠️ Respuesta lenta en {record.agent_name}: {record.execution_time:.2f}s")
        
        self.execution_monitor.add_listener(log_execution)
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = tk.Label(main_frame, text="🤖 Sistema de Agentes de IA", 
                              font=('Arial', 16, 'bold'), bg='#f0f0f0')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Panel izquierdo - Controles
        control_frame = ttk.LabelFrame(main_frame, text="🎮 Controles", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Selector de agente
        ttk.Label(control_frame, text="Seleccionar Agente:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.agent_var = tk.StringVar(value="auto")
        agent_combo = ttk.Combobox(control_frame, textvariable=self.agent_var, state="readonly", width=20)
        agent_combo['values'] = ("auto", "delivery", "reservas", "diseño", "api")
        agent_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Área de entrada de texto
        ttk.Label(control_frame, text="Tu solicitud:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.input_text = tk.Text(control_frame, height=4, width=30, wrap=tk.WORD)
        self.input_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botón enviar
        self.send_button = ttk.Button(control_frame, text="🚀 Enviar", command=self.send_request)
        self.send_button.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Ejemplos de solicitudes
        examples_frame = ttk.LabelFrame(control_frame, text="📝 Ejemplos", padding="5")
        examples_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        examples = [
            ("🍕 Delivery", "Quiero pedir comida italiana para 2 personas"),
            ("🍽️ Reserva", "Mesa para 4 personas el viernes a las 8 PM"),
            ("🏠 Diseño", "Diseñar dormitorio 4x5m, presupuesto $3000"),
            ("⚙️ API", "Crear API para gestión de productos con CRUD")
        ]
        
        for i, (title, example) in enumerate(examples):
            btn = ttk.Button(examples_frame, text=title, 
                           command=lambda e=example: self.set_example(e))
            btn.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Botones de acción adicionales
        action_frame = ttk.LabelFrame(control_frame, text="🔧 Acciones", padding="5")
        action_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(action_frame, text="📊 Estado Sistema", 
                  command=self.show_system_status).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(action_frame, text="🗑️ Limpiar Chat", 
                  command=self.clear_chat).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(action_frame, text="💾 Exportar Chat", 
                  command=self.export_chat).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Panel derecho - Chat
        chat_frame = ttk.LabelFrame(main_frame, text="💬 Conversación", padding="10")
        chat_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Área de chat con scroll
        self.chat_area = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED,
                                                  font=('Consolas', 10), bg='white')
        self.chat_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para colores
        self.chat_area.tag_configure("user", foreground="blue", font=('Consolas', 10, 'bold'))
        self.chat_area.tag_configure("agent", foreground="green", font=('Consolas', 10))
        self.chat_area.tag_configure("system", foreground="orange", font=('Consolas', 9, 'italic'))
        self.chat_area.tag_configure("error", foreground="red", font=('Consolas', 10, 'bold'))
        
        # Mensaje de bienvenida
        self.add_agent_message("¡Hola! Soy tu asistente de IA. Puedes solicitar ayuda con delivery, reservas, diseño de habitaciones o generación de APIs. ¿En qué puedo ayudarte?")
        
        # Bind Enter key
        self.input_text.bind('<Control-Return>', lambda e: self.send_request())
    
    def set_example(self, example_text):
        """Establece un ejemplo en el área de texto"""
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, example_text)
    
    def add_message(self, message, tag="agent"):
        """Agrega un mensaje al área de chat"""
        self.chat_area.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if tag == "user":
            self.chat_area.insert(tk.END, f"[{timestamp}] 👤 Tú: ", tag)
        elif tag == "agent":
            self.chat_area.insert(tk.END, f"[{timestamp}] 🤖 Agente: ", tag)
        elif tag == "system":
            self.chat_area.insert(tk.END, f"[{timestamp}] 🔧 Sistema: ", tag)
        elif tag == "error":
            self.chat_area.insert(tk.END, f"[{timestamp}] ❌ Error: ", tag)
        
        self.chat_area.insert(tk.END, f"{message}\n\n", tag)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
        
        # Actualizar historial
        self.conversation_history.append({
            'timestamp': timestamp,
            'type': tag,
            'message': message
        })
    
    def add_user_message(self, message):
        """Agrega mensaje del usuario"""
        self.add_message(message, "user")
    
    def add_agent_message(self, message):
        """Agrega mensaje del agente"""
        self.add_message(message, "agent")
    
    def add_system_message(self, message):
        """Agrega mensaje del sistema"""
        self.add_message(message, "system")
    
    def add_error_message(self, message):
        """Agrega mensaje de error"""
        self.add_message(message, "error")
    
    def send_request(self):
        """Envía la solicitud al agente apropiado"""
        user_input = self.input_text.get(1.0, tk.END).strip()
        
        if not user_input:
            messagebox.showwarning("Entrada vacía", "Por favor ingresa una solicitud.")
            return
        
        # Limpiar área de entrada
        self.input_text.delete(1.0, tk.END)
        
        # Mostrar mensaje del usuario
        self.add_user_message(user_input)
        
        # Deshabilitar botón mientras procesa
        self.send_button.config(state="disabled", text="🔄 Procesando...")
        
        # Procesar en hilo separado para no bloquear la UI
        def process_request():
            try:
                # Determinar agente
                selected_agent = self.agent_var.get()
                
                if selected_agent == "auto":
                    result = self.process_auto_request(user_input)
                else:
                    result = self.process_specific_agent(user_input, selected_agent)
                
                # Mostrar resultado en UI thread
                self.root.after(0, lambda: self.display_result(result))
                
            except Exception as e:
                self.root.after(0, lambda: self.add_error_message(f"Error inesperado: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.send_button.config(state="normal", text="🚀 Enviar"))
        
        # Ejecutar en hilo separado
        threading.Thread(target=process_request, daemon=True).start()
    
    def process_auto_request(self, user_input):
        """Procesa solicitud con detección automática de agente"""
        request_lower = user_input.lower()
        
        # Clasificar solicitud
        if any(keyword in request_lower for keyword in ['delivery', 'comida', 'pedir', 'restaurante', 'entrega']):
            return self.process_delivery_request(user_input)
        elif any(keyword in request_lower for keyword in ['reserva', 'mesa', 'reservar', 'cena']):
            return self.process_reservation_request(user_input)
        elif any(keyword in request_lower for keyword in ['diseño', 'habitación', 'decorar', 'muebles', 'diseñar']):
            return self.process_design_request(user_input)
        elif any(keyword in request_lower for keyword in ['api', 'código', 'programar', 'desarrollar', 'generar']):
            return self.process_api_request(user_input)
        else:
            return {
                'agent': 'general',
                'response': 'No estoy seguro de qué tipo de ayuda necesitas. ¿Podrías ser más específico? Puedo ayudarte con:\n\n🍕 Delivery de comida\n🍽️ Reservas en restaurantes\n🏠 Diseño de habitaciones\n⚙️ Generación de APIs'
            }
    
    def process_specific_agent(self, user_input, agent_type):
        """Procesa solicitud con agente específico"""
        if agent_type == "delivery":
            return self.process_delivery_request(user_input)
        elif agent_type == "reservas":
            return self.process_reservation_request(user_input)
        elif agent_type == "diseño":
            return self.process_design_request(user_input)
        elif agent_type == "api":
            return self.process_api_request(user_input)
        else:
            return {'agent': 'error', 'response': 'Agente no reconocido'}
    
    def process_delivery_request(self, user_input):
        """Procesa solicitud de delivery"""
        execution_id = self.execution_monitor.start_execution(
            "delivery_agent", "delivery", {"request": user_input[:200]}
        )
        
        try:
            response = self.delivery_agent.process_delivery_request(user_input)
            
            self.execution_monitor.end_execution(
                execution_id, response, ExecutionStatus.SUCCESS
            )
            
            return {
                'agent': 'delivery',
                'response': self.format_delivery_response(response),
                'raw_response': response
            }
        except Exception as e:
            self.execution_monitor.end_execution(
                execution_id, None, ExecutionStatus.ERROR, str(e)
            )
            return {'agent': 'delivery', 'response': f'Error en delivery: {str(e)}'}
    
    def process_reservation_request(self, user_input):
        """Procesa solicitud de reserva"""
        execution_id = self.execution_monitor.start_execution(
            "reservation_agent", "reservation", {"request": user_input[:200]}
        )
        
        try:
            response = self.reservation_agent.handle_reservation_request(user_input)
            
            self.execution_monitor.end_execution(
                execution_id, response, ExecutionStatus.SUCCESS
            )
            
            return {
                'agent': 'reservas',
                'response': self.format_reservation_response(response),
                'raw_response': response
            }
        except Exception as e:
            self.execution_monitor.end_execution(
                execution_id, None, ExecutionStatus.ERROR, str(e)
            )
            return {'agent': 'reservas', 'response': f'Error en reservas: {str(e)}'}
    
    def process_design_request(self, user_input):
        """Procesa solicitud de diseño"""
        execution_id = self.execution_monitor.start_execution(
            "design_agent", "design", {"request": user_input[:200]}
        )
        
        try:
            # Parsear parámetros básicos (valores por defecto)
            response = self.design_agent.generate_design(
                room_type="dormitorio_grande",
                room_dimensions="4x5m",
                style_preference="moderno",
                budget=3000
            )
            
            self.execution_monitor.end_execution(
                execution_id, response, ExecutionStatus.SUCCESS
            )
            
            return {
                'agent': 'diseño',
                'response': self.format_design_response(response),
                'raw_response': response
            }
        except Exception as e:
            self.execution_monitor.end_execution(
                execution_id, None, ExecutionStatus.ERROR, str(e)
            )
            return {'agent': 'diseño', 'response': f'Error en diseño: {str(e)}'}
    
    def process_api_request(self, user_input):
        """Procesa solicitud de API"""
        execution_id = self.execution_monitor.start_execution(
            "api_agent", "api_generation", {"request": user_input[:200]}
        )
        
        try:
            response = self.api_agent.generate_api(
                specification=user_input,
                framework='fastapi',
                format_type='natural'
            )
            
            self.execution_monitor.end_execution(
                execution_id, response, ExecutionStatus.SUCCESS
            )
            
            return {
                'agent': 'api',
                'response': self.format_api_response(response),
                'raw_response': response
            }
        except Exception as e:
            self.execution_monitor.end_execution(
                execution_id, None, ExecutionStatus.ERROR, str(e)
            )
            return {'agent': 'api', 'response': f'Error en API: {str(e)}'}
    
    def format_delivery_response(self, response):
        """Formatea respuesta del agente de delivery"""
        formatted = f"🍕 {response.get('response', 'Sin respuesta')}\n"
        
        if response.get('restaurants'):
            formatted += "\n🏪 Restaurantes encontrados:\n"
            for restaurant in response['restaurants'][:3]:  # Top 3
                formatted += f"  • {restaurant['name']} ({restaurant.get('cuisine', ['N/A'])[0]}) - ⭐ {restaurant.get('rating', 'N/A')} - 🚚 {restaurant.get('delivery_time', 'N/A')} min\n"
        
        return formatted
    
    def format_reservation_response(self, response):
        """Formatea respuesta del agente de reservas"""
        formatted = f"🍽️ {response.get('response', 'Sin respuesta')}\n"
        
        if response.get('reservation'):
            reservation = response['reservation']
            formatted += f"\n📋 Detalles de la reserva:\n"
            formatted += f"  • ID: {reservation.get('id', 'N/A')}\n"
            formatted += f"  • Restaurante: {reservation.get('restaurant_name', 'N/A')}\n"
            formatted += f"  • Fecha: {reservation.get('date', 'N/A')}\n"
            formatted += f"  • Hora: {reservation.get('time', 'N/A')}\n"
            formatted += f"  • Personas: {reservation.get('party_size', 'N/A')}\n"
        
        if response.get('alternatives'):
            formatted += f"\n⏰ Horarios alternativos: {', '.join(response['alternatives'])}\n"
        
        return formatted
    
    def format_design_response(self, response):
        """Formatea respuesta del agente de diseño"""
        if 'error' in response:
            return f"🏠 Error: {response['error']}"
        
        formatted = f"🏠 Diseño para {response.get('room_type', 'habitación')} creado exitosamente!\n"
        formatted += f"\n💰 Presupuesto:\n"
        formatted += f"  • Costo total: ${response.get('total_cost', 0):.0f}\n"
        formatted += f"  • Presupuesto restante: ${response.get('budget_remaining', 0):.0f}\n"
        formatted += f"  • Eficiencia del espacio: {response.get('area_efficiency', 0):.1f}%\n"
        
        shopping_list = response.get('shopping_list', [])
        if shopping_list:
            formatted += f"\n🛒 Lista de compras (top 5):\n"
            for item in shopping_list[:5]:
                formatted += f"  • {item.get('quantity', 1)}x {item.get('name', 'Item')} - ${item.get('total_price', 0):.0f}\n"
        
        recommendations = response.get('recommendations', [])
        if recommendations:
            formatted += f"\n💡 Recomendaciones:\n"
            for rec in recommendations[:3]:
                formatted += f"  • {rec}\n"
        
        return formatted
    
    def format_api_response(self, response):
        """Formatea respuesta del agente de API"""
        if 'error' in response:
            return f"⚙️ Error: {response['error']}"
        
        formatted = f"⚙️ API generada exitosamente! (ID: {response.get('generation_id', 'N/A')})\n"
        formatted += f"\n📊 Estadísticas:\n"
        formatted += f"  • Framework: {response.get('framework', 'N/A')}\n"
        formatted += f"  • Modelos: {response.get('models_count', 0)}\n"
        formatted += f"  • Endpoints: {response.get('endpoints_count', 0)}\n"
        formatted += f"  • Archivos generados: {len(response.get('generated_code', {}))}\n"
        
        generated_code = response.get('generated_code', {})
        if generated_code:
            formatted += f"\n📁 Archivos principales:\n"
            for filename in list(generated_code.keys())[:5]:
                formatted += f"  • {filename}\n"
        
        return formatted
    
    def display_result(self, result):
        """Muestra el resultado en la interfaz"""
        agent_name = result.get('agent', 'unknown')
        response_text = result.get('response', 'Sin respuesta')
        
        # Agregar emoji según el agente
        agent_emojis = {
            'delivery': '🍕',
            'reservas': '🍽️',
            'diseño': '🏠',
            'api': '⚙️',
            'general': '🤖'
        }
        
        emoji = agent_emojis.get(agent_name, '🤖')
        formatted_response = f"[{emoji} {agent_name.upper()}]\n\n{response_text}"
        
        self.add_agent_message(formatted_response)
    
    def show_system_status(self):
        """Muestra el estado del sistema"""
        try:
            overview = self.execution_monitor.get_system_overview(hours=1)
            
            status_text = f"📊 Estado del Sistema:\n\n"
            status_text += f"🔢 Ejecuciones totales: {overview.get('total_executions', 0)}\n"
            status_text += f"🤖 Agentes únicos: {overview.get('unique_agents', 0)}\n"
            status_text += f"✅ Tasa de éxito: {overview.get('overall_success_rate', 0):.1%}\n"
            status_text += f"⏱️ Tiempo promedio: {overview.get('avg_response_time', 0):.2f}s\n"
            status_text += f"🏆 Agente más activo: {overview.get('most_active_agent', 'N/A')}\n"
            
            # Obtener estadísticas de prompts
            prompt_stats = self.prompt_manager.get_usage_statistics()
            status_text += f"\n💬 Sistema de Prompts:\n"
            status_text += f"  • Templates registrados: {prompt_stats.get('templates_registered', 0)}\n"
            status_text += f"  • Prompts utilizados: {prompt_stats.get('total_prompts_used', 0)}\n"
            
            self.add_system_message(status_text)
            
        except Exception as e:
            self.add_error_message(f"Error obteniendo estado: {str(e)}")
    
    def clear_chat(self):
        """Limpia el área de chat"""
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar la conversación?"):
            self.chat_area.config(state=tk.NORMAL)
            self.chat_area.delete(1.0, tk.END)
            self.chat_area.config(state=tk.DISABLED)
            self.conversation_history = []
            self.add_agent_message("Conversación reiniciada. ¿En qué puedo ayudarte?")
    
    def export_chat(self):
        """Exporta la conversación a un archivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversacion_agentes_{timestamp}.json"
            
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'conversation_history': self.conversation_history,
                'system_info': self.execution_monitor.get_system_overview(hours=24)
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.add_system_message(f"Conversación exportada a: {filename}")
            
        except Exception as e:
            self.add_error_message(f"Error exportando: {str(e)}")


def main():
    """Función principal para ejecutar la GUI"""
    try:
        # Crear ventana principal
        root = tk.Tk()
        
        # Inicializar aplicación
        app = AgentGUI(root)
        
        # Configurar cierre de ventana
        def on_closing():
            if messagebox.askokcancel("Salir", "¿Quieres cerrar el sistema de agentes?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Ejecutar aplicación
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Error al inicializar la aplicación:\n{str(e)}")


if __name__ == "__main__":
    main()