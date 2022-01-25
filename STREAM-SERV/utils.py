# from socket import *
from collections import namedtuple
import time
import random
from string import ascii_lowercase

# import pandas
import sqlalchemy as sql
from numpy import clip

video_tuple = namedtuple('video_tuple', ['name', 'duration', 'min_quality', 'max_quality', 'file'])


def add_video(name, duration, min_quality=0, max_quality=2, file_type='.mp4'):
    """
    Adiciona o video para o banco de dados.

    Lembrando que a tabela videos não contém os videos em si, mas metadados dos mesmos. O conteudo em si
    deve ser adicinado manualmente ( por enquanto ) por fora, na pasta "video_fls".
    """

    # -----------------------------------------------------------
    # Niveis de qualidade:
    # 0 - 240p
    # 1 - 480p
    # 2 - 720p
    min_quality = clip(min_quality, 0, 2)
    max_quality = clip(max_quality, min_quality, 2)

    engine = sql.create_engine('sqlite:///STREAM-SERV/streaming.db')
    with engine.connect() as conn:

        add_stm = "INSERT INTO video ( name , duration, min_quality , max_quality , file ) values ( \"{}\" , {} , {} , {} , \"{}\" )".format(
            name, duration, min_quality, max_quality, file_type)
        rmv_stm = "DELETE FROM video WHERE name = \"{}\"".format(name)

        try:
            conn.execute(sql.text(add_stm))
        except sql.exc.DatabaseError:
            conn.execute(sql.text(rmv_stm))
            conn.execute(sql.text(add_stm))


def get_file_name(video_name, quality, video_format):
    quality = clip(quality, 0, 2)
    video_qual = ["360", "480", "720"][quality]

    return "STREAM-SERV/videos_fls/{}_{}.{}".format(video_name, video_qual, video_format)


def fetch_video(video_name, quality):
    """
    Busca um video pelo nome, e manda um file object como resposta, se o video existir no
    BD
    """

    engine = sql.create_engine('sqlite:///STREAM-SERV/streaming.db')
    with engine.connect() as conn:

        slc_stm = "SELECT * FROM video WHERE name = \"{}\"".format(video_name)
        seq = conn.execute(sql.text(slc_stm))
        if seq is None:
            raise ValueError("VIDEO NAO ENCONTRADO")

        db_tup = seq.first()
        if not (db_tup.max_quality >= quality >= db_tup.min_quality):
            raise ValueError("QUALIDADE NAO DISPONIVEL")

        file_name = get_file_name(db_tup.name, quality, db_tup.file)
        return open(file_name, 'rb')


def list_all_videos():
    engine = sql.create_engine('sqlite:///STREAM-SERV/streaming.db')
    with engine.connect() as conn:

        seq = conn.execute("SELECT name FROM video")
        if seq is None:
            return

        for row in seq:
            yield row
