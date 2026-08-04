# PulseTask v2 Quick Start Guide

## ⚡ Ejecutar la Aplicación

```bash
# Iniciar servidor de desarrollo
make run

# O manualmente:
npm run dev
```

El servidor estará disponible en: **http://localhost:3000**

## 🔧 Configuración Inicial (Solo primera vez)

```bash
# Instalar dependencias
make install

# Ejecutar
make run

# Compilar para producción
make build
```

## 📋 Comandos Disponibles

```bash
make install       # Instalar dependencias
make dev           # Servidor de desarrollo
make build         # Compilar para producción
make start         # Iniciar servidor de producción
make lint          # Verificar código
make clean         # Limpiar caché y node_modules
make run           # Alias para 'make dev'
make help          # Mostrar todos los comandos
```

## ❌ Errores Comunes

### Error: "Module not found"
```bash
make install
make run
```

### Error: Puerto 3000 en uso
```bash
# Encuentra el proceso en puerto 3000
lsof -i :3000

# O usa un puerto diferente:
PORT=3001 npm run dev
```

### Error: "Command not found: npm"
Asegúrate de tener Node.js instalado:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 22
nvm use 22
```

## 📁 Estructura del Proyecto

```
pulseTask/
├── app/            # Next.js app router
├── components/     # Componentes React (60+)
├── lib/            # Lógica y estado (Zustand)
├── hooks/          # React hooks custom
├── public/         # Assets estáticos
├── styles/         # Estilos globales
├── package.json    # Dependencias
└── tsconfig.json   # Configuración TypeScript
```

## 🚀 Próximos Pasos

1. Ejecutar: `make run`
2. Abrir: http://localhost:3000
3. Leer: [START_HERE.md](START_HERE.md)
4. Explorar: [README_REDESIGN.md](README_REDESIGN.md)

## 📚 Documentación Completa

- **START_HERE.md** - Guía rápida
- **README_REDESIGN.md** - Documentación del rediseño
- **MIGRATION_SUMMARY.md** - Detalles de la migración
- **REDESIGN_APPLIED.txt** - Checklist de implementación

