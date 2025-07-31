# This is a WOP but nice already from my perspective

If you like openScad but also the power of FreeCad you might like this.
You also need to like Python.

I was lazy and did not search the web if something like that already exists.
This version is also written by claude.ai to top of my lazyness.

Still. We have here a macro for FreeCad, that, when the current project is already saved, creates a python file for coding the geometry in python. A listener is created, that listenes to file changes so the view is updated on save.

Be aware, that this is not tested at all. I even write this before testing anyting.

Updates may follow.

For now we need to install the following python packages:

pyside6
watchdog

globally on the operating system.

I will give this now to claude and let it write this nicer. So please excuse the repetitiveness.

# FreeCAD Code-Driven Geometry Macro

**OpenSCAD-style parametric modeling for FreeCAD using Python**

If you like OpenSCAD's code-driven approach but want FreeCAD's advanced CAD features, this macro bridges that gap. You'll need to enjoy Python though!

*Disclaimer: This is a Work-in-Progress and written by Claude.ai to fuel my laziness. I didn't search if something similar already exists. Still works great though!*

## What It Does

- Creates a companion Python file alongside your FreeCAD document
- Opens the file in your preferred editor (VS Code, gedit, etc.)
- Watches for file changes and live-reloads geometry in FreeCAD
- Combines OpenSCAD's parametric workflow with FreeCAD's full power

## Demo

Save your FreeCAD document → Run the macro → Edit the generated Python file → Save → Watch FreeCAD update instantly!

```python
# Change these parameters and save to see live updates
box_width = 50   # Try changing to 80!
box_height = 30
cylinder_radius = 15
```

## Installation

### Prerequisites (Arch Linux)
```bash
# Install required Python packages
sudo pacman -S python-pyside6 python-watchdog

# Or if you prefer PySide2
sudo pacman -S python-pyside2 python-watchdog
```

### FreeCAD Setup
1. Copy the macro code to FreeCAD (`Macro` → `Macros...` → `Create`)
2. Save your FreeCAD document first
3. Run the macro
4. Start coding parametric geometry!

## Features

- ✅ **Live reload** - Save Python file, see instant updates
- ✅ **Editor agnostic** - Works with VS Code, gedit, kate, etc.
- ✅ **Thread-safe** - Proper GUI updates
- ✅ **Auto-cleanup** - Removes old objects when reloading
- ✅ **Full Python power** - Use variables, functions, loops, libraries
- ✅ **All FreeCAD modules** - Part, Draft, Mesh, etc. available

## Status

⚠️ **Not extensively tested** - I'm literally writing this README before thorough testing. Use at your own risk!

Updates and improvements may follow based on real-world usage.

## Contributing

Found a bug? Have an improvement? PRs welcome! This started as a lazy weekend project but could become something useful for the community.

## License

[Insert your preferred license here]
(... I saw that and will change it when I have decided)
