import tkinter as tk
import USR.assets.colors as colors

global member_login_text


def check_login(login, group, owner, root):
    print("validar o login " + str(login) + " e adicionar no grupo " + str(group['title']) + " do usuario " + str(owner))
    root.destroy()
    # informar com uma mensagem de texto


def quit_member_screen(root):
    print("Cancelar a inserção do usuário")
    root.destroy()


def member_login_widget(root, group, owner):
    global member_login_text
    member_login_frame = tk.Frame(root, bg=colors.white_color)
    login_label = tk.Label(member_login_frame, text="Login do usuário", bg=colors.white_color, font=("sans-serif", 15))
    login_label.pack()
    login_entry = tk.Entry(
        member_login_frame,
        textvariable=member_login_text,
        width=20, bg=colors.gray_color,
        fg=colors.text_color,
        font=("sans-serif", 12)
    )
    login_entry.pack(pady=10)

    options_frame = tk.Frame(member_login_frame, bg=colors.white_color)
    options_frame.pack()
    add_member_btn = tk.Button(
        options_frame,
        text="Adicionar",
        bg=colors.green_color,
        fg=colors.white_color,
        padx=20,
        width=5,
        font=("sans-serif", 12),
        command=lambda: check_login(login_entry.get(), group, owner, root)
    )
    add_member_btn.pack(pady=10)
    cancel_member_btn = tk.Button(
        options_frame,
        text="Cancelar",
        bg=colors.red_color,
        fg=colors.white_color,
        padx=20,
        width=5,
        font=("sans-serif", 12),
        command=lambda: quit_member_screen(root)
    )
    cancel_member_btn.pack(pady=10)

    return member_login_frame


def add_member_group_screen(master, group, owner):
    root = tk.Toplevel(master)
    root.title('Adicionar Integrante')
    root.configure(bg=colors.white_color)
    root.geometry("400x400")
    global member_login_text
    member_login_text = tk.StringVar()
    member_frame = member_login_widget(root, group, owner)
    #
    member_frame.pack()
    member_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    return root
