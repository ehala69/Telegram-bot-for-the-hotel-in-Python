import sqlite3

def create_new_database():
    conn = sqlite3.connect('abonements.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS abonements (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            username TEXT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            abonement TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('waiting', 'not_active', 'active', 'past')),
            start_date TEXT,        -- Дата начала (YYYY-MM-DD)
            end_date TEXT,          -- Дата окончания (YYYY-MM-DD)
            notification_date TEXT  -- Дата отправки уведомления (YYYY-MM-DD)
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_notification_date 
        ON abonements (notification_date)
    ''')

    conn.commit()
    conn.close()
    print("База данных успешно создана!")


if __name__ == "__main__":
    create_new_database()