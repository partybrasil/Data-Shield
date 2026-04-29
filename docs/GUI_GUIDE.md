# Guía de la Interfaz Gráfica (GUI) — Windows 11 Fluent Design 🎨

Data-Shield presenta una interfaz **premium y moderna** basada en **Windows 11 Fluent Design System**, construida con **PySide6** y **qfluentwidgets** para ofrecer una experiencia de seguridad profesional y responsiva.

---

## 🚀 Inicio Rápido

Para lanzar la interfaz gráfica:

```bash
# Instalar dependencias de GUI (si no lo has hecho)
pip install -e ".[gui]"

# Lanzar la interfaz
python -m datashield --gui

# O simplemente hacer doble clic en datashield.exe (distribución)
```

---

## 🎨 Arquitectura Visual — Fluent Design

### Componentes Principales

#### 1. **Barra de Título Dinámica** 📊
Monitoreo de recursos en tiempo real en la barra de título:
- **CPU**: Porcentaje de uso del procesador
- **RAM**: Consumo de memoria RAM
- **GPU**: Carga de tarjeta gráfica (si disponible)
- **Resolución**: Dimensiones actuales de la ventana
- **Ejemplo**: `Data-Shield - Premium Security [CPU: 12% | RAM: 45% | GPU: 8% | Res: 1920x1080]`

#### 2. **Navegación Lateral (NavSidebar)** 🧭
Panel izquierdo con acceso rápido a todas las funcionalidades:
- 🔍 **Scanner**: Escaneo de credenciales y secretos
- 🔐 **Vault**: Gestión de cifrado y almacenamiento seguro
- 👀 **Monitor**: Vigilancia en tiempo real del sistema
- ⚙️ **Settings**: Configuración de preferencias (abajo del sidebar)

Cada pestaña se selecciona con un clic y la navegación es suave.

#### 3. **Tema Neon Dark Personalizado** 💎
Paleta de colores moderna inspirada en Material Modern y Neon Cyberpunk:
- **Primary Cyan**: `#00f2ff` (botones, bordes, highlights)
- **Secondary Magenta**: `#ff00ff` (acentos, errores)
- **Lime**: `#00ffaa` (éxito, headers)
- **Orange**: `#ff6b00` (advertencias)
- **Background**: `#05070a` (oscuro profundo)
- **Surface**: `#0b0e14` (paneles)

#### 4. **Efectos Visuales Fluent** ✨
- **Transparencia Mica**: Fondo semi-transparente del window frame
- **Bordes Redondeados**: Todos los elementos con radio 8-10px
- **Gradientes**: Buttons con gradientes Cyan → Blue
- **Glow Effects**: Bordes luminosos en elementos activos
- **Animaciones Suaves**: Transiciones de 300-500ms

---

## 📋 Panel de Escaneo (Scanner)

### Interfaz Principal

```
┌─ Data-Shield - Premium Security [CPU: 12% | RAM: 45% | Res: 1920x1080] ─────┐
│                                                                                 │
│  Scanner │ Vault │ Monitor │ Settings                                          │
│                                                                                 │
│  ▌ System Security Scan                                                        │
│                                                                                 │
│  Path: [C:\Users\usuario\________] [📁 Browse]                               │
│  Mode: [SAFE ▼]  Depth: [0 (unlimited) ▼]  Threads: [4]                     │
│  ☐ Include Hidden   ☐ Deep Analysis    [🔵 SCAN] [🛑 STOP]                   │
│                                                                                 │
│  ████████████░░░░░░░  62%  │  14,382 / 23,100 archivos  │  ETA: 00:01:34    │
│                                                                                 │
│  ▌ Scan Findings                            Filter: [All Types ▼]            │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │ Archivo         │ Tipo       │ App      │ Riesgo     │ Detalles │ Acciones│ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │ id_rsa          │ SSH Key    │ Git      │ 🔴 CRITICAL│ ⓘ │ 🔐 🗂️ │ │
│  │ credentials     │ AWS Creds  │ AWS CLI  │ 🔴 CRITICAL│ ⓘ │ 🔐 🗂️ │ │
│  │ hosts.yml       │ OAuth      │ GitHub   │ 🟠 HIGH    │ ⓘ │ 🔐 🗂️ │ │
│  │ .git-cred...    │ Tokens     │ Git      │ 🟠 HIGH    │ ⓘ │ 🔐 🗂️ │ │
│  │ cookies.sqlite  │ Cookies    │ Chrome   │ 🟡 MEDIUM  │ ⓘ │ 🔐 🗂️ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│  ✓ 47 hallazgos   ● Escaneando...                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Características del Scanner Panel

#### **Selección de Ruta**
- Campo de texto con explorador de carpetas integrado
- Browse button (`📁`) para seleccionar directorios
- Validación de ruta en tiempo real

#### **Opciones de Escaneo**
- **Mode**: Selector con 5 modos (`ULTRA_FAST`, `FAST`, `SAFE`, `DEEP`, `INTERACTIVE`)
- **Depth**: Profundidad de recursión (0 = ilimitado)
- **Threads**: Número de hilos (1-32, por defecto 4)
- **Checkboxes**: Include Hidden, Deep Analysis

#### **Controles**
- **🔵 SCAN Button**: Inicia el escaneo (deshabilitado durante operación)
- **🛑 STOP Button**: Pausa/detiene el escaneo (mantiene resultados parciales)

#### **Barra de Progreso Animada**
```
████████████░░░░░░░  62%  │  14,382 / 23,100 archivos  │  Tiempo: 00:02:34  │  ETA: 00:01:34
```
- Actualización fluida en tiempo real
- Porcentaje, archivos procesados, tiempo y ETA

#### **Tabla de Resultados Interactiva**

| Columna | Descripción |
|---------|------------|
| **Archivo** | Nombre del archivo (truncado si es largo) |
| **Tipo** | Tipo de credencial (SSH Key, AWS, JWT, etc.) |
| **App** | Aplicación responsable (Git, AWS CLI, Docker, etc.) |
| **Riesgo** | Nivel (🔴 CRITICAL, 🟠 HIGH, 🟡 MEDIUM, 🔵 LOW) |
| **Detalles** | Botón `ⓘ` para ver información completa |
| **Acciones** | 🔐 Guardar en Vault, 🗂️ Abrir en Explorer |

##### **Filtro Dinámico**
- Dropdown "Filter by type..." en la esquina superior derecha
- Opciones: "All Types", "SSH Keys", "AWS Creds", "OAuth Tokens", etc.
- Se actualiza **en tiempo real** conforme se descubren nuevos tipos
- El filtrado **no detiene** el escaneo en progreso

---

## 🔐 Panel de Vault

### Características Principales

- 🔓 **Unlock**: Ingresa contraseña maestra para desbloquear el Vault
- 🔒 **Lock**: Cifra inmediatamente todos los archivos del Vault
- 📋 **Inventario**: Lista de archivos cifrados con metadatos
- ➕ **Add Entry**: Cifra nuevos archivos selectivamente
- ➖ **Remove**: Descifra y elimina entradas del Vault
- 📊 **Stats**: Cantidad de entradas, tamaño total, última modificación

### Flujo de Uso

1. **Primera Vez**: Establece contraseña maestra (PBKDF2 + AES-256-GCM)
2. **Cifrar**: Elige archivos, la app cifra y almacena en Vault
3. **Desbloquear**: Ingresa contraseña al iniciar sesión (automático si se configuró)
4. **Usar**: Accede a archivos descifrados temporalmente
5. **Bloquear**: Al apagar, automáticamente se cifran nuevamente

---

## 👀 Panel de Monitor (Watchdog)

### Vigilancia en Tiempo Real

- **Estado**: On/Off toggle
- **Rutas a Monitorear**: Lista editable de directorios
- **Whitelist**: Rutas excluidas de alertas
- **Notificaciones Toast**: Alerts nativos de Windows 10/11
- **Log de Eventos**: Historial de cambios detectados
- **Tray Icon**: Indicador visual en la bandeja del sistema

### Eventos Monitoreados

- ✏️ Archivos creados/modificados
- 🗑️ Archivos eliminados
- 📝 Cambios en permisos
- 🔗 Cambios en enlaces simbólicos

---

## ⚙️ Panel de Settings

### Configuraciones de Escaneo

#### **Exclusiones**
- Campo de texto: ingresa carpetas separadas por comas
- Ejemplo: `node_modules, venv, .git, .venv, __pycache__, .cache`
- Se persisten entre sesiones

#### **Threads (Multi-threading)**
- Selector 1-32 (recomendado: CPUs / 2)
- Ejemplo: 4 threads en CPU de 8 núcleos
- Impacto: Más threads = más rápido, pero más CPU

#### **Opciones de Tema**
- Toggle: Modo Oscuro / Modo Claro (futuro)
- Persistencia: Se guarda en QSettings

---

## 💾 Persistencia de Estado

Data-Shield **recuerda automáticamente**:
- ✅ Tamaño y posición de la ventana
- ✅ Última ruta escaneada
- ✅ Modo de escaneo preferido
- ✅ Número de threads
- ✅ Carpetas excluidas
- ✅ Posición del splitter (si la hay)

**Ubicación**: `C:\Users\tu-usuario\AppData\Roaming\DataShield\`

---

## 🎯 Flujos de Trabajo Típicos

### 1. Escaneo Rápido de Rutas Críticas
```
1. Seleccionar: C:\Users\usuario\.ssh
2. Mode: ULTRA_FAST (solo nombres)
3. Hilos: 8
4. Click SCAN
5. Resultado: < 2 segundos
```

### 2. Escaneo Profundo Completo
```
1. Seleccionar: C:\Users\usuario
2. Mode: DEEP (análisis completo)
3. Hilos: 4 (reducir para no saturar)
4. Include Hidden: ✓
5. Click SCAN
6. Resultado: 5-15 minutos (depende del sistema)
```

### 3. Guardar Hallazgos en Vault
```
1. Ejecutar escaneo
2. Seleccionar filas específicas
3. Click 🔐 (Save to Vault)
4. Automáticamente cifrado y almacenado
5. Revisar en panel Vault → Unlock
```

---

## 🔧 Troubleshooting

| Problema | Solución |
|----------|----------|
| GUI lenta / laggy | Reducir hilos, usar FAST mode en lugar de DEEP |
| Notificaciones no aparecen | Verificar permisos de notificaciones en Windows 10/11 |
| Vault no se desbloquea | Reiniciar app, verificar contraseña maestra |
| Monitor consume mucho CPU | Usar whitelist agresiva, excluir carpetas grandes |

---

## 📱 Requisitos Mínimos

- **Pantalla**: 1920x1080 (recomendado)
- **Windows**: 10 (build 1903+) o 11
- **Python**: 3.13 LTS
- **RAM**: 512MB (aplicación), 4GB+ (sistema)

---

## 🎓 Guía de Desarrollo

Ver `src/datashield/gui/` para:
- `main_window.py`: Ventana principal y coordinación
- `widgets.py`: Componentes específicos (ScanPanel, VaultPanel, etc.)
- `theme.py`: Gestor de temas (dark, light, customizaciones)
- `workers.py`: Threads para operaciones no-bloqueantes
- `app.py`: Inicialización de QApplication

---

*Estado actual: v0.1.0 (Windows 11 Premium Fluent Design — Production Ready)*
