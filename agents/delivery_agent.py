"""
PideBot - Agente de Delivery Inteligente y Proactivo
====================================================

Un asistente personal ejecutivo para gestión integral de delivery.
Maneja todo el ciclo: búsqueda, confirmación, pago seguro y monitoreo proactivo.

Características principales:
- Autonomía completa con confirmaciones de seguridad
- Monitoreo proactivo hasta la entrega
- Manejo seguro de pagos (solo tokens guardados)
- Comunicación clara y directa
- Persistencia de estado entre sesiones

Autor: Desarrollado según especificaciones del usuario
Versión: 2.0 - PideBot Avanzado
"""

import re
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


class EstadoPedido(Enum):
    """Estados posibles de un pedido de delivery"""
    CONFIRMANDO = "CONFIRMANDO"
    EN_PREPARACION = "EN_PREPARACION"
    MOTORIZADO_ASIGNADO = "MOTORIZADO_ASIGNADO"
    EN_CAMINO = "EN_CAMINO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


@dataclass
class Producto:
    """Modelo de producto de delivery"""
    producto_id: str
    nombre_producto: str
    precio: float
    restaurante_id: str
    restaurante_nombre: str
    descripcion: str = ""
    disponible: bool = True


@dataclass
class PedidoActivo:
    """Estado de un pedido en seguimiento"""
    pedido_id: str
    producto: Producto
    total_pagado: float
    estado_actual: EstadoPedido
    timestamp_inicio: datetime
    metodo_pago_usado: str
    usuario_notificado_estados: List[str]


@dataclass
class MetodoPagoGuardado:
    """Método de pago pre-registrado (solo token/ID)"""
    id: str
    nombre: str
    terminacion: str
    activo: bool = True


class RestauranteDB:
    """Base de datos simulada de restaurantes con productos específicos"""
    
    def __init__(self):
        self.restaurantes = {
            "NORKYS": {
                "nombre": "Norky's",
                "productos": {
                    "NORK-14P": {
                        "nombre": "1/4 Pollo a la Brasa + Papas + Ensalada",
                        "precio": 25.50,
                        "descripcion": "Cuarto de pollo tierno con papas fritas y ensalada fresca"
                    },
                    "NORK-12P": {
                        "nombre": "1/2 Pollo a la Brasa + Papas + Ensalada",
                        "precio": 35.90,
                        "descripcion": "Medio pollo jugoso con papas fritas y ensalada"
                    }
                }
            },
            "PARDOS": {
                "nombre": "Pardos Chicken",
                "productos": {
                    "PARD-14P": {
                        "nombre": "1/4 Pollo a la Brasa + Papas + Ensalada",
                        "precio": 28.00,
                        "descripcion": "Cuarto de pollo especial con papas doradas"
                    }
                }
            },
            "BEMBOS": {
                "nombre": "Bembos",
                "productos": {
                    "BEMB-HAM": {
                        "nombre": "Hamburguesa Doble con Queso",
                        "precio": 22.90,
                        "descripcion": "Hamburguesa doble carne con queso americano"
                    },
                    "BEMB-CLA": {
                        "nombre": "Hamburguesa Clásica",
                        "precio": 18.50,
                        "descripcion": "Hamburguesa tradicional con vegetales frescos"
                    }
                }
            }
        }
    
    def buscar_producto(self, query_producto: str, query_restaurante: str = None) -> List[Producto]:
        """Busca productos por nombre y restaurante"""
        resultados = []
        
        # Normalizar consultas
        query_producto = query_producto.lower()
        if query_restaurante:
            query_restaurante = query_restaurante.lower()
        
        for rest_id, rest_data in self.restaurantes.items():
            # Filtrar por restaurante si se especifica
            if query_restaurante and query_restaurante not in rest_data["nombre"].lower():
                continue
            
            for prod_id, prod_data in rest_data["productos"].items():
                # Buscar en nombre del producto
                if self._coincide_busqueda(query_producto, prod_data["nombre"]):
                    producto = Producto(
                        producto_id=prod_id,
                        nombre_producto=prod_data["nombre"],
                        precio=prod_data["precio"],
                        restaurante_id=rest_id,
                        restaurante_nombre=rest_data["nombre"],
                        descripcion=prod_data["descripcion"]
                    )
                    resultados.append(producto)
        
        return resultados
    
    def _coincide_busqueda(self, query: str, texto: str) -> bool:
        """Verifica si la consulta coincide con el texto del producto"""
        query_words = query.split()
        texto_lower = texto.lower()
        
        # Mapeo de sinónimos
        sinonimos = {
            "cuarto": ["1/4", "quarter"],
            "medio": ["1/2", "half"],
            "pollo": ["chicken"],
            "brasa": ["brasado", "a la brasa"],
            "hamburguesa": ["burger", "ham"],
            "doble": ["double", "2x"]
        }
        
        for word in query_words:
            word_found = word in texto_lower
            
            # Buscar sinónimos
            if not word_found:
                for key, values in sinonimos.items():
                    if word == key and any(v in texto_lower for v in values):
                        word_found = True
                        break
                    elif word in values and key in texto_lower:
                        word_found = True
                        break
            
            if word_found:
                return True
        
        return False


class PagosSeguroAPI:
    """Simulación de API de pagos segura"""
    
    def __init__(self):
        self.metodos_guardados = {
            "visa_1234": MetodoPagoGuardado("visa_1234", "Visa", "1234"),
            "master_5678": MetodoPagoGuardado("master_5678", "Mastercard", "5678")
        }
    
    def iniciar_pago(self, metodo_id: str, monto: float) -> Dict[str, Any]:
        """Procesa pago con método guardado"""
        if metodo_id not in self.metodos_guardados:
            return {
                "exito": False,
                "error_mensaje": "Método de pago no encontrado"
            }
        
        metodo = self.metodos_guardados[metodo_id]
        if not metodo.activo:
            return {
                "exito": False,
                "error_mensaje": "Método de pago inactivo"
            }
        
        # Simular verificaciones de pago
        import random
        
        # 90% de éxito, 10% de fallo simulado
        if random.random() < 0.9:
            pedido_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
            return {
                "exito": True,
                "pedido_id": pedido_id,
                "estado_actual": "CONFIRMANDO",
                "monto_cobrado": monto,
                "metodo_usado": f"{metodo.nombre} terminada en {metodo.terminacion}"
            }
        else:
            # Simular diferentes tipos de errores
            errores = [
                "Fondos insuficientes",
                "Tarjeta bloqueada",
                "Error de conexión con el banco"
            ]
            return {
                "exito": False,
                "error_mensaje": random.choice(errores)
            }


class MonitoreoAPI:
    """Simulación de API de monitoreo de pedidos"""
    
    def __init__(self):
        self.pedidos_estado = {}
        self.progresion_estados = [
            EstadoPedido.CONFIRMANDO,
            EstadoPedido.EN_PREPARACION,
            EstadoPedido.MOTORIZADO_ASIGNADO,
            EstadoPedido.EN_CAMINO,
            EstadoPedido.ENTREGADO
        ]
    
    def consultar_estado_pedido(self, pedido_id: str) -> Dict[str, Any]:
        """Consulta el estado actual de un pedido"""
        if pedido_id not in self.pedidos_estado:
            # Inicializar nuevo pedido
            self.pedidos_estado[pedido_id] = {
                "estado": EstadoPedido.CONFIRMANDO,
                "timestamp_ultimo_cambio": datetime.now(),
                "indice_progresion": 0
            }
        
        pedido_info = self.pedidos_estado[pedido_id]
        
        # Simular progresión automática del pedido
        tiempo_transcurrido = (datetime.now() - pedido_info["timestamp_ultimo_cambio"]).total_seconds()
        
        # Cada 15 segundos avanza al siguiente estado (para demo rápida)
        if tiempo_transcurrido > 15:
            indice_actual = pedido_info["indice_progresion"]
            if indice_actual < len(self.progresion_estados) - 1:
                pedido_info["indice_progresion"] += 1
                pedido_info["estado"] = self.progresion_estados[pedido_info["indice_progresion"]]
                pedido_info["timestamp_ultimo_cambio"] = datetime.now()
        
        return {
            "estado": pedido_info["estado"].value,
            "timestamp": pedido_info["timestamp_ultimo_cambio"].isoformat(),
            "estimado_entrega": (datetime.now() + timedelta(minutes=30)).isoformat()
        }


class CarritoCompras:
    """Gestor del carrito de compras"""
    
    def __init__(self):
        self.items = []
        self.costo_envio = 7.00
        self.comision_app = 0.15  # 15%
    
    def agregar_item(self, producto: Producto, cantidad: int = 1):
        """Agrega producto al carrito"""
        self.items.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": producto.precio * cantidad
        })
    
    def vaciar(self):
        """Vacía el carrito"""
        self.items = []
    
    def ver_total(self) -> Dict[str, float]:
        """Calcula el total del carrito con todos los costos"""
        subtotal = sum(item["subtotal"] for item in self.items)
        comision = subtotal * self.comision_app
        total = subtotal + self.costo_envio + comision
        
        return {
            "subtotal": round(subtotal, 2),
            "costo_envio": self.costo_envio,
            "comision": round(comision, 2),
            "total_pedido": round(total, 2)
        }


class PideBot:
    """
    PideBot - Agente de Delivery Proactivo y Seguro
    
    Personalidad: Asistente personal ejecutivo
    - Rápido, seguro, confiable y proactivo
    - Comunicación clara y directa
    - Especializado en costos y confirmaciones
    
    REGLAS DE ORO (INQUEBRANTABLES):
    1. SEGURIDAD ANTE TODO: Nunca maneja datos de pago directos
    2. CONFIRMACIÓN DE COSTO: Siempre confirma antes de pagar
    3. MEMORIA PERSISTENTE: Guarda pedidos activos para monitoreo
    4. MONITOREO PROACTIVO: Se auto-activa cada 10 minutos
    5. COMUNICACIÓN PROACTIVA: Notifica cada cambio importante
    """
    
    def __init__(self, notificar_usuario_callback: Callable = None, preguntar_usuario_callback: Callable = None):
        # APIs simuladas
        self.restaurant_db = RestauranteDB()
        self.pagos_api = PagosSeguroAPI()
        self.monitoreo_api = MonitoreoAPI()
        
        # Sistema de carrito
        self.carrito = CarritoCompras()
        
        # Callbacks para interacción
        self.notificar_usuario = notificar_usuario_callback or self._notificar_default
        self.preguntar_al_usuario = preguntar_usuario_callback or self._preguntar_default
        
        # Memoria persistente de pedidos activos
        self.pedidos_activos: Dict[str, PedidoActivo] = {}
        
        # Estado de conversación
        self.esperando_confirmacion = False
        self.producto_pendiente = None
        self.total_pendiente = None
        
        # Hilo de monitoreo
        self.monitoreo_activo = False
        self.hilo_monitoreo = None
        
        # Métodos de pago disponibles
        self.metodos_pago = {
            "visa_1234": "Visa terminada en 1234",
            "master_5678": "Mastercard terminada en 5678"
        }
        
        print("🤖 PideBot inicializado - ¡Listo para gestionar tus pedidos!")
    
    def procesar_solicitud(self, solicitud_usuario: str) -> str:
        """
        Punto de entrada principal para procesar solicitudes del usuario
        
        Args:
            solicitud_usuario: Texto natural del usuario
            
        Returns:
            Respuesta del agente
        """
        solicitud = solicitud_usuario.lower().strip()
        
        # Si estamos esperando confirmación de pago
        if self.esperando_confirmacion:
            return self._procesar_confirmacion_pago(solicitud)
        
        # Detectar tipo de solicitud
        if any(palabra in solicitud for palabra in ["estado", "seguimiento", "dónde está", "dónde", "pedido"]):
            return self._procesar_consulta_estado(solicitud)
        elif any(palabra in solicitud for palabra in ["quiero", "pide", "pedido", "ordenar"]):
            return self._procesar_nuevo_pedido(solicitud)
        elif any(palabra in solicitud for palabra in ["sí", "si", "dale", "ok", "confirmo"]):
            if self.esperando_confirmacion:
                return self._procesar_confirmacion_pago(solicitud)
        elif any(palabra in solicitud for palabra in ["no", "cancelar", "cancel"]):
            return self._cancelar_operacion_actual()
        else:
            return self._respuesta_bienvenida()
    
    def _procesar_nuevo_pedido(self, solicitud: str) -> str:
        """Procesa un nuevo pedido de delivery"""
        print(f"🔍 Procesando nuevo pedido: {solicitud}")
        
        # Extraer información del pedido
        info_pedido = self._extraer_info_pedido(solicitud)
        
        if not info_pedido["producto"]:
            return "❓ No pude identificar qué producto deseas. ¿Podrías ser más específico? Por ejemplo: 'Quiero una hamburguesa doble con queso de Bembos'"
        
        # 1. Buscar producto
        productos_encontrados = self.restaurant_db.buscar_producto(
            info_pedido["producto"], 
            info_pedido["restaurante"]
        )
        
        if not productos_encontrados:
            return self._buscar_alternativa(info_pedido["producto"])
        
        # Seleccionar mejor opción
        producto_seleccionado = productos_encontrados[0]
        
        # 2. Agregar al carrito
        self.carrito.vaciar()  # Limpiar carrito anterior
        self.carrito.agregar_item(producto_seleccionado)
        
        # 3. Obtener total
        totales = self.carrito.ver_total()
        
        # 4. Preparar confirmación (HITL obligatorio)
        self.esperando_confirmacion = True
        self.producto_pendiente = producto_seleccionado
        self.total_pendiente = totales["total_pedido"]
        
        # Formatear respuesta
        respuesta = f"""🎯 ¡Encontrado! 

📦 **{producto_seleccionado.nombre_producto}**
🏪 Restaurante: {producto_seleccionado.restaurante_nombre}
💰 Precio: S/ {producto_seleccionado.precio:.2f}
🚚 Envío: S/ {totales["costo_envio"]:.2f}
📱 Comisión: S/ {totales["comision"]:.2f}
💳 **TOTAL: S/ {totales["total_pedido"]:.2f}**

¿Confirmas el pedido con tu tarjeta guardada {self.metodos_pago['visa_1234']}?
Responde 'Sí' para confirmar o 'No' para cancelar."""
        
        return respuesta
    
    def _procesar_confirmacion_pago(self, respuesta: str) -> str:
        """Procesa la confirmación del usuario para el pago"""
        if any(palabra in respuesta.lower() for palabra in ["sí", "si", "dale", "ok", "confirmo", "acepto"]):
            return self._ejecutar_pago()
        elif any(palabra in respuesta.lower() for palabra in ["no", "cancelar", "cancel"]):
            return self._cancelar_operacion_actual()
        else:
            return "❓ Por favor responde 'Sí' para confirmar el pedido o 'No' para cancelar."
    
    def _ejecutar_pago(self) -> str:
        """Ejecuta el pago con el método guardado"""
        print("💳 Procesando pago...")
        
        resultado_pago = self.pagos_api.iniciar_pago("visa_1234", self.total_pendiente)
        
        if resultado_pago["exito"]:
            # Pago exitoso - guardar en memoria persistente
            pedido_activo = PedidoActivo(
                pedido_id=resultado_pago["pedido_id"],
                producto=self.producto_pendiente,
                total_pagado=self.total_pendiente,
                estado_actual=EstadoPedido.CONFIRMANDO,
                timestamp_inicio=datetime.now(),
                metodo_pago_usado=resultado_pago["metodo_usado"],
                usuario_notificado_estados=[]
            )
            
            self.pedidos_activos[resultado_pago["pedido_id"]] = pedido_activo
            
            # Iniciar monitoreo proactivo
            self._iniciar_monitoreo_proactivo()
            
            # Guardar referencias antes de limpiar
            nombre_restaurante = self.producto_pendiente.restaurante_nombre
            total_cobrado = self.total_pendiente
            
            # Limpiar estado de confirmación
            self._limpiar_estado_confirmacion()
            
            return f"""✅ ¡Pedido realizado exitosamente!

🆔 Número de pedido: **{resultado_pago["pedido_id"]}**
🏪 {nombre_restaurante} está confirmando tu orden
💳 Cobrado: S/ {total_cobrado:.2f} con {resultado_pago["metodo_usado"]}

📱 Te avisaré proactivamente de cada cambio de estado hasta la entrega.
🕐 El restaurante tardará unos minutos en confirmar."""
        
        else:
            # Error en el pago
            self._limpiar_estado_confirmacion()
            return f"""❌ Error en el pago: {resultado_pago["error_mensaje"]}

¿Quieres que intente con tu otro método guardado ({self.metodos_pago['master_5678']}) o prefieres cancelar?"""
    
    def _buscar_alternativa(self, producto_original: str) -> str:
        """Busca alternativas cuando el producto no se encuentra"""
        # Buscar en todos los restaurantes sin especificar uno
        todas_opciones = []
        for rest_id in self.restaurant_db.restaurantes:
            productos = self.restaurant_db.buscar_producto(producto_original)
            todas_opciones.extend(productos)
        
        if todas_opciones:
            alternativa = todas_opciones[0]
            return f"""❌ No encontré exactamente lo que buscas, pero tengo una alternativa:

🔄 **{alternativa.nombre_producto}**
🏪 {alternativa.restaurante_nombre} - S/ {alternativa.precio:.2f}

¿Te interesa este producto? Responde 'Sí' para agregarlo o dime qué más buscas."""
        
        return f"""❌ No encontré '{producto_original}' en nuestros restaurantes disponibles.

🍕 Productos populares disponibles:
• 1/4 Pollo a la Brasa (Norky's o Pardos)
• Hamburguesa Doble con Queso (Bembos)
• Hamburguesa Clásica (Bembos)

¿Cuál te interesa?"""
    
    def _extraer_info_pedido(self, solicitud: str) -> Dict[str, str]:
        """Extrae información del producto y restaurante de la solicitud"""
        solicitud_lower = solicitud.lower()
        
        # Detectar restaurantes
        restaurante = None
        if "norky" in solicitud_lower:
            restaurante = "Norky's"
        elif "pardo" in solicitud_lower:
            restaurante = "Pardos"
        elif "bembo" in solicitud_lower:
            restaurante = "Bembos"
        
        # Detectar productos
        producto = ""
        if any(palabra in solicitud_lower for palabra in ["cuarto", "1/4", "quarter"]):
            if any(palabra in solicitud_lower for palabra in ["pollo", "brasa"]):
                producto = "cuarto de pollo a la brasa"
        elif any(palabra in solicitud_lower for palabra in ["hamburguesa", "burger"]):
            if "doble" in solicitud_lower:
                producto = "hamburguesa doble con queso"
            else:
                producto = "hamburguesa"
        elif any(palabra in solicitud_lower for palabra in ["medio", "1/2"]):
            if "pollo" in solicitud_lower:
                producto = "medio pollo a la brasa"
        
        return {
            "producto": producto,
            "restaurante": restaurante
        }
    
    def _procesar_consulta_estado(self, solicitud: str) -> str:
        """Procesa consultas sobre el estado de pedidos"""
        if not self.pedidos_activos:
            return "📭 No tienes pedidos activos en este momento."
        
        # Mostrar estado de todos los pedidos activos
        respuestas = []
        for pedido_id, pedido in self.pedidos_activos.items():
            estado_actual = self.monitoreo_api.consultar_estado_pedido(pedido_id)
            respuestas.append(f"""📦 **Pedido {pedido_id}**
🍽️ {pedido.producto.nombre_producto}
📍 {pedido.producto.restaurante_nombre}
📊 Estado: {estado_actual['estado']}
⏰ Última actualización: {estado_actual['timestamp'][:19]}""")
        
        return "\n\n".join(respuestas)
    
    def _cancelar_operacion_actual(self) -> str:
        """Cancela la operación actual"""
        if self.esperando_confirmacion:
            self._limpiar_estado_confirmacion()
            return "❌ Pedido cancelado. ¿En qué más puedo ayudarte?"
        return "✅ No hay operaciones pendientes para cancelar."
    
    def _limpiar_estado_confirmacion(self):
        """Limpia el estado de confirmación pendiente"""
        self.esperando_confirmacion = False
        self.producto_pendiente = None
        self.total_pendiente = None
        self.carrito.vaciar()
    
    def _respuesta_bienvenida(self) -> str:
        """Respuesta de bienvenida y guía"""
        return """👋 ¡Hola! Soy **PideBot**, tu asistente de delivery ejecutivo.

🚀 Puedo ayudarte a:
• 🍽️ Hacer pedidos (ej: "Quiero una hamburguesa doble de Bembos")
• 📱 Consultar el estado de tus pedidos
• 🔍 Buscar productos en restaurantes

💡 **Ejemplos de pedidos:**
• "Quiero un cuarto de pollo a la brasa de Norky's"
• "Pídeme una hamburguesa doble con queso de Bembos"

¿Qué te gustaría ordenar hoy?"""
    
    def _iniciar_monitoreo_proactivo(self):
        """Inicia el monitoreo proactivo en segundo plano"""
        if not self.monitoreo_activo:
            self.monitoreo_activo = True
            self.hilo_monitoreo = threading.Thread(target=self._bucle_monitoreo, daemon=True)
            self.hilo_monitoreo.start()
            print("🔄 Monitoreo proactivo iniciado")
    
    def _bucle_monitoreo(self):
        """Bucle principal de monitoreo proactivo"""
        while self.monitoreo_activo and self.pedidos_activos:
            try:
                pedidos_a_eliminar = []
                
                for pedido_id, pedido in self.pedidos_activos.items():
                    estado_info = self.monitoreo_api.consultar_estado_pedido(pedido_id)
                    nuevo_estado = EstadoPedido(estado_info["estado"])
                    
                    # Verificar si el estado cambió
                    if nuevo_estado != pedido.estado_actual:
                        self._notificar_cambio_estado(pedido, nuevo_estado)
                        pedido.estado_actual = nuevo_estado
                    
                    # Si el pedido está completo, marcarlo para eliminación
                    if nuevo_estado in [EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO]:
                        pedidos_a_eliminar.append(pedido_id)
                
                # Eliminar pedidos completados
                for pedido_id in pedidos_a_eliminar:
                    del self.pedidos_activos[pedido_id]
                    print(f"✅ Pedido {pedido_id} completado y removido del monitoreo")
                
                # Si no hay más pedidos activos, detener monitoreo
                if not self.pedidos_activos:
                    self.monitoreo_activo = False
                    print("⏹️ Monitoreo proactivo detenido - No hay pedidos activos")
                    break
                
                # Esperar 10 segundos (en producción sería 10 minutos)
                time.sleep(10)
                
            except Exception as e:
                print(f"❌ Error en monitoreo: {e}")
                time.sleep(5)
    
    def _notificar_cambio_estado(self, pedido: PedidoActivo, nuevo_estado: EstadoPedido):
        """Notifica al usuario de cambios de estado importantes"""
        mensajes_estado = {
            EstadoPedido.EN_PREPARACION: f"🍳 ¡Buenas noticias! Tu pedido de {pedido.producto.restaurante_nombre} ya se está preparando.",
            EstadoPedido.MOTORIZADO_ASIGNADO: f"🏍️ ¡Tu pedido ya salió del restaurante! El motorizado está en camino.",
            EstadoPedido.EN_CAMINO: f"🚚 ¡El motorizado está llegando! Tu pedido está en camino a tu dirección.",
            EstadoPedido.ENTREGADO: f"✅ ¡Entregado! Tu pedido de {pedido.producto.restaurante_nombre} ha sido entregado. ¡Que lo disfrutes! 🍽️",
            EstadoPedido.CANCELADO: f"❌ Lo siento, {pedido.producto.restaurante_nombre} canceló tu pedido. Te contactaremos para el reembolso."
        }
        
        mensaje = mensajes_estado.get(nuevo_estado, f"📱 Estado actualizado: {nuevo_estado.value}")
        self.notificar_usuario(mensaje)
    
    def _notificar_default(self, mensaje: str):
        """Notificación por defecto (consola)"""
        print(f"🔔 NOTIFICACIÓN: {mensaje}")
    
    def _preguntar_default(self, pregunta: str) -> str:
        """Pregunta por defecto (consola)"""
        return input(f"❓ {pregunta}: ")
    
    def obtener_estado_sistema(self) -> Dict[str, Any]:
        """Obtiene el estado actual del sistema"""
        return {
            "pedidos_activos": len(self.pedidos_activos),
            "monitoreo_activo": self.monitoreo_activo,
            "esperando_confirmacion": self.esperando_confirmacion,
            "items_en_carrito": len(self.carrito.items),
            "metodos_pago_disponibles": list(self.metodos_pago.keys())
        }


# Alias para compatibilidad hacia atrás
DeliveryAgent = PideBot


def demo_delivery_agent():
    """Demostración del agente PideBot"""
    print("🤖 === DEMO: PideBot - Agente de Delivery Proactivo ===\n")
    
    # Callbacks para la demo
    def callback_notificar(mensaje):
        print(f"\n🔔 [NOTIFICACIÓN PROACTIVA] {mensaje}\n")
    
    def callback_preguntar(pregunta):
        return input(f"❓ {pregunta}: ")
    
    # Crear instancia del agente
    pidebot = PideBot(
        notificar_usuario_callback=callback_notificar,
        preguntar_usuario_callback=callback_preguntar
    )
    
    print("Ejemplo de conversación:")
    print("-" * 50)
    
    # Simular conversación
    ejemplos = [
        "Hola",
        "Quiero una hamburguesa doble con queso de Bembos",
        "Sí",  # Confirmación de pago
        "¿Dónde está mi pedido?"
    ]
    
    for i, ejemplo in enumerate(ejemplos, 1):
        print(f"\n👤 Usuario: {ejemplo}")
        respuesta = pidebot.procesar_solicitud(ejemplo)
        print(f"🤖 PideBot: {respuesta}")
        
        if i == 2:  # Después de confirmar pago
            print("\n⏰ [Simulando paso del tiempo - monitoreo automático...]")
            time.sleep(2)  # Simular tiempo
    
    # Mostrar estado del sistema
    estado = pidebot.obtener_estado_sistema()
    print(f"\n📊 Estado del sistema: {estado}")
    
    return pidebot


def demo_apis():
    """Demostración de las APIs del sistema"""
    print("\n🧪 === DEMO: APIs del Sistema ===\n")
    
    # Demo RestauranteDB
    print("1. 🏪 Base de Datos de Restaurantes:")
    db = RestauranteDB()
    productos = db.buscar_producto("cuarto pollo brasa", "Norky's")
    for producto in productos:
        print(f"   - {producto.nombre_producto} | {producto.restaurante_nombre} | S/ {producto.precio}")
    
    # Demo PagosSeguroAPI
    print("\n2. 💳 API de Pagos Seguros:")
    pagos = PagosSeguroAPI()
    resultado = pagos.iniciar_pago("visa_1234", 32.50)
    print(f"   - Resultado: {'✅ Exitoso' if resultado['exito'] else '❌ Fallido'}")
    if resultado["exito"]:
        print(f"   - Pedido ID: {resultado['pedido_id']}")
    
    # Demo MonitoreoAPI
    print("\n3. 📱 API de Monitoreo:")
    monitoreo = MonitoreoAPI()
    if resultado["exito"]:
        estado = monitoreo.consultar_estado_pedido(resultado["pedido_id"])
        print(f"   - Estado: {estado['estado']}")
        print(f"   - Timestamp: {estado['timestamp']}")


if __name__ == "__main__":
    # Ejecutar demos
    demo_apis()
    print("\n" + "="*60 + "\n")
    
    # Demo principal del agente
    agente = demo_delivery_agent()
    
    print("\n✅ Demo completada. PideBot está listo para uso!")
    print("💡 Para usar en producción, integra los callbacks con tu interfaz de usuario.")