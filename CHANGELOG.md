# CMD.Flow Changelog

## [v0.4.0] – 2025-07-25

### Added
- `short_desc` field support across all item types
- `is_done` propagation system (automatic completion logic across hierarchy)
- Project statistics in INFO panel (completed vs. remaining projects)
- Nearest deadline indicator in INFO panel
- Demo project data generator (from main menu)
- BACKSPACE navigation for Project View
- Refined add/edit/delete logic for all levels
- Footer action visibility adjusted per context
- Character limit enforcement for all input fields (configurable via `LayoutConfig`)
- Toggleable status box in subtask detail view
- View-specific behavior based on hierarchy level
- English localization (full rewrite of UI strings)

### Changed
- Refactored backend logic for better update propagation
- Unified add/edit system via `open_entry_form()`
- Moved config values to centralized `layout_config` object
- Rewritten view logic in `ProjectView` for clarity and modularity
- Cleaned up main control loop (`main.py`) for stability

### Fixed
- Subtask toggle now reliably updates parent state
- Flickering issue when returning from form to table view
- Proper parent tracking via `get_parent()` helper
- Prevented creation of children under subtasks
- Footer no longer displays "New" action when invalid
- Resolved erratic scroll behavior in detail tables
- ENTER key behavior now properly distinguishes between branching and toggling

### Notes
This is the first **public**, feature-complete, modular version.  
All major base systems are in place for future refinements and expansion.

---

## Previous Internal Milestones

### v0.3.0 *(Unreleased – UI Prototype)*
- First attempts at integrating curses-based visual layout
- Static logo rendering
- No modularity

### v0.2.0 *(Unreleased – Data Handling Test)*
- Early JSON data structure and hierarchy draft
- No interface

### v0.1.0 *(Unreleased – Concept Stage)*
- Directory sketches, handwritten notes, functional experiments
