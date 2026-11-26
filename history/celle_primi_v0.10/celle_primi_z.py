import math
import tkinter as tk
from tkinter import ttk

# --- CONFIGURAZIONE DEFAULT ---
DEFAULT_X = 10
DEFAULT_Y = 10
DEFAULT_Z = 10
MIN_CANVAS_SIZE = 240
ZOOM_STEP = 1.1
MIN_ZOOM = 0.35
MAX_ZOOM = 5.0
# ------------------------------

zoom_factor = 1.0


def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = int(math.sqrt(n)) + 1
    for i in range(3, limit, 2):
        if n % i == 0:
            return False
    return True



def is_perfect_square(n):
    if n < 0:
        return False
    r = math.isqrt(n)
    return r * r == n



def fib_set(limit):
    s = set()
    a, b = 0, 1
    while a <= limit:
        s.add(a)
        a, b = b, a + b
    return s



def safe_get_int(entry, default):
    try:
        return int(entry.get())
    except ValueError:
        return default



def set_entry_int(entry, value):
    entry.delete(0, tk.END)
    entry.insert(0, str(value))



def clamp(value, low, high):
    return max(low, min(value, high))



def total_cells(dim_x, dim_y, dim_z):
    return max(1, dim_x) * max(1, dim_y) * max(1, dim_z)



def global_index_from_xyz(x, y, z, dim_x, dim_y):
    return z * dim_x * dim_y + y * dim_x + x



def map_index_value(global_index, total, placement_mode):
    if placement_mode == "Lineare":
        return global_index
    if placement_mode == "Estremi interlacciati":
        last = total - 1
        if global_index % 2 == 0:
            return global_index // 2
        return last - (global_index // 2)
    return global_index



def get_number_value(global_index, total, placement_mode, shift_enabled):
    n = map_index_value(global_index, total, placement_mode)
    return n + 1 if shift_enabled else n



def cell_style(n, mode, param, fibs=None):
    selected = False
    fill_color = "white"

    if mode == "Primi":
        selected = is_prime(n)
        fill_color = "red" if selected else "white"

    elif mode == "Multipli di k":
        k = max(1, abs(param))
        selected = (n % k == 0)
        fill_color = "red" if selected else "white"

    elif mode == "Quadrati perfetti":
        selected = is_perfect_square(n)
        fill_color = "red" if selected else "white"

    elif mode == "Fibonacci":
        if fibs is None:
            fibs = set()
        selected = (n in fibs)
        fill_color = "red" if selected else "white"

    elif mode == "Residui modulo N":
        m = max(1, abs(param))
        residue_colors = [
            "#ff9999",
            "#99ff99",
            "#9999ff",
            "#ffff99",
            "#ff99ff",
            "#99ffff",
            "#ffcc99",
            "#d9d9d9",
            "#ffcce5",
            "#c2f0c2",
        ]
        fill_color = residue_colors[(n % m) % len(residue_colors)]
        selected = True

    return selected, fill_color



def overlay_fill_color(hits, visible_levels):
    if hits <= 0 or visible_levels <= 0:
        return "white"

    ratio = hits / visible_levels
    ratio = ratio ** 0.6  # enfatizza l'aumento di intensità

    red = 255
    green_blue = int(255 * (1 - ratio))
    green_blue = max(0, min(255, green_blue))
    return f"#{red:02x}{green_blue:02x}{green_blue:02x}"



def update_status_bar(dim_x, dim_y, dim_z, current_z, selected_in_view, selected_total, mode_label):
    overlay_suffix = " [overlay]" if overlay_var.get() else ""
    shift_suffix = " | Numerazione: da 1" if shift_var.get() else " | Numerazione: da 0"

    if overlay_var.get():
        view_label = f"Celle non vuote overlay ({mode_label})"
    else:
        view_label = f"Selezionati livello ({mode_label})"

    status_text = (
        " X: {0} | Y: {1} | Z: {2}"
        " | Celle totali: {3}"
        " | Livello corrente: {4}/{5}"
        " | {6}: {7}"
        " | Selezionati totali: {8}"
        " | Zoom: {9:.2f}x"
        "{10}{11} "
    ).format(
        dim_x,
        dim_y,
        dim_z,
        dim_x * dim_y * dim_z,
        current_z + 1,
        dim_z,
        view_label,
        selected_in_view,
        selected_total,
        zoom_factor,
        overlay_suffix,
        shift_suffix,
    )
    status_var.set(status_text)



def get_dimensions():
    dim_x = max(1, safe_get_int(entry_x, DEFAULT_X))
    dim_y = max(1, safe_get_int(entry_y, DEFAULT_Y))
    dim_z = max(1, safe_get_int(entry_z, DEFAULT_Z))

    set_entry_int(entry_x, dim_x)
    set_entry_int(entry_y, dim_y)
    set_entry_int(entry_z, dim_z)
    return dim_x, dim_y, dim_z



def sync_level_controls(dim_z):
    current_z = clamp(level_var.get(), 0, dim_z - 1)
    level_var.set(current_z)
    level_scale.config(from_=0, to=dim_z - 1)
    level_spin.config(from_=0, to=dim_z - 1)
    level_label_var.set(
        "Livello Z: {0} (visualizzato come {1}/{2})".format(
            current_z, current_z + 1, dim_z
        )
    )



def count_selected_total(total, mode, param, placement_mode, shift_enabled):
    max_value = max(0, total - 1) + (1 if shift_enabled else 0)
    fibs = fib_set(max_value) if mode == "Fibonacci" else None
    count = 0
    for global_index in range(total):
        n = get_number_value(global_index, total, placement_mode, shift_enabled)
        selected, _ = cell_style(n, mode, param, fibs)
        if selected:
            count += 1
    return count



def draw_table(event=None):
    dim_x, dim_y, dim_z = get_dimensions()
    total = total_cells(dim_x, dim_y, dim_z)
    current_z = clamp(level_var.get(), 0, dim_z - 1)
    level_var.set(current_z)
    sync_level_controls(dim_z)

    mode = mode_var.get()
    placement_mode = placement_var.get()
    param = safe_get_int(entry_param, 2)
    shift_enabled = shift_var.get()
    overlay_enabled = overlay_var.get()

    canvas_width = max(canvas.winfo_width(), MIN_CANVAS_SIZE)
    canvas_height = max(canvas.winfo_height(), MIN_CANVAS_SIZE)

    base_cell_w = float(canvas_width) / dim_x
    base_cell_h = float(canvas_height) / dim_y
    base_cell_size = min(base_cell_w, base_cell_h)
    cell_size = base_cell_size * zoom_factor

    grid_width = cell_size * dim_x
    grid_height = cell_size * dim_y

    offset_x = (canvas_width - grid_width) / 2.0 if grid_width < canvas_width else 0
    offset_y = (canvas_height - grid_height) / 2.0 if grid_height < canvas_height else 0

    canvas.delete("all")

    hide_numbers = hide_numbers_var.get()
    draw_grid_lines = show_grid_var.get()

    max_value = max(0, total - 1) + (1 if shift_enabled else 0)
    fibs = fib_set(max_value) if mode == "Fibonacci" else None
    selected_in_view = 0

    for y in range(dim_y):
        for x in range(dim_x):
            x1 = offset_x + x * cell_size
            y1 = offset_y + y * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            if overlay_enabled:
                hits = 0
                last_n = 0

                for z in range(current_z + 1):
                    global_index = global_index_from_xyz(x, y, z, dim_x, dim_y)
                    n = get_number_value(global_index, total, placement_mode, shift_enabled)
                    last_n = n
                    selected, _ = cell_style(n, mode, param, fibs)
                    if selected:
                        hits += 1

                if mode == "Residui modulo N":
                    _, fill_color = cell_style(last_n, mode, param, fibs)
                    cell_has_content = True
                    text_value = str(last_n)
                else:
                    fill_color = overlay_fill_color(hits, current_z + 1)
                    cell_has_content = hits > 0
                    text_value = str(hits)

                if cell_has_content:
                    selected_in_view += 1

            else:
                global_index = global_index_from_xyz(x, y, current_z, dim_x, dim_y)
                n = get_number_value(global_index, total, placement_mode, shift_enabled)
                selected, fill_color = cell_style(n, mode, param, fibs)
                if selected:
                    selected_in_view += 1
                text_value = str(n)

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=fill_color,
                outline="#666" if draw_grid_lines else "",
                width=1 if draw_grid_lines else 0,
            )

            if not hide_numbers:
                font_size = max(7, min(int(cell_size * 0.20), 18))
                canvas.create_text(
                    (x1 + x2) / 2.0,
                    (y1 + y2) / 2.0,
                    text=text_value,
                    font=("Arial", font_size),
                )

    selected_total = count_selected_total(total, mode, param, placement_mode, shift_enabled)
    update_status_bar(dim_x, dim_y, dim_z, current_z, selected_in_view, selected_total, mode)



def adjust_zoom(sign):
    global zoom_factor
    if sign > 0:
        zoom_factor = zoom_factor * ZOOM_STEP
    else:
        zoom_factor = zoom_factor / ZOOM_STEP
    zoom_factor = max(MIN_ZOOM, min(zoom_factor, MAX_ZOOM))



def adjust_x(sign):
    dim_x = max(1, safe_get_int(entry_x, DEFAULT_X) + sign)
    set_entry_int(entry_x, dim_x)



def adjust_y(sign):
    dim_y = max(1, safe_get_int(entry_y, DEFAULT_Y) + sign)
    set_entry_int(entry_y, dim_y)



def adjust_z(sign):
    dim_z = max(1, safe_get_int(entry_z, DEFAULT_Z) + sign)
    set_entry_int(entry_z, dim_z)
    current_z = clamp(level_var.get(), 0, dim_z - 1)
    level_var.set(current_z)



def adjust_level(sign):
    dim_z = max(1, safe_get_int(entry_z, DEFAULT_Z))
    current_z = clamp(level_var.get() + sign, 0, dim_z - 1)
    level_var.set(current_z)



def handle_wheel(sign, state):
    is_shift = bool(state & 0x0001)
    is_ctrl = bool(state & 0x0004)
    is_alt = bool(state & 0x0008)

    if is_ctrl and is_shift:
        adjust_z(sign)
    elif is_ctrl:
        adjust_x(sign)
    elif is_shift:
        adjust_level(sign)
    elif is_alt:
        adjust_y(sign)
    else:
        adjust_zoom(sign)

    draw_table()



def on_mousewheel(event):
    sign = 1 if event.delta > 0 else -1
    handle_wheel(sign, event.state)



def on_mousewheel_linux(event):
    sign = 1 if event.num == 4 else -1
    handle_wheel(sign, event.state)



def reset_view():
    global zoom_factor
    zoom_factor = 1.0
    level_var.set(0)
    draw_table()



def on_dimension_change(event=None):
    draw_table()



def on_level_change(*args):
    draw_table()


# --- GUI ---
root = tk.Tk()
root.title("Celle Primi - livelli Z - V0.10 - 2025")
root.geometry("1200x820")

frame_controls = tk.Frame(root)
frame_controls.pack(padx=10, pady=10, fill="x")

# Dimensioni
label_x = tk.Label(frame_controls, text="X colonne:")
label_x.grid(row=0, column=0, sticky="e", padx=5)
entry_x = tk.Entry(frame_controls, width=8)
entry_x.grid(row=0, column=1)
entry_x.insert(0, str(DEFAULT_X))
entry_x.bind("<Return>", on_dimension_change)

label_y = tk.Label(frame_controls, text="Y righe:")
label_y.grid(row=0, column=2, sticky="e", padx=5)
entry_y = tk.Entry(frame_controls, width=8)
entry_y.grid(row=0, column=3)
entry_y.insert(0, str(DEFAULT_Y))
entry_y.bind("<Return>", on_dimension_change)

label_z = tk.Label(frame_controls, text="Z livelli:")
label_z.grid(row=0, column=4, sticky="e", padx=5)
entry_z = tk.Entry(frame_controls, width=8)
entry_z.grid(row=0, column=5)
entry_z.insert(0, str(DEFAULT_Z))
entry_z.bind("<Return>", on_dimension_change)

btn_draw = tk.Button(frame_controls, text="Disegna", command=draw_table)
btn_draw.grid(row=0, column=6, padx=10)

btn_reset = tk.Button(frame_controls, text="Reset vista", command=reset_view)
btn_reset.grid(row=0, column=7, padx=10)

hide_numbers_var = tk.BooleanVar(value=False)
chk_hide = tk.Checkbutton(
    frame_controls,
    text="Nascondi numeri",
    variable=hide_numbers_var,
    command=draw_table,
)
chk_hide.grid(row=0, column=8, padx=10)

show_grid_var = tk.BooleanVar(value=True)
chk_grid = tk.Checkbutton(
    frame_controls,
    text="Mostra griglia",
    variable=show_grid_var,
    command=draw_table,
)
chk_grid.grid(row=0, column=9, padx=10)

overlay_var = tk.BooleanVar(value=False)
chk_overlay = tk.Checkbutton(
    frame_controls,
    text="Overlay livelli 0..Z",
    variable=overlay_var,
    command=draw_table,
)
chk_overlay.grid(row=0, column=10, padx=10)

shift_var = tk.BooleanVar(value=True)
chk_shift = tk.Checkbutton(
    frame_controls,
    text="Numerazione da 1",
    variable=shift_var,
    command=draw_table,
)
chk_shift.grid(row=0, column=11, padx=10)

# Modalità
label_mode = tk.Label(frame_controls, text="Modalità colore:")
label_mode.grid(row=1, column=0, sticky="e", padx=5, pady=(8, 0))

mode_var = tk.StringVar(value="Primi")
mode_combo = ttk.Combobox(
    frame_controls,
    textvariable=mode_var,
    state="readonly",
    width=18,
    values=[
        "Primi",
        "Multipli di k",
        "Quadrati perfetti",
        "Fibonacci",
        "Residui modulo N",
    ],
)
mode_combo.grid(row=1, column=1, columnspan=2, padx=5, pady=(8, 0))
mode_combo.bind("<<ComboboxSelected>>", draw_table)

label_param = tk.Label(frame_controls, text="Parametro (k / N):")
label_param.grid(row=1, column=3, sticky="e", padx=5, pady=(8, 0))
entry_param = tk.Entry(frame_controls, width=8)
entry_param.grid(row=1, column=4, padx=5, pady=(8, 0))
entry_param.insert(0, "2")
entry_param.bind("<Return>", draw_table)

label_place = tk.Label(frame_controls, text="Disposizione:")
label_place.grid(row=1, column=5, sticky="e", padx=5, pady=(8, 0))
placement_var = tk.StringVar(value="Lineare")
placement_combo = ttk.Combobox(
    frame_controls,
    textvariable=placement_var,
    state="readonly",
    width=18,
    values=["Lineare", "Estremi interlacciati"],
)
placement_combo.grid(row=1, column=6, columnspan=2, padx=5, pady=(8, 0))
placement_combo.bind("<<ComboboxSelected>>", draw_table)

# Controlli livello Z
frame_level = tk.Frame(root)
frame_level.pack(fill="x", padx=10, pady=(0, 8))

level_var = tk.IntVar(value=0)
level_var.trace_add("write", on_level_change)
level_label_var = tk.StringVar(value="Livello Z: 0")

level_info = tk.Label(frame_level, textvariable=level_label_var, anchor="w")
level_info.pack(side="left", padx=(0, 10))

btn_prev = tk.Button(frame_level, text="◀ Livello -", command=lambda: (adjust_level(-1), draw_table()))
btn_prev.pack(side="left", padx=4)

level_scale = tk.Scale(
    frame_level,
    from_=0,
    to=DEFAULT_Z - 1,
    orient="horizontal",
    variable=level_var,
    showvalue=True,
    resolution=1,
    length=400,
)
level_scale.pack(side="left", padx=8)

btn_next = tk.Button(frame_level, text="Livello + ▶", command=lambda: (adjust_level(1), draw_table()))
btn_next.pack(side="left", padx=4)

level_spin = tk.Spinbox(
    frame_level,
    from_=0,
    to=DEFAULT_Z - 1,
    width=6,
    textvariable=level_var,
    command=draw_table,
)
level_spin.pack(side="left", padx=10)

help_label = tk.Label(
    frame_level,
    text="Rotella: zoom | Shift+rotella: livello Z | Ctrl+rotella: X | Alt+rotella: Y | Ctrl+Shift+rotella: Z",
    anchor="e",
)
help_label.pack(side="right")

canvas = tk.Canvas(root, bg="white")
canvas.pack(padx=10, pady=10, expand=True, fill="both")
canvas.bind("<Configure>", draw_table)
canvas.bind("<MouseWheel>", on_mousewheel)
canvas.bind("<Button-4>", on_mousewheel_linux)
canvas.bind("<Button-5>", on_mousewheel_linux)

status_var = tk.StringVar()
status_bar = tk.Label(root, textvariable=status_var, anchor="w", bd=1, relief="sunken")
status_bar.pack(fill="x")

root.after(100, draw_table)
root.mainloop()
