#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diálogo de selección de notas para NoteLite.
Permite seleccionar notas existentes para varias operaciones.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget, QListWidgetItem,
                            QSplitter, QWidget, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon


class NoteSelectionDialog(QDialog):
    """Diálogo para seleccionar una nota existente."""
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.selected_note_id = None
        
        self.setWindowTitle("Seleccionar nota")
        self.setMinimumSize(700, 500)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Filtro de tipo de nota
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Mostrar:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Todas las notas", "Solo notas de texto", "Solo listas de tareas"])
        self.type_filter.currentIndexChanged.connect(self.filter_notes)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Splitter con lista de notas y vista previa
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Lista de notas
        self.notes_list = QListWidget()
        self.notes_list.setIconSize(QSize(32, 32))
        self.notes_list.setAlternatingRowColors(True)
        self.notes_list.itemClicked.connect(self.preview_note)
        splitter.addWidget(self.notes_list)
        
        # Panel de vista previa
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        
        preview_layout.addWidget(QLabel("Vista previa:"))
        
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        preview_layout.addWidget(self.preview_edit)
        
        splitter.addWidget(preview_panel)
        
        # Establecer tamaños iniciales
        splitter.setSizes([300, 400])
        
        layout.addWidget(splitter)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        select_btn = QPushButton("Seleccionar")
        select_btn.clicked.connect(self.select_note)
        select_btn.setDefault(True)
        buttons_layout.addWidget(select_btn)
        
        layout.addLayout(buttons_layout)
        
        # Cargar notas
        self.load_notes()
    
    def load_notes(self, note_type=None):
        """Carga las notas en la lista."""
        # Limpiar lista
        self.notes_list.clear()
        
        # Obtener todas las notas
        all_notes = self.data_manager.get_all_notes()
        
        # Filtrar por tipo si es necesario
        if note_type == "note":
            filtered_notes = {
                note_id: note for note_id, note in all_notes.items()
                if note.get('type') == 'note'
            }
        elif note_type == "task_list":
            filtered_notes = {
                note_id: note for note_id, note in all_notes.items()
                if note.get('type') == 'task_list'
            }
        else:
            filtered_notes = all_notes
        
        # Añadir a la lista
        for note_id, note in filtered_notes.items():
            title = note.get('title', 'Sin título')
            note_type = note.get('type', 'note')
            
            # Crear item
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, note_id)
            item.setData(Qt.ItemDataRole.UserRole + 1, note_type)
            
            # Establecer icono según tipo
            if note_type == 'task_list':
                item.setIcon(QIcon("icons/task_list.png"))
            else:
                item.setIcon(QIcon("icons/note.png"))
            
            self.notes_list.addItem(item)
    
    def filter_notes(self):
        """Filtra las notas según el tipo seleccionado."""
        filter_index = self.type_filter.currentIndex()
        
        if filter_index == 0:  # Todas
            self.load_notes()
        elif filter_index == 1:  # Solo notas
            self.load_notes("note")
        elif filter_index == 2:  # Solo listas
            self.load_notes("task_list")
    
    def preview_note(self, item):
        """Muestra una vista previa de la nota seleccionada."""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        note_data = self.data_manager.get_note(note_id)
        
        if not note_data:
            return
        
        # Mostrar contenido según el tipo
        note_type = note_data.get('type', 'note')
        content = note_data.get('content', '')
        
        if note_type == 'task_list':
            # Para listas de tareas
            if isinstance(content, list):
                preview_text = ""
                for task in content:
                    status = "✓" if task.get('completed', False) else "☐"
                    preview_text += f"{status} {task.get('text', '')}\n"
                self.preview_edit.setPlainText(preview_text)
            else:
                self.preview_edit.setPlainText("Contenido no disponible")
        else:
            # Para notas de texto
            if content:
                self.preview_edit.setHtml(content)
            else:
                self.preview_edit.setPlainText("Nota vacía")
    
    def select_note(self):
        """Selecciona la nota actual y cierra el diálogo."""
        selected_items = self.notes_list.selectedItems()
        
        if not selected_items:
            return
        
        # Guardar ID de la nota seleccionada
        self.selected_note_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Cerrar con éxito
        self.accept()
    
    def get_selected_note_id(self):
        """Devuelve el ID de la nota seleccionada."""
        return self.selected_note_id
