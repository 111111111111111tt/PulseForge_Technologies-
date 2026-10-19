from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "organization.db"

app = Flask(__name__)
app.secret_key = "pulseforge-demo-change-before-deployment"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Заполняем каталог только при первом запуске, если он пуст.
        service_count = db.execute("SELECT COUNT(*) FROM services").fetchone()[0]
        if service_count == 0:
            db.executemany(
                "INSERT INTO services (name, description, price) VALUES (?, ?, ?)",
                [
                    ("Веб-разработка", "Создание современных сайтов и веб-приложений для бизнеса.", "От 300 €"),
                    ("Автоматизация процессов", "Упрощение повторяющихся задач и рабочих процессов.", "От 200 €"),
                    ("Базы данных", "Проектирование структуры и организация хранения данных.", "От 150 €"),
                ],
            )


@app.route("/")
def index():
    with get_db() as db:
        services = db.execute("SELECT * FROM services ORDER BY id").fetchall()
    return render_template("index.html", services=services)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Заполните все поля формы.", "error")
            return redirect(url_for("contact"))

        if len(name) > 100 or len(email) > 150 or len(message) > 2000:
            flash("Проверьте длину введённых данных.", "error")
            return redirect(url_for("contact"))

        # Параметризованный запрос помогает защититься от SQL-инъекций.
        with get_db() as db:
            db.execute(
                "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                (name, email, message),
            )

        flash("Сообщение успешно сохранено. Спасибо за обращение!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/admin")
def admin():
    # Учебная демонстрационная страница без авторизации.
    # Не публикуйте сайт в интернете с таким маршрутом.
    with get_db() as db:
        messages = db.execute(
            "SELECT * FROM messages ORDER BY created_at DESC"
        ).fetchall()
    return render_template("admin.html", messages=messages)


init_db()

if __name__ == "__main__":
    # debug=True допустим только для локальной учебной разработки.
    app.run(debug=True)
