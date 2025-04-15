#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Motor de búsqueda avanzada para NoteLite.
Permite buscar notas por contenido, etiquetas, fecha y otros atributos.
"""

import re
import datetime
from typing import List, Dict, Any, Tuple

class SearchEngine:
    """
    Motor de búsqueda avanzada para encontrar notas en NoteLite.
    Implementa funciones de búsqueda por texto, etiquetas, y filtros avanzados.
    """
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
    
    def search(self, query=None, tags=None, date_from=None, date_to=None, 
                note_type=None, sort_by="updated_at", sort_order="desc"):
        """
        Realiza una búsqueda con los criterios especificados.
        
        Args:
            query: Texto a buscar en título y contenido
            tags: Lista de etiquetas para filtrar
            date_from: Fecha desde la cual filtrar (iso format)
            date_to: Fecha hasta la cual filtrar (iso format)
            note_type: Tipo de nota ('note' o 'task_list')
            sort_by: Campo por el cual ordenar ('title', 'created_at', 'updated_at')
            sort_order: Orden ('asc' o 'desc')
            
        Returns:
            Lista de notas que coinciden con los criterios
        """
        # Obtener todas las notas
        all_notes = self.data_manager.get_all_notes()
        results = []
        
        for note_id, note_data in all_notes.items():
            # Agregar metadatos que podrían faltar
            note_data['id'] = note_id
            if 'tags' not in note_data:
                note_data['tags'] = []
                
            # Aplicar filtros
            if not self._matches_filters(note_data, query, tags, date_from, date_to, note_type):
                continue
                
            results.append(note_data)
        
        # Ordenar resultados
        results = self._sort_results(results, sort_by, sort_order)
        
        return results
    
    def _matches_filters(self, note, query=None, tags=None, date_from=None, date_to=None, note_type=None) -> bool:
        """Comprueba si una nota coincide con los filtros aplicados."""
        # Filtro por tipo de nota
        if note_type and note.get('type') != note_type:
            return False
        
        # Filtro por texto
        if query and not self._matches_text(note, query):
            return False
        
        # Filtro por etiquetas
        if tags and not self._matches_tags(note, tags):
            return False
        
        # Filtro por fecha
        if not self._matches_date(note, date_from, date_to):
            return False
        
        return True
    
    def _matches_text(self, note, query) -> bool:
        """Comprueba si una nota coincide con la búsqueda de texto."""
        if not query:
            return True
            
        query = query.lower()
        
        # Buscar en el título
        if note.get('title', '').lower().find(query) != -1:
            return True
        
        # Buscar en el contenido (simplificado para contenido HTML)
        content = note.get('content', '')
        
        # Para listas de tareas, el contenido puede ser JSON
        if note.get('type') == 'task_list' and isinstance(content, str):
            try:
                # Para búsqueda básica, solo comprobamos si el texto aparece
                if content.lower().find(query) != -1:
                    return True
            except:
                pass
        # Para notas normales con HTML
        elif isinstance(content, str):
            # Eliminar tags HTML para búsqueda de texto
            text_content = re.sub(r'<[^>]*>', ' ', content)
            if text_content.lower().find(query) != -1:
                return True
        
        return False
    
    def _matches_tags(self, note, tags) -> bool:
        """Comprueba si una nota coincide con las etiquetas buscadas."""
        if not tags:
            return True
            
        note_tags = note.get('tags', [])
        
        # Verificar si todas las etiquetas buscadas están en la nota
        for tag in tags:
            if tag not in note_tags:
                return False
                
        return True
    
    def _matches_date(self, note, date_from, date_to) -> bool:
        """Comprueba si una nota está dentro del rango de fechas."""
        if not date_from and not date_to:
            return True
            
        # Obtener fecha de actualización de la nota
        updated_at = note.get('updated_at')
        if not updated_at:
            return True  # Si no tiene fecha, no filtramos
            
        try:
            note_date = datetime.datetime.fromisoformat(updated_at)
            
            if date_from:
                from_date = datetime.datetime.fromisoformat(date_from)
                if note_date < from_date:
                    return False
                    
            if date_to:
                to_date = datetime.datetime.fromisoformat(date_to)
                if note_date > to_date:
                    return False
                    
            return True
        except:
            return True  # En caso de error, no filtramos
    
    def _sort_results(self, results, sort_by, sort_order):
        """Ordena los resultados según el criterio especificado."""
        reverse = sort_order.lower() == 'desc'
        
        def get_sort_key(note):
            if sort_by == 'title':
                return note.get('title', '')
            elif sort_by in ['created_at', 'updated_at']:
                date_str = note.get(sort_by, '')
                try:
                    return datetime.datetime.fromisoformat(date_str)
                except:
                    return datetime.datetime.min
            return ''
        
        return sorted(results, key=get_sort_key, reverse=reverse)
    
    def get_all_tags(self) -> List[Tuple[str, int]]:
        """
        Obtiene todas las etiquetas utilizadas en las notas con su frecuencia.
        
        Returns:
            Lista de tuplas (etiqueta, frecuencia) ordenadas por frecuencia
        """
        all_notes = self.data_manager.get_all_notes()
        tag_counts = {}
        
        for _, note_data in all_notes.items():
            tags = note_data.get('tags', [])
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Ordenar por frecuencia (más frecuentes primero)
        return sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    
    def add_tag_to_note(self, note_id, tag):
        """Añade una etiqueta a una nota."""
        note = self.data_manager.get_note(note_id)
        if note:
            if 'tags' not in note:
                note['tags'] = []
            if tag not in note['tags']:
                note['tags'].append(tag)
                self.data_manager.update_note(
                    note_id, 
                    note.get('title', ''), 
                    note.get('content', ''),
                    note.get('type', 'note')
                )
                return True
        return False
    
    def remove_tag_from_note(self, note_id, tag):
        """Elimina una etiqueta de una nota."""
        note = self.data_manager.get_note(note_id)
        if note and 'tags' in note and tag in note['tags']:
            note['tags'].remove(tag)
            self.data_manager.update_note(
                note_id, 
                note.get('title', ''), 
                note.get('content', ''),
                note.get('type', 'note')
            )
            return True
        return False
