# 🖥️ PulseTask Desktop - Ubuntu Installation Guide

**PulseTask v0.2.0** is now available as both a **web application** and a **native desktop application** for Ubuntu/Linux.

Both versions use the **same beautiful design** with the same features. Choose whichever works best for your workflow.

---

## 🎯 Choose Your Version

### Web Version
- Run in browser
- No installation needed
- Access from any device
- Command: `make dev` → http://localhost:3000

### Desktop Version (Recommended for Ubuntu)
- Native Ubuntu/Linux application
- Install as system app
- Desktop shortcuts and launcher integration
- No browser tab needed
- Command: `make dev-desktop` or `make run-desktop`

---

## 🚀 Quick Start - Desktop

### Option 1: Development Mode (Easiest)
```bash
cd /run/media/nquiroga/SSDedo/Documents/personal/pulseTask
make dev-desktop
```

This starts both the development server and the Electron app with hot reload.

### Option 2: Build & Install (.deb)
```bash
# Build for production
make build-desktop

# The .deb file will be created in dist/ directory
# Install it:
sudo dpkg -i dist/PulseTask-*.deb

# Or double-click to install with software center
```

### Option 3: Run AppImage
```bash
# Build creates an AppImage file too
make build-desktop

# Make it executable and run
chmod +x dist/PulseTask-*.AppImage
./dist/PulseTask-*.AppImage
```

---

## 📋 Desktop vs Web Comparison

| Feature | Desktop | Web |
|---------|---------|-----|
| Installation | .deb/.AppImage | None (browser) |
| Native Integration | ✅ Yes | No |
| Desktop Shortcuts | ✅ Yes | No |
| System Tray | ✅ Possible | No |
| Offline Use | ✅ Yes | No |
| Access Remote | No | ✅ Yes |
| Browser Required | No | ✅ Yes |
| System Resources | Low | Low |
| Performance | Excellent | Excellent |

---

## 🔧 Desktop Development Commands

### Start Development
```bash
# Both Next.js dev server + Electron app
make dev-desktop
# or
npm run dev:desktop
```

### Build Desktop Installer
```bash
# Creates .deb and .AppImage files
make build-desktop
# or
npm run build:desktop
```

### Run Packaged App
```bash
# Run the built Electron app
make start-desktop
# or
npm run start:desktop
```

### Help
```bash
make help
```

---

## 📦 Installation Methods for End Users

### Method 1: .deb Package (Recommended for Ubuntu)
```bash
# Direct installation
sudo apt install ./PulseTask-*.deb

# Or use Software Center
# Double-click the .deb file
```

### Method 2: AppImage
```bash
# Download and run
chmod +x PulseTask-*.AppImage
./PulseTask-*.AppImage

# Or use AppImageLauncher
# Drag & drop to install
```

### Method 3: From Source
```bash
git clone https://github.com/matiasz8/pulseTask.git
cd pulseTask
npm install
make build-desktop
sudo dpkg -i dist/PulseTask-*.deb
```

---

## 🛠️ System Requirements

### Minimum
- Ubuntu 20.04 LTS or later
- 50 MB disk space
- 512 MB RAM

### Recommended
- Ubuntu 22.04 LTS or later
- 100 MB disk space
- 1 GB RAM

### Required Dependencies
- libxss1 (automatically installed with .deb)

---

## 🎨 Features Available in Desktop App

The desktop version has all the same features as the web version:

✅ **Focus View** - Pomodoro timer with countdown
✅ **Task Management** - Create, pause, resume, complete
✅ **Statistics** - Track productivity with charts
✅ **Settings Panel** - Customize app behavior
✅ **Overlay Widget** - Floating compact widget
✅ **Dark Mode** - Native theme support
✅ **Keyboard Shortcuts** - Efficient navigation
✅ **State Persistence** - Tasks saved across sessions

---

## 🔐 Security & Privacy

The desktop app:
- Runs entirely on your machine
- All data stored locally
- No server communication required
- Open source for transparency
- Built with Electron (trusted framework)

---

## 📝 Development

### Project Structure for Desktop
```
pulseTask/
├── electron/
│   ├── main.js        # Electron entry point
│   └── preload.js     # Security bridge
├── app/               # React components (shared)
├── components/        # UI components (shared)
├── lib/               # State & utilities (shared)
├── public/            # Icons and assets
└── package.json       # Build config with electron-builder
```

### Building from Source
```bash
# Install dependencies
npm install

# Development mode
npm run dev:desktop

# Production build
npm run build:desktop

# Output files in dist/
```

---

## 🐛 Troubleshooting

### Desktop app won't start
```bash
# Check if development server is running
lsof -i :3000

# Rebuild everything
make clean
npm install
make dev-desktop
```

### Port 3000 in use
```bash
# Kill process on port 3000
lsof -i :3000 | grep node | awk '{print $2}' | xargs kill -9

# Or use different port
PORT=3001 npm run dev:desktop
```

### Build fails
```bash
# Clear cache
make clean
npm install

# Rebuild
npm run build:desktop
```

### Permission denied on AppImage
```bash
chmod +x ./PulseTask-*.AppImage
./PulseTask-*.AppImage
```

---

## 🚀 Deployment

### For Users (End Distribution)
1. Build: `npm run build:desktop`
2. Find .deb in `dist/` directory
3. Distribute via GitHub Releases
4. Users install: `sudo apt install ./PulseTask-*.deb`

### For Flathub
Update flatpak configuration to use Electron instead of Python GTK

### For App Stores
Package with electron-builder for Linux app stores

---

## 📊 File Locations

Desktop app stores data in standard Linux locations:
```
~/.config/PulseTask/     # Application config
~/.local/share/PulseTask/ # Application data
```

---

## 🎉 What's Next

- ✅ Desktop app is ready for testing
- ⬜ Add system tray integration
- ⬜ Add automatic updates
- ⬜ Add native notifications
- ⬜ Publish to Flathub
- ⬜ Publish to Linux app stores

---

## 📞 Support

- **Web Version Issues**: http://localhost:3000
- **Desktop Version Issues**: Check logs in `~/.config/PulseTask/`
- **General Help**: See [START_HERE.md](START_HERE.md)
- **Repository**: https://github.com/matiasz8/pulseTask

---

**Both versions available. Same design. Same features. Your choice.**

*Updated: August 4, 2026*
