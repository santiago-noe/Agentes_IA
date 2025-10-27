"""
Script de lanzamiento rápido para la interfaz gráfica
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Verifica que todas las dependencias estén disponibles"""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def main():
    """Lanza la interfaz gráfica con verificaciones previas"""
    print("🚀 Iniciando Sistema de Agentes de IA...")
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ Error: tkinter no está disponible")
        print("💡 Instala tkinter ejecutando: pip install tk")
        return
    
    # Cambiar al directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Verificar estructura de archivos
    required_dirs = ['agents', 'core']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ Error: Directorio '{dir_name}' no encontrado")
            print("💡 Asegúrate de ejecutar desde el directorio del proyecto")
            return
    
    try:
        # Importar y ejecutar GUI
        from gui import AgentGUI
        
        print("✅ Dependencias verificadas")
        print("🎨 Lanzando interfaz gráfica...")
        
        # Crear ventana principal
        root = tk.Tk()
        
        # Configurar icono y propiedades
        root.iconify()  # Minimizar temporalmente
        root.deiconify()  # Mostrar
        
        # Centrar ventana
        root.eval('tk::PlaceWindow . center')
        
        # Inicializar aplicación
        app = AgentGUI(root)
        
        # Mensaje de bienvenida en consola
        print("🎯 Interfaz gráfica iniciada correctamente")
        print("📱 Usa la ventana de la aplicación para interactuar con los agentes")
        print("❌ Cierra esta consola para terminar la aplicación")
        
        # Ejecutar aplicación
        root.mainloop()
        
        print("👋 Sistema cerrado. ¡Hasta luego!")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Verifica que todos los archivos estén en su lugar")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print("💡 Revisa la consola para más detalles")

if __name__ == "__main__":
    main()