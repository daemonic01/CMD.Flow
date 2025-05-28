from ui.views.popup_confirm import PopupConfirmView
from utils.localization import t

def close_app(ctx):
    return PopupConfirmView(
                    ctx,
                    message=t("menu.exit_confirm"),
                    on_accept=lambda: exit(),
                    on_cancel=lambda: "pop"
                )