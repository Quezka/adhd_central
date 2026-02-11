# Building ADHD Central as a Windows Application

## Option 1: Simple Executable (No Installation)

This creates a standalone `.exe` file that users can run directly.

### Steps:

1. **Install dependencies** (if not already installed):

   ```
   pip install -r requirements.txt
   ```

2. **Run the build script**:
   - Simply double-click `build.bat` in the project folder
   - Or from command line:
     ```
     build.bat
     ```

3. **Output**:
   - Executable will be in: `dist\ADHD Central\ADHD Central.exe`
   - Users can run this directly without installation

---

## Option 2: Professional Windows Installer

This creates a proper Windows installer (`.exe`) with:

- Installation wizard
- Start Menu shortcuts
- Desktop shortcut
- Add/Remove Programs integration
- Uninstall functionality

### Prerequisites:

1. **Download and install NSIS**:
   - Download from: https://nsis.sourceforge.io/Download
   - Run the installer and complete setup

2. **Ensure you have the built executable**:
   - Run `build.bat` first (see Option 1)

### Steps:

1. **Build the installer**:
   - Open Windows Command Prompt
   - Navigate to the project folder:
     ```
     cd d:\Programming\adhd_central
     ```
   - Run:
     ```
     "C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi
     ```
   - Or if you installed NSIS elsewhere, adjust the path

2. **Output**:
   - Installer will be created at: `dist\ADHD Central Installer.exe`
   - Users can double-click to install ADHD Central on their system

3. **Distribution**:
   - Share `dist\ADHD Central Installer.exe` with users
   - They can install it like any Windows application
   - Uninstall via Windows Control Panel → Programs and Features

---

## Troubleshooting

### Build fails with missing modules:

- Ensure virtual environment is active
- Run: `pip install -r requirements.txt`

### Icons not showing in executable:

- Verify `icon.ico` exists in the project root
- Check that `icons/` folder is present

### NSIS installer fails:

- Ensure `dist\ADHD Central\` folder exists from previous build
- Check NSIS path is correct
- Run Command Prompt as Administrator

---

## Distribution Guide

### For End Users:

**Option A - Simple (No Installation)**

1. Download `ADHD Central.exe`
2. Double-click to run
3. No installation needed

**Option B - Professional (Recommended)**

1. Download `ADHD Central Installer.exe`
2. Double-click to run installer
3. Follow the installation wizard
4. Find "ADHD Central" in Start Menu

---

## Building for Distribution

Complete build workflow:

```bash
# 1. Build executable
build.bat

# 2. Build installer (after NSIS is installed)
"C:\Program Files (x86)\NSIS\makensis.exe" installer.nsi

# 3. Share dist\ADHD Central Installer.exe with users
```

---

## Technical Details

- **PyInstaller**: Converts Python scripts to standalone executables
- **NSIS**: Creates professional Windows installers
- **Spec File**: Defines what gets packaged (executables, data files, icons)

All configuration is in `adhd_central.spec` - modify if you need different settings.
