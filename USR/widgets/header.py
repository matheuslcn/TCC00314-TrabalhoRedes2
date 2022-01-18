import tkinter as tk

from USR.assets.colors import light_blue_color, text_color


def header_widget(root):
    root_width = root.winfo_screenwidth()

    header_frame = tk.Frame(root, height=50, pady=10, padx=70, bg=light_blue_color)
    header_frame.grid()

    title_frame = tk.Frame(header_frame, width=root_width, bg=light_blue_color)
    title_frame.pack()
    title = tk.Label(
        header_frame,
        text="Streaming de Vídeo",
        bg=light_blue_color,
        fg=text_color,
        font=("sans-serif", 18, "bold")
    )
    title.pack(side='left')
