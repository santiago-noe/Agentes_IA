"""
Agente de IA para diseño de habitaciones
Genera diseños personalizados basados en dimensiones, estilo y presupuesto
"""

import json
import math
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class FurnitureCatalog:
    """Catálogo de muebles y decoración"""
    
    def __init__(self):
        self.furniture_catalog = self._initialize_catalog()
    
    def _initialize_catalog(self) -> List[Dict[str, Any]]:
        """Inicializa el catálogo de muebles"""
        return [
            # Dormitorio - Moderno
            {
                'id': 'bed_modern_1',
                'name': 'Cama Platform King',
                'category': 'cama',
                'style': 'moderno',
                'price': 1200,
                'dimensions': {'width': 2.0, 'length': 2.2, 'height': 0.4},
                'description': 'Cama minimalista con cabecero bajo',
                'room_type': 'dormitorio'
            },
            {
                'id': 'nightstand_modern_1',
                'name': 'Mesa de Noche Suspendida',
                'category': 'mesa_noche',
                'style': 'moderno',
                'price': 180,
                'dimensions': {'width': 0.5, 'length': 0.3, 'height': 0.15},
                'description': 'Mesa flotante con cajón oculto',
                'room_type': 'dormitorio'
            },
            {
                'id': 'wardrobe_modern_1',
                'name': 'Closet Minimalista',
                'category': 'armario',
                'style': 'moderno',
                'price': 800,
                'dimensions': {'width': 2.5, 'length': 0.6, 'height': 2.4},
                'description': 'Armario con puertas corredizas',
                'room_type': 'dormitorio'
            },
            
            # Dormitorio - Clásico
            {
                'id': 'bed_classic_1',
                'name': 'Cama Colonial Tallada',
                'category': 'cama',
                'style': 'clasico',
                'price': 1800,
                'dimensions': {'width': 2.0, 'length': 2.2, 'height': 1.2},
                'description': 'Cama de madera maciza con cabecero tallado',
                'room_type': 'dormitorio'
            },
            {
                'id': 'nightstand_classic_1',
                'name': 'Cómoda Vintage',
                'category': 'mesa_noche',
                'style': 'clasico',
                'price': 320,
                'dimensions': {'width': 0.6, 'length': 0.4, 'height': 0.7},
                'description': 'Mesa de noche con tres cajones',
                'room_type': 'dormitorio'
            },
            
            # Sala de estar - Moderno
            {
                'id': 'sofa_modern_1',
                'name': 'Sofá Seccional L',
                'category': 'sofa',
                'style': 'moderno',
                'price': 1500,
                'dimensions': {'width': 2.8, 'length': 2.2, 'height': 0.8},
                'description': 'Sofá esquinero en tela gris',
                'room_type': 'sala'
            },
            {
                'id': 'coffee_table_modern_1',
                'name': 'Mesa Centro Cristal',
                'category': 'mesa_centro',
                'style': 'moderno',
                'price': 400,
                'dimensions': {'width': 1.2, 'length': 0.6, 'height': 0.4},
                'description': 'Mesa de cristal templado con base metálica',
                'room_type': 'sala'
            },
            {
                'id': 'tv_unit_modern_1',
                'name': 'Mueble TV Flotante',
                'category': 'mueble_tv',
                'style': 'moderno',
                'price': 600,
                'dimensions': {'width': 1.8, 'length': 0.4, 'height': 0.5},
                'description': 'Mueble suspendido con compartimientos',
                'room_type': 'sala'
            },
            
            # Comedor
            {
                'id': 'dining_table_modern_1',
                'name': 'Mesa Comedor Extensible',
                'category': 'mesa_comedor',
                'style': 'moderno',
                'price': 900,
                'dimensions': {'width': 1.6, 'length': 0.9, 'height': 0.75},
                'description': 'Mesa para 6-8 personas, extensible',
                'room_type': 'comedor'
            },
            {
                'id': 'dining_chair_modern_1',
                'name': 'Silla Comedor Tapizada',
                'category': 'silla',
                'style': 'moderno',
                'price': 120,
                'dimensions': {'width': 0.5, 'length': 0.5, 'height': 0.9},
                'description': 'Silla con respaldo alto, tapizado gris',
                'room_type': 'comedor'
            },
            
            # Oficina
            {
                'id': 'desk_modern_1',
                'name': 'Escritorio Ejecutivo',
                'category': 'escritorio',
                'style': 'moderno',
                'price': 700,
                'dimensions': {'width': 1.6, 'length': 0.8, 'height': 0.75},
                'description': 'Escritorio con cajones y cable management',
                'room_type': 'oficina'
            },
            {
                'id': 'office_chair_modern_1',
                'name': 'Silla Ergonómica',
                'category': 'silla_oficina',
                'style': 'moderno',
                'price': 450,
                'dimensions': {'width': 0.6, 'length': 0.6, 'height': 1.1},
                'description': 'Silla con soporte lumbar ajustable',
                'room_type': 'oficina'
            },
            
            # Decoración
            {
                'id': 'lamp_modern_1',
                'name': 'Lámpara de Pie LED',
                'category': 'iluminacion',
                'style': 'moderno',
                'price': 200,
                'dimensions': {'width': 0.3, 'length': 0.3, 'height': 1.6},
                'description': 'Lámpara LED regulable, diseño minimalista',
                'room_type': 'cualquiera'
            },
            {
                'id': 'plant_decor_1',
                'name': 'Maceta Grande con Planta',
                'category': 'decoracion',
                'style': 'cualquiera',
                'price': 80,
                'dimensions': {'width': 0.4, 'length': 0.4, 'height': 1.2},
                'description': 'Monstera en maceta de cerámica',
                'room_type': 'cualquiera'
            },
            {
                'id': 'artwork_modern_1',
                'name': 'Cuadro Abstracto Grande',
                'category': 'arte',
                'style': 'moderno',
                'price': 150,
                'dimensions': {'width': 1.0, 'length': 0.05, 'height': 0.8},
                'description': 'Arte abstracto enmarcado 100x80cm',
                'room_type': 'cualquiera'
            }
        ]
    
    def get_furniture_by_style(self, style: str) -> List[Dict[str, Any]]:
        """Obtiene muebles por estilo"""
        if style == 'cualquiera':
            return self.furniture_catalog
        return [item for item in self.furniture_catalog 
                if item['style'] == style or item['style'] == 'cualquiera']
    
    def get_furniture_by_room(self, room_type: str) -> List[Dict[str, Any]]:
        """Obtiene muebles por tipo de habitación"""
        return [item for item in self.furniture_catalog 
                if item['room_type'] == room_type or item['room_type'] == 'cualquiera']
    
    def get_furniture_by_budget(self, max_budget: float) -> List[Dict[str, Any]]:
        """Obtiene muebles dentro del presupuesto"""
        return [item for item in self.furniture_catalog if item['price'] <= max_budget]


class DesignVisualizer:
    """Generador de visualizaciones y layouts"""
    
    def __init__(self):
        self.canvas_size = (800, 600)
        self.scale = 100  # 1 metro = 100 píxeles
    
    def generate_room_layout(self, furniture_items: List[Dict], room_dimensions: Dict) -> Dict[str, Any]:
        """Genera diseño visual de la habitación"""
        layout = {
            'room': room_dimensions,
            'furniture': [],
            'walls': self._generate_walls(room_dimensions),
            'decorations': [],
            'total_area_used': 0,
            'area_efficiency': 0
        }
        
        # Posicionar muebles usando algoritmo simple
        positioned_items = []
        used_positions = []
        
        # Ordenar muebles por tamaño (más grandes primero)
        sorted_furniture = sorted(furniture_items, 
                                key=lambda x: x['dimensions']['width'] * x['dimensions']['length'], 
                                reverse=True)
        
        for item in sorted_furniture:
            position = self.find_optimal_position(item, room_dimensions, used_positions)
            if position:
                positioned_item = {
                    'id': item['id'],
                    'name': item['name'],
                    'category': item['category'],
                    'position': position,
                    'dimensions': item['dimensions'],
                    'rotation': 0,
                    'scale': 1.0
                }
                positioned_items.append(positioned_item)
                used_positions.append({
                    'x': position['x'],
                    'y': position['y'],
                    'width': item['dimensions']['width'],
                    'length': item['dimensions']['length']
                })
        
        layout['furniture'] = positioned_items
        layout['total_area_used'] = self._calculate_used_area(positioned_items)
        layout['area_efficiency'] = self._calculate_efficiency(layout, room_dimensions)
        
        return layout
    
    def find_optimal_position(self, furniture: Dict, room_dimensions: Dict, used_positions: List[Dict]) -> Optional[Dict]:
        """Encuentra la posición óptima para un mueble"""
        room_width = room_dimensions['width']
        room_length = room_dimensions['length']
        
        furniture_width = furniture['dimensions']['width']
        furniture_length = furniture['dimensions']['length']
        
        # Intentar diferentes posiciones con una grilla
        grid_size = 0.5  # Posiciones cada 50cm
        
        for x in self._frange(0.2, room_width - furniture_width - 0.2, grid_size):
            for y in self._frange(0.2, room_length - furniture_length - 0.2, grid_size):
                if not self._position_conflicts(x, y, furniture_width, furniture_length, used_positions):
                    return {'x': x, 'y': y}
        
        return None
    
    def _frange(self, start: float, stop: float, step: float):
        """Genera rango de flotantes"""
        while start < stop:
            yield start
            start += step
    
    def _position_conflicts(self, x: float, y: float, width: float, length: float, 
                          used_positions: List[Dict]) -> bool:
        """Verifica si una posición entra en conflicto con muebles existentes"""
        margin = 0.3  # Margen de 30cm entre muebles
        
        for used in used_positions:
            if (x < used['x'] + used['width'] + margin and
                x + width + margin > used['x'] and
                y < used['y'] + used['length'] + margin and
                y + length + margin > used['y']):
                return True
        return False
    
    def _generate_walls(self, room_dimensions: Dict) -> List[Dict]:
        """Genera información de paredes"""
        return [
            {'type': 'wall', 'start': (0, 0), 'end': (room_dimensions['width'], 0)},
            {'type': 'wall', 'start': (room_dimensions['width'], 0), 'end': (room_dimensions['width'], room_dimensions['length'])},
            {'type': 'wall', 'start': (room_dimensions['width'], room_dimensions['length']), 'end': (0, room_dimensions['length'])},
            {'type': 'wall', 'start': (0, room_dimensions['length']), 'end': (0, 0)}
        ]
    
    def _calculate_used_area(self, positioned_items: List[Dict]) -> float:
        """Calcula área total utilizada por los muebles"""
        total_area = 0
        for item in positioned_items:
            dims = item['dimensions']
            total_area += dims['width'] * dims['length']
        return total_area
    
    def _calculate_efficiency(self, layout: Dict, room_dimensions: Dict) -> float:
        """Calcula eficiencia del uso del espacio"""
        room_area = room_dimensions['width'] * room_dimensions['length']
        used_area = layout['total_area_used']
        return (used_area / room_area) * 100 if room_area > 0 else 0
    
    def generate_3d_visualization(self, layout: Dict) -> Dict[str, Any]:
        """Genera datos para visualización 3D simplificada"""
        visualization = {
            'scene_type': '3d_room',
            'camera_position': {'x': -2, 'y': 3, 'z': 2},
            'lighting': {
                'ambient': 0.4,
                'directional': {'intensity': 0.8, 'position': {'x': 5, 'y': 10, 'z': 5}}
            },
            'objects': []
        }
        
        # Agregar suelo
        visualization['objects'].append({
            'type': 'floor',
            'dimensions': layout['room'],
            'material': 'wood_floor',
            'color': '#8B4513'
        })
        
        # Agregar muebles
        for furniture in layout['furniture']:
            obj = {
                'type': 'furniture',
                'category': furniture['category'],
                'position': furniture['position'],
                'dimensions': furniture['dimensions'],
                'rotation': furniture['rotation'],
                'material': self._get_material_for_category(furniture['category']),
                'color': self._get_color_for_category(furniture['category'])
            }
            visualization['objects'].append(obj)
        
        return visualization
    
    def _get_material_for_category(self, category: str) -> str:
        """Obtiene material basado en categoría"""
        material_map = {
            'cama': 'fabric',
            'sofa': 'fabric',
            'mesa_centro': 'glass',
            'escritorio': 'wood',
            'silla': 'plastic',
            'armario': 'wood',
            'mueble_tv': 'wood',
            'mesa_comedor': 'wood',
            'iluminacion': 'metal'
        }
        return material_map.get(category, 'wood')
    
    def _get_color_for_category(self, category: str) -> str:
        """Obtiene color basado en categoría"""
        color_map = {
            'cama': '#E6E6FA',
            'sofa': '#708090',
            'mesa_centro': '#F5F5F5',
            'escritorio': '#8B4513',
            'silla': '#2F4F4F',
            'armario': '#D2B48C',
            'mueble_tv': '#696969',
            'mesa_comedor': '#A0522D',
            'iluminacion': '#FFD700'
        }
        return color_map.get(category, '#8B4513')


class RoomDesignAgent:
    """Agente principal para diseño de habitaciones"""
    
    def __init__(self):
        self.furniture_catalog = FurnitureCatalog()
        self.visualizer = DesignVisualizer()
        self.room_templates = self._load_room_templates()
        self.design_history = []
    
    def _load_room_templates(self) -> Dict[str, Any]:
        """Carga plantillas predefinidas de habitaciones"""
        return {
            'dormitorio_pequeno': {
                'required_furniture': ['cama', 'mesa_noche', 'armario'],
                'optional_furniture': ['silla', 'iluminacion', 'decoracion'],
                'min_dimensions': {'width': 3.0, 'length': 3.0}
            },
            'dormitorio_grande': {
                'required_furniture': ['cama', 'mesa_noche', 'armario', 'silla'],
                'optional_furniture': ['escritorio', 'iluminacion', 'decoracion', 'arte'],
                'min_dimensions': {'width': 4.0, 'length': 4.0}
            },
            'sala_estar': {
                'required_furniture': ['sofa', 'mesa_centro'],
                'optional_furniture': ['mueble_tv', 'iluminacion', 'decoracion', 'arte'],
                'min_dimensions': {'width': 3.5, 'length': 3.5}
            },
            'comedor': {
                'required_furniture': ['mesa_comedor', 'silla'],
                'optional_furniture': ['iluminacion', 'decoracion', 'arte'],
                'min_dimensions': {'width': 3.0, 'length': 3.0}
            },
            'oficina': {
                'required_furniture': ['escritorio', 'silla_oficina'],
                'optional_furniture': ['armario', 'iluminacion', 'decoracion'],
                'min_dimensions': {'width': 2.5, 'length': 2.5}
            }
        }
    
    def generate_design(self, room_type: str, room_dimensions: str, style_preference: str, 
                       budget: float, special_requirements: List[str] = None) -> Dict[str, Any]:
        """Genera diseño de habitación basado en parámetros"""
        
        # Parsear dimensiones
        dimensions = self._parse_dimensions(room_dimensions)
        if not dimensions:
            return {'error': 'Formato de dimensiones inválido. Use formato como "4x5m" o "4.5x3.2m"'}
        
        # Validar tipo de habitación
        if room_type not in self.room_templates:
            return {'error': f'Tipo de habitación no soportado. Tipos disponibles: {list(self.room_templates.keys())}'}
        
        # Verificar dimensiones mínimas
        template = self.room_templates[room_type]
        if (dimensions['width'] < template['min_dimensions']['width'] or 
            dimensions['length'] < template['min_dimensions']['length']):
            return {'error': f'Dimensiones muy pequeñas para {room_type}. Mínimo: {template["min_dimensions"]}'}
        
        # Filtrar muebles por estilo y presupuesto
        available_furniture = self.filter_furniture(style_preference, budget, room_type)
        
        if not available_furniture:
            return {'error': 'No hay muebles disponibles para el estilo y presupuesto especificados'}
        
        # Seleccionar muebles para el diseño
        selected_furniture = self.select_furniture(available_furniture, template, budget, special_requirements)
        
        # Generar layout
        layout = self.visualizer.generate_room_layout(selected_furniture, dimensions)
        
        # Generar visualización 3D
        visualization = self.visualizer.generate_3d_visualization(layout)
        
        # Crear lista de compras
        shopping_list = self.generate_shopping_list(selected_furniture)
        
        # Calcular costo total
        total_cost = self.calculate_total_cost(selected_furniture)
        
        # Generar recomendaciones adicionales
        recommendations = self.generate_recommendations(layout, dimensions, budget - total_cost)
        
        design_result = {
            'room_type': room_type,
            'dimensions': dimensions,
            'style': style_preference,
            'layout': layout,
            'visualization': visualization,
            'shopping_list': shopping_list,
            'total_cost': total_cost,
            'budget_remaining': budget - total_cost,
            'area_efficiency': layout['area_efficiency'],
            'recommendations': recommendations,
            'design_id': f"DESIGN-{len(self.design_history) + 1:04d}"
        }
        
        # Guardar en historial
        self.design_history.append({
            'design': design_result,
            'timestamp': datetime.now()
        })
        
        return design_result
    
    def _parse_dimensions(self, dimensions_str: str) -> Optional[Dict[str, float]]:
        """Parsea string de dimensiones como '4x5m' o '4.5x3.2m'"""
        import re
        
        # Remover 'm' y espacios
        clean_str = dimensions_str.lower().replace('m', '').replace(' ', '')
        
        # Buscar patrón número x número
        pattern = r'(\d+\.?\d*)x(\d+\.?\d*)'
        match = re.match(pattern, clean_str)
        
        if match:
            width = float(match.group(1))
            length = float(match.group(2))
            return {'width': width, 'length': length}
        
        return None
    
    def filter_furniture(self, style: str, budget: float, room_type: str) -> List[Dict[str, Any]]:
        """Filtra muebles por estilo, presupuesto y tipo de habitación"""
        # Obtener muebles por estilo
        style_furniture = self.furniture_catalog.get_furniture_by_style(style)
        
        # Filtrar por habitación
        room_furniture = [f for f in style_furniture 
                         if f['room_type'] == room_type or f['room_type'] == 'cualquiera']
        
        # Filtrar por presupuesto (muebles individuales que no excedan 50% del presupuesto)
        max_item_price = budget * 0.5
        budget_furniture = [f for f in room_furniture if f['price'] <= max_item_price]
        
        return budget_furniture
    
    def select_furniture(self, available_furniture: List[Dict], template: Dict, 
                        budget: float, special_requirements: List[str] = None) -> List[Dict[str, Any]]:
        """Selecciona muebles optimales para el diseño"""
        selected = []
        remaining_budget = budget
        
        # Agrupar muebles por categoría
        furniture_by_category = {}
        for item in available_furniture:
            category = item['category']
            if category not in furniture_by_category:
                furniture_by_category[category] = []
            furniture_by_category[category].append(item)
        
        # Seleccionar muebles requeridos primero
        for category in template['required_furniture']:
            if category in furniture_by_category:
                # Ordenar por precio (más barato primero para muebles requeridos)
                options = sorted(furniture_by_category[category], key=lambda x: x['price'])
                for option in options:
                    if option['price'] <= remaining_budget:
                        selected.append(option)
                        remaining_budget -= option['price']
                        break
        
        # Seleccionar sillas múltiples para comedor
        if 'silla' in template['required_furniture']:
            silla_category = 'silla'
            if silla_category in furniture_by_category:
                chair_options = sorted(furniture_by_category[silla_category], key=lambda x: x['price'])
                for chair in chair_options:
                    chairs_needed = 4  # Por defecto 4 sillas
                    total_chair_cost = chair['price'] * chairs_needed
                    if total_chair_cost <= remaining_budget:
                        for _ in range(chairs_needed):
                            selected.append(chair.copy())
                        remaining_budget -= total_chair_cost
                        break
        
        # Agregar muebles opcionales si queda presupuesto
        for category in template['optional_furniture']:
            if remaining_budget > 200 and category in furniture_by_category:  # Mínimo $200 para opcionales
                options = sorted(furniture_by_category[category], key=lambda x: x['price'], reverse=True)
                for option in options:
                    if option['price'] <= remaining_budget:
                        selected.append(option)
                        remaining_budget -= option['price']
                        break
        
        return selected
    
    def generate_shopping_list(self, furniture_items: List[Dict]) -> List[Dict[str, Any]]:
        """Genera lista de compras detallada"""
        shopping_list = []
        
        # Contar cantidades de cada mueble
        item_counts = {}
        for item in furniture_items:
            key = item['id']
            if key in item_counts:
                item_counts[key]['quantity'] += 1
            else:
                item_counts[key] = {
                    'name': item['name'],
                    'category': item['category'],
                    'price': item['price'],
                    'quantity': 1,
                    'description': item['description'],
                    'dimensions': item['dimensions']
                }
        
        # Convertir a lista ordenada por categoría
        for item_data in item_counts.values():
            total_price = item_data['price'] * item_data['quantity']
            shopping_list.append({
                'name': item_data['name'],
                'category': item_data['category'],
                'quantity': item_data['quantity'],
                'unit_price': item_data['price'],
                'total_price': total_price,
                'description': item_data['description'],
                'dimensions': item_data['dimensions']
            })
        
        # Ordenar por categoría y precio
        shopping_list.sort(key=lambda x: (x['category'], -x['total_price']))
        
        return shopping_list
    
    def calculate_total_cost(self, furniture_items: List[Dict]) -> float:
        """Calcula costo total de los muebles"""
        return sum(item['price'] for item in furniture_items)
    
    def generate_recommendations(self, layout: Dict, room_dimensions: Dict, 
                               remaining_budget: float) -> List[str]:
        """Genera recomendaciones adicionales"""
        recommendations = []
        
        # Recomendaciones basadas en eficiencia del espacio
        efficiency = layout['area_efficiency']
        if efficiency < 15:
            recommendations.append("El espacio está subutilizado. Considera agregar más muebles o decoración.")
        elif efficiency > 60:
            recommendations.append("El espacio está muy lleno. Considera remover algunos elementos.")
        else:
            recommendations.append("El uso del espacio es óptimo.")
        
        # Recomendaciones basadas en presupuesto restante
        if remaining_budget > 500:
            recommendations.append(f"Tienes ${remaining_budget:.0f} restantes. Considera agregar iluminación adicional o arte.")
        elif remaining_budget > 200:
            recommendations.append(f"Con ${remaining_budget:.0f} restantes puedes agregar plantas o accesorios decorativos.")
        elif remaining_budget < 0:
            recommendations.append(f"Te has excedido por ${-remaining_budget:.0f}. Considera opciones más económicas.")
        
        # Recomendaciones de diseño
        room_area = room_dimensions['width'] * room_dimensions['length']
        if room_area > 20:
            recommendations.append("Para habitaciones grandes, considera crear zonas definidas con alfombras.")
        elif room_area < 10:
            recommendations.append("Para espacios pequeños, usa muebles multifuncionales y colores claros.")
        
        # Recomendaciones por número de muebles
        furniture_count = len(layout['furniture'])
        if furniture_count < 3:
            recommendations.append("Considera agregar más elementos para crear un ambiente más acogedor.")
        
        return recommendations
    
    def get_design_suggestions(self, room_type: str, budget: float) -> Dict[str, Any]:
        """Obtiene sugerencias de diseño para un tipo de habitación"""
        if room_type not in self.room_templates:
            return {'error': 'Tipo de habitación no válido'}
        
        template = self.room_templates[room_type]
        
        # Calcular costos estimados por estilo
        style_estimates = {}
        styles = ['moderno', 'clasico']
        
        for style in styles:
            style_furniture = self.furniture_catalog.get_furniture_by_style(style)
            room_furniture = [f for f in style_furniture if f['room_type'] == room_type or f['room_type'] == 'cualquiera']
            
            # Estimar costo mínimo
            min_cost = 0
            for category in template['required_furniture']:
                category_items = [f for f in room_furniture if f['category'] == category]
                if category_items:
                    min_price = min(item['price'] for item in category_items)
                    if category == 'silla':
                        min_cost += min_price * 4  # 4 sillas para comedor
                    else:
                        min_cost += min_price
            
            style_estimates[style] = {
                'min_cost': min_cost,
                'within_budget': min_cost <= budget,
                'furniture_options': len(room_furniture)
            }
        
        return {
            'room_type': room_type,
            'budget': budget,
            'style_estimates': style_estimates,
            'recommended_dimensions': template['min_dimensions'],
            'required_furniture': template['required_furniture'],
            'optional_furniture': template['optional_furniture']
        }


# Función de demostración
def demo_room_design_agent():
    """Demuestra la funcionalidad del agente de diseño"""
    agent = RoomDesignAgent()
    
    print("=== DEMO: AGENTE DE DISEÑO DE HABITACIONES ===\n")
    
    # Caso 1: Diseño de dormitorio moderno
    print("Diseño 1: Dormitorio moderno 4x5m, presupuesto $3000")
    design1 = agent.generate_design(
        room_type="dormitorio_grande",
        room_dimensions="4x5m",
        style_preference="moderno",
        budget=3000
    )
    
    if 'error' not in design1:
        print(f"✓ Diseño creado exitosamente (ID: {design1['design_id']})")
        print(f"  - Costo total: ${design1['total_cost']:.0f}")
        print(f"  - Presupuesto restante: ${design1['budget_remaining']:.0f}")
        print(f"  - Eficiencia del espacio: {design1['area_efficiency']:.1f}%")
        print(f"  - Muebles incluidos: {len(design1['shopping_list'])} items")
        print("  - Lista de compras:")
        for item in design1['shopping_list'][:3]:  # Mostrar primeros 3
            print(f"    * {item['quantity']}x {item['name']} - ${item['total_price']:.0f}")
        if len(design1['shopping_list']) > 3:
            print(f"    ... y {len(design1['shopping_list']) - 3} items más")
    else:
        print(f"✗ Error: {design1['error']}")
    print()
    
    # Caso 2: Oficina en casa
    print("Diseño 2: Oficina 3x3m, estilo clásico, presupuesto $1500")
    design2 = agent.generate_design(
        room_type="oficina",
        room_dimensions="3x3m",
        style_preference="clasico",
        budget=1500
    )
    
    if 'error' not in design2:
        print(f"✓ Diseño creado exitosamente (ID: {design2['design_id']})")
        print(f"  - Costo total: ${design2['total_cost']:.0f}")
        print(f"  - Eficiencia del espacio: {design2['area_efficiency']:.1f}%")
        print("  - Recomendaciones:")
        for rec in design2['recommendations'][:2]:
            print(f"    * {rec}")
    else:
        print(f"✗ Error: {design2['error']}")
    print()
    
    # Caso 3: Sugerencias para sala de estar
    print("Sugerencias para sala de estar con presupuesto $2000:")
    suggestions = agent.get_design_suggestions("sala_estar", 2000)
    
    if 'error' not in suggestions:
        print("✓ Análisis de estilos:")
        for style, data in suggestions['style_estimates'].items():
            status = "✓" if data['within_budget'] else "✗"
            print(f"  {status} {style.capitalize()}: Desde ${data['min_cost']:.0f} ({data['furniture_options']} opciones)")
        print(f"  - Dimensiones recomendadas: {suggestions['recommended_dimensions']}")
        print(f"  - Muebles requeridos: {', '.join(suggestions['required_furniture'])}")
    else:
        print(f"✗ Error: {suggestions['error']}")
    print()


if __name__ == "__main__":
    demo_room_design_agent()