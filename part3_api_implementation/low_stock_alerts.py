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

