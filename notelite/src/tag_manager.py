#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de etiquetas para NoteLite.
Permite organizar y filtrar notas mediante un sistema de etiquetas.
"""

import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QListWidget, QListWidgetItem,
                            QPushButton, QColorDialog, QMenu, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor, QPixmap


class TagManager:
    """
    Gestor de etiquetas para organizar y clasificar notas.
    """
    
    def __init__(self, data_manager):
        """Inicializa el gestor de etiquetas."""
        self.data_manager = data_manager
        self.tags_dir = os.path.join(os.path.expanduser("~"), "NoteLite", "tags")
        
        # Asegurar que el directorio existe
        os.makedirs(self.tags_dir, exist_ok=True)
        
        # Cargar etiquetas existentes
        self.tags = self._load_tags()
        
    def _load_tags(self):
        """Carga las etiquetas desde el sistema."""
        tags_file = os.path.join(self.tags_dir, "tags.json")
        
        if os.path.exists(tags_file):
            try:
                with open(tags_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al cargar etiquetas: {e}")
                return {}
        else:
            # Crear etiquetas por defecto
            default_tags = {
                "importante": {"color": "#FF5733", "icon": "star.png"},
                "personal": {"color": "#33A8FF", "icon": "user.png"},
                "trabajo": {"color": "#33FF57", "icon": "briefcase.png"},
                "idea": {"color": "#FFD700", "icon": "lightbulb.png"},
                "pendiente": {"color": "#8A2BE2", "icon": "clock.png"}
            }
            self._save_tags(default_tags)
            return default_tags
    
    def _save_tags(self, tags_data):
        """Guarda las etiquetas en el sistema."""
        tags_file = os.path.join(self.tags_dir, "tags.json")
        
        try:
            with open(tags_file, 'w', encoding='utf-8') as f:
                json.dump(tags_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar etiquetas: {e}")
            return False
    
    def get_all_tags(self):
        """Obtiene todas las etiquetas disponibles."""
        return self.tags
    
    def get_tag(self, tag_name):
        """Obtiene información de una etiqueta específica."""
        return self.tags.get(tag_name)
    
    def create_tag(self, tag_name, color="#CCCCCC", icon=None):
        """Crea una nueva etiqueta."""
        if tag_name in self.tags:
            return False
        
        self.tags[tag_name] = {
            "color": color,
            "icon": icon or "tag.png"
        }
        
        return self._save_tags(self.tags)
    
    def update_tag(self, tag_name, new_name=None, color=None, icon=None):
        """Actualiza una etiqueta existente."""
        if tag_name not in self.tags:
            return False
        
        if new_name and new_name != tag_name:
            # Renombrar etiqueta
            tag_data = self.tags[tag_name]
            del self.tags[tag_name]
            self.tags[new_name] = tag_data
            
            # Actualizar las notas que usan esta etiqueta
            self._update_notes_with_tag(tag_name, new_name)
            
        if color:
            self.tags[new_name or tag_name]["color"] = color
            
        if icon:
            self.tags[new_name or tag_name]["icon"] = icon
        
        return self._save_tags(self.tags)
    
    def delete_tag(self, tag_name):
        """Elimina una etiqueta."""
        if tag_name not in self.tags:
            return False
        
        # Eliminar etiqueta de todas las notas que la usan
        self._remove_tag_from_notes(tag_name)
        
        # Eliminar la etiqueta
        del self.tags[tag_name]
        
        return self._save_tags(self.tags)
    
    def _update_notes_with_tag(self, old_tag, new_tag):
        """Actualiza las notas que usan una etiqueta renombrada."""
        all_notes = self.data_manager.get_all_notes()
        
        for note_id, note_data in all_notes.items():
            if "tags" in note_data:
                if old_tag in note_data["tags"]:
                    # Reemplazar con la nueva etiqueta
                    note_data["tags"].remove(old_tag)
                    note_data["tags"].append(new_tag)
                    self.data_manager.update_note(
                        note_id, 
                        note_data.get("title", ""),
                        note_data.get("content", ""),
                        note_data.get("type", "note"),
                        note_data["tags"]
                    )
    
    def _remove_tag_from_notes(self, tag_name):
        """Elimina una etiqueta de todas las notas que la usan."""
        all_notes = self.data_manager.get_all_notes()
        
        for note_id, note_data in all_notes.items():
            if "tags" in note_data:
                if tag_name in note_data["tags"]:
                    # Quitar la etiqueta
                    note_data["tags"].remove(tag_name)
                    self.data_manager.update_note(
                        note_id, 
                        note_data.get("title", ""),
                        note_data.get("content", ""),
                        note_data.get("type", "note"),
                        note_data["tags"]
                    )
    
    def add_tag_to_note(self, note_id, tag_name):
        """Añade una etiqueta a una nota."""
        if tag_name not in self.tags:
            return False
        
        note_data = self.data_manager.get_note(note_id)
        if not note_data:
            return False
        
        # Asegurar que tags es una lista
        if "tags" in note_data:
            if isinstance(note_data["tags"], list):
                tags = note_data["tags"]
            else:
                tags = []
        else:
            tags = []
        
        if tag_name not in tags:
            tags.append(tag_name)
        
        try:
            return self.data_manager.update_note(
                note_id, 
                note_data.get("title", ""),
                note_data.get("content", ""),
                note_data.get("type", "note"),
                tags
            )
        except Exception as e:
            print(f"Error al añadir etiqueta: {e}")
            return False
    
    def remove_tag_from_note(self, note_id, tag_name):
        """Elimina una etiqueta de una nota."""
        note_data = self.data_manager.get_note(note_id)
        if not note_data:
            return False
        
        # Asegurar que tags es una lista
        if "tags" in note_data:
            if isinstance(note_data["tags"], list):
                tags = note_data["tags"]
            else:
                tags = []
        else:
            tags = []
        
        if tag_name in tags:
            tags.remove(tag_name)
        
        try:
            return self.data_manager.update_note(
                note_id, 
                note_data.get("title", ""),
                note_data.get("content", ""),
                note_data.get("type", "note"),
                tags
            )
        except Exception as e:
            print(f"Error al eliminar etiqueta: {e}")
            return False
    
    def get_notes_with_tag(self, tag_name):
        """Obtiene todas las notas que tienen una etiqueta específica."""
        all_notes = self.data_manager.get_all_notes()
        
        return {
            note_id: note_data for note_id, note_data in all_notes.items()
            if "tags" in note_data and tag_name in note_data["tags"]
        }
    
    def create_tag_pixmap(self, tag_name, size=16):
        """Crea un QPixmap para una etiqueta."""
        tag_data = self.get_tag(tag_name)
        if not tag_data:
            return None
        
        # Crear pixmap con el color de la etiqueta
        color = QColor(tag_data.get("color", "#CCCCCC"))
        pixmap = QPixmap(size, size)
        pixmap.fill(color)
        
        return pixmap


class TagSelectorWidget(QWidget):
    """Widget para seleccionar etiquetas para una nota."""
    
    tags_changed = pyqtSignal(list)  # Emitida cuando se cambian las etiquetas
    
    def __init__(self, tag_manager, parent=None):
        super().__init__(parent)
        self.tag_manager = tag_manager
        self.note_id = None
        self.note_tags = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Etiquetas")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Campo para añadir nueva etiqueta
        add_layout = QHBoxLayout()
        
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Nueva etiqueta...")
        add_layout.addWidget(self.tag_input)
        
        add_btn = QPushButton("+")
        add_btn.setMaximumWidth(30)
        add_btn.clicked.connect(self.add_tag)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # Lista de etiquetas disponibles
        self.tags_list = QListWidget()
        self.tags_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tags_list.customContextMenuRequested.connect(self.show_tag_context_menu)
        layout.addWidget(self.tags_list)
        
        # Lista de etiquetas de la nota actual
        current_tags_label = QLabel("Etiquetas de esta nota:")
        layout.addWidget(current_tags_label)
        
        self.note_tags_list = QListWidget()
        self.note_tags_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.note_tags_list.customContextMenuRequested.connect(self.show_note_tag_context_menu)
        layout.addWidget(self.note_tags_list)
        
        # Cargar etiquetas
        self.load_all_tags()
        
    def load_all_tags(self):
        """Carga todas las etiquetas disponibles."""
        self.tags_list.clear()
        
        all_tags = self.tag_manager.get_all_tags()
        for tag_name, tag_data in all_tags.items():
            item = QListWidgetItem(tag_name)
            item.setIcon(QIcon(self.tag_manager.create_tag_pixmap(tag_name)))
            self.tags_list.addItem(item)
        
        self.tags_list.sortItems()
    
    def set_note(self, note_id):
        """Establece la nota actual y carga sus etiquetas."""
        self.note_id = note_id
        
        if not note_id:
            self.note_tags = []
            self.note_tags_list.clear()
            return
        
        # Cargar etiquetas de la nota
        note_data = self.tag_manager.data_manager.get_note(note_id)
        if note_data and "tags" in note_data:
            self.note_tags = note_data["tags"]
        else:
            self.note_tags = []
            
        # Actualizar lista
        self.update_note_tags_list()
    
    def update_note_tags_list(self):
        """Actualiza la lista de etiquetas de la nota actual."""
        self.note_tags_list.clear()
        
        for tag_name in self.note_tags:
            item = QListWidgetItem(tag_name)
            item.setIcon(QIcon(self.tag_manager.create_tag_pixmap(tag_name)))
            self.note_tags_list.addItem(item)
    
    def add_tag(self):
        """Añade una nueva etiqueta."""
        tag_name = self.tag_input.text().strip().lower()
        
        if not tag_name:
            return
            
        # Verificar si la etiqueta ya existe
        all_tags = self.tag_manager.get_all_tags()
        if tag_name not in all_tags:
            # Crear nueva etiqueta
            color_dialog = QColorDialog(self)
            color = color_dialog.getColor()
            
            if color.isValid():
                self.tag_manager.create_tag(tag_name, color.name())
                self.load_all_tags()
        
        # Añadir a la nota actual si existe
        if self.note_id:
            self.tag_manager.add_tag_to_note(self.note_id, tag_name)
            
            # Actualizar lista de etiquetas de la nota
            if tag_name not in self.note_tags:
                self.note_tags.append(tag_name)
                self.update_note_tags_list()
                self.tags_changed.emit(self.note_tags)
        
        # Limpiar campo
        self.tag_input.clear()
    
    def show_tag_context_menu(self, position):
        """Muestra el menú contextual para una etiqueta."""
        item = self.tags_list.itemAt(position)
        if not item:
            return
            
        tag_name = item.text()
        
        menu = QMenu(self)
        
        # Opción para añadir a la nota actual
        if self.note_id and tag_name not in self.note_tags:
            add_action = menu.addAction("Añadir a esta nota")
            add_action.triggered.connect(lambda: self.add_tag_to_note(tag_name))
        
        # Opción para editar
        edit_action = menu.addAction("Editar etiqueta")
        edit_action.triggered.connect(lambda: self.edit_tag(tag_name))
        
        # Opción para eliminar
        delete_action = menu.addAction("Eliminar etiqueta")
        delete_action.triggered.connect(lambda: self.delete_tag(tag_name))
        
        menu.exec(self.tags_list.mapToGlobal(position))
    
    def show_note_tag_context_menu(self, position):
        """Muestra el menú contextual para una etiqueta de la nota."""
        item = self.note_tags_list.itemAt(position)
        if not item:
            return
            
        tag_name = item.text()
        
        menu = QMenu(self)
        
        # Opción para quitar de la nota
        remove_action = menu.addAction("Quitar de esta nota")
        remove_action.triggered.connect(lambda: self.remove_tag_from_note(tag_name))
        
        menu.exec(self.note_tags_list.mapToGlobal(position))
    
    def add_tag_to_note(self, tag_name):
        """Añade una etiqueta a la nota actual."""
        if not self.note_id:
            return
            
        if self.tag_manager.add_tag_to_note(self.note_id, tag_name):
            if tag_name not in self.note_tags:
                self.note_tags.append(tag_name)
                self.update_note_tags_list()
                self.tags_changed.emit(self.note_tags)
    
    def remove_tag_from_note(self, tag_name):
        """Elimina una etiqueta de la nota actual."""
        if not self.note_id:
            return
            
        if self.tag_manager.remove_tag_from_note(self.note_id, tag_name):
            if tag_name in self.note_tags:
                self.note_tags.remove(tag_name)
                self.update_note_tags_list()
                self.tags_changed.emit(self.note_tags)
    
    def edit_tag(self, tag_name):
        """Edita una etiqueta existente."""
        # Mostrar diálogo de edición
        dialog = TagEditDialog(self.tag_manager, tag_name, self)
        
        if dialog.exec():
            # Actualizar vistas
            self.load_all_tags()
            self.update_note_tags_list()
    
    def delete_tag(self, tag_name):
        """Elimina una etiqueta."""
        # Confirmar eliminación
        from PyQt6.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar la etiqueta '{tag_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.tag_manager.delete_tag(tag_name):
                # Actualizar vistas
                self.load_all_tags()
                
                # Actualizar lista de etiquetas de la nota si es necesario
                if tag_name in self.note_tags:
                    self.note_tags.remove(tag_name)
                    self.update_note_tags_list()
                    self.tags_changed.emit(self.note_tags)


class TagEditDialog(QDialog):
    """Diálogo para editar una etiqueta."""
    
    def __init__(self, tag_manager, tag_name, parent=None):
        super().__init__(parent)
        self.tag_manager = tag_manager
        self.tag_name = tag_name
        self.tag_data = tag_manager.get_tag(tag_name)
        
        self.setWindowTitle(f"Editar etiqueta: {tag_name}")
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        form_layout = QHBoxLayout()
        
        # Campo para el nombre
        form_layout.addWidget(QLabel("Nombre:"))
        self.name_input = QLineEdit(self.tag_name)
        form_layout.addWidget(self.name_input)
        
        # Selector de color
        self.color_btn = QPushButton("")
        self.color_btn.setMinimumWidth(50)
        if self.tag_data:
            color = self.tag_data.get("color", "#CCCCCC")
            self.color_btn.setStyleSheet(f"background-color: {color};")
        self.color_btn.clicked.connect(self.choose_color)
        form_layout.addWidget(self.color_btn)
        
        layout.addLayout(form_layout)
        
        # Vista previa
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Vista previa:"))
        
        self.preview_label = QLabel(self.tag_name)
        if self.tag_data:
            pixmap = self.tag_manager.create_tag_pixmap(self.tag_name, 24)
            self.preview_label.setPixmap(pixmap)
        preview_layout.addWidget(self.preview_label)
        
        layout.addLayout(preview_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_tag)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def choose_color(self):
        """Abre el diálogo de selección de color."""
        current_color = QColor(self.tag_data.get("color", "#CCCCCC"))
        
        color_dialog = QColorDialog(self)
        color_dialog.setCurrentColor(current_color)
        new_color = color_dialog.getColor()
        
        if new_color.isValid():
            # Actualizar botón
            self.color_btn.setStyleSheet(f"background-color: {new_color.name()};")
            
            # Actualizar vista previa
            self.tag_data["color"] = new_color.name()
            pixmap = QPixmap(24, 24)
            pixmap.fill(new_color)
            self.preview_label.setText("")
            self.preview_label.setPixmap(pixmap)
    
    def save_tag(self):
        """Guarda los cambios en la etiqueta."""
        new_name = self.name_input.text().strip()
        
        if not new_name:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "El nombre de la etiqueta no puede estar vacío.")
            return
        
        # Si se cambió el nombre, verificar que no existe
        if new_name != self.tag_name and new_name in self.tag_manager.get_all_tags():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Ya existe una etiqueta con el nombre '{new_name}'.")
            return
        
        # Guardar cambios
        if self.tag_manager.update_tag(
            self.tag_name,
            new_name=new_name,
            color=self.tag_data.get("color")
        ):
            self.accept()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "No se pudo guardar la etiqueta.")


class TagFilterWidget(QWidget):
    """Widget para filtrar notas por etiquetas."""
    
    filter_changed = pyqtSignal(list)  # Emitida cuando cambia el filtro
    
    def __init__(self, tag_manager, parent=None):
        super().__init__(parent)
        self.tag_manager = tag_manager
        self.selected_tags = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Etiqueta
        layout.addWidget(QLabel("Filtrar por:"))
        
        # Lista de etiquetas seleccionadas
        self.filter_list = QListWidget()
        self.filter_list.setMaximumHeight(30)
        self.filter_list.setFlow(QListWidget.Flow.LeftToRight)
        self.filter_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.filter_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.filter_list.itemClicked.connect(self.remove_filter_tag)
        layout.addWidget(self.filter_list)
        
        # Botón para mostrar todas las etiquetas
        add_filter_btn = QPushButton("+")
        add_filter_btn.setMaximumWidth(30)
        add_filter_btn.clicked.connect(self.show_tag_selector)
        layout.addWidget(add_filter_btn)
        
        # Botón para limpiar todos los filtros
        clear_btn = QPushButton("Limpiar")
        clear_btn.setMaximumWidth(60)
        clear_btn.clicked.connect(self.clear_filters)
        layout.addWidget(clear_btn)
    
    def show_tag_selector(self):
        """Muestra el selector de etiquetas para filtrar."""
        all_tags = self.tag_manager.get_all_tags()
        
        # Crear menú con todas las etiquetas
        menu = QMenu(self)
        
        for tag_name in sorted(all_tags.keys()):
            action = menu.addAction(tag_name)
            action.setCheckable(True)
            action.setChecked(tag_name in self.selected_tags)
            
            # Añadir icono
            pixmap = self.tag_manager.create_tag_pixmap(tag_name)
            if pixmap:
                action.setIcon(QIcon(pixmap))
        
        # Conectar acciones
        menu.triggered.connect(self.toggle_filter_tag)
        
        # Mostrar menú
        menu.exec(self.mapToGlobal(self.rect().bottomRight()))
    
    def toggle_filter_tag(self, action):
        """Alterna una etiqueta en el filtro."""
        tag_name = action.text()
        
        if action.isChecked():
            # Añadir etiqueta al filtro
            if tag_name not in self.selected_tags:
                self.selected_tags.append(tag_name)
        else:
            # Quitar etiqueta del filtro
            if tag_name in self.selected_tags:
                self.selected_tags.remove(tag_name)
        
        # Actualizar vista
        self.update_filter_list()
        
        # Emitir señal
        self.filter_changed.emit(self.selected_tags)
    
    def remove_filter_tag(self, item):
        """Elimina una etiqueta del filtro al hacer clic en ella."""
        text = item.text().strip()
        # Extraer solo el nombre de la etiqueta (quitar el ícono X)
        tag_name = text.split(" ✕")[0].strip()
        
        if tag_name in self.selected_tags:
            self.selected_tags.remove(tag_name)
            
            # Actualizar vista
            self.update_filter_list()
            
            # Emitir señal
            self.filter_changed.emit(self.selected_tags)
    
    def update_filter_list(self):
        """Actualiza la lista de etiquetas seleccionadas para el filtro."""
        self.filter_list.clear()
        
        for tag_name in self.selected_tags:
            item = QListWidgetItem(f" {tag_name} ✕")
            pixmap = self.tag_manager.create_tag_pixmap(tag_name)
            if pixmap:
                item.setIcon(QIcon(pixmap))
            self.filter_list.addItem(item)
    
    def clear_filters(self):
        """Limpia todos los filtros."""
        self.selected_tags = []
        self.filter_list.clear()
        self.filter_changed.emit([])
