import tkinter as tk
import USR.assets.colors as colors
import USR.config as config
import easygui


def add_video():

    video_path = easygui.fileopenbox()
    temp = video_path.split('\\')
    video_name = temp[len(temp)-1]
    config.send_message_to_streaming(f'UPLOAD {video_name} {video_path}')
    print("video adicionado")


def list_videos_widget(root, videos, group):
    for video in videos:
        video_widget(root, video, group)


def play_video(video, group):
    print("Rodar o Video " + video['title'])
    if group is None:
        print("Rodar apenas para mim")
    else:
        print("Rodar para o grupo " + group['title'])


def delete_video(video):
    print("Apagar o Video " + video['title'])


def video_widget(root, video, group):
    video_frame = tk.Frame(root, bg=colors.dark_gray_color)
    video_frame.pack(pady=10)

    # usar imagem depois
    label_image = tk.Label(
        video_frame,
        text=video['thumbnail'],
        bg=colors.gray_color,
        font=("sans-serif", 12)
    )
    label_image.grid(row=1, column=1, padx=(20, 100), pady=5)

    title_frame = tk.Frame(video_frame, bg=colors.dark_gray_color)
    title_frame.grid(row=1, column=2, padx=(20, 150), pady=5)
    title_label = tk.Label(
        title_frame,
        text=video['title'],
        bg=colors.dark_gray_color,
        fg=colors.white_color,
        font=("sans-serif", 12)
    )
    title_label.pack()
    duration_label = tk.Label(
        title_frame,
        text=video['duration'],
        bg=colors.dark_gray_color,
        fg=colors.white_color,
        font=("sans-serif", 12)
    )
    duration_label.pack()

    options_frame = tk.Frame(video_frame, bg=colors.dark_gray_color)
    options_frame.grid(row=1, column=3, padx=(150, 20), pady=5)
    play_btn = tk.Button(
        options_frame,
        text="Play",
        bg=colors.dark_blue_color,
        fg=colors.white_color,
        padx=20,
        font=("sans-serif", 12),
        width=5,
        command=lambda: play_video(video, group)
    )
    play_btn.grid(row=1, column=1, padx=10)
    delete_btn = tk.Button(
        options_frame,
        text="Delete",
        bg=colors.red_color,
        fg=colors.white_color,
        padx=20,
        font=("sans-serif", 12),
        width=5,
        command=lambda: delete_video(video)
    )
    delete_btn.grid(row=1, column=2, padx=10)


def list_videos_screen(root, owner, group=None):
    videos = [
        {
            'title': 'Titulo Video 01',
            'duration': '3min',
            'thumbnail': 'thumbnail.jpg'
        },
        {
            'title': 'Titulo Video 02',
            'duration': '5min',
            'thumbnail': 'thumbnail2.jpg'
        },
        {
            'title': 'Titulo Video 03',
            'duration': '7min',
            'thumbnail': 'thumbnail3.jpg'
        },
        {
            'title': 'Titulo Video 04',
            'duration': '5min',
            'thumbnail': 'thumbnail4.jpg'
        }
    ]

    root_width = root.winfo_screenwidth()
    root_height = root.winfo_screenheight()
    videos_frame = tk.Frame(root, bg=colors.white_color)

    videos_label = tk.Label(
        videos_frame,
        bg=colors.white_color,
        text="Lista de Vídeos",
        font=("sans-serif", 15)
    )
    videos_label.pack(pady=10)

    add_video_frame = tk.Frame(videos_frame, bg=colors.white_color)
    add_video_frame.pack(padx=100)
    add_video_frame.configure(width=root_width, height=38)
    add_video_frame.propagate(0)

    add_video_btn = tk.Button(
        add_video_frame,
        text="Adicionar Vídeo",
        bg=colors.green_color,
        fg=colors.white_color,
        padx=20,
        width=10,
        font=("sans-serif", 12),
        command=add_video,
    )
    add_video_btn.pack(side=tk.LEFT)

    list_videos_frame = tk.Frame(videos_frame, bg=colors.white_color)
    list_videos_frame.pack()
    list_videos_frame.configure(width=root_width, height=root_height)
    list_videos_frame.propagate(0)

    list_videos_widget(list_videos_frame, videos, group)

    return videos_frame
