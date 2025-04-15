#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget de calendario para NoteLite.
Permite visualizar notas asignadas a fechas.
"""

import os
import datetime
from PyQt6.QtWidgets import (
    QWidget, QCalendarWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QListWidget, QListWidgetItem, QDialog,
    QCheckBox, QDateEdit, QTimeEdit, QFormLayout, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QBrush, QTextCharFormat

class NoteCalendarWidget(QWidget):
    """Widget de calendario para visualizar notas asignadas a fechas."""
    
    note_selected = pyqtSignal(str)  # ID de la nota seleccionada
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.date_notes = {}  # Diccionario de notas por fecha {fecha_str: [note_ids]}
        
        self.setup_ui()
        self.load_dated_notes()
        
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        
        # Calendario
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_clicked)
        layout.addWidget(self.calendar)
        
        # Lista de notas para la fecha seleccionada
        notes_layout = QVBoxLayout()
        notes_label = QLabel("Notas para esta fecha:")
        notes_layout.addWidget(notes_label)
        
        self.notes_list = QListWidget()
        self.notes_list.itemDoubleClicked.connect(self.on_note_selected)
        notes_layout.addWidget(self.notes_list)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.assign_btn = QPushButton("Asignar nota a esta fecha")
        self.assign_btn.clicked.connect(self.assign_note_to_date)
        buttons_layout.addWidget(self.assign_btn)
        
        self.remove_btn = QPushButton("Eliminar asignación")
        self.remove_btn.clicked.connect(self.remove_date_assignment)
        self.remove_btn.setEnabled(False)
        buttons_layout.addWidget(self.remove_btn)
        
        notes_layout.addLayout(buttons_layout)
        layout.addLayout(notes_layout)
    
    def load_dated_notes(self):
        """Carga todas las notas con fechas asignadas."""
        self.date_notes = {}
        
        # Obtener todas las notas
        all_notes = self.data_manager.get_all_notes()
        for note_id, note_data in all_notes.items():
            # Verificar si tiene recordatorios o fechas asignadas
            if "reminders" in note_data:
                for reminder in note_data["reminders"]:
                    # Extraer solo la fecha del recordatorio (sin hora)
                    try:
                        reminder_date = reminder["datetime"].split()[0]  # Formato YYYY-MM-DD
                        if reminder_date not in self.date_notes:
                            self.date_notes[reminder_date] = []
                        if note_id not in self.date_notes[reminder_date]:
                            self.date_notes[reminder_date].append(note_id)
                    except (KeyError, IndexError):
                        pass
            
            # Verificar si tiene fecha asignada directamente
            if "date" in note_data:
                date_str = note_data["date"]
                if date_str not in self.date_notes:
                    self.date_notes[date_str] = []
                if note_id not in self.date_notes[date_str]:
                    self.date_notes[date_str].append(note_id)
        
        # Actualizar el formato del calendario
        self.update_calendar_format()
    
    def update_calendar_format(self):
        """Actualiza el formato del calendario para mostrar fechas con notas."""
        # Restablecer formato
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # Destacar fechas con notas
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QBrush(QColor(173, 216, 230)))  # Azul claro
        
        for date_str in self.date_notes.keys():
            try:
                year, month, day = map(int, date_str.split('-'))
                date = QDate(year, month, day)
                self.calendar.setDateTextFormat(date, highlight_format)
            except (ValueError, IndexError):
                pass
    
    def on_date_clicked(self, date):
        """Manejador para cuando se hace clic en una fecha del calendario."""
        # Convertir QDate a cadena YYYY-MM-DD
        date_str = date.toString("yyyy-MM-dd")
        
        # Limpiar lista de notas
        self.notes_list.clear()
        self.remove_btn.setEnabled(False)
        
        # Verificar si hay notas para esta fecha
        if date_str in self.date_notes and self.date_notes[date_str]:
            for note_id in self.date_notes[date_str]:
                note_data = self.data_manager.get_note(note_id)
                if note_data:
                    item = QListWidgetItem(note_data.get("title", "Sin título"))
                    item.setData(Qt.ItemDataRole.UserRole, note_id)
                    self.notes_list.addItem(item)
    
    def on_note_selected(self, item):
        """Manejador para cuando se selecciona una nota de la lista."""
        note_id = item.data(Qt.ItemDataRole.UserRole)
        self.note_selected.emit(note_id)
        self.remove_btn.setEnabled(True)
    
    def assign_note_to_date(self):
        """Abre un diálogo para asignar una nota a la fecha seleccionada."""
        date = self.calendar.selectedDate()
        date_str = date.toString("yyyy-MM-dd")
        
        dialog = DateAssignmentDialog(self.data_manager, date_str, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_dated_notes()
            self.on_date_clicked(date)
    
    def remove_date_assignment(self):
        """Elimina la asignación de fecha para la nota seleccionada."""
        selected_items = self.notes_list.selectedItems()
        if not selected_items:
            return
            
        note_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        date = self.calendar.selectedDate()
        date_str = date.toString("yyyy-MM-dd")
        
        note_data = self.data_manager.get_note(note_id)
        if not note_data:
            return
            
        # Eliminar fecha asignada
        if "date" in note_data and note_data["date"] == date_str:
            note_data_copy = note_data.copy()
            note_data_copy.pop("date", None)
            self.data_manager.update_note(
                note_id, 
                note_data_copy.get("title", ""), 
                note_data_copy.get("content", ""),
                note_data_copy.get("type", "note"),
                note_data_copy.get("tags", [])
            )
            
            # Actualizar vistas
            self.load_dated_notes()
            self.on_date_clicked(date)


class DateAssignmentDialog(QDialog):
    """Diálogo para asignar una nota a una fecha."""
    
    def __init__(self, data_manager, date_str, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.date_str = date_str
        
        self.setWindowTitle(f"Asignar nota a {date_str}")
        self.setup_ui()
        self.load_notes()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Lista de notas
        layout.addWidget(QLabel("Selecciona una nota:"))
        self.notes_list = QListWidget()
        layout.addWidget(self.notes_list)
        
        # Opciones adicionales
        options_layout = QFormLayout()
        
        # Crear recordatorio
        self.reminder_check = QCheckBox("Crear recordatorio")
        self.reminder_check.setChecked(True)
        options_layout.addRow("", self.reminder_check)
        
        # Hora del recordatorio
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(datetime.time(9, 0))  # 9:00 AM predeterminado
        options_layout.addRow("Hora:", self.time_edit)
        
        # Título del recordatorio
        self.title_edit = QLineEdit("Recordatorio")
        options_layout.addRow("Título:", self.title_edit)
        
        # Descripción
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Descripción (opcional)")
        self.desc_edit.setMaximumHeight(80)
        options_layout.addRow("Descripción:", self.desc_edit)
        
        layout.addLayout(options_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.assign_btn = QPushButton("Asignar")
        self.assign_btn.clicked.connect(self.assign_date)
        self.assign_btn.setEnabled(False)
        buttons_layout.addWidget(self.assign_btn)
        
        layout.addLayout(buttons_layout)
        
        # Conectar eventos
        self.notes_list.itemSelectionChanged.connect(self.on_selection_changed)
        
    def load_notes(self):
        """Carga la lista de notas disponibles."""
        all_notes = self.data_manager.get_all_notes()
        
        for note_id, note_data in all_notes.items():
            item = QListWidgetItem(note_data.get("title", "Sin título"))
            item.setData(Qt.ItemDataRole.UserRole, note_id)
            self.notes_list.addItem(item)
    
    def on_selection_changed(self):
        """Habilita el botón de asignar cuando hay selección."""
        self.assign_btn.setEnabled(len(self.notes_list.selectedItems()) > 0)
    
    def assign_date(self):
        """Asigna la fecha a la nota seleccionada."""
        selected_items = self.notes_list.selectedItems()
        if not selected_items:
            return
            
        note_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        note_data = self.data_manager.get_note(note_id)
        
        if note_data:
            # Actualizar nota con la fecha
            note_data_copy = note_data.copy()
            note_data_copy["date"] = self.date_str
            
            # Actualizar en el gestor de datos
            self.data_manager.update_note(
                note_id, 
                note_data_copy.get("title", ""), 
                note_data_copy.get("content", ""),
                note_data_copy.get("type", "note"),
                note_data_copy.get("tags", [])
            )
            
            # Crear recordatorio si está marcado
            if self.reminder_check.isChecked():
                time_str = self.time_edit.time().toString("hh:mm")
                datetime_str = f"{self.date_str} {time_str}"
                
                # Importar ReminderManager aquí para evitar importación circular
                from reminder_manager import ReminderManager
                reminder_manager = ReminderManager(self.data_manager)
                
                reminder_manager.create_reminder(
                    note_id,
                    self.title_edit.text() or "Recordatorio",
                    datetime_str,
                    self.desc_edit.toPlainText()
                )
            
            # Aceptar diálogo
            self.accept()
