#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Conector de temas para NoteLite.
Evita problemas con el método change_theme.
"""

from PyQt6.QtWidgets import QApplication

def connect_theme_selector(app, theme_selector):
    """
    Conecta el selector de temas con un manejador alternativo.
    Esta función evita problemas con el método change_theme.
    """
    # Desconectar cualquier conexión anterior
    try:
        theme_selector.theme_changed.disconnect()
    except:
        pass
    
    # Conectar al manejador alternativo
    theme_selector.theme_changed.connect(lambda theme_id: change_theme_handler(app, theme_id))
    
def change_theme_handler(app, theme_id):
    """
    Manejador alternativo para cambios de tema.
    """
    # Aplicar el tema
    if app.theme_manager.apply_theme(QApplication.instance(), theme_id):
        # Mostrar mensaje de cambio de tema
        theme_name = app.theme_manager.THEMES[theme_id]["name"]
        app.show_retro_message(f"Tema cambiado a: {theme_name}")
        # Evitar fuentes problemáticas después de cambiar el tema
        if hasattr(app, 'avoid_problematic_fonts'):
            app.avoid_problematic_fonts()
