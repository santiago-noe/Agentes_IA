# 🎨 Interfaz Gráfica - Sistema de Agentes IA

## 📖 Descripción

Interfaz gráfica intuitiva desarrollada con tkinter para interactuar con el sistema de agentes de IA. Proporciona una experiencia visual y fácil de usar para probar todos los agentes disponibles.

## ✨ Características

### 🖥️ Interfaz Principal
- **Panel de Control**: Selector de agentes, área de entrada de texto y botones de acción
- **Chat Interactivo**: Conversación en tiempo real con historial completo
- **Ejemplos Rápidos**: Botones con solicitudes predefinidas para cada agente
- **Monitoreo Visual**: Estado del sistema y alertas en tiempo real

### 🤖 Agentes Disponibles
1. **🍕 Delivery**: Búsqueda de restaurantes y gestión de pedidos
2. **🍽️ Reservas**: Reservas en restaurantes con verificación de disponibilidad
3. **🏠 Diseño**: Diseño de habitaciones con optimización de presupuesto
4. **⚙️ API**: Generación automática de código de APIs

### 🔧 Funcionalidades Avanzadas
- **Detección Automática**: El sistema detecta automáticamente qué agente usar
- **Procesamiento Asíncrono**: Respuestas sin bloquear la interfaz
- **Exportación**: Guarda conversaciones en formato JSON
- **Monitoreo**: Estadísticas de rendimiento en tiempo real

## 🚀 Instalación y Uso

### Prerrequisitos
```bash
# Python 3.8+
# tkinter (incluido en Python estándar)
```

### Ejecución Rápida
```bash
# Opción 1: Usando el launcher
python launcher.py

# Opción 2: Directa
python gui.py
```

### Estructura de Archivos
```
agentes_ia/
├── gui.py          # Interfaz gráfica principal
├── launcher.py     # Script de lanzamiento
├── agents/         # Módulos de agentes
├── core/          # Sistemas principales
└── README_GUI.md  # Esta documentación
```

## 🎮 Guía de Uso

### 1. Inicio
- Ejecuta `python launcher.py`
- La interfaz se abrirá automáticamente
- Mensaje de bienvenida aparecerá en el chat

### 2. Selección de Agente
**Modo Automático (recomendado)**:
- Deja "auto" seleccionado
- El sistema detectará automáticamente el agente apropiado

**Modo Manual**:
- Selecciona un agente específico del menú desplegable
- Útil para forzar un tipo de respuesta

### 3. Envío de Solicitudes
- Escribe tu solicitud en el área de texto
- Presiona "🚀 Enviar" o Ctrl+Enter
- Observa la respuesta en el chat

### 4. Ejemplos Rápidos
Usa los botones de ejemplo para probar funcionalidades:

**🍕 Delivery**: 
```
"Quiero pedir comida italiana para 2 personas"
```

**🍽️ Reserva**: 
```
"Mesa para 4 personas el viernes a las 8 PM"
```

**🏠 Diseño**: 
```
"Diseñar dormitorio 4x5m, presupuesto $3000"
```

**⚙️ API**: 
```
"Crear API para gestión de productos con CRUD"
```

## 📊 Panel de Control

### Botones de Acción
- **📊 Estado Sistema**: Muestra estadísticas de rendimiento
- **🗑️ Limpiar Chat**: Limpia la conversación actual
- **💾 Exportar Chat**: Guarda la conversación en JSON

### Indicadores Visuales
- **🔄 Procesando**: Mientras el agente trabaja
- **⚠️ Alertas**: Respuestas lentas o errores
- **✅ Éxito**: Confirmación de operaciones

## 🎨 Personalización de la Interfaz

### Colores del Chat
- **Azul**: Mensajes del usuario
- **Verde**: Respuestas de agentes
- **Naranja**: Mensajes del sistema
- **Rojo**: Errores y alertas

### Configuración de Ventana
```python
# En gui.py, línea ~26
self.root.geometry("1000x700")  # Cambiar dimensiones
self.root.configure(bg='#f0f0f0')  # Cambiar color de fondo
```

## 🔧 Funciones Técnicas

### Monitoreo de Rendimiento
```python
# Tiempo de respuesta
execution_time = monitor.get_execution_time(execution_id)

# Estadísticas del sistema
overview = monitor.get_system_overview(hours=1)
```

### Manejo de Errores
- **Errores de Agente**: Se muestran en rojo en el chat
- **Errores de Sistema**: Alertas automáticas
- **Recuperación**: Reinicio automático de componentes

### Exportación de Datos
```json
{
  "timestamp": "2025-10-27T15:30:00",
  "conversation_history": [...],
  "system_info": {...}
}
```

## 🐛 Solución de Problemas

### Error: "tkinter no encontrado"
```bash
# Windows
pip install tk

# Linux/Ubuntu
sudo apt-get install python3-tk

# macOS
# tkinter incluido en Python estándar
```

### Error: "Módulos no encontrados"
```bash
# Verificar estructura de directorios
ls -la agents/ core/

# Ejecutar desde directorio correcto
cd agentes_ia/
python launcher.py
```

### Ventana no aparece
```python
# Verificar resolución de pantalla
# Reducir tamaño de ventana en gui.py línea 26
self.root.geometry("800x600")
```

### Respuestas lentas
- **Causa**: Procesamiento complejo de agentes
- **Solución**: Observar indicador "🔄 Procesando"
- **Optimización**: Ver estadísticas del sistema

## 📈 Métricas y Estadísticas

### Dashboard del Sistema
Presiona "📊 Estado Sistema" para ver:
- Ejecuciones totales en la última hora
- Agentes únicos utilizados
- Tasa de éxito global
- Tiempo promedio de respuesta
- Agente más activo

### Datos de Prompts
- Templates registrados
- Prompts utilizados total
- Patrones de uso por categoría

## 🔄 Actualizaciones y Mantenimiento

### Logs del Sistema
```python
# Ver logs en tiempo real
tail -f logs/system.log  # Linux/macOS
Get-Content logs\system.log -Wait  # Windows PowerShell
```

### Limpieza de Datos
```python
# Limpiar historial de ejecuciones
monitor.clear_old_records(days=7)

# Reset estadísticas de prompts
prompt_manager.reset_statistics()
```

## 🎯 Próximas Características

### Planificadas
- [ ] **Temas Visuales**: Modo oscuro/claro
- [ ] **Configuración Avanzada**: Panel de settings
- [ ] **Plugins**: Sistema de extensiones
- [ ] **Notificaciones**: Alertas de escritorio
- [ ] **Historial Persistente**: Base de datos local

### En Desarrollo
- [ ] **Modo Voz**: Entrada y salida por voz
- [ ] **Gráficos**: Visualización de datos de agentes
- [ ] **Colaboración**: Múltiples usuarios
- [ ] **APIs Web**: Acceso remoto

## 🤝 Contribución

### Estructura del Código
```python
class AgentGUI:
    def __init__(self, root):          # Inicialización
    def create_widgets(self):          # Creación de UI
    def send_request(self):            # Manejo de solicitudes
    def process_*_request(self):       # Procesadores específicos
    def format_*_response(self):       # Formateadores de respuesta
```

### Agregar Nuevo Agente
1. Crear procesador en `process_*_request()`
2. Agregar formateador en `format_*_response()`
3. Actualizar selector de agentes
4. Agregar ejemplo rápido

## 📞 Soporte

Para problemas o sugerencias:
1. Verificar logs del sistema
2. Revisar estado de componentes
3. Exportar conversación para debugging
4. Consultar documentación de agentes

---

**🎨 Interfaz creada con ❤️ para facilitar el uso de agentes de IA**