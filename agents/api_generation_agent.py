"""
Agente de IA para generación automática de APIs
Genera código REST API basado en especificaciones y modelos de datos
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class APIEndpoint:
    """Representa un endpoint de API"""
    name: str
    method: str
    route: str
    description: str
    parameters: List[Dict]
    response_model: str
    request_model: Optional[str] = None
    auth_required: bool = False
    rate_limit: Optional[int] = None


@dataclass
class DataModel:
    """Representa un modelo de datos"""
    name: str
    fields: List[Dict]
    relationships: List[Dict]
    validations: List[Dict]
    description: str


class CodeTemplateManager:
    """Gestor de plantillas de código para diferentes frameworks"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Carga plantillas de código para diferentes frameworks"""
        return {
            'fastapi': {
                'app_main': '''from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from . import models, schemas, crud
from .database import SessionLocal, engine

# Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{api_title}",
    description="{api_description}",
    version="{api_version}"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency para obtener DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

{endpoints}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
                
                'model_template': '''from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class {model_name}(Base):
    __tablename__ = "{table_name}"
    
{fields}
{relationships}

    def __repr__(self):
        return f"<{model_name}(id={{self.id}})>"
''',
                
                'schema_template': '''from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class {model_name}Base(BaseModel):
{fields}

class {model_name}Create({model_name}Base):
    pass

class {model_name}Update(BaseModel):
{optional_fields}

class {model_name}(BaseModel):
    id: int
{fields}
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class {model_name}List(BaseModel):
    items: List[{model_name}]
    total: int
    page: int
    size: int
''',
                
                'crud_template': '''from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from . import models, schemas

class {model_name}CRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, obj_in: schemas.{model_name}Create) -> models.{model_name}:
        db_obj = models.{model_name}(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get(self, id: int) -> Optional[models.{model_name}]:
        return self.db.query(models.{model_name}).filter(models.{model_name}.id == id).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[models.{model_name}]:
        return self.db.query(models.{model_name}).offset(skip).limit(limit).all()

    def update(self, db_obj: models.{model_name}, obj_in: schemas.{model_name}Update) -> models.{model_name}:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        obj = self.db.query(models.{model_name}).filter(models.{model_name}.id == id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def search(self, query: str) -> List[models.{model_name}]:
        # Implementar búsqueda básica
        return self.db.query(models.{model_name}).filter(
            or_({search_fields})
        ).all()
''',
                
                'endpoint_template': '''
@app.{method}("{route}", response_model={response_model})
async def {function_name}({parameters}, db: Session = Depends(get_db)):
    """{description}"""
    try:
{body}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
''',
                
                'database_template': '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL de la base de datos
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Crear engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={{"check_same_thread": False}} if "sqlite" in SQLALCHEMY_DATABASE_URL else {{}}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()
'''
            },
            
            'flask': {
                'app_main': '''from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

{models}

{endpoints}

@app.errorhandler(404)
def not_found(error):
    return jsonify({{'error': 'Resource not found'}}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({{'error': 'Internal server error'}}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
''',
                
                'model_template': '''class {model_name}(db.Model):
    __tablename__ = '{table_name}'
    
{fields}

    def to_dict(self):
        return {{
{to_dict_fields}
        }}

    def __repr__(self):
        return f'<{model_name} {{self.id}}>'
''',
                
                'endpoint_template': '''
@app.route('{route}', methods=['{method}'])
def {function_name}():
    """{description}"""
    try:
{body}
    except Exception as e:
        return jsonify({{'error': str(e)}}), 500
'''
            }
        }
    
    def get_template(self, framework: str, template_type: str) -> str:
        """Obtiene una plantilla específica"""
        return self.templates.get(framework, {}).get(template_type, "")


class APISpecificationParser:
    """Parser para especificaciones de API"""
    
    def __init__(self):
        self.supported_formats = ['json', 'yaml', 'openapi']
    
    def parse_specification(self, spec_text: str, format_type: str = 'json') -> Dict[str, Any]:
        """Parsea especificación de API"""
        if format_type == 'json':
            return self._parse_json_spec(spec_text)
        elif format_type == 'natural':
            return self._parse_natural_language(spec_text)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")
    
    def _parse_json_spec(self, spec_text: str) -> Dict[str, Any]:
        """Parsea especificación JSON"""
        try:
            spec = json.loads(spec_text)
            return self._normalize_specification(spec)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido: {e}")
    
    def _parse_natural_language(self, description: str) -> Dict[str, Any]:
        """Parsea descripción en lenguaje natural"""
        spec = {
            'api_info': {},
            'models': [],
            'endpoints': []
        }
        
        lines = description.strip().split('\n')
        current_section = None
        current_model = None
        current_endpoint = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detectar secciones
            if line.lower().startswith('api:') or line.lower().startswith('aplicación:'):
                current_section = 'api_info'
                spec['api_info']['title'] = line.split(':', 1)[1].strip()
                continue
            elif line.lower().startswith('modelo:') or line.lower().startswith('entidad:'):
                current_section = 'model'
                model_name = line.split(':', 1)[1].strip()
                current_model = {
                    'name': model_name,
                    'fields': [],
                    'relationships': [],
                    'description': ''
                }
                spec['models'].append(current_model)
                continue
            elif line.lower().startswith('endpoint:') or line.lower().startswith('ruta:'):
                current_section = 'endpoint'
                endpoint_desc = line.split(':', 1)[1].strip()
                current_endpoint = self._parse_endpoint_description(endpoint_desc)
                spec['endpoints'].append(current_endpoint)
                continue
            
            # Procesar contenido según sección
            if current_section == 'model' and current_model:
                self._parse_model_field(line, current_model)
            elif current_section == 'endpoint' and current_endpoint:
                self._parse_endpoint_detail(line, current_endpoint)
        
        return self._normalize_specification(spec)
    
    def _parse_endpoint_description(self, description: str) -> Dict[str, Any]:
        """Parsea descripción de endpoint"""
        # Buscar método HTTP y ruta
        method_patterns = {
            'GET': r'\b(get|obtener|listar|mostrar)\b',
            'POST': r'\b(post|crear|agregar|nuevo)\b',
            'PUT': r'\b(put|actualizar|modificar|editar)\b',
            'DELETE': r'\b(delete|eliminar|borrar)\b'
        }
        
        method = 'GET'  # Por defecto
        for http_method, pattern in method_patterns.items():
            if re.search(pattern, description.lower()):
                method = http_method
                break
        
        # Extraer entidad/recurso
        entity_match = re.search(r'\b(usuario|producto|pedido|cliente|orden)\w*', description.lower())
        entity = entity_match.group(0) if entity_match else 'resource'
        
        # Generar ruta
        if method == 'GET' and 'listar' in description.lower():
            route = f"/{entity}s"
        elif method == 'POST':
            route = f"/{entity}s"
        elif method in ['PUT', 'DELETE']:
            route = f"/{entity}s/{{id}}"
        else:
            route = f"/{entity}s/{{id}}"
        
        return {
            'name': f"{method.lower()}_{entity}",
            'method': method.lower(),
            'route': route,
            'description': description,
            'parameters': [],
            'response_model': f"{entity.capitalize()}Response"
        }
    
    def _parse_model_field(self, line: str, model: Dict[str, Any]):
        """Parsea campo de modelo"""
        # Formato: "- campo: tipo [opciones]"
        if line.startswith('-'):
            field_desc = line[1:].strip()
            if ':' in field_desc:
                field_name, field_type_desc = field_desc.split(':', 1)
                field_name = field_name.strip()
                field_type_desc = field_type_desc.strip()
                
                # Extraer tipo
                field_type = self._extract_field_type(field_type_desc)
                
                # Extraer opciones
                options = self._extract_field_options(field_type_desc)
                
                field = {
                    'name': field_name,
                    'type': field_type,
                    'required': options.get('required', True),
                    'unique': options.get('unique', False),
                    'description': options.get('description', '')
                }
                
                model['fields'].append(field)
    
    def _extract_field_type(self, type_desc: str) -> str:
        """Extrae tipo de campo de la descripción"""
        type_desc_lower = type_desc.lower()
        
        type_mapping = {
            'string': ['string', 'str', 'texto', 'cadena'],
            'integer': ['int', 'integer', 'entero', 'número'],
            'float': ['float', 'decimal', 'real'],
            'boolean': ['bool', 'boolean', 'booleano'],
            'datetime': ['datetime', 'fecha', 'timestamp'],
            'email': ['email', 'correo'],
            'phone': ['phone', 'teléfono', 'telefono']
        }
        
        for field_type, keywords in type_mapping.items():
            if any(keyword in type_desc_lower for keyword in keywords):
                return field_type
        
        return 'string'  # Por defecto
    
    def _extract_field_options(self, type_desc: str) -> Dict[str, Any]:
        """Extrae opciones de campo"""
        options = {}
        
        if 'obligatorio' in type_desc.lower() or 'required' in type_desc.lower():
            options['required'] = True
        elif 'opcional' in type_desc.lower() or 'optional' in type_desc.lower():
            options['required'] = False
        
        if 'único' in type_desc.lower() or 'unique' in type_desc.lower():
            options['unique'] = True
        
        return options
    
    def _parse_endpoint_detail(self, line: str, endpoint: Dict[str, Any]):
        """Parsea detalles adicionales del endpoint"""
        if line.startswith('-'):
            detail = line[1:].strip().lower()
            if 'parámetro' in detail or 'parameter' in detail:
                # Extraer parámetro
                param_name = re.search(r'(\w+)', detail)
                if param_name:
                    endpoint['parameters'].append({
                        'name': param_name.group(1),
                        'type': 'string',
                        'required': True
                    })
    
    def _normalize_specification(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza la especificación a formato estándar"""
        normalized = {
            'api_info': {
                'title': spec.get('api_info', {}).get('title', 'Generated API'),
                'description': spec.get('api_info', {}).get('description', 'Auto-generated REST API'),
                'version': spec.get('api_info', {}).get('version', '1.0.0')
            },
            'models': [],
            'endpoints': []
        }
        
        # Normalizar modelos
        for model in spec.get('models', []):
            normalized_model = DataModel(
                name=model.get('name', ''),
                fields=model.get('fields', []),
                relationships=model.get('relationships', []),
                validations=model.get('validations', []),
                description=model.get('description', '')
            )
            normalized['models'].append(normalized_model)
        
        # Normalizar endpoints
        for endpoint in spec.get('endpoints', []):
            normalized_endpoint = APIEndpoint(
                name=endpoint.get('name', ''),
                method=endpoint.get('method', 'get'),
                route=endpoint.get('route', '/'),
                description=endpoint.get('description', ''),
                parameters=endpoint.get('parameters', []),
                response_model=endpoint.get('response_model', 'dict'),
                request_model=endpoint.get('request_model'),
                auth_required=endpoint.get('auth_required', False)
            )
            normalized['endpoints'].append(normalized_endpoint)
        
        return normalized


class APIGenerationAgent:
    """Agente principal para generación de APIs"""
    
    def __init__(self):
        self.template_manager = CodeTemplateManager()
        self.spec_parser = APISpecificationParser()
        self.generation_history = []
    
    def generate_api(self, specification: str, framework: str = 'fastapi', 
                    format_type: str = 'natural') -> Dict[str, Any]:
        """Genera API completa basada en especificaciones"""
        
        # Validar framework
        if framework not in self.template_manager.templates:
            return {'error': f'Framework no soportado: {framework}. Opciones: {list(self.template_manager.templates.keys())}'}
        
        try:
            # Parsear especificación
            parsed_spec = self.spec_parser.parse_specification(specification, format_type)
            
            # Generar código
            generated_code = self._generate_code_structure(parsed_spec, framework)
            
            # Generar tests
            tests = self._generate_tests(parsed_spec, framework)
            
            # Generar documentación
            documentation = self._generate_documentation(parsed_spec)
            
            # Crear resultado
            result = {
                'api_info': parsed_spec['api_info'],
                'framework': framework,
                'generated_code': generated_code,
                'tests': tests,
                'documentation': documentation,
                'models_count': len(parsed_spec['models']),
                'endpoints_count': len(parsed_spec['endpoints']),
                'generation_id': f"API-{len(self.generation_history) + 1:04d}",
                'generated_at': datetime.now().isoformat()
            }
            
            # Guardar en historial
            self.generation_history.append(result)
            
            return result
            
        except Exception as e:
            return {'error': f'Error en generación: {str(e)}'}
    
    def _generate_code_structure(self, spec: Dict[str, Any], framework: str) -> Dict[str, str]:
        """Genera estructura completa de código"""
        code_structure = {}
        
        if framework == 'fastapi':
            # Generar modelos SQLAlchemy
            code_structure['models.py'] = self._generate_models(spec['models'], framework)
            
            # Generar schemas Pydantic
            code_structure['schemas.py'] = self._generate_schemas(spec['models'], framework)
            
            # Generar CRUD operations
            code_structure['crud.py'] = self._generate_crud(spec['models'], framework)
            
            # Generar configuración de base de datos
            code_structure['database.py'] = self.template_manager.get_template(framework, 'database_template')
            
            # Generar endpoints
            endpoints_code = self._generate_endpoints(spec['endpoints'], framework)
            
            # Generar main app
            code_structure['main.py'] = self.template_manager.get_template(framework, 'app_main').format(
                api_title=spec['api_info']['title'],
                api_description=spec['api_info']['description'],
                api_version=spec['api_info']['version'],
                endpoints=endpoints_code
            )
            
        elif framework == 'flask':
            # Generar todo en un archivo para Flask
            models_code = self._generate_models(spec['models'], framework)
            endpoints_code = self._generate_endpoints(spec['endpoints'], framework)
            
            code_structure['app.py'] = self.template_manager.get_template(framework, 'app_main').format(
                models=models_code,
                endpoints=endpoints_code
            )
        
        # Generar requirements.txt
        code_structure['requirements.txt'] = self._generate_requirements(framework)
        
        # Generar README.md
        code_structure['README.md'] = self._generate_readme(spec, framework)
        
        return code_structure
    
    def _generate_models(self, models: List[DataModel], framework: str) -> str:
        """Genera código de modelos"""
        models_code = []
        
        for model in models:
            if framework == 'fastapi':
                fields_code = self._generate_sqlalchemy_fields(model.fields)
                relationships_code = self._generate_sqlalchemy_relationships(model.relationships)
                
                model_code = self.template_manager.get_template(framework, 'model_template').format(
                    model_name=model.name,
                    table_name=model.name.lower(),
                    fields=fields_code,
                    relationships=relationships_code
                )
                
            elif framework == 'flask':
                fields_code = self._generate_flask_fields(model.fields)
                to_dict_fields = self._generate_to_dict_fields(model.fields)
                
                model_code = self.template_manager.get_template(framework, 'model_template').format(
                    model_name=model.name,
                    table_name=model.name.lower(),
                    fields=fields_code,
                    to_dict_fields=to_dict_fields
                )
            
            models_code.append(model_code)
        
        return '\n\n'.join(models_code)
    
    def _generate_sqlalchemy_fields(self, fields: List[Dict]) -> str:
        """Genera campos SQLAlchemy"""
        field_lines = []
        field_lines.append("    id = Column(Integer, primary_key=True, index=True)")
        
        for field in fields:
            field_type = self._get_sqlalchemy_type(field['type'])
            constraints = []
            
            if field.get('unique'):
                constraints.append('unique=True')
            if not field.get('required', True):
                constraints.append('nullable=True')
            
            constraints_str = ', '.join(constraints)
            if constraints_str:
                constraints_str = ', ' + constraints_str
            
            field_line = f"    {field['name']} = Column({field_type}{constraints_str})"
            field_lines.append(field_line)
        
        field_lines.append("    created_at = Column(DateTime, default=datetime.utcnow)")
        field_lines.append("    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)")
        
        return '\n'.join(field_lines)
    
    def _generate_flask_fields(self, fields: List[Dict]) -> str:
        """Genera campos para Flask-SQLAlchemy"""
        field_lines = []
        field_lines.append("    id = db.Column(db.Integer, primary_key=True)")
        
        for field in fields:
            field_type = self._get_flask_sqlalchemy_type(field['type'])
            constraints = []
            
            if field.get('unique'):
                constraints.append('unique=True')
            if not field.get('required', True):
                constraints.append('nullable=True')
            
            constraints_str = ', '.join(constraints)
            if constraints_str:
                constraints_str = ', ' + constraints_str
            
            field_line = f"    {field['name']} = db.Column({field_type}{constraints_str})"
            field_lines.append(field_line)
        
        field_lines.append("    created_at = db.Column(db.DateTime, default=datetime.utcnow)")
        
        return '\n'.join(field_lines)
    
    def _get_sqlalchemy_type(self, field_type: str) -> str:
        """Mapea tipos a SQLAlchemy"""
        type_map = {
            'string': 'String(255)',
            'integer': 'Integer',
            'float': 'Float',
            'boolean': 'Boolean',
            'datetime': 'DateTime',
            'email': 'String(255)',
            'phone': 'String(20)'
        }
        return type_map.get(field_type, 'String(255)')
    
    def _get_flask_sqlalchemy_type(self, field_type: str) -> str:
        """Mapea tipos a Flask-SQLAlchemy"""
        type_map = {
            'string': 'db.String(255)',
            'integer': 'db.Integer',
            'float': 'db.Float',
            'boolean': 'db.Boolean',
            'datetime': 'db.DateTime',
            'email': 'db.String(255)',
            'phone': 'db.String(20)'
        }
        return type_map.get(field_type, 'db.String(255)')
    
    def _generate_schemas(self, models: List[DataModel], framework: str) -> str:
        """Genera schemas Pydantic"""
        if framework != 'fastapi':
            return ""
        
        schemas_code = []
        
        for model in models:
            fields_code = self._generate_pydantic_fields(model.fields)
            optional_fields_code = self._generate_pydantic_optional_fields(model.fields)
            
            schema_code = self.template_manager.get_template(framework, 'schema_template').format(
                model_name=model.name,
                fields=fields_code,
                optional_fields=optional_fields_code
            )
            schemas_code.append(schema_code)
        
        return '\n\n'.join(schemas_code)
    
    def _generate_pydantic_fields(self, fields: List[Dict]) -> str:
        """Genera campos Pydantic"""
        field_lines = []
        
        for field in fields:
            field_type = self._get_pydantic_type(field['type'])
            
            if not field.get('required', True):
                field_type = f"Optional[{field_type}] = None"
            
            description = field.get('description', '')
            if description:
                field_line = f"    {field['name']}: {field_type} = Field(..., description=\"{description}\")"
            else:
                field_line = f"    {field['name']}: {field_type}"
            
            field_lines.append(field_line)
        
        return '\n'.join(field_lines) if field_lines else "    pass"
    
    def _generate_pydantic_optional_fields(self, fields: List[Dict]) -> str:
        """Genera campos opcionales para updates"""
        field_lines = []
        
        for field in fields:
            field_type = self._get_pydantic_type(field['type'])
            field_line = f"    {field['name']}: Optional[{field_type}] = None"
            field_lines.append(field_line)
        
        return '\n'.join(field_lines) if field_lines else "    pass"
    
    def _get_pydantic_type(self, field_type: str) -> str:
        """Mapea tipos a Pydantic"""
        type_map = {
            'string': 'str',
            'integer': 'int',
            'float': 'float',
            'boolean': 'bool',
            'datetime': 'datetime',
            'email': 'str',
            'phone': 'str'
        }
        return type_map.get(field_type, 'str')
    
    def _generate_endpoints(self, endpoints: List[APIEndpoint], framework: str) -> str:
        """Genera código de endpoints"""
        endpoints_code = []
        
        for endpoint in endpoints:
            if framework == 'fastapi':
                endpoint_code = self._generate_fastapi_endpoint(endpoint)
            elif framework == 'flask':
                endpoint_code = self._generate_flask_endpoint(endpoint)
            
            endpoints_code.append(endpoint_code)
        
        return '\n'.join(endpoints_code)
    
    def _generate_fastapi_endpoint(self, endpoint: APIEndpoint) -> str:
        """Genera endpoint FastAPI"""
        # Generar parámetros
        params = []
        if 'id' in endpoint.route:
            params.append('id: int')
        
        for param in endpoint.parameters:
            param_type = self._get_pydantic_type(param.get('type', 'string'))
            param_str = f"{param['name']}: {param_type}"
            if not param.get('required', True):
                param_str += " = None"
            params.append(param_str)
        
        if endpoint.request_model:
            params.append(f"item: schemas.{endpoint.request_model}")
        
        parameters_str = ', '.join(params)
        
        # Generar cuerpo del endpoint
        body = self._generate_endpoint_body(endpoint, 'fastapi')
        
        function_name = endpoint.name.replace('-', '_').replace('/', '_')
        
        return self.template_manager.get_template('fastapi', 'endpoint_template').format(
            method=endpoint.method,
            route=endpoint.route,
            response_model=f"schemas.{endpoint.response_model}",
            function_name=function_name,
            parameters=parameters_str,
            description=endpoint.description,
            body=body
        )
    
    def _generate_endpoint_body(self, endpoint: APIEndpoint, framework: str) -> str:
        """Genera cuerpo del endpoint"""
        method = endpoint.method.upper()
        
        if framework == 'fastapi':
            if method == 'GET' and '{id}' in endpoint.route:
                return '''        obj = crud.get(db, id=id)
        if not obj:
            raise HTTPException(status_code=404, detail="Item not found")
        return obj'''
            elif method == 'GET':
                return '''        items = crud.get_multi(db, skip=0, limit=100)
        return {"items": items, "total": len(items)}'''
            elif method == 'POST':
                return '''        return crud.create(db, obj_in=item)'''
            elif method == 'PUT':
                return '''        obj = crud.get(db, id=id)
        if not obj:
            raise HTTPException(status_code=404, detail="Item not found")
        return crud.update(db, db_obj=obj, obj_in=item)'''
            elif method == 'DELETE':
                return '''        success = crud.delete(db, id=id)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item deleted successfully"}'''
        
        return '''        # Implementar lógica del endpoint
        return {"message": "Endpoint not implemented"}'''
    
    def _generate_requirements(self, framework: str) -> str:
        """Genera archivo requirements.txt"""
        if framework == 'fastapi':
            return '''fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
'''
        elif framework == 'flask':
            return '''Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
'''
        return ""
    
    def _generate_tests(self, spec: Dict[str, Any], framework: str) -> Dict[str, str]:
        """Genera tests automatizados"""
        tests = {}
        
        if framework == 'fastapi':
            tests['test_main.py'] = '''import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

# Agregar más tests aquí
'''
        
        return tests
    
    def _generate_documentation(self, spec: Dict[str, Any]) -> str:
        """Genera documentación de la API"""
        doc_lines = [
            f"# {spec['api_info']['title']}",
            "",
            spec['api_info']['description'],
            "",
            f"**Versión:** {spec['api_info']['version']}",
            "",
            "## Modelos",
            ""
        ]
        
        for model in spec['models']:
            doc_lines.extend([
                f"### {model.name}",
                "",
                model.description if model.description else f"Modelo {model.name}",
                "",
                "**Campos:**",
                ""
            ])
            
            for field in model.fields:
                required = "✓" if field.get('required', True) else "○"
                doc_lines.append(f"- `{field['name']}` ({field['type']}) {required}")
            
            doc_lines.append("")
        
        doc_lines.extend([
            "## Endpoints",
            ""
        ])
        
        for endpoint in spec['endpoints']:
            doc_lines.extend([
                f"### {endpoint.method.upper()} {endpoint.route}",
                "",
                endpoint.description,
                ""
            ])
        
        return '\n'.join(doc_lines)
    
    def _generate_readme(self, spec: Dict[str, Any], framework: str) -> str:
        """Genera README.md"""
        return f'''# {spec['api_info']['title']}

{spec['api_info']['description']}

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
{"uvicorn main:app --reload" if framework == 'fastapi' else "python app.py"}
```

## Documentación

La documentación interactiva está disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Modelos

{len(spec['models'])} modelos definidos:
{', '.join([model.name for model in spec['models']])}

## Endpoints

{len(spec['endpoints'])} endpoints disponibles:
{chr(10).join([f"- {ep.method.upper()} {ep.route}" for ep in spec['endpoints']])}
'''

    def analyze_specification(self, specification: str) -> Dict[str, Any]:
        """Analiza especificación y proporciona estimaciones"""
        try:
            parsed_spec = self.spec_parser.parse_specification(specification, 'natural')
            
            analysis = {
                'models_count': len(parsed_spec['models']),
                'endpoints_count': len(parsed_spec['endpoints']),
                'estimated_development_time': self._estimate_development_time(parsed_spec),
                'complexity_score': self._calculate_complexity(parsed_spec),
                'recommended_framework': self._recommend_framework(parsed_spec),
                'missing_elements': self._find_missing_elements(parsed_spec)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': f'Error en análisis: {str(e)}'}
    
    def _estimate_development_time(self, spec: Dict[str, Any]) -> Dict[str, int]:
        """Estima tiempo de desarrollo en horas"""
        base_time = 4  # Horas base para setup
        model_time = len(spec['models']) * 2  # 2 horas por modelo
        endpoint_time = len(spec['endpoints']) * 1  # 1 hora por endpoint
        
        total_hours = base_time + model_time + endpoint_time
        
        return {
            'setup_hours': base_time,
            'models_hours': model_time,
            'endpoints_hours': endpoint_time,
            'total_hours': total_hours,
            'estimated_days': max(1, total_hours // 8)
        }
    
    def _calculate_complexity(self, spec: Dict[str, Any]) -> int:
        """Calcula score de complejidad (1-10)"""
        score = 1
        
        # Complejidad por número de modelos
        score += min(3, len(spec['models']) // 2)
        
        # Complejidad por número de endpoints
        score += min(3, len(spec['endpoints']) // 5)
        
        # Complejidad por relaciones entre modelos
        for model in spec['models']:
            score += min(2, len(model.relationships))
        
        return min(10, score)
    
    def _recommend_framework(self, spec: Dict[str, Any]) -> str:
        """Recomienda framework basado en especificación"""
        if len(spec['models']) > 5 or len(spec['endpoints']) > 10:
            return 'fastapi'  # Para APIs más complejas
        else:
            return 'flask'    # Para APIs simples
    
    def _find_missing_elements(self, spec: Dict[str, Any]) -> List[str]:
        """Encuentra elementos faltantes en la especificación"""
        missing = []
        
        if not spec['models']:
            missing.append('No se definieron modelos de datos')
        
        if not spec['endpoints']:
            missing.append('No se definieron endpoints')
        
        for model in spec['models']:
            if not model.fields:
                missing.append(f'Modelo {model.name} no tiene campos definidos')
        
        return missing


# Función de demostración
def demo_api_generation_agent():
    """Demuestra la funcionalidad del agente de generación de APIs"""
    agent = APIGenerationAgent()
    
    print("=== DEMO: AGENTE DE GENERACIÓN DE APIs ===\n")
    
    # Especificación de ejemplo
    specification = """
API: Sistema de Gestión de Productos

Modelo: Producto
- nombre: string obligatorio
- precio: float obligatorio
- descripcion: string opcional
- categoria: string obligatorio
- stock: integer obligatorio

Modelo: Categoria
- nombre: string único obligatorio
- descripcion: string opcional

Endpoint: GET /productos - Listar todos los productos
Endpoint: POST /productos - Crear nuevo producto
Endpoint: PUT /productos/{id} - Actualizar producto
Endpoint: DELETE /productos/{id} - Eliminar producto
"""
    
    print("Especificación de entrada:")
    print(specification)
    print("\n" + "="*50 + "\n")
    
    # Análisis de especificación
    print("1. Analizando especificación...")
    analysis = agent.analyze_specification(specification)
    
    if 'error' not in analysis:
        print(f"✓ Modelos detectados: {analysis['models_count']}")
        print(f"✓ Endpoints detectados: {analysis['endpoints_count']}")
        print(f"✓ Complejidad: {analysis['complexity_score']}/10")
        print(f"✓ Framework recomendado: {analysis['recommended_framework']}")
        print(f"✓ Tiempo estimado: {analysis['estimated_development_time']['total_hours']} horas")
        if analysis.get('missing_elements'):
            print("⚠ Elementos faltantes:")
            for missing in analysis['missing_elements']:
                print(f"  - {missing}")
    else:
        print(f"✗ Error en análisis: {analysis['error']}")
    
    print("\n" + "="*50 + "\n")
    
    # Generación de API
    print("2. Generando API con FastAPI...")
    result = agent.generate_api(specification, framework='fastapi', format_type='natural')
    
    if 'error' not in result:
        print(f"✓ API generada exitosamente (ID: {result['generation_id']})")
        print(f"✓ Framework: {result['framework']}")
        print(f"✓ Modelos: {result['models_count']}")
        print(f"✓ Endpoints: {result['endpoints_count']}")
        print(f"✓ Archivos generados: {len(result['generated_code'])}")
        
        print("\nArchivos generados:")
        for filename in result['generated_code'].keys():
            print(f"  - {filename}")
        
        print("\nVista previa de main.py:")
        main_code = result['generated_code'].get('main.py', '')
        preview_lines = main_code.split('\n')[:20]
        for i, line in enumerate(preview_lines, 1):
            print(f"{i:2d}: {line}")
        if len(main_code.split('\n')) > 20:
            print("    ... (código truncado)")
            
    else:
        print(f"✗ Error en generación: {result['error']}")
    
    print("\n" + "="*50 + "\n")
    
    # Generación con Flask
    print("3. Generando la misma API con Flask...")
    result_flask = agent.generate_api(specification, framework='flask', format_type='natural')
    
    if 'error' not in result_flask:
        print(f"✓ API Flask generada (ID: {result_flask['generation_id']})")
        print(f"✓ Archivos generados: {len(result_flask['generated_code'])}")
        
        print("\nComparación de frameworks:")
        print(f"FastAPI: {len(result['generated_code'])} archivos")
        print(f"Flask: {len(result_flask['generated_code'])} archivos")
        
    else:
        print(f"✗ Error en generación Flask: {result_flask['error']}")


if __name__ == "__main__":
    demo_api_generation_agent()