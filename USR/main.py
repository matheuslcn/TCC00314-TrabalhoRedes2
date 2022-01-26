import tkinter as tk
import USR.assets.colors as colors
from USR.screens.groups import groups_screen
from USR.screens.list_videos import list_videos_screen
from USR.widgets.header import header_widget
import USR.config as config
import socket


def update_screen(screen):
    global login
    global gps_screen
    global videos_screen

    login.destroy()

    if screen == 0:
        gps_screen.destroy()
        videos_screen = list_videos_screen(root, login_text.get())
        videos_screen.pack()
    elif screen == 1:
        videos_screen.destroy()
        gps_screen = groups_screen(root, login_text.get())
        gps_screen.pack()
    else:
        print("Deu ruim")


def check_login(login):
    print('validar usuario ' + login)
    config.send_message_to_manager(f'ENTRAR_NA_APP {login} {socket.gethostname()}')
    login_text.set(login)
    global header
    header.destroy()
    header = header_widget(root, login_text)
    header.pack()
    update_screen(0)


def login_widget(root):
    login_frame = tk.Frame(root, bg="white")
    # login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    login_label = tk.Label(login_frame, text="Login", bg=colors.white_color, font=("sans-serif", 15))
    login_label.pack()
    login_entry = tk.Entry(login_frame, textvariable=login_text, width=20, bg=colors.gray_color, fg=colors.text_color, font=("sans-serif", 15))
    login_entry.pack(pady=10)
    login_btn = tk.Button(
        login_frame,
        text="Entrar",
        bg=colors.dark_blue_color,
        fg=colors.white_color,
        padx=20,
        width=5,
        font=("sans-serif", 12),
        command=lambda: check_login(login_entry.get())
    )
    login_btn.pack(pady=10)

    return login_frame


if __name__ == "__main__":
    config.init()

    root = tk.Tk()
    # full screen ubuntu
    # root.attributes('-zoomed', True)
    # full screen windows
    # root.state('zoomed')
    root.title("Streaming de Vídeo")
    root.configure(bg=colors.white_color)
    root.geometry("1024x650")
    root_height = root.winfo_screenheight()
    root_width = root.winfo_screenwidth()

    menubar = tk.Menu(root)
    root.config(menu=menubar)

    menubar.add_command(
        label='Lista de Vídeos',
        command=lambda: update_screen(0)
    )

    menubar.add_command(
        label='Grupos',
        command=lambda: update_screen(1)
    )

    login_text = tk.StringVar()
    # widgets
    header = header_widget(root)
    login = login_widget(root)
    videos_screen = list_videos_screen(root, login_text.get())
    gps_screen = groups_screen(root, login_text.get())

    header.pack()
    login.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    root.mainloop()


