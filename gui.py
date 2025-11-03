"""
Interfaz gráfica para PideBot - Agente de Delivery
Proporciona una GUI intuitiva para interactuar con el agente de delivery
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

# Imports del agente de delivery
from agents.delivery_agent import PideBot

# Imports de sistemas core (opcionales)
try:
    from core.logger import get_logger
    from core.config import get_config
except ImportError:
    get_logger = None
    get_config = None


class PideBotGUI:
    """Interfaz gráfica principal para PideBot"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 PideBot - Agente de Delivery Inteligente")
        
        # Inicializar sistemas primero
        self.logger = get_logger("PideBotGUI") if get_logger else None
        self.config = get_config() if get_config else None
        
        # Configurar ventana (ahora que config está disponible)
        self._configurar_ventana()
        
        # Inicializar PideBot con callbacks GUI
        self.pidebot = PideBot(
            notificar_usuario_callback=self._mostrar_notificacion,
            preguntar_usuario_callback=self._preguntar_usuario_gui
        )
        
        # Variables de estado
        self.conversation_history = []
        self.waiting_for_response = False
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Mostrar mensaje de bienvenida
        self._agregar_mensaje("🤖 PideBot", self.pidebot._respuesta_bienvenida(), "bot")
        
        if self.logger:
            self.logger.info("PideBotGUI inicializada correctamente")
    
    def _configurar_ventana(self):
        """Configura las propiedades básicas de la ventana"""
        # Configurar tamaño y posición por defecto
        ancho, alto = 1200, 800
        
        # Intentar obtener configuración personalizada
        try:
            if self.config and hasattr(self.config, 'gui'):
                ancho = getattr(self.config.gui, 'window_width', 1200)
                alto = getattr(self.config.gui, 'window_height', 800)
        except (AttributeError, TypeError):
            # Usar valores por defecto si hay problemas con la configuración
            pass
        
        self.root.geometry(f"{ancho}x{alto}")
        self.root.configure(bg='#f0f8ff')
        
        # Centrar ventana
        try:
            self.root.eval('tk::PlaceWindow . center')
        except tk.TclError:
            # Si no se puede centrar, usar posicionamiento manual
            x = (self.root.winfo_screenwidth() // 2) - (ancho // 2)
            y = (self.root.winfo_screenheight() // 2) - (alto // 2)
            self.root.geometry(f"{ancho}x{alto}+{x}+{y}")
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)
        
        # Configurar ícono (si está disponible)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass  # No hay problema si no existe el ícono
    
    def _crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar redimensionamiento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="🤖 PideBot - Tu Asistente de Delivery",
            font=('Segoe UI', 16, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Panel de conversación
        self._crear_panel_conversacion(main_frame)
        
        # Panel de entrada
        self._crear_panel_entrada(main_frame)
        
        # Panel de estado
        self._crear_panel_estado(main_frame)
        
        # Panel de acciones rápidas
        self._crear_panel_acciones(main_frame)
    
    def _crear_panel_conversacion(self, parent):
        """Crea el panel de conversación"""
        conv_frame = ttk.LabelFrame(parent, text="💬 Conversación", padding="5")
        conv_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        conv_frame.columnconfigure(0, weight=1)
        conv_frame.rowconfigure(0, weight=1)
        
        # Área de texto para conversación
        self.conversation_text = scrolledtext.ScrolledText(
            conv_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 10),
            state=tk.DISABLED,
            bg='#ffffff',
            fg='#333333'
        )
        self.conversation_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para colores
        self.conversation_text.tag_configure("user", foreground="#0066cc", font=('Consolas', 10, 'bold'))
        self.conversation_text.tag_configure("bot", foreground="#cc6600", font=('Consolas', 10))
        self.conversation_text.tag_configure("notification", foreground="#009900", font=('Consolas', 10, 'italic'))
        self.conversation_text.tag_configure("error", foreground="#cc0000", font=('Consolas', 10, 'bold'))
    
    def _crear_panel_entrada(self, parent):
        """Crea el panel de entrada de texto"""
        entrada_frame = ttk.LabelFrame(parent, text="✏️ Tu Mensaje", padding="5")
        entrada_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        entrada_frame.columnconfigure(0, weight=1)
        
        # Campo de entrada
        self.entrada_text = tk.Text(
            entrada_frame,
            height=3,
            wrap=tk.WORD,
            font=('Segoe UI', 11)
        )
        self.entrada_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Botón enviar
        self.enviar_btn = ttk.Button(
            entrada_frame,
            text="Enviar",
            command=self._enviar_mensaje,
            width=12
        )
        self.enviar_btn.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind Enter para enviar
        self.entrada_text.bind('<Control-Return>', lambda e: self._enviar_mensaje())
        self.entrada_text.bind('<Return>', self._on_enter_key)
        
        # Focus inicial
        self.entrada_text.focus()
    
    def _crear_panel_estado(self, parent):
        """Crea el panel de estado del sistema"""
        estado_frame = ttk.LabelFrame(parent, text="📊 Estado del Sistema", padding="5")
        estado_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Variables de estado
        self.estado_vars = {
            "pedidos_activos": tk.StringVar(value="0"),
            "monitoreo_activo": tk.StringVar(value="No"),
            "esperando_confirmacion": tk.StringVar(value="No")
        }
        
        # Labels de estado
        row = 0
        for key, var in self.estado_vars.items():
            label_name = key.replace('_', ' ').title()
            ttk.Label(estado_frame, text=f"{label_name}:").grid(row=row, column=0, sticky=tk.W, pady=2)
            ttk.Label(estado_frame, textvariable=var, font=('Consolas', 9, 'bold')).grid(row=row, column=1, sticky=tk.W, padx=(5, 0), pady=2)
            row += 1
        
        # Botón actualizar estado
        ttk.Button(
            estado_frame,
            text="🔄 Actualizar",
            command=self._actualizar_estado,
            width=15
        ).grid(row=row, column=0, columnspan=2, pady=(10, 0))
    
    def _crear_panel_acciones(self, parent):
        """Crea el panel de acciones rápidas"""
        acciones_frame = ttk.LabelFrame(parent, text="⚡ Acciones Rápidas", padding="5")
        acciones_frame.grid(row=2, column=2, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # Botones de acciones rápidas
        acciones = [
            ("🍔 Hamburguesa Bembos", "Quiero una hamburguesa doble con queso de Bembos"),
            ("🍗 Pollo Norky's", "Quiero un cuarto de pollo a la brasa de Norky's"),
            ("📍 Estado Pedido", "¿Dónde está mi pedido?"),
            ("🧹 Limpiar Chat", self._limpiar_conversacion),
        ]
        
        for i, (texto, accion) in enumerate(acciones):
            if callable(accion):
                comando = accion
            else:
                comando = lambda msg=accion: self._enviar_mensaje_rapido(msg)
            
            ttk.Button(
                acciones_frame,
                text=texto,
                command=comando,
                width=20
            ).grid(row=i, column=0, pady=2, sticky=tk.W)
    
    def _on_enter_key(self, event):
        """Maneja la tecla Enter"""
        if event.state & 0x4:  # Ctrl+Enter
            return
        else:  # Enter solo
            self._enviar_mensaje()
            return 'break'  # Prevenir salto de línea
    
    def _enviar_mensaje(self):
        """Envía un mensaje a PideBot"""
        if self.waiting_for_response:
            messagebox.showwarning("Esperando", "Por favor espera la respuesta anterior")
            return
        
        mensaje = self.entrada_text.get("1.0", tk.END).strip()
        
        if not mensaje:
            return
        
        # Limpiar entrada
        self.entrada_text.delete("1.0", tk.END)
        
        # Mostrar mensaje del usuario
        self._agregar_mensaje("👤 Tú", mensaje, "user")
        
        # Procesar en hilo separado
        self.waiting_for_response = True
        self.enviar_btn.configure(state='disabled', text="Procesando...")
        
        threading.Thread(
            target=self._procesar_mensaje,
            args=(mensaje,),
            daemon=True
        ).start()
    
    def _enviar_mensaje_rapido(self, mensaje):
        """Envía un mensaje predefinido"""
        self.entrada_text.delete("1.0", tk.END)
        self.entrada_text.insert("1.0", mensaje)
        self._enviar_mensaje()
    
    def _procesar_mensaje(self, mensaje):
        """Procesa el mensaje en hilo separado"""
        try:
            respuesta = self.pidebot.procesar_solicitud(mensaje)
            
            # Mostrar respuesta en UI thread
            self.root.after(0, self._mostrar_respuesta, respuesta)
            
        except Exception as e:
            error_msg = f"Error procesando mensaje: {e}"
            if self.logger:
                self.logger.error(error_msg, exc_info=True)
            self.root.after(0, self._mostrar_error, error_msg)
        
        finally:
            self.root.after(0, self._habilitar_entrada)
    
    def _mostrar_respuesta(self, respuesta):
        """Muestra la respuesta de PideBot"""
        self._agregar_mensaje("🤖 PideBot", respuesta, "bot")
        self._actualizar_estado()
    
    def _mostrar_error(self, error):
        """Muestra un error"""
        self._agregar_mensaje("❌ Error", error, "error")
    
    def _habilitar_entrada(self):
        """Habilita la entrada de nuevo"""
        self.waiting_for_response = False
        self.enviar_btn.configure(state='normal', text="Enviar")
        self.entrada_text.focus()
    
    def _agregar_mensaje(self, remitente, mensaje, tipo):
        """Agrega un mensaje al área de conversación"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.conversation_text.configure(state=tk.NORMAL)
        
        # Agregar timestamp y remitente
        self.conversation_text.insert(tk.END, f"[{timestamp}] {remitente}:\n", tipo)
        
        # Agregar mensaje
        self.conversation_text.insert(tk.END, f"{mensaje}\n\n")
        
        self.conversation_text.configure(state=tk.DISABLED)
        self.conversation_text.see(tk.END)
        
        # Guardar en historial
        self.conversation_history.append({
            "timestamp": timestamp,
            "remitente": remitente,
            "mensaje": mensaje,
            "tipo": tipo
        })
    
    def _mostrar_notificacion(self, mensaje):
        """Callback para notificaciones de PideBot"""
        self.root.after(0, self._agregar_mensaje, "🔔 Notificación", mensaje, "notification")
    
    def _preguntar_usuario_gui(self, pregunta):
        """Callback para preguntas de PideBot (modo GUI)"""
        # En modo GUI, simplemente mostramos la pregunta y esperamos respuesta normal
        self.root.after(0, self._agregar_mensaje, "❓ PideBot", pregunta, "bot")
        return ""  # Retornamos vacío, la respuesta vendrá por el chat normal
    
    def _actualizar_estado(self):
        """Actualiza el estado del sistema"""
        try:
            estado = self.pidebot.obtener_estado_sistema()
            
            self.estado_vars["pedidos_activos"].set(str(estado.get("pedidos_activos", 0)))
            self.estado_vars["monitoreo_activo"].set("Sí" if estado.get("monitoreo_activo", False) else "No")
            self.estado_vars["esperando_confirmacion"].set("Sí" if estado.get("esperando_confirmacion", False) else "No")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error actualizando estado: {e}")
    
    def _limpiar_conversacion(self):
        """Limpia el área de conversación"""
        respuesta = messagebox.askyesno("Confirmar", "¿Limpiar toda la conversación?")
        if respuesta:
            self.conversation_text.configure(state=tk.NORMAL)
            self.conversation_text.delete("1.0", tk.END)
            self.conversation_text.configure(state=tk.DISABLED)
            self.conversation_history.clear()
            
            # Mostrar mensaje de bienvenida nuevamente
            self._agregar_mensaje("🤖 PideBot", self.pidebot._respuesta_bienvenida(), "bot")
    
    def _cerrar_aplicacion(self):
        """Maneja el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Deseas cerrar PideBot?"):
            if self.logger:
                self.logger.info("Aplicación cerrada por el usuario")
            self.root.destroy()


# Alias para compatibilidad hacia atrás
AgentGUI = PideBotGUI


def main():
    """Función principal para ejecutar la GUI"""
    root = tk.Tk()
    app = PideBotGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Aplicación interrumpida")
    except Exception as e:
        print(f"Error en la aplicación: {e}")
        messagebox.showerror("Error crítico", f"Error inesperado: {e}")


if __name__ == "__main__":
    main()