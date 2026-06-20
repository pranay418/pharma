import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date

# ---------------- CONFIGURATION & SYSTEM THEME ----------------
st.set_page_config(
    page_title="Smart Pharmacy System",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DATABASE CONNECTION ----------------
conn = sqlite3.connect("pharmacy.db", check_same_thread=False)
cursor = conn.cursor()

# Create medicines table (with location column)
cursor.execute("""
CREATE TABLE IF NOT EXISTS medicines(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity INTEGER,
    price REAL,
    expiry_date TEXT,
    location TEXT
)
""")

# Create sales table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name TEXT,
    quantity INTEGER,
    total_price REAL,
    sale_date TEXT
)
""")
conn.commit()

# ---------------- CUSTOM CSS INJECTIONS ----------------
def inject_custom_css():
    st.markdown("""
        <style>
        /* Import premium font */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        
        /* Apply font family */
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        
        /* Modern Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: var(--secondary-background-color);
            border-right: 1px solid rgba(128, 128, 128, 0.1);
        }
        
        /* Glassmorphic KPI Cards */
        .kpi-card {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.15);
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
            margin-bottom: 20px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
            border-color: var(--primary-color);
        }
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background-color: var(--primary-color);
            border-radius: 4px 0 0 4px;
        }
        .kpi-title {
            font-size: 0.85rem;
            color: var(--text-color);
            opacity: 0.65;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-color);
            line-height: 1.2;
        }
        .kpi-sub {
            font-size: 0.78rem;
            color: var(--text-color);
            opacity: 0.5;
            margin-top: 4px;
        }
        
        /* Styled Buttons & Inputs */
        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
            padding: 0.55rem 1.1rem;
            transition: all 0.2s ease;
        }
        div.stButton > button:hover {
            transform: scale(1.01);
        }
        
        /* Tables & Dataframes styling */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(128, 128, 128, 0.15);
        }
        
        /* Alert Containers */
        div[data-testid="stAlert"] {
            border-radius: 12px;
            border: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        }
        
        /* Invoice/Receipt Style */
        .invoice-box {
            background-color: var(--secondary-background-color);
            border: 2px dashed rgba(128, 128, 128, 0.3);
            border-radius: 12px;
            padding: 28px;
            font-family: 'Courier New', Courier, monospace;
            margin-bottom: 25px;
            color: var(--text-color);
            max-width: 500px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }
        .invoice-title {
            text-align: center;
            font-weight: bold;
            font-size: 1.35rem;
            margin-bottom: 4px;
            letter-spacing: 1px;
        }
        .invoice-line {
            border-bottom: 1px dashed rgba(128, 128, 128, 0.3);
            margin: 8px 0;
        }
        .invoice-row {
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            font-size: 0.9rem;
        }
        
        /* Custom Header Brand logo */
        .logo-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            padding: 5px 10px;
        }
        .logo-icon {
            font-size: 2.2rem;
        }
        .logo-text {
            font-size: 1.6rem;
            font-weight: 800;
            background: linear-gradient(90deg, var(--primary-color), #00d285);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ---------------- AI PLACE PREDICTOR ----------------
def ai_place(medicine_name):
    name = medicine_name.lower()
    if any(x in name for x in ["paracetamol", "dolo", "crocin", "calpol"]):
        return "Drawer A1 - Fever"
    elif any(x in name for x in ["metformin", "insulin", "glimepiride", "gliclazide"]):
        return "Drawer B1 - Diabetes"
    elif any(x in name for x in ["ibuprofen", "diclofenac", "aspirin", "combiflam"]):
        return "Drawer A2 - Pain Relief"
    elif any(x in name for x in ["amoxicillin", "azithromycin", "cefixime", "ciprofloxacin"]):
        return "Drawer C1 - Antibiotics"
    elif any(x in name for x in ["cough", "koflet", "benadryl", "cetirizine"]):
        return "Drawer D2 - Cough & Cold"
    else:
        return "Drawer D1 - General"

# Disease Map for AI Recommendations
disease_map = {
    "fever": ["Paracetamol", "Dolo 650", "Crocin"],
    "diabetes": ["Metformin", "Insulin"],
    "pain": ["Ibuprofen", "Aspirin"],
    "infection": ["Amoxicillin", "Azithromycin"]
}

# ---------------- SIDEBAR NAVIGATION ----------------
st.sidebar.markdown("""
    <div class="logo-container">
        <span class="logo-icon">💊</span>
        <span class="logo-text">PharmaSmart</span>
    </div>
""", unsafe_allow_html=True)

# Handle dynamic menu redirections (e.g. from Disease AI to Register)
default_menu_idx = 0
if "menu_selection" in st.session_state:
    menu_options = [
        "Dashboard",
        "Add Medicine",
        "View Medicines",
        "Billing System",
        "Daily Reports",
        "Sales History",
        "Disease AI Assistant"
    ]
    if st.session_state["menu_selection"] in menu_options:
        default_menu_idx = menu_options.index(st.session_state["menu_selection"])
    # Delete redirection key so it doesn't lock navigation
    del st.session_state["menu_selection"]

menu = st.sidebar.selectbox(
    "Navigation Menu",
    [
        "Dashboard",
        "Add Medicine",
        "View Medicines",
        "Billing System",
        "Daily Reports",
        "Sales History",
        "Disease AI Assistant"
    ],
    index=default_menu_idx
)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.title("📊 Pharmacy Dashboard")
    
    # Query database
    df_meds = pd.read_sql_query("SELECT * FROM medicines", conn)
    df_sales = pd.read_sql_query("SELECT * FROM sales", conn)
    
    # Calculate stats
    today_str = str(date.today())
    df_sales_today = df_sales[df_sales["sale_date"] == today_str] if len(df_sales) > 0 else pd.DataFrame()
    revenue_today = df_sales_today["total_price"].sum() if len(df_sales_today) > 0 else 0.0
    items_sold_today = df_sales_today["quantity"].sum() if len(df_sales_today) > 0 else 0
    
    total_meds = len(df_meds)
    total_qty = df_meds["quantity"].sum() if total_meds > 0 else 0
    low_stock_count = len(df_meds[df_meds["quantity"] < 10]) if total_meds > 0 else 0
    
    # Render KPI Cards in a wide layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">📦 Total Medicines</div>
                <div class="kpi-value">{total_meds}</div>
                <div class="kpi-sub">Unique items registered</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">🔢 Total Stock Units</div>
                <div class="kpi-value">{total_qty}</div>
                <div class="kpi-sub">Physical quantity in warehouse</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        sub_text = "Action required" if low_stock_count > 0 else "All stocks healthy"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">⚠️ Low Stock Alerts</div>
                <div class="kpi-value" style="color: {'#FF4B4B' if low_stock_count > 0 else 'inherit'};">{low_stock_count}</div>
                <div class="kpi-sub">{sub_text} (Stock &lt; 10)</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">💰 Today's Revenue</div>
                <div class="kpi-value">₹{revenue_today:,.2f}</div>
                <div class="kpi-sub">{items_sold_today} items sold today</div>
            </div>
        """, unsafe_allow_html=True)

    # Main dashboard view splitting low stock and sales history charts
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("⚠️ Low Stock Items")
        if total_meds > 0:
            low_stock_df = df_meds[df_meds["quantity"] < 10]
            if len(low_stock_df) > 0:
                st.dataframe(
                    low_stock_df[["id", "name", "quantity", "price", "location", "expiry_date"]], 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.success("✅ Stock levels are healthy across all products!")
        else:
            st.info("No medicines added yet.")
            
    with col_right:
        st.subheader("📈 Top-Selling Medicines")
        if len(df_sales) > 0:
            top_meds = df_sales.groupby("medicine_name")["quantity"].sum().reset_index()
            top_meds = top_meds.sort_values(by="quantity", ascending=False).head(10)
            st.bar_chart(data=top_meds, x="medicine_name", y="quantity", use_container_width=True)
        else:
            st.info("No sales data available to plot charts.")

# ---------------- ADD MEDICINE ----------------
elif menu == "Add Medicine":
    st.title("➕ Add Medicine to Inventory")
    
    # Pre-fill verification (if coming from AI search helper)
    prefill_name = ""
    prefill_loc = ""
    if "add_med_prefill_name" in st.session_state:
        prefill_name = st.session_state["add_med_prefill_name"]
        prefill_loc = st.session_state["add_med_prefill_loc"]
        # Clear pre-fill inputs so they don't persist on page switch
        del st.session_state["add_med_prefill_name"]
        del st.session_state["add_med_prefill_loc"]
        
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Medicine Name", value=prefill_name, placeholder="e.g. Paracetamol, Metformin...")
        
    # Dynamically compute suggested location based on current typed name
    recommended_loc = prefill_loc if prefill_loc else (ai_place(name) if name else "")
    
    with col2:
        location = st.text_input(
            "Storage Location (AI Predicted/Editable)", 
            value=recommended_loc, 
            help="AI assigns default drawer based on drug category. Feel free to customize."
        )
        
    col3, col4, col5 = st.columns(3)
    with col3:
        quantity = st.number_input("Quantity", min_value=0, step=1, value=50)
    with col4:
        price = st.number_input("Price (₹)", min_value=0.0, step=0.5, value=10.0)
    with col5:
        expiry = st.date_input("Expiry Date", min_value=date.today())
        
    if st.button("💾 Add Medicine", type="primary", use_container_width=True):
        if not name.strip():
            st.error("Medicine Name cannot be empty.")
        else:
            cursor.execute(
                """
                INSERT INTO medicines
                (name, quantity, price, expiry_date, location)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name.strip(), quantity, price, str(expiry), location.strip())
            )
            conn.commit()
            st.success(f"🎉 '{name}' successfully added to database at location '{location}'!")

# ---------------- VIEW MEDICINES ----------------
elif menu == "View Medicines":
    st.title("📦 Inventory Management")
    
    df = pd.read_sql_query("SELECT * FROM medicines", conn)
    if not df.empty and "expiry_date" in df.columns:
        df["expiry_date"] = pd.to_datetime(df["expiry_date"], errors="coerce").dt.date
    
    tab1, tab2, tab3 = st.tabs([
        "📋 Interactive Spreadsheet Editor", 
        "✏️ Manual Edit Form", 
        "🗑 Delete Medicine"
    ])
    
    with tab1:
        st.markdown("### Bulk Spreadsheet Editor")
        st.info("💡 Edit cells directly in the table below, append new rows at the bottom, or select rows and press Delete on your keyboard. Click 'Save Changes' to apply updates.")
        
        # Configure columns inside spreadsheet editor
        edited_df = st.data_editor(
            df,
            key="inv_editor",
            use_container_width=True,
            num_rows="dynamic",
            disabled=["id"],
            column_config={
                "id": st.column_config.NumberColumn("ID", disabled=True),
                "name": st.column_config.TextColumn("Medicine Name", required=True),
                "quantity": st.column_config.NumberColumn("Quantity", min_value=0, step=1, required=True),
                "price": st.column_config.NumberColumn("Price (₹)", min_value=0.0, step=0.1, required=True),
                "expiry_date": st.column_config.DateColumn("Expiry Date", required=True),
                "location": st.column_config.TextColumn("Storage Location")
            }
        )
        
        if st.button("💾 Save All Spreadsheet Changes", type="primary", use_container_width=True):
            state = st.session_state.inv_editor
            
            # Apply edits
            for idx, changes in state["edited_rows"].items():
                db_id = int(df.loc[int(idx), "id"])
                for col, val in changes.items():
                    if col == "expiry_date" and val is not None:
                        val = str(val)
                    cursor.execute(f"UPDATE medicines SET {col} = ? WHERE id = ?", (val, db_id))
            
            # Apply deletions
            for idx in state["deleted_rows"]:
                db_id = int(df.loc[int(idx), "id"])
                cursor.execute("DELETE FROM medicines WHERE id = ?", (db_id,))
                
            # Apply additions
            for row in state["added_rows"]:
                name = row.get("name", "New Medicine")
                qty = row.get("quantity", 0)
                prc = row.get("price", 0.0)
                exp = str(row.get("expiry_date", str(date.today())))
                loc = row.get("location", ai_place(name))
                cursor.execute("""
                    INSERT INTO medicines (name, quantity, price, expiry_date, location)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, qty, prc, exp, loc))
                
            conn.commit()
            st.success("All spreadsheet changes saved successfully!")
            st.rerun()
            
    with tab2:
        st.markdown("### Edit Medicine Form")
        if len(df) == 0:
            st.warning("Inventory is currently empty.")
        else:
            med_list = df["name"].tolist()
            selected_med = st.selectbox("Select Medicine to Edit", med_list, key="edit_selector")
            
            # Fetch data of the selected medicine
            med_row = df[df["name"] == selected_med].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                edit_name = st.text_input("Medicine Name", value=med_row["name"])
                edit_qty = st.number_input("Quantity", min_value=0, step=1, value=int(med_row["quantity"]))
            with col2:
                exp_date = med_row["expiry_date"]
                if not isinstance(exp_date, (datetime, date)) or pd.isna(exp_date):
                    try:
                        exp_date = datetime.strptime(str(exp_date), "%Y-%m-%d").date()
                    except:
                        exp_date = date.today()
                edit_expiry = st.date_input("Expiry Date", value=exp_date, key="edit_exp")
                edit_price = st.number_input("Price (₹)", min_value=0.0, step=0.1, value=float(med_row["price"]))
                
            edit_loc = st.text_input("Storage Location", value=str(med_row["location"] or ""))
            
            if st.button("💾 Update Details", use_container_width=True):
                cursor.execute("""
                    UPDATE medicines
                    SET name = ?, quantity = ?, price = ?, expiry_date = ?, location = ?
                    WHERE id = ?
                """, (edit_name, edit_qty, edit_price, str(edit_expiry), edit_loc, int(med_row["id"])))
                conn.commit()
                st.success(f"Medicine '{edit_name}' updated successfully!")
                st.rerun()
                
    with tab3:
        st.markdown("### Remove Medicine from Inventory")
        if len(df) == 0:
            st.warning("Inventory is empty.")
        else:
            del_list = df["name"].tolist()
            selected_del = st.selectbox("Select Medicine to Delete", del_list, key="del_selector")
            del_row = df[df["name"] == selected_del].iloc[0]
            
            st.warning(f"Are you sure you want to permanently delete **{selected_del}**?")
            if st.button("🗑 Delete Medicine Record", type="primary", use_container_width=True):
                cursor.execute("DELETE FROM medicines WHERE id = ?", (int(del_row["id"]),))
                conn.commit()
                st.success(f"Medicine '{selected_del}' deleted successfully!")
                st.rerun()

# ---------------- BILLING SYSTEM (CART-BASED) ----------------
elif menu == "Billing System":
    st.title("💳 Smart Billing System")
    
    # Initialize checkout session state cart
    if "cart" not in st.session_state:
        st.session_state["cart"] = []
        
    # Display receipt block if a checkout completed recently
    if "last_receipt" in st.session_state:
        receipt = st.session_state["last_receipt"]
        st.subheader("🧾 Invoice Generated")
        
        # Styled terminal invoice HTML
        receipt_html = f"""
        <div class="invoice-box">
            <div class="invoice-title">💊 PHARMASMART</div>
            <div style="text-align: center; font-size: 0.75rem; opacity: 0.8; margin-bottom: 10px;">
                INVOICE RECEIPT
            </div>
            <div class="invoice-line"></div>
            <div class="invoice-row">
                <span>Date & Time:</span>
                <span>{receipt['date']}</span>
            </div>
            <div class="invoice-line"></div>
            <div class="invoice-row" style="font-weight: bold; padding-bottom: 5px;">
                <span style="flex: 2;">Item Name</span>
                <span style="flex: 1; text-align: right;">Qty</span>
                <span style="flex: 1; text-align: right;">Unit</span>
                <span style="flex: 1; text-align: right;">Total</span>
            </div>
        """
        for item in receipt["items"]:
            receipt_html += f"""
            <div class="invoice-row">
                <span style="flex: 2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{item['name']}</span>
                <span style="flex: 1; text-align: right;">{item['quantity']}</span>
                <span style="flex: 1; text-align: right;">₹{item['price']}</span>
                <span style="flex: 1; text-align: right;">₹{item['total']}</span>
            </div>
            """
        receipt_html += f"""
            <div class="invoice-line"></div>
            <div class="invoice-row" style="font-weight: bold; font-size: 1.15rem; margin-top: 8px;">
                <span>GRAND TOTAL:</span>
                <span>₹{receipt['total']:,.2f}</span>
            </div>
            <div class="invoice-line"></div>
            <div style="text-align: center; font-size: 0.75rem; margin-top: 15px; line-height: 1.4;">
                Thank you for your visit!<br>
                Take medicines as prescribed. Get well soon! ❤️
            </div>
        </div>
        """
        st.markdown(receipt_html, unsafe_allow_html=True)
        if st.button("❌ Close Invoice & Start New Billing", use_container_width=True):
            del st.session_state["last_receipt"]
            st.rerun()
            
    # Regular billing setup
    df_instock = pd.read_sql_query("SELECT * FROM medicines WHERE quantity > 0", conn)
    
    if len(df_instock) == 0:
        st.warning("⚠️ No medicines currently in stock.")
    else:
        col_form, col_cart = st.columns([2, 3])
        
        with col_form:
            st.subheader("🛒 Add to Bill")
            med_options = df_instock["name"].tolist()
            selected_med = st.selectbox("Select Medicine", med_options)
            
            # Fetch inventory details
            med_details = df_instock[df_instock["name"] == selected_med].iloc[0]
            max_qty = int(med_details["quantity"])
            price = float(med_details["price"])
            loc = med_details["location"] or "Unassigned"
            
            # Calculate remaining stock based on cart inclusions
            in_cart_qty = sum(item["quantity"] for item in st.session_state["cart"] if item["name"] == selected_med)
            remaining_stock = max_qty - in_cart_qty
            
            st.info(f"ℹ️ **Inventory Specs:**\n- **Stock Available:** {max_qty} units\n- **Storage Location:** {loc}\n- **Price per unit:** ₹{price}")
            
            if remaining_stock <= 0:
                st.error("⚠️ All in-stock units are already in the billing cart.")
                qty_input = st.number_input("Quantity to Sell", min_value=0, max_value=0, value=0, disabled=True)
                btn_add = st.button("🛒 Add to Cart", disabled=True, use_container_width=True)
            else:
                qty_input = st.number_input("Quantity to Sell", min_value=1, max_value=remaining_stock, value=1, step=1)
                btn_add = st.button("🛒 Add to Cart", use_container_width=True)
                
                if btn_add:
                    # Search if item exists in cart
                    found = False
                    for item in st.session_state["cart"]:
                        if item["name"] == selected_med:
                            item["quantity"] += qty_input
                            item["total"] = item["quantity"] * item["price"]
                            found = True
                            break
                    if not found:
                        st.session_state["cart"].append({
                            "name": selected_med,
                            "price": price,
                            "quantity": qty_input,
                            "total": qty_input * price
                        })
                    st.success(f"Added {qty_input}x '{selected_med}' to cart!")
                    st.rerun()
                    
        with col_cart:
            st.subheader("📋 Billing Items")
            if len(st.session_state["cart"]) == 0:
                st.info("No items in cart yet. Add medicines from the left form.")
            else:
                cart_df = pd.DataFrame(st.session_state["cart"])
                cart_df.index = cart_df.index + 1
                st.dataframe(cart_df[["name", "price", "quantity", "total"]], use_container_width=True)
                
                grand_total = cart_df["total"].sum()
                st.markdown(f"### 💵 Grand Total: **₹{grand_total:,.2f}**")
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("🗑 Clear Cart", use_container_width=True):
                        st.session_state["cart"] = []
                        st.rerun()
                with col_c2:
                    if st.button("💳 Confirm Checkout & Print", type="primary", use_container_width=True):
                        checkout_valid = True
                        
                        # Double-check database quantities to prevent race condition
                        for item in st.session_state["cart"]:
                            cursor.execute("SELECT quantity FROM medicines WHERE name = ?", (item["name"],))
                            row = cursor.fetchone()
                            if not row or row[0] < item["quantity"]:
                                st.error(f"Cannot complete checkout. '{item['name']}' stock fell below quantity requested.")
                                checkout_valid = False
                                break
                                
                        if checkout_valid:
                            today = str(date.today())
                            sale_items = list(st.session_state["cart"])
                            
                            for item in sale_items:
                                # Decrease inventory quantity
                                cursor.execute("""
                                    UPDATE medicines
                                    SET quantity = quantity - ?
                                    WHERE name = ?
                                """, (item["quantity"], item["name"]))
                                
                                # Insert sales records
                                cursor.execute("""
                                    INSERT INTO sales (medicine_name, quantity, total_price, sale_date)
                                    VALUES (?, ?, ?, ?)
                                """, (item["name"], item["quantity"], item["total"], today))
                                
                            conn.commit()
                            
                            # Cache receipt info & clean cart
                            st.session_state["last_receipt"] = {
                                "items": sale_items,
                                "total": grand_total,
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            st.session_state["cart"] = []
                            st.success("Checkout Successful!")
                            st.rerun()

# ---------------- DAILY REPORTS ----------------
elif menu == "Daily Reports":
    st.title("📊 Pharmacy Sales Reports")
    
    col_sel, _ = st.columns([2, 2])
    with col_sel:
        selected_date = st.date_input("Select Report Date", date.today())
        
    df_sales = pd.read_sql_query("SELECT * FROM sales", conn)
    
    if len(df_sales) == 0:
        st.info("No sales data is currently recorded in the system.")
    else:
        date_str = str(selected_date)
        day_sales = df_sales[df_sales["sale_date"] == date_str]
        
        revenue = day_sales["total_price"].sum() if len(day_sales) > 0 else 0.0
        items = day_sales["quantity"].sum() if len(day_sales) > 0 else 0
        transactions = len(day_sales)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Revenue", f"₹{revenue:,.2f}")
        with col2:
            st.metric("Total Units Sold", items)
        with col3:
            st.metric("Transactions Count", transactions)
            
        if len(day_sales) > 0:
            st.subheader(f"Transactions on {selected_date}")
            st.dataframe(day_sales[["id", "medicine_name", "quantity", "total_price"]], use_container_width=True, hide_index=True)
            
            st.subheader("Sales Volume by Medicine")
            chart_df = day_sales.groupby("medicine_name")["quantity"].sum().reset_index()
            st.bar_chart(data=chart_df, x="medicine_name", y="quantity", use_container_width=True)
        else:
            st.warning(f"No sales transaction data recorded on {selected_date}.")

# ---------------- SALES HISTORY ----------------
elif menu == "Sales History":
    st.title("🧾 Historical Sales Log")
    
    df_sales = pd.read_sql_query("SELECT * FROM sales ORDER BY id DESC", conn)
    
    if len(df_sales) == 0:
        st.info("No transaction history recorded yet.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            med_filter = st.multiselect("Filter by Medicine Name", options=sorted(df_sales["medicine_name"].unique()))
        with col2:
            date_filter = st.multiselect("Filter by Sale Date", options=sorted(df_sales["sale_date"].unique(), reverse=True))
            
        filtered_df = df_sales
        if med_filter:
            filtered_df = filtered_df[filtered_df["medicine_name"].isin(med_filter)]
        if date_filter:
            filtered_df = filtered_df[filtered_df["sale_date"].isin(date_filter)]
            
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        # Download log link
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Log to CSV",
            data=csv_data,
            file_name=f"sales_log_{date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ---------------- DISEASE AI ASSISTANT ----------------
elif menu == "Disease AI Assistant":
    st.title("🧠 Smart Disease AI Assistant")
    st.markdown("Search for symptoms/diseases to view recommended medications, verify live warehouse stock, locate drawers, and add recommended items to the active billing cart.")
    
    disease = st.text_input("Enter Disease (e.g. fever, diabetes, pain, infection)", placeholder="Type symptom/disease...")
    
    if disease:
        disease = disease.strip().lower()
        if disease in disease_map:
            st.success(f"Recommended Medicines for '{disease.capitalize()}':")
            
            meds_recommended = disease_map[disease]
            db_meds = pd.read_sql_query("SELECT * FROM medicines", conn)
            
            for med in meds_recommended:
                st.markdown("---")
                
                # Check case-insensitive match in database
                match = db_meds[db_meds["name"].str.lower() == med.lower()] if len(db_meds) > 0 else pd.DataFrame()
                
                col_info, col_btn = st.columns([3, 1])
                
                if len(match) > 0:
                    med_data = match.iloc[0]
                    qty = int(med_data["quantity"])
                    price = float(med_data["price"])
                    loc = med_data["location"] or "Unassigned"
                    
                    with col_info:
                        st.markdown(f"#### 💊 {med_data['name']}")
                        if qty > 0:
                            st.markdown(f"🟢 **In Stock** | Units Available: **{qty}** | Price: **₹{price}** | Storage: **{loc}**")
                        else:
                            st.markdown(f"🔴 **Out of Stock** | Price: **₹{price}** | Storage: **{loc}**")
                            
                    with col_btn:
                        if qty > 0:
                            # Direct add-to-cart button integration
                            if st.button("🛒 Quick Add to Cart", key=f"ai_add_{med_data['id']}", use_container_width=True):
                                if "cart" not in st.session_state:
                                    st.session_state["cart"] = []
                                    
                                found = False
                                for item in st.session_state["cart"]:
                                    if item["name"] == med_data["name"]:
                                        if item["quantity"] + 1 <= qty:
                                            item["quantity"] += 1
                                            item["total"] = item["quantity"] * item["price"]
                                            st.success(f"Added another unit of {med_data['name']}!")
                                        else:
                                            st.error("Cannot add. Exceeds stock limit.")
                                        found = True
                                        break
                                if not found:
                                    st.session_state["cart"].append({
                                        "name": med_data["name"],
                                        "price": price,
                                        "quantity": 1,
                                        "total": price
                                    })
                                    st.success(f"Added 1x {med_data['name']} to cart!")
                                st.rerun()
                        else:
                            st.button("🚫 Out of Stock", key=f"ai_oos_{med_data['id']}", disabled=True, use_container_width=True)
                else:
                    with col_info:
                        st.markdown(f"#### 💊 {med}")
                        st.markdown("⚪ **Not Registered** | This recommended medicine is not currently registered in the database inventory.")
                    with col_btn:
                        if st.button("➕ Register Item", key=f"ai_reg_{med}", use_container_width=True):
                            st.session_state["add_med_prefill_name"] = med
                            st.session_state["add_med_prefill_loc"] = ai_place(med)
                            st.session_state["menu_selection"] = "Add Medicine"
                            st.rerun()
        else:
            st.warning("⚠️ No AI recommendation data available for this disease. Try 'fever', 'diabetes', 'pain', or 'infection'.")
