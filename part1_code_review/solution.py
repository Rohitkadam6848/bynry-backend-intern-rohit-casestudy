from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    try:
      
        required_fields = ['name', 'sku', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        
        price = Decimal(str(data['price']))

       
        existing = Product.query.filter_by(sku=data['sku']).first()
        if existing:
            return jsonify({"error": "SKU already exists"}), 400

     
        with db.session.begin():

           
            product = Product(
                name=data['name'],
                sku=data['sku'],
                price=price
            )
            db.session.add(product)
            db.session.flush() 

            
            if 'warehouse_id' in data and 'initial_quantity' in data:
                if data['initial_quantity'] < 0:
                    return jsonify({"error": "Invalid quantity"}), 400

                inventory = Inventory(
                    product_id=product.id,
                    warehouse_id=data['warehouse_id'],
                    quantity=data['initial_quantity']
                )
                db.session.add(inventory)

        return jsonify({
            "message": "Product created",
            "product_id": product.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
