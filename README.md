# NoteLite

Una aplicación de notas moderna y ligera similar a Notion, desarrollada con Python y PyQt6.

## Características

- **Notas con texto enriquecido**: Permite crear y editar notas con formato (negrita, cursiva, listas, etc.)
- **Listas de tareas**: Crea listas de tareas con casillas de verificación
- **Atajos de teclado**: Totalmente personalizables para funciones comunes
- **Organización en páginas**: Estructura similar a Notion
- **Búsqueda rápida**: Encuentra notas por título y contenido
- **Almacenamiento local**: Todas las notas se guardan localmente
- **Interfaz moderna**: Diseño minimalista y atractivo

## Requisitos

- Python 3.6+
- PyQt6
- PyQt6-WebEngine
- Markdown

## Instalación

1. Clona o descarga este repositorio:
```
git clone https://github.com/tu-usuario/notelite.git
cd notelite
```

2. Instala las dependencias:
```
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```
python src/main.py
```

## Empaquetado para Windows

Para crear un ejecutable para Windows, puedes usar PyInstaller:

1. Instala PyInstaller:
```
pip install pyinstaller
```

2. Crea el ejecutable:
```
pyinstaller --name=NoteLite --windowed --icon=assets/icon.ico --add-data="assets/style.qss;assets" src/main.py
```

El ejecutable final se creará en la carpeta `dist/NoteLite/`.

## Estructura del proyecto

- `src/`: Código fuente de la aplicación
  - `main.py`: Punto de entrada de la aplicación
  - `note_editor.py`: Editor de notas con formato enriquecido
  - `task_list.py`: Componente para listas de tareas
  - `data_manager.py`: Gestión de datos y almacenamiento
  - `shortcuts.py`: Manejo de atajos de teclado
- `assets/`: Recursos como hojas de estilo e iconos
  - `style.qss`: Estilos CSS para la interfaz

## Personalización

### Añadir nuevos atajos de teclado

Para añadir un nuevo atajo de teclado, edita el archivo `src/shortcuts.py` y modifica el método `_load_config()` para incluir tu nuevo atajo. También tendrás que registrar el atajo usando el método `register_shortcut()` en la clase `NoteLiteApp`.

### Modificar la apariencia

Puedes personalizar la apariencia editando el archivo `assets/style.qss`, que sigue una sintaxis similar a CSS.

## Licencia

Este proyecto está licenciado bajo [MIT License](LICENSE).
