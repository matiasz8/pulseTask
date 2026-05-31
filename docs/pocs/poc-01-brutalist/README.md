# POC-01: Minimal Brutalist

## Filosofía Visual

**Concepto:** Máxima claridad, cero distracción, estética hacker/developer-first  
**Target:** Developers Linux, terminal power users, UNIX purists  
**Feeling:** Profesional extremo, confianza, seriedad  
**Accesibilidad:** ⭐⭐⭐⭐⭐ Excelente (alto contraste)  
**Performance:** ⭐⭐⭐⭐⭐ Excelente (sin efectos, CSS simple)

---

## 🎨 Paleta de Colores

### Light Mode
```
Fondo principal:    #FFFFFF (blanco puro)
Texto principal:    #000000 (negro puro)
Bordes/acentos:     #333333 (gris oscuro)
Separadores:        #CCCCCC (gris medio)
Éxito:              #0EA854 (verde)
Alerta:             #D62828 (rojo)
Info/disabled:      #666666 (gris texto)
```

### Dark Mode
```
Fondo principal:    #1A1A1A (almost black)
Texto principal:    #FFFFFF (blanco)
Bordes/acentos:     #CCCCCC (gris claro)
Separadores:        #333333 (gris oscuro)
Éxito:              #4ADE80 (verde claro)
Alerta:             #FF6B6B (rojo claro)
Info/disabled:      #999999 (gris texto)
```

---

## 🔤 Tipografía

**Timer (Hero):**
- Font Family: `JetBrains Mono` o `IBM Plex Mono` (monospace)
- Size: 72px (main window), 48px (overlay)
- Weight: 700 (BOLD)
- Letter-spacing: 2px (maximum clarity)
- Line-height: 1.1

**Headings (Task titles, labels):**
- Font Family: `Inter` o `Ubuntu` (sans-serif)
- Size: 14-16px
- Weight: 600 (semi-bold)
- Letter-spacing: 0.5px

**Body Text:**
- Font Family: `Inter` o `Ubuntu` (sans-serif)
- Size: 13px
- Weight: 400 (regular)
- Letter-spacing: 0px
- Line-height: 1.5

**Labels/Captions:**
- Font Family: Same sans-serif
- Size: 12px
- Weight: 600 (semi-bold)
- Text-transform: UPPERCASE
- Letter-spacing: 1px (high legibility)

---

## 📐 Spacing & Layout

**Grid System:** 8px strict grid
```
Margins:        24px (window edge)
Padding cards:  16px
Padding buttons: 8px (v) x 16px (h)
Gap between elements: 8px or 16px
Rounded corners: 0px (NO rounded corners - sharp edges only)
```

**Vertical Rhythm:**
- Section spacing: 16px
- Element spacing: 8px
- Compact layout, no waste

---

## 🎛️ UI Components

### Timer Display
```
┌─────────────────┐
│    75:42        │
│  (Big, mono)    │
└─────────────────┘
```
- Monospace, BOLD, 72px
- Centered
- No background, no shadow
- Letter-spacing: 2px for separation

### Task Card (Inactive)
```
┌─────────────────────────────────┐
│ • Code Review (20 min)          │
│   PENDING                       │
└─────────────────────────────────┘
```
- Border: 1px #CCCCCC (light) / #333333 (dark)
- Padding: 16px
- No shadow
- Text color: #666666 (muted)

### Task Card (Active)
```
┌─────────────────────────────────┐
│ ▶ Fix Comments (30 min)         │
│   ACTIVE                        │
├─────────────────────────────────┤
│ ████████████░░░░░░░░░░░░░ 40% │
└─────────────────────────────────┘
```
- Border: 2px #000000 (light) / #FFFFFF (dark)
- Font-weight: 600
- Progress bar: simple, no animation

### Task Card (Completed)
```
┌─────────────────────────────────┐
│ ✓ Review API (20 min)           │
│   COMPLETED                     │
└─────────────────────────────────┘
```
- Opacity: 0.5
- Text-decoration: line-through
- Color: #999999

### Buttons
```
[PAUSE]    [SKIP TASK]    [SETTINGS]
```
- Style: Outline only (no fill)
- Border: 1px solid (color matches text)
- Padding: 8px vertical, 16px horizontal
- Hover: background #F0F0F0 (light) / #2A2A2A (dark)
- No shadow, no rounded corners
- Cursor: pointer on hover
- Font-weight: 500

### Primary Button
```
[START EXECUTION]
```
- Style: Solid black/white (inverted)
- Hover: darker shade
- Same sizing as outline buttons

### Destructive Button
```
[DELETE]
```
- Border color: #D62828
- Text color: #D62828
- Hover: background #D62828, text white

### Success Button
```
[COMPLETE]
```
- Border color: #0EA854
- Text color: #0EA854
- Hover: background #0EA854, text white

---

## 🎬 Animations & Transitions

**Philosophy:** Minimal, purposeful animations only

### Timer Update
- No animation on every tick
- Optional: subtle pulse when active (every 2s)
```css
@keyframes pulse-minimal {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```

### Button Hover
- Transition: 0.15s background color
- No transform, no scale

### Task Transition
- Fade in/out: 0.2s opacity
- Slide: optional, 0.3s translate

---

## 📱 Layout Structure

### Main Window
```
┌──────────────────────────────────────┐
│ PulseTask                    ⊖ □ ×  │  Header (24px padding)
├──────────────────────────────────────┤
│                                      │
│              75:42                   │  Timer card (centered)
│         Code Review Session          │
│         Task 2/5                     │
│                                      │
├──────────────────────────────────────┤  Separator
│ Task Queue                           │  Section label
│ ─────────────────────────────────── │  Separator line
│ ✓ Review API (20m)      [COMPLETED]│  Task rows
│ ▶ Fix Comments (30m)    [ACTIVE]   │
│ • Deploy (10m)          [PENDING]  │
│ • Test (15m)            [PENDING]  │
│ • Cleanup (5m)          [PENDING]  │
│                                      │
├──────────────────────────────────────┤
│  [PAUSE]  [SKIP]  [⋮ MENU]          │  Control buttons
│                                      │
└──────────────────────────────────────┘
```

### Overlay Window (Focus Mode)
```
┌─────────────────┐
│ 75:42           │  Timer (48px mono)
│ Code Review     │  Task name (14px)
│ 2/5 ▶           │  Progress + icon
└─────────────────┘
```
- Minimal, always-on-top
- 200-300px wide
- Transparent background (or very light)
- Click to expand to full window

---

## ♿ Accessibility

- **Contrast:** WCAG AAA (7:1 ratio minimum)
- **Focus indicators:** Clear, high-contrast outline
- **Keyboard navigation:** Tab order logical, all clickable elements accessible
- **Screen reader:** Labels on all interactive elements
- **Font size:** Minimum 13px for body text, 12px labels
- **Touch targets:** Minimum 44px (buttons)

---

## 🖥️ Implementation Details

### CSS Variables
```css
:root {
  --color-bg: #ffffff;
  --color-text: #000000;
  --color-border: #cccccc;
  --color-accent: #333333;
  --color-success: #0ea854;
  --color-error: #d62828;
  
  --font-mono: "JetBrains Mono", monospace;
  --font-sans: "Inter", sans-serif;
  
  --spacing-xs: 8px;
  --spacing-s: 16px;
  --spacing-m: 24px;
  --spacing-l: 32px;
  
  --transition-fast: 0.15s;
  --transition-normal: 0.3s;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #1a1a1a;
    --color-text: #ffffff;
    --color-border: #333333;
    --color-accent: #cccccc;
    --color-success: #4ade80;
    --color-error: #ff6b6b;
  }
}
```

### Box Model
- No rounded corners on anything
- Sharp, clean angles
- Borders: 1px solid
- Shadows: NONE (keep it flat)

### Hover States
- Background color change (dark/light overlay)
- Text color change (if needed for contrast)
- No transform/scale
- Cursor pointer

---

## 📊 Comparison to Other POCs

| Aspecto | POC-01 | POC-02 | POC-03 |
|---------|--------|--------|--------|
| Contraste | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Profesionalismo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Calm Feeling | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Wow Factor | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Dev Speed | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ |

---

## ✅ Design Checklist

- [ ] All text has sufficient contrast (WCAG AA minimum)
- [ ] No decorative elements
- [ ] All borders 1px sharp
- [ ] No shadows or depth effects
- [ ] Timer is always largest, most prominent
- [ ] Buttons are clear and accessible
- [ ] Monospace font for all timers
- [ ] Grid-based spacing (8px increments)
- [ ] Works in light AND dark modes
- [ ] Performance: <10ms paint time

---

## 🎯 When to Use POC-01

✅ **Use POC-01 if:**
- You want maximum clarity and accessibility
- Your users are developers/terminal-heavy
- You need fast implementation
- You value reliability over visual polish
- You want timeless aesthetic (won't feel dated)
- Performance is critical

❌ **Don't use POC-01 if:**
- You need visual "wow" factor for marketing
- Your users expect modern gradients/effects
- You're competing primarily on visual appeal
- You have ADHD users who need softer UI

---

## 🚀 Implementation Order

1. **CSS variables** - Set all colors, spacing, fonts
2. **Base components** - Button, label, card styles
3. **Timer styling** - Make timer hero element
4. **Task card styling** - Active, inactive, completed states
5. **Layout** - Main window + overlay
6. **Animations** - Minimal transitions
7. **Dark mode** - Test in both modes
8. **Accessibility** - Verify contrast, focus states, keyboard nav

---

## 📝 References

- **GNOME Design Patterns:** https://developer.gnome.org/hig/ (for accessibility)
- **Accessible Colors:** https://webaim.org/resources/contrastchecker/
- **GTK4 Styling:** https://docs.gtk.org/gtk4/css-properties.html
- **Monospace Fonts:** JetBrains Mono, IBM Plex Mono, Courier Prime

