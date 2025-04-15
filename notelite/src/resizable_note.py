#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Editor de notas redimensionable y sticky notes.
Permite ajustar el tamaño de las notas y crear notas flotantes.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QFontComboBox, 
    QSpinBox, QToolBar, QSizePolicy, QMenu, QColorDialog,
    QMainWindow, QTextBrowser, QDialog, QGroupBox,
    QGridLayout, QToolButton, QCheckBox, QApplication
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import (
    QFont, QTextCharFormat, QColor, QTextCursor, QIcon,
    QTextFormat, QTextBlockFormat, QTextImageFormat, QTextListFormat,
    QPalette, QGuiApplication, QScreen
)

class ResizableNoteEditor(QTextEdit):
    """Editor de texto con capacidad de redimensionamiento."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize_active = False
        self.resize_corner_size = 20
        self.original_size = None
        
        # Establecer política de tamaño
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(300, 200)
        
        # Establecer cursor predeterminado
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        """Maneja el evento de presionar el mouse."""
        if self.is_in_resize_corner(event.position().toPoint()):
            self.resize_active = True
            self.original_size = self.size()
            self.resize_start_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Maneja el evento de mover el mouse."""
        if self.resize_active:
            # Calcular la nueva diferencia de tamaño
            diff = event.globalPosition().toPoint() - self.resize_start_pos
            
            # Aplicar el nuevo tamaño
            new_width = max(300, self.original_size.width() + diff.x())
            new_height = max(200, self.original_size.height() + diff.y())
            self.resize(new_width, new_height)
            
            event.accept()
        elif self.is_in_resize_corner(event.position().toPoint()):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            event.accept()
        else:
            self.setCursor(Qt.CursorShape.IBeamCursor)
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Maneja el evento de soltar el mouse."""
        if self.resize_active:
            self.resize_active = False
            self.setCursor(Qt.CursorShape.IBeamCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)
            
    def is_in_resize_corner(self, pos):
        """Determina si la posición está en la esquina de redimensionamiento."""
        width = self.width()
        height = self.height()
        corner_rect_width = self.resize_corner_size
        corner_rect_height = self.resize_corner_size
        
        return (width - corner_rect_width <= pos.x() <= width and 
                height - corner_rect_height <= pos.y() <= height)
    
    def paintEvent(self, event):
        """Personaliza el pintado del widget."""
        super().paintEvent(event)
        # Aquí podríamos dibujar una señal visual para la esquina de redimensionamiento


class FormattingToolbar(QToolBar):
    """Barra de herramientas para dar formato al texto."""
    
    def __init__(self, text_edit, parent=None):
        super().__init__(parent)
        self.text_edit = text_edit
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la barra de herramientas."""
        # Selector de fuente
        self.fontComboBox = QFontComboBox()
        self.fontComboBox.currentFontChanged.connect(self.change_font)
        self.addWidget(self.fontComboBox)
        
        # Tamaño de fuente
        self.sizeComboBox = QComboBox()
        self.sizeComboBox.addItems(["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26", "28", "36", "48", "72"])
        self.sizeComboBox.setCurrentText("12")
        self.sizeComboBox.currentTextChanged.connect(self.change_font_size)
        self.addWidget(self.sizeComboBox)
        
        self.addSeparator()
        
        # Botones de formato básico
        self.bold_action = QAction(QIcon(), "N", self)
        self.bold_action.setCheckable(True)
        self.bold_action.triggered.connect(self.toggle_bold)
        self.bold_action.setShortcut("Ctrl+B")
        self.addAction(self.bold_action)
        
        self.italic_action = QAction(QIcon(), "K", self)
        self.italic_action.setCheckable(True)
        self.italic_action.triggered.connect(self.toggle_italic)
        self.italic_action.setShortcut("Ctrl+I")
        self.addAction(self.italic_action)
        
        self.underline_action = QAction(QIcon(), "S", self)
        self.underline_action.setCheckable(True)
        self.underline_action.triggered.connect(self.toggle_underline)
        self.underline_action.setShortcut("Ctrl+U")
        self.addAction(self.underline_action)
        
        self.addSeparator()
        
        # Color de texto
        self.text_color_action = QAction(QIcon(), "Color", self)
        self.text_color_action.triggered.connect(self.change_text_color)
        self.addAction(self.text_color_action)
        
        self.addSeparator()
        
        # Alineación de texto
        self.align_left_action = QAction(QIcon(), "Izquierda", self)
        self.align_left_action.triggered.connect(lambda: self.align_text(Qt.AlignmentFlag.AlignLeft))
        self.addAction(self.align_left_action)
        
        self.align_center_action = QAction(QIcon(), "Centro", self)
        self.align_center_action.triggered.connect(lambda: self.align_text(Qt.AlignmentFlag.AlignCenter))
        self.addAction(self.align_center_action)
        
        self.align_right_action = QAction(QIcon(), "Derecha", self)
        self.align_right_action.triggered.connect(lambda: self.align_text(Qt.AlignmentFlag.AlignRight))
        self.addAction(self.align_right_action)
        
        self.align_justify_action = QAction(QIcon(), "Justificar", self)
        self.align_justify_action.triggered.connect(lambda: self.align_text(Qt.AlignmentFlag.AlignJustify))
        self.addAction(self.align_justify_action)
        
        self.addSeparator()
        
        # Lista
        self.bullet_list_action = QAction(QIcon(), "Lista", self)
        self.bullet_list_action.triggered.connect(self.toggle_bullet_list)
        self.addAction(self.bullet_list_action)
        
        # Bloques de código
        self.code_block_action = QAction(QIcon(), "Código", self)
        self.code_block_action.triggered.connect(self.insert_code_block)
        self.addAction(self.code_block_action)
        
        # Fórmula matemática
        self.math_action = QAction(QIcon(), "Fórmula", self)
        self.math_action.triggered.connect(self.insert_math_formula)
        self.addAction(self.math_action)
    
    def change_font(self, font):
        """Cambia la fuente del texto seleccionado."""
        current_format = QTextCharFormat()
        current_format.setFont(font)
        self.merge_format(current_format)
    
    def change_font_size(self, size_text):
        """Cambia el tamaño de la fuente del texto seleccionado."""
        size = int(size_text)
        current_format = QTextCharFormat()
        current_format.setFontPointSize(size)
        self.merge_format(current_format)
    
    def toggle_bold(self):
        """Activa/desactiva negrita en el texto seleccionado."""
        current_format = QTextCharFormat()
        current_format.setFontWeight(QFont.Weight.Bold if self.bold_action.isChecked() else QFont.Weight.Normal)
        self.merge_format(current_format)
    
    def toggle_italic(self):
        """Activa/desactiva cursiva en el texto seleccionado."""
        current_format = QTextCharFormat()
        current_format.setFontItalic(self.italic_action.isChecked())
        self.merge_format(current_format)
    
    def toggle_underline(self):
        """Activa/desactiva subrayado en el texto seleccionado."""
        current_format = QTextCharFormat()
        current_format.setFontUnderline(self.underline_action.isChecked())
        self.merge_format(current_format)
    
    def change_text_color(self):
        """Cambia el color del texto seleccionado."""
        color = QColorDialog.getColor(Qt.GlobalColor.black, self.parent())
        if color.isValid():
            current_format = QTextCharFormat()
            current_format.setForeground(color)
            self.merge_format(current_format)
    
    def align_text(self, alignment):
        """Alinea el texto según la opción seleccionada."""
        self.text_edit.setAlignment(alignment)
    
    def toggle_bullet_list(self):
        """Activa/desactiva lista con viñetas."""
        cursor = self.text_edit.textCursor()
        
        # Crear formato de lista
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.Style.ListDisc)
        list_format.setIndent(1)
        
        cursor.createList(list_format)
    
    def insert_code_block(self):
        """Inserta un bloque de código."""
        cursor = self.text_edit.textCursor()
        
        # Crear formato de bloque
        block_format = QTextBlockFormat()
        block_format.setBackground(QColor("#f0f0f0"))
        block_format.setLeftMargin(20)
        block_format.setRightMargin(20)
        
        # Formato de carácter para código
        char_format = QTextCharFormat()
        char_format.setFontFamily("Courier New")
        
        # Aplicar formatos
        cursor.insertBlock(block_format, char_format)
        cursor.insertText("// Código aquí")
    
    def insert_math_formula(self):
        """Inserta un bloque para fórmulas matemáticas."""
        cursor = self.text_edit.textCursor()
        
        # Crear formato de bloque
        block_format = QTextBlockFormat()
        block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Aplicar formatos
        cursor.insertBlock(block_format)
        cursor.insertText("f(x) = ")
    
    def merge_format(self, format):
        """Aplica el formato al texto seleccionado."""
        cursor = self.text_edit.textCursor()
        cursor.mergeCharFormat(format)
        self.text_edit.mergeCurrentCharFormat(format)


class StickyNoteWindow(QMainWindow):
    """Ventana de nota adhesiva flotante."""
    
    note_closed = pyqtSignal(str)  # ID de la nota cerrada
    note_content_changed = pyqtSignal(str, str)  # ID de la nota, nuevo contenido
    
    def __init__(self, note_id, title, content, parent=None):
        super().__init__(parent, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.note_id = note_id
        self.note_title = title
        self.note_content = content
        self.is_moving = False
        
        self.setup_ui()
        self.setup_window_properties()
    
    def setup_ui(self):
        """Configura la interfaz de la nota adhesiva."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Barra de título personalizada
        title_bar = QWidget()
        title_bar.setObjectName("stickyNoteTitleBar")
        title_bar.setFixedHeight(30)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 0, 10, 0)
        
        # Título
        title_label = QLabel(self.note_title)
        title_label.setObjectName("stickyNoteTitle")
        title_bar_layout.addWidget(title_label)
        
        # Botón de cerrar
        close_button = QPushButton("×")
        close_button.setObjectName("stickyNoteCloseButton")
        close_button.setFixedSize(20, 20)
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)
        
        layout.addWidget(title_bar)
        
        # Editor de texto
        self.editor = ResizableNoteEditor()
        self.editor.setHtml(self.note_content)
        self.editor.textChanged.connect(self.on_content_changed)
        layout.addWidget(self.editor)
        
        # Barra de formato
        self.formatting_toolbar = FormattingToolbar(self.editor)
        layout.addWidget(self.formatting_toolbar)
    
    def setup_window_properties(self):
        """Configura las propiedades de la ventana."""
        self.setWindowTitle(self.note_title)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # Tamaño y posición
        self.resize(300, 300)
        self.center_on_screen()
        
        # Establecer estilo
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFF99;
                border: 1px solid #E6E600;
                border-radius: 5px;
            }
            #stickyNoteTitleBar {
                background-color: #FFCC66;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            #stickyNoteTitle {
                font-weight: bold;
            }
            #stickyNoteCloseButton {
                background-color: #FF9966;
                border-radius: 10px;
                font-weight: bold;
                color: white;
            }
            QTextEdit {
                background-color: #FFFFCC;
                border: none;
            }
        """)
    
    def center_on_screen(self):
        """Centra la ventana en la pantalla."""
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            screen_geometry.width() // 2 - self.width() // 2,
            screen_geometry.height() // 2 - self.height() // 2
        )
    
    def mousePressEvent(self, event):
        """Maneja el evento de presionar el mouse."""
        if event.position().y() < 30:  # Si es en la barra de título
            self.is_moving = True
            self.drag_start_position = event.globalPosition().toPoint()
            self.window_position = self.pos()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Maneja el evento de mover el mouse."""
        if self.is_moving:
            delta = event.globalPosition().toPoint() - self.drag_start_position
            self.move(self.window_position + delta)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Maneja el evento de soltar el mouse."""
        self.is_moving = False
        super().mouseReleaseEvent(event)
    
    def closeEvent(self, event):
        """Maneja el evento de cerrar la ventana."""
        self.note_closed.emit(self.note_id)
        super().closeEvent(event)
    
    def on_content_changed(self):
        """Maneja el cambio en el contenido de la nota."""
        new_content = self.editor.toPlainText()
        self.note_content_changed.emit(self.note_id, new_content)


def create_sticky_note(note_id, title, content):
    """Crea una nota adhesiva flotante."""
    note = StickyNoteWindow(note_id, title, content)
    note.show()
    return note
