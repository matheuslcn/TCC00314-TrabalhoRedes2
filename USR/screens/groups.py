import tkinter as tk


def groups_screen(root):
    groups_frame = tk.Frame(root)

    grupos_label = tk.Label(groups_frame, text="Grupos", bg="white", font=("sans-serif", 15))
    grupos_label.pack()

    return groups_frame
