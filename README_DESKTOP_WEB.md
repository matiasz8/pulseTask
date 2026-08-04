# PulseTask v0.2.0 - Desktop & Web Edition

**Deadlines visible. Focus real.**

PulseTask is now available in **two complementary versions** - both with the same beautiful design:

- 🖥️ **Desktop App** - Native Ubuntu/Linux application
- 🌐 **Web App** - Browser-based version

Choose whichever fits your workflow. Same features, same design, your choice.

---

## 🎯 Quick Start

### Desktop Version (Ubuntu)
```bash
make dev-desktop
# Native app opens automatically
```

### Web Version (Browser)
```bash
make dev
# Opens http://localhost:3000
```

---

## 📊 Desktop vs Web

| Feature | Desktop | Web |
|---------|---------|-----|
| **Installation** | .deb/.AppImage | None (browser) |
| **Native Integration** | ✅ Yes | No |
| **System Shortcuts** | ✅ Yes | No |
| **Offline Use** | ✅ Yes | Limited |
| **Remote Access** | No | ✅ Yes |
| **Performance** | Excellent | Excellent |
| **Design** | Same | Same |
| **Features** | All | All |

---

## 🚀 Installation Options

### Desktop (Ubuntu/Linux)

**Development:**
```bash
make dev-desktop
```

**Production (.deb):**
```bash
make build-desktop
sudo dpkg -i dist/PulseTask-*.deb
```

**AppImage:**
```bash
make build-desktop
chmod +x dist/PulseTask-*.AppImage
./dist/PulseTask-*.AppImage
```

### Web (Any Browser)

**Development:**
```bash
make dev
```

**Production:**
```bash
make build
make start
```

---

## 🎨 Features (Both Versions)

✅ Focus View - Pomodoro timer with countdown  
✅ Task Management - Create, pause, resume, complete  
✅ Statistics Dashboard - Track productivity  
✅ Settings Panel - Customize behavior  
✅ Overlay Widget - Floating compact mode  
✅ Dark Mode - Native theme support  
✅ Keyboard Shortcuts - Efficient navigation  
✅ State Persistence - Tasks saved locally  

---

## 💻 Tech Stack

**Both versions use:**
- React 19 - UI framework
- Next.js 16 - Web framework
- TypeScript - Type safety
- Tailwind CSS 4 - Styling
- Radix UI - Accessible components
- Zustand - State management

**Desktop adds:**
- Electron - Desktop framework
- electron-builder - Packaging

---

## 🔧 Available Commands

```bash
# Web
make dev              # Start web dev server
make build            # Build web for production
make start            # Start web production server

# Desktop
make dev-desktop      # Start desktop app dev mode
make build-desktop    # Build .deb and .AppImage
make start-desktop    # Run packaged desktop app

# General
make install          # Install dependencies
make lint             # Run ESLint
make clean            # Remove build artifacts
make help             # Show all commands
```

---

## 📁 Project Structure

```
pulseTask/
├── electron/              # Desktop app (Electron)
│   ├── main.js           # Electron entry point
│   └── preload.js        # Security bridge
├── app/                   # Next.js pages
├── components/            # React components (shared)
├── lib/                   # State & utilities (shared)
├── hooks/                 # Custom hooks (shared)
├── public/                # Icons and assets
├── styles/                # Global styles
├── Makefile              # Build commands
├── package.json          # Dependencies & build config
└── next.config.mjs       # Next.js configuration
```

---

## 🎯 Which Version Should I Use?

### Choose Desktop If:
- You use Ubuntu/Linux
- You want a native app experience
- You want desktop shortcuts
- You want offline capability
- You prefer desktop over browser

### Choose Web If:
- You want to access from multiple devices
- You prefer browser-based apps
- You want no installation hassle
- You need remote access
- You work in different environments

---

## 📦 Distribution

### For Users

**Desktop:**
```bash
sudo apt install ./PulseTask-*.deb
```

**Web:**
- Deploy to Vercel, GitHub Pages, or your own server

### For Developers

**Both versions:**
```bash
git clone https://github.com/matiasz8/pulseTask.git
cd pulseTask
npm install
```

Then choose:
- `npm run dev` for web
- `npm run dev:desktop` for desktop

---

## 🔒 Security & Privacy

Both versions:
- Run entirely on your machine
- All data stored locally
- No server communication
- Open source transparency
- Zero tracking

---

## 📚 Documentation

- **[START_HERE.md](START_HERE.md)** - Quick start guide
- **[DESKTOP_INSTALLATION.md](DESKTOP_INSTALLATION.md)** - Desktop setup (Ubuntu)
- **[README_REDESIGN.md](README_REDESIGN.md)** - Redesign details
- **[DEPLOYMENT_READY.md](DEPLOYMENT_READY.md)** - Deployment guide

---

## 🤝 Contributing

Both versions welcome contributions:
1. React components (both versions benefit)
2. Desktop-specific features (Electron)
3. Web-specific features (Next.js)
4. Documentation improvements

---

## 📝 License

MIT License - See LICENSE file

---

## 🚀 Roadmap

### Current (v0.2.0)
- ✅ Desktop app with Electron
- ✅ Web app with Next.js
- ✅ Same design in both versions
- ✅ Full feature parity

### Next (v0.3.0)
- System tray integration
- Automatic updates
- Native notifications
- Flathub distribution

### Future
- Mobile app
- Cloud sync option
- Team collaboration
- Advanced analytics

---

## 💡 Tips

**Desktop Development:**
```bash
# Hot reload enabled - changes reflect instantly
make dev-desktop
```

**Web Development:**
```bash
# Hot reload enabled - changes reflect instantly
make dev
```

**Building Release:**
```bash
# Desktop
make build-desktop
# Creates dist/PulseTask-*.deb and .AppImage

# Web
make build
# Ready for deployment
```

---

## 📞 Support

- **Issues:** GitHub Issues
- **Web Version:** http://localhost:3000
- **Desktop Version:** Check logs in ~/.config/PulseTask/
- **Documentation:** See [START_HERE.md](START_HERE.md)

---

**Available in two versions. Same design. Same features. Your choice.**

*v0.2.0 - August 4, 2026*
