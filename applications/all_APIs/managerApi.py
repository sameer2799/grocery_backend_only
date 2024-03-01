from flask_restful import Api, Resource, reqparse
from flask_restful import fields, marshal_with
from applications.all_APIs.validations import *
from applications.models import *
from flask import current_app as app
import datetime

apiM = Api()

#====================================================   Category related Request Parser and return format    ====================================================
category_parser = reqparse.RequestParser()
category_parser.add_argument('category_name')

return_format = {
    'category_id': fields.Integer,
    'category_name': fields.String
}


#==============================================================================================================================================
#====================================================   Category Management related APIs    ===================================================
#==============================================================================================================================================

class CategoryAPI(Resource):
    @marshal_with(return_format)
    def get(self, manager_id, id):
        category = db.session.query(Category).filter(Category.category_id == id).first()
        if category:
            return category, 200
        raise CategoryNotFoundError(status_code = 404, error_code = "CA400", error_message = "The category you are looking for, was not found")

    @marshal_with(return_format)
    def put(self, manager_id, id):
        args = category_parser.parse_args()
        category = db.session.query(Category).filter(Category.category_id == id).first()
        cat_name = args.get("category_name", None)

        category = db.session.query(Category).filter(Category.category_name == cat_name).all()
        if category:
            raise UniqueConstraintFailed(status_code = 300, error_code = "UQ300", error_message = "Please enter a unique name!")
        
        if (category is None):
            raise CategoryNotFoundError(status_code = 404, error_code = "CA400", error_message = "The category you are looking for, was not found")
        else:
            if cat_name:
                category = db.session.query(Category).filter(Category.category_id == id).first()
                category.category_name = cat_name
                db.session.commit()
                return category, 200
            else:
                raise EmptyEntriesError(status_code = 405, error_code = "EM300", error_message = "Fields are empty!")
                

    def delete(self, manager_id, id):
        if id:
            for_cart_delete = db.session.query(Products).filter(Products.product_category_id == id).all()
            prod_ids = [el.product_id for el in for_cart_delete]
            carted = db.session.query(Customer_cart).filter(Customer_cart.carted_products.in_(prod_ids)).delete(synchronize_session="fetch")
            products = db.session.query(Products).filter(Products.product_category_id == id).delete(synchronize_session="fetch")
            of_cat = db.session.query(Categorize).filter(Categorize.c_category_id == id).delete(synchronize_session="fetch")
            if of_cat:
                db.session.commit()
                
                return {"Status":"Category Deletion Successful"}, 200
            else:
                raise CategoryNotFoundError(status_code = 404, error_code = "CA400", error_message = "The category you are looking for, was not found")
        else:
            raise EmptyEntriesError(status_code = 405, error_code = "EM300", error_message = "Fields are empty!")

    @marshal_with(return_format)
    def post(self, manager_id):
        args = category_parser.parse_args()
        cat_name = args.get("category_name", None)
        if cat_name:
            category = db.session.query(Category).filter(Category.category_name == cat_name).all()
            if category:
                raise UniqueConstraintFailed(status_code = 300, error_code = "UQ300", error_message = "Please enter a unique name!")
            else:
                cate = Category(category_name = cat_name)
                db.session.add(cate)
                db.session.commit()
                
                cate = db.session.query(Category).filter(Category.category_name == cat_name).first()
                m_cate = Categorize(c_category_id = cate.category_id, c_m_id = manager_id)
                
                db.session.add(m_cate)
                db.session.commit()

                return cate, 200
        elif cat_name == "":
            raise EmptyEntriesError(status_code = 405, error_code = "EM300", error_message = "Fields are empty!")
            


apiM.add_resource(CategoryAPI, "/api/manager/<int:manager_id>/get/category/<int:id>","/api/manager/<int:manager_id>/put/category/<int:id>", "/api/manager/<int:manager_id>/delete/category/<int:id>", "/api/manager/<int:manager_id>/add/category")



#==============================================================================================================================================
#====================================================   Product Management related APIs    ====================================================
#==============================================================================================================================================

#====================================================   Product related Request Parser and return format    ====================================================
product_parser = reqparse.RequestParser()
product_parser.add_argument('product_name')
product_parser.add_argument('units')
product_parser.add_argument('price_per_unit')
product_parser.add_argument('stock')
product_parser.add_argument('expiry_date')
product_parser.add_argument('description')

product_return_format = {
    'product_name': fields.String,
    'units': fields.String,
    'price_per_unit': fields.String,
    'stock': fields.Integer,
    'expiry_date': fields.String,
    'description': fields.String
}


class ProductAPI(Resource):
    @marshal_with(product_return_format)
    def get(self, manager_id, id, p_id):
        product = db.session.query(Products).filter(Products.product_id == p_id).first()
        if product is None:
            raise ProductNotFoundError(status_code = 400, error_code = "PR400", error_message = "The product you are looking for, was not found!")
        return product, 200

    @marshal_with(product_return_format)
    def put(self, manager_id, id, p_id):
        args = product_parser.parse_args()
        product_name = args.get("product_name", None)
        units = args.get("units", None)
        price_per_unit = args.get("price_per_unit", None)
        stock = args.get("stock", None)
        expiry_date = args.get("expiry_date", None)
        description = args.get("description", None)

        expiry_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()

        p_exists = db.session.query(Products).filter(Products.product_name == product_name).all()
        if p_exists:
            raise UniqueConstraintFailed(status_code = 300, error_code = "UQ300", error_message = "Please enter a unique name!")

        if product_name and units and price_per_unit and stock and expiry_date and description:
            
            product = db.session.query(Products).filter(Products.product_id == p_id).first()
            if product is None:
                raise ProductNotFoundError(status_code = 400, error_code = "PR400", error_message = "The product you are looking for, was not found!")
            
            product = db.session.query(Products).filter(Products.product_id == p_id).delete(synchronize_session='evaluate')
            updated_product = Products(product_name = product_name, units = units, price_per_unit = price_per_unit, stock = stock, expiry_date = expiry_date, description = description, product_category_id = id)
            cat = db.session.query(Category).filter(Category.category_id == id).first()
            cat.contains.append(updated_product)
            db.session.add(updated_product)
            db.session.commit()
            
            return updated_product, 200
            
        elif (product_name or units or price_per_unit or stock or expiry_date or description == None) or (product_name or units or price_per_unit or stock or expiry_date or description == ""):
            
            raise EmptyEntriesError(status_code = 405, error_code = "EM300", error_message = "Fields are empty!")
            

    @marshal_with(product_return_format)
    def post(self, manager_id, id):
        args = product_parser.parse_args()
        product_name = args.get("product_name", None)
        units = args.get("units", None)
        price_per_unit = args.get("price_per_unit", None)
        stock = args.get("stock", None)
        expiry_date = args.get("expiry_date", None)
        description = args.get("description", None)

        expiry_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
        
        p_exists = db.session.query(Products).filter(Products.product_name == product_name).all()
        if p_exists:
            raise UniqueConstraintFailed(status_code = 300, error_code = "UQ300", error_message = "Please enter a unique name!")

        if product_name and units and price_per_unit and stock and expiry_date and description:
            cat = db.session.query(Category).filter(Category.category_id == id).first()
            product = Products(product_name = product_name, units = units, price_per_unit = price_per_unit, stock = stock, expiry_date = expiry_date, description = description,product_category_id = id)
            cat.contains.append(product)
            db.session.add(product)
            db.session.commit()
            
            return product, 200
            
        elif (product_name or units or price_per_unit or stock or expiry_date or description == None) or (product_name or units or price_per_unit or stock or expiry_date or description == ""):
            raise EmptyEntriesError(status_code = 405, error_code = "EM300", error_message = "Fields are empty!")
            

    def delete(self, manager_id, id, p_id):
        if p_id:
            product = db.session.query(Products).filter(Products.product_id == p_id).first()
            if product is None:
                raise ProductNotFoundError(status_code = 400, error_code = "PR400", error_message = "The product you are looking for, was not found!")
            
            carted = db.session.query(Customer_cart).filter(Customer_cart.carted_products == p_id).delete(synchronize_session="fetch")
            product = db.session.query(Products).filter(Products.product_id == p_id).delete(synchronize_session="fetch")
            db.session.commit()
            return {"Status":"Product Deletion Successful"}, 200
        else:
            raise EmptyEntriesError(status_code = 405, error_code = "EM300", error_message = "Fields are empty!")
        



apiM.add_resource(ProductAPI, "/api/manager/<int:manager_id>/category/<int:id>/get/product/<int:p_id>", "/api/manager/<int:manager_id>/category/<int:id>/put/product/<int:p_id>", "/api/manager/<int:manager_id>/category/<int:id>/delete/product/<int:p_id>", "/api/manager/<int:manager_id>/category/<int:id>/add/product")