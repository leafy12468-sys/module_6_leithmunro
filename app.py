from flask import Flask, render_template, request
import sqlite3
import os

from database_ import create_db
from data_loader import load_csv_to_db


app = Flask(__name__)


if __name__ == '__main__':
    app.run(debug=True)