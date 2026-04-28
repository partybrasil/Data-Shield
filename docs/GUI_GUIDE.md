# Guía de la Interfaz Gráfica (GUI) 🎨

Data-Shield cuenta con una interfaz moderna basada en **Fluent Design** de Windows 11, diseñada para ofrecer una experiencia premium y profesional de seguridad.

## 🚀 Inicio Rápido
Para lanzar la interfaz gráfica, simplemente ejecuta:
```bash
# Asegúrate de tener las dependencias de la GUI instaladas
pip install -e ".[gui]"

# Lanzar la interfaz
python -m datashield --gui
```

## 📋 Características Principales

### 1. Monitor de Recursos (Título)
La barra de título dinámica muestra en tiempo real:
- **CPU**: Uso de procesador.
- **RAM**: Consumo de memoria.
- **GPU**: Carga de la tarjeta gráfica (si está disponible).
- **Resolución**: Dimensiones actuales de la ventana.

### 2. Navegación Lateral
Utiliza la barra lateral para moverte entre los diferentes módulos:
- 🔍 **Scanner**: Panel principal para buscar credenciales.
- 🔐 **Vault**: Gestión de archivos cifrados y caja fuerte.
- 👤 **Monitor**: Seguimiento en tiempo real de cambios en el sistema.
- ⚙️ **Settings**: Configuración de hilos, exclusiones y preferencias.

## ✨ Características Principales
- **Escaneo Inteligente**:
    - **Visualización en tiempo real**: Los secretos aparecen en la lista conforme se encuentran.
    - **Filtro dinámico**: Un selector discreto permite ver solo tipos específicos (ej. solo "SSH Keys") sin detener el escaneo.
    - **Control total**: Botón de parada inmediata que conserva los resultados parciales.
- **Nuevos Modos de Escaneo**:
    - **ULTRA_FAST**: Instantáneo, solo nombres de archivos.
    - **FAST**: Rápido, Regex y YARA en cabeceras.
    - **SAFE**: Estándar, análisis profundo de 1MB por archivo (Recomendado).
    - **DEEP**: Paranoico, analiza el archivo completo y busca alta entropía.
    - **INTERACTIVE**: Te pregunta qué hacer con cada hallazgo al momento.
- **Personalización y Persistencia**:
    - La aplicación recuerda el tamaño de tu ventana, posición y hilos de escaneo.
    - Monitor de recursos (CPU/RAM/GPU) en la barra de título para vigilar el impacto en el sistema.

## 📸 Capturas de Pantalla

### Panel de Escaneo
![Fluent Scanner](../docs/images/gui_fluent_scanner.png)
*Interfaz limpia con barra de progreso estilizada y tabla de resultados con niveles de riesgo.*

## ⚙️ Configuración Avanzada
En el panel de **Settings**, puedes ajustar el rendimiento:
- **Max Threads**: Aumenta para escaneos más rápidos en CPUs multi-core.
- **Exclusions**: Añade carpetas separadas por comas que no deseas analizar (ej: node_modules, .git).

---
*Estado actual: v0.1.0 (Fluent UI Migrated)*
