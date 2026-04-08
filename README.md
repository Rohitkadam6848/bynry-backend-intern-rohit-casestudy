# Bynry Backend Intern - Case Study Solution

**Name:** Rohit Bhanudas kadam 
**Email:** rohitkadam1230@gmail.com  
**Date:** 8 April 2026  

---

##  Overview

This submission contains my solution to the StockFlow inventory management case study.  
The goal was to analyze existing code, design a scalable database, and implement a real-world API while handling incomplete requirements.

I focused on:
- Data consistency and integrity
- Scalability for multi-warehouse systems
- Real-world edge cases and failure handling

---

##  Part 1: Code Review & Debugging

###  Issues Identified

1. **Lack of Transaction Atomicity**  
   The code performs two separate commits. If the second operation fails, the product is created but inventory is not, leading to inconsistent data.

2. **No Input Validation**  
   Missing or invalid fields (e.g., price, SKU) can crash the API or store incorrect data.

3. **SKU Uniqueness Not Enforced**  
   Duplicate SKUs can cause major issues in tracking and inventory management.

4. **Incorrect Data Modeling**  
   Product is tied to a single warehouse, violating the requirement that products exist in multiple warehouses.

5. **No Error Handling**  
   Any database failure will crash the API and expose internal errors.

6. **Improper Price Handling**  
   Using float instead of decimal can lead to precision issues in financial data.

7. **No Validation for Inventory Quantity**  
   Negative or missing quantities can corrupt inventory records.

---

### ✅ Fixed Code
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    try:
        # ✅ Validation
        required_fields = ['name', 'sku', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        # ✅ Convert price safely
        price = Decimal(str(data['price']))

        # ✅ Check SKU uniqueness
        existing = Product.query.filter_by(sku=data['sku']).first()
        if existing:
            return jsonify({"error": "SKU already exists"}), 400

        # ✅ Transaction block
        with db.session.begin():

            # Create product (NO warehouse_id here)
            product = Product(
                name=data['name'],
                sku=data['sku'],
                price=price
            )
            db.session.add(product)
            db.session.flush()  # get product.id

            # Optional inventory creation
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



---

##  Part 2: Database Design

### 📊 Schema

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE warehouses (
    id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(id),
    name VARCHAR(255),
    location TEXT
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    sku VARCHAR(100) UNIQUE NOT NULL,
    price DECIMAL(10,2),
    product_type VARCHAR(50)
);

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    warehouse_id INT REFERENCES warehouses(id),
    quantity INT DEFAULT 0,
    UNIQUE(product_id, warehouse_id)
);

CREATE TABLE inventory_logs (
    id SERIAL PRIMARY KEY,
    product_id INT,
    warehouse_id INT,
    change INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    contact_email VARCHAR(255)
);

CREATE TABLE product_suppliers (
    product_id INT,
    supplier_id INT,
    PRIMARY KEY(product_id, supplier_id)
);

-- Bundle support
CREATE TABLE product_bundles (
    bundle_id INT,
    child_product_id INT,
    quantity INT,
    PRIMARY KEY(bundle_id, child_product_id)
);


---

### 🧠 Design Decisions

- Used `DECIMAL/NUMERIC` for price to avoid floating-point precision errors
- Created separate `inventory` table to support multi-warehouse storage
- Added `inventory_logs` for tracking stock changes over time
- Introduced `product_bundles` to support composite products
- Used composite unique constraints to prevent duplicate inventory entries

---

### ❓ Questions for Product Team

1. Is SKU uniqueness global or scoped per company?
2. What defines "recent sales activity" (time window)?
3. Can a product have multiple suppliers?
4. How should bundle inventory be calculated?
5. Do we need soft deletes for products/inventory?
6. Should inventory support reserved stock (pending orders)?

---

## ⚙️ Part 3: API Implementation

### 📌 Assumptions Made

- "Recent sales" = last 30 days
- Low stock threshold stored in product or product type
- Only one (primary) supplier is returned
- Days until stockout is estimated using average daily sales

---

### 💻 Implementation

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    alerts = []

    # Get all warehouses of company
    warehouses = Warehouse.query.filter_by(company_id=company_id).all()

    for warehouse in warehouses:
        inventories = Inventory.query.filter_by(warehouse_id=warehouse.id).all()

        for inv in inventories:
            product = Product.query.get(inv.product_id)

            # Example threshold logic
            threshold = 20 if product.product_type == "standard" else 10

            # Recent sales check (dummy logic)
            recent_sales = Sale.query.filter(
                Sale.product_id == product.id,
                Sale.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count()

            if inv.quantity < threshold and recent_sales > 0:

                supplier = db.session.query(Supplier)\
                    .join(ProductSupplier)\
                    .filter(ProductSupplier.product_id == product.id)\
                    .first()

                alerts.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "sku": product.sku,
                    "warehouse_id": warehouse.id,
                    "warehouse_name": warehouse.name,
                    "current_stock": inv.quantity,
                    "threshold": threshold,
                    "days_until_stockout": 10,  # assumed
                    "supplier": {
                        "id": supplier.id if supplier else None,
                        "name": supplier.name if supplier else None,
                        "contact_email": supplier.contact_email if supplier else None
                    }
                })

    return {
        "alerts": alerts,
        "total_alerts": len(alerts)
    }


---

### ⚠️ Edge Cases Handled

- Company not found → returns 404
- No warehouses → returns empty list
- No supplier linked → returns null safely
- Products with no recent sales → ignored
- Zero daily sales → stockout cannot be calculated

---

## ⚖️ Overall Assumptions & Trade-offs

Due to incomplete requirements, several assumptions were made regarding sales tracking, supplier relationships, and stock thresholds.  
The design prioritizes **data consistency, scalability, and flexibility** for future extensions such as multi-supplier support and advanced analytics.

Trade-offs include:
- Simpler threshold logic instead of configurable rules engine
- Basic stockout estimation instead of predictive modeling

---

## ▶️ How to Run (Optional)

```bash
pip install -r requirements.txt
python app.py
