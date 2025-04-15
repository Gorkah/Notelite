#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Editor de notas con soporte para texto enriquecido.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                           QTextEdit, QToolBar, QPushButton, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QTextListFormat, QFont, QTextCursor, QKeySequence

class NoteEditor(QWidget):
    """Editor de notas con formato enriquecido."""
    
    # Señal que se emite cuando cambian los datos
    data_changed = pyqtSignal(str, str, str)  # note_id, title, content
    
    def __init__(self, note_id, title, content):
        super().__init__()
        
        self.note_id = note_id
        self.title = title
        self.content = content
        
        self.setup_ui()
        self.load_content()
        
        # Conectar a eventos de cambio
        self.title_edit.textChanged.connect(self.on_data_changed)
        self.text_edit.textChanged.connect(self.on_data_changed)
    
    def setup_ui(self):
        """Configura la interfaz del editor."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Título
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Título de la nota")
        self.title_edit.setProperty("class", "note-title")
        font = self.title_edit.font()
        font.setPointSize(16)
        self.title_edit.setFont(font)
        layout.addWidget(self.title_edit)
        
        # Barra de herramientas de formato
        self.format_toolbar = QToolBar()
        self.setup_format_toolbar()
        layout.addWidget(self.format_toolbar)
        
        # Editor de texto
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Escribe aquí tu nota...")
        layout.addWidget(self.text_edit)
    
    def setup_format_toolbar(self):
        """Configura la barra de herramientas de formato."""
        # Negrita
        bold_action = QAction("Negrita", self)
        bold_action.setShortcut(QKeySequence("Ctrl+B"))
        bold_action.triggered.connect(self.toggle_bold)
        self.format_toolbar.addAction(bold_action)
        
        # Cursiva
        italic_action = QAction("Cursiva", self)
        italic_action.setShortcut(QKeySequence("Ctrl+I"))
        italic_action.triggered.connect(self.toggle_italic)
        self.format_toolbar.addAction(italic_action)
        
        # Subrayado
        underline_action = QAction("Subrayado", self)
        underline_action.setShortcut(QKeySequence("Ctrl+U"))
        underline_action.triggered.connect(self.toggle_underline)
        self.format_toolbar.addAction(underline_action)
        
        self.format_toolbar.addSeparator()
        
        # Lista con viñetas
        bullet_list_action = QAction("Lista viñetas", self)
        bullet_list_action.triggered.connect(self.toggle_bullet_list)
        self.format_toolbar.addAction(bullet_list_action)
        
        # Lista numerada
        numbered_list_action = QAction("Lista numerada", self)
        numbered_list_action.triggered.connect(self.toggle_numbered_list)
        self.format_toolbar.addAction(numbered_list_action)
        
        self.format_toolbar.addSeparator()
        
        # Alineación
        align_left_action = QAction("Alinear izquierda", self)
        align_left_action.triggered.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignLeft))
        align_left_action.setShortcut(QKeySequence("Ctrl+L"))
        self.format_toolbar.addAction(align_left_action)
        
        align_center_action = QAction("Centrar", self)
        align_center_action.triggered.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignCenter))
        align_center_action.setShortcut(QKeySequence("Ctrl+E"))
        self.format_toolbar.addAction(align_center_action)
        
        align_right_action = QAction("Alinear derecha", self)
        align_right_action.triggered.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignRight))
        align_right_action.setShortcut(QKeySequence("Ctrl+R"))
        self.format_toolbar.addAction(align_right_action)
    
    def load_content(self):
        """Carga el contenido en el editor."""
        self.title_edit.setText(self.title)
        self.text_edit.setHtml(self.content)
    
    def on_data_changed(self):
        """Maneja los cambios en los datos."""
        self.title = self.title_edit.text()
        self.content = self.text_edit.toHtml()
        self.data_changed.emit(self.note_id, self.title, self.content)
    
    def save(self):
        """Guarda explícitamente la nota."""
        self.data_changed.emit(self.note_id, self.title_edit.text(), self.text_edit.toHtml())
    
    def toggle_bold(self):
        """Activa/desactiva texto en negrita."""
        cursor = self.text_edit.textCursor()
        format = cursor.charFormat()
        format.setFontWeight(QFont.Weight.Bold if format.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
        cursor.mergeCharFormat(format)
        self.text_edit.setTextCursor(cursor)
    
    def toggle_italic(self):
        """Activa/desactiva texto en cursiva."""
        cursor = self.text_edit.textCursor()
        format = cursor.charFormat()
        format.setFontItalic(not format.fontItalic())
        cursor.mergeCharFormat(format)
        self.text_edit.setTextCursor(cursor)
    
    def toggle_underline(self):
        """Activa/desactiva texto subrayado."""
        cursor = self.text_edit.textCursor()
        format = cursor.charFormat()
        format.setFontUnderline(not format.fontUnderline())
        cursor.mergeCharFormat(format)
        self.text_edit.setTextCursor(cursor)
    
    def toggle_bullet_list(self):
        """Activa/desactiva lista con viñetas."""
        cursor = self.text_edit.textCursor()
        
        # Crear formato de lista
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.Style.ListDisc)
        list_format.setIndent(1)
        
        # Aplicar o remover formato
        cursor.createList(list_format)
        self.text_edit.setTextCursor(cursor)
    
    def toggle_numbered_list(self):
        """Activa/desactiva lista numerada."""
        cursor = self.text_edit.textCursor()
        
        # Crear formato de lista
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.Style.ListDecimal)
        list_format.setIndent(1)
        
        # Aplicar o remover formato
        cursor.createList(list_format)
        self.text_edit.setTextCursor(cursor)
    
    def set_alignment(self, alignment):
        """Establece la alineación del texto."""
        self.text_edit.setAlignment(alignment)
