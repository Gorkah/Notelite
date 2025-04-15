#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de temas retro para NoteLite.
Permite cambiar entre diferentes estilos nostálgicos.
"""

import os
import json
from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

class RetroThemeManager:
    """Gestor de temas retro para NoteLite."""
    
    # Definición de los temas disponibles
    THEMES = {
        # Temas basados en sistemas operativos históricos
        "win95": {
            "name": "Windows 95",
            "category": "OS",
            "year": "1995",
            "description": "Clásico gris y azul de Windows 95/98",
            "stylesheet": "win95.qss",
            "icon": "win95.png",
            "editable": False
        },
        "msdos": {
            "name": "MS-DOS",
            "category": "OS",
            "year": "1981",
            "description": "Pantalla de texto verde sobre negro",
            "stylesheet": "msdos.qss",
            "icon": "msdos.png",
            "editable": False
        },
        "amiga": {
            "name": "Amiga Workbench",
            "category": "OS",
            "year": "1985",
            "description": "Estilo del Commodore Amiga",
            "stylesheet": "amiga.qss",
            "icon": "amiga.png",
            "editable": False
        },
        "mac_classic": {
            "name": "Macintosh",
            "category": "OS",
            "year": "1984",
            "description": "Interfaz Mac OS clásico con bordes redondeados",
            "stylesheet": "mac.qss",
            "icon": "mac.png",
            "editable": False
        },
        "atari": {
            "name": "Atari ST GEM",
            "category": "OS",
            "year": "1985",
            "description": "Interfaz GEM del Atari ST",
            "stylesheet": "atari.qss",
            "icon": "atari.png",
            "editable": False
        },
        
        # Temas creativos y de otros estilos
        "cyberpunk": {
            "name": "Cyberpunk",
            "category": "Estilo",
            "year": "",
            "description": "Neones futuristas en fondo oscuro",
            "stylesheet": "cyberpunk.qss",
            "icon": "cyberpunk.png",
            "editable": False,
            "colors": {
                "background": "#0D0221",
                "foreground": "#FA448C",
                "accent": "#31E8FF",
                "secondary": "#722AFF",
                "text": "#FFFFFF"
            }
        },
        "vaporwave": {
            "name": "Vaporwave",
            "category": "Estilo",
            "year": "",
            "description": "Estética retro de los 80s y 90s",
            "stylesheet": "vaporwave.qss",
            "icon": "vaporwave.png",
            "editable": False,
            "colors": {
                "background": "#2D0B37",
                "foreground": "#FF6AD5",
                "accent": "#8C52FF",
                "secondary": "#33FFFC",
                "text": "#FFFFFF"
            }
        },
        "retrogaming": {
            "name": "Retro Gaming",
            "category": "Estilo",
            "year": "",
            "description": "Estilo de videojuegos clásicos pixelados",
            "stylesheet": "retrogaming.qss",
            "icon": "retrogaming.png",
            "editable": False,
            "colors": {
                "background": "#000000",
                "foreground": "#0FFF00",
                "accent": "#FF0000",
                "secondary": "#FFFF00",
                "text": "#FFFFFF"
            }
        },
        "terminal": {
            "name": "Terminal",
            "category": "Estilo",
            "year": "",
            "description": "Minimalista estilo de terminal",
            "stylesheet": "terminal.qss",
            "icon": "terminal.png",
            "editable": False,
            "colors": {
                "background": "#000000",
                "foreground": "#00FF00",
                "accent": "#C0C0C0",
                "secondary": "#808080",
                "text": "#00FF00"
            }
        },
        "newspaper": {
            "name": "Periódico",
            "category": "Estilo",
            "year": "",
            "description": "Estilo periódico antiguo",
            "stylesheet": "newspaper.qss",
            "icon": "newspaper.png",
            "editable": False,
            "colors": {
                "background": "#F5F5DC",
                "foreground": "#000000",
                "accent": "#8B4513",
                "secondary": "#A0A0A0",
                "text": "#000000"
            }
        },
        "custom1": {
            "name": "Personalizado 1",
            "category": "Custom",
            "year": "",
            "description": "Tema personalizable por el usuario",
            "stylesheet": "custom1.qss",
            "icon": "custom.png",
            "editable": True,
            "colors": {
                "background": "#FFFFFF",
                "foreground": "#000000",
                "accent": "#4F46E5",
                "secondary": "#A0A0A0",
                "text": "#000000"
            }
        },
        "custom2": {
            "name": "Personalizado 2",
            "category": "Custom",
            "year": "",
            "description": "Tema personalizable por el usuario",
            "stylesheet": "custom2.qss",
            "icon": "custom.png",
            "editable": True,
            "colors": {
                "background": "#222222",
                "foreground": "#FFFFFF",
                "accent": "#FF5733",
                "secondary": "#A0A0A0",
                "text": "#FFFFFF"
            }
        }
    }
    
    def __init__(self):
        """Inicializa el gestor de temas."""
        self.current_theme = "win95"  # Tema por defecto
        self.themes_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "assets", 
            "themes"
        )
        
        # Crear directorio de temas si no existe
        os.makedirs(self.themes_path, exist_ok=True)
        
        # Cargar preferencia de tema guardada
        self.config_path = os.path.join(
            os.path.expanduser("~"), 
            "NoteLite", 
            "config", 
            "theme.json"
        )
        self._load_theme_preference()
    
    def _load_theme_preference(self):
        """Carga la preferencia de tema guardada."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "theme" in config and config["theme"] in self.THEMES:
                        self.current_theme = config["theme"]
            except Exception as e:
                print(f"Error al cargar preferencia de tema: {e}")
    
    def _save_theme_preference(self):
        """Guarda la preferencia de tema."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception as e:
            print(f"Error al guardar preferencia de tema: {e}")
    
    def get_stylesheet_path(self, theme_id=None):
        """Obtiene la ruta del archivo de estilo para el tema especificado."""
        if theme_id is None:
            theme_id = self.current_theme
            
        if theme_id not in self.THEMES:
            theme_id = "win95"  # Tema por defecto si no existe
            
        return os.path.join(self.themes_path, self.THEMES[theme_id]["stylesheet"])
    
    def apply_theme(self, app, theme_id=None):
        """Aplica el tema especificado a la aplicación."""
        if theme_id:
            self.current_theme = theme_id
            
        # Buscar archivo de estilo
        theme_data = self.THEMES.get(self.current_theme)
        if not theme_data:
            return False
        
        # Si es un tema personalizado y no tiene archivo CSS, generarlo
        if self.current_theme.startswith("custom") and theme_data.get("editable"):
            # Verificar si el archivo existe o generar nuevo
            if not os.path.exists(os.path.join(self.themes_path, theme_data["stylesheet"])):
                if not self._generate_custom_stylesheet(self.current_theme, theme_data.get("colors", {})):
                    return False
            
        stylesheet_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", "assets", theme_data["stylesheet"]
        )
        
        # Si no existe en assets, buscar en directorio de usuario
        if not os.path.exists(stylesheet_file):
            stylesheet_file = os.path.join(self.themes_path, theme_data["stylesheet"])
            
        # Si el archivo existe, aplicar estilo
        if os.path.exists(stylesheet_file):
            try:
                with open(stylesheet_file, 'r', encoding='utf-8') as f:
                    app.setStyleSheet(f.read())
                return True
            except Exception as e:
                print(f"Error al aplicar tema: {e}")
                return False
        else:
            # Si no se encuentra, intentar con el primer tema
            if self.current_theme != list(self.THEMES.keys())[0]:
                self.current_theme = list(self.THEMES.keys())[0]
                return self.apply_theme(app)
            return False
    
    def get_available_themes(self):
        """Obtiene la lista de temas disponibles."""
        return self.THEMES


class ThemeSelectorWidget(QWidget):
    """Widget selector de temas retro."""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del selector de temas."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)
        
        # Etiqueta
        theme_label = QLabel("Tema:")
        theme_label.setFont(QFont("Courier New", 9))
        layout.addWidget(theme_label)
        
        # Selector de temas
        self.theme_combo = QComboBox()
        themes = self.theme_manager.get_available_themes()
        current_theme = self.theme_manager.current_theme
        
        # Añadir temas al selector
        for theme_id, theme_data in themes.items():
            self.theme_combo.addItem(f"{theme_data['name']} ({theme_data['year']})", theme_id)
            
            # Seleccionar el tema actual
            if theme_id == current_theme:
                self.theme_combo.setCurrentIndex(self.theme_combo.count() - 1)
        
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        # Añadir espaciador
        layout.addStretch()
    
    def on_theme_changed(self, index):
        """Maneja el cambio de tema."""
        theme_id = self.theme_combo.currentData()
        self.theme_changed.emit(theme_id)
