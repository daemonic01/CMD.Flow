import curses
import datetime
from utils.localization import t

def draw_menu_info_box(win, ctx, padding=1):
    try:
        now = datetime.datetime.now()

        day_en = now.strftime("%A")
        if ctx.config.lang == "hu":
            day = t("week").get(day_en, day_en)
            date_str = now.strftime(f"%Y.%m.%d. ({day})")
        else:
            date_str = now.strftime("%Y.%m.%d. (%A)")

        time_str = now.strftime("%H:%M:%S")

        rows, cols = win.getmaxyx()

        win.addstr(2, (cols-len(date_str))//2, date_str, curses.A_BOLD)
        win.addstr(3, (cols-len(time_str))//2, time_str, curses.A_NORMAL)
        win.hline(5, 1, "-", cols-2)
        win.addstr(6, 3, f"{t("menu.loaded_projects")}: {len(ctx.data["projektek"])}")
        win.addstr(7, 3, f"0 {t("menu.projects_done")} | 5 {t("menu.projects_in_progress")}")
        win.hline(8, 1, "-", cols-2)
        deadline_text = f"{t("menu.next_deadline")}: 2025.06.27"
        win.addstr(10, max((cols - len(deadline_text)) // 2, 0), deadline_text)

    except curses.error:
        pass
