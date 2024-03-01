from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

#========================== Manager related Tables ====================================
class Managers(db.Model):
    __tablename__ = 'managers'
    
    m_id = db.Column(db.Integer, primary_key = True)
    mana_name = db.Column(db.String(20), unique=True, nullable = False)
    mana_password = db.Column(db.String(80), nullable = False)
    categories = db.relationship('Category', backref = "its_manager", secondary = "categorize")

    def __repr__(self):
        return f"<managers {self.mana_name}>"

class Category(db.Model):
    __tablename__ = 'category'    
    
    category_id = db.Column(db.Integer, primary_key = True)
    category_name = db.Column(db.String, unique=True, nullable = False)
    contains = db.relationship('Products', backref = 'of_category')
    
    def __repr__(self):
        return f"<category {self.category_name}>"

class Products(db.Model):
    __tablename__ = 'products'
    
    product_id = db.Column(db.Integer, primary_key = True)
    product_name = db.Column(db.String(length = 30), unique=True, nullable = False)
    units = db.Column(db.String, nullable = False)
    price_per_unit = db.Column(db.Double, nullable = False)
    stock = db.Column(db.Integer, nullable = False)
    expiry_date = db.Column(db.Date, nullable = False)
    description = db.Column(db.Text, nullable = False)
    product_category_id = db.Column(db.Integer, db.ForeignKey("category.category_id"))

    def __repr__(self):
        return f"<products {self.product_name}>"

class Categorize(db.Model):
    __tablename__ = 'categorize'
    
    c_category_id = db.Column(db.Integer, db.ForeignKey("category.category_id"), primary_key=True)
    c_m_id = db.Column(db.Integer, db.ForeignKey("managers.m_id"), primary_key=True)

#========================== User related Tables ====================================

class Customer(db.Model, UserMixin):
    __tablename__ = 'customer'    
    
    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(20), unique=True, nullable = False)
    user_password = db.Column(db.String(80), nullable = False)
    customer_carted = db.relationship("Products", backref = "of_customer", secondary = "customer_cart")

    def __repr__(self):
        return f"<customer {self.user_name}>"

class Customer_cart(db.Model):
    __tablename__ = 'customer_cart'    
    
    cust = db.Column(db.Integer, db.ForeignKey("customer.id"),primary_key = True)
    carted_products = db.Column(db.Integer, db.ForeignKey("products.product_id"), primary_key = True)
    quantity = db.Column(db.Integer, default = 1, nullable = False)


#========================== Oreders Table ====================================

class Order(db.Model):
    __tablename__ = "order"
    order_id = db.Column(db.Integer, primary_key = True)
    order_customer_id = db.Column(db.Integer, nullable = False)
    order_category_id = db.Column(db.Integer, nullable = False)
    order_product_id = db.Column(db.Integer, nullable = False)
    total_amount = db.Column(db.Double, nullable = False)

    def __repr__(self):
        return f"<order {self.order_id}>"