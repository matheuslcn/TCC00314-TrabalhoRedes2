import tkinter as tk
from USR.assets.colors import white_color
from USR.screens.login import login_widget
from USR.widgets.header import header_widget


if __name__ == "__main__":
    root = tk.Tk()
    # full screen ubuntu
    # root.attributes('-zoomed', True)
    # full screen windows
    root.state('zoomed')
    root.title("Streaming de Vídeo")
    root.configure(bg=white_color)

    root_height = root.winfo_screenheight()
    root_width = root.winfo_screenwidth()
    root.geometry(str(root_width) + "x" + str(root_height))

    header_widget(root)
    login_widget(root)
    root.mainloop()
