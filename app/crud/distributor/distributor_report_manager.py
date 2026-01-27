from collections import defaultdict
from ...models.retailer.retailer_order_model import RetailerOrder, RetailerOrderItem
from ...models.retailer.medicine_model import Medicine
from ...schemas.distributor.distributor_report_schema import DistributorSalesDashboard, DistributorTopSellingProduct
from ...db.base.database_manager import DatabaseManager
import calendar

class DistributorReportManager:
    def __init__(self, db_type: str):
        self.db_manager = DatabaseManager(db_type)

    async def get_sales_dashboard(self, distributor_id: int) -> DistributorSalesDashboard:
        await self.db_manager.connect()

        try:
            # ---------------------------
            # Fetch orders & order items
            # ---------------------------
            orders = await self.db_manager.read(RetailerOrder, {"DistributorId": distributor_id})
            order_items = await self.db_manager.read(RetailerOrderItem, {"DistributorId": distributor_id})

            # ---------------------------
            # Fetch all medicines (no filtering by list)
            # ---------------------------
            medicines = await self.db_manager.read(Medicine, {})
            medicine_map = {m.MedicineId: m for m in medicines}

            # ---------------------------
            # Revenue & average order value
            # ---------------------------
            total_revenue = sum(ord.Amount or 0 for ord in orders)
            total_orders = len(orders)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

            # ---------------------------
            # Monthly trends
            # ---------------------------
            sales_trend_dict = defaultdict(float)
            order_volume_dict = defaultdict(int)

            for ord in orders:
                month_name = ord.OrderDateTime.strftime("%b")
                sales_trend_dict[month_name] += ord.Amount or 0
                order_volume_dict[month_name] += 1

            all_months = [calendar.month_abbr[i] for i in range(1, 13)]
            sales_trend = [{month: sales_trend_dict.get(month, 0)} for month in all_months]
            order_volume = [{month: order_volume_dict.get(month, 0)} for month in all_months]

            # ---------------------------
            # Top selling products
            # ---------------------------
            product_sales = defaultdict(lambda: {"Quantity": 0, "Revenue": 0})

            for item in order_items:
                med = medicine_map.get(item.MedicineId)
                if not med:
                    continue

                product_sales[med.MedicineName]["Quantity"] += item.Quantity
                product_sales[med.MedicineName]["Revenue"] += item.Quantity * med.UnitPrice

            top_products = sorted(
                [
                    DistributorTopSellingProduct(
                        MedicineName=k,
                        Quantity=v["Quantity"],
                        UnitPrice=v["Revenue"]
                    )
                    for k, v in product_sales.items()
                ],
                key=lambda x: x.Quantity,
                reverse=True
            )[:10]

            return DistributorSalesDashboard(
                TotalRevenue=total_revenue,
                TotalOrders=total_orders,
                AvgOrderValue=avg_order_value,
                SalesTrend=sales_trend,
                OrderVolume=order_volume,
                TopSellingProduct=top_products
            )

        finally:
            await self.db_manager.disconnect()
