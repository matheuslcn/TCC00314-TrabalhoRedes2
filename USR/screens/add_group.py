import tkinter as tk
import USR.assets.colors as colors

global group_text


def check_group(title, owner, root):
    print("validar o nome do grupo " + str(title) + " e o seu dono " + str(owner))
    root.destroy()
    # informar com uma mensagem de texto


def quit_member_screen(root):
    print("cancelar criação do grupo")
    root.destroy()


def group_title_widget(root, owner):
    global group_text
    group_text_frame = tk.Frame(root, bg=colors.white_color)
    group_label = tk.Label(
        group_text_frame,
        text="Nome do Grupo",
        bg=colors.white_color,
        font=("sans-serif", 15)
    )
    group_label.pack()
    group_entry = tk.Entry(
        group_text_frame,
        textvariable=group_text,
        width=20, bg=colors.gray_color,
        fg=colors.text_color,
        font=("sans-serif", 12)
    )
    group_entry.pack(pady=10)

    options_frame = tk.Frame(group_text_frame, bg=colors.white_color)
    options_frame.pack()
    add_member_btn = tk.Button(
        options_frame,
        text="Adicionar",
        bg=colors.green_color,
        fg=colors.white_color,
        padx=20,
        width=5,
        font=("sans-serif", 12),
        command=lambda: check_group(group_entry.get(), owner, root)
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

    return group_text_frame


def add_group_screen(master, owner):
    root = tk.Toplevel(master)
    root.title('Adicionar Grupo')
    root.configure(bg=colors.white_color)
    root.geometry("400x400")

    global group_text
    group_text = tk.StringVar()
    group_title_frame = group_title_widget(root, owner)
    #
    group_title_frame.pack()
    group_title_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    return root
