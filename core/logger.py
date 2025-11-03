"""
Sistema de logging mejorado para el sistema de agentes de IA
Proporciona logging estructurado con diferentes niveles y formatos
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


class ColoredFormatter(logging.Formatter):
    """Formatter personalizado con colores para la consola"""
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Obtener el color basado en el nivel
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formato personalizado
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Emoji según el nivel
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '💥'
        }
        emoji = emoji_map.get(record.levelname, '📝')
        
        # Formatear mensaje
        formatted = f"{color}{emoji} [{timestamp}] {record.levelname:<8} | {record.name:<20} | {record.getMessage()}{reset}"
        
        # Añadir información de excepción si existe
        if record.exc_info:
            formatted += f"\n{color}{self.formatException(record.exc_info)}{reset}"
            
        return formatted


class AgentLogger:
    """Clase principal para manejo de logging en el sistema de agentes"""
    
    def __init__(self, name: str = "AgentSystem", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar logger principal
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura los handlers para console y archivo"""
        
        # Handler para consola con colores
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        
        # Handler para archivo (todos los niveles)
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formato para archivo
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Handler para errores críticos (archivo separado)
        error_file = self.log_dir / f"{self.name}_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # Agregar handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
    
    def get_logger(self, component: str = None) -> logging.Logger:
        """Obtiene un logger para un componente específico"""
        if component:
            logger_name = f"{self.name}.{component}"
            return logging.getLogger(logger_name)
        return self.logger
    
    def log_agent_action(self, agent_name: str, action: str, data: Dict[str, Any] = None):
        """Log especializado para acciones de agentes"""
        logger = self.get_logger(agent_name)
        message = f"Acción: {action}"
        
        if data:
            # Serializar datos de forma segura
            try:
                data_str = json.dumps(data, ensure_ascii=False, indent=2)
                message += f"\nDatos: {data_str}"
            except (TypeError, ValueError):
                message += f"\nDatos: {str(data)}"
        
        logger.info(message)
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any] = None):
        """Log de errores con contexto adicional"""
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        self.logger.error(f"Error capturado: {json.dumps(error_data, ensure_ascii=False, indent=2)}", exc_info=True)
    
    def log_performance(self, component: str, operation: str, duration: float, success: bool = True):
        """Log de métricas de rendimiento"""
        logger = self.get_logger("Performance")
        status = "✅ Éxito" if success else "❌ Fallo"
        logger.info(f"{component}.{operation} | {duration:.3f}s | {status}")


# Instancia global del logger
_global_logger = None

def get_logger(component: str = None) -> logging.Logger:
    """Función helper para obtener logger global"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = AgentLogger()
    
    return _global_logger.get_logger(component)


def log_agent_action(agent_name: str, action: str, data: Dict[str, Any] = None):
    """Función helper para log de acciones de agentes"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = AgentLogger()
    
    _global_logger.log_agent_action(agent_name, action, data)


def log_error(error: Exception, context: Dict[str, Any] = None):
    """Función helper para log de errores"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = AgentLogger()
    
    _global_logger.log_error_with_context(error, context)


def log_performance(component: str, operation: str, duration: float, success: bool = True):
    """Función helper para log de rendimiento"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = AgentLogger()
    
    _global_logger.log_performance(component, operation, duration, success)


# Decorator para logging automático de funciones
def logged_function(component: str = None):
    """Decorator que añade logging automático a funciones"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(component or func.__module__)
            func_name = func.__name__
            
            try:
                logger.debug(f"Iniciando {func_name}")
                start_time = datetime.now()
                
                result = func(*args, **kwargs)
                
                duration = (datetime.now() - start_time).total_seconds()
                logger.debug(f"Completado {func_name} en {duration:.3f}s")
                log_performance(component or func.__module__, func_name, duration, True)
                
                return result
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                log_error(e, {
                    'function': func_name,
                    'args': str(args)[:200],  # Limitar longitud
                    'kwargs': str(kwargs)[:200]
                })
                log_performance(component or func.__module__, func_name, duration, False)
                raise
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Ejemplo de uso
    logger = get_logger("TestComponent")
    
    logger.debug("Mensaje de debug")
    logger.info("Mensaje informativo")
    logger.warning("Mensaje de advertencia")
    logger.error("Mensaje de error")
    
    # Ejemplo con decorator
    @logged_function("TestComponent")
    def test_function():
        logger.info("Función de prueba ejecutándose")
        return "resultado"
    
    result = test_function()
    print(f"Resultado: {result}")