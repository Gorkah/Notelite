#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Barra de título personalizada con estilo retro para NoteLite.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class RetroTitleBar(QWidget):
    """Barra de título personalizada con estilo retro."""
    
    # Señales para las acciones de la ventana
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    
    def __init__(self, title="NoteLite"):
        super().__init__()
        self.title = title
        self.setObjectName("titleBar")
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la barra de título."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        # Título
        title_label = QLabel(f"  {self.title}  ")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(title_label)
        
        # Espaciador
        layout.addStretch()
        
        # Botones de la ventana (estilo Windows 95)
        self.min_button = QPushButton("_")
        self.min_button.setObjectName("minButton")
        self.min_button.setFixedSize(16, 16)
        self.min_button.clicked.connect(self.minimize_clicked)
        
        self.max_button = QPushButton("□")
        self.max_button.setObjectName("maxButton")
        self.max_button.setFixedSize(16, 16)
        self.max_button.clicked.connect(self.maximize_clicked)
        
        self.close_button = QPushButton("×")
        self.close_button.setObjectName("closeButton")
        self.close_button.setFixedSize(16, 16)
        self.close_button.clicked.connect(self.close_clicked)
        
        layout.addWidget(self.min_button)
        layout.addWidget(self.max_button)
        layout.addWidget(self.close_button)
