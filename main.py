import datetime, json
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_cors import CORS
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

from applications.models import *
from applications.Login_Form_model import *
from applications.all_APIs.managerApi import *

# from requests import get, put, post, delete 
# import json

#================================================== Base App config ========================================================
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"
app.config['SECRET_KEY'] = 'Impenetrable_KEY@Production'
db.init_app(app)
CORS(app)
apiM.init_app(app)

bcrypt = Bcrypt(app)
app.app_context().push()

#==================================  Login and Registration related config and routes   =================================
#==================================      contains both for managers and customers       =================================

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    u = db.session.query(Customer).filter(Customer.id == int(user_id)).first()
    
    return u

#=================================================== Home Route =========================================================
@app.route("/")
def home_page():
    return render_template("home_page.html")

#=======================================================================================================================
#==============================================     Manager related Routes     =========================================
#=======================================================================================================================
@app.route("/manager", methods = ['GET', 'POST'])
def manager():
    if request.method == 'GET':
        return render_template("/Manager/Manager_login.html")
    if request.method == 'POST':       
        name = request.form.get('username')
        passkey = request.form.get('pass')
        
        if name and passkey:
            existing_mana = Managers.query.filter(Managers.mana_name == name).first()
            if existing_mana:
                if existing_mana.mana_password == passkey:
                    return redirect(url_for('manager_dashboard', id = existing_mana.m_id))
                flash('Wrong password!')    
                return redirect(url_for('manager'))
            else:
                new_manager = Managers(mana_name = name, mana_password = passkey)
                db.session.add(new_manager)
                db.session.commit()
                new_manager_id = Managers.query.filter(Managers.mana_name == name).first()
                return redirect(url_for('manager_dashboard', id = new_manager_id.m_id))
        else:
            flash('Enter all fields!')    
            return redirect(url_for('manager'))


@app.route('/manager/<int:id>/dashboard', methods=['GET', 'POST'])
def manager_dashboard(id):
    if request.method == 'GET':
        Man_obj = db.session.query(Managers).filter(Managers.m_id == id).first()
        return render_template("/Manager/Manager_Dashboard.html", manager = Man_obj)

#=========================================    Category Management     ==================================================

#===========  For category add  ===============================
@app.route('/manager/<int:id>/add/category', methods =['GET', 'POST'])
def category_add(id):
    if request.method == 'GET':
        return render_template('/Manager/Category Manage/Category_ADD.html', id= id)
    if request.method == 'POST':
        cat_name = request.form.get('cate_name')
        
        
        #   Attempted to use the APIs created, but after many failed tries I just implemented directly.

        """
        payload = {"category_name" : cat_name}
        print(payload)
        response = r.post(f"http://localhost:5000/manager/api/add/category", headers={"Content-Type" : "application/json"}, data = payload)
        print(response)
        print(response.status_code)
        """
        
        if cat_name:
            cate = db.session.query(Category).filter(Category.category_name == cat_name).all()
            if cate:
                flash("Please enter a unique name!")
                return redirect(url_for('category_add', id = id))
                
            else:
                new_cate = Category(category_name = cat_name)
                db.session.add(new_cate)
                db.session.commit()
                cate_id = db.session.query(Category).filter(Category.category_name == cat_name).first()
                m_cate = Categorize(c_category_id = cate_id.category_id, c_m_id = id)
                db.session.add(m_cate)
                db.session.commit()
                flash("Category successfully added!")
                return redirect(url_for('manager_dashboard', id = id))
        else:
            flash("Please enter some name!")
            return redirect(url_for('category_add', id = id))

#===========  For category update  ===============================
@app.route('/manager/<int:id>/update/category/<int:cat_id>', methods=['GET','POST'])
def category_update(id, cat_id):
    if request.method == 'GET':
        return render_template('/Manager/Category Manage/Category_UPDATE.html', id= id, cat_id = cat_id)
    if request.method == 'POST':
        new_cat_name = request.form.get('cate_name')
        
        categories = db.session.query(Category).filter(Category.category_name == new_cat_name).all()
        if categories:
            flash("Please enter a unique name!")
            return render_template('/Manager/Category Manage/Category_UPDATE.html', id= id, cat_id = cat_id)

        if new_cat_name:
            cat = db.session.query(Category).filter(Category.category_id == cat_id).first()
            cat.category_name = new_cat_name
            db.session.commit()
            flash("Category successfully updated!")
            return redirect(url_for('manager_dashboard', id = id))
        else:
            flash("Please Enter a name!")
            return render_template('/Manager/Category Manage/Category_UPDATE.html', id= id, cat_id = cat_id)
        
#===========  For category delete  ===============================
@app.route('/manager/<int:id>/delete/category/<int:cat_id>', methods=['GET', 'POST'])
def category_delete(id, cat_id):
    if request.method == 'GET':
        return render_template('/Manager/Category Manage/Category_DELETE.html', id= id, cat_id = cat_id)
    if request.method == 'POST':
        val = request.form.get('confirm')
        if val == "YES":
            for_cart_delete = db.session.query(Products).filter(Products.product_category_id == cat_id).all()
            prod_ids = [el.product_id for el in for_cart_delete]
            carted = db.session.query(Customer_cart).filter(Customer_cart.carted_products.in_(prod_ids)).delete(synchronize_session="fetch")
            products = db.session.query(Products).filter(Products.product_category_id == cat_id).delete(synchronize_session="fetch")
            of_cat = db.session.query(Categorize).filter(Categorize.c_category_id == cat_id).delete(synchronize_session="fetch")
            db.session.commit()
            flash("Category successfully deleted!")
            return redirect(url_for('manager_dashboard', id = id))
        else:
            return redirect(url_for('manager_dashboard', id = id))

#===========================================  Product Management  =====================================================

#==============  For product add  ===============================
@app.route('/manager/<int:id>/category/<int:cat_id>/add/product', methods=['GET', 'POST'])
def product_add(id, cat_id):
    if request.method == 'GET':
        cat = db.session.query(Category).filter(Category.category_id == cat_id).first()
        return render_template('/Manager/Product Manage/Product_ADD.html', id= id, cat_id = cat_id, cat_name = cat.category_name)
    if request.method == 'POST':
        name = request.form.get('prod_name')
        units = request.form.get('units')
        unitPrice = request.form.get('unit_price')
        stock = request.form.get('stocked')
        expi = request.form.get('expiry')
        des = request.form.get('descrip')
        
        expi_d = datetime.datetime.strptime(expi, "%Y-%m-%d").date()
        
        p_exists = db.session.query(Products).filter(Products.product_name == name).all()
        if p_exists:
            flash('Enter a unique name for your product!')
            return redirect(url_for('product_add', id= id, cat_id = cat_id))

        if name and units and unitPrice and stock and expi and des:
            cat = db.session.query(Category).filter(Category.category_id == cat_id).first()
            product = Products(product_name = name, units=units, price_per_unit=unitPrice, stock=stock, expiry_date=expi_d, description=des,product_category_id=cat_id)
            cat.contains.append(product)
            db.session.add(product)
            db.session.commit()
            flash("Product successfully added!")
            return redirect(url_for('manager_dashboard', id = id))
        else:
            flash('Enter all values!')
            return redirect(url_for('product_add', id= id, cat_id = cat_id))

#==============  For product update  ===============================
@app.route('/manager/<int:id>/category/<int:cat_id>/update/product/<int:prod_id>', methods=['GET', 'POST'])
def product_update(id, cat_id, prod_id):
    if request.method == 'GET':
        return render_template('/Manager/Product Manage/Product_UPDATE.html', id= id, cat_id = cat_id, prod_id = prod_id)
    if request.method == 'POST':
        name = request.form.get('prod_name')
        units = request.form.get('units')
        unitPrice = request.form.get('unit_price')
        stock = request.form.get('stocked')
        expi = request.form.get('expiry')
        des = request.form.get('descrip')

        expi_d = datetime.datetime.strptime(expi, "%Y-%m-%d").date()
        
        p_exists = db.session.query(Products).filter(Products.product_name == name).all()
        if p_exists:
            flash('Enter a unique name for your product!')
            return redirect(url_for('product_add', id= id, cat_id = cat_id))

        if name and units and unitPrice and stock and expi and des:
            product = db.session.query(Products).filter(Products.product_id == prod_id).delete(synchronize_session='evaluate')
            
            updated_product = Products(product_name = name, units = units, price_per_unit = unitPrice, stock = stock, expiry_date = expi_d, description = des, product_category_id = cat_id)
            cat = db.session.query(Category).filter(Category.category_id == cat_id).first()
            cat.contains.append(updated_product)
            db.session.add(updated_product)
            db.session.commit()
            flash("Product successfully updated!")
            return redirect(url_for('manager_dashboard', id = id))
        else:
            flash('Enter all values!')
            return redirect(url_for('product_update', id= id, cat_id = cat_id, prod_id = prod_id))

#==============  For product delete  ===============================
@app.route('/manager/<int:id>/category/<int:cat_id>/delete/product/<int:prod_id>', methods=['GET', 'POST'])
def product_delete(id, cat_id, prod_id):
    if request.method == 'GET':
        return render_template('/Manager/Product Manage/Product_DELETE.html', id= id, cat_id = cat_id, prod_id = prod_id)
    if request.method == 'POST':
        val = request.form.get('confirm')
        if val == "YES":
            
            carted = db.session.query(Customer_cart).filter(Customer_cart.carted_products == prod_id).delete(synchronize_session="fetch")
            
            product = db.session.query(Products).filter(Products.product_id == prod_id).delete(synchronize_session="fetch")
            db.session.commit()
            flash("Product successfully deleted!")
            return redirect(url_for('manager_dashboard', id = id))
        else:
            return redirect(url_for('manager_dashboard', id = id))


#=====================================================================================================================
#================================================     User related Routes     ========================================
#=====================================================================================================================

#===================================   Customer Login, Logout, Register routes  ======================================

@app.route("/cust", methods = ['GET', 'POST'])
def customer():
    if request.method == 'GET':
        return render_template("/User/Account.html")
    
@app.route('/cust/customer_login', methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        cust = Customer.query.filter_by(user_name = form.username.data).first()
        if cust:
            if bcrypt.check_password_hash(cust.user_password, form.password.data):
                login_user(cust)
                return redirect(url_for('cust_dashboard', cust_id = cust.id))
            else:
                flash("Wrong password!")
                return render_template('/User/customer_login_page.html', form = form)

    return render_template('/User/customer_login_page.html', form = form) 

@app.route('/cust/customer_logout')
@login_required
def cust_logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/cust/registration', methods=['GET','POST'])
def customer_register():
    form = UserRegisterForm()

    if form.validate_on_submit():
        
        encrypted_password = bcrypt.generate_password_hash(form.password.data)
        new_cust = Customer(user_name = form.username.data, user_password = encrypted_password)
        db.session.add(new_cust)
        db.session.commit()
        return redirect(url_for('login'))

    
    return render_template('/User/customer_register_page.html', form = form)

#=========================================   Customer Dashboard   =============================================

@app.route('/cust/<int:cust_id>/dashboard', methods=['GET','POST'])
@login_required
def cust_dashboard(cust_id):
    c = Customer_cart.query.filter(Customer_cart.cust == cust_id).all()
    
    cat = db.session.query(Category).all()
    
    
    return render_template('/User/Customer_Dashboard.html', cart = c, category = cat)

#=========================================   Cart Actions   =============================================
@app.route('/cust/<int:cust_id>/cart', methods=['GET'])
@login_required
def cust_cart(cust_id):
    #---------  the parameter cust_id is for my convenience, current_user does the same job------
    cart = Customer_cart.query.filter(Customer_cart.cust == cust_id).all()
    custo = Customer.query.filter(Customer.id == cust_id).first()
    products = db.session.query(Products).all()
    p_stock = {}
    
    price_to_pay = 0
    for c in cart:
        for p in custo.customer_carted:
            if c.carted_products == p.product_id:
                price_to_pay += p.price_per_unit * c.quantity
                p_stock[p.product_id] = p.stock
    

    if request.method == 'GET':
        return render_template('/User/customer_cart.html', customer = custo, cart = cart, total = price_to_pay, p_stock = p_stock)


@app.route('/cust/<int:cust_id>/adding_to_cart', methods=['POST'])
@login_required
def addding_to_cart(cust_id):
    p_id = request.form.get('product_id')
    quant = request.form.get('quantity')
    
    if request.method == 'POST':
        c = db.session.query(Customer_cart).filter_by(cust = cust_id, carted_products = p_id).first()
        if c:
            flash("Product added to cart")
            c.quantity += int(quant)
            db.session.commit()
        else:
            flash("Product added to cart")
            cart_obj = Customer_cart(cust = cust_id, carted_products = p_id, quantity = quant)
            db.session.add(cart_obj)
            db.session.commit()
        
        return redirect(url_for('cust_dashboard', cust_id = cust_id))

@app.route('/cust/<int:cust_id>/remove_item/<int:product_id>', methods=['POST'])
@login_required
def remove_item(cust_id, product_id):
    if request.method == 'POST':
        item = db.session.query(Customer_cart).filter(Customer_cart.cust == cust_id, Customer_cart.carted_products == product_id).delete(synchronize_session="fetch")
        db.session.commit()
        flash("Product removed successfully!")
        return redirect(url_for('cust_cart', cust_id = cust_id))

#=================================================    Search Route    ================================================

@app.route('/search/<int:cust_id>', methods=['GET', 'POST'])
def search(cust_id):
    if request.method == 'GET':
        return render_template("search_results.html",cust_for_id = cust_id, q = None, category_results = None, product_name_results = None, product_price_r = None, product_date_r = None)
    if request.method == 'POST':
        q = request.form.get('q')
        d_q = q

        if q:
            if "-" in q:
                d_q = datetime.datetime.strptime(q, "%Y-%m-%d").date()
            category_results = db.session.query(Category).filter(Category.category_name.like(q)).all()
            product_name_results = db.session.query(Products).filter(Products.product_name.like(q)).all()
            product_price_r = db.session.query(Products).filter(Products.price_per_unit.like(q)).all()
            product_date_r = db.session.query(Products).filter(Products.expiry_date.like(d_q)).all()
            
            
            return render_template("search_results.html",cust_for_id = cust_id, q = q, category_results = category_results, product_name_results = product_name_results, product_price_r = product_price_r, product_date_r = product_date_r)
        else:
            return redirect(url_for('cust_dashboard', cust_id = cust_id))
        


#=================================================    Order Route    ================================================

@app.route('/checking_out/<int:cust_i>', methods=['GET'])
def checkout(cust_i):
    if request.method =='GET':
        customer = db.session.query(Customer).filter(Customer.id == cust_i).first()
        cart = db.session.query(Customer_cart).filter(Customer_cart.cust == cust_i).all()
        prods_arr = customer.customer_carted
        if prods_arr:
            all_prod_id, all_cat_id = [],[]
            total_amt = 0
            cart_prods = {}
            for item in cart:
                cart_prods[item.carted_products] = item.quantity
            
            for i in range(len(prods_arr)):
                all_prod_id.append(prods_arr[i].product_id)
                all_cat_id.append(prods_arr[i].product_category_id)
                j = prods_arr[i].product_id
                price = prods_arr[i].price_per_unit
                total_amt += price * cart_prods[j]
            
            for i in range(len(all_prod_id)):
                order_obj = Order(order_customer_id = cust_i, order_category_id = all_cat_id[i], order_product_id = all_prod_id[i], total_amount = total_amt)
                customer.customer_carted.pop(i)
                db.session.add(order_obj)
                db.session.commit()

            for i in range(len(all_prod_id)):
                ordered_product_id = all_prod_id[i]
                product = db.session.query(Products).filter(Products.product_id == ordered_product_id).first()
                product.stock -= cart_prods[ordered_product_id]
                db.session.commit()

            return {}, 200
        else:
            return {"error": "Cart is empty"}, 404



#=====================================================================================================================
#=================================================     Main Driver Code     ==========================================
#=====================================================================================================================

if __name__=='__main__':
    
    """app.run(debug =True)
    """
    with app.app_context():
        db.create_all()
        app.run(debug = False)
    
    
    






