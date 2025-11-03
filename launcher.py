"""
Script de lanzamiento mejorado para el sistema de agentes de IA
Incluye validaciones robustas, configuración avanzada y mejor manejo de errores
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import logging
from datetime import datetime
from typing import Optional


def setup_environment():
    """Configura el entorno de ejecución"""
    # Agregar directorios al path
    script_dir = Path(__file__).parent.absolute()
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Cambiar al directorio del script
    os.chdir(script_dir)
    
    return script_dir


def check_python_version() -> bool:
    """Verifica que la versión de Python sea compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Se requiere Python 3.7 o superior")
        print(f"💡 Versión actual: {sys.version}")
        return False
    return True


def check_dependencies() -> tuple[bool, list]:
    """Verifica que todas las dependencias estén disponibles"""
    required_modules = {
        'tkinter': 'Interfaz gráfica',
        'threading': 'Manejo de hilos',
        'json': 'Procesamiento JSON',
        'datetime': 'Manejo de fechas',
        'pathlib': 'Manejo de rutas',
        'dataclasses': 'Clases de datos'
    }
    
    missing_modules = []
    
    for module, description in required_modules.items():
        try:
            __import__(module)
        except ImportError:
            missing_modules.append((module, description))
    
    return len(missing_modules) == 0, missing_modules


def validate_project_structure(base_dir: Path) -> tuple[bool, list]:
    """Valida la estructura del proyecto"""
    required_structure = {
        'agents': 'Directorio de agentes',
        'core': 'Directorio de sistemas core',
        'agents/delivery_agent.py': 'Agente de delivery (PideBot)',
        'core/__init__.py': 'Módulo core',
        'gui.py': 'Interfaz gráfica principal'
    }
    
    missing_items = []
    
    for item, description in required_structure.items():
        item_path = base_dir / item
        if not item_path.exists():
            missing_items.append((item, description))
    
    return len(missing_items) == 0, missing_items


def initialize_logging(base_dir: Path) -> Optional[logging.Logger]:
    """Inicializa el sistema de logging"""
    try:
        from core.logger import get_logger
        logger = get_logger("Launcher")
        logger.info("Sistema de logging inicializado correctamente")
        return logger
    except ImportError as e:
        print(f"⚠️ No se pudo inicializar logging avanzado: {e}")
        print("📝 Usando logging básico")
        
        # Configurar logging básico
        log_dir = base_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"launcher_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger("Launcher")


def initialize_config(base_dir: Path) -> Optional[object]:
    """Inicializa el sistema de configuración"""
    try:
        from core.config import init_config
        config = init_config()
        print("⚙️ Sistema de configuración inicializado")
        return config
    except ImportError as e:
        print(f"⚠️ No se pudo inicializar configuración: {e}")
        print("📝 Usando configuración por defecto")
        return None


def create_gui_window(config: Optional[object] = None) -> tk.Tk:
    """Crea y configura la ventana principal"""
    root = tk.Tk()
    
    # Configurar propiedades básicas
    if config and hasattr(config, 'gui'):
        root.geometry(f"{config.gui.window_width}x{config.gui.window_height}")
        if config.gui.center_window:
            root.eval('tk::PlaceWindow . center')
    else:
        root.geometry("1200x800")
        root.eval('tk::PlaceWindow . center')
    
    # Configurar título y icono
    root.title("🤖 Sistema de Agentes de IA - PideBot v2.0")
    root.configure(bg='#f0f0f0')
    
    # Configurar comportamiento de cierre
    def on_closing():
        if messagebox.askokcancel("Salir", "¿Deseas cerrar el sistema de agentes?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    return root


def display_startup_info():
    """Muestra información de inicio del sistema"""
    print("=" * 60)
    print("🤖 SISTEMA DE AGENTES DE IA - MEJORADO")
    print("=" * 60)
    print("🚀 Características principales:")
    print("   • PideBot - Agente de delivery proactivo")
    print("   • Sistema de logging avanzado")
    print("   • Configuración centralizada")
    print("   • Monitoreo en tiempo real")
    print("   • Interfaz gráfica mejorada")
    print("-" * 60)


def main():
    """Función principal de lanzamiento"""
    display_startup_info()
    
    print("� Verificando sistema...")
    
    # 1. Verificar versión de Python
    if not check_python_version():
        input("Presiona Enter para salir...")
        return 1
    
    # 2. Configurar entorno
    try:
        base_dir = setup_environment()
        print(f"📁 Directorio base: {base_dir}")
    except Exception as e:
        print(f"❌ Error configurando entorno: {e}")
        input("Presiona Enter para salir...")
        return 1
    
    # 3. Verificar dependencias
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        print("❌ Dependencias faltantes:")
        for module, desc in missing_deps:
            print(f"   • {module}: {desc}")
        print("💡 Instala las dependencias y vuelve a intentar")
        input("Presiona Enter para salir...")
        return 1
    
    # 4. Validar estructura del proyecto
    structure_ok, missing_items = validate_project_structure(base_dir)
    if not structure_ok:
        print("❌ Estructura del proyecto incompleta:")
        for item, desc in missing_items:
            print(f"   • {item}: {desc}")
        print("💡 Asegúrate de tener todos los archivos necesarios")
        input("Presiona Enter para salir...")
        return 1
    
    # 5. Inicializar sistemas
    logger = initialize_logging(base_dir)
    config = initialize_config(base_dir)
    
    if logger:
        logger.info("Iniciando sistema de agentes de IA")
    
    # 6. Cargar e inicializar GUI
    try:
        print("🎨 Cargando interfaz gráfica...")
        
        from gui import AgentGUI
        
        # Crear ventana principal
        root = create_gui_window(config)
        
        # Inicializar aplicación
        app = AgentGUI(root)
        
        print("✅ Sistema inicializado correctamente")
        print("🎯 Interfaz gráfica lista")
        print("📱 PideBot activo y listo para pedidos")
        print("❌ Cierra esta ventana para terminar la aplicación")
        print("=" * 60)
        
        if logger:
            logger.info("GUI inicializada exitosamente")
        
        # Ejecutar aplicación
        root.mainloop()
        
        print("👋 Sistema cerrado correctamente. ¡Hasta luego!")
        if logger:
            logger.info("Sistema cerrado por el usuario")
        
        return 0
        
    except ImportError as e:
        error_msg = f"Error de importación: {e}"
        print(f"❌ {error_msg}")
        print("💡 Verifica que todos los archivos estén en su lugar")
        
        if logger:
            logger.error(error_msg)
        
        messagebox.showerror("Error de Importación", 
                           f"{error_msg}\n\nVerifica que todos los archivos estén presentes.")
        return 1
        
    except Exception as e:
        error_msg = f"Error inesperado: {e}"
        print(f"❌ {error_msg}")
        print("💡 Revisa los logs para más detalles")
        
        if logger:
            logger.error(error_msg, exc_info=True)
        
        messagebox.showerror("Error", 
                           f"{error_msg}\n\nRevisa la consola para más información.")
        return 1


def demo_pidebot():
    """Ejecuta una demostración de PideBot desde terminal"""
    print("=== DEMO TERMINAL DE PIDEBOT ===\n")
    
    try:
        base_dir = setup_environment()
        from agents.delivery_agent import demo_delivery_agent
        
        print("Ejecutando demostración de PideBot...")
        demo_delivery_agent()
        
    except Exception as e:
        print(f"Error en demo: {e}")


if __name__ == "__main__":
    # Verificar si se quiere ejecutar la demo
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_pidebot()
    else:
        exit_code = main()
        sys.exit(exit_code)