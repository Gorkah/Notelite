#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de plantillas para NoteLite.
Permite crear, aplicar y gestionar plantillas para diferentes tipos de notas.
"""

import os
import json
import uuid
from datetime import datetime

class TemplateManager:
    """
    Gestor de plantillas que permite usar y crear formatos predefinidos para diferentes
    tipos de notas y listas de tareas.
    """
    
    # Plantillas predefinidas por defecto
    DEFAULT_TEMPLATES = {
        "blank_note": {
            "title": "Nota en blanco",
            "content": "",
            "icon": "blank.png",
            "type": "note",
            "description": "Una nota en blanco para empezar desde cero."
        },
        "meeting_notes": {
            "title": "Notas de reunión",
            "content": """<h2>Detalles de la reunión</h2>
<p><strong>Fecha:</strong> </p>
<p><strong>Participantes:</strong> </p>
<p><strong>Objetivo:</strong> </p>

<h2>Puntos tratados</h2>
<ul>
<li>Punto 1</li>
<li>Punto 2</li>
<li>Punto 3</li>
</ul>

<h2>Decisiones tomadas</h2>
<ul>
<li></li>
</ul>

<h2>Tareas asignadas</h2>
<ul>
<li></li>
</ul>

<h2>Próximos pasos</h2>
<p></p>""",
            "icon": "meeting.png",
            "type": "note",
            "description": "Estructura para tomar notas durante reuniones."
        },
        "daily_planner": {
            "title": "Planificador diario",
            "content": """<h2>Objetivos del día</h2>
<ul>
<li></li>
<li></li>
<li></li>
</ul>

<h2>Prioridades</h2>
<ol>
<li></li>
<li></li>
<li></li>
</ol>

<h2>Reuniones/Eventos</h2>
<ul>
<li><strong>9:00</strong> - </li>
<li><strong>12:00</strong> - </li>
<li><strong>15:00</strong> - </li>
</ul>

<h2>Notas</h2>
<p></p>

<h2>Reflexión del día</h2>
<p></p>""",
            "icon": "daily.png",
            "type": "note",
            "description": "Plantilla para planificar y organizar tu día."
        },
        "todo_list": {
            "title": "Lista de tareas",
            "content": [
                {"text": "Tarea importante", "completed": False},
                {"text": "Tarea secundaria", "completed": False},
                {"text": "Ejemplo de tarea completada", "completed": True}
            ],
            "icon": "todo.png",
            "type": "task_list",
            "description": "Lista básica de tareas por hacer."
        },
        "project_plan": {
            "title": "Plan de proyecto",
            "content": [
                {"text": "Fase 1: Planificación", "completed": False},
                {"text": "Definir objetivos", "completed": False},
                {"text": "Establecer plazos", "completed": False},
                {"text": "Asignar recursos", "completed": False},
                {"text": "Fase 2: Ejecución", "completed": False},
                {"text": "Desarrollo", "completed": False},
                {"text": "Pruebas", "completed": False},
                {"text": "Fase 3: Cierre", "completed": False},
                {"text": "Entrega", "completed": False},
                {"text": "Evaluación", "completed": False}
            ],
            "icon": "project.png",
            "type": "task_list",
            "description": "Estructura para gestionar las fases de un proyecto."
        },
        "shopping_list": {
            "title": "Lista de compras",
            "content": [
                {"text": "🥦 Verduras", "completed": False},
                {"text": "🍎 Frutas", "completed": False},
                {"text": "🥖 Pan", "completed": False},
                {"text": "🥛 Leche", "completed": False},
                {"text": "🧀 Queso", "completed": False}
            ],
            "icon": "shopping.png",
            "type": "task_list",
            "description": "Lista para organizar tus compras."
        }
    }
    
    def __init__(self, data_manager):
        """Inicializa el gestor de plantillas."""
        self.data_manager = data_manager
        self.templates_dir = os.path.join(os.path.expanduser("~"), "NoteLite", "templates")
        
        # Asegurar que el directorio existe
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Cargar plantillas personalizadas o crear las predeterminadas
        self.templates = self._load_templates()
        
    def _load_templates(self):
        """Carga las plantillas desde el sistema o crea las predeterminadas."""
        templates_file = os.path.join(self.templates_dir, "templates.json")
        
        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al cargar plantillas: {e}")
                return self.DEFAULT_TEMPLATES.copy()
        else:
            # Si no existen, guardar las predeterminadas
            self._save_templates(self.DEFAULT_TEMPLATES)
            return self.DEFAULT_TEMPLATES.copy()
    
    def _save_templates(self, templates_data):
        """Guarda las plantillas en el sistema."""
        templates_file = os.path.join(self.templates_dir, "templates.json")
        
        try:
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar plantillas: {e}")
            return False
    
    def get_all_templates(self):
        """Obtiene todas las plantillas disponibles."""
        return self.templates
    
    def get_template(self, template_id):
        """Obtiene una plantilla específica por su ID."""
        return self.templates.get(template_id)
    
    def get_templates_by_type(self, template_type):
        """Obtiene las plantillas filtradas por tipo."""
        return {
            template_id: template 
            for template_id, template in self.templates.items() 
            if template.get('type') == template_type
        }
    
    def create_note_from_template(self, template_id):
        """Crea una nueva nota a partir de una plantilla."""
        template = self.get_template(template_id)
        if not template:
            return None
        
        # Crear la nota
        title = template.get('title', 'Nueva nota')
        content = template.get('content', '')
        note_type = template.get('type', 'note')
        
        # Ajustar el título para indicar que es nuevo
        if title == "Notas de reunión":
            title = f"Reunión {datetime.now().strftime('%d/%m/%Y')}"
        elif title == "Planificador diario":
            title = f"Plan para {datetime.now().strftime('%d/%m/%Y')}"
        
        # Crear la nota en el gestor de datos
        note_id = self.data_manager.create_note(title, content, note_type)
        return note_id
    
    def save_as_template(self, note_id, template_name, description=""):
        """Guarda una nota existente como una nueva plantilla."""
        note = self.data_manager.get_note(note_id)
        if not note:
            return False
        
        # Generar ID único para la plantilla
        template_id = f"custom_{uuid.uuid4().hex[:8]}"
        
        # Crear la plantilla
        template = {
            "title": template_name,
            "content": note.get('content', ''),
            "icon": "custom.png",
            "type": note.get('type', 'note'),
            "description": description
        }
        
        # Guardar la plantilla
        self.templates[template_id] = template
        self._save_templates(self.templates)
        
        return template_id
    
    def delete_template(self, template_id):
        """Elimina una plantilla personalizada."""
        # No permitir eliminar plantillas predeterminadas
        if template_id in self.DEFAULT_TEMPLATES:
            return False
        
        if template_id in self.templates:
            del self.templates[template_id]
            self._save_templates(self.templates)
            return True
        
        return False
