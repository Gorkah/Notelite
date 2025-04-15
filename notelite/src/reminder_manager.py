#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de recordatorios para NoteLite.
Permite crear, editar y gestionar recordatorios asociados a notas.
"""

import os
import json
import time
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QDateTimeEdit, QLineEdit, QListWidget, QListWidgetItem,
                            QPushButton, QDialog, QMessageBox, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime, QTimer, QSize
from PyQt6.QtGui import QIcon, QPixmap
import winsound


class ReminderManager:
    """
    Gestor para manejar recordatorios asociados a notas.
    """
    
    def __init__(self, data_manager):
        """Inicializa el gestor de recordatorios."""
        self.data_manager = data_manager
        self.reminders_dir = os.path.join(os.path.expanduser("~"), "NoteLite", "reminders")
        
        # Asegurar que el directorio existe
        os.makedirs(self.reminders_dir, exist_ok=True)
        
        # Cargar recordatorios
        self.reminders = self._load_reminders()
        
        # Timer para comprobar recordatorios
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_due_reminders)
        self.check_timer.start(60000)  # Comprobar cada minuto
        
        # Callback para notificaciones
        self.notification_callback = None
    
    def _load_reminders(self):
        """Carga los recordatorios guardados."""
        reminders_file = os.path.join(self.reminders_dir, "reminders.json")
        
        if os.path.exists(reminders_file):
            try:
                with open(reminders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al cargar recordatorios: {e}")
                return []
        else:
            return []
    
    def _save_reminders(self):
        """Guarda los recordatorios en disco."""
        reminders_file = os.path.join(self.reminders_dir, "reminders.json")
        
        try:
            with open(reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar recordatorios: {e}")
            return False
    
    def create_reminder(self, note_id, title, datetime_str, description="", repeat=None):
        """
        Crea un nuevo recordatorio.
        
        Args:
            note_id: ID de la nota asociada
            title: Título del recordatorio
            datetime_str: Fecha y hora del recordatorio (ISO format)
            description: Descripción opcional
            repeat: Intervalo de repetición (None, 'daily', 'weekly', 'monthly')
            
        Returns:
            ID del recordatorio creado
        """
        # Generar ID único
        reminder_id = str(int(time.time()))
        
        # Crear recordatorio
        reminder = {
            "id": reminder_id,
            "note_id": note_id,
            "title": title,
            "datetime": datetime_str,
            "description": description,
            "repeat": repeat,
            "completed": False,
            "dismissed": False
        }
        
        self.reminders.append(reminder)
        self._save_reminders()
        
        return reminder_id
    
    def update_reminder(self, reminder_id, title=None, datetime_str=None, 
                       description=None, repeat=None, completed=None, dismissed=None):
        """Actualiza un recordatorio existente."""
        for reminder in self.reminders:
            if reminder["id"] == reminder_id:
                if title is not None:
                    reminder["title"] = title
                if datetime_str is not None:
                    reminder["datetime"] = datetime_str
                if description is not None:
                    reminder["description"] = description
                if repeat is not None:
                    reminder["repeat"] = repeat
                if completed is not None:
                    reminder["completed"] = completed
                if dismissed is not None:
                    reminder["dismissed"] = dismissed
                
                self._save_reminders()
                return True
                
        return False
    
    def delete_reminder(self, reminder_id):
        """Elimina un recordatorio."""
        for i, reminder in enumerate(self.reminders):
            if reminder["id"] == reminder_id:
                del self.reminders[i]
                self._save_reminders()
                return True
                
        return False
    
    def get_reminder(self, reminder_id):
        """Obtiene un recordatorio por su ID."""
        for reminder in self.reminders:
            if reminder["id"] == reminder_id:
                return reminder
                
        return None
    
    def get_all_reminders(self):
        """Obtiene todos los recordatorios."""
        return self.reminders
    
    def get_reminders_for_note(self, note_id):
        """Obtiene todos los recordatorios asociados a una nota."""
        return [r for r in self.reminders if r["note_id"] == note_id]
    
    def get_upcoming_reminders(self, days=7):
        """Obtiene los recordatorios próximos."""
        now = datetime.datetime.now()
        end_date = now + datetime.timedelta(days=days)
        
        upcoming = []
        for reminder in self.reminders:
            if reminder["completed"] or reminder["dismissed"]:
                continue
                
            try:
                reminder_date = datetime.datetime.fromisoformat(reminder["datetime"])
                if now <= reminder_date <= end_date:
                    upcoming.append(reminder)
            except:
                continue
                
        return upcoming
    
    def check_due_reminders(self):
        """Comprueba si hay recordatorios pendientes."""
        now = datetime.datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M")
        
        for reminder in self.reminders:
            if reminder["completed"] or reminder["dismissed"]:
                continue
                
            try:
                reminder_date = datetime.datetime.fromisoformat(reminder["datetime"])
                reminder_str = reminder_date.strftime("%Y-%m-%d %H:%M")
                
                # Si es hora del recordatorio
                if reminder_str == now_str:
                    self._handle_due_reminder(reminder)
                    
                    # Si es un recordatorio recurrente, programar el siguiente
                    if reminder["repeat"]:
                        self._schedule_next_occurrence(reminder)
            except:
                continue
    
    def _handle_due_reminder(self, reminder):
        """Maneja un recordatorio que ha llegado su hora."""
        # Reproducir sonido
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            # En sistemas que no sean Windows, ignorar
            pass
        
        # Llamar al callback de notificación si existe
        if self.notification_callback:
            self.notification_callback(reminder)
    
    def _schedule_next_occurrence(self, reminder):
        """Programa la siguiente ocurrencia de un recordatorio recurrente."""
        repeat_type = reminder["repeat"]
        
        try:
            current_date = datetime.datetime.fromisoformat(reminder["datetime"])
            
            if repeat_type == "daily":
                next_date = current_date + datetime.timedelta(days=1)
            elif repeat_type == "weekly":
                next_date = current_date + datetime.timedelta(days=7)
            elif repeat_type == "monthly":
                # Intentar sumar un mes
                month = current_date.month + 1
                year = current_date.year
                if month > 12:
                    month = 1
                    year += 1
                    
                day = min(current_date.day, 28)  # Evitar problemas con febrero
                next_date = current_date.replace(year=year, month=month, day=day)
            else:
                return  # Tipo de repetición desconocido
            
            # Actualizar fecha del recordatorio
            reminder["datetime"] = next_date.isoformat()
            self._save_reminders()
            
        except Exception as e:
            print(f"Error al programar repetición: {e}")
    
    def set_notification_callback(self, callback):
        """Establece el callback a llamar cuando un recordatorio está pendiente."""
        self.notification_callback = callback
    
    def get_overdue_reminders(self):
        """Obtiene recordatorios vencidos pero no completados."""
        now = datetime.datetime.now()
        
        overdue = []
        for reminder in self.reminders:
            if reminder["completed"] or reminder["dismissed"]:
                continue
                
            try:
                reminder_date = datetime.datetime.fromisoformat(reminder["datetime"])
                if reminder_date < now:
                    overdue.append(reminder)
            except:
                continue
                
        return overdue


class ReminderDialog(QDialog):
    """Diálogo para crear o editar un recordatorio."""
    
    def __init__(self, reminder_manager, note_id=None, reminder_id=None, parent=None):
        super().__init__(parent)
        self.reminder_manager = reminder_manager
        self.note_id = note_id
        self.reminder_id = reminder_id
        
        # Si es un recordatorio existente, cargarlo
        self.reminder = None
        if reminder_id:
            self.reminder = reminder_manager.get_reminder(reminder_id)
            self.note_id = self.reminder["note_id"] if self.reminder else note_id
        
        self.setWindowTitle("Recordatorio" if not self.reminder else "Editar recordatorio")
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Título
        layout.addWidget(QLabel("Título:"))
        self.title_input = QLineEdit()
        if self.reminder:
            self.title_input.setText(self.reminder["title"])
        layout.addWidget(self.title_input)
        
        # Fecha y hora
        layout.addWidget(QLabel("Fecha y hora:"))
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setCalendarPopup(True)
        self.datetime_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        
        if self.reminder:
            try:
                reminder_date = datetime.datetime.fromisoformat(self.reminder["datetime"])
                self.datetime_input.setDateTime(QDateTime(
                    reminder_date.year, reminder_date.month, reminder_date.day,
                    reminder_date.hour, reminder_date.minute
                ))
            except:
                self.datetime_input.setDateTime(QDateTime.currentDateTime())
        else:
            # Por defecto, 15 minutos en el futuro
            future = QDateTime.currentDateTime().addSecs(15 * 60)
            self.datetime_input.setDateTime(future)
            
        layout.addWidget(self.datetime_input)
        
        # Descripción
        layout.addWidget(QLabel("Descripción (opcional):"))
        self.description_input = QLineEdit()
        if self.reminder:
            self.description_input.setText(self.reminder["description"])
        layout.addWidget(self.description_input)
        
        # Repetir
        layout.addWidget(QLabel("Repetir:"))
        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["No repetir", "Diariamente", "Semanalmente", "Mensualmente"])
        
        if self.reminder and self.reminder["repeat"]:
            if self.reminder["repeat"] == "daily":
                self.repeat_combo.setCurrentIndex(1)
            elif self.reminder["repeat"] == "weekly":
                self.repeat_combo.setCurrentIndex(2)
            elif self.reminder["repeat"] == "monthly":
                self.repeat_combo.setCurrentIndex(3)
                
        layout.addWidget(self.repeat_combo)
        
        # Si es un recordatorio existente, mostrar opciones de completado y descartado
        if self.reminder:
            self.completed_checkbox = QCheckBox("Marcar como completado")
            self.completed_checkbox.setChecked(self.reminder["completed"])
            layout.addWidget(self.completed_checkbox)
            
            self.dismissed_checkbox = QCheckBox("Descartar recordatorio")
            self.dismissed_checkbox.setChecked(self.reminder["dismissed"])
            layout.addWidget(self.dismissed_checkbox)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_reminder)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def save_reminder(self):
        """Guarda el recordatorio."""
        title = self.title_input.text().strip()
        
        if not title:
            QMessageBox.warning(self, "Error", "El título no puede estar vacío.")
            return
        
        # Obtener fecha y hora
        qdt = self.datetime_input.dateTime()
        dt = datetime.datetime(
            qdt.date().year(), qdt.date().month(), qdt.date().day(),
            qdt.time().hour(), qdt.time().minute()
        )
        
        # Convertir a string ISO
        dt_str = dt.isoformat()
        
        # Descripción
        description = self.description_input.text()
        
        # Repetición
        repeat_index = self.repeat_combo.currentIndex()
        repeat = None
        if repeat_index == 1:
            repeat = "daily"
        elif repeat_index == 2:
            repeat = "weekly"
        elif repeat_index == 3:
            repeat = "monthly"
        
        if self.reminder_id:
            # Actualizar recordatorio existente
            completed = self.completed_checkbox.isChecked() if hasattr(self, 'completed_checkbox') else None
            dismissed = self.dismissed_checkbox.isChecked() if hasattr(self, 'dismissed_checkbox') else None
            
            success = self.reminder_manager.update_reminder(
                self.reminder_id, title, dt_str, description, repeat, completed, dismissed
            )
        else:
            # Crear nuevo recordatorio
            success = bool(self.reminder_manager.create_reminder(
                self.note_id, title, dt_str, description, repeat
            ))
        
        if success:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar el recordatorio.")


class ReminderListWidget(QWidget):
    """Widget para mostrar y gestionar recordatorios."""
    
    reminder_changed = pyqtSignal()  # Emitida cuando se modifica un recordatorio
    
    def __init__(self, reminder_manager, parent=None):
        super().__init__(parent)
        self.reminder_manager = reminder_manager
        self.note_id = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        
        # Título
        title_layout = QHBoxLayout()
        title_label = QLabel("Recordatorios")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)
        title_layout.addWidget(title_label)
        
        # Botón para añadir recordatorio
        self.add_btn = QPushButton("+")
        self.add_btn.setMaximumWidth(30)
        self.add_btn.clicked.connect(self.add_reminder)
        title_layout.addWidget(self.add_btn)
        
        layout.addLayout(title_layout)
        
        # Lista de recordatorios
        self.reminders_list = QListWidget()
        self.reminders_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.reminders_list.customContextMenuRequested.connect(self.show_context_menu)
        self.reminders_list.itemDoubleClicked.connect(self.edit_reminder)
        layout.addWidget(self.reminders_list)
        
        # Estado inicial
        self.set_note(None)
    
    def set_note(self, note_id):
        """Establece la nota actual y carga sus recordatorios."""
        self.note_id = note_id
        self.update_reminders_list()
        
        # Habilitar/deshabilitar botón de añadir
        self.add_btn.setEnabled(bool(note_id))
    
    def update_reminders_list(self):
        """Actualiza la lista de recordatorios."""
        self.reminders_list.clear()
        
        if not self.note_id:
            return
            
        # Obtener recordatorios de la nota
        reminders = self.reminder_manager.get_reminders_for_note(self.note_id)
        
        for reminder in reminders:
            item = QListWidgetItem()
            
            # Establecer texto
            title = reminder["title"]
            
            try:
                dt = datetime.datetime.fromisoformat(reminder["datetime"])
                date_str = dt.strftime("%d/%m/%Y %H:%M")
            except:
                date_str = "Fecha no válida"
            
            # Estado
            status = ""
            if reminder["completed"]:
                status = " (Completado)"
            elif reminder["dismissed"]:
                status = " (Descartado)"
                
            item.setText(f"{title} - {date_str}{status}")
            
            # Formato según estado
            if reminder["completed"]:
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
            
            # Guardar ID en los datos del item
            item.setData(Qt.ItemDataRole.UserRole, reminder["id"])
            
            self.reminders_list.addItem(item)
    
    def add_reminder(self):
        """Añade un nuevo recordatorio."""
        if not self.note_id:
            return
            
        dialog = ReminderDialog(self.reminder_manager, self.note_id, parent=self)
        
        if dialog.exec():
            self.update_reminders_list()
            self.reminder_changed.emit()
    
    def edit_reminder(self, item=None):
        """Edita un recordatorio existente."""
        if not item:
            items = self.reminders_list.selectedItems()
            if not items:
                return
            item = items[0]
            
        reminder_id = item.data(Qt.ItemDataRole.UserRole)
        
        dialog = ReminderDialog(self.reminder_manager, reminder_id=reminder_id, parent=self)
        
        if dialog.exec():
            self.update_reminders_list()
            self.reminder_changed.emit()
    
    def show_context_menu(self, position):
        """Muestra el menú contextual para un recordatorio."""
        item = self.reminders_list.itemAt(position)
        if not item:
            return
            
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # Obtener el recordatorio
        reminder_id = item.data(Qt.ItemDataRole.UserRole)
        reminder = self.reminder_manager.get_reminder(reminder_id)
        
        # Opciones según el estado
        if reminder["completed"]:
            mark_action = menu.addAction("Marcar como no completado")
            mark_action.triggered.connect(lambda: self.toggle_completed(reminder_id, False))
        else:
            mark_action = menu.addAction("Marcar como completado")
            mark_action.triggered.connect(lambda: self.toggle_completed(reminder_id, True))
            
        if reminder["dismissed"]:
            dismiss_action = menu.addAction("Restaurar recordatorio")
            dismiss_action.triggered.connect(lambda: self.toggle_dismissed(reminder_id, False))
        else:
            dismiss_action = menu.addAction("Descartar recordatorio")
            dismiss_action.triggered.connect(lambda: self.toggle_dismissed(reminder_id, True))
            
        menu.addSeparator()
        
        edit_action = menu.addAction("Editar")
        edit_action.triggered.connect(lambda: self.edit_reminder(item))
        
        delete_action = menu.addAction("Eliminar")
        delete_action.triggered.connect(lambda: self.delete_reminder(reminder_id))
        
        menu.exec(self.reminders_list.mapToGlobal(position))
    
    def toggle_completed(self, reminder_id, completed):
        """Marca o desmarca un recordatorio como completado."""
        if self.reminder_manager.update_reminder(reminder_id, completed=completed):
            self.update_reminders_list()
            self.reminder_changed.emit()
    
    def toggle_dismissed(self, reminder_id, dismissed):
        """Descarta o restaura un recordatorio."""
        if self.reminder_manager.update_reminder(reminder_id, dismissed=dismissed):
            self.update_reminders_list()
            self.reminder_changed.emit()
    
    def delete_reminder(self, reminder_id):
        """Elimina un recordatorio."""
        confirm = QMessageBox.question(
            self, "Confirmar eliminación",
            "¿Estás seguro de que deseas eliminar este recordatorio?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.reminder_manager.delete_reminder(reminder_id):
                self.update_reminders_list()
                self.reminder_changed.emit()


class ReminderNotificationDialog(QDialog):
    """Diálogo para mostrar notificaciones de recordatorios."""
    
    def __init__(self, reminder, parent=None):
        super().__init__(parent)
        self.reminder = reminder
        
        self.setWindowTitle("Recordatorio")
        self.setup_ui()
        
        # Reproducir sonido al mostrar
        try:
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        except:
            pass
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel(self.reminder["title"])
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Fecha y hora
        try:
            dt = datetime.datetime.fromisoformat(self.reminder["datetime"])
            date_str = dt.strftime("%d/%m/%Y %H:%M")
        except:
            date_str = "Fecha no válida"
            
        datetime_label = QLabel(date_str)
        datetime_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(datetime_label)
        
        # Descripción
        if self.reminder["description"]:
            description_label = QLabel(self.reminder["description"])
            description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(description_label)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        dismiss_btn = QPushButton("Descartar")
        dismiss_btn.clicked.connect(self.dismiss_reminder)
        buttons_layout.addWidget(dismiss_btn)
        
        complete_btn = QPushButton("Completar")
        complete_btn.clicked.connect(self.complete_reminder)
        buttons_layout.addWidget(complete_btn)
        
        snooze_btn = QPushButton("Posponer")
        snooze_btn.clicked.connect(self.snooze_reminder)
        buttons_layout.addWidget(snooze_btn)
        
        layout.addLayout(buttons_layout)
    
    def dismiss_reminder(self):
        """Descarta el recordatorio."""
        # Esta función será sobrescrita por la ventana principal
        self.accept()
    
    def complete_reminder(self):
        """Marca el recordatorio como completado."""
        # Esta función será sobrescrita por la ventana principal
        self.accept()
    
    def snooze_reminder(self):
        """Pospone el recordatorio."""
        # Mostrar diálogo para elegir tiempo
        from PyQt6.QtWidgets import QInputDialog
        times = ["5 minutos", "15 minutos", "30 minutos", "1 hora", "3 horas"]
        choice, ok = QInputDialog.getItem(
            self, "Posponer", "Posponer por:", times, 1, False
        )
        
        if ok:
            # Esta función será sobrescrita por la ventana principal
            self.accept()
