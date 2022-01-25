import tkinter as tk
import USR.assets.colors as colors


def header_widget(root, login_text=None):
    root_width = root.winfo_screenwidth()

    header_frame = tk.Frame(root, height=50, pady=10, padx=70, bg=colors.light_blue_color)
    header_frame.configure(width=root_width, height=50)
    header_frame.propagate(0)

    title_frame = tk.Frame(header_frame, bg=colors.light_blue_color)
    title_frame.pack()
    title = tk.Label(
        header_frame,
        text="Streaming de Vídeo",
        bg=colors.light_blue_color,
        fg=colors.text_color,
        font=("sans-serif", 15, "bold")
    )
    title.pack(side=tk.LEFT)

    login_frame = tk.Frame(header_frame)
    login_frame.pack(side=tk.RIGHT)
    login_label = tk.Label(
        login_frame,
        text="",
        textvariable=login_text,
        bg=colors.light_blue_color,
        fg=colors.text_color,
        font=("sans-serif", 12, "bold")
    )
    login_label.pack()

    return header_frame
