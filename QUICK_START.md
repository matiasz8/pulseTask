# PulseTask Quick Start Guide

## ⚡ Ejecutar la Aplicación

```bash
# Comando correcto (Python, no Node.js)
make run

# O manualmente:
uv run pulsetask
```

## 🔧 Configuración Inicial (Solo primera vez)

```bash
# Crear virtual environment
make venv

# Instalar dependencias
make sync

# Ejecutar
make run
```

## 📋 Comandos Disponibles

```bash
make test          # Ejecutar tests (151 tests)
make lint          # Verificar código
make typecheck     # Type checking
make run           # Ejecutar app
make ci            # Lint + typecheck + test
```

## ❌ Errores Comunes

### Error: "GTK4/libadwaita is not available"
```bash
# En Ubuntu/Debian:
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libnotify-bin

# Luego recrear el venv:
rm -rf .venv
make venv
make sync
make run
```

### Error: "npm run dev" no existe
Este es un proyecto **Python**, no Node.js
- ❌ `npm run dev` (Node.js)
- ✅ `make run` (Python)

### Error: "module not found"
```bash
make venv
make sync
make run
```

## 📁 Estructura del Proyecto

```
pulseTask/
├── src/pulse_task/     # Código fuente
│   ├── core/           # Lógica de negocio
│   ├── ui/             # Interfaz GTK4
│   └── dbus/           # Integración GNOME
├── tests/              # Tests
├── docs/               # Documentación
└── data/               # Metadatos desktop/dbus
```

## 🚀 Próximos Pasos

Ver: [FINAL_PROJECT_STATUS.md](FINAL_PROJECT_STATUS.md)

- Flathub submission
- Community launch (Reddit, HackerNews)
- v0.3.0 GNOME integration

## 📚 Documentación Completa

- **README.md** - Overview del proyecto
- **CONTRIBUTING.md** - Guía de contribución
- **docs/API.md** - API documentation
- **docs/ARCHITECTURE.md** - Arquitectura
- **docs/marketing/** - Guías de marketing para launch
