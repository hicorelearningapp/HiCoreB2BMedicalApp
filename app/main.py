from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


from .api.retailer.medicine_api import MedicineAPI
from .api.retailer.customer_order_api import CustomerOrderAPI


# Retailer
from .api.retailer.retailer_api import RetailerAPI
from .api.retailer.retailer_inventory_api import RetailerInventoryAPI
from .api.retailer.retailer_order_api import RetailerOrderAPI, RetailerOrderItemAPI
from .api.retailer.retailer_report_api import RetailerReportAPI
from .api.retailer.retailer_dashboard_api import RetailerDashboardAPI
from .api.retailer.customer_invoice_api import CustomerInvoiceAPI
from .api.retailer.retailer_notification_api import RetailerNotificationAPI


# Distributor
from .api.distributor.distributor_api import DistributorAPI
from .api.distributor.distributor_notification_api import DistributorNotificationAPI
from .api.distributor.distributor_inventory_api import DistributorInventoryAPI
from .api.distributor.retailer_invoice_api import RetailerInvoiceAPI
from .api.distributor.distributor_report_api import DistributorReportAPI
from .api.distributor.distributor_dashboard_api import DistributorDashboardAPI
from .api.distributor.pharma_order_api import PharmaOrderAPI




app = FastAPI(title="Medical App API list")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow all origins
    allow_credentials=True,
    allow_methods=["*"],          # allow all HTTP methods
    allow_headers=["*"],          # allow all headers
)

app.mount("/Images", StaticFiles(directory="Images"), name="Images")


medicine_api = MedicineAPI()
customer_order_api = CustomerOrderAPI()

# Retailer
retailer_api = RetailerAPI()
retailer_inventory_api = RetailerInventoryAPI()
retailer_order_api = RetailerOrderAPI()
retailer_order_item_api = RetailerOrderItemAPI()
retailer_report_api = RetailerReportAPI()
retailer_dashboard_api = RetailerDashboardAPI()
customer_invoice_api = CustomerInvoiceAPI()
retailer_notification_api = RetailerNotificationAPI()


# Distributor
distributor_api = DistributorAPI()
distributor_notification_api = DistributorNotificationAPI()
distributor_inventory_api = DistributorInventoryAPI()
# distributor_order_api = DistributorAPI()
retailer_invoice_api = RetailerInvoiceAPI()
distributor_report_api = DistributorReportAPI()
distributor_dashboard_api = DistributorDashboardAPI()
pharma_order_api = PharmaOrderAPI()




app.include_router(medicine_api.router, tags=["Medicine"])
app.include_router(customer_order_api.router, tags=["Customer Order Api"])


# Retailer
# app.include_router(retailer_dashboard_api.router, tags=["Retailer Dashboard"])
# app.include_router(retailer_inventory_api.router, tags=["Retailer Inventory"])
app.include_router(retailer_order_api.router, tags=["Retailer Orders"])
app.include_router(retailer_order_item_api.router, tags=["Retailer Order Items"])
app.include_router(customer_invoice_api.router, tags=["Retailer Invoices"])
# app.include_router(retailer_report_api.router, tags=["Retailer Reports"])
app.include_router(retailer_api.router, tags=["Retailer"])
app.include_router(retailer_notification_api.router, tags=["Retailer Notifications"])



# Distributor
app.include_router(distributor_api.router, tags=["Distributor"])
app.include_router(distributor_notification_api.router, tags=["Distributor Notification"])
# app.include_router(distributor_inventory_api.router, tags=["Distributor Inventory"])
# app.include_router(distributor_order_api.router, tags=["Distributor Orders"])
app.include_router(retailer_invoice_api.router, tags=["Distributor Invoices"])
app.include_router(distributor_report_api.router, tags=["Distributor Report"])
app.include_router(distributor_dashboard_api.router, tags=["Distributor Dashboard"])
app.include_router(pharma_order_api.router, tags=["Pharma Orders"])



