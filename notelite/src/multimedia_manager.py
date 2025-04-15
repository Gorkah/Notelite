#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de contenido multimedia para NoteLite.
Permite insertar, gestionar y mostrar imágenes, audio y otros contenidos en las notas.
"""

import os
import uuid
import base64
import shutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFileDialog, QComboBox, QDialog,
                            QLineEdit, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QBuffer, QByteArray, QIODevice
from PyQt6.QtGui import QPixmap, QImage, QIcon, QImageReader
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

class MultimediaManager:
    """
    Gestor para manejar contenido multimedia en las notas, incluyendo
    imágenes, audio, video y archivos adjuntos.
    """
    
    def __init__(self):
        """Inicializa el gestor de multimedia."""
        self.media_dir = os.path.join(os.path.expanduser("~"), "NoteLite", "media")
        
        # Asegurar que el directorio existe
        os.makedirs(self.media_dir, exist_ok=True)
        
        # Configuración de tipos de archivo soportados
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        self.supported_audio_formats = ['.mp3', '.wav', '.ogg']
        self.supported_video_formats = ['.mp4', '.webm', '.avi']
        
        # Tamaño máximo para archivos - 20 MB
        self.max_file_size = 20 * 1024 * 1024
    
    def get_media_path(self, filename):
        """Obtiene la ruta completa a un archivo multimedia."""
        return os.path.join(self.media_dir, filename)
    
    def import_media_file(self, source_path):
        """
        Importa un archivo multimedia al directorio de medios.
        
        Args:
            source_path: Ruta al archivo a importar
            
        Returns:
            Tuple (éxito, ID único o mensaje de error)
        """
        try:
            # Verificar tamaño
            file_size = os.path.getsize(source_path)
            if file_size > self.max_file_size:
                return False, f"Archivo demasiado grande (máximo: 20 MB)"
            
            # Obtener extensión
            _, ext = os.path.splitext(source_path)
            ext = ext.lower()
            
            # Verificar tipo soportado
            if ext not in self.supported_image_formats + self.supported_audio_formats + self.supported_video_formats:
                return False, f"Formato de archivo no soportado: {ext}"
            
            # Generar nombre único
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}{ext}"
            target_path = self.get_media_path(filename)
            
            # Copiar archivo
            shutil.copy2(source_path, target_path)
            
            # Devolver ID para referencia
            return True, filename
        except Exception as e:
            return False, f"Error al importar archivo: {str(e)}"
    
    def get_media_type(self, filename):
        """
        Determina el tipo de un archivo multimedia.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Tipo de archivo ('image', 'audio', 'video' o 'unknown')
        """
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        if ext in self.supported_image_formats:
            return 'image'
        elif ext in self.supported_audio_formats:
            return 'audio'
        elif ext in self.supported_video_formats:
            return 'video'
        return 'unknown'
    
    def get_image_as_base64(self, filename, max_width=800):
        """
        Convierte una imagen a formato base64 para mostrar en HTML.
        
        Args:
            filename: Nombre del archivo
            max_width: Ancho máximo para redimensionar
            
        Returns:
            String en formato "data:image/png;base64,..."
        """
        try:
            image_path = self.get_media_path(filename)
            img = QImage(image_path)
            
            # Redimensionar si es necesario
            if img.width() > max_width:
                img = img.scaledToWidth(max_width, Qt.TransformationMode.SmoothTransformation)
            
            # Convertir a PNG
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            img.save(buffer, "PNG")
            
            # Codificar en base64
            base64_data = base64.b64encode(byte_array.data()).decode('utf-8')
            
            # Determinar tipo MIME
            _, ext = os.path.splitext(filename)
            mime_type = self._get_mime_type(ext)
            
            return f"data:{mime_type};base64,{base64_data}"
        except Exception as e:
            print(f"Error al procesar imagen: {e}")
            return ""
    
    def get_html_for_media(self, filename, width=None, height=None, align='center'):
        """
        Genera código HTML para mostrar un elemento multimedia.
        
        Args:
            filename: Nombre del archivo
            width: Ancho del elemento (opcional)
            height: Alto del elemento (opcional)
            align: Alineación ('left', 'center', 'right')
            
        Returns:
            Código HTML para mostrar el elemento
        """
        media_type = self.get_media_type(filename)
        
        # Determinar dimensiones
        width_attr = f'width="{width}"' if width else 'style="max-width: 100%"'
        height_attr = f'height="{height}"' if height else ''
        align_style = f'style="text-align: {align};"'
        
        if media_type == 'image':
            # Para imágenes, usar base64 para mostrar directamente
            img_data = self.get_image_as_base64(filename)
            return f'<div {align_style}><img src="{img_data}" {width_attr} {height_attr} alt="Imagen" /></div>'
        
        elif media_type == 'audio':
            # Para audio, usar un reproductor de audio
            return f'<div {align_style}><audio controls {width_attr}><source src="file://{self.get_media_path(filename)}" type="audio/mpeg">Tu navegador no soporta el elemento audio.</audio></div>'
            
        elif media_type == 'video':
            # Para video, usar un reproductor de video
            return f'<div {align_style}><video controls {width_attr} {height_attr}><source src="file://{self.get_media_path(filename)}" type="video/mp4">Tu navegador no soporta el elemento video.</video></div>'
            
        return f'<div {align_style}>[Archivo no compatible: {filename}]</div>'
    
    def delete_media_file(self, filename):
        """
        Elimina un archivo multimedia.
        
        Args:
            filename: Nombre del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            file_path = self.get_media_path(filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error al eliminar archivo: {e}")
            return False
    
    def _get_mime_type(self, ext):
        """Determina el tipo MIME en base a la extensión."""
        ext = ext.lower()
        
        if ext in ['.jpg', '.jpeg']:
            return 'image/jpeg'
        elif ext == '.png':
            return 'image/png'
        elif ext == '.gif':
            return 'image/gif'
        elif ext == '.bmp':
            return 'image/bmp'
        elif ext == '.mp3':
            return 'audio/mpeg'
        elif ext == '.wav':
            return 'audio/wav'
        elif ext == '.ogg':
            return 'audio/ogg'
        elif ext == '.mp4':
            return 'video/mp4'
        elif ext == '.webm':
            return 'video/webm'
        elif ext == '.avi':
            return 'video/x-msvideo'
        
        return 'application/octet-stream'


class MediaInsertDialog(QDialog):
    """Diálogo para insertar contenido multimedia en una nota."""
    
    media_selected = pyqtSignal(str, int, int, str)  # filename, width, height, align
    
    def __init__(self, multimedia_manager, parent=None):
        super().__init__(parent)
        self.multimedia_manager = multimedia_manager
        self.selected_file = ""
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        self.setWindowTitle("Insertar multimedia")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Selector de archivo
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        file_layout.addWidget(self.file_path)
        
        browse_btn = QPushButton("Examinar...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        # Opciones de visualización
        options_layout = QHBoxLayout()
        
        # Ancho
        options_layout.addWidget(QLabel("Ancho:"))
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Auto")
        options_layout.addWidget(self.width_input)
        
        # Alto
        options_layout.addWidget(QLabel("Alto:"))
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Auto")
        options_layout.addWidget(self.height_input)
        
        layout.addLayout(options_layout)
        
        # Alineación
        align_layout = QHBoxLayout()
        align_layout.addWidget(QLabel("Alineación:"))
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Izquierda", "Centro", "Derecha"])
        self.align_combo.setCurrentIndex(1)  # Centro por defecto
        align_layout.addWidget(self.align_combo)
        layout.addLayout(align_layout)
        
        # Vista previa (para imágenes)
        self.preview_label = QLabel("Vista previa no disponible")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        layout.addWidget(self.preview_label)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Botones
        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        insert_btn = QPushButton("Insertar")
        insert_btn.clicked.connect(self.insert_media)
        buttons_layout.addWidget(insert_btn)
        layout.addLayout(buttons_layout)
    
    def browse_file(self):
        """Abre un diálogo para seleccionar un archivo multimedia."""
        formats = []
        formats.extend(self.multimedia_manager.supported_image_formats)
        formats.extend(self.multimedia_manager.supported_audio_formats)
        formats.extend(self.multimedia_manager.supported_video_formats)
        
        # Crear filtro para el diálogo
        filter_str = "Archivos multimedia ("
        for fmt in formats:
            filter_str += f"*{fmt} "
        filter_str = filter_str.strip() + ")"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo multimedia", "", filter_str
        )
        
        if file_path:
            # Mostrar ruta en el campo
            self.file_path.setText(file_path)
            
            # Si es una imagen, mostrar vista previa
            _, ext = os.path.splitext(file_path)
            if ext.lower() in self.multimedia_manager.supported_image_formats:
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # Escalar para mantener proporciones
                    pixmap = pixmap.scaled(
                        300, 200, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.preview_label.setPixmap(pixmap)
                else:
                    self.preview_label.setText("No se pudo cargar la vista previa")
            else:
                self.preview_label.setText(f"Archivo {ext}: Vista previa no disponible")
    
    def insert_media(self):
        """Procesa e inserta el archivo multimedia."""
        file_path = self.file_path.text()
        if not file_path:
            QMessageBox.warning(self, "Error", "Por favor selecciona un archivo.")
            return
        
        # Mostrar barra de progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        
        # Importar archivo al directorio de medios
        success, result = self.multimedia_manager.import_media_file(file_path)
        self.progress_bar.setValue(70)
        
        if not success:
            self.progress_bar.setVisible(False)
            QMessageBox.warning(self, "Error", result)
            return
        
        # Obtener parámetros de visualización
        filename = result
        
        # Procesar dimensiones
        width = None
        if self.width_input.text():
            try:
                width = int(self.width_input.text())
            except ValueError:
                width = None
        
        height = None
        if self.height_input.text():
            try:
                height = int(self.height_input.text())
            except ValueError:
                height = None
        
        # Obtener alineación
        align_index = self.align_combo.currentIndex()
        align = ["left", "center", "right"][align_index]
        
        self.progress_bar.setValue(100)
        
        # Emitir señal con los parámetros
        self.media_selected.emit(filename, width, height, align)
        
        # Cerrar diálogo
        self.accept()
