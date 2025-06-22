import json
import logging
import sqlite3
from datetime import datetime


class BotDB:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscription (
                user_id UNIQUE ON CONFLICT REPLACE,
                status,
                date,
                sisyphus_date
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS todo (
                user_id UNIQUE ON CONFLICT REPLACE,
                tasks DEFAULT ""
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS up (
                user_id UNIQUE ON CONFLICT REPLACE,
                subscription DEFAULT (0),
                survey,
                inputed_partner,
                date
            );
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER UNIQUE ON CONFLICT REPLACE,
                username TEXT DEFAULT NULL,
                first_name TEXT DEFAULT NULL,
                birth_day TEXT DEFAULT NULL,
                birth_place TEXT DEFAULT NULL,
                birth_time TEXT DEFAULT NULL,
                personality_type,
                today_task,
                task_date,
                energy TEXT DEFAULT NULL,
                motivation,
                dream,
                about TEXT,
                status INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NULL,
                thread
            );
        ''')

        self.connection.commit()

    def add_user(self, user_id, username, first_name):
        self.cursor.execute('''
            INSERT INTO users (user_id, username, first_name, created_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, datetime.now().strftime('%Y-%m-%d %H:%M')))
        self.connection.commit()





    def get_all_user_ids(self):
        self.cursor.execute('SELECT user_id FROM users')
        rows = self.cursor.fetchall()
        user_ids = [row[0] for row in rows]
        return user_ids

    def get_all_users(self):
        # Получает всех пользователей и их дату окончания подписки
        self.cursor.execute("SELECT user_id FROM users")
        return self.cursor.fetchall()

    def get_birth_day(self, user_id):
        self.cursor.execute('SELECT birth_day FROM users WHERE user_id = ?', (user_id,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        return None

    def update_user_details(self, user_id, birth_day, birth_place, birth_time):
        self.cursor.execute(
            "UPDATE users SET birth_day = ?, birth_place = ?, birth_time = ? WHERE user_id = ?",
            (birth_day, birth_place, birth_time, user_id)
        )
        return self.connection.commit()

    def get_user_details(self, user_id):
        self.cursor.execute('SELECT birth_day, birth_place, birth_time FROM users WHERE user_id = ?', (user_id,))
        row = self.cursor.fetchone()
        if row:
            if row[0]:
                return {
                    "date": row[0],  # Assuming the format is YYYY-MM-DD
                    "place": row[1],
                    "formatted_time": row[2],
                }
        return None

    def get_user_id_by_username(self, username):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()

        # Если пользователь найден, возвращаем его ID, иначе None
        if result:
            return result[0]  # user_id
        return None

    def get_partner_details(self, user_id):
        self.cursor.execute(
            'SELECT partner_date, partner_place, partner_birth_time, type_relation FROM partners WHERE user_id = ?',
            (user_id,))
        row = self.cursor.fetchone()
        if row:
            if row[3]:
                return {
                    "date": row[0],  # Assuming the format is YYYY-MM-DD
                    "place": row[1],
                    "time": row[2],
                    "type_relation": row[3]
                }
        else:
            return None

    def update_partner_details(self, user_id, partner_date, partner_place, partner_birth_time):
        self.cursor.execute(
            "UPDATE partners SET partner_date = ?, partner_place = ?, partner_birth_time = ? WHERE user_id = ?",
            (partner_date, partner_place, partner_birth_time, user_id)
        )
        return self.connection.commit()

    def update_type_relation(self, user_id, type_relation):
        self.cursor.execute(
            "UPDATE partners SET type_relation = ? WHERE user_id = ?",
            (type_relation, user_id)
        )
        return self.connection.commit()

    def insert_type_relation(self, user_id, type_relation):
        self.cursor.execute('''
            INSERT INTO partners (user_id, type_relation)
            VALUES (?, ?)
        ''', (user_id, type_relation))
        self.connection.commit()

    def update_personality_type(self, user_id, personality_type):
        self.cursor.execute(
            "UPDATE users SET personality_type = ? WHERE user_id = ?",
            (personality_type, user_id)
        )
        return self.connection.commit()

    def get_personality_type(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT personality_type FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def update_partner_personality_type(self, user_id, personality_type):
        self.cursor.execute(
            "UPDATE partners SET personality_type = ? WHERE user_id = ?",
            (personality_type, user_id)
        )
        return self.connection.commit()

    def insert_partner_personality(self, user_id, personality_type):
        self.cursor.execute('''
            INSERT INTO partners (user_id, personality_type)
            VALUES (?, ?)
        ''', (user_id, personality_type))
        self.connection.commit()

    def get_partner_personality_type(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT personality_type FROM partners WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def update_thread(self, user_id, thread):
        self.cursor.execute(
            "UPDATE users SET thread = ? WHERE user_id = ?",
            (thread, user_id)
        )
        return self.connection.commit()

    def insert_thread(self, user_id, thread):
        self.cursor.execute('''
            INSERT INTO users (user_id, thread)
            VALUES (?, ?)
        ''', (user_id, thread))
        self.connection.commit()

    def get_thread(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT thread FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def insert_status(self, user_id):
        self.cursor.execute('''
            INSERT INTO subscription (user_id)
            VALUES (?)
        ''', (user_id,))
        self.connection.commit()

    def status_active(self, user_id):
        self.cursor.execute(
            "UPDATE subscription SET status = 1 WHERE user_id = ?",
            (user_id,)
        )
        return self.connection.commit()

    def status_inactive(self, user_id):
        self.cursor.execute(
            "UPDATE subscription SET status = 0 WHERE user_id = ?",
            (user_id,)
        )
        return self.connection.commit()

    def get_subscription(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT status FROM subscription WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def sisyphus_active(self, user_id):
        # Получаем текущую дату в формате дд мм гггг
        current_date = datetime.now().strftime("%d-%m-%Y")

        # Выполняем SQL-запрос для обновления столбца sisyphus
        self.cursor.execute(
            "UPDATE subscription SET sisyphus_date = ? WHERE user_id = ?",
            (current_date, user_id)
        )

        # Сохраняем изменения в базе данных
        self.connection.commit()

    def get_sisyphus_date(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT sisyphus_date FROM subscription WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def get_tasks(self, user_id):
        # Пример SQL-запроса для получения задач по user_id
        self.cursor.execute("SELECT tasks FROM todo WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result and result[0]:
            try:
                # Пробуем загрузить данные как JSON
                return json.loads(result[0])
            except json.JSONDecodeError:
                # Если данные не JSON, возвращаем пустой список
                logging.error(f"Некорректный JSON для пользователя {user_id}: {result[0]}")
                return []
        else:
            return []

    def update_tasks(self, user_id, tasks):
        # Преобразуем список задач в строку JSON
        tasks_json = json.dumps(tasks, ensure_ascii=False)
        # Сохраняем в базу данных
        self.cursor.execute(
            "UPDATE todo SET tasks = ? WHERE user_id = ?",
            (tasks_json, user_id)
        )
        self.connection.commit()

    def update_survey(self, user_id, survey):
        print(f"DEBUG: Updating survey for user_id={user_id}")
        self.cursor.execute(
            "SELECT * FROM up WHERE user_id = ?",
            (user_id,)
        )
        if not self.cursor.fetchone():
            print(f"DEBUG: No entry found, creating new one for user_id={user_id}")
            self.cursor.execute(
                "INSERT INTO up (user_id, survey) VALUES (?, ?)",
                (user_id, survey)
            )
        else:
            print(f"DEBUG: Entry found, updating for user_id={user_id}")
            self.cursor.execute(
                "UPDATE up SET survey = ? WHERE user_id = ?",
                (survey, user_id)
            )
        self.connection.commit()

    def get_survey(self, user_id):
        self.cursor.execute("SELECT survey FROM up WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def update_partner_id(self, user_id, partner_id):
        self.cursor.execute(
            "UPDATE users SET partner_id = ? WHERE user_id = ?",
            (partner_id, user_id)
        )
        return self.connection.commit()

    def get_partner_id(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT partner_id FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def get_ids(self):
        result = self.cursor.execute("SELECT user_id FROM users")
        result = [str(item[0]) for item in result.fetchall()]
        return result

    def up_active(self, user_id):
        # Получаем текущую дату в формате дд мм гггг
        current_date = datetime.now().strftime("%d-%m-%Y")

        # Выполняем SQL-запрос для обновления столбца sisyphus
        self.cursor.execute(
            "UPDATE up SET subscription = ? WHERE user_id = ?",
            (current_date, user_id)
        )

        # Сохраняем изменения в базе данных
        self.connection.commit()

    def update_partner_info_up(self, user_id, inputed_partner):
        self.cursor.execute(
            "UPDATE up SET inputed_partner = ? WHERE user_id = ?",
            (inputed_partner, user_id)
        )
        return self.connection.commit()

    def get_partner_info_up(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT inputed_partner FROM up WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def get_info_up(self, user_id):
        # Пример SQL-запроса для получения данных о партнере из таблицы users
        self.cursor.execute("""
            SELECT first_name, birth_day, birth_place, birth_time, personality_type
            FROM users
            WHERE user_id = ?
        """, (user_id,))
        result = self.cursor.fetchone()

        if result:
            first_name, birth_day, birth_place, birth_time, personal = result
            return {
                "name": first_name,
                "birth_date": birth_day,
                "birth_place": birth_place,
                "birth_time": birth_time,
                "personality_type": personal
            }

        else:
            return None

    def up_date(self, user_id):
        # Получаем текущую дату в формате дд мм гггг
        current_date = datetime.now().strftime("%d-%m-%Y")

        # Выполняем SQL-запрос для обновления столбца sisyphus
        self.cursor.execute(
            "UPDATE up SET date = ? WHERE user_id = ?",
            (current_date, user_id)
        )

        # Сохраняем изменения в базе данных
        self.connection.commit()

    def get_up_date(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT date FROM up WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def add_todo(self, user_id):
        self.cursor.execute('''
            INSERT INTO todo (user_id)
            VALUES (?)
        ''', (user_id,))
        self.connection.commit()

    def get_todolist(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT tasks FROM todo WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def update_energy(self, user_id, energy):
        self.cursor.execute(
            "UPDATE users SET energy = ? WHERE user_id = ?",
            (energy, user_id)
        )
        return self.connection.commit()

    def update_about(self, user_id, about):
        self.cursor.execute(
            "UPDATE users SET about = ? WHERE user_id = ?",
            (about, user_id)
        )
        return self.connection.commit()

    def get_all_about(self, user_id):
        self.cursor.execute(
            'SELECT birth_day, birth_place, birth_time, personality_type, about FROM users WHERE user_id = ?',
            (user_id,))
        row = self.cursor.fetchone()

        if row:
            birth_date = row[0] if row[0] else "Не указано"
            birth_place = row[1] if row[1] else "Не указано"
            birth_time = row[2] if row[2] else "Не указано"
            personality_type = row[3] if row[3] else "Не определено"
            about = row[4] if row[4] else "Не указано"

            return (
                f"Дата рождения: {birth_date}\n"
                f"Место рождения: {birth_place}\n"
                f"Время рождения: {birth_time}\n"
                f"Тип личности: {personality_type}\n"
                f"О себе: {about}"
            )

        return "Профиль не найден"

    def update_todaytask(self, user_id, today_task):
        self.cursor.execute(
            "UPDATE users SET today_task = ? WHERE user_id = ?",
            (today_task, user_id)
        )
        return self.connection.commit()

    def update_taskdate(self, user_id):
        self.cursor.execute(
            "UPDATE users SET task_date = ? WHERE user_id = ?",
            (datetime.now().strftime('%Y-%m-%d')
, user_id)
        )
        return self.connection.commit()

    def get_dream(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT dream FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def update_dream(self, user_id, dream):
        self.cursor.execute(
            "UPDATE users SET dream = ? WHERE user_id = ?",
            (dream, user_id)
        )
        return self.connection.commit()

    def get_motivation(self, user_id):
        # Пример SQL-запроса для получения user_id по username
        self.cursor.execute("SELECT motivation FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    def update_motivation(self, user_id, motivation):
        self.cursor.execute(
            "UPDATE users SET motivation = ? WHERE user_id = ?",
            (motivation, user_id)
        )
        return self.connection.commit()