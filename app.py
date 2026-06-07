from flask import Flask, render_template, request, redirect, url_for, flash

import sqlite3
import os

from database_ import create_db
from data_loader import load_csv_to_db

#   flase database setup
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"

app.secret_key = "secret_key" 

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#   database created
DATABASE = "my_database.db"

with sqlite3.connect(DATABASE) as conn:
    create_db(conn)

#   homepage setup
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

#   uploads files and displays messages
@app.route("/upload", methods=["POST"])
def upload():

    if "csv_file" not in request.files:
        return "No file uploaded"

    file = request.files["csv_file"]

    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("home"))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    if os.path.exists(filepath):
        flash(f"File '{file.filename}' already exists.", "error")
        return redirect(url_for("home"))

    file.save(filepath)

    try:
        conn = sqlite3.connect(DATABASE)
        create_db(conn)
        load_csv_to_db(conn, filepath)
        conn.close()
        flash(f"File '{file.filename}' uploaded successfully!", "success")
        return redirect(url_for("home"))

    except Exception as e:
            return redirect(url_for("home"))
    
#   file details page setup
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

#   file delete option setup
@app.route('/delete/file/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    with sqlite3.connect(DATABASE) as conn:

        conn.execute("DELETE FROM file_table WHERE file_id = ?", (file_id,))
        conn.execute("DELETE FROM file_uploadtable WHERE file_id = ?", (file_id,))
        return render_template("page.html")
    
@app.route("/error_logs")
def errorlogs():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    errors = conn.execute(
        """SELECT filename, error_message, import_time 
           FROM import_log 
           WHERE status = 'INVALID'
           ORDER BY filename"""
    ).fetchall()
    conn.close()
    return render_template("errors.html", errors=errors)

if __name__ == '__main__':
    app.run(debug=True)