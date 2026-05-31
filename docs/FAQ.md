# PulseTask FAQ

## General

### What is PulseTask?
PulseTask is a **calm execution environment for Linux power users**. It focuses on one thing: helping you complete tasks within time budgets through group execution sessions.

Unlike generic task managers, PulseTask prioritizes:
- **Time over tasks** - The countdown is the UI
- **Groups over individual tasks** - Execute 5 tasks in one focused session
- **Local over cloud** - Your data stays on your machine
- **Native over web** - GNOME design language, keyboard-first

### Who should use PulseTask?
- **Developers** (especially freelancers/DevOps)
- **Remote workers** doing focused blocks
- **People with ADHD** who benefit from time pressure and structure
- **Power users** who want a focused Linux native tool
- Anyone who values **calm, distraction-free work**

### Who should NOT use PulseTask?
- People needing cloud sync across devices
- Teams requiring collaboration features
- Anyone wanting "smart" AI-powered suggestions
- Mobile app users
- People who need calendar integration

### Is it free?
Yes, 100% free and open source (MIT licensed). No ads, no tracking, no premium tier (for now).

### Can I use it on Windows/Mac?
No, PulseTask is Linux-first. It uses GTK4 and GNOME design language, which aren't available on other platforms.

### Why not add cloud sync?
Because we believe in **local-first, distraction-free execution**. Cloud features would require:
- Authentication complexity
- Constant connectivity concerns
- Notification temptation
- Scope creep that kills focus

Your data should be yours, not hosted on someone's server.

---

## Usage

### How do I create a task group?
```
1. Click "New Group"
2. Add a group name (e.g., "Morning Focus")
3. Set time budget (e.g., 60 minutes)
4. Add tasks with descriptions
5. Click "Start"
```

### What's "time budget"?
The total time you're allocating for ALL tasks in the group. PulseTask will:
- Divide it evenly across tasks (or you can customize)
- Show countdown for current task
- Alert you if time's up

### Can I pause mid-execution?
Yes. Click "Pause" and the timer freezes. Resume whenever ready.

### Can I skip a task?
Yes. Click "Skip" to move to the next task without completing the current one. This counts as an interruption (tracked in stats).

### What happens when time runs out?
The current task goes red and timer shows "00:00". You can:
- Click "Next" to move to the next task
- Click "Pause" to take a break
- Click "Stop" to end the session

The app doesn't force you to stop—it just shows you've exceeded budget.

### Can I run multiple groups simultaneously?
No. PulseTask focuses on one group at a time. If you need parallel work, create multiple groups and switch between them.

### How do I export my data?
```
1. Open Stats window
2. Click "Export as CSV" or "Export as JSON"
3. Save to your preferred location
```

Data is exported as raw task completion records—you can analyze in Excel, Python, or wherever.

---

## Accessibility

### Is PulseTask keyboard accessible?
Yes, 100%. You can control everything without a mouse:

```
Tab / Shift+Tab     - Navigate between elements
Enter               - Activate button
Space               - Toggle checkbox
Arrow keys          - Navigate lists
Escape              - Close dialog
Alt+[key]           - Activate menu items
```

All buttons have focus indicators (3px outline).

### Does it work with screen readers?
Yes, GTK4 integrates with GNOME Accessibility (ATK). Tested with Orca screen reader.

### Does it respect "Reduce Motion"?
Yes. If you have "Reduce Motion" enabled in Accessibility settings, PulseTask disables animations.

### Does it support high contrast?
Yes. If you enable "High Contrast" in Accessibility settings, PulseTask uses higher contrast colors and thicker borders.

---

## Data & Privacy

### Where is my data stored?
Locally in `~/.local/share/pulseTask/data.db` (SQLite database).

### Can PulseTask access my personal files?
No. It has no file system permissions beyond its own data directory.

### Does it phone home?
No. Zero network calls. It's 100% offline-first.

### Can I back up my data?
Yes. Copy `~/.local/share/pulseTask/data.db` to anywhere. That's your complete backup.

### Can I transfer data to another machine?
Yes. Copy the `data.db` file to the same location on the new machine.

### What happens if I uninstall?
Your data stays in `~/.local/share/pulseTask/` and is safe. Reinstalling PulseTask will read it back.

---

## Technical

### What's the system requirement?
- **Ubuntu 22.04 LTS+** (or any recent GNOME-based distro)
- **Python 3.12+**
- **GTK4 + libadwaita** (auto-installed via apt)

### How do I install?
```bash
# From Flathub (coming soon)
flatpak install flathub org.gnome.Pulse

# From source
git clone https://github.com/matiasz8/pulseTask.git
cd pulseTask
make venv && make sync && make doctor-gtk
make run
```

### Why does it require libadwaita?
libadwaita provides GNOME design language (colors, spacing, animations). It ensures PulseTask feels native on your system.

### Can I run it on Wayland?
Yes. PulseTask works on both Wayland and X11.

### Does it work on KDE Plasma?
Technically yes, but it won't look as polished. We optimize for GNOME. If you use KDE, you might prefer KDE-native tools.

### Can I customize the theme?
Currently, PulseTask respects your system theme. Custom themes coming in v0.3.0.

---

## Troubleshooting

### "GTK4/libadwaita is not available"
You need to install system dependencies:
```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 libnotify-bin
```

Then recreate the venv:
```bash
rm -rf .venv
make venv && make sync && make doctor-gtk
```

### "App crashes on startup"
First, check logs:
```bash
PulseTask 2>&1 | head -50
```

Common issues:
- Missing GTK dependencies (see above)
- SQLite database corruption (delete `~/.local/share/pulseTask/data.db` and restart)
- Incompatible GTK version (update Ubuntu: `sudo apt upgrade`)

### "Timer display is too small"
System scaling issue. Try:
```bash
GDK_SCALE=2 pulsetask
```

Or adjust in GNOME Settings → Display → Scale.

### "Statistics show wrong completion rate"
Completion rate = `tasks_completed / estimated_capacity`. If your estimate is off, rates will be too. Update your estimates in group settings.

### "I can't delete a task group"
Only completed or archived groups can be deleted. Active groups must be stopped first.

---

## Workflow Tips

### Tip 1: Use realistic time budgets
Don't allocate 5 minutes for a 30-minute task. The timer is a guide, not a tyrant.

### Tip 2: Group similar tasks
"Morning admin" might include: email, Slack, GitHub issues. They're context-similar.

### Tip 3: Review stats weekly
Each Friday, export your stats and notice patterns:
- When do you focus best?
- How many interruptions per session?
- What task types take longest?

### Tip 4: Use the overlay
For passive monitoring, switch to the overlay window (compact mode). Keeps the countdown visible without blocking your whole screen.

### Tip 5: Respect the timer
The magic of PulseTask happens when you **actually stop** when time's up, instead of "just 5 more minutes." That boundary creates focus.

---

## Feature Requests

### "Can you add cloud sync?"
Not in our roadmap. Cloud sync contradicts our local-first philosophy. If you need sync, try [Todoist](https://todoist.com) or [TickTick](https://ticktick.com).

### "Can you add collaboration?"
Not planned. Team features cause scope creep that kills focus. PulseTask is single-user by design.

### "Can you add mobile?"
No. PulseTask is desktop-first. The countdown timer on a mobile screen would create unhealthy urgency.

### "Can you add dark mode?"
PulseTask respects your system theme automatically (via libadwaita). Enable dark mode in GNOME Settings → Appearance.

### "Can you add [feature]?"
Check [CONTRIBUTING.md](../CONTRIBUTING.md) for our philosophy on features. Open a GitHub Discussion (not an issue) to discuss.

---

## Roadmap

### v0.2.0 (Current)
✅ Group execution engine
✅ Full keyboard accessibility
✅ Statistics + export
✅ GNOME design language

### v0.3.0 (Next, ~3 months)
- [ ] Deep GNOME integration (Quick Settings, Shell integration)
- [ ] Actionable notifications
- [ ] Global keyboard shortcuts
- [ ] Search provider integration

### v0.4.0+ (Future)
- [ ] Custom themes
- [ ] Advanced heatmaps (correlate stats with calendar)
- [ ] Team read-only sharing (no sync)
- [ ] Historical data analysis

---

## Support

**Having issues?**

1. Check this FAQ
2. Read `docs/ACCESSIBILITY_CHECKLIST.md` (if accessibility issue)
3. Search existing [GitHub Issues](https://github.com/matiasz8/pulseTask/issues)
4. Open a [GitHub Discussion](https://github.com/matiasz8/pulseTask/discussions)
5. File a bug report with system info + reproduction steps

**Want to contribute?**

See [CONTRIBUTING.md](../CONTRIBUTING.md).

---

**Last updated**: May 31, 2026
**Version**: PulseTask v0.2.0+
