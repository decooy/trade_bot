import psycopg2
import psycopg2.extras


class database:
    def __init__(self):
        self.sqlite_connection = psycopg2.connect(dbname='postgres', user='postgres', password='1q2w3e123qwe',
                                                  host='localhost', port='5432')
        self.cursor = self.sqlite_connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                  id BIGINT,
                  deposit INT default 0 not null,
                  risk decimal(8,2) default 0 not null,
                  subscription BOOL
                  );
               """)
        self.sqlite_connection.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS signals(
                          id SERIAL,
                          token TEXT,
                          shortlong TEXT,
                          entry_min decimal(8,2) default 0 not null,
                          entry_max decimal(8,2) default 0 not null,
                          goal decimal(8,2) default 0 not null,
                          stop decimal(8,2) default 0 not null,
                          percentstop decimal(8,2) default 0 not null
                          );
                       """)
        self.sqlite_connection.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS admins(
                                  id BIGINT);
                               """)
        self.sqlite_connection.commit()

    def check_user(self, id):
        command = f"""SELECT * FROM users WHERE id={id}"""
        self.cursor.execute(command)
        res = self.cursor.fetchall()
        return res

    def register_user(self, id, deposit, risk):
        command = f"""INSERT INTO users(id, deposit, risk, subscription) VALUES(
        {id},
        {deposit},
        {risk},
        {True})"""
        self.cursor.execute(command)
        self.sqlite_connection.commit()

    def get_deposit(self, id):
        command = f"""SELECT deposit FROM users WHERE id={id}"""
        self.cursor.execute(command)
        result = self.cursor.fetchone()
        return result[0]

    def change_deposit(self, id, deposit):
        command = f"""UPDATE users SET deposit={deposit} WHERE id={id}"""
        self.cursor.execute(command)
        self.sqlite_connection.commit()

    def get_risk(self, id):
        command = f"""SELECT risk FROM users WHERE id={id}"""
        self.cursor.execute(command)
        result = self.cursor.fetchone()
        return result[0]

    def change_risk(self, id, risk):
        command = f"""UPDATE users SET risk={risk} WHERE id={id}"""
        self.cursor.execute(command)
        self.sqlite_connection.commit()

    def unsubscribe(self, id):
        command = f"""UPDATE users SET subscription=FALSE WHERE id={id}"""
        self.cursor.execute(command)
        self.sqlite_connection.commit()

    def get_sub(self, id):
        command = f"""SELECT subscription FROM users WHERE id={id}"""
        self.cursor.execute(command)
        return self.cursor.fetchone()[0]

    def subscribe(self, id):
        command = f"""UPDATE users SET subscription=TRUE WHERE id={id}"""
        self.cursor.execute(command)
        self.sqlite_connection.commit()

    def isadmin(self, id):
        command = f"""SELECT id FROM admins WHERE id={id}"""
        self.cursor.execute(command)
        if self.cursor.fetchone() is None:
            return False
        else:
            return True

    def get_users(self):
        command = f"""SELECT * FROM users WHERE subscription=TRUE"""
        self.cursor.execute(command)
        return self.cursor.fetchall()