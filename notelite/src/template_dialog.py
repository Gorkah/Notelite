#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diálogo de plantillas para NoteLite.
Muestra y permite seleccionar plantillas para diferentes tipos de notas.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QListWidget, QListWidgetItem,
                            QTabWidget, QWidget, QTextEdit, QGroupBox,
                            QFormLayout, QLineEdit, QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap


class TemplatesDialog(QDialog):
    """Diálogo para mostrar y seleccionar plantillas."""
    
    template_selected = pyqtSignal(str)  # Señal para indicar la plantilla seleccionada
    
    def __init__(self, templates_manager, parent=None):
        super().__init__(parent)
        self.templates_manager = templates_manager
        self.setWindowTitle("Plantillas de NoteLite")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        main_layout = QVBoxLayout(self)
        
        # Pestañas para tipos de plantillas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        
        # Pestaña para notas
        self.notes_tab = QWidget()
        self.tabs.addTab(self.notes_tab, "Notas")
        
        # Pestaña para listas de tareas
        self.tasks_tab = QWidget()
        self.tabs.addTab(self.tasks_tab, "Listas de tareas")
        
        # Pestaña para plantillas personalizadas
        self.custom_tab = QWidget()
        self.tabs.addTab(self.custom_tab, "Mis plantillas")
        
        main_layout.addWidget(self.tabs)
        
        # Configurar cada pestaña
        self.setup_notes_tab()
        self.setup_tasks_tab()
        self.setup_custom_tab()
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(close_btn)
        
        create_btn = QPushButton("Crear nueva nota")
        create_btn.clicked.connect(self.create_from_selected)
        create_btn.setDefault(True)
        buttons_layout.addWidget(create_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_notes_tab(self):
        """Configura la pestaña de plantillas de notas."""
        layout = QVBoxLayout(self.notes_tab)
        
        # Obtener plantillas de notas
        note_templates = self.templates_manager.get_templates_by_type("note")
        
        # Lista de plantillas
        self.notes_list = TemplateListWidget()
        layout.addWidget(self.notes_list)
        
        # Añadir plantillas a la lista
        for template_id, template in note_templates.items():
            title = template.get('title', 'Sin título')
            description = template.get('description', '')
            icon = template.get('icon', 'note.png')
            
            # Crear item para la lista
            item = TemplateListItem(template_id, title, description, icon)
            self.notes_list.addItem(item)
            
        # Conectar evento de selección
        self.notes_list.itemClicked.connect(self.preview_template)
    
    def setup_tasks_tab(self):
        """Configura la pestaña de plantillas de listas de tareas."""
        layout = QVBoxLayout(self.tasks_tab)
        
        # Obtener plantillas de listas
        task_templates = self.templates_manager.get_templates_by_type("task_list")
        
        # Lista de plantillas
        self.tasks_list = TemplateListWidget()
        layout.addWidget(self.tasks_list)
        
        # Añadir plantillas a la lista
        for template_id, template in task_templates.items():
            title = template.get('title', 'Sin título')
            description = template.get('description', '')
            icon = template.get('icon', 'todo.png')
            
            # Crear item para la lista
            item = TemplateListItem(template_id, title, description, icon)
            self.tasks_list.addItem(item)
            
        # Conectar evento de selección
        self.tasks_list.itemClicked.connect(self.preview_template)
    
    def setup_custom_tab(self):
        """Configura la pestaña de plantillas personalizadas."""
        main_layout = QVBoxLayout(self.custom_tab)
        
        # Dividir panel para lista y formulario
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel izquierdo: lista de plantillas personalizadas
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Lista de plantillas personalizadas
        self.custom_list = TemplateListWidget()
        left_layout.addWidget(self.custom_list)
        
        # Botones para gestionar plantillas
        buttons_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Eliminar")
        delete_btn.clicked.connect(self.delete_custom_template)
        buttons_layout.addWidget(delete_btn)
        
        left_layout.addLayout(buttons_layout)
        
        # Panel derecho: formulario para crear nueva plantilla
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Formulario
        form_group = QGroupBox("Nueva plantilla personalizada")
        form_layout = QFormLayout(form_group)
        
        self.template_name = QLineEdit()
        form_layout.addRow("Nombre:", self.template_name)
        
        self.template_description = QLineEdit()
        form_layout.addRow("Descripción:", self.template_description)
        
        from_note_btn = QPushButton("Crear a partir de una nota existente")
        from_note_btn.clicked.connect(self.show_note_selection)
        form_layout.addRow("", from_note_btn)
        
        right_layout.addWidget(form_group)
        
        # Agregar paneles al splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 400])
        
        # Cargar plantillas personalizadas
        self.load_custom_templates()
        
        # Conectar evento de selección
        self.custom_list.itemClicked.connect(self.preview_template)
    
    def load_custom_templates(self):
        """Carga las plantillas personalizadas en la lista."""
        # Limpiar lista
        self.custom_list.clear()
        
        # Obtener todas las plantillas
        all_templates = self.templates_manager.get_all_templates()
        default_template_ids = self.templates_manager.DEFAULT_TEMPLATES.keys()
        
        # Filtrar solo las personalizadas
        custom_templates = {
            template_id: template for template_id, template in all_templates.items()
            if template_id not in default_template_ids
        }
        
        # Añadir a la lista
        for template_id, template in custom_templates.items():
            title = template.get('title', 'Sin título')
            description = template.get('description', '')
            icon = template.get('icon', 'custom.png')
            
            # Crear item para la lista
            item = TemplateListItem(template_id, title, description, icon)
            self.custom_list.addItem(item)
    
    def preview_template(self, item):
        """Muestra una vista previa de la plantilla seleccionada."""
        template_id = item.data(Qt.ItemDataRole.UserRole)
        template = self.templates_manager.get_template(template_id)
        
        if not template:
            return
        
        # Crear diálogo de vista previa
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle(f"Vista previa: {template.get('title', 'Sin título')}")
        preview_dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(preview_dialog)
        
        # Información de la plantilla
        info_layout = QHBoxLayout()
        
        # Icono
        icon_label = QLabel()
        if template.get('icon'):
            # Intentar cargar el icono
            pixmap = QPixmap(f"icons/{template.get('icon')}")
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        info_layout.addWidget(icon_label)
        
        # Título y descripción
        text_layout = QVBoxLayout()
        title_label = QLabel(template.get('title', 'Sin título'))
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        text_layout.addWidget(title_label)
        
        desc_label = QLabel(template.get('description', ''))
        text_layout.addWidget(desc_label)
        
        info_layout.addLayout(text_layout)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # Contenido de la plantilla
        content_label = QLabel("Contenido:")
        layout.addWidget(content_label)
        
        content = template.get('content', '')
        preview = QTextEdit()
        preview.setReadOnly(True)
        
        # Mostrar el contenido según el tipo
        if template.get('type') == 'note':
            # Para notas, mostrar el HTML
            preview.setHtml(content)
        elif template.get('type') == 'task_list':
            # Para listas de tareas, mostrar texto representativo
            if isinstance(content, list):
                preview_text = ""
                for task in content:
                    status = "✓" if task.get('completed', False) else "☐"
                    preview_text += f"{status} {task.get('text', '')}\n"
                preview.setPlainText(preview_text)
        
        layout.addWidget(preview)
        
        # Botón para usar esta plantilla
        use_btn = QPushButton("Usar esta plantilla")
        use_btn.clicked.connect(lambda: self.select_template(template_id, preview_dialog))
        layout.addWidget(use_btn)
        
        preview_dialog.exec()
    
    def select_template(self, template_id, dialog=None):
        """Selecciona una plantilla y cierra el diálogo."""
        self.template_selected.emit(template_id)
        
        # Cerrar diálogo de vista previa si existe
        if dialog:
            dialog.accept()
            
        # Cerrar diálogo principal
        self.accept()
    
    def create_from_selected(self):
        """Crea una nota a partir de la plantilla seleccionada."""
        # Determinar qué pestaña está activa
        current_tab = self.tabs.currentWidget()
        
        if current_tab == self.notes_tab:
            selected_items = self.notes_list.selectedItems()
        elif current_tab == self.tasks_tab:
            selected_items = self.tasks_list.selectedItems()
        elif current_tab == self.custom_tab:
            selected_items = self.custom_list.selectedItems()
        else:
            selected_items = []
        
        if not selected_items:
            QMessageBox.warning(self, "Selección requerida", "Por favor selecciona una plantilla.")
            return
        
        # Obtener ID de la plantilla seleccionada
        template_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.select_template(template_id)
    
    def delete_custom_template(self):
        """Elimina una plantilla personalizada."""
        selected_items = self.custom_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "Selección requerida", "Por favor selecciona una plantilla para eliminar.")
            return
        
        # Confirmar eliminación
        template_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        template = self.templates_manager.get_template(template_id)
        
        if not template:
            return
        
        confirm = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar la plantilla '{template.get('title')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        # Eliminar plantilla
        success = self.templates_manager.delete_template(template_id)
        
        if success:
            QMessageBox.information(self, "Plantilla eliminada", "La plantilla se ha eliminado correctamente.")
            self.load_custom_templates()
        else:
            QMessageBox.warning(self, "Error", "No se pudo eliminar la plantilla.")
    
    def show_note_selection(self):
        """Muestra un diálogo para seleccionar una nota existente."""
        from note_selector_dialog import NoteSelectionDialog
        
        dialog = NoteSelectionDialog(self.templates_manager.data_manager, self)
        
        if dialog.exec():
            note_id = dialog.get_selected_note_id()
            if note_id:
                self.save_note_as_template(note_id)
    
    def save_note_as_template(self, note_id):
        """Guarda una nota como plantilla personalizada."""
        note = self.templates_manager.data_manager.get_note(note_id)
        
        if not note:
            QMessageBox.warning(self, "Error", "La nota seleccionada no existe.")
            return
        
        # Obtener nombre y descripción
        template_name = self.template_name.text().strip()
        template_description = self.template_description.text().strip()
        
        if not template_name:
            template_name = note.get('title', 'Nueva plantilla')
        
        # Guardar como plantilla
        template_id = self.templates_manager.save_as_template(
            note_id, template_name, template_description
        )
        
        if template_id:
            QMessageBox.information(
                self, "Plantilla creada", 
                f"Se ha creado correctamente la plantilla '{template_name}'."
            )
            self.load_custom_templates()
        else:
            QMessageBox.warning(self, "Error", "No se pudo crear la plantilla.")


class TemplateListWidget(QListWidget):
    """Widget personalizado para mostrar la lista de plantillas."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(48, 48))
        self.setSpacing(2)
        self.setAlternatingRowColors(True)


class TemplateListItem(QListWidgetItem):
    """Item personalizado para la lista de plantillas."""
    
    def __init__(self, template_id, title, description, icon_filename):
        super().__init__()
        
        # Guardar ID de plantilla en los datos del item
        self.setData(Qt.ItemDataRole.UserRole, template_id)
        
        # Configurar texto
        self.setText(f"{title}\n{description}")
        
        # Configurar icono
        icon_path = f"icons/{icon_filename}"
        if QIcon(icon_path).isNull():
            # Si no existe, usar un icono por defecto
            self.setIcon(QIcon("icons/generic_template.png"))
        else:
            self.setIcon(QIcon(icon_path))
        
        # Configurar tamaño
        self.setSizeHint(QSize(self.sizeHint().width(), 60))
