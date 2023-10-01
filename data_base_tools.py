import psycopg2


class Data_Base_Tools:
    """
    Data_Base_Tools при создании экземпляра класса принимает значения data_base_name, login, password, host, port.
    По умолчанию значения host=127.0.0.1, port=5432.

    add_data_base_table - метод создает набор таблиц, не принимает аргументов.

    add_person_in_people_list - метод принимает значения id_vk, first_name, last_name, sex, birthday, city
    добавляет строку в таблицу people и возвращает id добавленной строки.

    select_person_id - метод принимает значения first_name, last_name и возвращет id строки с данными пользователя из
    таблицы people, в виде кортежа.

    add_person_in_like_list - метод принимает id_person, id_like_person, являющиеся id строк из таблицы people и
    добавляет строку в таблицу like_list и возвращает id добавленной строки.

    add_person_in_ban_list - метод принимает id_person, id_ban_person, являющиеся id строк из таблицы people и
    добавляет строку в таблицу ban_list и возвращает id добавленной строки.

    delete_person_out_ban_list - метод принимает id_person, id_ban_person, являющиеся id строк из таблицы people и
    удаляет строку из таблицы ban_list

    delete_person_out_like_list - метод принимает id_person, id_like_person, являющиеся id строк из таблицы people и
    удаляет строку из таблицы like_list

    select_like_people - метод принимает id_person и возвращает список кортежей значений id_like_person

    select_ban_people - метод принимает id_person и возвращает список кортежей значений id_ban_person

    add_photo -  метод принимает id_person и url_photo, id_person является  id строки из таблицы people,
    добавляет строку в таблицу photo_tab и возвращает id добавленной строки

    select_photo - метод принимает id_person, id_person является  id строки из таблицы people
    и возвращает список кортежей со значениями стобца url.
        """

    def __init__(self, data_base_name, login, password,  host="127.0.0.1", port="5432"):
        self.data_base_name = data_base_name
        self.login = login
        self.password = password
        self.host = host
        self.port = port

    def add_data_base_tables(self):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute('create table if not exists people(\
            id SERIAL primary key, \
            id_vk varchar(90) not null unique, \
            first_name VARCHAR(60) not null, \
            last_name VARCHAR(60) not null, \
            sex VARCHAR(10) not null, \
            birthday VARCHAR(10) not null, \
            city VARCHAR(15) not null)')
            cur.execute('create table if not exists photo_tab(\
            id SERIAL primary key,\
            id_person integer not null references people(id),\
            url_photo VARCHAR(240) not null unique)')
            cur.execute('create table if not exists ban_list(\
            id_ban SERIAL primary key,\
            id_person integer not null references people(id),\
            id_ban_person integer not null references people(id))')
            cur.execute('create table if not exists like_list(\
            id_like SERIAL primary key,\
            id_person integer not null references people(id),\
            id_like_person integer not null references people(id))')
            conn.commit()
        conn.close()

    def add_person_in_people_list(self, id_vk, first_name, last_name, sex, birthday, city):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute('insert into people(id_vk, first_name, last_name, sex, birthday, city)\
            values(%s, %s, %s, %s, %s, %s) RETURNING id', (id_vk, first_name, last_name, sex, birthday, city))
            conn.commit()
            returning = cur.fetchone()
        conn.close()
        return returning

    def add_photo(self, id_person, url_photo):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute('insert into photo_tab(id_person, url_photo) values(%s, %s) RETURNING id', (id_person, url_photo))
            conn.commit()
            returning = cur.fetchone()
        conn.close()
        return returning

    def select_photo(self, id_person):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute('select url_photo from photo_tab where id_person = %s', (id_person,))
            conn.commit()
            returning = cur.fetchall()
        conn.close()
        return returning

    def add_person_in_like_list(self, id_person, id_like_person):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute('insert into like_list(id_person, id_like_person)\
            values(%s, %s) RETURNING id_like', (id_person, id_like_person))
            conn.commit()
            returning = cur.fetchone()
        conn.close()
        return returning

    def add_person_in_ban_list(self, id_person, id_ban_person):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute('insert into ban_list(id_person, id_ban_person)\
            values(%s, %s) RETURNING id_ban', (id_person, id_ban_person))
            conn.commit()
            returning = cur.fetchone()
        conn.close()
        return returning

    def select_person_id(self, first_name, last_name):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute('select id from people where first_name=%s and last_name=%s', (first_name, last_name))
            conn.commit()
            returning = cur.fetchone()
        conn.close()
        return returning

    def delete_person_out_like_list(self, id_person, id_like_person):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute('delete from like_list\
            where id_person = %s and id_like_person = %s', (id_person, id_like_person))
            conn.commit()
        conn.close()

    def delete_person_out_ban_list(self, id_person, id_ban_person):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute(f'delete from ban_list\
            where id_person = %s and id_ban_person = %s', (id_person, id_ban_person))
            conn.commit()
        conn.close()

    def select_like_people(self, id_person):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute(f'select id_like_person from like_list\
                    where id_person = %s', (id_person,))
            # conn.commit()
            returning = cur.fetchall()
        conn.close()
        return returning

    def select_ban_people(self, id_person):
        conn = psycopg2.connect(database=self.data_base_name, user=self.login, password=self.password,
                                host=self.host, port=self.port)
        with conn.cursor() as cur:
            cur.execute(f'select id_ban_person from ban_list\
                    where id_person = %s', (id_person,))
            # conn.commit()
            returning = cur.fetchall()
        conn.close()
        return returning


