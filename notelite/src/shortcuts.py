#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de atajos de teclado para NoteLite.
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QKeySequence, QShortcut
import json
import os

class ShortcutManager:
    """Gestor de atajos de teclado personalizables."""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.shortcuts = {}
        self.config_path = os.path.join(
            os.path.expanduser("~"), 
            "NoteLite", 
            "config", 
            "shortcuts.json"
        )
        
        # Asegurar que el directorio de configuración existe
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Cargar configuración existente o crear nueva
        self.config = self._load_config()
    
    def _load_config(self):
        """Carga la configuración de atajos de teclado."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al cargar atajos de teclado: {e}")
        
        # Configuración por defecto
        return {
            "new_note": "Ctrl+N",
            "new_task_list": "Ctrl+T",
            "save": "Ctrl+S",
            "search": "Ctrl+F",
            "toggle_bold": "Ctrl+B",
            "toggle_italic": "Ctrl+I",
            "toggle_underline": "Ctrl+U"
        }
    
    def _save_config(self):
        """Guarda la configuración de atajos de teclado."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar atajos de teclado: {e}")
            return False
    
    def register_shortcut(self, action_name, key_sequence, callback, description=""):
        """Registra un atajo de teclado.
        
        Args:
            action_name: Nombre identificativo de la acción.
            key_sequence: Secuencia de teclas (QKeySequence o string).
            callback: Función a llamar cuando se active el atajo.
            description: Descripción de la acción.
        """
        # Usar configuración personalizada si existe
        if action_name in self.config:
            key_sequence = QKeySequence(self.config[action_name])
        else:
            # Guardar el atajo por defecto si no está en la configuración
            self.config[action_name] = key_sequence.toString()
            self._save_config()
        
        # Crear el atajo
        shortcut = QShortcut(key_sequence, self.parent)
        shortcut.activated.connect(callback)
        
        # Almacenar información
        self.shortcuts[action_name] = {
            "shortcut": shortcut,
            "key_sequence": key_sequence,
            "callback": callback,
            "description": description
        }
    
    def update_shortcut(self, action_name, new_key_sequence):
        """Actualiza un atajo de teclado existente.
        
        Args:
            action_name: Nombre de la acción.
            new_key_sequence: Nueva secuencia de teclas (QKeySequence o string).
            
        Returns:
            True si la actualización fue exitosa, False en caso contrario.
        """
        if action_name not in self.shortcuts:
            return False
        
        # Obtener información del atajo
        shortcut_info = self.shortcuts[action_name]
        
        # Convertir a QKeySequence si es necesario
        if isinstance(new_key_sequence, str):
            new_key_sequence = QKeySequence(new_key_sequence)
        
        # Actualizar el atajo
        shortcut_info["shortcut"].setKey(new_key_sequence)
        shortcut_info["key_sequence"] = new_key_sequence
        
        # Actualizar configuración
        self.config[action_name] = new_key_sequence.toString()
        return self._save_config()
    
    def get_shortcut(self, action_name):
        """Obtiene la información de un atajo.
        
        Args:
            action_name: Nombre de la acción.
            
        Returns:
            Diccionario con información del atajo o None si no existe.
        """
        return self.shortcuts.get(action_name)
    
    def get_all_shortcuts(self):
        """Obtiene todos los atajos registrados.
        
        Returns:
            Diccionario con todos los atajos.
        """
        return {
            action: {
                "key_sequence": info["key_sequence"].toString(),
                "description": info["description"]
            }
            for action, info in self.shortcuts.items()
        }
