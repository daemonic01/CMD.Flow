# CMD.Flow

A minimalist, curses-based task & project workflow manager built entirely for the terminal.

CMD.Flow allows you to create structured projects with four hierarchical levels:
**Project → Phase → Task → Subtask** – all displayed in a compact retro-style interface.

---

## 🔧 Features (v0.4.0)

- Four-level hierarchical structure (Project → Phase → Task → Subtask)
- Manual JSON-based save/load
- Modular view system with `FooterController` support
- Project creation & deletion interface
- INFO panel and dynamic logo rendering
- Project cards with progress bars and extended metadata
- Window size validation and fallback message
- Help menus and footer hints
- Built-in changelog panel

---

## 📖 Why v0.4.0?

Earlier versions (0.1.0–0.3.0) were internal prototypes used to explore layout, input handling, and structural design.  
**v0.4.0 is the first usable and modular version**, marking the start of public development.

---

## 🚀 Roadmap

Planned for upcoming releases:

- Settings panel with `config.ini` support
- Theme/skin system
- Multilingual support (starting with English & Hungarian)
- Logging panel for last 10 system messages
- INFO/WARNING/ERROR message types
- Fully editable project details and in-place form editing
- Compact/Normal/Extended display modes

---

## 🛠️ Getting Started

```bash
git clone https://github.com/<your-user>/CMDFlow.git
cd CMDFlow
python core/main.py
```

Tested with **Python 3.10+** on Windows and Linux (Curses required)

---

## 📄 License

MIT License – use freely and break things responsibly.
