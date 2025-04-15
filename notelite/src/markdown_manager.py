#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gestor de markdown para NoteLite.
Permite convertir texto markdown a HTML con estilos retro.
"""

import re
import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
import xml.etree.ElementTree as etree

class RetroMarkdownManager:
    """
    Gestor para convertir markdown a HTML con estilos retro.
    Incluye características especiales como bloques ASCII art.
    """
    
    def __init__(self, theme_manager=None):
        """Inicializa el gestor de markdown."""
        self.theme_manager = theme_manager
        
        # Configurar extensiones de markdown
        self.extensions = [
            'tables',
            'fenced_code',
            'nl2br',
            AsciiArtExtension(),
            RetroElementsExtension(),
            'codehilite'
        ]
    
    def markdown_to_html(self, text):
        """
        Convierte texto markdown a HTML con estilos retro.
        
        Args:
            text: Texto en formato markdown
            
        Returns:
            HTML formateado con estilos retro
        """
        # Procesar el markdown
        html = markdown.markdown(text, extensions=self.extensions)
        
        # Aplicar estilos adicionales según el tema actual
        if self.theme_manager:
            current_theme = self.theme_manager.get_current_theme()
            if current_theme == "windows95":
                html = self._apply_windows95_styles(html)
            elif current_theme == "msdos":
                html = self._apply_msdos_styles(html)
            elif current_theme == "amiga":
                html = self._apply_amiga_styles(html)
            elif current_theme == "macintosh":
                html = self._apply_macintosh_styles(html)
            elif current_theme == "atari":
                html = self._apply_atari_styles(html)
        
        return html
    
    def _apply_windows95_styles(self, html):
        """Aplica estilos específicos del tema Windows 95."""
        # Reemplazar listas con iconos de Windows 95
        html = html.replace('<ul>', '<ul class="win95-list">')
        html = html.replace('<ol>', '<ol class="win95-list">')
        
        # Estilizar encabezados
        for i in range(1, 7):
            html = html.replace(f'<h{i}>', f'<h{i} class="win95-heading">')
        
        # Estilizar bloques de código
        html = html.replace('<pre><code>', '<pre class="win95-code"><code>')
        
        return html
    
    def _apply_msdos_styles(self, html):
        """Aplica estilos específicos del tema MS-DOS."""
        # Añadir efecto de fuente monoespaciada a todo
        html = f'<div class="msdos-text">{html}</div>'
        
        # Estilizar bloques de código con recuadro DOS
        html = html.replace('<pre><code>', '<pre class="dos-code"><code>')
        
        return html
    
    def _apply_amiga_styles(self, html):
        """Aplica estilos específicos del tema Amiga Workbench."""
        # Estilizar encabezados con el estilo Amiga
        for i in range(1, 7):
            html = html.replace(f'<h{i}>', f'<h{i} class="amiga-heading">')
        
        # Estilizar bloques de código
        html = html.replace('<pre><code>', '<pre class="amiga-code"><code>')
        
        return html
    
    def _apply_macintosh_styles(self, html):
        """Aplica estilos específicos del tema Macintosh Classic."""
        # Estilizar encabezados con el estilo Mac
        for i in range(1, 7):
            html = html.replace(f'<h{i}>', f'<h{i} class="mac-heading">')
        
        # Estilizar listas
        html = html.replace('<ul>', '<ul class="mac-list">')
        
        return html
    
    def _apply_atari_styles(self, html):
        """Aplica estilos específicos del tema Atari ST."""
        # Estilizar encabezados con el estilo Atari
        for i in range(1, 7):
            html = html.replace(f'<h{i}>', f'<h{i} class="atari-heading">')
        
        # Estilizar bloques de código
        html = html.replace('<pre><code>', '<pre class="atari-code"><code>')
        
        return html


class AsciiArtProcessor(Preprocessor):
    """Procesa bloques de ASCII art en markdown."""
    
    RE_ASCII_ART = re.compile(r'```ascii\s*\n(.*?)\n```', re.DOTALL)
    
    def run(self, lines):
        """
        Procesa el texto para identificar bloques de ASCII art.
        
        Args:
            lines: Lista de líneas de texto
            
        Returns:
            Lista de líneas procesadas
        """
        text = '\n'.join(lines)
        match = self.RE_ASCII_ART.search(text)
        
        while match:
            # Extraer el contenido ASCII
            ascii_content = match.group(1)
            
            # Reemplazar con un bloque pre especial
            replacement = f'<div class="ascii-art"><pre>{ascii_content}</pre></div>'
            text = text[:match.start()] + replacement + text[match.end():]
            
            # Buscar el siguiente bloque
            match = self.RE_ASCII_ART.search(text)
        
        return text.split('\n')


class AsciiArtExtension(Extension):
    """Extensión de markdown para ASCII art."""
    
    def extendMarkdown(self, md):
        """Añade el procesador al pipeline de markdown."""
        md.preprocessors.register(AsciiArtProcessor(md), 'ascii_art', 175)


class RetroElementPattern(InlineProcessor):
    """Procesa elementos retro en línea en markdown."""
    
    def handleMatch(self, m, data):
        """
        Maneja las coincidencias del patrón.
        
        Args:
            m: Objeto match con los grupos capturados
            data: Datos del texto
            
        Returns:
            Tuple (elemento, inicio, fin)
        """
        # Extraer tipo y contenido
        element_type = m.group(1)
        content = m.group(2)
        
        # Crear elementos según el tipo
        if element_type.lower() == 'pixel':
            el = etree.Element('span')
            el.set('class', 'pixel-text')
            el.text = content
        elif element_type.lower() == 'blink':
            el = etree.Element('span')
            el.set('class', 'blink-text')
            el.text = content
        elif element_type.lower() == 'retro':
            el = etree.Element('span')
            el.set('class', 'retro-text')
            el.text = content
        elif element_type.lower() == 'win':
            el = etree.Element('div')
            el.set('class', 'win95-window')
            title = etree.SubElement(el, 'div')
            title.set('class', 'win95-title')
            title.text = 'Ventana'
            body = etree.SubElement(el, 'div')
            body.set('class', 'win95-body')
            body.text = content
        else:
            el = etree.Element('span')
            el.text = content
        
        return el, m.start(0), m.end(0)


class RetroElementsExtension(Extension):
    """Extensión de markdown para elementos retro."""
    
    def extendMarkdown(self, md):
        """Añade el procesador al pipeline de markdown."""
        pattern = r':(\w+):(.*?)::(\w+):'
        processor = RetroElementPattern(pattern)
        md.inlinePatterns.register(processor, 'retro_elements', 175)


class MarkdownEditorHelper:
    """
    Clase auxiliar para proporcionar sugerencias y completado
    en el editor de markdown.
    """
    
    def __init__(self):
        """Inicializa el helper."""
        # Atajos comunes de markdown
        self.markdown_snippets = {
            "# ": "Encabezado 1",
            "## ": "Encabezado 2",
            "### ": "Encabezado 3",
            "**": "Texto en negrita",
            "*": "Texto en cursiva",
            "- ": "Elemento de lista",
            "1. ": "Lista numerada",
            "[": "Enlace",
            "![": "Imagen",
            "```": "Bloque de código",
            "```ascii": "Arte ASCII",
            "> ": "Cita",
            "--- ": "Línea horizontal",
            ":pixel:": "Texto pixelado",
            ":blink:": "Texto parpadeante",
            ":retro:": "Texto con estilo retro",
            ":win:": "Ventana de Windows 95"
        }
    
    def get_completion_options(self, current_text, cursor_position):
        """
        Obtiene opciones de autocompletado según el texto actual.
        
        Args:
            current_text: Texto actual en el editor
            cursor_position: Posición del cursor
            
        Returns:
            Lista de sugerencias de autocompletado
        """
        # Obtener el texto antes del cursor
        text_before_cursor = current_text[:cursor_position]
        
        # Verificar coincidencias con snippets
        suggestions = []
        for snippet, description in self.markdown_snippets.items():
            if snippet.startswith(text_before_cursor[-len(snippet):]):
                suggestions.append((snippet, description))
        
        return suggestions
    
    def insert_snippet(self, snippet_key):
        """
        Obtiene el código completo para un snippet.
        
        Args:
            snippet_key: Clave del snippet a insertar
            
        Returns:
            Tupla con el texto del snippet y la posición del cursor
        """
        if snippet_key == "**":
            return "**texto**", -2
        elif snippet_key == "*":
            return "*texto*", -1
        elif snippet_key == "[":
            return "[texto](url)", -1
        elif snippet_key == "![":
            return "![alt](url)", -1
        elif snippet_key == "```":
            return "```\ncódigo\n```", -4
        elif snippet_key == "```ascii":
            return "```ascii\n    ____    \n   /    \\   \n  | RETRO |  \n   \\____/   \n```", -4
        elif snippet_key == ":pixel:":
            return ":pixel:texto::pixel:", -9
        elif snippet_key == ":blink:":
            return ":blink:texto::blink:", -9
        elif snippet_key == ":retro:":
            return ":retro:texto::retro:", -9
        elif snippet_key == ":win:":
            return ":win:contenido de la ventana::win:", -7
        else:
            return snippet_key, 0
