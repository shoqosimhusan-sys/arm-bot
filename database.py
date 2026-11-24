import sqlite3
import os
from config import DATABASE_NAME

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), DATABASE_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Kurslar jadvali (1, 2, 3, 4-kurs va boshqalar)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL
    );
    """)

    # 2. Kategoriyalar / Bo'limlar jadvali (Badiiy, Ilmiy, Chet tili va h.k.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL -- 'course' (kurs darsligi) yoki 'library' (umumiy kutubxona)
    );
    """)

    # 3. Kitoblar jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        course_id INTEGER,          -- 1, 2, 3, 4 yoki NULL
        category_id INTEGER,        -- Fan yoki kategoriya
        file_id TEXT NOT NULL,      -- Telegram file_id (tezkor yuklash uchun)
        file_name TEXT,
        description TEXT,
        downloads_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (course_id) REFERENCES courses (id),
        FOREIGN KEY (category_id) REFERENCES categories (id)
    );
    """)

    # 4. Foydalanuvchilar jadvali
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Kitob so'rovlari (Talabalar buyurtmalari)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS book_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        request_text TEXT NOT NULL,
        status TEXT DEFAULT 'kutilmoqda', -- kutilmoqda, topildi, topilmadi
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Boshlang'ich kurslarni kiritish
    default_courses = [
        ("1-kurs", "kurs_1"),
        ("2-kurs", "kurs_2"),
        ("3-kurs", "kurs_3"),
        ("4-kurs", "kurs_4"),
        ("Magistratura", "magistratura")
    ]
    for name, code in default_courses:
        cursor.execute("INSERT OR IGNORE INTO courses (name, code) VALUES (?, ?)", (name, code))

    # Boshlang'ich umumiy kutubxona bo'limlari
    default_categories = [
        ("📖 Badiiy adabiyotlar", "library"),
        ("🔬 Ilmiy maqolalar va monografiyalar", "library"),
        ("🇬🇧 Chet tillari va lug'atlar", "library"),
        ("💻 Axborot texnologiyalari va dasturlash", "library")
    ]
    cursor.execute("SELECT COUNT(*) as cnt FROM categories WHERE type = 'library'")
    if cursor.fetchone()["cnt"] == 0:
        for name, c_type in default_categories:
            cursor.execute("INSERT INTO categories (name, type) VALUES (?, ?)", (name, c_type))

    conn.commit()
    conn.close()

# Foydalanuvchini ro'yxatga olish
def add_user(user_id, full_name, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO users (user_id, full_name, username) 
    VALUES (?, ?, ?)
    """, (user_id, full_name, username))
    conn.commit()
    conn.close()

# Kurslar ro'yxatini olish
def get_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Muayyan kurs bo'yicha kitoblarni olish
def get_books_by_course(course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM books 
    WHERE course_id = ? 
    ORDER BY id DESC
    """, (course_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Umumiy kutubxona kategoriyalarini olish
def get_library_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE type = 'library' ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Kategoriya bo'yicha kitoblarni olish
def get_books_by_category(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM books 
    WHERE category_id = ? 
    ORDER BY id DESC
    """, (category_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Kitobni ID bo'yicha olish
def get_book_by_id(book_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE books SET downloads_count = downloads_count + 1 WHERE id = ?", (book_id,))
        conn.commit()
    conn.close()
    return row

# Qidiruv
def search_books(query):
    conn = get_connection()
    cursor = conn.cursor()
    like_query = f"%{query}%"
    cursor.execute("""
    SELECT * FROM books 
    WHERE title LIKE ? OR author LIKE ? 
    ORDER BY id DESC LIMIT 20
    """, (like_query, like_query))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Yangi kitob qo'shish
def add_book(title, author, course_id, category_id, file_id, file_name, description=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO books (title, author, course_id, category_id, file_id, file_name, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, author, course_id, category_id, file_id, file_name, description))
    conn.commit()
    conn.close()

# Kitob o'chirish
def delete_book(book_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

# Kitob so'rovi qoldirish
def add_book_request(user_id, request_text):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO book_requests (user_id, request_text) VALUES (?, ?)", (user_id, request_text))
    conn.commit()
    conn.close()

# Statistika olish
def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as users_count FROM users")
    users_count = cursor.fetchone()["users_count"]
    cursor.execute("SELECT COUNT(*) as books_count FROM books")
    books_count = cursor.fetchone()["books_count"]
    cursor.execute("SELECT SUM(downloads_count) as total_downloads FROM books")
    total_downloads = cursor.fetchone()["total_downloads"] or 0
    cursor.execute("SELECT COUNT(*) as req_count FROM book_requests")
    req_count = cursor.fetchone()["req_count"]
    conn.close()
    return {
        "users": users_count,
        "books": books_count,
        "downloads": total_downloads,
        "requests": req_count
    }

if __name__ == "__main__":
    init_db()
    print("Ma'lumotlar bazasi muvaffaqiyatli yaratildi va sozlandi!")
