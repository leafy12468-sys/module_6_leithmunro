import sqlite3
import pandas as pd
from database_ import create_db
from datetime import datetime

def load_csv_to_db(conn, csv_path='csv.csv'):
    cursor = conn.cursor()

    base_filename = csv_path
    filename = base_filename

#   generates errors for invalid file
    try:
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()

        csv_time = str(df.iloc[0]['timestamp'])
        csv_time = csv_time.replace(":", "")

        date_part = datetime.now().strftime("%Y%m%d")

        filename = f"MED_DATA{date_part}{csv_time}.csv"
    except Exception as e:
        filename = f"invalid_file({csv_path})"
        cursor.execute("""
            INSERT INTO import_log (filename, status, error_message)
            VALUES (?, ?, ?)
        """, (filename, "INVALID", str(e)))
        conn.commit()
        raise

    cursor.execute("SELECT file_id FROM file_uploadtable WHERE filename = ?", (filename,))
    if cursor.fetchone():
        raise ValueError(f"File '{filename}' has already been uploaded")
    cursor.execute("INSERT INTO file_uploadtable (filename) VALUES (?)", (filename,))
    conn.commit()
    file_id = cursor.lastrowid

    try:
        for _, row in df.iterrows():
            # Seperate timestamp into parts
            time_parts = str(row['timestamp']).split(':')
            hour, minute, second = int(time_parts[0]), int(time_parts[1]), int(time_parts[2])

            # Insert into timestamp_table
            cursor.execute("""
                INSERT INTO timestamp_table (second, minute, hour)
                VALUES (?, ?, ?)
            """, (second, minute, hour))
            timestamp_id = cursor.lastrowid

            # Insert into batch_id_table 
            cursor.execute("""
                INSERT OR IGNORE INTO batch_id_table (batch_id_value)
                VALUES (?)
            """, (int(row['batch_id']),))
            cursor.execute("SELECT batch_id FROM batch_id_table WHERE batch_id_value = ?", (int(row['batch_id']),))
            batch_id = cursor.fetchone()[0]

        # Insert each reading and link in file_table
            cursor.execute("""
                INSERT INTO readings (
                    reading1, reading2, reading3, reading4, reading5,
                    reading6, reading7, reading8, reading9, reading10
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['reading1'],
                row['reading2'],
                row['reading3'],
                row['reading4'],
                row['reading5'],
                row['reading6'],
                row['reading7'],
                row['reading8'],
                row['reading9'],
                row['reading10']
            ))

            reading_id = cursor.lastrowid

            cursor.execute("""
            INSERT INTO file_table (
                file_id, batch_id, reading_id, timestamp_id
            )
            VALUES (?, ?, ?, ?)
            """, (file_id, batch_id, reading_id, timestamp_id))

            conn.commit()

        cursor.execute("""
            INSERT INTO import_log
            (filename, status)
            VALUES (?, ?)
        """, (filename, "VALID"))

        conn.commit()

    except Exception as e:

        cursor.execute("""
            INSERT INTO import_log
            (filename, status, error_message)
            VALUES (?, ?, ?)
        """, (filename, "INVALID", str(e)))

        conn.commit()

        raise

if __name__ == "__main__":
    conn = sqlite3.connect('my_database.db')
    create_db(conn)
    load_csv_to_db(conn)
    conn.close()