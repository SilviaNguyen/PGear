import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="PGear", layout="wide")

# --- CSS GIAO DIỆN DARK MODE (TEXT ONLY) ---
st.markdown("""
<style>
    /* --- 1. MÀU SẮC --- */
    :root {
        --bg-color: #0e1117;
        --card-bg: #1e252b;
        --primary: #29b5e8;         /* Xanh dương */
        --success: #00c853;         /* Xanh lá */
        --danger: #ff5252;          /* Đỏ */
        --text-sub: #9e9e9e;        /* Xám */
    }

    /* --- 2. CARD SẢN PHẨM --- */
    div.stContainer {
        background-color: var(--card-bg);
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }

    /* --- 3. INPUTS --- */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0e1117 !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 4px;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--primary) !important;
    }

    /* --- 4. METRICS --- */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: var(--primary) !important;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        color: var(--text-sub) !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* --- 5. BUTTONS --- */
    .stButton button {
        border-radius: 4px;
        font-weight: 600;
        border: none;
        text-transform: uppercase;
        font-size: 0.8rem;
    }
    .stButton button[type="primary"] {
        background-color: var(--primary) !important;
        color: #000 !important;
    }
    .stButton button[type="primary"]:hover {
        background-color: #0099cc !important;
        color: white !important;
    }
    .stButton button[type="secondary"] {
        background-color: #2d333b !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
    }
    
    /* Ẩn hướng dẫn input */
    div[data-testid="InputInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
DB_FILE = "gear_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            buy_price REAL,
            sell_price REAL,
            status TEXT,
            condition TEXT,
            warranty_info TEXT,
            date_added TEXT
        )
    ''')
    # Migration
    c.execute("PRAGMA table_info(products)")
    columns = [info[1] for info in c.fetchall()]
    if 'condition' not in columns:
        try:
            c.execute("ALTER TABLE products ADD COLUMN condition TEXT")
        except:
            pass
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM products ORDER BY id DESC", conn)
    conn.close()
    return df

def add_product(name, category, buy_price, sell_price, condition, warranty_info):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO products (name, category, buy_price, sell_price, status, condition, warranty_info, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, category, buy_price, sell_price, "Sẵn hàng", condition, warranty_info, date_added))
    conn.commit()
    conn.close()

def update_status(product_id, new_status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE products SET status = ? WHERE id = ?", (new_status, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

# --- MAIN ---
def main():
    init_db()
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("NHẬP KHO")
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("Tên sản phẩm", placeholder="VD: Chuột Logitech G Pro...")
            category = st.selectbox("Loại", ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"])
            
            c1, c2 = st.columns(2)
            buy = c1.number_input("Giá nhập", step=50000, format="%d")
            sell = c2.number_input("Giá bán", step=50000, format="%d")
            
            condition = st.text_input("Tình trạng", placeholder="VD: Fullbox, Nobox...")
            warranty = st.text_input("Bảo hành", placeholder="VD: 12T Hãng")
            
            if st.form_submit_button("LƯU SẢN PHẨM", type="primary"):
                if name:
                    cond_val = condition if condition else "---"
                    add_product(name, category, buy, sell, cond_val, warranty)
                    st.success("Đã thêm!")
                    st.rerun()

    # --- HEADER ---
    c_head_1, c_head_2 = st.columns([6, 1])
    with c_head_1:
        st.title("PGEAR MANAGER")
    with c_head_2:
        if st.button("REFRESH"):
            st.rerun()

    df = load_data()

    # --- METRICS ---
    if not df.empty:
        df['Lợi nhuận'] = df['sell_price'] - df['buy_price']
        inventory = df[df['status'] == 'Sẵn hàng']
        sold = df[df['status'] == 'Đã bán']
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("TỒN KHO", f"{len(inventory)}")
        m2.metric("VỐN TỒN", f"{inventory['buy_price'].sum():,.0f} đ")
        m3.metric("ĐÃ BÁN", f"{len(sold)}")
        profit = sold['Lợi nhuận'].sum()
        m4.metric("LỢI NHUẬN", f"{profit:,.0f} đ")
    
    st.divider()

    # --- FILTER ---
    c_search, c_filter = st.columns([3, 1])
    with c_search:
        search_query = st.text_input("", placeholder="Tìm kiếm tên sản phẩm...", label_visibility="collapsed").lower()
    with c_filter:
        view_filter = st.selectbox("", ["Tất cả", "Sẵn hàng", "Đã bán"], label_visibility="collapsed")

    # --- LIST ---
    if not df.empty:
        df_display = df.copy()
        if search_query:
            df_display = df_display[df_display['name'].str.lower().str.contains(search_query)]
        if view_filter != "Tất cả":
            df_display = df_display[df_display['status'] == view_filter]

        rows = [df_display.iloc[i:i + 3] for i in range(0, len(df_display), 3)]

        for row in rows:
            cols = st.columns(3)
            for col, item in zip(cols, row.iterrows()):
                item_data = item[1]
                with col:
                    with st.container():
                        # STATUS BADGE
                        is_sold = item_data['status'] == "Đã bán"
                        st_text = "ĐÃ BÁN" if is_sold else "SẴN HÀNG"
                        st_color = "#00c853" if is_sold else "#29b5e8"
                        
                        st.markdown(
                            f"""
                            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                                <span style="color:{st_color}; font-weight:bold; border:1px solid {st_color}; padding:2px 8px; border-radius:4px; font-size:0.7rem; letter-spacing: 1px;">
                                    {st_text}
                                </span>
                                <span style="color:#9e9e9e; font-size:0.7rem; text-transform:uppercase;">{item_data['category']}</span>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        # NAME
                        st.markdown(f"#### {item_data['name']}")
                        
                        # INFO ROW
                        cond_display = item_data['condition'] if item_data['condition'] else "---"
                        st.caption(f"Tình trạng: {cond_display}  |  BH: {item_data['warranty_info']}")

                        # --- PRICE SECTION (3 COLUMNS) ---
                        # Chia làm 3 cột rõ ràng: Nhập - Bán - Lãi
                        p1, p2, p3 = st.columns(3)
                        
                        with p1:
                            st.caption("GIÁ NHẬP")
                            st.markdown(f"**{item_data['buy_price']:,.0f}**")
                            
                        with p2:
                            st.caption("GIÁ BÁN")
                            st.markdown(f"**{item_data['sell_price']:,.0f}**")
                            
                        with p3:
                            st.caption("LỢI NHUẬN")
                            profit = item_data['sell_price'] - item_data['buy_price']
                            p_color = "#00c853" if profit > 0 else "#ff5252"
                            st.markdown(f"<span style='color:{p_color}; font-weight:bold'>{profit:+,.0f}</span>", unsafe_allow_html=True)

                        st.markdown("<div style='margin-top: 15px'></div>", unsafe_allow_html=True)
                        
                        # BUTTONS
                        b1, b2 = st.columns([2, 1])
                        if b1.button("HOÀN TÁC" if is_sold else "BÁN NGAY", key=f"btn_s_{item_data['id']}", type="secondary" if is_sold else "primary"):
                            update_status(item_data['id'], "Sẵn hàng" if is_sold else "Đã bán")
                            st.rerun()
                        
                        if b2.button("XÓA", key=f"btn_d_{item_data['id']}", type="secondary"):
                            delete_product(item_data['id'])
                            st.rerun()
    else:
        st.info("Chưa có dữ liệu.")

if __name__ == "__main__":
    main()