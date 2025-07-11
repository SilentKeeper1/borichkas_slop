from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify # Додано jsonify
from models import SessionLocal, User
import sqlite3
import json
import bcrypt
from models import SessionLocal, User, Order
from sqlalchemy import func
from datetime import datetime


app = Flask(__name__)
app.secret_key = "borichka-secret"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        db = SessionLocal()
        if db.query(User).filter(User.email == email).first():
            message = "Користувач з такою поштою вже існує."
        else:
            db.add(User(name=name, email=email, password=hashed_password))
            db.commit()
            return redirect(url_for("login"))
    return render_template("register.html", message=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session["user_id"] = user.id
            session["user_name"] = user.name
            return redirect(url_for("index"))
        else:
            message = "Неправильна пошта або пароль"

    return render_template("login.html", message=message)

@app.route("/menu/")
def menu():
    conn = sqlite3.connect("instance/borichkas_slop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, description, price, image_url FROM products WHERE category = 'pizza'")
    items = cursor.fetchall()
    conn.close()
    return render_template("menu.html", items=items)


@app.route("/cart")
def cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cart = session.get("cart", [])
    total = sum(item["price"] * item["quantity"] for item in cart)
    return render_template("cart.html", cart=cart, total=total)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    # Отримуємо дані з JSON-запиту, а не з форми
    data = request.get_json()
    name = data.get("name")
    price = float(data.get("price"))
    image_url = data.get("image_url")

    cart = session.get("cart", [])

    # Перевірка, чи товар вже в кошику
    for item in cart:
        if item["name"] == name:
            item["quantity"] += 1
            break
    else:
        cart.append({
            "name": name,
            "price": price,
            "quantity": 1,
            "image_url": image_url
        })

    session["cart"] = cart
    session.modified = True

    return jsonify({"message": f"Товар '{name}' додано до кошика!"}), 200



@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    if "user_id" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name")
    cart = session.get("cart", [])
    cart = [item for item in cart if item["name"] != name]
    session["cart"] = cart

    return redirect(url_for("cart"))


@app.route("/clear_cart")
def clear_cart():
    session["cart"] = []
    return redirect(url_for("cart"))


@app.route("/checkout")
def checkout():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cart = session.get("cart", [])
    if not cart:
        return redirect(url_for("cart"))

    total = sum(item["price"] * item["quantity"] for item in cart)


    db = SessionLocal()
    user = db.query(User).filter(User.id == session["user_id"]).first()
    db.close()

    user_phone = user.phone if user else ''

    return render_template("checkout.html", cart=cart, total=total, user_phone=user_phone)


@app.route("/create_order", methods=["POST"])
def create_order():
    if "user_id" not in session:
        return redirect(url_for("login"))

    cart = session.get("cart", [])
    if not cart:
        return redirect(url_for("cart"))

    address = request.form.get("address", "").strip()
    phone = request.form.get("phone", "").strip()

    if not address:
        flash("Адреса доставки є обов'язковою!", "error")
        return redirect(url_for("checkout"))

    if not phone:
        flash("Номер телефону є обов'язковим!", "error")
        return redirect(url_for("checkout"))

    total_price = sum(item["price"] * item["quantity"] for item in cart)
    bonus_earned = int(total_price // 10)

    db = SessionLocal()

    new_order = Order(
        user_id=session["user_id"],
        items=json.dumps(cart),
        total=total_price,
        address=address,
        phone=phone,
        status="new"
    )
    db.add(new_order)

    user = db.query(User).filter(User.id == session["user_id"]).first()
    if user:
        user.bonus_balance = (user.bonus_balance or 0) + bonus_earned
        if user.phone != phone:
            user.phone = phone

    db.commit()
    db.close()

    session["cart"] = []
    flash("Замовлення успішно оформлено!", "success")
    return redirect(url_for("cart"))

@app.route("/bonus")
def bonus():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = SessionLocal()
    user = db.query(User).filter(User.id == session["user_id"]).first()

    if not user:
        db.close()
        return redirect(url_for("logout"))

    total_spent = db.query(func.sum(Order.total)).filter(Order.user_id == user.id).scalar() or 0
    bonuses = user.bonus_balance

    db.close()
    return render_template("bonus.html", bonus=bonuses, total_spent=total_spent)


@app.route("/dashboard/", methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == session['user_id']).first()

        if not user:
            flash("Користувача не знайдено. Будь ласка, увійдіть знову.", "error")
            return redirect(url_for('logout'))

        if request.method == 'POST':
            user.name = request.form.get('name')
            user.surname = request.form.get('surname')
            user.phone = request.form.get('phone')

            try:
                db.commit()
                flash('Профіль успішно оновлено!', 'success')
            except Exception as e:
                db.rollback()
                flash(f'Помилка при оновленні профілю: {e}', 'error')

        return render_template("dashboard.html", user=user)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/admin/")
def admin():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = SessionLocal()

    # Останні 10 замовлень
    orders = db.query(Order).order_by(Order.id.desc()).limit(10).all()

    orders_data = []
    for order in orders:
        items = json.loads(order.items)
        pizza_names = ", ".join([item.get("name", "") for item in items])

        created_at = getattr(order, "created_at", None)
        date_str = created_at.strftime("%d.%m.%Y") if created_at else "—"

        user = db.query(User).filter(User.id == order.user_id).first()
        client_name = user.name if user else "Користувач"

        status_map = {
            "new": ("Новий", "bg-warning text-dark"),
            "delivered": ("Доставлено", "bg-success"),
            "cancelled": ("Відмінено", "bg-danger"),
            "in_process": ("В процесі", "bg-info text-white"),
        }
        status_text, status_class = status_map.get(order.status, (order.status.capitalize(), "bg-secondary"))

        orders_data.append({
            "id": order.id,
            "client": client_name,
            "pizza": pizza_names,
            "total": order.total,
            "status_text": status_text,
            "status_class": status_class,
            "date": date_str,
            "address": order.address
        })


    total_orders = db.query(func.count(Order.id)).scalar()
    total_income = db.query(func.sum(Order.total)).scalar() or 0

    db.close()

    return render_template("admin.html",
                           orders=orders_data,
                           total_orders=total_orders,
                           total_income=total_income)


@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = float(request.form.get("price"))
        image_url = request.form.get("image_url")

        # Пріоритет — файл, якщо завантажено
        image_file = request.files.get("image_file")
        if image_file and image_file.filename:
            image_path = f"static/uploads/{image_file.filename}"
            image_file.save(image_path)
            image_url = "/" + image_path  # Шлях для відображення

        conn = sqlite3.connect("instance/borichkas_slop.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, description, price, image_url, category)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, price, image_url, "pizza"))  # або "drink"
        conn.commit()
        conn.close()

        flash("Позицію успішно додано!")
        return redirect(url_for("admin"))

    return render_template("add.html")

if __name__ == "__main__":
    app.run(port=12434, debug=True)