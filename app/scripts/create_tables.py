import sqlite3
from sqlite3 import Connection

class TableCreator:
    def __init__(self, sqlite_url: str):
        # Parse file path from SQLAlchemy-style URL
        if sqlite_url.startswith("sqlite+aiosqlite:///"):
            self.db_file = sqlite_url.replace("sqlite+aiosqlite:///", "")
        else:
            raise ValueError("Invalid SQLite URL format")

    def get_connection(self) -> Connection:
        return sqlite3.connect(self.db_file)
    


    # ------------------------
    # Medicine Table
    # ------------------------
    def create_medicine_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Medicine (
            MedicineId INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            GenericName TEXT,
            DosageForm TEXT,
            Strength TEXT,
            Manufacturer TEXT,
            PrescriptionRequired BOOLEAN DEFAULT 0,
            Size TEXT,
            UnitPrice REAL NOT NULL,
            TherapeuticClass TEXT,
            ImgUrl TEXT,
            MedicineCategoryId INTEGER
        );
        """
        self._execute(sql, "Medicine")


    # Retailer Tables
    # ------------------------------------------------------------------
    # 1️⃣ Retailer
    # ------------------------------------------------------------------
    def create_retailer_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Retailer (
            RetailerId INTEGER PRIMARY KEY AUTOINCREMENT,
            ShopName TEXT,
            OwnerName TEXT,
            GSTNumber TEXT,
            LicenseNumber TEXT,
            PhoneNumber TEXT,
            Email TEXT,
            PasswordHash TEXT,
            AddressLine1 TEXT NOT NULL,
            AddressLine2 TEXT,
            City TEXT NOT NULL,
            State TEXT NOT NULL,
            Country TEXT NOT NULL,
            PostalCode TEXT NOT NULL,
            Latitude REAL,
            Longitude REAL,
            ShopPic TEXT,
            BankName TEXT,
            AccountNumber TEXT,
            IFSCCode TEXT,
            Branch TEXT
        );
        """
        self._execute(sql, "Retailer")


    # ------------------------------------------------------------------
    # 2️⃣ RetailerInventory
    # ------------------------------------------------------------------
    def create_retailer_inventory_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS RetailerInventory (
            RetailerInventoryId INTEGER PRIMARY KEY AUTOINCREMENT,
            RetailerId INTEGER NOT NULL,
            MedicineName TEXT NOT NULL,
            Brand TEXT,
            MinStock INTEGER,
            MaxStock INTEGER,
            Price REAL NOT NULL,
            Batch TEXT,
            ExpiryDate DATE,
            Status TEXT,
            Quantity INTEGER NOT NULL
        );
        """
        self._execute(sql, "RetailerInventory")

    # ------------------------------------------------------------------
    # 3️⃣ RetailerNotification
    # ------------------------------------------------------------------
    def create_retailer_notification_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS RetailerNotification (
            NotificationId INTEGER PRIMARY KEY AUTOINCREMENT,
            RetailerId INTEGER NOT NULL,
            Title TEXT NOT NULL,
            Message TEXT NOT NULL,
            Type TEXT NOT NULL,
            IsRead BOOLEAN DEFAULT 0,
            Date DATETIME DEFAULT CURRENT_TIMESTAMP,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        self._execute(sql, "RetailerNotification")

    # ------------------------------------------------------------------
    # 4️⃣ RetailerOrder + RetailerOrderItem
    # ------------------------------------------------------------------
    def create_retailer_order_tables(self):
        order_sql = """
        CREATE TABLE IF NOT EXISTS RetailerOrders (
            OrderId INTEGER PRIMARY KEY AUTOINCREMENT,
            RetailerId INTEGER NOT NULL,
            DistributorId INTEGER NOT NULL,
            OrderDateTime DATETIME DEFAULT CURRENT_TIMESTAMP,
            ExpectedDelivery DATETIME,
            DeliveryMode TEXT,
            DeliveryService TEXT,
            DeliveryPartnerTrackingId TEXT,
            DeliveryStatus TEXT DEFAULT 'Pending',
            PaymentMode TEXT,
            PaymentStatus TEXT DEFAULT 'Pending',
            PaymentTransactionId TEXT,
            Amount REAL DEFAULT 0.0,
            OrderStatus TEXT DEFAULT 'New',
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        item_sql = """
        CREATE TABLE IF NOT EXISTS RetailerOrderItem (
            ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderId INTEGER NOT NULL,
            RetailerId INTEGER NOT NULL,
            DistributorId INTEGER NOT NULL,
            MedicineId INTEGER NOT NULL,
            Quantity INTEGER NOT NULL,
            GSTPercentage REAL NOT NULL,
            TotalAmount REAL NOT NULL,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """

        self._execute(order_sql, "RetailerOrders")
        self._execute(item_sql, "RetailerOrderItem")



    # ------------------------------------------------------------------
    # 6️⃣ CustomerInvoice + CustomerInvoiceItem
    # ------------------------------------------------------------------
    def create_customer_invoice_tables(self):
        invoice_sql = """
        CREATE TABLE IF NOT EXISTS CustomerInvoice (
            InvoiceId INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderId INTEGER NOT NULL,
            RetailerId INTEGER NOT NULL,
            CustomerName TEXT NOT NULL,
            InvoiceDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            DueDate DATETIME,
            TotalAmount REAL,
            TaxAmount REAL DEFAULT 0.0,
            DiscountAmount REAL DEFAULT 0.0,
            NetAmount REAL,
            PaymentStatus TEXT DEFAULT 'Pending',
            PaymentMode TEXT,
            PaymentTransactionId TEXT,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            CreatedBy TEXT,
            UpdatedBy TEXT
        );
        """
        item_sql = """
        CREATE TABLE IF NOT EXISTS CustomerInvoiceItem (
            ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
            InvoiceId INTEGER NOT NULL,
            OrderId INTEGER NOT NULL,
            RetailerId INTEGER NOT NULL,
            MedicineName TEXT NOT NULL,
            Brand TEXT,
            Quantity INTEGER NOT NULL,
            Price REAL,
            TotalAmount REAL,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        self._execute(invoice_sql, "CustomerInvoice")
        self._execute(item_sql, "CustomerInvoiceItem")


    # ------------------------------------------------------------------
    # Distributor
    # ------------------------------------------------------------------
    def create_distributor_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Distributor (
            DistributorId INTEGER PRIMARY KEY AUTOINCREMENT,
            CompanyName TEXT,
            ContactPersonName TEXT,
            GSTNumber TEXT,
            LicenseNumber TEXT,
            PhoneNumber TEXT,
            Email TEXT,
            PasswordHash TEXT,

            -- Address fields (same as Retailer)
            AddressLine1 TEXT NOT NULL,
            AddressLine2 TEXT,
            City TEXT NOT NULL,
            State TEXT NOT NULL,
            Country TEXT NOT NULL,
            PostalCode TEXT NOT NULL,
            Latitude REAL,
            Longitude REAL,

            CompanyPicture TEXT,

            -- Banking info
            BankName TEXT,
            AccountNumber TEXT,
            IFSCCode TEXT,
            Branch TEXT
        );
        """
        self._execute(sql, "Distributor")


    # ------------------------------------------------------------------
    # DistributorInventory
    # ------------------------------------------------------------------
    def create_distributor_inventory_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS DistributorInventory (
            DistributorInventoryId INTEGER PRIMARY KEY AUTOINCREMENT,
            DistributorId INTEGER NOT NULL,
            MedicineName TEXT NOT NULL,
            Brand TEXT,
            MinStock INTEGER,
            MaxStock INTEGER,
            Price REAL NOT NULL,
            Batch TEXT,
            ExpiryDate DATE,
            Status TEXT,
            Quantity INTEGER NOT NULL
        );
        """
        self._execute(sql, "DistributorInventory")



    # ------------------------------------------------------------------
    # RetailerInvoice + RetailerInvoiceItem
    # ------------------------------------------------------------------
    def create_retailer_invoice_tables(self):
        invoice_sql = """
        CREATE TABLE IF NOT EXISTS RetailerInvoice (
            InvoiceId INTEGER PRIMARY KEY AUTOINCREMENT,
            OrderId INTEGER NOT NULL,
            DistributorId INTEGER NOT NULL,
            RetailerName TEXT NOT NULL,
            InvoiceDate DATETIME DEFAULT CURRENT_TIMESTAMP,
            DueDate DATETIME,
            TotalAmount REAL,
            TaxAmount REAL DEFAULT 0.0,
            DiscountAmount REAL DEFAULT 0.0,
            NetAmount REAL,
            PaymentStatus TEXT DEFAULT 'Pending',
            PaymentMode TEXT,
            PaymentTransactionId TEXT,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            UpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            CreatedBy TEXT,
            UpdatedBy TEXT
        );
        """
        item_sql = """
        CREATE TABLE IF NOT EXISTS RetailerInvoiceItem (
            ItemId INTEGER PRIMARY KEY AUTOINCREMENT,
            InvoiceId INTEGER NOT NULL,
            OrderId INTEGER NOT NULL,
            DistributorId INTEGER NOT NULL,
            MedicineName TEXT NOT NULL,
            Brand TEXT,
            Quantity INTEGER NOT NULL,
            Price REAL,
            TotalAmount REAL,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        self._execute(invoice_sql, "RetailerInvoice")
        self._execute(item_sql, "RetailerInvoiceItem")


    # ------------------------------------------------------------------
    # DistributorNotification
    # ------------------------------------------------------------------
    def create_distributor_notification_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS DistributorNotification (
            NotificationId INTEGER PRIMARY KEY AUTOINCREMENT,
            DistributorId INTEGER NOT NULL,
            Title TEXT NOT NULL,
            Message TEXT NOT NULL,
            Type TEXT NOT NULL,
            IsRead BOOLEAN DEFAULT 0,
            Date DATETIME DEFAULT CURRENT_TIMESTAMP,
            CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        self._execute(sql, "DistributorNotification")


    def add_column_if_not_exists(self, table: str, column: str, datatype: str):
        """
        Safely adds a new column to a table only if it does not already exist.
        Works for SQLite.
        """
        try:
            # 1. Get existing table schema
            schema_query = f"PRAGMA table_info({table});"
            columns = self._fetchall(schema_query)

            # 2. Check if column already exists
            existing_columns = [col[1] for col in columns]  # col[1] = column name

            if column in existing_columns:
                print(f"Column '{column}' already exists in table '{table}'. Skipping.")
                return

            # 3. Add new column
            alter_sql = f"ALTER TABLE {table} ADD COLUMN {column} {datatype};"
            self._execute(alter_sql, f"Add column {column}")

            print(f"Column '{column}' added successfully to '{table}'.")
        
        except Exception as e:
            print(f"Error adding column '{column}' to '{table}': {e}")

    def _fetchall(self, sql: str):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return []
        finally:
            conn.close()

    def remove_column_if_exists(self, table: str, column: str):
        """
        Removes a column from a SQLite table by rebuilding the table.
        Simplified version: copies all columns except the one to remove.
        """
        try:
            # 1. Get existing columns
            columns = [c[1] for c in self._fetchall(f"PRAGMA table_info({table});")]

            if column not in columns:
                print(f"Column '{column}' does not exist in '{table}'. Skipping.")
                return

            # Columns to keep
            keep_cols = [c for c in columns if c != column]
            cols_str = ", ".join(keep_cols)

            conn = self.get_connection()
            cur = conn.cursor()

            # 2. Read original CREATE TABLE statement
            cur.execute(f"""
                SELECT sql FROM sqlite_master
                WHERE type='table' AND name='{table}';
            """)
            create_sql = cur.fetchone()[0]

            # 3. Build new CREATE TABLE without the column definition
            inside = create_sql[create_sql.index("(")+1 : create_sql.rindex(")")]
            new_inside = ", ".join(
                part.strip()
                for part in inside.split(",")
                if not part.strip().startswith(column + " ")
            )
            new_create_sql = f"CREATE TABLE {table}_new ({new_inside});"

            # 4. Rebuild table
            cur.execute(new_create_sql)
            cur.execute(f"INSERT INTO {table}_new ({cols_str}) SELECT {cols_str} FROM {table};")
            cur.execute(f"DROP TABLE {table};")
            cur.execute(f"ALTER TABLE {table}_new RENAME TO {table};")

            conn.commit()

            print(f"Column '{column}' removed successfully from '{table}'.")

        except Exception as e:
            print(f"❌ Error removing column '{column}': {e}")

        finally:
            try:
                conn.close()
            except:
                pass

    def remove_table_if_exists(self, table: str):
        """
        Removes a table from the SQLite database if it exists.
        """
        conn = None
        try:
            conn = self.get_connection()
            cur = conn.cursor()

            # Check if table exists
            cur.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?;
            """, (table,))
            
            if not cur.fetchone():
                print(f"Table '{table}' does not exist. Skipping.")
                return

            # Drop table
            cur.execute(f"DROP TABLE {table};")
            conn.commit()

            print(f"Table '{table}' removed successfully.")

        except Exception as e:
            print(f"❌ Error removing table '{table}': {e}")

        finally:
            try:
                if conn:
                    conn.close()
            except:
                pass



    # ------------------------------------------------------------------
    # INTERNAL HELPER
    # ------------------------------------------------------------------
    def _execute(self, sql: str, table_name: str):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            print(f"✅ Table '{table_name}' created successfully!")
        except Exception as e:
            print(f"❌ Error creating table '{table_name}':", e)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # MAIN CREATION FUNCTION
    # ------------------------------------------------------------------
    def create_all_tables(self):       

        self.create_medicine_table()

        # Retailer tables
        self.create_retailer_table()
        # self.create_retailer_inventory_table()
        # self.create_retailer_notification_table()
        self.create_retailer_order_tables()
        self.create_customer_invoice_tables()


        # Distributor tables
        self.create_distributor_table()
        # self.create_distributor_inventory_table()
        # self.create_distributor_notification_table()
        self.create_retailer_invoice_tables()


        # self.add_column_if_not_exists("RetailerOrders", "RetailerName", "TEXT")
        # self.remove_column_if_exists("RetailerOrders", "DistributorrName")
        # self.remove_table_if_exists("Doctor")


        # tables = [
        #     "MedicineType", "MedicineCategory", "Medicine", "Customer", "Address", "Retailer",
        #     "Orders", "OrderItem", "RetailerNotification", "CustomerInvoice", "CustomerInvoiceItem",
        #     "RetailerOrders", "RetailerOrderItem", "Prescription", "CustomerNotification",
        #     "DistributorNotification", "RetailerInvoice", "RetailerInvoiceItem", "Lab",
        #     "Doctor", "MedicalFacility", "MedicalLab"
        # ]

        # for table in tables:
        #     self.remove_table_if_exists(table)





if __name__ == "__main__":
    sqlite_url = "sqlite+aiosqlite:///./medical.db"
    creator = TableCreator(sqlite_url)
    creator.create_all_tables()

