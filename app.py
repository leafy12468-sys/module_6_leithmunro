from flask import Flask, render_template, request, redirect, url_for

import sqlite3
import os

from database_ import create_db
from data_loader import load_csv_to_db


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = "my_database.db"

with sqlite3.connect(DATABASE) as conn:
    create_db(conn)

@app.route("/")
def home():
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT DISTINCT f.file_id, fu.filename
            FROM file_table f
            JOIN file_uploadtable fu ON f.file_id = fu.file_id
        """).fetchall()
        invalid = conn.execute("""
            SELECT filename, error_message, import_time 
            FROM import_log 
            WHERE status = 'INVALID'
        """).fetchall()
    return render_template("page.html", rows=rows, invalid=invalid)

@app.route("/upload", methods=["POST"])
def upload():

    if "csv_file" not in request.files:
        return "No file uploaded"

    file = request.files["csv_file"]

    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        conn = sqlite3.connect(DATABASE)

        create_db(conn)

        load_csv_to_db(conn, filepath)

        conn.close()
        
        return redirect(url_for("home"))

    except Exception as e:
            return redirect(url_for("home"))

@app.route("/file/<int:file_id>")
def file_detail(file_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT 
                f.file_id,
                b.batch_id_value,
                r.reading1, r.reading2, r.reading3, r.reading4, r.reading5,
                r.reading6, r.reading7, r.reading8, r.reading9, r.reading10,
                t.hour, t.minute, t.second
            FROM file_table f
            JOIN batch_id_table b ON f.batch_id = b.batch_id
            JOIN readings r ON f.reading_id = r.reading_id
            JOIN timestamp_table t ON f.timestamp_id = t.time_id
            WHERE f.file_id = ?
        """, (file_id,)).fetchall()

    if not rows:
        return "File not found", 404

    return render_template("file_detail.html", rows=rows, file_id=file_id)
if __name__ == '__main__':
    app.run(debug=True)