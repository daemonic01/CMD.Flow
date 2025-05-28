# helpers/state_utils.py
def set_mode(ctx, new_mode: str):
    ctx.control.mode = new_mode
