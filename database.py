import sqlite3

def init_db():
    conn = sqlite3.connect('coachingms.db')
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS users(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL,
              password TEXT NOT NULL
              )
              ''')
    c.execute("INSERT INTO users(username, password) VALUES(?, ?)",('anushka','tungtungsahur'))
    conn.commit()
    conn.close()

if __name__ == "__main__":
        init_db()
        print("Database created and user added!")
