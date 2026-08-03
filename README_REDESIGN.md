# PulseTask v2 - Web Redesign

## Migration from Python/GTK to React/Next.js

This project has been migrated from a Python/GTK desktop application to a modern web application built with React and Next.js.

### What Changed

- **Frontend**: Migrated from Python GTK UI to React/Next.js with TypeScript
- **Styling**: Updated to use Tailwind CSS v4 with responsive design
- **State Management**: Using Zustand for client-side state management
- **UI Components**: Built with Radix UI for accessible components
- **Deployment**: Now runs as a web application (localhost:3000 during development)

### Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The app will be available at `http://localhost:3000`

### Key Features

- **Focus Mode**: Dedicated task timer with countdown display
- **Task Management**: Create, pause, resume, and complete tasks
- **Statistics**: Track your productivity with metrics and charts
- **Compact Overlay**: Floating widget for quick task access
- **Dark Mode**: Native dark mode support
- **Keyboard Shortcuts**: Quick navigation (1-4 for views, Ctrl+O for overlay, N for new task)

### Project Structure

```
├── app/              # Next.js app directory
├── components/       # React components
│   ├── ui/          # UI component library (Radix)
│   └── *.tsx        # Feature components
├── hooks/           # Custom React hooks
├── lib/             # Utilities and store
├── public/          # Static assets
├── styles/          # Global styles
└── package.json     # Dependencies
```

### Technologies

- **React 19** - UI framework
- **Next.js 16** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS 4** - Utility-first CSS
- **Zustand** - State management
- **Radix UI** - Accessible components
- **React Hook Form** - Form management
- **Zod** - Schema validation
- **Recharts** - Data visualization

### Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

---

**Note**: The Python/GTK version has been archived in git history for reference.
