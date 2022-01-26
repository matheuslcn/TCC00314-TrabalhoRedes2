import tkinter as tk
import USR.assets.colors as colors
from USR.screens.add_group import add_group_screen
from USR.screens.group_members import group_members_screen
from USR.screens.list_videos import list_videos_screen


def add_group(root, owner):
    print("Adicionar grupo")
    add_group__screen = add_group_screen(root, owner)


def list_groups_widget(root, frame, groups, owner):
    for group in groups:
        group_widget(root, frame, group, owner)


def play_video_group(root, group, owner):
    print("Rodar video para o grupo: [" + str(group['title']) + ", " + str(group['owner']) + "]")
    # abrir uma janela pra escolher o video
    new_window = tk.Toplevel(root)
    new_window.title('Videos para reproduzir pro grupo ' + str(group['title']))
    new_window.configure(bg=colors.white_color)
    new_window.geometry("1024x650")
    list_video = list_videos_screen(new_window, owner, group)
    list_video.pack()


def delete_group(group, owner):
    print("Remover vídeo: [" + str(group['title']) + ", " + str(group['owner']) + "]")


def members_group(root, group, owner):
    print("Membros do grupo")
    # abrir uma nova janela mostrando os integrantes do grupo
    members_screen = group_members_screen(root, group, owner)


def group_widget(root, frame, group, owner):
    group_frame = tk.Frame(frame, bg=colors.dark_gray_color)
    group_frame.pack(pady=10)

    label_title = tk.Label(
        group_frame,
        text=group['title'],
        bg=colors.gray_color,
        font=("sans-serif", 12)
    )
    label_title.grid(row=1, column=1, padx=(20, 100), pady=5)

    options_frame = tk.Frame(group_frame, bg=colors.dark_gray_color)
    options_frame.grid(row=1, column=2, padx=(150, 20), pady=5)
    play_btn = tk.Button(
        options_frame,
        text="Play Vídeo",
        bg=colors.dark_blue_color,
        fg=colors.white_color,
        padx=20,
        font=("sans-serif", 12),
        width=5,
        command=lambda: play_video_group(root, group, owner)
    )
    play_btn.grid(row=1, column=1, padx=10)
    members_btn = tk.Button(
        options_frame,
        text="Integrantes",
        bg=colors.light_blue_color,
        fg=colors.white_color,
        padx=20,
        font=("sans-serif", 12),
        width=5,
        command=lambda: members_group(root, group, owner)
    )
    members_btn.grid(row=1, column=2, padx=10)
    delete_btn = tk.Button(
        options_frame,
        text="Delete",
        bg=colors.red_color,
        fg=colors.white_color,
        padx=20,
        font=("sans-serif", 12),
        width=5,
        command=lambda: delete_group(group, owner)
    )
    delete_btn.grid(row=1, column=3, padx=10)


def groups_screen(root, owner):
    groups = [
        {
            'owner': 'login1',
            'title': 'titulo1',
        },
        {
            'owner': 'login2',
            'title': 'titulo2',
        },
        {
            'owner': 'login3',
            'title': 'titulo3',
        },
        {
            'owner': 'login4',
            'title': 'titulo4',
        },
    ]

    print("Dono do grupo " + str(owner))

    root_width = root.winfo_screenwidth()
    root_height = root.winfo_screenheight()
    groups_frame = tk.Frame(root, bg=colors.white_color)

    groups_label = tk.Label(groups_frame, text="Grupos", bg=colors.white_color, font=("sans-serif", 15))
    groups_label.pack(pady=10)

    add_group_frame = tk.Frame(groups_frame, bg=colors.white_color)
    add_group_frame.pack(padx=100)
    add_group_frame.configure(width=root_width, height=38)
    add_group_frame.propagate(0)

    add_video_btn = tk.Button(
        add_group_frame,
        text="Adicionar Grupo",
        bg=colors.green_color,
        fg=colors.white_color,
        padx=20,
        width=10,
        font=("sans-serif", 12),
        command=lambda: add_group(root, owner),
    )
    add_video_btn.pack(side=tk.LEFT)

    list_groups_frame = tk.Frame(groups_frame, bg=colors.white_color)
    list_groups_frame.pack()
    list_groups_frame.configure(width=root_width, height=root_height)
    list_groups_frame.propagate(0)

    list_groups_widget(root, list_groups_frame, groups, owner)

    return groups_frame
