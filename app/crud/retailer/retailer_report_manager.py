from collections import defaultdict
from ...models.customer.order_model import Order, OrderItem
from ...models.retailer.customer_invoice_model import CustomerInvoice
from ...db.base.database_manager import DatabaseManager
from ...schemas.retailer.retailer_report_schema import RetailerSalesDashboard, RetailerTopSellingProduct
import calendar

class RetailerReportManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    async def get_sales_dashboard(self, retailer_id: int) -> RetailerSalesDashboard:
        await self.db_manager.connect()

        # ---------------------------
        # Fetch orders & invoices
        # ---------------------------
        # invoices = await self.db_manager.read(CustomerInvoice, {"RetailerId": retailer_id})
        orders = await self.db_manager.read(Order, {"RetailerId": retailer_id})
        order_items = await self.db_manager.read(OrderItem, {"RetailerId": retailer_id})

        total_revenue = sum(o.Amount or 0 for o in orders)
        total_orders = len(orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # ---------------------------
        # Monthly Trends
        # ---------------------------
        sales_trend_dict = defaultdict(float)
        order_volume_dict = defaultdict(int)

        for ord in orders:
            month_name = ord.OrderDateTime.strftime("%b")
            sales_trend_dict[month_name] += ord.Amount or 0

        for ord in orders:
            month_name = ord.OrderDateTime.strftime("%b")
            order_volume_dict[month_name] += 1

        # Ensure all months present
        all_months = [calendar.month_abbr[i] for i in range(1, 13)]
        sales_trend = [{month: sales_trend_dict.get(month, 0)} for month in all_months]
        order_volume = [{month: order_volume_dict.get(month, 0)} for month in all_months]

        # ---------------------------
        # Top Selling Products
        # ---------------------------
        product_sales = defaultdict(lambda: {"Quantity": 0, "UnitPrice": 0})
        for item in order_items:
            if item.MedicineName not in product_sales:
                product_sales[item.MedicineName]["Quantity"] = 0
                product_sales[item.MedicineName]["UnitPrice"] = 0
            product_sales[item.MedicineName]["Quantity"] += item.Quantity or 0
            product_sales[item.MedicineName]["UnitPrice"] += (item.Quantity or 0) * (item.UnitPrice or 0)

        top_products = sorted(
            [RetailerTopSellingProduct(MedicineName=k, Quantity=v["Quantity"], UnitPrice=v["UnitPrice"]) for k, v in product_sales.items()],
            key=lambda x: x.Quantity,
            reverse=True
        )[:10]  # top 10 products

        await self.db_manager.disconnect()

        return RetailerSalesDashboard(
            TotalRevenue=total_revenue,
            TotalOrders=total_orders,
            AvgOrderValue=avg_order_value,
            SalesTrend=sales_trend,
            OrderVolume=order_volume,
            TopSellingProduct=top_products
        )
