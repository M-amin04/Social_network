import sqlite3

DB_NAME = 'social_network.db'

def connect():
    return sqlite3.connect(DB_NAME)


def create_tabel():
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            birthdate TEXT,
            gender TEXT,
            city TEXT
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            content TEXT,
            date TEXT
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            content TEXT,
            date TEXT
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1 TEXT,
            user2 TEXT
        )
        ''')
        conn.commit()
        
        
def add_user(data):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
        INSERT INTO users (username, password, first_name, last_name, birthdate, gender, city)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['Username'],
            data['Password'],
            data['Name'],
            data['Lastname'],
            data['Birthdate'],
            data['Gender'],
            data['City'],
        ))
        conn.commit()
        
        
def user_exists(username):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        return c.fetchone() is not None
    

def get_user(username):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = c.fetchone()
        if row:
            return {
                'username': row[0],
                'password': row[1],
                'first_name': row[2],
                'last_name': row[3],
                'birthdate': row[4],
                'gender': row[5],
                'city': row[6]
            }
        return None
    
    
def update_user(old_username, data):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            UPDATE users
            SET username = ?, first_name = ?, last_name = ?, birthdate = ?, gender = ?, city = ?
            WHERE username = ?
        ''', (
            data['username'],
            data['first_name'],
            data['last_name'],
            data['birthdate'],
            data['gender'],
            data['city'],
            old_username
        ))
        conn.commit()

    
def get_all_users():
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT username, password, first_name, last_name, birthdate, gender, city FROM users')
        return c.fetchall()


def add_post(username, content, date):
    with connect() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO posts (username, content, date) VALUES (?, ?, ?)', (username, content, date))
        conn.commit()


def get_posts_by_user(username):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT content, date FROM posts WHERE username = ? ORDER BY date DESC', (username,))
        return c.fetchall()
    
    
def get_friends(username):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT user2 FROM friends WHERE user1 = ?
            UNION
            SELECT user1 FROM friends WHERE user2 = ?
        ''', (username, username))
        return [row[0] for row in c.fetchall()]


def get_posts_by_users(username):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT content, date FROM posts WHERE username = ?', (username, ))
        return c.fetchall()


def send_friend_request(sender, receiver):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            SELECT 1 FROM friend_requests WHERE sender = ? AND receiver = ?
        ''', (sender, receiver))
        if c.fetchone():
            return False  

        c.execute('''
            SELECT 1 FROM friends WHERE (user1 = ? AND user2 = ?) OR (user1 = ? AND user2 = ?)
        ''', (sender, receiver, receiver, sender))
        if c.fetchone():
            return False  

        c.execute('INSERT INTO friend_requests (sender, receiver) VALUES (?, ?)', (sender, receiver))
        conn.commit()
        return True


def get_incoming_requests(username):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT sender FROM friend_requests WHERE receiver = ?', (username,))
        return [row[0] for row in c.fetchall()]


def accept_friend_request(sender, receiver):
    with connect() as conn:
        c = conn.cursor()
        c.execute('INSERT INTO friends (user1, user2) VALUES (?, ?)', (sender, receiver))

        c.execute('DELETE FROM friend_requests WHERE sender = ? AND receiver = ?', (sender, receiver))
        conn.commit()


def reject_friend_request(sender, receiver):
    with connect() as conn:
        c = conn.cursor()
        c.execute('DELETE FROM friend_requests WHERE sender = ? AND receiver = ?', (sender, receiver))
        conn.commit()


def send_message(sender, receiver, content, date):
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO messages (sender, receiver, content, date)
            VALUES (?, ?, ?, ?)
        ''', (sender, receiver, content, date))
        conn.commit()

    
def get_all_messages():
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT sender, receiver, content, date FROM messages ORDER BY date DESC')
        return c.fetchall()
    
    
def get_messages_with_friends(username, friends):
    if not friends:
        return []
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT sender, receiver, content, date FROM messages')
        rows = c.fetchall()
        messages = []
        for sender, receiver, content, date in rows:
            if (sender == username and receiver in friends) or (receiver == username and sender in friends):
                messages.append({
                    'sender': sender,
                    'receiver': receiver,
                    'content': content,
                    'date': date
                })
        messages.sort(key=lambda m: m['date'], reverse=True)
    return messages

    
def get_all_posts():
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT username, content, date FROM posts ORDER BY date DESC')
        return c.fetchall()


def get_all_usernames_except(username):
    with connect() as conn:
        c = conn.cursor()
        c.execute('SELECT username FROM users WHERE username != ?', (username,))
        return [row[0] for row in c.fetchall()]