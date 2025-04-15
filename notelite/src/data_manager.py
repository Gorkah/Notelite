#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de datos para NoteLite.
Maneja el guardado y carga de notas y listas de tareas.
"""

import os
import json
import uuid
from datetime import datetime

class DataManager:
    """Gestor de datos para almacenar y recuperar notas y listas de tareas."""
    
    def __init__(self):
        # Directorio base para almacenar datos
        self.data_dir = os.path.join(os.path.expanduser("~"), "NoteLite")
        self.notes_dir = os.path.join(self.data_dir, "notes")
        
        # Asegurar que los directorios existen
        self._ensure_dirs_exist()
        
        # Cargar notas
        self.notes = self._load_notes()
    
    def _ensure_dirs_exist(self):
        """Asegura que los directorios necesarios existen."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.notes_dir, exist_ok=True)
    
    def _load_notes(self):
        """Carga todas las notas del sistema de archivos."""
        notes = {}
        
        if os.path.exists(self.notes_dir):
            for filename in os.listdir(self.notes_dir):
                if filename.endswith(".json"):
                    note_id = filename[:-5]  # Eliminar la extensión .json
                    note_path = os.path.join(self.notes_dir, filename)
                    
                    try:
                        with open(note_path, 'r', encoding='utf-8') as f:
                            note_data = json.load(f)
                            notes[note_id] = note_data
                    except Exception as e:
                        print(f"Error al cargar la nota {note_id}: {e}")
        
        return notes
    
    def _save_note_to_file(self, note_id, note_data):
        """Guarda una nota en un archivo JSON."""
        note_path = os.path.join(self.notes_dir, f"{note_id}.json")
        
        try:
            with open(note_path, 'w', encoding='utf-8') as f:
                json.dump(note_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar la nota {note_id}: {e}")
            return False
    
    def create_note(self, title, content, note_type="note"):
        """Crea una nueva nota.
        
        Args:
            title: Título de la nota.
            content: Contenido de la nota.
            note_type: Tipo de nota ('note' o 'task_list').
            
        Returns:
            ID de la nota creada.
        """
        note_id = str(uuid.uuid4())
        
        note_data = {
            'id': note_id,
            'title': title,
            'content': content,
            'type': note_type,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.notes[note_id] = note_data
        self._save_note_to_file(note_id, note_data)
        
        return note_id
    
    def update_note(self, note_id, title, content, note_type=None, tags=None):
        """Actualiza una nota existente.
        
        Args:
            note_id: ID de la nota a actualizar.
            title: Nuevo título.
            content: Nuevo contenido.
            note_type: Tipo de nota (opcional).
            tags: Lista de etiquetas (opcional).
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario.
        """
        if note_id not in self.notes:
            return False
        
        note_data = self.notes[note_id]
        note_data['title'] = title
        note_data['content'] = content
        note_data['updated_at'] = datetime.now().isoformat()
        
        if note_type:
            note_data['type'] = note_type
        
        # Actualizar etiquetas si se proporcionan
        if tags is not None:
            note_data['tags'] = tags
        
        self.notes[note_id] = note_data
        return self._save_note_to_file(note_id, note_data)
    
    def get_note(self, note_id):
        """Obtiene una nota por su ID.
        
        Args:
            note_id: ID de la nota.
            
        Returns:
            Datos de la nota o None si no existe.
        """
        return self.notes.get(note_id)
    
    def delete_note(self, note_id):
        """Elimina una nota.
        
        Args:
            note_id: ID de la nota a eliminar.
            
        Returns:
            True si la eliminación fue exitosa, False en caso contrario.
        """
        if note_id not in self.notes:
            return False
        
        # Eliminar del diccionario en memoria
        del self.notes[note_id]
        
        # Eliminar el archivo
        note_path = os.path.join(self.notes_dir, f"{note_id}.json")
        try:
            if os.path.exists(note_path):
                os.remove(note_path)
            return True
        except Exception as e:
            print(f"Error al eliminar la nota {note_id}: {e}")
            return False
    
    def get_all_notes(self):
        """Obtiene todas las notas.
        
        Returns:
            Diccionario con todas las notas.
        """
        return self.notes
    
    def search_notes(self, query):
        """Busca notas que coincidan con la consulta.
        
        Args:
            query: Texto a buscar en títulos y contenido.
            
        Returns:
            Lista de IDs de notas que coinciden con la búsqueda.
        """
        results = []
        query = query.lower()
        
        for note_id, note_data in self.notes.items():
            title = note_data.get('title', '').lower()
            content = note_data.get('content', '').lower()
            
            if query in title or query in content:
                results.append(note_id)
        
        return results
