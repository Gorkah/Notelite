#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de estadísticas mejorado para NoteLite.
Proporciona estadísticas detalladas sobre el uso de la aplicación.
"""

import os
import json
import datetime
import time
from collections import Counter
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
    QPushButton, QScrollArea, QFrame, QGridLayout
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

class EnhancedStatsManager:
    """Gestor de estadísticas mejorado para NoteLite."""
    
    def __init__(self, data_manager):
        """Inicializa el gestor de estadísticas."""
        self.data_manager = data_manager
        self.stats_path = os.path.join(os.path.expanduser("~"), "NoteLite", "stats.json")
        self.metrics = {
            "general": {
                "total_notes": 0,
                "total_chars": 0,
                "total_words": 0,
                "avg_note_length": 0,
                "last_update": "",
                "creation_dates": {},
                "edit_dates": {}
            },
            "typing": {
                "chars_per_session": [],
                "words_per_second": [],
                "typing_sessions": [],
                "avg_typing_speed": 0
            },
            "tags": {
                "tag_usage": {},
                "most_used_tags": []
            },
            "reminders": {
                "total_reminders": 0,
                "completed_reminders": 0,
                "pending_reminders": 0,
                "overdue_reminders": 0
            },
            "session": {
                "start_time": time.time(),
                "chars_typed": 0,
                "words_typed": 0,
                "notes_created": 0,
                "notes_edited": 0,
                "notes_deleted": 0
            }
        }
        
        # Cargar estadísticas si existen
        self.load_stats()
        
        # Iniciar sesión
        self.start_session()
    
    def load_stats(self):
        """Carga las estadísticas desde el archivo."""
        if os.path.exists(self.stats_path):
            try:
                with open(self.stats_path, 'r', encoding='utf-8') as f:
                    saved_stats = json.load(f)
                    
                    # Actualizar las métricas con las guardadas
                    for category in saved_stats:
                        if category in self.metrics:
                            for metric in saved_stats[category]:
                                if metric in self.metrics[category]:
                                    self.metrics[category][metric] = saved_stats[category][metric]
            except Exception as e:
                print(f"Error al cargar estadísticas: {e}")
    
    def save_stats(self):
        """Guarda las estadísticas en un archivo."""
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(self.stats_path), exist_ok=True)
        
        # Actualizar la fecha de última actualización
        self.metrics["general"]["last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Guardar en archivo
        try:
            with open(self.stats_path, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar estadísticas: {e}")
    
    def start_session(self):
        """Inicia una nueva sesión de estadísticas."""
        self.metrics["session"] = {
            "start_time": time.time(),
            "chars_typed": 0,
            "words_typed": 0,
            "notes_created": 0,
            "notes_edited": 0,
            "notes_deleted": 0
        }
    
    def end_session(self):
        """Finaliza la sesión actual y guarda las estadísticas."""
        # Calcular duración de la sesión
        session_duration = time.time() - self.metrics["session"]["start_time"]
        
        # Si se escribió algo durante la sesión, guardar métricas de velocidad
        if self.metrics["session"]["chars_typed"] > 0:
            chars_per_second = self.metrics["session"]["chars_typed"] / session_duration
            self.metrics["typing"]["chars_per_session"].append(round(chars_per_second, 2))
            
            # Limitar historial a últimas 50 sesiones
            if len(self.metrics["typing"]["chars_per_session"]) > 50:
                self.metrics["typing"]["chars_per_session"] = self.metrics["typing"]["chars_per_session"][-50:]
            
            # Calcular velocidad de escritura en palabras por minuto
            if session_duration > 0:
                wpm = (self.metrics["session"]["words_typed"] / session_duration) * 60
                self.metrics["typing"]["words_per_second"].append(round(wpm, 2))
                
                # Limitar historial
                if len(self.metrics["typing"]["words_per_second"]) > 50:
                    self.metrics["typing"]["words_per_second"] = self.metrics["typing"]["words_per_second"][-50:]
                
                # Actualizar promedio
                if self.metrics["typing"]["words_per_second"]:
                    self.metrics["typing"]["avg_typing_speed"] = sum(self.metrics["typing"]["words_per_second"]) / len(self.metrics["typing"]["words_per_second"])
        
        # Guardar estadísticas
        self.update_general_stats()
        self.save_stats()
    
    def update_general_stats(self):
        """Actualiza las estadísticas generales."""
        # Contar notas totales
        notes = self.data_manager.get_all_notes()
        self.metrics["general"]["total_notes"] = len(notes)
        
        # Contar caracteres y palabras totales
        total_chars = 0
        total_words = 0
        
        for note_id, note_data in notes.items():
            content = note_data.get("content", "")
            total_chars += len(content)
            total_words += len(content.split())
        
        self.metrics["general"]["total_chars"] = total_chars
        self.metrics["general"]["total_words"] = total_words
        
        # Calcular longitud promedio de notas
        if self.metrics["general"]["total_notes"] > 0:
            self.metrics["general"]["avg_note_length"] = total_chars / self.metrics["general"]["total_notes"]
        
    def update_tag_stats(self):
        """Actualiza las estadísticas de etiquetas."""
        notes = self.data_manager.get_all_notes()
        tag_usage = {}
        
        # Contar uso de etiquetas
        for note_id, note_data in notes.items():
            tags = note_data.get("tags", [])
            for tag in tags:
                if tag in tag_usage:
                    tag_usage[tag] += 1
                else:
                    tag_usage[tag] = 1
        
        self.metrics["tags"]["tag_usage"] = tag_usage
        
        # Calcular etiquetas más usadas
        self.metrics["tags"]["most_used_tags"] = [tag for tag, count in 
                                                Counter(tag_usage).most_common(5)]
    
    def update_reminder_stats(self):
        """Actualiza las estadísticas de recordatorios."""
        notes = self.data_manager.get_all_notes()
        total_reminders = 0
        completed_reminders = 0
        pending_reminders = 0
        overdue_reminders = 0
        
        current_datetime = datetime.datetime.now()
        
        for note_id, note_data in notes.items():
            reminders = note_data.get("reminders", [])
            total_reminders += len(reminders)
            
            for reminder in reminders:
                if reminder.get("completed", False):
                    completed_reminders += 1
                else:
                    # Verificar si está vencido
                    try:
                        reminder_datetime = datetime.datetime.strptime(
                            reminder.get("datetime", ""), 
                            "%Y-%m-%d %H:%M"
                        )
                        
                        if reminder_datetime < current_datetime:
                            overdue_reminders += 1
                        else:
                            pending_reminders += 1
                    except (ValueError, TypeError):
                        pending_reminders += 1  # Si hay error, asumir pendiente
        
        self.metrics["reminders"]["total_reminders"] = total_reminders
        self.metrics["reminders"]["completed_reminders"] = completed_reminders
        self.metrics["reminders"]["pending_reminders"] = pending_reminders
        self.metrics["reminders"]["overdue_reminders"] = overdue_reminders
    
    def register_text_change(self, old_text, new_text):
        """Registra un cambio de texto para estadísticas de escritura."""
        # Calcular caracteres escritos
        chars_diff = len(new_text) - len(old_text)
        if chars_diff > 0:
            self.metrics["session"]["chars_typed"] += chars_diff
        
        # Calcular palabras
        old_words = set(old_text.split())
        new_words = set(new_text.split())
        words_diff = len(new_words - old_words)
        if words_diff > 0:
            self.metrics["session"]["words_typed"] += words_diff
    
    def register_note_creation(self, note_id):
        """Registra la creación de una nota."""
        self.metrics["session"]["notes_created"] += 1
        
        # Registrar fecha de creación
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        if date_str in self.metrics["general"]["creation_dates"]:
            self.metrics["general"]["creation_dates"][date_str] += 1
        else:
            self.metrics["general"]["creation_dates"][date_str] = 1
    
    def register_note_edit(self, note_id):
        """Registra la edición de una nota."""
        self.metrics["session"]["notes_edited"] += 1
        
        # Registrar fecha de edición
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        if date_str in self.metrics["general"]["edit_dates"]:
            self.metrics["general"]["edit_dates"][date_str] += 1
        else:
            self.metrics["general"]["edit_dates"][date_str] = 1
    
    def register_note_deletion(self, note_id):
        """Registra la eliminación de una nota."""
        self.metrics["session"]["notes_deleted"] += 1
    
    def get_current_typing_speed(self):
        """Devuelve la velocidad de escritura actual en caracteres por segundo."""
        session_duration = time.time() - self.metrics["session"]["start_time"]
        if session_duration > 0 and self.metrics["session"]["chars_typed"] > 0:
            return round(self.metrics["session"]["chars_typed"] / session_duration, 2)
        return 0
    
    def get_current_wpm(self):
        """Devuelve la velocidad de escritura actual en palabras por minuto."""
        session_duration = time.time() - self.metrics["session"]["start_time"]
        if session_duration > 0 and self.metrics["session"]["words_typed"] > 0:
            return round((self.metrics["session"]["words_typed"] / session_duration) * 60, 2)
        return 0
    
    def get_session_stats(self):
        """Devuelve estadísticas de la sesión actual."""
        return {
            "chars_typed": self.metrics["session"]["chars_typed"],
            "words_typed": self.metrics["session"]["words_typed"],
            "notes_created": self.metrics["session"]["notes_created"],
            "notes_edited": self.metrics["session"]["notes_edited"],
            "notes_deleted": self.metrics["session"]["notes_deleted"],
            "chars_per_second": self.get_current_typing_speed(),
            "words_per_minute": self.get_current_wpm(),
            "duration": round(time.time() - self.metrics["session"]["start_time"], 2)
        }


class EnhancedStatsWidget(QWidget):
    """Widget para mostrar estadísticas mejoradas."""
    
    def __init__(self, stats_manager, parent=None):
        super().__init__(parent)
        self.stats_manager = stats_manager
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_realtime_stats)
        self.timer.start(5000)  # Actualizar cada 5 segundos
        
        self.setup_ui()
        self.update_all_stats()
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        main_layout = QVBoxLayout(self)
        
        # Crear pestañas
        tabs = QTabWidget()
        
        # Pestaña de estadísticas generales
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Métricas generales en grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        
        # Primera fila
        self.total_notes_label = StatsValueLabel("0")
        grid_layout.addWidget(StatsNameLabel("Notas totales:"), 0, 0)
        grid_layout.addWidget(self.total_notes_label, 0, 1)
        
        self.total_chars_label = StatsValueLabel("0")
        grid_layout.addWidget(StatsNameLabel("Caracteres totales:"), 0, 2)
        grid_layout.addWidget(self.total_chars_label, 0, 3)
        
        # Segunda fila
        self.total_words_label = StatsValueLabel("0")
        grid_layout.addWidget(StatsNameLabel("Palabras totales:"), 1, 0)
        grid_layout.addWidget(self.total_words_label, 1, 1)
        
        self.avg_length_label = StatsValueLabel("0")
        grid_layout.addWidget(StatsNameLabel("Longitud promedio:"), 1, 2)
        grid_layout.addWidget(self.avg_length_label, 1, 3)
        
        general_layout.addLayout(grid_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        general_layout.addWidget(separator)
        
        # Estadísticas de sesión
        session_label = QLabel("Estadísticas de sesión actual")
        session_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        general_layout.addWidget(session_label)
        
        session_grid = QGridLayout()
        
        # Primera fila de sesión
        self.session_chars_label = StatsValueLabel("0")
        session_grid.addWidget(StatsNameLabel("Caracteres escritos:"), 0, 0)
        session_grid.addWidget(self.session_chars_label, 0, 1)
        
        self.session_words_label = StatsValueLabel("0")
        session_grid.addWidget(StatsNameLabel("Palabras escritas:"), 0, 2)
        session_grid.addWidget(self.session_words_label, 0, 3)
        
        # Segunda fila de sesión
        self.typing_speed_label = StatsValueLabel("0 car/s")
        session_grid.addWidget(StatsNameLabel("Velocidad:"), 1, 0)
        session_grid.addWidget(self.typing_speed_label, 1, 1)
        
        self.wpm_label = StatsValueLabel("0 PPM")
        session_grid.addWidget(StatsNameLabel("Palabras por minuto:"), 1, 2)
        session_grid.addWidget(self.wpm_label, 1, 3)
        
        general_layout.addLayout(session_grid)
        
        # Añadir pestaña general
        tabs.addTab(general_tab, "General")
        
        # Pestaña de etiquetas
        tags_tab = QWidget()
        tags_layout = QVBoxLayout(tags_tab)
        
        tags_label = QLabel("Estadísticas de etiquetas")
        tags_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        tags_layout.addWidget(tags_label)
        
        # Etiquetas más usadas
        self.tag_stats_layout = QGridLayout()
        tags_layout.addLayout(self.tag_stats_layout)
        
        # Añadir pestaña de etiquetas
        tabs.addTab(tags_tab, "Etiquetas")
        
        # Pestaña de recordatorios
        reminders_tab = QWidget()
        reminders_layout = QVBoxLayout(reminders_tab)
        
        reminders_label = QLabel("Estadísticas de recordatorios")
        reminders_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        reminders_layout.addWidget(reminders_label)
        
        # Grid de estadísticas de recordatorios
        reminders_grid = QGridLayout()
        
        self.total_reminders_label = StatsValueLabel("0")
        reminders_grid.addWidget(StatsNameLabel("Total recordatorios:"), 0, 0)
        reminders_grid.addWidget(self.total_reminders_label, 0, 1)
        
        self.completed_reminders_label = StatsValueLabel("0")
        reminders_grid.addWidget(StatsNameLabel("Completados:"), 1, 0)
        reminders_grid.addWidget(self.completed_reminders_label, 1, 1)
        
        self.pending_reminders_label = StatsValueLabel("0")
        reminders_grid.addWidget(StatsNameLabel("Pendientes:"), 2, 0)
        reminders_grid.addWidget(self.pending_reminders_label, 2, 1)
        
        self.overdue_reminders_label = StatsValueLabel("0")
        reminders_grid.addWidget(StatsNameLabel("Vencidos:"), 3, 0)
        reminders_grid.addWidget(self.overdue_reminders_label, 3, 1)
        
        reminders_layout.addLayout(reminders_grid)
        
        # Añadir pestaña de recordatorios
        tabs.addTab(reminders_tab, "Recordatorios")
        
        # Añadir pestañas al layout principal
        main_layout.addWidget(tabs)
        
        # Botón de actualizar
        refresh_btn = QPushButton("Actualizar estadísticas")
        refresh_btn.clicked.connect(self.update_all_stats)
        main_layout.addWidget(refresh_btn)
    
    def update_all_stats(self):
        """Actualiza todas las estadísticas."""
        # Actualizar estadísticas en el gestor
        self.stats_manager.update_general_stats()
        self.stats_manager.update_tag_stats()
        self.stats_manager.update_reminder_stats()
        
        # Actualizar métricas generales
        metrics = self.stats_manager.metrics
        self.total_notes_label.setText(str(metrics["general"]["total_notes"]))
        self.total_chars_label.setText(str(metrics["general"]["total_chars"]))
        self.total_words_label.setText(str(metrics["general"]["total_words"]))
        self.avg_length_label.setText(f"{metrics['general']['avg_note_length']:.2f}")
        
        # Actualizar estadísticas de sesión
        session_stats = self.stats_manager.get_session_stats()
        self.session_chars_label.setText(str(session_stats["chars_typed"]))
        self.session_words_label.setText(str(session_stats["words_typed"]))
        self.typing_speed_label.setText(f"{session_stats['chars_per_second']} car/s")
        self.wpm_label.setText(f"{session_stats['words_per_minute']} PPM")
        
        # Actualizar estadísticas de etiquetas
        self.update_tag_stats(metrics["tags"])
        
        # Actualizar estadísticas de recordatorios
        self.total_reminders_label.setText(str(metrics["reminders"]["total_reminders"]))
        self.completed_reminders_label.setText(str(metrics["reminders"]["completed_reminders"]))
        self.pending_reminders_label.setText(str(metrics["reminders"]["pending_reminders"]))
        self.overdue_reminders_label.setText(str(metrics["reminders"]["overdue_reminders"]))
    
    def update_realtime_stats(self):
        """Actualiza las estadísticas en tiempo real."""
        # Solo actualizar estadísticas de sesión para no sobrecargarse
        session_stats = self.stats_manager.get_session_stats()
        self.session_chars_label.setText(str(session_stats["chars_typed"]))
        self.session_words_label.setText(str(session_stats["words_typed"]))
        self.typing_speed_label.setText(f"{session_stats['chars_per_second']} car/s")
        self.wpm_label.setText(f"{session_stats['words_per_minute']} PPM")
    
    def update_tag_stats(self, tag_metrics):
        """Actualiza las estadísticas de etiquetas."""
        # Limpiar layout
        for i in reversed(range(self.tag_stats_layout.count())):
            self.tag_stats_layout.itemAt(i).widget().setParent(None)
        
        # Título
        self.tag_stats_layout.addWidget(StatsNameLabel("Etiqueta"), 0, 0)
        self.tag_stats_layout.addWidget(StatsNameLabel("Usos"), 0, 1)
        
        # Añadir etiquetas más usadas
        row = 1
        for tag in tag_metrics["most_used_tags"]:
            tag_count = tag_metrics["tag_usage"].get(tag, 0)
            
            self.tag_stats_layout.addWidget(QLabel(tag), row, 0)
            self.tag_stats_layout.addWidget(QLabel(str(tag_count)), row, 1)
            
            row += 1
            
            # Limitar a 10 etiquetas
            if row > 10:
                break


class StatsNameLabel(QLabel):
    """Etiqueta para nombres de estadísticas."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Arial", 9, QFont.Weight.Bold))


class StatsValueLabel(QLabel):
    """Etiqueta para valores de estadísticas."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Arial", 9))
        
        # Alineación a la derecha para valores
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)


class StatsStatusBar(QWidget):
    """Barra de estado con estadísticas en tiempo real."""
    
    def __init__(self, stats_manager, parent=None):
        super().__init__(parent)
        self.stats_manager = stats_manager
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Actualizar cada segundo
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la barra de estado."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Caracteres en la sesión
        self.chars_label = QLabel("0 caracteres")
        layout.addWidget(self.chars_label)
        
        # Separador
        separator1 = QLabel("|")
        layout.addWidget(separator1)
        
        # Palabras en la sesión
        self.words_label = QLabel("0 palabras")
        layout.addWidget(self.words_label)
        
        # Separador
        separator2 = QLabel("|")
        layout.addWidget(separator2)
        
        # Velocidad de escritura
        self.speed_label = QLabel("0 car/s")
        layout.addWidget(self.speed_label)
        
        # Separador
        separator3 = QLabel("|")
        layout.addWidget(separator3)
        
        # Palabras por minuto
        self.wpm_label = QLabel("0 PPM")
        layout.addWidget(self.wpm_label)
        
        # Espacio flexible
        layout.addStretch()
        
        # Notas creadas/editadas
        self.notes_label = QLabel("Notas: 0 creadas, 0 editadas")
        layout.addWidget(self.notes_label)
    
    def update_stats(self):
        """Actualiza las estadísticas mostradas."""
        session_stats = self.stats_manager.get_session_stats()
        
        self.chars_label.setText(f"{session_stats['chars_typed']} caracteres")
        self.words_label.setText(f"{session_stats['words_typed']} palabras")
        self.speed_label.setText(f"{session_stats['chars_per_second']} car/s")
        self.wpm_label.setText(f"{session_stats['words_per_minute']} PPM")
        self.notes_label.setText(
            f"Notas: {session_stats['notes_created']} creadas, "
            f"{session_stats['notes_edited']} editadas"
        )
