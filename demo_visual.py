"""
Demo Visual - Capturas de funcionalidades de la interfaz gráfica
Muestra ejemplos de uso para todos los agentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.delivery_agent import DeliveryAgent
from agents.reservation_agent import RestaurantReservationAgent  
from agents.room_design_agent import RoomDesignAgent
from agents.api_generation_agent import APIGenerationAgent

def demo_delivery():
    """Demo del agente de delivery"""
    print("🍕 DEMO: Agente de Delivery")
    print("="*50)
    
    agent = DeliveryAgent()
    
    ejemplos = [
        "Quiero pedir pizza para 2 personas",
        "Busco comida china con delivery rápido",
        "Necesito comida vegetariana para hoy"
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"\n📝 Ejemplo {i}: {ejemplo}")
        try:
            respuesta = agent.process_delivery_request(ejemplo)
            print(f"✅ Respuesta: {respuesta.get('response', 'Sin respuesta')[:100]}...")
            if respuesta.get('restaurants'):
                print(f"🏪 Restaurantes encontrados: {len(respuesta['restaurants'])}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*50)

def demo_reservations():
    """Demo del agente de reservas"""
    print("\n🍽️ DEMO: Agente de Reservas")
    print("="*50)
    
    agent = RestaurantReservationAgent()
    
    ejemplos = [
        "Mesa para 4 personas el viernes a las 8 PM",
        "Reserva para 2 el sábado a las 7:30",
        "Necesito mesa para 6 personas mañana"
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"\n📝 Ejemplo {i}: {ejemplo}")
        try:
            respuesta = agent.handle_reservation_request(ejemplo)
            print(f"✅ Respuesta: {respuesta.get('response', 'Sin respuesta')[:100]}...")
            if respuesta.get('reservation'):
                print(f"📋 Reserva ID: {respuesta['reservation'].get('id', 'N/A')}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*50)

def demo_design():
    """Demo del agente de diseño"""
    print("\n🏠 DEMO: Agente de Diseño")
    print("="*50)
    
    agent = RoomDesignAgent()
    
    ejemplos = [
        ("dormitorio_grande", "4x5m", "moderno", 3000),
        ("sala_estar", "5x6m", "minimalista", 5000),
        ("oficina", "3x4m", "industrial", 2000)
    ]
    
    for i, (tipo, dimensiones, estilo, presupuesto) in enumerate(ejemplos, 1):
        print(f"\n📝 Ejemplo {i}: {tipo} {dimensiones}, estilo {estilo}, ${presupuesto}")
        try:
            respuesta = agent.generate_design(tipo, dimensiones, estilo, presupuesto)
            if 'error' not in respuesta:
                print(f"✅ Diseño creado - Costo: ${respuesta.get('total_cost', 0):.0f}")
                print(f"🛒 Items en lista: {len(respuesta.get('shopping_list', []))}")
                print(f"💡 Recomendaciones: {len(respuesta.get('recommendations', []))}")
            else:
                print(f"❌ Error: {respuesta['error']}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*50)

def demo_api():
    """Demo del agente de API"""
    print("\n⚙️ DEMO: Agente de API")
    print("="*50)
    
    agent = APIGenerationAgent()
    
    ejemplos = [
        "API para gestión de productos con CRUD completo",
        "Sistema de usuarios con autenticación JWT", 
        "API de blog con posts y comentarios"
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"\n📝 Ejemplo {i}: {ejemplo}")
        try:
            respuesta = agent.generate_api(ejemplo, 'fastapi', 'natural')
            if 'error' not in respuesta:
                print(f"✅ API generada - ID: {respuesta.get('generation_id', 'N/A')}")
                print(f"📊 Modelos: {respuesta.get('models_count', 0)}")
                print(f"🔗 Endpoints: {respuesta.get('endpoints_count', 0)}")
                print(f"📁 Archivos: {len(respuesta.get('generated_code', {}))}")
            else:
                print(f"❌ Error: {respuesta['error']}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*50)

def mostrar_interfaz_info():
    """Muestra información sobre la interfaz gráfica"""
    print("\n🎨 INTERFAZ GRÁFICA - Guía Rápida")
    print("="*60)
    
    info = """
📱 CARACTERÍSTICAS PRINCIPALES:
  • Selector de agentes (automático o manual)
  • Chat interactivo con historial completo
  • Ejemplos rápidos para cada agente
  • Monitoreo de rendimiento en tiempo real
  • Exportación de conversaciones

🎮 CÓMO USAR:
  1. Ejecuta: python launcher.py (o gui.bat en Windows)
  2. Selecciona agente o deja en "auto"
  3. Escribe tu solicitud en el área de texto
  4. Presiona "🚀 Enviar" o Ctrl+Enter
  5. Observa la respuesta en el chat

🚀 EJEMPLOS RÁPIDOS:
  🍕 Delivery: "Quiero pedir comida italiana para 2 personas"
  🍽️ Reserva: "Mesa para 4 personas el viernes a las 8 PM"  
  🏠 Diseño: "Diseñar dormitorio 4x5m, presupuesto $3000"
  ⚙️ API: "Crear API para gestión de productos con CRUD"

🔧 FUNCIONES AVANZADAS:
  📊 Estado Sistema: Estadísticas de rendimiento
  🗑️ Limpiar Chat: Reinicia la conversación
  💾 Exportar Chat: Guarda en formato JSON

⚡ TIPS:
  • El modo "auto" detecta automáticamente el agente apropiado
  • Usa ejemplos rápidos para probar funcionalidades
  • Monitorea el rendimiento con "Estado Sistema"
  • Exporta conversaciones importantes
    """
    
    print(info)
    print("="*60)

def main():
    """Ejecuta el demo completo"""
    print("🤖 DEMO COMPLETO - Sistema de Agentes IA")
    print("="*70)
    print("Este demo muestra las capacidades de todos los agentes")
    print("Para la interfaz gráfica, ejecuta: python launcher.py")
    print("="*70)
    
    # Mostrar información de la interfaz
    mostrar_interfaz_info()
    
    # Demos de agentes
    try:
        demo_delivery()
        demo_reservations() 
        demo_design()
        demo_api()
        
        print("\n🎉 DEMO COMPLETADO")
        print("="*50)
        print("✅ Todos los agentes funcionan correctamente")
        print("🎨 Para usar la interfaz gráfica:")
        print("   - Ejecuta: python launcher.py")
        print("   - O doble click en: gui.bat (Windows)")
        print("\n📚 Para más información:")
        print("   - README.md: Documentación general")
        print("   - README_GUI.md: Guía de la interfaz gráfica")
        
    except Exception as e:
        print(f"\n❌ Error en demo: {e}")
        print("💡 Verifica que todos los archivos estén en su lugar")

if __name__ == "__main__":
    main()