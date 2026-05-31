# POC-02: Glassmorphism + Modern

## Filosofía Visual

**Concepto:** Premium, vibrante, efectos modernos (2024/2025)  
**Target:** Visual appeal máximo, usuarios nuevos, competencia con apps premium  
**Feeling:** Premium/moderno, contemporáneo, engaging  
**Accesibilidad:** ⭐⭐⭐ Mediano (requiere careful contrast testing)  
**Performance:** ⭐⭐ Bajo-Mediano (blur effects + gradients)

---

## 🎨 Paleta de Colores

### Light Mode (Base: Cool Gray-100 to Blue-50)
```
Fondo principal:    #F8FAFC (cool gray, very light)
Fondo secundario:   #F1F5F9 (subtle darker)
Texto principal:    #1E293B (dark slate)
Texto secundario:   #64748B (slate)

Primario:           #6366F1 (Indigo)
Primario hover:     #4F46E5 (Indigo darker)
Secundario:         #EC4899 (Pink/Magenta)
Terciario:          #F59E0B (Amber)

Éxito:              #10B981 (Emerald green)
Alerta:             #EF4444 (Red)
Info:               #3B82F6 (Blue)
Warning:            #F59E0B (Amber)

Glass surface:      rgba(255, 255, 255, 0.1) + backdrop-filter: blur(10px)
```

### Dark Mode (Base: Cool Gray-900 to Blue-950)
```
Fondo principal:    #0F172A (navy)
Fondo secundario:   #0C0F1F (darker navy)
Texto principal:    #F1F5F9 (light gray)
Texto secundario:   #94A3B8 (muted gray)

Primario:           #818CF8 (Indigo light)
Primario hover:     #6366F1 (Indigo)
Secundario:         #F472B6 (Pink light)
Terciario:          #FBBF24 (Amber light)

Éxito:              #34D399 (Green light)
Alerta:             #F87171 (Red light)
Info:               #60A5FA (Blue light)
Warning:            #FBBF24 (Amber light)

Glass surface:      rgba(15, 23, 42, 0.1) + backdrop-filter: blur(10px)
```

---

## 🔤 Tipografía

**Timer (Hero):**
- Font Family: `GeistMono` o `SpaceGrotesque` (geometric monospace)
- Size: 64px (main window), 48px (overlay)
- Weight: 600 (semi-bold, NOT bold)
- Gradient: Linear from Indigo to Pink
- Letter-spacing: 1px (generous spacing)
- Background-clip: text (gradient effect)

**Headings:**
- Font Family: `GeistVariable` o `Inter` (sans-serif)
- Size: 16-20px
- Weight: 600 (semi-bold)
- Letter-spacing: 0px (natural)

**Body Text:**
- Font Family: `GeistVariable` o `Inter`
- Size: 14px
- Weight: 400 (regular)
- Line-height: 1.6

**Labels/Captions:**
- Font Family: Same sans-serif
- Size: 12px
- Weight: 600 (semi-bold)
- Text-transform: UPPERCASE (optional, use sparingly)
- Letter-spacing: 0.5px

---

## 📐 Spacing & Layout

**Grid System:** Flexible (not strict 8px)
```
Margins:        16-24px (generous)
Padding cards:  20-24px
Padding buttons: 12px (v) x 24px (h)
Gap between elements: 12-16px
Rounded corners: 12-16px (soft, generous)
```

**Vertical Rhythm:**
- Section spacing: 20px
- Element spacing: 12px
- Breathing room between elements
- Generous padding

---

## 🎛️ UI Components

### Timer Display (Gradient Hero)
```
┌─────────────────────┐
│    75:42            │  (Gradient: Indigo→Pink)
│  (64px semi-bold)   │
└─────────────────────┘
```
- Gradient background: linear-gradient(135deg, #6366F1, #EC4899)
- Text with background-clip
- Soft glow shadow effect
- Letter-spacing: 1px

### Task Card (Inactive)
```
┌────────────────────────────────────┐
│ • Code Review                (20m)│
│   PENDING        [Glass surface]   │
└────────────────────────────────────┘
```
- Background: rgba(255,255,255,0.1) + backdrop-filter: blur(8px)
- Border: 1px solid rgba(255,255,255,0.2)
- Border-radius: 12px
- Box-shadow: 0 8px 32px rgba(0,0,0,0.1)
- Hover: subtle lift effect

### Task Card (Active)
```
┌────────────────────────────────────┐
│ ▶ Fix Comments                (30m)│
│   ACTIVE                           │
├────────────────────────────────────┤
│ ███████████░░░░░░░░░░░░░░░ 40%   │
└────────────────────────────────────┘
```
- Background: rgba(99,102,241,0.1) (Indigo tint)
- Border: 1px solid #6366F1 or rgba(99,102,241,0.3)
- Shadow: glow effect
- Progress bar: gradient Indigo→Pink

### Progress Bar
```
████████████████░░░░░░░░░░░░░░░░
[████████] 40% | 18:30 remaining
```
- Gradient: linear-gradient(90deg, #6366F1, #EC4899)
- Height: 4-6px (thin and elegant)
- Background: very light gray
- Radius: 2-3px

### Buttons
```
[START EXECUTION]    [Skip]    [⚙ Settings]
```
- Filled: gradient(#6366F1 → #8B5CF6)
- Outline: glass morphism
- Padding: 12px x 24px
- Border-radius: 8px
- Box-shadow: 0 4px 15px rgba(99,102,241,0.4)
- Hover: lift + glow intensifies

### Button States
- **Primary:** Gradient Indigo
- **Secondary:** Glass (blur + transparent)
- **Success:** Emerald green
- **Destructive:** Red
- Hover: intensifies shadow, lift effect

---

## 🎬 Animations & Transitions

**Philosophy:** Smooth, delightful, micro-interactions

### Glow Pulse (On Active)
```css
@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4); }
  50% { box-shadow: 0 6px 25px rgba(99, 102, 241, 0.6); }
}
```

### Button Hover
- Duration: 0.2s
- Effects: translateY(-2px), box-shadow intensifies

### Card Hover
- Duration: 0.3s
- Effects: background lightens, border glow

### Progress Bar Fill
- Duration: 0.3s
- Easing: ease-out

---

## 📱 Layout Structure

### Main Window
```
┌────────────────────────────────────┐
│ PulseTask        ⊖ □ ×             │  Header glass card
├────────────────────────────────────┤
│  ╭────────────────────────────────╮│
│  │                                 ││ Timer card (glass)
│  │         75:42                   ││ (Gradient + glow)
│  │      (Gradient + Shadow)        ││
│  │   Code Review Session           ││
│  ╰────────────────────────────────╯│
│                                     │
│ ┌──────────────────────────────────┐│ Task list (glass cards)
│ │ ✓ Review API (20m)      [DONE]  ││
│ │                                  ││
│ │ ▶ Fix Comments (30m)    [ACTIVE]││
│ │ ████████████░░░░░░░░░░░ (40%)  ││
│ │                                  ││
│ │ • Deploy (10m)          [NEXT]  ││
│ │ • Test (15m)            [WAIT]  ││
│ └──────────────────────────────────┘│
│                                     │
│    [◼ Pause]  [⊳ Skip]  [⚙ More]  │ Controls (buttons)
│                                     │
└────────────────────────────────────┘
```

### Overlay Window
```
╭─────────────────────╮
│ 75:42               │ Timer (gradient, glow)
│ Code Review         │ Task name
│ 2/5 ▶               │ Progress badge
╰─────────────────────╯
```

---

## 🔮 Glass Morphism Specifics

**What is Glass Morphism?**
- Semi-transparent surface
- Backdrop blur effect
- Border with semi-transparent white
- Shadows creating depth
- Modern, premium feel

**Implementation:**
```css
.glass-surface {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

@media (prefers-color-scheme: dark) {
  .glass-surface {
    background: rgba(15, 23, 42, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
}
```

---

## ♿ Accessibility Considerations

- **Contrast:** Check all text with glass backgrounds (may need adjustments)
- **Focus:** Clear focus indicators (outline or glow)
- **Motion:** Reduce animations if prefers-reduced-motion
- **Performance:** Test on older devices (blur is CPU intensive)

---

## 📊 Comparison

| Aspecto | This POC | POC-01 | POC-03 |
|---------|----------|--------|--------|
| Wow Factor | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Performance | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Calm | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Modern | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Accessibility | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 When to Use POC-02

✅ **Use if:**
- You want maximum visual appeal for marketing
- Your users expect modern design
- You have performance headroom
- You're competing on visual differentiation
- Screenshots are important

❌ **Don't use if:**
- You need max accessibility
- Performance is critical (low-end devices)
- You want timeless design (trends change)
- Blur effects aren't well-supported on target

---

## 🚀 Implementation Checklist

- [ ] Define all color variables (CSS custom properties)
- [ ] Create gradient definitions for timer + buttons
- [ ] Implement glassmorphic cards
- [ ] Add backdrop-filter blur effects
- [ ] Create smooth hover transitions
- [ ] Add glow animations
- [ ] Test in light + dark modes
- [ ] Verify performance (paint times)
- [ ] Check accessibility (contrast, focus)
- [ ] Test on mobile/tablet

