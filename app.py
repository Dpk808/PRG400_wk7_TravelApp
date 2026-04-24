from __future__ import annotations

import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "travel.db"),
    )

    os.makedirs(app.instance_path, exist_ok=True)

    def get_db() -> sqlite3.Connection:
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(exception: Exception | None) -> None:
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def login_required(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                flash("Please log in to continue.")
                return redirect(url_for("login"))
            return view(**kwargs)

        return wrapped_view

    def admin_required(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None or g.user["role"] != "admin":
                flash("Admin access required.")
                return redirect(url_for("destinations"))
            return view(**kwargs)

        return wrapped_view

    @app.before_request
    def load_logged_in_user() -> None:
        user_id = session.get("user_id")
        if user_id is None:
            g.user = None
            return
        db = get_db()
        g.user = db.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()

    @app.route("/")
    def home():
        return redirect(url_for("destinations"))

    @app.route("/signup", methods=("GET", "POST"))
    def signup():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            error = None
            if not name or not email or not password:
                error = "All fields are required."

            if error is None:
                db = get_db()
                try:
                    db.execute(
                        """
                        INSERT INTO user (name, email, password_hash, role, balance_nrs)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (name, email, generate_password_hash(password), "user", 200000),
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    error = "Email already registered."

            if error is None:
                flash("Account created. Please log in.")
                return redirect(url_for("login"))

            flash(error)

        return render_template("signup.html")

    @app.route("/login", methods=("GET", "POST"))
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            db = get_db()
            user = db.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()

            error = None
            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Invalid email or password."

            if error is None:
                session.clear()
                session["user_id"] = user["id"]
                flash("Logged in successfully.")
                return redirect(url_for("destinations"))

            flash(error)

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out.")
        return redirect(url_for("login"))

    @app.route("/destinations")
    def destinations():
        db = get_db()
        destinations_list = db.execute(
            "SELECT * FROM destination ORDER BY price_nrs ASC"
        ).fetchall()
        return render_template("destinations.html", destinations=destinations_list)

    @app.route("/book/<int:destination_id>", methods=("POST",))
    @login_required
    def book(destination_id: int):
        db = get_db()
        destination = db.execute(
            "SELECT * FROM destination WHERE id = ?", (destination_id,)
        ).fetchone()
        if destination is None:
            flash("Destination not found.")
            return redirect(url_for("destinations"))

        user_row = db.execute(
            "SELECT balance_nrs FROM user WHERE id = ?",
            (g.user["id"],),
        ).fetchone()
        if user_row is None:
            flash("User not found.")
            return redirect(url_for("destinations"))

        if user_row["balance_nrs"] < destination["price_nrs"]:
            flash("Insufficient balance for this booking.")
            return redirect(url_for("destinations"))

        balance_update = db.execute(
            """
            UPDATE user
            SET balance_nrs = balance_nrs - ?
            WHERE id = ? AND balance_nrs >= ?
            """,
            (destination["price_nrs"], g.user["id"], destination["price_nrs"]),
        )
        if balance_update.rowcount == 0:
            flash("Insufficient balance for this booking.")
            return redirect(url_for("destinations"))

        db.execute(
            "INSERT INTO booking (user_id, destination_id, status) VALUES (?, ?, ?)",
            (g.user["id"], destination_id, "confirmed"),
        )
        db.commit()
        flash("Booking confirmed. Balance updated.")
        return redirect(url_for("my_bookings"))

    @app.route("/my-bookings")
    @login_required
    def my_bookings():
        db = get_db()
        bookings = db.execute(
            """
            SELECT booking.id, booking.status, booking.created_at,
                   destination.title, destination.duration_days, destination.price_nrs
            FROM booking
            JOIN destination ON booking.destination_id = destination.id
            WHERE booking.user_id = ?
            ORDER BY booking.created_at DESC
            """,
            (g.user["id"],),
        ).fetchall()
        return render_template("bookings.html", bookings=bookings)

    @app.route("/admin")
    @admin_required
    def admin():
        db = get_db()
        user_options = db.execute(
            "SELECT id, name, email FROM user WHERE role = 'user' ORDER BY name"
        ).fetchall()
        users = db.execute(
            """
            SELECT id, name, email, role, balance_nrs, created_at
            FROM user
            ORDER BY created_at DESC
            """
        ).fetchall()
        destinations_list = db.execute(
            "SELECT * FROM destination ORDER BY id DESC"
        ).fetchall()
        bookings = db.execute(
            """
            SELECT booking.id, booking.status, booking.created_at,
                   user.name AS user_name, user.email AS user_email,
                   destination.title, destination.price_nrs
            FROM booking
            JOIN user ON booking.user_id = user.id
            JOIN destination ON booking.destination_id = destination.id
            ORDER BY booking.created_at DESC
            """
        ).fetchall()
        return render_template(
            "admin.html",
            user_options=user_options,
            users=users,
            destinations=destinations_list,
            bookings=bookings,
        )

    @app.route("/admin/add-funds", methods=("POST",))
    @admin_required
    def add_funds():
        user_id = request.form.get("user_id", type=int)
        amount = request.form.get("amount", type=int)

        if not user_id or not amount or amount <= 0:
            flash("Enter a valid user and positive amount.")
            return redirect(url_for("admin"))

        db = get_db()
        user = db.execute(
            "SELECT role FROM user WHERE id = ?",
            (user_id,),
        ).fetchone()
        if user is None or user["role"] != "user":
            flash("Invalid user selected.")
            return redirect(url_for("admin"))

        db.execute(
            "UPDATE user SET balance_nrs = balance_nrs + ? WHERE id = ?",
            (amount, user_id),
        )
        db.commit()
        flash("Funds added successfully.")
        return redirect(url_for("admin"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
