import sqlite3

conn = sqlite3.connect("instance/borichkas_slop.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image_url TEXT,
    category TEXT,
    company TEXT
)
''')

pizzas = [
    ("Класична Пепероні", "Салямі, томатний соус, моцарела.", 179, "https://cdn.smak.menu/images/maxone/14741/14741-354a42d77438f1873a7305a65df61089.jpg"),
    ("Маргарита", "Томати, базилік, моцарела.", 149, "https://foodfestival.com.ua/image/cache/catalog/articles/glavnoe_blyudo-pizza-margherita-pomidory-motsarela-bazilik-1920x1000.jpg"),
    ("Гавайська", "Шинка, ананас, сир.", 165, "https://galya-baluwana.in.ua/wp-content/uploads/2023/11/Pitsa-Gavajska.webp"),
    ("Супрім", "Перець, гриби, ковбаса, маслини, сир.", 189, "https://cdn1.komiz.io/44854898/share/data/p/chiken-suprim-8533-2x2000x2000x0x0x0.jpg"),
    ("Чотири сири", "Моцарела, горгонзола, пармезан, едам.", 195, "https://static.toiimg.com/thumb/53110049.cms?imgsize=275940&width=800&height=800"),
    ("Вегетаріанська", "Овочі, томати, сир, базилік.", 159, "https://cdn.pixabay.com/photo/2017/12/09/08/18/pizza-3007395_1280.jpg"),
    ("М’ясна", "Ковбаса, бекон, шинка, соус BBQ.", 199, "https://presa.com.ua/images/2021/09/26/photo_large.jpg"),
    ("З грибами", "Печериці, сир, соус, зелень.", 155, "https://th.bing.com/th/id/R.a8527f63668258a446ee3660851a997d?rik=%2bJ0aezvQ1pkgKg&pid=ImgRaw&r=0"),
    ("BBQ курка", "Курка, соус BBQ, цибуля, сир.", 185, "https://static.tildacdn.com/stor3531-3632-4235-b536-333032666536/23603086.jpg"),
    ("4 Сезони", "Сир, м’ясо, овочі, морепродукти.", 205, "https://www.moi-sushi.com.ua/wp-content/uploads/2022/08/piczcza-4-sezona.jpg"),
    ("Дьябло", "Пікантна ковбаса, перець чилі, томати.", 189, "https://th.bing.com/th/id/OIP.1qzotMZKH4Bj5_1dJbNuwAHaFb?rs=1&pid=ImgDetMain"),
    ("Шинка та чеддер", "Шинка, сир чеддер, гриби, вершковий соус.", 175, "https://rozdil.lviv.ua/statti/1/b1667756303-963.jpg")
]

# Вставка даних з додаванням category та company за замовчуванням
pizza_products = []
for pizza in pizzas:
    pizza_products.append((pizza[0], pizza[1], pizza[2], pizza[3], "pizza", "Borichka"))

cursor.executemany('''
INSERT INTO products (name, description, price, image_url, category, company)
VALUES (?, ?, ?, ?, ?, ?)
''', pizza_products)

conn.commit()
conn.close()

print("Таблиця borichkas_slop.db створена та заповнена піцами")
