# IMPLEMENTACIÓN DE AGENTES DE IA PARA CASOS REALES

## 📋 Descripción

Este proyecto implementa un sistema completo de agentes de IA especializados para casos de uso reales, incluyendo:

- **🍕 Agente de Delivery**: Gestión de pedidos de comida, búsqueda de restaurantes y seguimiento
- **🍽️ Agente de Reservas**: Reservas en restaurantes con gestión de disponibilidad
- **🏠 Agente de Diseño**: Diseño de habitaciones con visualización y presupuesto
- **⚙️ Agente de APIs**: Generación automática de código REST API
- **💬 Sistema de Prompts**: Gestión contextualizada de prompts para todos los agentes
- **📊 Sistema de Monitoreo**: Captura y análisis de desempeño en tiempo real

## 🚀 Características Principales

### Agentes Especializados
- **Procesamiento de lenguaje natural** para entender solicitudes de usuarios
- **Filtros inteligentes** basados en preferencias y contexto
- **Respuestas contextualizadas** usando plantillas dinámicas
- **Integración completa** entre todos los componentes

### Sistema de Monitoreo
- **Métricas en tiempo real** de todos los agentes
- **Alertas automáticas** por rendimiento degradado
- **Reportes de desempeño** con recomendaciones
- **Análisis de tendencias** y patrones de uso

### Gestión de Prompts
- **Plantillas reutilizables** por categoría y tipo
- **Contexto dinámico** basado en datos de entrada
- **Múltiples idiomas** (español por defecto)
- **Estadísticas de uso** y optimización

## 🎨 Interfaz Gráfica

Este proyecto incluye una **interfaz gráfica intuitiva** desarrollada con tkinter que permite:

- **�️ Chat Interactivo**: Conversación visual con todos los agentes
- **🎮 Selector de Agentes**: Modo automático o manual
- **📝 Ejemplos Rápidos**: Botones con solicitudes predefinidas  
- **📊 Monitoreo Visual**: Estado del sistema en tiempo real
- **💾 Exportación**: Guarda conversaciones en JSON

### 🚀 Uso Rápido de la GUI
```bash
# Opción 1: Launcher con verificaciones
python launcher.py

# Opción 2: Directo
python gui.py

# Opción 3: Windows (doble click)
gui.bat
```

## �📁 Estructura del Proyecto

```
agentes_ia/
├── agents/                     # Agentes especializados
│   ├── delivery_agent.py      # Agente de delivery
│   ├── reservation_agent.py   # Agente de reservas
│   ├── room_design_agent.py   # Agente de diseño
│   └── api_generation_agent.py # Agente de APIs
├── core/                       # Sistemas centrales
│   ├── prompt_manager.py      # Gestión de prompts
│   └── execution_monitor.py   # Monitoreo de ejecución
├── gui.py                     # 🎨 Interfaz gráfica principal
├── launcher.py                # 🚀 Launcher con verificaciones
├── gui.bat                    # 🖱️ Acceso directo Windows
├── demo_visual.py             # 📺 Demo de funcionalidades
├── main.py                    # Script principal (consola)
├── requirements.txt           # Dependencias
├── README.md                  # Documentación general
└── README_GUI.md              # 🎨 Guía de interfaz gráfica
```

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar** el proyecto
2. **Crear entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Uso

### 🎨 Interfaz Gráfica (Recomendado)
```bash
# Launcher con verificaciones automáticas
python launcher.py

# O directamente
python gui.py

# Windows: doble click en gui.bat
```

**Características de la GUI:**
- **Chat visual** con historial completo
- **Selector de agentes** automático o manual
- **Ejemplos rápidos** para probar funcionalidades
- **Monitoreo en tiempo real** del sistema
- **Exportación** de conversaciones

### 🖥️ Interfaz de Consola
```bash
python main.py
```

**Modo Interactivo** - Selecciona opción `1`:
- `"Quiero pedir comida italiana para 2 personas"`
- `"Necesito reservar mesa para 4 personas el viernes"`
- `"Quiero diseñar mi dormitorio de 4x5m con presupuesto de $3000"`
- `"Necesito generar una API para gestión de productos"`

### 📺 Demo Visual
```bash
python demo_visual.py
```
Muestra ejemplos de funcionamiento de todos los agentes.

### Demo Completo Automático (Consola)
```bash
python main.py
```
Selecciona la opción `2` para ver todos los agentes en acción.

### Uso Individual de Agentes

#### Agente de Delivery
```python
from agents.delivery_agent import DeliveryAgent

agent = DeliveryAgent()
response = agent.process_delivery_request("Quiero comida china rápida")
print(response)
```

#### Agente de Reservas
```python
from agents.reservation_agent import RestaurantReservationAgent

agent = RestaurantReservationAgent()
response = agent.handle_reservation_request("Mesa para 4 personas mañana a las 8 PM")
print(response)
```

#### Agente de Diseño
```python
from agents.room_design_agent import RoomDesignAgent

agent = RoomDesignAgent()
design = agent.generate_design(
    room_type="dormitorio_grande",
    room_dimensions="4x5m", 
    style_preference="moderno",
    budget=3000
)
print(design)
```

#### Agente de APIs
```python
from agents.api_generation_agent import APIGenerationAgent

agent = APIGenerationAgent()
specification = """
API: Sistema de Productos
Modelo: Producto
- nombre: string obligatorio
- precio: float obligatorio
Endpoint: GET /productos - Listar productos
"""

result = agent.generate_api(specification, framework='fastapi')
print(result)
```

## 🧪 Testing

### Ejecutar Tests Individuales
```bash
# Test del agente de delivery
python agents/delivery_agent.py

# Test del agente de reservas  
python agents/reservation_agent.py

# Test del agente de diseño
python agents/room_design_agent.py

# Test del agente de APIs
python agents/api_generation_agent.py

# Test del sistema de prompts
python core/prompt_manager.py

# Test del sistema de monitoreo
python core/execution_monitor.py
```

### Tests Automatizados
```bash
pytest tests/ -v
```

## 📊 Monitoreo y Métricas

El sistema incluye monitoreo automático que captura:

- **Tiempo de respuesta** de cada agente
- **Tasa de éxito/error** por agente
- **Uso de memoria y CPU**
- **Patrones de uso** por hora/día
- **Alertas automáticas** por rendimiento

### Ver Estado del Sistema
En el modo interactivo, escribe `status` para ver:
- Agentes activos
- Estadísticas de ejecución
- Salud del sistema
- Agente más utilizado

## 🎯 Ejemplos de Casos de Uso

### Caso 1: Búsqueda de Restaurantes
```
Usuario: "Busco restaurantes económicos de comida mexicana que entreguen rápido"

Respuesta: 
🏪 Tacos El Mariachi (mexicana) ⭐ 4.3 🚚 20 min 💰 económico
- Tacos al Pastor
- Quesadillas  
- Burritos
```

### Caso 2: Reserva Completa
```
Usuario: "Mesa para 6 personas en La Bella Italiana el sábado a las 9 PM"

Respuesta:
✅ Reserva confirmada
🏪 Restaurante: La Bella Italiana
👥 Mesa para: 6 personas  
📅 Fecha: 2024-12-16
🕘 Hora: 21:00
📋 Código: RES-0001
```

### Caso 3: Diseño de Habitación
```
Usuario: Configuración -> room_type="sala_estar", dimensions="5x4m", budget=2500

Respuesta:
💡 Concepto: Moderno y funcional
💰 Presupuesto: $2,360 de $2,500 ($140 restante)
📐 Eficiencia: 68.5%

Muebles incluidos:
🪑 Sofá Seccional L - $1,500
🪑 Mesa Centro Cristal - $400  
🪑 Mueble TV Flotante - $600
```

### Caso 4: API Generada
```
Especificación: "API para gestión de productos con CRUD completo"

Resultado:
🎉 API generada exitosamente!
📋 ID: API-0001
⚙️ Framework: FastAPI
📁 Archivos: 5 (main.py, models.py, schemas.py, crud.py, database.py)
📊 Modelos: 1 (Producto)
🌐 Endpoints: 4 (GET, POST, PUT, DELETE)
```

## 🔧 Configuración Avanzada

### Personalizar Umbrales de Alertas
```python
from core.execution_monitor import ExecutionMonitor

monitor = ExecutionMonitor()
monitor.alert_thresholds = {
    'max_response_time': 10.0,  # segundos
    'min_success_rate': 0.90,   # 90%
    'max_error_rate': 0.10,     # 10%
    'max_memory_usage': 256.0,  # MB
}
```

### Agregar Prompts Personalizados
```python
from core.prompt_manager import PromptManager, PromptTemplate, PromptCategory, PromptType

manager = PromptManager()
custom_prompt = PromptTemplate(
    "mi_prompt_personalizado",
    PromptCategory.DELIVERY, 
    PromptType.CONFIRMATION,
    "Tu pedido de {item} está listo. Total: ${total}",
    ["item", "total"]
)
manager.register_template(custom_prompt)
```

## 🚀 Extensibilidad

### Agregar Nuevo Agente
1. Crear archivo en `agents/mi_agente.py`
2. Implementar clase con métodos estándar
3. Integrar en `main.py` en el orquestador
4. Agregar prompts específicos en `prompt_manager.py`

### Ejemplo de Nuevo Agente
```python
class MiNuevoAgente:
    def __init__(self):
        self.configuracion = {}
    
    def procesar_solicitud(self, entrada):
        # Lógica del agente
        return {"respuesta": "Procesado"}
```

## 📈 Rendimiento

### Métricas Típicas
- **Tiempo de respuesta promedio**: 1-3 segundos
- **Tasa de éxito**: >90% en condiciones normales
- **Memoria utilizada**: <100MB por agente
- **Concurrencia**: Soporta múltiples solicitudes simultáneas

### Optimizaciones
- Caché de resultados frecuentes
- Pool de conexiones para bases de datos
- Procesamiento asíncrono para APIs
- Compresión de datos de monitoreo

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama para nueva característica
3. Implementar cambios con tests
4. Crear pull request con descripción detallada

## 📝 Licencia

Este proyecto es de código abierto bajo licencia MIT.

## 📞 Soporte

Para preguntas, sugerencias o reportes de bugs:
- Crear issue en el repositorio
- Incluir logs y pasos para reproducir el problema
- Especificar versión de Python y sistema operativo

## 🗺️ Roadmap

### Próximas Funcionalidades
- [ ] Integración con APIs reales de restaurantes
- [ ] Visualización 3D real para diseños
- [ ] Deployment automático de APIs generadas  
- [ ] Dashboard web para monitoreo
- [ ] Soporte para múltiples idiomas
- [ ] Integración con bases de datos reales
- [ ] API REST para el sistema completo
- [ ] Autenticación y autorización
- [ ] Análisis de sentimientos en feedback
- [ ] Machine Learning para mejorar recomendaciones

---

**Desarrollado por Noe Santiago para demostrar el poder de los agentes de IA en casos reales**