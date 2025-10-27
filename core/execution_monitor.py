"""
Sistema de monitoreo y evaluación para agentes de IA
Captura, analiza y evalúa el desempeño de todos los agentes
"""

import json
import time
import traceback
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import threading
from collections import defaultdict


class ExecutionStatus(Enum):
    """Estados de ejecución"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    TIMEOUT = "timeout"
    PARTIAL_SUCCESS = "partial_success"


class MetricType(Enum):
    """Tipos de métricas"""
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    ERROR_RATE = "error_rate"
    USER_SATISFACTION = "user_satisfaction"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"


@dataclass
class ExecutionRecord:
    """Registro de ejecución de un agente"""
    execution_id: str
    agent_name: str
    agent_type: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    start_time: datetime
    end_time: Optional[datetime]
    execution_time: Optional[float]
    status: ExecutionStatus
    error_message: Optional[str]
    error_traceback: Optional[str]
    memory_usage: Optional[float]
    cpu_usage: Optional[float]
    context_size: Optional[int]
    user_id: Optional[str]
    session_id: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        data = asdict(self)
        # Convertir datetime a string
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat() if self.end_time else None
        data['status'] = self.status.value
        return data


@dataclass
class PerformanceMetrics:
    """Métricas de desempeño"""
    metric_id: str
    agent_name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['metric_type'] = self.metric_type.value
        return data


class ExecutionMonitor:
    """Monitor principal de ejecución de agentes"""
    
    def __init__(self, max_records: int = 10000):
        self.execution_records: List[ExecutionRecord] = []
        self.performance_metrics: List[PerformanceMetrics] = []
        self.max_records = max_records
        self.active_executions: Dict[str, ExecutionRecord] = {}
        self.alert_thresholds = self._initialize_thresholds()
        self.listeners: List[Callable] = []
        self._lock = threading.Lock()
    
    def _initialize_thresholds(self) -> Dict[str, float]:
        """Inicializa umbrales de alerta"""
        return {
            'max_response_time': 30.0,  # segundos
            'min_success_rate': 0.85,   # 85%
            'max_error_rate': 0.15,     # 15%
            'max_memory_usage': 512.0,  # MB
            'max_cpu_usage': 80.0       # %
        }
    
    def start_execution(self, agent_name: str, agent_type: str, input_data: Dict[str, Any],
                       user_id: str = None, session_id: str = None) -> str:
        """Inicia el monitoreo de una ejecución"""
        execution_id = f"{agent_name}_{int(time.time() * 1000)}"
        
        record = ExecutionRecord(
            execution_id=execution_id,
            agent_name=agent_name,
            agent_type=agent_type,
            input_data=input_data,
            output_data=None,
            start_time=datetime.now(),
            end_time=None,
            execution_time=None,
            status=ExecutionStatus.SUCCESS,
            error_message=None,
            error_traceback=None,
            memory_usage=self._get_memory_usage(),
            cpu_usage=self._get_cpu_usage(),
            context_size=len(str(input_data)),
            user_id=user_id,
            session_id=session_id
        )
        
        with self._lock:
            self.active_executions[execution_id] = record
        
        return execution_id
    
    def end_execution(self, execution_id: str, output_data: Dict[str, Any] = None,
                     status: ExecutionStatus = ExecutionStatus.SUCCESS,
                     error_message: str = None) -> ExecutionRecord:
        """Finaliza el monitoreo de una ejecución"""
        with self._lock:
            if execution_id not in self.active_executions:
                raise ValueError(f"Ejecución no encontrada: {execution_id}")
            
            record = self.active_executions[execution_id]
            record.end_time = datetime.now()
            record.execution_time = (record.end_time - record.start_time).total_seconds()
            record.output_data = output_data
            record.status = status
            record.error_message = error_message
            
            if status == ExecutionStatus.ERROR and error_message:
                record.error_traceback = traceback.format_exc()
            
            # Mover a historial
            self.execution_records.append(record)
            del self.active_executions[execution_id]
            
            # Limpiar registros antiguos si es necesario
            if len(self.execution_records) > self.max_records:
                self.execution_records = self.execution_records[-self.max_records:]
            
            # Calcular métricas
            self._calculate_metrics(record)
            
            # Verificar alertas
            self._check_alerts(record)
            
            # Notificar listeners
            self._notify_listeners(record)
        
        return record
    
    def capture_execution(self, agent_name: str, agent_type: str, input_data: Dict[str, Any],
                         output_data: Dict[str, Any], execution_time: float,
                         status: ExecutionStatus = ExecutionStatus.SUCCESS,
                         error_message: str = None, user_id: str = None) -> ExecutionRecord:
        """Captura una ejecución completa (método simplificado)"""
        execution_id = self.start_execution(agent_name, agent_type, input_data, user_id)
        
        # Simular tiempo de ejecución
        time.sleep(0.001)  # Pequeña pausa para simular procesamiento
        
        return self.end_execution(execution_id, output_data, status, error_message)
    
    def _calculate_metrics(self, record: ExecutionRecord):
        """Calcula métricas basadas en el registro de ejecución"""
        timestamp = datetime.now()
        
        # Métrica de tiempo de respuesta
        if record.execution_time:
            self.performance_metrics.append(PerformanceMetrics(
                metric_id=f"rt_{record.execution_id}",
                agent_name=record.agent_name,
                metric_type=MetricType.RESPONSE_TIME,
                value=record.execution_time,
                timestamp=timestamp,
                context={"execution_id": record.execution_id}
            ))
        
        # Métrica de éxito/error
        success_value = 1.0 if record.status == ExecutionStatus.SUCCESS else 0.0
        self.performance_metrics.append(PerformanceMetrics(
            metric_id=f"sr_{record.execution_id}",
            agent_name=record.agent_name,
            metric_type=MetricType.SUCCESS_RATE,
            value=success_value,
            timestamp=timestamp,
            context={"status": record.status.value}
        ))
        
        # Métrica de completitud (basada en si hay output)
        completeness = 1.0 if record.output_data else 0.0
        self.performance_metrics.append(PerformanceMetrics(
            metric_id=f"comp_{record.execution_id}",
            agent_name=record.agent_name,
            metric_type=MetricType.COMPLETENESS,
            value=completeness,
            timestamp=timestamp,
            context={"has_output": bool(record.output_data)}
        ))
    
    def _check_alerts(self, record: ExecutionRecord):
        """Verifica si se deben disparar alertas"""
        alerts = []
        
        # Alerta por tiempo de respuesta
        if (record.execution_time and 
            record.execution_time > self.alert_thresholds['max_response_time']):
            alerts.append({
                'type': 'slow_response',
                'message': f"Respuesta lenta: {record.execution_time:.2f}s",
                'severity': 'warning'
            })
        
        # Alerta por error
        if record.status == ExecutionStatus.ERROR:
            alerts.append({
                'type': 'execution_error',
                'message': f"Error en ejecución: {record.error_message}",
                'severity': 'error'
            })
        
        # Alerta por uso de memoria
        if (record.memory_usage and 
            record.memory_usage > self.alert_thresholds['max_memory_usage']):
            alerts.append({
                'type': 'high_memory',
                'message': f"Uso alto de memoria: {record.memory_usage:.1f}MB",
                'severity': 'warning'
            })
        
        # Procesar alertas
        for alert in alerts:
            self._process_alert(alert, record)
    
    def _process_alert(self, alert: Dict[str, Any], record: ExecutionRecord):
        """Procesa una alerta"""
        print(f"🚨 ALERTA [{alert['severity'].upper()}]: {alert['message']} - {record.agent_name}")
    
    def _notify_listeners(self, record: ExecutionRecord):
        """Notifica a los listeners sobre nueva ejecución"""
        for listener in self.listeners:
            try:
                listener(record)
            except Exception as e:
                print(f"Error en listener: {e}")
    
    def add_listener(self, listener: Callable[[ExecutionRecord], None]):
        """Agrega un listener para eventos de ejecución"""
        self.listeners.append(listener)
    
    def _get_memory_usage(self) -> float:
        """Obtiene uso actual de memoria (simulado)"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 64.0  # Valor simulado
    
    def _get_cpu_usage(self) -> float:
        """Obtiene uso actual de CPU (simulado)"""
        try:
            import psutil
            return psutil.cpu_percent()
        except ImportError:
            return 25.0  # Valor simulado
    
    def get_agent_statistics(self, agent_name: str, hours: int = 24) -> Dict[str, Any]:
        """Obtiene estadísticas de un agente específico"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filtrar registros del agente en el período
        agent_records = [
            r for r in self.execution_records 
            if r.agent_name == agent_name and r.start_time >= cutoff_time
        ]
        
        if not agent_records:
            return {
                'agent_name': agent_name,
                'period_hours': hours,
                'total_executions': 0,
                'message': 'No hay datos para el período especificado'
            }
        
        # Calcular estadísticas
        total_executions = len(agent_records)
        successful_executions = len([r for r in agent_records if r.status == ExecutionStatus.SUCCESS])
        error_executions = len([r for r in agent_records if r.status == ExecutionStatus.ERROR])
        
        execution_times = [r.execution_time for r in agent_records if r.execution_time]
        
        stats = {
            'agent_name': agent_name,
            'period_hours': hours,
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'error_executions': error_executions,
            'success_rate': successful_executions / total_executions if total_executions > 0 else 0,
            'error_rate': error_executions / total_executions if total_executions > 0 else 0,
            'avg_response_time': statistics.mean(execution_times) if execution_times else 0,
            'median_response_time': statistics.median(execution_times) if execution_times else 0,
            'min_response_time': min(execution_times) if execution_times else 0,
            'max_response_time': max(execution_times) if execution_times else 0,
            'last_execution': max(agent_records, key=lambda r: r.start_time).start_time.isoformat()
        }
        
        return stats
    
    def get_system_overview(self, hours: int = 24) -> Dict[str, Any]:
        """Obtiene vista general del sistema"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_records = [r for r in self.execution_records if r.start_time >= cutoff_time]
        
        if not recent_records:
            return {
                'period_hours': hours,
                'total_executions': 0,
                'message': 'No hay datos para el período especificado'
            }
        
        # Estadísticas por agente
        agents = {}
        for record in recent_records:
            if record.agent_name not in agents:
                agents[record.agent_name] = []
            agents[record.agent_name].append(record)
        
        agent_stats = {}
        for agent_name, records in agents.items():
            successful = len([r for r in records if r.status == ExecutionStatus.SUCCESS])
            agent_stats[agent_name] = {
                'executions': len(records),
                'success_rate': successful / len(records),
                'avg_response_time': statistics.mean([r.execution_time for r in records if r.execution_time])
            }
        
        # Estadísticas generales
        total_executions = len(recent_records)
        successful_executions = len([r for r in recent_records if r.status == ExecutionStatus.SUCCESS])
        execution_times = [r.execution_time for r in recent_records if r.execution_time]
        
        overview = {
            'period_hours': hours,
            'total_executions': total_executions,
            'unique_agents': len(agents),
            'overall_success_rate': successful_executions / total_executions,
            'avg_response_time': statistics.mean(execution_times) if execution_times else 0,
            'agent_statistics': agent_stats,
            'most_active_agent': max(agents.keys(), key=lambda k: len(agents[k])) if agents else None,
            'slowest_agent': max(agent_stats.keys(), key=lambda k: agent_stats[k]['avg_response_time']) if agent_stats else None,
            'fastest_agent': min(agent_stats.keys(), key=lambda k: agent_stats[k]['avg_response_time']) if agent_stats else None
        }
        
        return overview
    
    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Genera reporte completo de desempeño"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_records = [r for r in self.execution_records if r.start_time >= cutoff_time]
        recent_metrics = [m for m in self.performance_metrics if m.timestamp >= cutoff_time]
        
        if not recent_records:
            return {
                'report_generated': datetime.now().isoformat(),
                'period_hours': hours,
                'message': 'No hay datos suficientes para generar el reporte'
            }
        
        # Análisis de errores comunes
        error_records = [r for r in recent_records if r.status == ExecutionStatus.ERROR]
        error_analysis = defaultdict(int)
        for record in error_records:
            if record.error_message:
                # Simplificar mensaje de error para agrupar
                simplified_error = record.error_message.split(':')[0] if ':' in record.error_message else record.error_message
                error_analysis[simplified_error] += 1
        
        # Tendencias de tiempo de respuesta
        response_time_metrics = [m for m in recent_metrics if m.metric_type == MetricType.RESPONSE_TIME]
        response_trends = {}
        for metric in response_time_metrics:
            hour = metric.timestamp.hour
            if hour not in response_trends:
                response_trends[hour] = []
            response_trends[hour].append(metric.value)
        
        # Promedios por hora
        hourly_averages = {
            hour: statistics.mean(times) 
            for hour, times in response_trends.items()
        }
        
        # Recomendaciones
        recommendations = self._generate_recommendations(recent_records, recent_metrics)
        
        report = {
            'report_generated': datetime.now().isoformat(),
            'period_hours': hours,
            'summary': {
                'total_executions': len(recent_records),
                'total_agents': len(set(r.agent_name for r in recent_records)),
                'overall_success_rate': len([r for r in recent_records if r.status == ExecutionStatus.SUCCESS]) / len(recent_records),
                'avg_response_time': statistics.mean([r.execution_time for r in recent_records if r.execution_time]),
                'total_errors': len(error_records)
            },
            'error_analysis': dict(error_analysis),
            'response_time_trends': hourly_averages,
            'agent_performance': {
                agent: self.get_agent_statistics(agent, hours)
                for agent in set(r.agent_name for r in recent_records)
            },
            'recommendations': recommendations,
            'alerts_triggered': self._count_alerts(recent_records)
        }
        
        return report
    
    def _generate_recommendations(self, records: List[ExecutionRecord], 
                                metrics: List[PerformanceMetrics]) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []
        
        if not records:
            return recommendations
        
        # Análizar tiempos de respuesta
        response_times = [r.execution_time for r in records if r.execution_time]
        if response_times:
            avg_time = statistics.mean(response_times)
            if avg_time > 10:
                recommendations.append(f"Tiempo de respuesta promedio alto ({avg_time:.2f}s). Considerar optimización.")
        
        # Analizar tasa de error
        error_rate = len([r for r in records if r.status == ExecutionStatus.ERROR]) / len(records)
        if error_rate > 0.1:
            recommendations.append(f"Tasa de error alta ({error_rate:.1%}). Revisar logs y validaciones.")
        
        # Analizar uso de memoria
        memory_usages = [r.memory_usage for r in records if r.memory_usage]
        if memory_usages:
            avg_memory = statistics.mean(memory_usages)
            if avg_memory > 256:
                recommendations.append(f"Uso promedio de memoria alto ({avg_memory:.1f}MB). Optimizar gestión de memoria.")
        
        # Analizar patrones por agente
        agent_counts = defaultdict(int)
        for record in records:
            agent_counts[record.agent_name] += 1
        
        most_used = max(agent_counts.keys(), key=lambda k: agent_counts[k])
        if agent_counts[most_used] > len(records) * 0.7:
            recommendations.append(f"Agente '{most_used}' maneja {agent_counts[most_used]/len(records):.1%} del tráfico. Considerar balance de carga.")
        
        return recommendations
    
    def _count_alerts(self, records: List[ExecutionRecord]) -> Dict[str, int]:
        """Cuenta alertas por tipo"""
        alerts = {
            'slow_response': 0,
            'execution_error': 0,
            'high_memory': 0,
            'high_cpu': 0
        }
        
        for record in records:
            if record.execution_time and record.execution_time > self.alert_thresholds['max_response_time']:
                alerts['slow_response'] += 1
            if record.status == ExecutionStatus.ERROR:
                alerts['execution_error'] += 1
            if record.memory_usage and record.memory_usage > self.alert_thresholds['max_memory_usage']:
                alerts['high_memory'] += 1
        
        return alerts
    
    def export_data(self, format_type: str = 'json', hours: int = 24) -> str:
        """Exporta datos de monitoreo"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_records = [r for r in self.execution_records if r.start_time >= cutoff_time]
        recent_metrics = [m for m in self.performance_metrics if m.timestamp >= cutoff_time]
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'period_hours': hours,
            'execution_records': [r.to_dict() for r in recent_records],
            'performance_metrics': [m.to_dict() for m in recent_metrics]
        }
        
        if format_type == 'json':
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")


# Decorador para monitoreo automático
def monitor_execution(monitor: ExecutionMonitor, agent_name: str, agent_type: str):
    """Decorador para monitorear automáticamente funciones de agentes"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Preparar datos de entrada
            input_data = {
                'args': str(args)[:500],  # Limitar tamaño
                'kwargs': {k: str(v)[:200] for k, v in kwargs.items()}
            }
            
            execution_id = monitor.start_execution(agent_name, agent_type, input_data)
            
            try:
                result = func(*args, **kwargs)
                
                # Preparar datos de salida
                output_data = {
                    'result_type': type(result).__name__,
                    'result_size': len(str(result)) if result else 0,
                    'has_result': result is not None
                }
                
                monitor.end_execution(execution_id, output_data, ExecutionStatus.SUCCESS)
                return result
                
            except Exception as e:
                monitor.end_execution(execution_id, None, ExecutionStatus.ERROR, str(e))
                raise
        
        return wrapper
    return decorator


# Función de demostración
def demo_execution_monitor():
    """Demuestra la funcionalidad del monitor de ejecución"""
    monitor = ExecutionMonitor()
    
    print("=== DEMO: SISTEMA DE MONITOREO DE AGENTES ===\n")
    
    # Simular ejecuciones de diferentes agentes
    agents_data = [
        {"name": "delivery_agent", "type": "delivery", "success_rate": 0.9, "avg_time": 2.5},
        {"name": "reservation_agent", "type": "reservation", "success_rate": 0.95, "avg_time": 1.8},
        {"name": "design_agent", "type": "design", "success_rate": 0.85, "avg_time": 5.2},
        {"name": "api_agent", "type": "api_generation", "success_rate": 0.88, "avg_time": 8.1}
    ]
    
    print("1. Simulando ejecuciones de agentes...")
    
    # Simular 50 ejecuciones
    import random
    for i in range(50):
        agent_data = random.choice(agents_data)
        
        # Simular datos de entrada
        input_data = {
            "user_request": f"Solicitud {i+1}",
            "timestamp": datetime.now().isoformat(),
            "user_id": f"user_{random.randint(1, 10)}"
        }
        
        # Simular resultado basado en tasa de éxito
        is_success = random.random() < agent_data["success_rate"]
        status = ExecutionStatus.SUCCESS if is_success else ExecutionStatus.ERROR
        
        # Simular tiempo de ejecución
        execution_time = agent_data["avg_time"] + random.uniform(-1, 2)
        
        # Datos de salida
        output_data = None
        error_message = None
        
        if is_success:
            output_data = {
                "response": f"Respuesta del {agent_data['name']}",
                "success": True,
                "data_size": random.randint(100, 1000)
            }
        else:
            error_message = random.choice([
                "Connection timeout",
                "Invalid input format",
                "Service unavailable",
                "Rate limit exceeded"
            ])
        
        # Registrar ejecución
        monitor.capture_execution(
            agent_name=agent_data["name"],
            agent_type=agent_data["type"],
            input_data=input_data,
            output_data=output_data,
            execution_time=execution_time,
            status=status,
            error_message=error_message,
            user_id=input_data["user_id"]
        )
    
    print(f"✓ Simuladas {len(monitor.execution_records)} ejecuciones")
    print()
    
    # Mostrar estadísticas del sistema
    print("2. Vista general del sistema:")
    overview = monitor.get_system_overview(hours=1)
    print(f"Total de ejecuciones: {overview['total_executions']}")
    print(f"Agentes únicos: {overview['unique_agents']}")
    print(f"Tasa de éxito general: {overview['overall_success_rate']:.1%}")
    print(f"Tiempo promedio de respuesta: {overview['avg_response_time']:.2f}s")
    print(f"Agente más activo: {overview['most_active_agent']}")
    print(f"Agente más lento: {overview['slowest_agent']}")
    print()
    
    # Estadísticas por agente
    print("3. Estadísticas por agente:")
    for agent_name in overview['agent_statistics']:
        stats = monitor.get_agent_statistics(agent_name, hours=1)
        print(f"\n📊 {agent_name}:")
        print(f"  - Ejecuciones: {stats['total_executions']}")
        print(f"  - Éxito: {stats['success_rate']:.1%}")
        print(f"  - Errores: {stats['error_rate']:.1%}")
        print(f"  - Tiempo promedio: {stats['avg_response_time']:.2f}s")
        print(f"  - Rango de tiempo: {stats['min_response_time']:.2f}s - {stats['max_response_time']:.2f}s")
    
    print()
    
    # Generar reporte de desempeño
    print("4. Reporte de desempeño:")
    report = monitor.generate_performance_report(hours=1)
    
    print(f"📈 Resumen del período de {report['period_hours']} hora(s):")
    summary = report['summary']
    print(f"  - Total de ejecuciones: {summary['total_executions']}")
    print(f"  - Agentes activos: {summary['total_agents']}")
    print(f"  - Tasa de éxito: {summary['overall_success_rate']:.1%}")
    print(f"  - Tiempo promedio: {summary['avg_response_time']:.2f}s")
    print(f"  - Total de errores: {summary['total_errors']}")
    
    if report['error_analysis']:
        print("\n🚨 Análisis de errores:")
        for error_type, count in report['error_analysis'].items():
            print(f"  - {error_type}: {count} occurrencias")
    
    if report['recommendations']:
        print("\n💡 Recomendaciones:")
        for recommendation in report['recommendations']:
            print(f"  • {recommendation}")
    
    print("\n📊 Alertas disparadas:")
    alerts = report['alerts_triggered']
    for alert_type, count in alerts.items():
        if count > 0:
            print(f"  - {alert_type}: {count}")
    
    print()
    
    # Ejemplo de uso con decorador
    print("5. Ejemplo con decorador de monitoreo:")
    
    @monitor_execution(monitor, "example_agent", "example")
    def example_function(message: str) -> str:
        """Función de ejemplo para mostrar el decorador"""
        time.sleep(0.1)  # Simular procesamiento
        if "error" in message.lower():
            raise ValueError("Error simulado")
        return f"Procesado: {message}"
    
    # Ejecutar función monitoreada
    try:
        result = example_function("Hola mundo")
        print(f"✓ Resultado: {result}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    try:
        result = example_function("Esto causará error")
    except Exception as e:
        print(f"✗ Error capturado: {e}")
    
    # Mostrar estadísticas actualizadas
    print(f"\nEjecuciones totales después del ejemplo: {len(monitor.execution_records)}")


if __name__ == "__main__":
    demo_execution_monitor()