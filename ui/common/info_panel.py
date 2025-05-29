from utils.localization import t

def draw_info_panel(win, version: str, build: str):
    rows, cols = win.getmaxyx()
    win.addstr(1, cols - 33, f"[INFO] {t("footer.info_panel.active_version")}: {version}")
    win.addstr(2, cols - 26, f"{t("footer.info_panel.build")}: {build}")