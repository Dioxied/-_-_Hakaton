import sqlite3
from datetime import datetime

DB_NAME = "database.db"


def StartDatabase():
    with sqlite3.connect(DB_NAME) as conn:
        # Таблица пользователей
        conn.execute('''CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            first_name TEXT,
            last_name TEXT,
            telegram_id TEXT,
            telegram_chat_id TEXT,
            preferences TEXT
        )''')

        # Таблица проектов
        conn.execute('''CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            type TEXT CHECK (type IN ('startup', 'equipment_request', 'investment', 'RnD', 'other')),
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            owner_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES Users(id)
        )''')

        # Чаты
        conn.execute('''CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            title TEXT,
            chat_type TEXT CHECK (chat_type IN ('text', 'voice', 'vcs')),
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )''')

        # Участники чатов
        conn.execute('''CREATE TABLE IF NOT EXISTS chat_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            role TEXT,
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )''')

        # Сообщения
        conn.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            sender_id INTEGER,
            content TEXT,
            markdown_enabled BOOLEAN DEFAULT FALSE,
            voice_note_url TEXT,
            file_url TEXT,
            message_type TEXT DEFAULT 'text',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES Users(id)
        )''')

        # Уведомления (универсальные)
        conn.execute('''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT CHECK (type IN ('message', 'event', 'comment', 'approval')),
            content TEXT,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            related_type TEXT,
            related_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )''')

        # Теги к чатам
        conn.execute('''CREATE TABLE IF NOT EXISTS chat_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            tag TEXT,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        )''')

        # Интеграции
        conn.execute('''CREATE TABLE IF NOT EXISTS integrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT CHECK (service IN ('telegram', 'google_calendar', 'email')),
            config TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )''')

        # Файлы
        conn.execute('''CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_name TEXT,
                        stored_name TEXT,
                        mime_type TEXT,
                        size INTEGER,
                        uploader_id INTEGER,
                        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (uploader_id) REFERENCES Users(id)
)
''')

# ======================= Пользователи =======================
def isUserExists(email):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE email = ?)",(email,))
        return bool(cursor.fetchone()[0])

def loginUser(email, password):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (email, password,))
        return cursor.fetchone()


def createUser(email, password, first_name, last_name):
    with sqlite3.connect('database.db') as conn:
        if isUserExists(email):
            return False
        else:
            conn.execute("INSERT INTO Users (email, password, first_name, last_name) VALUES (?,?,?,?)", (email, password, first_name, last_name,))
            return True




def rename_user(email, first_name, last_name):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE Users SET first_name = ?, last_name = ? WHERE email = ?",
            (first_name, last_name, email)
        )
def set_telegram(email, telegram_id, telegram_chat_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE Users SET telegram_id = ?, telegram_chat_id = ? WHERE email = ?",
            (telegram_id, telegram_chat_id, email)
        )
def get_telegram_chat_id_from_email(email):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "SELECT telegram_chat_id FROM Users WHERE email =?",
            (email,)
        )
        return cursor.fetchone()[0] if cursor.fetchone() else None
def set_avatar_for_user(email, id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE Users SET avatar =? WHERE email =?",
            (id, email,)
        )


# ======================= Проекты =======================
def create_project(title, description, type_, status, owner_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            '''INSERT INTO projects (title, description, type, status, created_at, updated_at, owner_id)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)''',
            (title, description, type_, status, owner_id)
        )
def update_project_status(project_id, status):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE projects SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, project_id)
        )
def search_projects_by_title(text):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "SELECT * FROM projects WHERE title LIKE ?",
            ('%' + text + '%',)
        )
        return cursor.fetchall()
# ======================= Чаты =======================

def create_chat(project_id, title, chat_type, status):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            '''INSERT INTO chats (project_id, title, chat_type, status)
               VALUES (?, ?, ?, ?)''',
            (project_id, title, chat_type, status)
        )
def archive_chat(chat_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE chats SET status = 'archived' WHERE id = ?",
            (chat_id,)
        )
def filter_chats(project_id, chat_type):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "SELECT * FROM chats WHERE project_id = ? AND chat_type = ?",
            (project_id, chat_type)
        )
        return cursor.fetchall()
def add_user_to_chat(chat_id, user_id, role):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO chat_participants (chat_id, user_id, role) VALUES (?, ?, ?)",
            (chat_id, user_id, role)
        )


# ======================= Теги чатов =======================
def add_tag_to_chat(chat_id, tag):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO chat_tags (chat_id, tag) VALUES (?, ?)",
            (chat_id, tag)
        )


# ======================= Сообщения =======================
def send_message(chat_id, sender_id, text, markdown=False, voice_url=None, file_url=None, message_type="text"):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            '''INSERT INTO messages
               (chat_id, sender_id, content, markdown_enabled, voice_note_url, file_url, message_type)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (chat_id, sender_id, text, markdown, voice_url, file_url, message_type)
        )
def get_chat_history(chat_id, limit=50):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at DESC LIMIT ?",
            (chat_id, limit)
        )
        return cursor.fetchall()
def delete_message(message_id, sender_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "DELETE FROM messages WHERE id = ? AND sender_id = ?",
            (message_id, sender_id)
        )


# ======================= Уведомления =======================
def create_notification(user_id, message, type_, related_type, related_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            '''INSERT INTO notifications
               (user_id, content, type, related_type, related_id, created_at)
               VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
            (user_id, message, type_, related_type, related_id)
        )
def mark_notification_read(notification_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "UPDATE notifications SET is_read = TRUE WHERE id = ?",
            (notification_id,)
        )
def get_unread_notifications(user_id):

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "SELECT * FROM notifications WHERE user_id = ? AND is_read = FALSE",
            (user_id,)
        )
        return cursor.fetchall()

# ======================= Интеграции =======================
def add_integration(user_id, service_name, config):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            '''INSERT INTO integrations (user_id, service, config, is_active)
               VALUES (?, ?, ?, TRUE)''',
            (user_id, service_name, config)
        )
def get_user_integration(user_id, service_name):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "SELECT config FROM integrations WHERE user_id = ? AND service = ? AND is_active = TRUE",
            (user_id, service_name)
        )
        result = cursor.fetchone()
        return result[0] if result else None

# ======================= Файлы ========================
def add_file_metadata(original_name, stored_name, mime_type, size, uploader_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "INSERT INTO files (original_name, stored_name, mime_type, size, uploader_id, uploader_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (original_name, stored_name, mime_type, size, uploader_id)
        )
def get_file_metadata(file_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute(
            "SELECT id, original_name, stored_name, mime_type, size, uploaded_at FROM files WHERE id = ?",
            (file_id,)
        )
        return cursor.fetchone()

# Инициализация базы при запуске
StartDatabase()
