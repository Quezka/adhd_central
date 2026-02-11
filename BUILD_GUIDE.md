# Building ADHD Central - Complete Guide

## Quick Start (Professional Installer)

The easiest way to build everything:

1. **Install NSIS** (one-time setup):
   - Download from: https://nsis.sourceforge.io/Download
   - Run the installer
   - Use default settings

2. **Build Everything**:
   - Double-click `build-installer.bat` in your project folder
   - Wait for completion (~2-3 minutes)
   - Done! You'll have both the executable and installer

3. **Output Files**:
   - **Executable**: `dist\ADHD Central\ADHD Central.exe` (standalone, no install needed)
   - **Installer**: `dist\ADHD Central Installer.exe` (professional Windows installer)

---

## Detailed Build Options

### Option 1: Build Just the Executable

Perfect for testing or for users who don't need installation (portable app).

**Steps**:

1. Double-click `build.bat`
2. Wait for completion
3. Executable is at: `dist\ADHD Central\ADHD Central.exe`

**Distribution**:

- Users can run the `.exe` directly without any installation
- No need for NSIS

---

### Option 2: Build Executable + Professional Installer (Recommended)

Creates a proper Windows application with installer.

**Prerequisites**:

- NSIS installed from https://nsis.sourceforge.io/Download

**Steps**:

1. Double-click `build-installer.bat`
2. Script will:
   - Clean old builds
   - Build the executable
   - Auto-detect NSIS
   - Create the Windows installer
3. Both files are ready in `dist\`:
   - `ADHD Central\ADHD Central.exe` (standalone)
   - `ADHD Central Installer.exe` (for distribution)

**Distribution**:

- Share `dist\ADHD Central Installer.exe` with users
- They run it like any Windows installer
- Creates Start Menu shortcuts
- Integrates with Add/Remove Programs
- Can be uninstalled normally

---

## Features of the Professional Installer

The `ADHD Central Installer.exe` includes:

✅ Modern installation wizard  
✅ Custom installation directory  
✅ Start Menu shortcuts  
✅ Desktop shortcut  
✅ Add/Remove Programs integration  
✅ Professional uninstall process  
✅ Application icon in taskbar & shortcuts  
✅ Registry entries for system integration

---

## Troubleshooting

### "NSIS not found" error:

- Download NSIS from: https://nsis.sourceforge.io/Download
- Install it with default settings
- Run `build-installer.bat` again

### Build fails with missing dependencies:

```bash
pip install -r requirements.txt
```

### Icon not showing:

- Verify `icon.ico` exists in project root
- Verify `icons/` folder exists
- Rebuild using `build.bat` or `build-installer.bat`

### "Access Denied" error in installer:

- Run the build script as Administrator
- Right-click the `.bat` file → "Run as administrator"

---

## File Structure After Build

```
dist/
├── ADHD Central/                    # Standalone executable
│   ├── ADHD Central.exe            # Main application
│   ├── icon.ico                    # Icon file
│   ├── icons/                      # Icon assets
│   └── [dependencies]              # PySide6 and Python libraries
│
└── ADHD Central Installer.exe       # Windows installer for distribution
```

---

## For Distribution

### Option A: Share Just the Executable

- Users download `ADHD Central.exe`
- They can run it immediately, no installation needed
- Perfect for quick testing or portable use

### Option B: Share the Installer (Recommended)

- Users download `ADHD Central Installer.exe`
- They run it like any Windows app installer
- Shortcuts are created automatically
- Can be uninstalled via Control Panel
- More professional presentation

---

## Technical Details

### Build Files:

| File                  | Purpose                        |
| --------------------- | ------------------------------ |
| `build.bat`           | Creates executable only        |
| `build-installer.bat` | Creates executable + installer |
| `adhd_central.spec`   | PyInstaller configuration      |
| `installer.nsi`       | NSIS installer script          |
| `requirements.txt`    | Project dependencies           |

### Tools Used:

- **PyInstaller**: Converts Python to Windows executable
- **NSIS**: Creates professional Windows installers
- Icon support through `.ico` file (displayed in taskbar, shortcuts, etc.)

---

## Advanced: Manual Build Steps

If the batch scripts don't work:

**Build Executable**:

```bash
# Activate virtual environment
venv\Scripts\activate.bat

# Run PyInstaller
pyinstaller adhd_central.spec --distpath dist --buildpath build
```

**Create Installer** (requires NSIS):

```bash
# Windows Standard Installation Path
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

# Or if installed elsewhere
makensis installer.nsi
```

---

## Version Management

To update the version number in the installer:

1. Edit `installer.nsi`
2. Change `"Version" "1.0"` to desired version
3. Change `BrandingText "ADHD Central v1.0"` to match
4. Rebuild using `build-installer.bat`
