#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de sincronización para NoteLite.
Permite la sincronización con servicios en la nube, respaldo automático y exportación.
"""

import os
import json
import shutil
import zipfile
import datetime
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal

class SyncManager(QObject):
    """
    Gestor de sincronización para NoteLite.
    Permite sincronizar notas con diferentes servicios y realizar respaldos automáticos.
    """
    
    # Señales
    sync_started = pyqtSignal()
    sync_finished = pyqtSignal(bool, str)  # éxito, mensaje
    backup_finished = pyqtSignal(bool, str)  # éxito, mensaje
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.sync_path = os.path.join(os.path.expanduser("~"), "NoteLite", "sync")
        self.backup_path = os.path.join(os.path.expanduser("~"), "NoteLite", "backups")
        
        # Asegurar que los directorios existan
        os.makedirs(self.sync_path, exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        
        # Configurar temporizador para respaldo automático
        self.backup_timer = None
        
    def start_auto_backup(self, interval_minutes=30):
        """Inicia el respaldo automático con el intervalo especificado."""
        if self.backup_timer is None:
            self.backup_timer = threading.Timer(interval_minutes * 60, self._auto_backup_task)
            self.backup_timer.daemon = True
            self.backup_timer.start()
    
    def stop_auto_backup(self):
        """Detiene el respaldo automático."""
        if self.backup_timer:
            self.backup_timer.cancel()
            self.backup_timer = None
    
    def _auto_backup_task(self):
        """Tarea de respaldo automático que se ejecuta periódicamente."""
        self.create_backup()
        # Reiniciar el temporizador para la próxima ejecución
        self.backup_timer = threading.Timer(30 * 60, self._auto_backup_task)
        self.backup_timer.daemon = True
        self.backup_timer.start()
    
    def create_backup(self):
        """Crea un respaldo de todas las notas."""
        try:
            # Crear nombre de archivo con marca de tiempo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_path, f"notelite_backup_{timestamp}.zip")
            
            # Crear archivo ZIP
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Añadir archivos de notas
                notes_dir = os.path.join(os.path.expanduser("~"), "NoteLite", "notes")
                if os.path.exists(notes_dir):
                    for root, _, files in os.walk(notes_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(notes_dir))
                            zipf.write(file_path, arcname)
                
                # Añadir configuración
                config_dir = os.path.join(os.path.expanduser("~"), "NoteLite", "config")
                if os.path.exists(config_dir):
                    for root, _, files in os.walk(config_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(config_dir))
                            zipf.write(file_path, arcname)
            
            # Limpiar respaldos antiguos (mantener solo los 5 más recientes)
            self._clean_old_backups()
            
            self.backup_finished.emit(True, f"Respaldo creado: {os.path.basename(backup_file)}")
            return True, backup_file
        except Exception as e:
            self.backup_finished.emit(False, f"Error al crear respaldo: {str(e)}")
            return False, str(e)
    
    def _clean_old_backups(self, keep=5):
        """Limpia respaldos antiguos, manteniendo solo los más recientes."""
        try:
            backups = []
            for file in os.listdir(self.backup_path):
                if file.startswith("notelite_backup_") and file.endswith(".zip"):
                    full_path = os.path.join(self.backup_path, file)
                    backups.append((full_path, os.path.getmtime(full_path)))
            
            # Ordenar por fecha de modificación (más reciente primero)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Eliminar los más antiguos
            for path, _ in backups[keep:]:
                os.remove(path)
        except Exception as e:
            print(f"Error al limpiar respaldos antiguos: {e}")
    
    def export_notes(self, export_dir, format="json"):
        """Exporta todas las notas al directorio especificado."""
        try:
            os.makedirs(export_dir, exist_ok=True)
            
            # Obtener todas las notas
            notes = self.data_manager.get_all_notes()
            
            # Exportar según el formato
            if format == "json":
                for note_id, note_data in notes.items():
                    file_path = os.path.join(export_dir, f"{note_id}.json")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(note_data, f, ensure_ascii=False, indent=2)
            
            elif format == "txt":
                for note_id, note_data in notes.items():
                    file_path = os.path.join(export_dir, f"{note_data.get('title', 'Nota sin título')}.txt")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Título: {note_data.get('title', 'Sin título')}\n")
                        f.write(f"Fecha: {note_data.get('updated_at', '')}\n")
                        f.write("\n" + self._html_to_text(note_data.get('content', '')))
            
            elif format == "html":
                for note_id, note_data in notes.items():
                    file_path = os.path.join(export_dir, f"{note_data.get('title', 'Nota sin título')}.html")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"<html><head><title>{note_data.get('title', 'Sin título')}</title></head>")
                        f.write("<body>")
                        f.write(f"<h1>{note_data.get('title', 'Sin título')}</h1>")
                        f.write(f"<p><em>Fecha: {note_data.get('updated_at', '')}</em></p>")
                        f.write(note_data.get('content', ''))
                        f.write("</body></html>")
            
            return True, f"Notas exportadas a {export_dir}"
        except Exception as e:
            return False, f"Error al exportar notas: {str(e)}"
    
    def _html_to_text(self, html_content):
        """Convierte contenido HTML a texto plano (implementación básica)."""
        # Esta es una implementación muy básica, idealmente usaríamos BeautifulSoup
        text = html_content
        text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        text = text.replace('<p>', '\n').replace('</p>', '\n')
        text = text.replace('<div>', '\n').replace('</div>', '\n')
        text = text.replace('<li>', '\n- ').replace('</li>', '')
        
        # Eliminar otras etiquetas HTML (implementación muy básica)
        while '<' in text and '>' in text:
            start = text.find('<')
            end = text.find('>', start)
            if start != -1 and end != -1:
                text = text[:start] + text[end+1:]
            else:
                break
        
        return text
    
    def simulate_cloud_sync(self):
        """
        Simula una sincronización con la nube.
        En una implementación real, esto se conectaría con un servicio como Dropbox, Google Drive, etc.
        """
        self.sync_started.emit()
        
        # Simulamos un proceso que toma tiempo
        def sync_process():
            time.sleep(2)  # Simulamos que la sincronización toma 2 segundos
            
            # Copiar los archivos de notas al directorio de sincronización
            try:
                notes_dir = os.path.join(os.path.expanduser("~"), "NoteLite", "notes")
                sync_notes_dir = os.path.join(self.sync_path, "notes")
                os.makedirs(sync_notes_dir, exist_ok=True)
                
                if os.path.exists(notes_dir):
                    for file in os.listdir(notes_dir):
                        if file.endswith(".json"):
                            shutil.copy2(
                                os.path.join(notes_dir, file),
                                os.path.join(sync_notes_dir, file)
                            )
                
                # Crear un archivo de metadatos para simular información de sincronización
                meta_file = os.path.join(self.sync_path, "sync_meta.json")
                with open(meta_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "last_sync": datetime.datetime.now().isoformat(),
                        "device": "PC",
                        "status": "success"
                    }, f, ensure_ascii=False, indent=2)
                
                self.sync_finished.emit(True, "Sincronización completada con éxito")
            except Exception as e:
                self.sync_finished.emit(False, f"Error en sincronización: {str(e)}")
        
        # Iniciar proceso en un hilo separado
        threading.Thread(target=sync_process, daemon=True).start()
        return True, "Sincronización iniciada"
