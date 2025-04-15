#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget para listas de tareas con casillas de verificación.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                           QCheckBox, QPushButton, QScrollArea, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont
import json

class TaskListWidget(QWidget):
    """Widget para crear y gestionar listas de tareas."""
    
    # Señal que se emite cuando cambian los datos
    data_changed = pyqtSignal(str, str, str)  # note_id, title, content
    
    def __init__(self, note_id, title, content):
        super().__init__()
        
        self.note_id = note_id
        self.title = title
        self.tasks = []
        
        # Intentar cargar tareas desde el contenido
        if content:
            try:
                self.tasks = json.loads(content)
            except json.JSONDecodeError:
                # Si falla, iniciar con una lista vacía
                self.tasks = []
        
        if not self.tasks:
            # Añadir una tarea vacía por defecto
            self.tasks.append({"text": "", "completed": False})
        
        self.setup_ui()
        self.load_content()
    
    def setup_ui(self):
        """Configura la interfaz de la lista de tareas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Título
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Título de la lista de tareas")
        self.title_edit.setProperty("class", "note-title")
        font = self.title_edit.font()
        font.setPointSize(16)
        self.title_edit.setFont(font)
        layout.addWidget(self.title_edit)
        
        # Etiqueta para la lista
        layout.addWidget(QLabel("Tareas:"))
        
        # Área de desplazamiento para las tareas
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Contenedor para las tareas
        self.tasks_container = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        scroll_area.setWidget(self.tasks_container)
        
        # Botón para añadir nueva tarea
        add_task_btn = QPushButton("+ Añadir tarea")
        add_task_btn.clicked.connect(self.add_task)
        layout.addWidget(add_task_btn)
        
        # Conectar señal de cambio en el título
        self.title_edit.textChanged.connect(self.on_data_changed)
    
    def load_content(self):
        """Carga las tareas desde self.tasks."""
        self.title_edit.setText(self.title)
        
        # Limpiar contenedor actual
        while self.tasks_layout.count():
            item = self.tasks_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Añadir las tareas
        for i, task in enumerate(self.tasks):
            self.add_task_widget(i, task["text"], task["completed"])
    
    def add_task_widget(self, index, text="", completed=False):
        """Añade un widget de tarea."""
        task_widget = QWidget()
        task_layout = QHBoxLayout(task_widget)
        task_layout.setContentsMargins(0, 5, 0, 5)
        
        # Casilla de verificación
        checkbox = QCheckBox()
        checkbox.setChecked(completed)
        checkbox.stateChanged.connect(lambda state, idx=index: self.on_task_state_changed(idx, state))
        task_layout.addWidget(checkbox)
        
        # Campo de texto
        text_edit = QLineEdit(text)
        text_edit.setPlaceholderText("Escribe una tarea...")
        text_edit.textChanged.connect(lambda text, idx=index: self.on_task_text_changed(idx, text))
        task_layout.addWidget(text_edit)
        
        # Botón para eliminar
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(QSize(25, 25))
        delete_btn.clicked.connect(lambda _, idx=index: self.delete_task(idx))
        task_layout.addWidget(delete_btn)
        
        self.tasks_layout.addWidget(task_widget)
        
        return task_widget
    
    def add_task(self):
        """Añade una nueva tarea vacía."""
        self.tasks.append({"text": "", "completed": False})
        self.add_task_widget(len(self.tasks) - 1)
        self.on_data_changed()
    
    def delete_task(self, index):
        """Elimina una tarea por su índice."""
        if index < len(self.tasks):
            # Eliminar de la lista de datos
            self.tasks.pop(index)
            
            # Recargar la UI
            self.load_content()
            self.on_data_changed()
    
    def on_task_text_changed(self, index, text):
        """Maneja los cambios en el texto de una tarea."""
        if index < len(self.tasks):
            self.tasks[index]["text"] = text
            self.on_data_changed()
    
    def on_task_state_changed(self, index, state):
        """Maneja los cambios en el estado de una tarea."""
        if index < len(self.tasks):
            self.tasks[index]["completed"] = (state == Qt.CheckState.Checked.value)
            self.on_data_changed()
    
    def on_data_changed(self):
        """Emite la señal de cambio de datos."""
        self.title = self.title_edit.text()
        content = json.dumps(self.tasks)
        self.data_changed.emit(self.note_id, self.title, content)
    
    def save(self):
        """Guarda explícitamente la lista de tareas."""
        self.on_data_changed()
