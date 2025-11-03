"""
Sistema de configuración centralizada para agentes de IA
Maneja settings, rutas, y configuraciones del sistema
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class GUIConfig:
    """Configuración de la interfaz gráfica"""
    window_width: int = 1200
    window_height: int = 800
    theme: str = "light"
    font_family: str = "Segoe UI"
    font_size: int = 10
    center_window: bool = True
    remember_position: bool = True
    enable_animations: bool = True


@dataclass
class LoggingConfig:
    """Configuración del sistema de logging"""
    log_level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    log_directory: str = "logs"
    max_log_files: int = 30
    log_format: str = "detailed"
    enable_colors: bool = True


@dataclass
class AgentConfig:
    """Configuración de agentes"""
    max_retry_attempts: int = 3
    timeout_seconds: int = 30
    enable_monitoring: bool = True
    cache_responses: bool = True
    cache_ttl_hours: int = 24


@dataclass
class SystemConfig:
    """Configuración general del sistema"""
    project_name: str = "Sistema de Agentes IA"
    version: str = "1.1.0"
    author: str = "Desarrollador"
    debug_mode: bool = False
    auto_save_interval: int = 300  # segundos
    max_memory_usage_mb: int = 512
    enable_telemetry: bool = False


class ConfigManager:
    """Gestor centralizado de configuración"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "app_config.json"
        self.user_config_file = self.config_dir / "user_config.json"
        
        # Configuraciones por defecto
        self.gui = GUIConfig()
        self.logging = LoggingConfig()
        self.agents = AgentConfig()
        self.system = SystemConfig()
        
        # Cargar configuraciones
        self.load_config()
    
    def load_config(self):
        """Carga configuración desde archivos"""
        # Cargar configuración base
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    base_config = json.load(f)
                self._update_from_dict(base_config)
            except Exception as e:
                print(f"⚠️ Error cargando configuración base: {e}")
        
        # Cargar configuración de usuario (override)
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self._update_from_dict(user_config)
            except Exception as e:
                print(f"⚠️ Error cargando configuración de usuario: {e}")
    
    def save_config(self, user_only: bool = True):
        """Guarda configuración a archivo"""
        config_data = {
            'gui': asdict(self.gui),
            'logging': asdict(self.logging),
            'agents': asdict(self.agents),
            'system': asdict(self.system),
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'version': self.system.version
            }
        }
        
        target_file = self.user_config_file if user_only else self.config_file
        
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuración guardada en: {target_file}")
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
    
    def _update_from_dict(self, config_dict: Dict[str, Any]):
        """Actualiza configuración desde diccionario"""
        if 'gui' in config_dict:
            self._update_dataclass(self.gui, config_dict['gui'])
        
        if 'logging' in config_dict:
            self._update_dataclass(self.logging, config_dict['logging'])
        
        if 'agents' in config_dict:
            self._update_dataclass(self.agents, config_dict['agents'])
        
        if 'system' in config_dict:
            self._update_dataclass(self.system, config_dict['system'])
    
    def _update_dataclass(self, obj, data: Dict[str, Any]):
        """Actualiza un dataclass con datos del diccionario"""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
    
    def get_paths(self) -> Dict[str, Path]:
        """Retorna rutas importantes del sistema"""
        base_dir = Path.cwd()
        
        return {
            'base': base_dir,
            'config': self.config_dir,
            'logs': base_dir / self.logging.log_directory,
            'agents': base_dir / 'agents',
            'core': base_dir / 'core',
            'data': base_dir / 'data',
            'tests': base_dir / 'tests',
            'temp': base_dir / 'temp'
        }
    
    def create_default_config(self):
        """Crea archivo de configuración por defecto"""
        if not self.config_file.exists():
            self.save_config(user_only=False)
            print(f"✅ Archivo de configuración por defecto creado: {self.config_file}")
    
    def validate_config(self) -> Dict[str, list]:
        """Valida la configuración actual"""
        issues = {
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Validar GUI
        if self.gui.window_width < 800:
            issues['warnings'].append("Ancho de ventana muy pequeño (< 800px)")
        
        if self.gui.window_height < 600:
            issues['warnings'].append("Alto de ventana muy pequeño (< 600px)")
        
        # Validar logging
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.log_level not in valid_levels:
            issues['errors'].append(f"Nivel de log inválido: {self.logging.log_level}")
        
        # Validar rutas
        paths = self.get_paths()
        for name, path in paths.items():
            if name in ['logs', 'temp'] and not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    issues['info'].append(f"Directorio creado: {path}")
                except Exception as e:
                    issues['errors'].append(f"No se pudo crear directorio {name}: {e}")
        
        # Validar agentes
        if self.agents.timeout_seconds < 5:
            issues['warnings'].append("Timeout muy bajo para agentes (< 5s)")
        
        if self.agents.max_retry_attempts > 10:
            issues['warnings'].append("Demasiados reintentos configurados (> 10)")
        
        return issues
    
    def get_env_var(self, key: str, default: Any = None, cast_type: type = str) -> Any:
        """Obtiene variable de entorno con casting"""
        value = os.getenv(key, default)
        
        if value is None:
            return default
        
        try:
            if cast_type == bool:
                # Si ya es bool, devolverlo directamente
                if isinstance(value, bool):
                    return value
                # Si es string, convertir a bool
                elif isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                else:
                    return bool(value)
            elif cast_type == int:
                return int(value)
            elif cast_type == float:
                return float(value)
            else:
                return cast_type(value)
        except (ValueError, TypeError):
            return default
    
    def apply_env_overrides(self):
        """Aplica overrides desde variables de entorno"""
        # GUI overrides
        self.gui.window_width = self.get_env_var('GUI_WIDTH', self.gui.window_width, int)
        self.gui.window_height = self.get_env_var('GUI_HEIGHT', self.gui.window_height, int)
        self.gui.theme = self.get_env_var('GUI_THEME', self.gui.theme)
        
        # Logging overrides
        self.logging.log_level = self.get_env_var('LOG_LEVEL', self.logging.log_level)
        self.logging.log_to_file = self.get_env_var('LOG_TO_FILE', self.logging.log_to_file, bool)
        
        # System overrides
        self.system.debug_mode = self.get_env_var('DEBUG_MODE', self.system.debug_mode, bool)
    
    def export_config(self, format: str = 'json') -> str:
        """Exporta configuración como string"""
        config_data = {
            'gui': asdict(self.gui),
            'logging': asdict(self.logging),
            'agents': asdict(self.agents),
            'system': asdict(self.system)
        }
        
        return json.dumps(config_data, indent=2, ensure_ascii=False)


# Instancia global
_config_manager = None

def get_config() -> ConfigManager:
    """Obtiene la instancia global del gestor de configuración"""
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.apply_env_overrides()
    
    return _config_manager


def init_config(config_dir: str = "config") -> ConfigManager:
    """Inicializa el sistema de configuración"""
    global _config_manager
    
    _config_manager = ConfigManager(config_dir)
    _config_manager.apply_env_overrides()
    
    # Validar configuración
    issues = _config_manager.validate_config()
    
    if issues['errors']:
        print("❌ Errores en configuración:")
        for error in issues['errors']:
            print(f"  • {error}")
    
    if issues['warnings']:
        print("⚠️ Advertencias de configuración:")
        for warning in issues['warnings']:
            print(f"  • {warning}")
    
    if issues['info']:
        print("ℹ️ Información:")
        for info in issues['info']:
            print(f"  • {info}")
    
    return _config_manager


if __name__ == "__main__":
    # Ejemplo de uso
    config = init_config()
    
    print("Configuración actual:")
    print(config.export_config())
    
    # Ejemplo de modificación
    config.gui.window_width = 1400
    config.system.debug_mode = True
    
    # Guardar cambios
    config.save_config()