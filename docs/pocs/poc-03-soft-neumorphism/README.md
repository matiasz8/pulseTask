# POC-03: Soft Neumorphism

## Filosofía Visual

**Concepto:** Soft UI, ergonómico, genuinamente "calm"  
**Target:** ADHD-friendly, usuarios stress-prone, calm philosophy advocates  
**Feeling:** Suave, ergonómico, táctil, no estimulante  
**Accesibilidad:** ⭐⭐⭐⭐⭐ Excelente (soft contrasts = no eye strain)  
**Performance:** ⭐⭐⭐⭐ Bueno (sombras suaves, sin blur)

---

## 🎨 Paleta de Colores

### Light Mode (Base: Violet-50 to Purple-100)
```
Fondo principal:    #F3E8FF (very light purple)
Fondo secundario:   #F5F3FF (subtle darker)
Texto principal:    #3F3F46 (dark gray)
Texto secundario:   #A1A1A1 (medium gray)

Primario:           #7C3AED (Violet)
Primario soft:      #8B5CF6 (Purple)
Terciario:          #A78BFA (Lavender light)

Éxito:              #86EFAC (Green soft/light)
Alerta:             #FCA5A5 (Red soft/light)
Info:               #93C5FD (Blue soft/light)
Warning:            #FCD34D (Amber soft/light)

Sombra inset:       inset 2px 2px 5px rgba(0,0,0,0.05)
Sombra outset:      2px 2px 10px rgba(0,0,0,0.1)
```

### Dark Mode (Base: Violet-900 to Purple-950)
```
Fondo principal:    #2E1065 (dark purple)
Fondo secundario:   #3F306B (slightly lighter)
Texto principal:    #F4F4F5 (light gray)
Texto secundario:   #D4D4D8 (medium light gray)

Primario:           #A78BFA (Lavender)
Primario soft:      #C4B5FD (Lavender light)
Terciario:          #D8B4FE (Lavender lighter)

Éxito:              #6EE7B7 (Green light)
Alerta:             #FDA29B (Red light)
Info:               #7DD3FC (Blue light)
Warning:            #FBBF24 (Amber light)

Sombra inset:       inset 2px 2px 5px rgba(0,0,0,0.3)
Sombra outset:      2px 2px 10px rgba(0,0,0,0.3)
```

---

## 🔤 Tipografía

**Timer (Hero):**
- Font Family: `InterVariable` o `Ubuntu` (geometric sans-serif)
- Size: 56px (main window), 40px (overlay)
- Weight: 500 (medium, NOT bold - softer feel)
- Color: #7C3AED (Violet)
- Letter-spacing: 0.5px (generous but not aggressive)
- Line-height: 1.1

**Headings:**
- Font Family: `InterVariable` o `Ubuntu`
- Size: 16-18px
- Weight: 500 (medium)
- Letter-spacing: 0px (natural, soft)

**Body Text:**
- Font Family: `InterVariable` o `Ubuntu`
- Size: 14px
- Weight: 400 (regular)
- Line-height: 1.6 (generous for readability)

**Labels:**
- Font Family: Same sans-serif
- Size: 12px
- Weight: 500 (medium)
- Letter-spacing: 0.3px (subtle)

---

## 📐 Spacing & Layout

**Grid System:** Generous, breathing room
```
Margins:        16-20px
Padding cards:  20-24px (generous)
Padding buttons: 16px (v) x 24px (h)
Gap between elements: 16px
Rounded corners: 16-20px (very rounded, soft)
```

**Vertical Rhythm:**
- Section spacing: 24px (breathing room)
- Element spacing: 16px (comfortable)
- Card padding: 20px+ (generous internal space)
- No compressed layouts

---

## 🎛️ UI Components

### Timer Display (Neumorphic Pressed)
```
╭───────────────────╮
│      56:42        │  (Medium weight, Violet)
│   (Neumorphic)    │  (Inset + outset shadows)
╰───────────────────╯
```
- Monospace-like serif (elegant, not technical)
- Weight: 500 (medium, soft)
- Color: #7C3AED (primary violet)
- Shadow: multi-layer neumorphic effect
- No letter-spacing aggression

### Task Card (Inactive)
```
╭────────────────────────────────────╮
│ • Code Review                (20m)│
│   PENDING                          │
│ [Neumorphic surface, soft shadow] │
╰────────────────────────────────────╯
```
- Background: #F3E8FF (light purple)
- Border-radius: 16px (very soft)
- Shadow: multi-layer (inset + outset)
- Hover: subtle lift (shadow intensifies)
- No sharp edges

### Task Card (Active - Embossed)
```
╭────────────────────────────────────╮
│ ▶ Fix Comments                (30m)│
│   ACTIVE                           │
│ [Embossed, prominent shadow]      │
├────────────────────────────────────┤
│ ▢▢▢▢▢▢▢▢▢▢░░░░░░░░░░░░░░ 40%    │
│ [Soft progress, no hard line]      │
╰────────────────────────────────────╯
```
- Border: 2px solid #D8B4FE (lavender)
- Background: #F3E8FF with tint
- Shadow: more pronounced (embossed look)
- Progress bar: soft gradient (not bright)

### Progress Bar (Soft)
```
┌────────────────────────────────────┐
│ ▢▢▢▢▢▢▢▢▢▢░░░░░░░░░░░░░░░░░░   │
│ Remaining: 18:30                   │
└────────────────────────────────────┘
```
- Background: #E9D5FF (soft purple)
- Fill: Gradient (#7C3AED → #A78BFA)
- Height: 8px (thicker, softer)
- Border-radius: 4px (rounded)
- Shadow: inset, subtle

### Buttons (Neumorphic 3D)
```
╭────────────────────────╮
│  [START EXECUTION]     │  (Appears pressable)
│  [◼ Pause] [⊳ Skip]   │  (Soft 3D effect)
╰────────────────────────╯
```
- Style: Soft neumorphic (3D but not harsh)
- Shadows: inset (pressed look) + outset (depth)
- Padding: 16px x 24px (generous)
- Border-radius: 12px (soft)
- Hover: shadow reduces (releasing)
- Active: shadow increases (pressing down)

---

## 🎬 Animations & Transitions

**Philosophy:** Gentle, soothing, no jarring movements

### Gentle Pulse (Breathing Animation)
```css
@keyframes gentle-pulse {
  0%, 100% {
    box-shadow: /* normal */;
  }
  50% {
    box-shadow: /* slightly intensified */;
  }
}
```

### Button Press
- Duration: 0.2s (smooth)
- Effect: Shadow adjusts (no scale/transform)
- Easing: ease-in-out

### Card Hover
- Duration: 0.3s
- Effect: Shadow softens, lift is subtle
- Easing: ease-out

### Progress Fill
- Duration: 0.4s
- Effect: smooth width increase
- Easing: ease-out

---

## 📱 Layout Structure

### Main Window
```
┌──────────────────────────────────────┐
│ PulseTask                    ⊖ □ ×  │  Header
├──────────────────────────────────────┤
│                                      │
│  ╭────────────────────────────────╮ │
│  │                                 │ │ Timer card
│  │           56:42                 │ │ (Neumorphic)
│  │      Code Review Session        │ │
│  ╰────────────────────────────────╯ │
│                                      │
│ ╭──────────────────────────────────╮│
│ │ ✓ Review API (20m)      [DONE]  ││ Task cards
│ │                                  ││
│ │ ▶ Fix Comments (30m)    [ACTIVE]││ (Soft, rounded)
│ │ ▢▢▢▢▢▢▢░░░░░░░░░░░░░░ (40%)   ││
│ │                                  ││
│ │ • Deploy (10m)          [NEXT]  ││
│ │ • Test (15m)            [WAIT]  ││
│ ╰──────────────────────────────────╯│
│                                      │
│    [◼ Pause]  [⊳ Skip]  [⚙ More]   │ Buttons
│                                      │
└──────────────────────────────────────┘
```

### Overlay
```
╭─────────────────────╮
│ 40:15               │ Timer (soft shadow)
│ Code Review         │ Task name
│ 3/5 ▶               │ Progress
╰─────────────────────╯
```

---

## 🔮 Neumorphism Specifics

**What is Neumorphism?**
- Soft UI design trend (combines Skeuomorphism + Flat)
- Multi-layer shadows (inset + outset)
- Minimalist aesthetic
- Buttons appear pressable (3D but soft)
- Color palette limited (usually monochromatic + 1 accent)

**Key Techniques:**
1. Inset shadows for depression/pressed state
2. Outset shadows for elevation/relief
3. Very rounded corners (16px+)
4. Soft color palette
5. No borders (just shadows)

**Example Implementation:**
```css
.neomorph-surface {
  background: #f3e8ff;
  border-radius: 16px;
  box-shadow:
    inset 2px 2px 5px rgba(0, 0, 0, 0.05),
    inset -2px -2px 5px rgba(255, 255, 255, 0.8),
    2px 2px 10px rgba(0, 0, 0, 0.1),
    -2px -2px 10px rgba(255, 255, 255, 0.8);
}

.neomorph-surface:hover {
  box-shadow:
    inset 1px 1px 3px rgba(0, 0, 0, 0.05),
    inset -2px -2px 5px rgba(255, 255, 255, 0.9),
    3px 3px 12px rgba(0, 0, 0, 0.12),
    -3px -3px 12px rgba(255, 255, 255, 0.9);
}
```

---

## ♿ Accessibility

- **Contrast:** Soft, but tested to WCAG AA minimum
- **No Motion Sickness:** Gentle animations (no aggressive transforms)
- **Large Touch Targets:** Buttons 44px+ for mobile
- **Clear Focus:** Outline or glow on focus
- **Readability:** Generous line-height (1.6+)

---

## 📊 Comparison

| Aspecto | This POC | POC-01 | POC-02 |
|---------|----------|--------|--------|
| Calm | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Accessibility | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| ADHD-Friendly | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Professional | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Modern | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Performance | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |

---

## 🎯 When to Use POC-03

✅ **Use if:**
- Calm execution is core to your philosophy
- ADHD users are a significant audience
- You want maximum accessibility
- Performance matters (embedded systems, old devices)
- You want design that won't feel dated
- No eye strain is important

❌ **Don't use if:**
- You need maximum visual wow factor
- Your users expect modern trends
- You're targeting Gen-Z visual tastes
- Gradients/effects are a must

---

## 🚀 Implementation Checklist

- [ ] Define violet/purple color palette
- [ ] Create shadow function (inset + outset)
- [ ] Implement neumorphic cards
- [ ] Style buttons with pressed/released states
- [ ] Add gentle animations
- [ ] Test in light + dark modes
- [ ] Verify accessibility (contrast, focus)
- [ ] Test on various screen sizes
- [ ] Check performance (shadow rendering)
- [ ] WCAG AA compliance verification

---

## 💡 Design Philosophy

**"Soft UI is not about how things look,  
but about how they feel to use."**

- Reduce cognitive load
- Minimize aggressive stimuli
- Maximize breathing room
- Natural, ergonomic interactions
- Calm, focused experience

