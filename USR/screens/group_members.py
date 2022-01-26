import tkinter as tk
import USR.assets.colors as colors
from USR.screens.add_member_group import add_member_group_screen
from USR.screens.list_videos import list_videos_screen


def list_members_widget(root, frame, members):
    for member in members:
        members_widget(root, frame, member)


def delete_member(member):
    print("remover membro " + str(member['name']))


def members_widget(root, frame, member):
    member_frame = tk.Frame(frame, bg=colors.dark_gray_color)
    member_frame.pack(pady=10)

    label_title = tk.Label(
        member_frame,
        text=member['name'],
        bg=colors.gray_color,
        font=("sans-serif", 12)
    )
    label_title.grid(row=1, column=1, padx=(20, 100), pady=5)

    options_frame = tk.Frame(member_frame, bg=colors.dark_gray_color)
    options_frame.grid(row=1, column=2, padx=(150, 20), pady=5)

    delete_btn = tk.Button(
        options_frame,
        text="Delete",
        bg=colors.red_color,
        fg=colors.white_color,
        padx=20,
        font=("sans-serif", 12),
        width=5,
        command=lambda: delete_member(member)
    )
    delete_btn.pack(padx=10)


def add_member(root, group, owner):
    print("Adicionar usuário ao grupo " + str(group['title']))
    # abrir uma nova tela para adicionar o usuario
    add_member_group = add_member_group_screen(root, group, owner)


def play_video_group(root, group, owner):
    print("Rodar video para o grupo: [" + str(group['title']) + ", " + str(group['owner']) + "]")
    # abrir uma janela pra escolher o video
    new_window = tk.Toplevel(root)
    new_window.title('Videos para reproduzir pro grupo ' + str(group['title']))
    new_window.configure(bg=colors.white_color)
    new_window.geometry("1024x650")
    list_video = list_videos_screen(new_window, owner, group)
    list_video.pack()


def group_members_screen(master, group, owner):
    root = tk.Toplevel(master)
    root.title('Integrantes')
    root.configure(bg=colors.white_color)
    root.geometry("900x600")

    root_width = root.winfo_screenwidth()
    root_height = root.winfo_screenheight()

    members = [
        {
            'owner': group['owner'],
            'name': 'login1',
        },
        {
            'owner': group['owner'],
            'name': 'login2',
        },
        {
            'owner': group['owner'],
            'name': 'login3',
        },
        {
            'owner': group['owner'],
            'name': 'login4',
        },
    ]

    members_frame = tk.Frame(root, bg=colors.white_color)
    members_frame.pack()

    members_label = tk.Label(
        members_frame,
        text="Integrantes do grupo " + str(group['title']),
        bg=colors.white_color,
        font=("sans-serif", 15)
    )
    members_label.pack(pady=10)

    btns_member_frame = tk.Frame(members_frame, bg=colors.white_color)
    btns_member_frame.pack(padx=100)
    btns_member_frame.configure(width=root_width, height=38)
    btns_member_frame.propagate(0)

    add_member_btn = tk.Button(
        btns_member_frame,
        text="Adicionar Usuário",
        bg=colors.green_color,
        fg=colors.white_color,
        padx=20,
        width=10,
        font=("sans-serif", 12),
        command=lambda: add_member(root, group, owner),
    )
    add_member_btn.pack(side=tk.LEFT)
    add_member_btn = tk.Button(
        btns_member_frame,
        text="Play Vídeo",
        bg=colors.dark_blue_color,
        fg=colors.white_color,
        padx=20,
        width=9,
        font=("sans-serif", 12),
        command=lambda: play_video_group(root, group, owner),
    )
    add_member_btn.pack(side=tk.RIGHT)

    list_members_frame = tk.Frame(members_frame, bg=colors.white_color)
    list_members_frame.pack()
    list_members_frame.configure(width=root_width, height=root_height)
    list_members_frame.propagate(0)

    list_members_widget(root, list_members_frame, members)

    return root
