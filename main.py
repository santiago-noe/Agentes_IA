"""
Script principal - PideBot Delivery Agent
Demostración del agente de delivery inteligente y proactivo
"""

import sys
import os
import time
from datetime import datetime
from typing import Dict, Any

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports del agente de delivery
from agents.delivery_agent import PideBot, demo_delivery_agent, demo_apis

# Imports de sistemas core
try:
    from core.logger import get_logger
    from core.config import get_config
except ImportError:
    print("⚠️ Sistemas core no disponibles, usando funcionalidad básica")
    get_logger = None
    get_config = None


class PideBotSystem:
    """Sistema principal que maneja únicamente PideBot"""
    
    def __init__(self):
        # Inicializar logger si está disponible
        self.logger = get_logger("PideBotSystem") if get_logger else None
        
        # Inicializar configuración si está disponible
        self.config = get_config() if get_config else None
        
        # Inicializar PideBot
        self.pidebot = PideBot(
            notificar_usuario_callback=self._notificar_usuario,
            preguntar_usuario_callback=self._preguntar_usuario
        )
        
        if self.logger:
            self.logger.info("PideBotSystem inicializado correctamente")
        else:
            print("🤖 PideBotSystem inicializado correctamente")
    
    def _notificar_usuario(self, mensaje: str):
        """Callback para notificaciones del usuario"""
        print(f"\n🔔 [NOTIFICACIÓN] {mensaje}\n")
        if self.logger:
            self.logger.info(f"Notificación enviada: {mensaje}")
    
    def _preguntar_usuario(self, pregunta: str) -> str:
        """Callback para preguntas al usuario"""
        respuesta = input(f"❓ {pregunta}: ")
        if self.logger:
            self.logger.info(f"Pregunta: {pregunta} | Respuesta: {respuesta}")
        return respuesta
    
    def ejecutar_conversacion_interactiva(self):
        """Ejecuta una conversación interactiva con PideBot"""
        print("=" * 60)
        print("🤖 PIDEBOT - AGENTE DE DELIVERY INTERACTIVO")
        print("=" * 60)
        print("💡 Ejemplos de comandos:")
        print("   • 'Quiero una hamburguesa doble de Bembos'")
        print("   • 'Pídeme un cuarto de pollo de Norky's'")
        print("   • '¿Dónde está mi pedido?'")
        print("   • 'salir' para terminar")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n👤 Tú: ").strip()
                
                if user_input.lower() in ['salir', 'exit', 'quit']:
                    print("👋 ¡Hasta luego! Gracias por usar PideBot.")
                    break
                
                if not user_input:
                    continue
                
                respuesta = self.pidebot.procesar_solicitud(user_input)
                print(f"🤖 PideBot: {respuesta}")
                
            except KeyboardInterrupt:
                print("\n👋 Sesión interrumpida. ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                if self.logger:
                    self.logger.error(f"Error en conversación: {e}", exc_info=True)
    
    def ejecutar_demo_completa(self):
        """Ejecuta una demostración completa del sistema"""
        print("🚀 Ejecutando demostración completa de PideBot...")
        
        # Demo de APIs
        demo_apis()
        
        print("\n" + "="*60 + "\n")
        
        # Demo de agente
        demo_delivery_agent()
        
        print("\n" + "="*60 + "\n")
        
        # Mostrar estado del sistema
        estado = self.pidebot.obtener_estado_sistema()
        print("📊 Estado actual del sistema:")
        for key, value in estado.items():
            print(f"   • {key}: {value}")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        estado_pidebot = self.pidebot.obtener_estado_sistema()
        
        return {
            "sistema": "PideBot Delivery Agent",
            "version": "2.0",
            "estado_agente": estado_pidebot,
            "logger_activo": self.logger is not None,
            "config_activa": self.config is not None,
            "timestamp": datetime.now().isoformat()
        }


def main_interactivo():
    """Función principal para modo interactivo"""
    print("🚀 Iniciando PideBot System...")
    
    try:
        sistema = PideBotSystem()
        sistema.ejecutar_conversacion_interactiva()
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return 1
    
    return 0


def main_demo():
    """Función principal para demostración"""
    print("🚀 Iniciando demostración de PideBot...")
    
    try:
        sistema = PideBotSystem()
        sistema.ejecutar_demo_completa()
        
        # Mostrar estadísticas finales
        stats = sistema.obtener_estadisticas()
        print("\n📈 Estadísticas del sistema:")
        for key, value in stats.items():
            print(f"   • {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        return 1
    
    return 0


def main_simple():
    """Función principal simple - solo demo de agente"""
    try:
        demo_delivery_agent()
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    # Determinar modo de ejecución
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
        
        if modo == "--interactivo" or modo == "-i":
            exit_code = main_interactivo()
        elif modo == "--demo" or modo == "-d":
            exit_code = main_demo()
        elif modo == "--simple" or modo == "-s":
            exit_code = main_simple()
        else:
            print("Modos disponibles:")
            print("  --interactivo (-i): Conversación interactiva con PideBot")
            print("  --demo (-d): Demostración completa del sistema")
            print("  --simple (-s): Demo simple del agente")
            exit_code = 0
    else:
        # Por defecto: demo simple
        exit_code = main_simple()
    
    sys.exit(exit_code)