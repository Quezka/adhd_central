# ADHD Central
ADHD Central is a lightweight, cross‑platform productivity tool designed around ADHD‑friendly workflows.
It focuses on reducing friction, lowering activation energy, and making decisions easier through simple, fast, and structured tools.
This project currently includes:
- A Qt Widgets desktop app (Python + PySide6)
- A JSON‑based local database
- Optional Syncthing sync support
- A planned Android app (Java)

# ✨ Features
## 📝 Task Manager
- Add tasks instantly
- Remove tasks
- Random task picker to break decision paralysis
- Persistent storage in data.json
## ⏱ Sprint Timer
- 5‑minute sprint cycles
- Start / Stop / Clear controls
- Automatic logging of completed sprints
- Real‑time countdown display
- Helps kickstart focus and build momentum
## 😴 Sleep Log
- One‑tap “Sleep” and “Wake” logging
- Timestamped entries
- Included in weekly summaries
## 📊 Weekly Review
- Calculates:
- Total sprints
- Total focused minutes
- Sleep log entries
- Week start date
- Helps you reflect on habits and progress
## 🔄 Syncthing‑Ready Storage
All data is stored in a single JSON file:
data.json

This file is:
- Human‑readable
- Easy to back up
- Easy to sync across devices
- Compatible with Syncthing, Dropbox, iCloud, etc.

# 🧱 Tech Stack
Desktop App
- Python 3
- PySide6 (Qt Widgets)
- JSON persistence
# Planned Mobile App
- Android (Java)
- Shared JSON schema
- Optional Syncthing integration

# 📁 Project Structure
adhd_central/
│
├── main.py               # App entry point
├── backend.py            # Core logic (tasks, timer, sleep, weekly review)
├── data.json             # Local database (auto-created)
│
├── ui/                   # Qt UI files (if applicable)
└── android/              # Android app (planned)

# 🔧 Installation
## 1. Go to the Releases page
## 2. Download ADHD-Central.exe (portable) or ADHD-Central-Installer.exe (installer)
## 3. Use!

# 🔄 Syncing Data with Syncthing (Optional)
You can sync your data.json across devices using Syncthing:
- Create a shared folder in Syncthing
- Place data.json inside it
- Point the app to that folder (configurable path)
- Syncthing keeps everything in sync automatically
This gives you a peer‑to‑peer cloud backend without servers.

# 🛣 Roadmap
- Android app (Java/Kotlin)
- iOS app (Swift)
- Better task categories & tagging
- Daily/Monthly review pages
- Charts & analytics
- Optional encrypted sync backend
- UI improvements (themes, animations, acrylic/Mica on Windows)

# 🤝 Contributing
Contributions are welcome!
Feel free to open issues, submit PRs, or propose features.

# 📜 License
MIT License — see ```LICENSE``` for details.
