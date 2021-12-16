'''
Esse script inicializa o banco de dados do trabalho. Use apenas uma vez
'''
import sqlalchemy as sql

if __name__ == "__main__":

    engine = sql.create_engine( 'sqlite:///CONTROL-SERV/controle.db')

    with engine.connect() as conn:

        #-----------------------------------------------------------
        # Tabela dos usuarios. Cada entrada é um nome de usuario ( string )
        # e um booleano indicando se é um premium ou nao.
        conn.execute( sql.text(
            '''
            CREATE TABLE "user"(
                "name"	TEXT NOT NULL,
                "premium"	INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY("name")
            );
            '''
        ) )

        #-----------------------------------------------------------
        # Tabela de grupos. Suas tuplas sao as contem o nome do grupo
        # e o nome do dono. Um constraint é que o dono tem que ser premium
        conn.execute( sql.text(
            '''
            CREATE TABLE "group"(
                "name" TEXT NOT NULL,
                "owner" TEXT NOT NULL,

                PRIMARY KEY ("name"),
                FOREIGN KEY ("owner") REFERENCES "user"("name")
                ON DELETE CASCADE
            );
            '''
        ) )

        #-----------------------------------------------------------
        # Tabela relação entre grupos e usuários
        conn.execute( sql.text(
            '''
            CREATE TABLE "membership"(
                "u_name" TEXT NOT NULL,
                "g_name" TEXT NOT NULL,

                FOREIGN KEY ("u_name") REFERENCES  "user"("name")
                ON DELETE CASCADE,

                FOREIGN KEY ("g_name") REFERENCES "group"("name")
                ON DELETE CASCADE
            );
            '''
        ) )

        conn.commit()