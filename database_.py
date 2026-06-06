import sqlite3

def create_db(conn):
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timestamp_table (
        time_id INTEGER PRIMARY KEY AUTOINCREMENT,
        second INTEGER CHECK(second BETWEEN 0 AND 59),
        minute INTEGER CHECK(minute BETWEEN 0 AND 59),
        hour INTEGER CHECK(hour BETWEEN 0 AND 23)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batch_id_table (
        batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id_value INTEGER UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS readings (
        reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reading1 REAL,
        reading2 REAL,
        reading3 REAL,
        reading4 REAL,
        reading5 REAL,
        reading6 REAL,
        reading7 REAL,
        reading8 REAL,
        reading9 REAL,
        reading10 REAL
    )
    """)

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS file_uploadtable (
        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS file_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER,
        batch_id INTEGER,
        reading_id INTEGER,
        timestamp_id INTEGER,
        FOREIGN KEY (file_id) REFERENCES file_uploadtable(file_id),
        FOREIGN KEY (batch_id) REFERENCES batch_id_table(batch_id),
        FOREIGN KEY (reading_id) REFERENCES readings(reading_id),
        FOREIGN KEY (timestamp_id) REFERENCES timestamp_table(time_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS import_log (
        import_id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        status TEXT,
        error_message TEXT,
        import_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()