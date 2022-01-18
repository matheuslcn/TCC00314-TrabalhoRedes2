import tkinter as tk

from USR.assets.colors import white_color, dark_blue_color, gray_color, text_color
from USR.screens.list_videos import list_videos
from USR.widgets.header import header_widget


def action_btn(text, login_frame):
    
    login_frame.destroy()
    list_videos(login_frame.master)



def login_widget(root):
    root_height = root.winfo_screenheight()
    root_width = root.winfo_screenwidth()

    login_frame = tk.Frame(root, bg="white", pady=root_height/4)
    login_frame.grid()

    login_label_frame = tk.Frame(login_frame, width=root_width / 5)
    login_label_frame.grid(column=0, row=0, pady=5)

    login_label = tk.Label(login_label_frame, text="Login", bg="white", font=("sans-serif", 15))
    login_label.pack()

    login_entry = tk.Entry(login_frame, width=20, bg=gray_color, fg=text_color, font=("sans-serif", 15))
    login_entry.grid(column=0, row=1, pady=5)

    login_btn = tk.Button(
        login_frame,
        text="Entrar",
        bg=dark_blue_color,
        fg=white_color,
        padx=20,
        font=("sans-serif", 15),
        command=lambda: action_btn(login_entry.get(), login_frame)
    )
    login_btn.grid(column=0, row=2, pady=20)