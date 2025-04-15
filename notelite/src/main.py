#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NoteLite - Una aplicación de notas moderna y ligera con temas retro.
"""

import sys
import os
import random
import datetime
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplitter, QTreeView, 
                           QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget,
                           QPushButton, QFileDialog, QMessageBox, QMenu,
                           QStatusBar, QLabel, QTabWidget, QToolBar, QToolButton,
                           QComboBox, QDialog, QFontComboBox, QGridLayout,
                           QColorDialog, QLineEdit, QGroupBox)
from PyQt6.QtCore import Qt, QSize, QModelIndex, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QStandardItemModel, QStandardItem, QFont

from note_editor import NoteEditor
from task_list import TaskListWidget
from data_manager import DataManager
from theme_manager import RetroThemeManager, ThemeSelectorWidget
from theme_connector import connect_theme_selector
from templates_manager import TemplateManager
from stats_manager import StatsManager, StatsWidget
from enhanced_stats_manager import EnhancedStatsManager, EnhancedStatsWidget, StatsStatusBar
from multimedia_manager import MultimediaManager, MediaInsertDialog
from markdown_manager import RetroMarkdownManager, MarkdownEditorHelper
from template_dialog import TemplatesDialog
from tag_manager import TagManager, TagSelectorWidget, TagFilterWidget
from reminder_manager import ReminderManager, ReminderListWidget, ReminderDialog, ReminderNotificationDialog
from calendar_widget import NoteCalendarWidget
from resizable_note import ResizableNoteEditor, FormattingToolbar, StickyNoteWindow, create_sticky_note

class NoteLiteApp(QMainWindow):
    """Ventana principal de la aplicación NoteLite."""
    
    def __init__(self):
        super().__init__()
        
        # Inicializar gestor de temas retro
        self.theme_manager = RetroThemeManager()
        
        # Configuración de la ventana principal
        self.setWindowTitle("NoteLite - Bloc de Notas Retro")
        self.setMinimumSize(1000, 700)
        
        # Inicializa los gestores principales
        self.data_manager = DataManager()
        self.templates_manager = TemplateManager(self.data_manager)
        self.stats_manager = StatsManager(self.data_manager)
        self.enhanced_stats_manager = EnhancedStatsManager(self.data_manager)  # Estadísticas mejoradas
        self.multimedia_manager = MultimediaManager()
        self.markdown_manager = RetroMarkdownManager(self.theme_manager)
        self.markdown_helper = MarkdownEditorHelper()
        self.tag_manager = TagManager(self.data_manager)
        self.reminder_manager = ReminderManager(self.data_manager)
        
        # Diccionario para llevar registro de sticky notes abiertas
        self.sticky_notes = {}
        
        # Configurar callback para notificaciones de recordatorios
        self.reminder_manager.set_notification_callback(self.show_reminder_notification)
        
        # Variables de sesión
        self.session_start_time = time.time()
        
        # Configurar interfaz principal
        self.setup_ui()
        
        # Aplicar tema inicial
        self.apply_current_theme()
        
        # Evitar fuentes problemáticas
        self.avoid_problematic_fonts()
        
        # Iniciar carga de notas
        self.load_notes()
        
        # Añadir efectos retro
        self.setup_retro_effects()
        
        # Registrar inicio de sesión
        self.stats_manager.record_app_launch()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Panel principal con splitter
        main_panel = QWidget()
        content_layout = QHBoxLayout(main_panel)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Splitter para permitir redimensionar los paneles
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        content_layout.addWidget(self.splitter)
        
        # Panel superior para selector de temas y otras opciones
        top_panel = QWidget()
        top_panel.setMaximumHeight(40)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(5, 5, 5, 5)
        
        # Selector de temas
        self.theme_selector = ThemeSelectorWidget(self.theme_manager)
        # Usar el conector de temas en lugar de conectar directamente
        connect_theme_selector(self, self.theme_selector)
        top_layout.addWidget(self.theme_selector)
        
        # Botón para personalizar temas
        self.customize_theme_btn = QPushButton("Personalizar tema")
        self.customize_theme_btn.clicked.connect(self.show_theme_customizer)
        top_layout.addWidget(self.customize_theme_btn)
        
        # Botón de estadísticas
        self.stats_button = QPushButton("Estadísticas")
        self.stats_button.clicked.connect(self.show_enhanced_stats)
        top_layout.addWidget(self.stats_button)
        
        # Filtro de etiquetas
        self.tag_filter = TagFilterWidget(self.tag_manager)
        self.tag_filter.filter_changed.connect(self.apply_tag_filter)
        top_layout.addWidget(self.tag_filter)
        
        # Añadir paneles al layout principal
        main_layout.addWidget(top_panel)
        main_layout.addWidget(main_panel)
        
        # Panel izquierdo con pestañas para navegación y calendario
        left_tabs = QTabWidget()
        
        # Tab de navegación
        self.navigation_panel = QWidget()
        nav_layout = QVBoxLayout(self.navigation_panel)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        
        # Botones de acción en el panel de navegación
        actions_layout = QHBoxLayout()
        
        self.new_note_btn = QPushButton("Nueva nota")
        self.new_note_btn.clicked.connect(self.create_new_note)
        actions_layout.addWidget(self.new_note_btn)
        
        self.new_task_list_btn = QPushButton("Nueva lista")
        self.new_task_list_btn.clicked.connect(self.create_new_task_list)
        actions_layout.addWidget(self.new_task_list_btn)
        
        self.templates_btn = QPushButton("Plantillas")
        self.templates_btn.clicked.connect(self.show_templates)
        actions_layout.addWidget(self.templates_btn)
        
        nav_layout.addLayout(actions_layout)
        
        # Árbol de navegación
        self.notes_tree = QTreeView()
        self.notes_tree.setHeaderHidden(True)
        self.notes_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.notes_tree.clicked.connect(self.on_note_selected)
        
        self.tree_model = QStandardItemModel()
        self.notes_tree.setModel(self.tree_model)
        
        nav_layout.addWidget(self.notes_tree)
        
        # Añadir tab de navegación
        left_tabs.addTab(self.navigation_panel, "Notas")
        
        # Tab de calendario
        self.calendar_widget = NoteCalendarWidget(self.data_manager)
        self.calendar_widget.note_selected.connect(self.open_note)
        left_tabs.addTab(self.calendar_widget, "Calendario")
        
        # Panel derecho - Editor y paneles adicionales
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear un splitter vertical para dividir editor y panel inferior
        vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Editor principal
        self.editor_container = QStackedWidget()
        vertical_splitter.addWidget(self.editor_container)
        
        # Panel inferior para etiquetas, recordatorios y personalización
        bottom_panel = QTabWidget()
        vertical_splitter.addWidget(bottom_panel)
        
        # Configurar proporciones iniciales del splitter vertical (70% editor, 30% panel inferior)
        vertical_splitter.setSizes([700, 300])
        
        # Añadir el splitter vertical al layout principal derecho
        right_layout.addWidget(vertical_splitter)
        
        # Tab de etiquetas
        tags_tab = QWidget()
        tags_layout = QVBoxLayout(tags_tab)
        self.tag_selector = TagSelectorWidget(self.tag_manager)
        self.tag_selector.tags_changed.connect(self.on_tags_changed)
        tags_layout.addWidget(self.tag_selector)
        bottom_panel.addTab(tags_tab, "Etiquetas")
        
        # Tab de recordatorios
        reminders_tab = QWidget()
        reminders_layout = QVBoxLayout(reminders_tab)
        self.reminder_list = ReminderListWidget(self.reminder_manager)
        self.reminder_list.reminder_changed.connect(self.on_reminder_changed)
        reminders_layout.addWidget(self.reminder_list)
        bottom_panel.addTab(reminders_tab, "Recordatorios")
        
        # Tab de personalización del editor
        editor_tab = QWidget()
        editor_layout = QVBoxLayout(editor_tab)
        
        # Opciones de fuente
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Fuente:"))
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.change_editor_font)
        font_layout.addWidget(self.font_combo)
        
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Tamaño:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24"])
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.currentTextChanged.connect(self.change_editor_font_size)
        font_size_layout.addWidget(self.font_size_combo)
        
        editor_layout.addLayout(font_layout)
        editor_layout.addLayout(font_size_layout)
        
        # Botón para convertir a sticky note
        sticky_btn = QPushButton("Convertir a Sticky Note")
        sticky_btn.clicked.connect(self.convert_to_sticky_note)
        editor_layout.addWidget(sticky_btn)
        
        bottom_panel.addTab(editor_tab, "Personalizar")
        
        # Añadir panel inferior al layout derecho
        right_layout.addWidget(bottom_panel)
        right_layout.setStretch(0, 3)  # Editor ocupa más espacio
        right_layout.setStretch(1, 1)  # Panel inferior más pequeño
        
        # Agregar los paneles al splitter
        self.splitter.addWidget(left_tabs)
    
        self.splitter.addWidget(right_panel)
        
        # Establecer proporciones iniciales del splitter (30% navegación, 70% editor)
        self.splitter.setSizes([300, 700])
        
        # Barra de estado con efectos retro y estadísticas mejoradas
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(0)
        
        # Barra de estado principal
        self.status_bar = QStatusBar()
        status_layout.addWidget(self.status_bar)
        
        # Barra de estadísticas en tiempo real
        self.stats_status_bar = StatsStatusBar(self.enhanced_stats_manager)
        status_layout.addWidget(self.stats_status_bar)
        
        # Widget contenedor para la barra de estado
        status_container = QWidget()
        status_container.setLayout(status_layout)
        main_layout.addWidget(status_container)
        
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("NoteLite iniciado. Cargando notas...")
        
        # NOTA: Barra de herramientas ya no es necesaria debido a la interfaz mejorada
    
    def create_new_note(self):
        """Crea una nueva nota."""
        note_id = self.data_manager.create_note("Nueva nota", "")
        self.add_note_to_tree(note_id, "Nueva nota", "note")
        self.open_note(note_id)
        self.stats_manager.record_note_created()
        self.enhanced_stats_manager.register_note_creation(note_id)
    
    def create_new_task_list(self):
        """Crea una nueva lista de tareas."""
        note_id = self.data_manager.create_note("Nueva lista de tareas", "", note_type="task_list")
        self.add_note_to_tree(note_id, "Nueva lista de tareas", "task_list")
        self.open_note(note_id)
        self.stats_manager.record_note_created()
        self.enhanced_stats_manager.register_note_creation(note_id)
    
    def add_note_to_tree(self, note_id, title, note_type):
        """Añade una nota al árbol de navegación."""
        item = QStandardItem(title)
        item.setData(note_id, Qt.ItemDataRole.UserRole)
        item.setData(note_type, Qt.ItemDataRole.UserRole + 1)
        self.tree_model.appendRow(item)
    
    def on_note_selected(self, index):
        """Maneja la selección de una nota en el árbol."""
        item = self.tree_model.itemFromIndex(index)
        note_id = item.data(Qt.ItemDataRole.UserRole)
        self.open_note(note_id)
    
    def open_note(self, note_id):
        """Abre una nota para edición."""
        note_data = self.data_manager.get_note(note_id)
        
        if not note_data:
            return
        
        # Eliminar el widget editor actual si existe
        while self.editor_container.count() > 0:
            widget = self.editor_container.widget(0)
            self.editor_container.removeWidget(widget)
            widget.deleteLater()
        
        # Crear el widget apropiado según el tipo de nota
        if note_data.get('type') == 'task_list':
            editor = TaskListWidget(note_id, note_data.get('title', ''), note_data.get('content', ''))
            editor.data_changed.connect(self.save_task_list)
        else:
            editor = NoteEditor(note_id, note_data.get('title', ''), note_data.get('content', ''))
            editor.data_changed.connect(self.save_note)
        
        self.editor_container.addWidget(editor)
        self.editor_container.setCurrentWidget(editor)
        
        # Actualizar selector de etiquetas con las etiquetas de esta nota
        self.tag_selector.set_note(note_id)
        
        # Actualizar lista de recordatorios
        self.reminder_list.set_note(note_id)
    
    def save_note(self, note_id, title, content):
        """Guarda los cambios en una nota."""
        # Obtener contenido anterior para estadísticas
        old_note = self.data_manager.get_note(note_id)
        old_content = old_note.get("content", "") if old_note else ""
        
        self.data_manager.update_note(note_id, title, content)
        
        # Actualizar el título en el árbol
        for i in range(self.tree_model.rowCount()):
            item = self.tree_model.item(i, 0)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                item.setText(title)
                break
        
        # Registrar edición
        self.stats_manager.record_note_edited()
        self.enhanced_stats_manager.register_note_edit(note_id)
        self.enhanced_stats_manager.register_text_change(old_content, content)
        
        # Actualizar sticky note si existe
        if note_id in self.sticky_notes and not self.sticky_notes[note_id].isHidden():
            self.sticky_notes[note_id].editor.setPlainText(content)
    
    def save_task_list(self, note_id, title, content):
        """Guarda los cambios en una lista de tareas."""
        # Comprobar si hay tareas completadas nuevas
        old_data = self.data_manager.get_note(note_id)
        old_content = old_data.get('content', [])
        
        # Convertir a lista si es necesario
        if isinstance(old_content, str) and old_content:
            try:
                import json
                old_content = json.loads(old_content)
            except:
                old_content = []
        
        # Contar tareas completadas antes y después
        if isinstance(old_content, list):
            old_completed = sum(1 for task in old_content if task.get('completed', False))
            
            if isinstance(content, list):
                new_completed = sum(1 for task in content if task.get('completed', False))
                
                # Si hay nuevas tareas completadas, registrar
                if new_completed > old_completed:
                    self.stats_manager.record_task_completed()
        
        # Guardar los cambios
        self.data_manager.update_note(note_id, title, content, note_type="task_list")
        
        # Actualizar el título en el árbol
        for i in range(self.tree_model.rowCount()):
            item = self.tree_model.item(i, 0)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                item.setText(title)
                break
                
        # Registrar edición
        self.stats_manager.record_note_edited()
    
    def markdown_preview(self):
        """Muestra una vista previa del markdown con estilos retro."""
        # Verificar que haya un editor activo
        if self.editor_container.count() == 0:
            return
            
        editor = self.editor_container.currentWidget()
        if not hasattr(editor, 'get_content'):
            return
            
        # Obtener contenido y convertir a HTML
        content = editor.get_content()
        html = self.markdown_manager.markdown_to_html(content)
        
        # Mostrar diálogo con vista previa
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("Vista previa de Markdown")
        preview_dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(preview_dialog)
        
        # Usar QTextEdit en lugar de QWebEngineView
        text_preview = QTextEdit()
        text_preview.setReadOnly(True)
        text_preview.setHtml(html)
        layout.addWidget(text_preview)
        
        preview_dialog.exec()
        
    def insert_media(self):
        """Muestra el diálogo para insertar contenido multimedia."""
        # Verificar que haya un editor activo
        if self.editor_container.count() == 0:
            return
            
        editor = self.editor_container.currentWidget()
        if not hasattr(editor, 'insert_html'):
            QMessageBox.warning(self, "Error", "Esta función solo está disponible en notas de texto.")
            return
            
        # Mostrar diálogo de selección de multimedia
        media_dialog = MediaInsertDialog(self.multimedia_manager, self)
        media_dialog.media_selected.connect(lambda filename, width, height, align: 
            self.insert_media_to_note(editor, filename, width, height, align))
        media_dialog.exec()
    
    def insert_media_to_note(self, editor, filename, width, height, align):
        """Inserta un elemento multimedia en la nota actual."""
        # Generar HTML para el elemento multimedia
        html = self.multimedia_manager.get_html_for_media(filename, width, height, align)
        
        # Insertar en el editor
        editor.insert_html(html)
        self.show_status_message(f"Elemento multimedia insertado")
    
    def show_templates(self):
        """Muestra el diálogo de plantillas."""
        templates_dialog = TemplatesDialog(self.templates_manager, self)
        templates_dialog.template_selected.connect(self.create_from_template)
        templates_dialog.exec()
    
    def create_from_template(self, template_id):
        """Crea una nueva nota a partir de una plantilla."""
        note_id = self.templates_manager.create_note_from_template(template_id)
        if note_id:
            # Obtener datos de la nueva nota
            note_data = self.data_manager.get_note(note_id)
            self.add_note_to_tree(note_id, note_data.get('title', 'Nueva nota'), note_data.get('type', 'note'))
            self.open_note(note_id)
            self.stats_manager.record_note_created()
            self.show_status_message(f"Nota creada desde plantilla")
            
    def show_stats(self):
        """Muestra la ventana de estadísticas."""
        # Registrar tiempo de sesión actual
        current_time = time.time()
        session_time = int(current_time - self.session_start_time)
        self.stats_manager.record_session_time(session_time)
        self.session_start_time = current_time  # Reiniciar contador
        
        # Crear y mostrar el widget de estadísticas
        stats_dialog = QDialog(self)
        stats_dialog.setWindowTitle("Estadísticas de NoteLite")
        stats_dialog.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(stats_dialog)
        stats_widget = StatsWidget(self.stats_manager)
        layout.addWidget(stats_widget)
        
        stats_dialog.exec()
        
    def show_status_message(self, message, timeout=3000):
        """Muestra un mensaje en la barra de estado."""
        self.status_bar.showMessage(message, timeout)
    
    def save_current_document(self):
        """Guarda el documento actual."""
        current_widget = self.editor_container.currentWidget()
        if current_widget:
            current_widget.save()
            self.show_retro_message("Documento guardado")
            
    def apply_current_theme(self):
        """Aplica el tema actual de la aplicación."""
        self.theme_manager.apply_theme(QApplication.instance())
        
    def change_theme(self, theme_id):
        """Cambia el tema de la aplicación."""
        if self.theme_manager.apply_theme(QApplication.instance(), theme_id):
            # Mostrar mensaje de cambio de tema
            theme_name = self.theme_manager.THEMES[theme_id]["name"]
            self.show_retro_message(f"Tema cambiado a: {theme_name}")
            # Evitar fuentes problemáticas después de cambiar el tema
            self.avoid_problematic_fonts()
            
    def setup_retro_effects(self):
        """Configura efectos retro adicionales."""
        # Frases nostálgicas aleatorias que aparecen al trabajar
        self.retro_phrases = [
            "Cargando datos...",
            "Insertando diskette...",
            "Espere un momento...",
            "Memoria: 640K debería ser suficiente",
            "Disco duro: 20MB disponibles",
            "Iniciando sistema...",
            "Sector de arranque OK",
            "CRC Check: OK",
            "Presione cualquier tecla para continuar..."
        ]
        
        # Timer para mostrar mensajes retro de vez en cuando
        self.retro_timer = QTimer(self)
        self.retro_timer.timeout.connect(self.show_random_retro_message)
        self.retro_timer.start(30000)  # Cada 30 segundos
        
    def show_random_retro_message(self):
        """Muestra un mensaje retro aleatorio."""
        if random.random() < 0.3:  # 30% de probabilidad
            message = random.choice(self.retro_phrases)
            self.show_retro_message(message)
            
    def show_context_menu(self, position):
        """Muestra el menú contextual para una nota."""
        index = self.notes_tree.indexAt(position)
        if not index.isValid():
            return
        
        item = self.tree_model.itemFromIndex(index)
        note_id = item.data(Qt.ItemDataRole.UserRole)
        note_type = item.data(Qt.ItemDataRole.UserRole + 1)
        
        menu = QMenu(self)
        
        rename_action = menu.addAction("Renombrar")
        rename_action.triggered.connect(lambda: self.rename_note(note_id))
        
        delete_action = menu.addAction("Eliminar")
        delete_action.triggered.connect(lambda: self.delete_note(note_id))
        
        # Submenú de etiquetas
        tags_menu = menu.addMenu("Etiquetas")
        
        # Obtener etiquetas de la nota
        note_data = self.data_manager.get_note(note_id)
        note_tags = note_data.get("tags", []) if note_data else []
        
        # Obtener todas las etiquetas disponibles
        all_tags = self.tag_manager.get_all_tags()
        
        # Añadir opciones para cada etiqueta
        for tag_name in sorted(all_tags.keys()):
            tag_action = tags_menu.addAction(tag_name)
            tag_action.setCheckable(True)
            tag_action.setChecked(tag_name in note_tags)
            
            # Crear closure para capturar tag_name
            def make_toggle_function(tag, note_id):
                return lambda checked: self.toggle_note_tag(note_id, tag, checked)
            
            tag_action.toggled.connect(make_toggle_function(tag_name, note_id))
            
            # Agregar icono si está disponible
            pixmap = self.tag_manager.create_tag_pixmap(tag_name)
            if pixmap:
                tag_action.setIcon(QIcon(pixmap))
        
        # Opción para crear una nueva etiqueta
        tags_menu.addSeparator()
        new_tag_action = tags_menu.addAction("Nueva etiqueta...")
        new_tag_action.triggered.connect(lambda: self.create_tag_for_note(note_id))
        
        # Añadir opción para crear recordatorio
        menu.addSeparator()
        reminder_action = menu.addAction("Crear recordatorio")
        reminder_action.triggered.connect(lambda: self.create_reminder(note_id))
        
        menu.exec(self.notes_tree.mapToGlobal(position))
    
    def delete_note(self, note_id):
        """Elimina una nota."""
        # Confirmar eliminación
        reply = QMessageBox.question(
            self, 
            "Confirmar eliminación", 
            "¿Estás seguro de que quieres eliminar esta nota?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Buscar el índice de la nota en el árbol
            for i in range(self.tree_model.rowCount()):
                item = self.tree_model.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == note_id:
                    self.data_manager.delete_note(note_id)
                    self.tree_model.removeRow(i)
                    break
    
    def rename_note(self, note_id):
        """Cambia el nombre de una nota."""
        note_data = self.data_manager.get_note(note_id)
        if not note_data:
            return
            
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(
            self, "Renombrar nota", "Nuevo nombre:", 
            text=note_data.get('title', '')
        )
        
        if ok and name.strip():
            # Actualizar el título en el gestor de datos
            self.data_manager.update_note(
                note_id, 
                name.strip(), 
                note_data.get('content', ''),
                note_data.get('type', 'note'),
                note_data.get('tags', [])
            )
            
            # Actualizar el título en el árbol
            for i in range(self.tree_model.rowCount()):
                item = self.tree_model.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == note_id:
                    item.setText(name.strip())
                    break
                    
            # Si la nota está abierta, actualizar el título en el editor
            current_widget = self.editor_container.currentWidget()
            if current_widget and hasattr(current_widget, 'note_id') and current_widget.note_id == note_id:
                current_widget.set_title(name.strip())
    
    def on_tags_changed(self, tags):
        """Maneja cambios en las etiquetas de una nota."""
        # Esta señal ya actualiza los datos de la nota, solo necesitamos mostrar un mensaje
        self.show_status_message("Etiquetas actualizadas")
    
    def on_reminder_changed(self):
        """Maneja cambios en los recordatorios."""
        self.show_status_message("Recordatorio actualizado")
    
    def apply_tag_filter(self, tags):
        """Aplica un filtro de etiquetas a la lista de notas."""
        # Limpiar árbol siempre primero para evitar duplicados
        self.tree_model.clear()
        
        # Si no hay etiquetas seleccionadas, mostrar todas las notas
        if not tags:
            self.load_notes(raw=True)  # Usar el parámetro raw=True para evitar limpiar el árbol nuevamente
            self.show_status_message("Mostrando todas las notas")
            return
            
        # Para cada etiqueta, obtener las notas asociadas y añadirlas al árbol
        added_notes = set()
        for tag_name in tags:
            notes_with_tag = self.tag_manager.get_notes_with_tag(tag_name)
            
            for note_id, note_data in notes_with_tag.items():
                if note_id not in added_notes:
                    self.add_note_to_tree(
                        note_id,
                        note_data.get('title', 'Sin título'),
                        note_data.get('type', 'note')
                    )
                    added_notes.add(note_id)
                    
        self.show_status_message(f"Mostrando {len(added_notes)} notas con las etiquetas seleccionadas")
    
    def toggle_note_tag(self, note_id, tag_name, add_tag):
        """Añade o elimina una etiqueta de una nota."""
        if add_tag:
            self.tag_manager.add_tag_to_note(note_id, tag_name)
        else:
            self.tag_manager.remove_tag_from_note(note_id, tag_name)
            
        # Actualizar selector de etiquetas si es la nota actual
        current_widget = self.editor_container.currentWidget()
        if current_widget and hasattr(current_widget, 'note_id') and current_widget.note_id == note_id:
            self.tag_selector.set_note(note_id)
    
    def create_tag_for_note(self, note_id):
        """Crea una nueva etiqueta y la asigna a la nota."""
        from PyQt6.QtWidgets import QInputDialog, QColorDialog
        
        # Solicitar nombre
        name, ok = QInputDialog.getText(self, "Nueva etiqueta", "Nombre de la etiqueta:")
        if not ok or not name.strip():
            return
            
        name = name.strip().lower()
        
        # Verificar si ya existe
        if name in self.tag_manager.get_all_tags():
            # Simplemente añadir a la nota
            self.tag_manager.add_tag_to_note(note_id, name)
            self.tag_selector.set_note(note_id)  # Actualizar vista
            return
            
        # Solicitar color
        color_dialog = QColorDialog(self)
        color = color_dialog.getColor()
        
        if not color.isValid():
            return
            
        # Crear etiqueta
        if self.tag_manager.create_tag(name, color.name()):
            # Añadir a la nota
            self.tag_manager.add_tag_to_note(note_id, name)
            self.tag_selector.set_note(note_id)  # Actualizar vista
            self.show_status_message(f"Etiqueta '{name}' creada y asignada")
    
    def create_reminder(self, note_id):
        """Crea un recordatorio para una nota."""
        dialog = ReminderDialog(self.reminder_manager, note_id, parent=self)
        
        if dialog.exec():
            self.reminder_list.update_reminders_list()
            self.show_status_message("Recordatorio creado")
            
    def show_reminder_notification(self, reminder):
        """Muestra una notificación para un recordatorio."""
        # Obtener datos de la nota asociada para el título del diálogo
        note_data = self.data_manager.get_note(reminder["note_id"])
        note_title = note_data.get("title", "Nota") if note_data else "Nota"
        
        dialog = ReminderNotificationDialog(reminder, self)
        
        # Sobrescribir métodos para manejar las acciones
        original_dismiss = dialog.dismiss_reminder
        original_complete = dialog.complete_reminder
        original_snooze = dialog.snooze_reminder
        
        def dismiss_reminder_override():
            self.reminder_manager.update_reminder(reminder["id"], dismissed=True)
            original_dismiss()
            self.reminder_list.update_reminders_list()  # Actualizar lista si está visible
            
        def complete_reminder_override():
            self.reminder_manager.update_reminder(reminder["id"], completed=True)
            original_complete()
            self.reminder_list.update_reminders_list()  # Actualizar lista si está visible
            
        def snooze_reminder_override():
            # Esta función es llamada después de que el usuario elige un tiempo
            times = {"5 minutos": 5, "15 minutos": 15, "30 minutos": 30, "1 hora": 60, "3 horas": 180}
            choice = dialog.sender().text()
            minutes = times.get(choice, 15)  # Por defecto 15 minutos
            
            # Calcular nueva fecha y hora
            now = datetime.datetime.now()
            new_time = now + datetime.timedelta(minutes=minutes)
            
            # Actualizar recordatorio
            self.reminder_manager.update_reminder(reminder["id"], datetime_str=new_time.isoformat())
            original_snooze()
            self.reminder_list.update_reminders_list()  # Actualizar lista si está visible
            
        # Reemplazar métodos
        dialog.dismiss_reminder = dismiss_reminder_override
        dialog.complete_reminder = complete_reminder_override
        dialog.snooze_reminder = snooze_reminder_override
        
        # Mostrar diálogo
        dialog.setWindowTitle(f"Recordatorio: {note_title}")
        dialog.exec()
            
    def load_notes(self, raw=False):
        """Carga las notas existentes.
        
        Args:
            raw: Si es True, no limpia el árbol antes de cargar las notas
        """
        if not raw:
            self.tree_model.clear()
            
        notes = self.data_manager.get_all_notes()   
        for note_id, note_data in notes.items():
            self.add_note_to_tree(
                note_id, 
                note_data.get('title', 'Sin título'), 
                note_data.get('type', 'note')
            )
            
    def avoid_problematic_fonts(self):
        """Evita el uso de fuentes problemáticas que causan errores DirectWrite."""
        problematic_fonts = ["Small Fonts", "System", "MS Sans Serif"]
        app = QApplication.instance()
        
        # Establecer fuente predeterminada
        default_font = QFont("Segoe UI", 10)  # Fuente moderna y confiable
        app.setFont(default_font)
        
        # Asegurar que los editores usen fuentes seguras
        for i in range(self.editor_container.count()):
            widget = self.editor_container.widget(i)
            if hasattr(widget, "editor"):
                current_font = widget.editor.font()
                if current_font.family() in problematic_fonts:
                    safe_font = QFont("Consolas", current_font.pointSize())
                    widget.editor.setFont(safe_font)
            elif hasattr(widget, "task_edit"):
                current_font = widget.task_edit.font()
                if current_font.family() in problematic_fonts:
                    safe_font = QFont("Consolas", current_font.pointSize())
                    widget.task_edit.setFont(safe_font)

    def show_stats(self):
        """Muestra la ventana de estadísticas básicas."""
        stats_dialog = QDialog(self)
        stats_dialog.setWindowTitle("Estadísticas de NoteLite")
        stats_dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(stats_dialog)
        
        # Widget de estadísticas
        stats_widget = StatsWidget(self.stats_manager)
        layout.addWidget(stats_widget)
        
        # Botón de cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(stats_dialog.accept)
        layout.addWidget(close_btn)
        
        stats_dialog.exec()
        
    def show_enhanced_stats(self):
        """Muestra la ventana de estadísticas mejoradas."""
        stats_dialog = QDialog(self)
        stats_dialog.setWindowTitle("Estadísticas Avanzadas de NoteLite")
        stats_dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(stats_dialog)
        
        # Widget de estadísticas mejoradas
        stats_widget = EnhancedStatsWidget(self.enhanced_stats_manager)
        layout.addWidget(stats_widget)
        
        # Botón de cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(stats_dialog.accept)
        layout.addWidget(close_btn)
        
        # Al cerrar el diálogo, guardar estadísticas
        stats_dialog.finished.connect(self.enhanced_stats_manager.save_stats)
        
        stats_dialog.exec()
    
    def show_theme_customizer(self):
        """Muestra el diálogo para personalizar temas."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Personalizar tema")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Selección de tema personalizable
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema a personalizar:"))
        
        theme_combo = QComboBox()
        editable_themes = {}
        
        # Añadir solo temas editables
        for theme_id, theme_data in self.theme_manager.THEMES.items():
            if theme_data.get("editable", False):
                theme_combo.addItem(theme_data["name"], theme_id)
                editable_themes[theme_id] = theme_data
                
        theme_layout.addWidget(theme_combo)
        layout.addLayout(theme_layout)
        
        # Campos para nombre del tema
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nombre:"))
        name_edit = QLineEdit()
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        # Selección de colores
        colors_group = QGroupBox("Colores del tema")
        colors_layout = QGridLayout(colors_group)
        
        # Campos para cada color
        color_fields = {}
        color_buttons = {}
        
        row = 0
        for color_key, color_name in [
            ("background", "Fondo"),
            ("foreground", "Primer plano"),
            ("accent", "Acento"),
            ("secondary", "Secundario"),
            ("text", "Texto")
        ]:
            colors_layout.addWidget(QLabel(f"{color_name}:"), row, 0)
            
            color_edit = QLineEdit()
            color_fields[color_key] = color_edit
            colors_layout.addWidget(color_edit, row, 1)
            
            color_btn = QPushButton("Seleccionar")
            color_buttons[color_key] = color_btn
            colors_layout.addWidget(color_btn, row, 2)
            
            row += 1
        
        layout.addWidget(colors_group)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Función para actualizar los campos con los datos del tema seleccionado
        def update_theme_fields():
            theme_id = theme_combo.currentData()
            if theme_id in editable_themes:
                theme_data = editable_themes[theme_id]
                name_edit.setText(theme_data["name"])
                
                if "colors" in theme_data:
                    for color_key, color_field in color_fields.items():
                        if color_key in theme_data["colors"]:
                            color_field.setText(theme_data["colors"][color_key])
        
        # Función para seleccionar un color
        def create_color_selector(color_key):
            def select_color():
                current_color = QColor(color_fields[color_key].text()) if color_fields[color_key].text() else QColor("#FFFFFF")
                color = QColorDialog.getColor(current_color, dialog)
                if color.isValid():
                    color_fields[color_key].setText(color.name())
            return select_color
        
        # Conectar señales
        theme_combo.currentIndexChanged.connect(update_theme_fields)
        for color_key, color_btn in color_buttons.items():
            color_btn.clicked.connect(create_color_selector(color_key))
        
        # Inicializar campos
        update_theme_fields()
        
        # Ejecutar diálogo
        if dialog.exec() == QDialog.DialogCode.Accepted:
            theme_id = theme_combo.currentData()
            theme_name = name_edit.text()
            
            # Recoger colores
            colors = {}
            for color_key, color_field in color_fields.items():
                colors[color_key] = color_field.text()
            
            # Guardar tema personalizado
            self.theme_manager.save_custom_theme(theme_id, theme_name, colors)
            
            # Aplicar el tema si está seleccionado
            if self.theme_manager.current_theme == theme_id:
                self.theme_manager.apply_theme(QApplication.instance(), theme_id)
    
    def change_editor_font(self, font):
        """Cambia la fuente del editor actual."""
        current_widget = self.editor_container.currentWidget()
        if not current_widget:
            return
            
        # Obtener el tamaño actual para mantenerlo
        try:
            if hasattr(current_widget, "editor") and hasattr(current_widget.editor, "font"):
                size = current_widget.editor.font().pointSize()
                editor = current_widget.editor
            elif hasattr(current_widget, "task_edit") and hasattr(current_widget.task_edit, "font"):
                size = current_widget.task_edit.font().pointSize()
                editor = current_widget.task_edit
            elif hasattr(current_widget, "document"):
                size = current_widget.document().defaultFont().pointSize()
                editor = current_widget
            else:
                return
                
            # Aplicar la nueva fuente manteniendo el tamaño
            new_font = QFont(font)
            new_font.setPointSize(size)
            
            # Aplicar al editor
            if hasattr(editor, "setFont"):
                editor.setFont(new_font)
            
            # Actualizar el selector de fuente para reflejar el cambio
            self.font_combo.setCurrentFont(new_font)
            
            # Guardar la configuración
            self.show_status_message(f"Fuente cambiada a {font.family()}")
        except Exception as e:
            self.show_status_message(f"Error al cambiar la fuente: {str(e)}")
    
    def change_editor_font_size(self, size_text):
        """Cambia el tamaño de fuente del editor actual."""
        try:
            size = int(size_text)
            current_widget = self.editor_container.currentWidget()
            if not current_widget:
                return
                
            # Identificar el editor correcto
            if hasattr(current_widget, "editor") and hasattr(current_widget.editor, "font"):
                editor = current_widget.editor
                old_font = editor.font()
            elif hasattr(current_widget, "task_edit") and hasattr(current_widget.task_edit, "font"):
                editor = current_widget.task_edit
                old_font = editor.font()
            elif hasattr(current_widget, "document"):
                editor = current_widget
                old_font = editor.document().defaultFont()
            else:
                return
                
            # Aplicar el nuevo tamaño a la fuente actual
            new_font = QFont(old_font)
            new_font.setPointSize(size)
            
            # Aplicar al editor
            if hasattr(editor, "setFont"):
                editor.setFont(new_font)
            
            # Actualizar el selector de tamaño para reflejar el cambio
            self.font_size_combo.setCurrentText(str(size))
            
            # Mostrar mensaje
            self.show_status_message(f"Tamaño de fuente cambiado a {size}")
        except (ValueError, TypeError) as e:
            self.show_status_message(f"Error al cambiar tamaño de fuente: {str(e)}")
            pass
    
    def convert_to_sticky_note(self):
        """Convierte la nota actual en una sticky note flotante."""
        current_widget = self.editor_container.currentWidget()
        if not current_widget or not hasattr(current_widget, "note_id"):
            return
            
        note_id = current_widget.note_id
        note_data = self.data_manager.get_note(note_id)
        
        if note_data:
            # Crear sticky note
            sticky = create_sticky_note(
                note_id,
                note_data.get("title", "Sin título"),
                note_data.get("content", "")
            )
            
            # Conectar señales
            sticky.note_closed.connect(self.on_sticky_note_closed)
            sticky.note_content_changed.connect(self.on_sticky_note_content_changed)
            
            # Guardar referencia
            self.sticky_notes[note_id] = sticky
    
    def on_sticky_note_closed(self, note_id):
        """Manejador para cuando se cierra una sticky note."""
        if note_id in self.sticky_notes:
            del self.sticky_notes[note_id]
    
    def on_sticky_note_content_changed(self, note_id, content):
        """Manejador para cuando cambia el contenido de una sticky note."""
        # Obtener datos actuales de la nota
        note_data = self.data_manager.get_note(note_id)
        if note_data:
            # Actualizar nota con nuevo contenido
            self.data_manager.update_note(
                note_id,
                note_data.get("title", "Sin título"),
                content,
                note_data.get("type", "note"),
                note_data.get("tags", [])
            )
            
            # Actualizar editor si está abierto
            current_widget = self.editor_container.currentWidget()
            if current_widget and hasattr(current_widget, "note_id") and current_widget.note_id == note_id:
                if hasattr(current_widget, "editor") and hasattr(current_widget.editor, "setPlainText"):
                    current_widget.editor.setPlainText(content)

def main():
    app = QApplication(sys.argv)
    
    # Aplicar estilos
    style_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "style.qss")
    if os.path.exists(style_file):
        with open(style_file, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    
    ex = NoteLiteApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
