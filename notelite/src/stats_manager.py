#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de estadísticas para NoteLite.
Proporciona análisis de uso y productividad.
"""

import os
import json
import datetime
import calendar
import matplotlib.pyplot as plt
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StatsManager:
    """
    Gestor de estadísticas que analiza el uso de la aplicación
    y proporciona métricas de productividad.
    """
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.stats_dir = os.path.join(os.path.expanduser("~"), "NoteLite", "stats")
        
        # Asegurar que el directorio existe
        os.makedirs(self.stats_dir, exist_ok=True)
        
        # Cargar o inicializar datos de uso
        self.usage_data = self._load_usage_data()
    
    def _load_usage_data(self):
        """Carga los datos de uso o inicializa si no existen."""
        usage_file = os.path.join(self.stats_dir, "usage_data.json")
        
        if os.path.exists(usage_file):
            try:
                with open(usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al cargar datos de uso: {e}")
                return self._initialize_usage_data()
        else:
            return self._initialize_usage_data()
    
    def _initialize_usage_data(self):
        """Inicializa la estructura de datos de uso."""
        return {
            "app_launches": 0,
            "session_time": 0,  # tiempo total en segundos
            "notes_created": 0,
            "notes_edited": 0,
            "tasks_completed": 0,
            "daily_stats": {},
            "last_update": datetime.datetime.now().isoformat()
        }
    
    def _save_usage_data(self):
        """Guarda los datos de uso en el sistema."""
        usage_file = os.path.join(self.stats_dir, "usage_data.json")
        
        try:
            with open(usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar datos de uso: {e}")
            return False
    
    def record_app_launch(self):
        """Registra el inicio de la aplicación."""
        self.usage_data["app_launches"] += 1
        self._update_daily_stat("launches", 1)
        self._save_usage_data()
    
    def record_session_time(self, seconds):
        """Registra el tiempo de sesión."""
        self.usage_data["session_time"] += seconds
        self._update_daily_stat("session_time", seconds)
        self._save_usage_data()
    
    def record_note_created(self):
        """Registra la creación de una nota."""
        self.usage_data["notes_created"] += 1
        self._update_daily_stat("notes_created", 1)
        self._save_usage_data()
    
    def record_note_edited(self):
        """Registra la edición de una nota."""
        self.usage_data["notes_edited"] += 1
        self._update_daily_stat("notes_edited", 1)
        self._save_usage_data()
    
    def record_task_completed(self):
        """Registra la finalización de una tarea."""
        self.usage_data["tasks_completed"] += 1
        self._update_daily_stat("tasks_completed", 1)
        self._save_usage_data()
    
    def _update_daily_stat(self, stat_name, value):
        """Actualiza una estadística diaria."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if "daily_stats" not in self.usage_data:
            self.usage_data["daily_stats"] = {}
            
        if today not in self.usage_data["daily_stats"]:
            self.usage_data["daily_stats"][today] = {}
            
        if stat_name not in self.usage_data["daily_stats"][today]:
            self.usage_data["daily_stats"][today][stat_name] = 0
            
        self.usage_data["daily_stats"][today][stat_name] += value
        self.usage_data["last_update"] = datetime.datetime.now().isoformat()
    
    def get_productivity_score(self, days=7):
        """
        Calcula una puntuación de productividad basada en la actividad reciente.
        
        Args:
            days: Número de días a considerar para el cálculo.
            
        Returns:
            Puntuación de productividad entre 0 y 100.
        """
        # Obtener las fechas de los últimos 'days' días
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days-1)
        
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.strftime("%Y-%m-%d"))
            current_date += datetime.timedelta(days=1)
        
        # Recopilar estadísticas para el rango de fechas
        tasks_completed = 0
        notes_created = 0
        notes_edited = 0
        
        for date in date_range:
            daily_stats = self.usage_data.get("daily_stats", {}).get(date, {})
            tasks_completed += daily_stats.get("tasks_completed", 0)
            notes_created += daily_stats.get("notes_created", 0)
            notes_edited += daily_stats.get("notes_edited", 0)
        
        # Calcular puntuación (ponderación arbitraria)
        score = (tasks_completed * 5) + (notes_created * 3) + (notes_edited * 1)
        
        # Normalizar a 0-100 (considerando un valor máximo arbitrario)
        max_expected_score = 20 * days  # Valor máximo esperado para 'days' días
        normalized_score = min(100, int((score / max_expected_score) * 100))
        
        return normalized_score
    
    def get_streak(self):
        """
        Calcula la racha actual de días consecutivos usando la aplicación.
        
        Returns:
            Número de días consecutivos de uso.
        """
        if not self.usage_data.get("daily_stats"):
            return 0
            
        # Obtener fechas ordenadas de más reciente a más antigua
        dates = sorted(self.usage_data["daily_stats"].keys(), reverse=True)
        
        if not dates:
            return 0
            
        # Verificar si hoy hay actividad
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today not in dates:
            # No hay actividad hoy, verificar ayer
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            if yesterday not in dates:
                return 0  # Racha terminada (no hay actividad hoy ni ayer)
            else:
                # Comenzar desde ayer
                current_date = datetime.datetime.strptime(yesterday, "%Y-%m-%d")
        else:
            # Comenzar desde hoy
            current_date = datetime.datetime.strptime(today, "%Y-%m-%d")
        
        # Contar días consecutivos
        streak = 1  # Empezamos con el día actual
        while True:
            previous_date = (current_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            if previous_date in self.usage_data["daily_stats"]:
                streak += 1
                current_date = current_date - datetime.timedelta(days=1)
            else:
                break
        
        return streak
    
    def get_monthly_task_completion(self, year=None, month=None):
        """
        Obtiene datos de finalización de tareas por día para un mes específico.
        
        Args:
            year: Año (default: actual)
            month: Mes (default: actual)
            
        Returns:
            Diccionario con días y número de tareas completadas.
        """
        if year is None:
            year = datetime.datetime.now().year
        if month is None:
            month = datetime.datetime.now().month
            
        # Obtener número de días en el mes
        _, days_in_month = calendar.monthrange(year, month)
        
        # Inicializar datos para todos los días del mes
        task_data = {day: 0 for day in range(1, days_in_month + 1)}
        
        # Rellenar con datos reales
        for date_str, stats in self.usage_data.get("daily_stats", {}).items():
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj.year == year and date_obj.month == month:
                    day = date_obj.day
                    task_data[day] = stats.get("tasks_completed", 0)
            except:
                continue
        
        return task_data
    
    def generate_activity_heatmap_data(self, year=None):
        """
        Genera datos para un mapa de calor de actividad anual.
        
        Args:
            year: Año para el que generar datos (default: actual)
            
        Returns:
            Matriz numpy con actividad por día (filas: semanas, columnas: días de la semana)
        """
        if year is None:
            year = datetime.datetime.now().year
            
        # Crear matriz para 53 semanas x 7 días
        activity_data = np.zeros((53, 7))
        
        # Rellenar con datos reales
        for date_str, stats in self.usage_data.get("daily_stats", {}).items():
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj.year == year:
                    # Calcular la semana y el día de la semana (0-6, donde 0 es lunes)
                    week_num = int(date_obj.strftime("%W"))
                    weekday = date_obj.weekday()
                    
                    # Sumar actividad (notas creadas + tareas completadas)
                    activity = (
                        stats.get("notes_created", 0) + 
                        stats.get("tasks_completed", 0)
                    )
                    
                    activity_data[week_num, weekday] = activity
            except:
                continue
        
        return activity_data
    
    def get_summary_stats(self):
        """
        Obtiene estadísticas resumidas de uso.
        
        Returns:
            Diccionario con estadísticas resumidas.
        """
        total_notes = len(self.data_manager.get_all_notes())
        
        # Contar tareas completadas vs. totales
        task_notes = [
            note for note_id, note in self.data_manager.get_all_notes().items()
            if note.get("type") == "task_list"
        ]
        
        total_tasks = 0
        completed_tasks = 0
        
        for note in task_notes:
            content = note.get("content", "")
            if isinstance(content, str):
                try:
                    tasks = json.loads(content)
                    total_tasks += len(tasks)
                    completed_tasks += sum(1 for task in tasks if task.get("completed", False))
                except:
                    pass
            elif isinstance(content, list):
                total_tasks += len(content)
                completed_tasks += sum(1 for task in content if task.get("completed", False))
        
        # Calcular tiempo total de uso en horas
        total_time_hours = round(self.usage_data.get("session_time", 0) / 3600, 1)
        
        # Calcular productividad
        productivity_score = self.get_productivity_score()
        
        # Calcular racha
        streak = self.get_streak()
        
        return {
            "total_notes": total_notes,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round(completed_tasks / total_tasks * 100 if total_tasks > 0 else 0, 1),
            "total_time_hours": total_time_hours,
            "productivity_score": productivity_score,
            "streak": streak,
            "app_launches": self.usage_data.get("app_launches", 0)
        }


class StatsWidget(QWidget):
    """Widget para mostrar estadísticas de uso y productividad."""
    
    def __init__(self, stats_manager):
        super().__init__()
        self.stats_manager = stats_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        
        # Título
        title_label = QLabel("Estadísticas y Productividad")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # Selector de vista
        self.view_selector = QComboBox()
        self.view_selector.addItems([
            "Resumen", 
            "Tareas completadas", 
            "Mapa de actividad", 
            "Estadísticas detalladas"
        ])
        self.view_selector.currentIndexChanged.connect(self.change_view)
        layout.addWidget(self.view_selector)
        
        # Contenedor para el gráfico
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Área de estadísticas de texto
        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)
        
        # Botón de actualizar
        update_btn = QPushButton("Actualizar estadísticas")
        update_btn.clicked.connect(self.update_stats)
        layout.addWidget(update_btn)
        
        # Mostrar vista inicial
        self.change_view(0)
    
    def change_view(self, index):
        """Cambia la vista según la selección."""
        self.figure.clear()
        
        if index == 0:  # Resumen
            self.show_summary_view()
        elif index == 1:  # Tareas completadas
            self.show_tasks_view()
        elif index == 2:  # Mapa de actividad
            self.show_activity_heatmap()
        elif index == 3:  # Estadísticas detalladas
            self.show_detailed_stats()
        
        self.canvas.draw()
    
    def show_summary_view(self):
        """Muestra la vista de resumen."""
        stats = self.stats_manager.get_summary_stats()
        
        # Crear gráfico de productividad
        ax = self.figure.add_subplot(111)
        
        # Gráfico de medidor para productividad
        self._create_gauge_chart(ax, stats["productivity_score"], "Productividad")
        
        # Estadísticas de texto
        text = f"""
<h3>Resumen de actividad</h3>
<p><b>Notas totales:</b> {stats['total_notes']}</p>
<p><b>Tareas completadas:</b> {stats['completed_tasks']} de {stats['total_tasks']} ({stats['completion_rate']}%)</p>
<p><b>Tiempo total de uso:</b> {stats['total_time_hours']} horas</p>
<p><b>Racha actual:</b> {stats['streak']} días</p>
<p><b>Inicios de la aplicación:</b> {stats['app_launches']} veces</p>
"""
        self.stats_label.setText(text)
    
    def show_tasks_view(self):
        """Muestra la vista de tareas completadas por día del mes actual."""
        # Obtener datos del mes actual
        task_data = self.stats_manager.get_monthly_task_completion()
        
        # Crear gráfico de barras
        ax = self.figure.add_subplot(111)
        days = list(task_data.keys())
        tasks = list(task_data.values())
        
        bars = ax.bar(days, tasks, color='#4F46E5')
        
        # Resaltar el día actual
        current_day = datetime.datetime.now().day
        if current_day in days:
            idx = days.index(current_day)
            bars[idx].set_color('#FF5733')
        
        ax.set_xlabel('Día del mes')
        ax.set_ylabel('Tareas completadas')
        ax.set_title('Tareas completadas por día')
        
        # Ajustar etiquetas del eje x para mostrar solo algunos días
        ax.set_xticks([1, 5, 10, 15, 20, 25, 30])
        
        self.stats_label.setText("<p>Este gráfico muestra cuántas tareas has completado cada día del mes actual.</p>")
    
    def show_activity_heatmap(self):
        """Muestra un mapa de calor de actividad anual."""
        # Obtener datos de actividad
        activity_data = self.stats_manager.generate_activity_heatmap_data()
        
        # Crear mapa de calor
        ax = self.figure.add_subplot(111)
        heatmap = ax.imshow(activity_data, cmap='Blues')
        
        # Configurar ejes
        ax.set_yticks([0, 10, 20, 30, 40, 50])
        ax.set_yticklabels(['1', '11', '21', '31', '41', '51'])
        ax.set_ylabel('Semana del año')
        
        ax.set_xticks(range(7))
        ax.set_xticklabels(['L', 'M', 'X', 'J', 'V', 'S', 'D'])
        
        # Añadir barra de color
        self.figure.colorbar(heatmap, ax=ax, label='Actividad')
        
        ax.set_title('Mapa de actividad anual')
        
        self.stats_label.setText("<p>Este mapa de calor muestra tu actividad durante el año. Los colores más oscuros indican mayor actividad en ese día.</p>")
    
    def show_detailed_stats(self):
        """Muestra estadísticas detalladas."""
        # Obtener datos para diferentes métricas
        stats = self.stats_manager.get_summary_stats()
        
        # Crear múltiples subgráficos
        ax1 = self.figure.add_subplot(221)
        ax2 = self.figure.add_subplot(222)
        ax3 = self.figure.add_subplot(223)
        ax4 = self.figure.add_subplot(224)
        
        # Gráfico 1: Proporción de tareas
        labels = ['Completadas', 'Pendientes']
        sizes = [stats['completed_tasks'], stats['total_tasks'] - stats['completed_tasks']]
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
               colors=['#4F46E5', '#E0E0E0'])
        ax1.set_title('Estado de tareas')
        
        # Gráfico 2: Productividad de los últimos días
        days = [1, 7, 30]
        scores = [
            self.stats_manager.get_productivity_score(days=1),
            self.stats_manager.get_productivity_score(days=7),
            self.stats_manager.get_productivity_score(days=30)
        ]
        ax2.bar(['Hoy', 'Semana', 'Mes'], scores, color='#4F46E5')
        ax2.set_ylim(0, 100)
        ax2.set_title('Productividad')
        
        # Gráfico 3: Distribución de tipos de notas
        all_notes = self.stats_manager.data_manager.get_all_notes()
        note_types = {'note': 0, 'task_list': 0}
        for _, note in all_notes.items():
            note_type = note.get('type', 'note')
            note_types[note_type] = note_types.get(note_type, 0) + 1
        
        ax3.pie(note_types.values(), labels=['Notas', 'Listas'], autopct='%1.1f%%',
               startangle=90, colors=['#FFC107', '#4F46E5'])
        ax3.set_title('Tipos de documentos')
        
        # Gráfico 4: Racha
        ax4.text(0.5, 0.5, f"{stats['streak']}", horizontalalignment='center',
                verticalalignment='center', transform=ax4.transAxes, fontsize=40)
        ax4.text(0.5, 0.3, "Días consecutivos", horizontalalignment='center',
                verticalalignment='center', transform=ax4.transAxes)
        ax4.axis('off')
        
        self.figure.tight_layout()
        
        # Texto descriptivo
        self.stats_label.setText("<p>Esta vista muestra estadísticas detalladas sobre tu uso de NoteLite, incluyendo el estado de tus tareas, niveles de productividad en diferentes períodos, tipos de documentos y tu racha actual.</p>")
    
    def _create_gauge_chart(self, ax, value, label):
        """Crea un gráfico de medidor para mostrar una puntuación."""
        # Configurar gráfico
        ax.set_xlim([-1, 1])
        ax.set_ylim([-1, 1])
        ax.axis('off')
        
        # Crear anillo de fondo
        theta = np.linspace(3*np.pi/4, 9*np.pi/4, 100)
        r = 0.8
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        ax.plot(x, y, color='#E0E0E0', linewidth=10)
        
        # Crear anillo de valor
        value_theta = np.linspace(3*np.pi/4, 3*np.pi/4 + (3*np.pi/2) * (value/100), 100)
        x_val = r * np.cos(value_theta)
        y_val = r * np.sin(value_theta)
        ax.plot(x_val, y_val, color='#4F46E5', linewidth=10)
        
        # Añadir valor numérico
        ax.text(0, -0.2, f"{value}%", horizontalalignment='center', 
                verticalalignment='center', fontsize=36)
        
        # Añadir etiqueta
        ax.text(0, -0.5, label, horizontalalignment='center', 
                verticalalignment='center', fontsize=14)
    
    def update_stats(self):
        """Actualiza las estadísticas y redibuja la vista actual."""
        current_index = self.view_selector.currentIndex()
        self.change_view(current_index)
