# CMD.Flow

A minimalist, curses-based task & project workflow manager built entirely for the terminal.

CMD.Flow lets you create and manage structured projects with four hierarchical levels:  
**Project → Phase → Task → Subtask** – all displayed in a compact retro-style interface.

---

## 🔧 Features (v0.4.0)

- Four-level hierarchical structure (Project → Phase → Task → Subtask)
- Manual JSON-based save/load system
- Dynamic progress calculation with `is_done` propagation
- Demo data generator for testing
- Short and full description fields per item
- Modular view system with `FooterController`
- Project creation, editing & deletion interface
- Project card view with progress bars and metadata
- Details panel with optional subtask table view
- Window size validation and fallback message
- INFO panel (project count, completed vs. remaining, upcoming deadlines)
- Help menus and footer hints
- Built-in changelog viewer
- Keyboard navigation (arrows, ENTER, TAB, BACKSPACE)

---

## 📖 Why v0.4.0?

Earlier versions (0.1.0–0.3.0) were internal prototypes used to explore layout, input handling, and structural design.  
**v0.4.0 is the first feature-complete and modular version**, intended as a public developer preview.  
Expect occasional curses-induced rage.

---

## 🚀 Roadmap Highlights

Planned for future versions:

- Settings panel (`config.ini`) support
- Theme/skin system
- Multilingual support (EN & HU)
- Compact/Normal/Extended view modes
- Footer-integrated message logging (last 10 entries)
- Structured system messages (INFO/WARNING/ERROR)
- In-place editing and smarter form behavior
- Refactored logo and visual improvements
- Transition to [Textual](https://textual.textualize.io/) (possible future direction)

---

## 🛠️ Getting Started

```bash
git clone https://github.com/<your-user>/CMDFlow.git
cd CMDFlow
python core/main.py


---

## 📄 License

MIT License – use freely and break things responsibly.
