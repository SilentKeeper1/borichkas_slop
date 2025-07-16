from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, create_engine, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
Base = declarative_base()

#  Користувачі
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    surname = Column(String)
    phone = Column(String)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    bonus_balance = Column(Integer, default=0)

    is_admin = Column(Boolean, default=False)

    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")


#  Замовлення
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    items = Column(Text, nullable=False)  # JSON товарів
    total = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String)
    status = Column(String, default="new")

    user = relationship("User", back_populates="orders")


#  Кошик
class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    user = relationship("User", back_populates="cart_items")


#  Ініціалізація БД
engine = create_engine("sqlite:///instance/db.sqlite3.db", echo=True)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)