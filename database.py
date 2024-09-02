import sqlite3

class Database:
    def __init__(self):
        self.db = sqlite3.connect('database.db')
        self.cursor = self.db.cursor()

    def clothes_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS clothes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(221),
                price INT
            )
        """)
        self.db.commit()

    def footwear_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS footwear (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(221),
                price INT
            )
        """)
        self.db.commit()

    def add_data_to_clothes(self, name, price):
        name = name.lower().strip()  
        self.cursor.execute("""
            INSERT INTO clothes(name, price)
            VALUES (?, ?)
        """, (name, price))
        self.db.commit()
    
    def add_data_to_footwear(self, name, price):
        name = name.lower().strip() 
        self.cursor.execute("""
            INSERT INTO footwear(name, price)
            VALUES (?, ?)
        """, (name, price))
        self.db.commit()


    def users_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY,
                full_name VARCHAR(221)
            )
        """)
        self.db.commit()

    def add_data(self, user_id, user_full_name):
        self.cursor.execute("""
            INSERT OR IGNORE INTO users(id, full_name)
            VALUES (?, ?)
        """, (user_id, user_full_name))
        self.db.commit()

    def all_data_clothes(self):
        self.cursor.execute("""
            SELECT * FROM clothes
        """)
        return self.cursor.fetchall()

    def all_data_footwear(self):
        self.cursor.execute("""
            SELECT * FROM footwear
        """)
        return self.cursor.fetchall()

    def update_clothes(self, old_name, new_name, new_price):
        self.cursor.execute("""
            UPDATE clothes
            SET name = ?, price = ?
            WHERE name = ?
        """, (new_name, new_price, old_name))
        self.db.commit()

    def update_footwear(self, old_name, new_name, new_price):
        self.cursor.execute("""
            UPDATE footwear
            SET name = ?, price = ?
            WHERE name = ?
        """, (new_name, new_price, old_name))
        self.db.commit()

    def delete_clothes(self, name):
        self.cursor.execute("""
            DELETE FROM clothes
            WHERE name = ?
        """, (name,))
        self.db.commit()

    def delete_footwear(self, name):
        self.cursor.execute("""
            DELETE FROM footwear
            WHERE name = ?
        """, (name,))
        self.db.commit()

    def all_data_users(self):
        self.cursor.execute("""
            SELECT * FROM users
        """)
        return self.cursor.fetchall()

    def get_user_data(self, user_id):
        self.cursor.execute("""
            SELECT id, full_name FROM users WHERE id = ?
        """, (user_id,))
        return self.cursor.fetchone()

    def close(self):
        self.db.close()
