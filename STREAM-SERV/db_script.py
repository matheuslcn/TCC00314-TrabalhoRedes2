'''
Esse script inicializa o banco de dados do trabalho. Use apenas uma vez
'''
import sqlalchemy as sql

if __name__ == "__main__":

    engine = sql.create_engine( 'sqlite:///STREAM-SERV/streaming.db')
    with engine.connect() as conn:

        #-----------------------------------------------------------
        # Tabela dos videos, é chaveada pelo seu nome. Cada video tem sua qualida
        # dede minima e maxima disponivel, a duração e o nome do arquivo contendo 
        # o video 
        #
        # Quanto a qualidade, é um inteiro de 0 a 2, cada um representando um
        # nível descrito pelo enunciado da professora

        conn.execute( sql.text(
            '''
            CREATE TABLE "video"(

                "name" TEXT NOT NULL,

                "duration" NUMERIC NOT NULL,
                "min_quality" INTEGER NOT NULL DEFAULT 0,
                "max_quality" INTEGER NOT NULL DEFAULT 2,

                "file" TEXT NOT NULL,

                PRIMARY KEY("name")
            );
            '''
        ) )

        conn.commit()