import streamlit as st
import pandas as pd
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(
    page_title="PGear", 
    layout="wide",
    initial_sidebar_state="collapsed"
)
url = "https://www.facebook.com/thanh.phat.114166"

link_text ="Thanh Phat"
st.markdown("""
<style>
    .stApp { overflow-y: auto !important; height: 100vh; }
    :root {
        --primary: #29b5e8; --success: #00c853; --danger: #ff5252; --text-sub: #9e9e9e;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e252b; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0e1117 !important; color: white !important; border: 1px solid #30363d !important;
    }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: var(--primary) !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { color: var(--text-sub) !important; font-size: 0.8rem !important; text-transform: uppercase; }
    .stButton button { border-radius: 4px; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; }
    
    /* ẨN NÚT MỞ SIDEBAR */
    section[data-testid="stSidebar"][aria-expanded="false"] { display: none; }
    div[data-testid="InputInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'show_login' not in st.session_state: st.session_state.show_login = False

@st.cache_resource
def connect_to_sheet():
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if os.path.exists("service_account.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
        elif "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        else:
            st.error("Lỗi cấu hình bảo mật.")
            st.stop()
        client = gspread.authorize(creds)
        return client.open("PhatGear_DB").sheet1
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
        st.stop()

def load_data():
    try:
        sheet = connect_to_sheet()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        required_cols = ['id', 'name', 'category', 'buy_price', 'sell_price', 'status', 'condition', 'warranty_info', 'date_added']
        if df.empty: return pd.DataFrame(columns=required_cols)
        if not all(col in df.columns for col in required_cols):
             missing = [c for c in required_cols if c not in df.columns]
             st.error(f"Lỗi cột Sheet: {missing}")
             st.stop()
        if 'id' in df.columns: df = df.sort_values(by='id', ascending=False)
        return df
    except: return pd.DataFrame()

def add_product(name, category, buy_price, sell_price, condition, warranty_info):
    sheet = connect_to_sheet()
    data = sheet.get_all_records()
    ids = [row['id'] for row in data if str(row['id']).isdigit()]
    new_id = max(ids) + 1 if ids else 1
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([new_id, name, category, buy_price, sell_price, "Sẵn hàng", condition, warranty_info, date_added])
    st.cache_data.clear()

def update_status(product_id, new_status):
    try:
        sheet = connect_to_sheet()
        cell = sheet.find(str(product_id), in_column=1) 
        if cell: sheet.update_cell(cell.row, 6, new_status)
        st.cache_data.clear()
    except: pass

def delete_product(product_id):
    try:
        sheet = connect_to_sheet()
        cell = sheet.find(str(product_id), in_column=1)
        if cell: sheet.delete_rows(cell.row)
        st.cache_data.clear()
    except: pass
def get_admin_password():
    try:
        if "admin_password" in st.secrets:
            return st.secrets["admin_password"]
        elif "general" in st.secrets and "admin_password" in st.secrets["general"]:
            return st.secrets["general"]["admin_password"]
        else:
            st.stop()
    except Exception as e:
        st.error(f"Lỗi đọc secrets: {e}")
        st.stop()
def main():
    c_head_1, c_head_2 = st.columns([6, 1])
    with c_head_1:
        st.title("PGEAR")

    df = load_data()

    c_search, c_filter = st.columns([3, 1])
    with c_search:
        search_query = st.text_input("", placeholder="Tìm kiếm sản phẩm...", label_visibility="collapsed",key="search_input", autocomplete="off")
    
    with c_filter:
        if not df.empty:
            categories = ["Tất cả"] + sorted(df['category'].dropna().unique().tolist())
        else:
            categories = ["Tất cả"]
            
        view_category = st.selectbox("", categories, label_visibility="collapsed")

    if search_query == "#login#":
        st.session_state.show_login = True
        search_query = ""

    if st.session_state.show_login and not st.session_state.is_admin:
        with st.expander("Hi Phát", expanded=True):
            password = st.text_input("", type="password")
            if st.button("Xác nhận"):
                correct_pass = get_admin_password()  
                if password == correct_pass:
                    st.session_state.is_admin = True
                    st.session_state.show_login = False
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Sai mật khẩu!")

    if st.session_state.is_admin:
        with st.sidebar:

            if st.button("ĐĂNG XUẤT"):
                st.session_state.is_admin = False
                st.rerun()
            st.markdown("---")
            st.header("NHẬP KHO")
            with st.form("add_form", clear_on_submit=True):
                name = st.text_input("Tên sản phẩm")
                category = st.selectbox("Loại", ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"])
                c1, c2 = st.columns(2)
                buy = c1.number_input("Giá nhập", step=50000, format="%d")
                sell = c2.number_input("Giá bán", step=50000, format="%d")
                condition = st.text_input("Tình trạng")
                warranty = st.text_input("Bảo hành")
                if st.form_submit_button("LƯU SẢN PHẨM", type="primary"):
                    if name:
                        cond_val = condition if condition else "---"
                        with st.spinner("Đang lưu..."):
                            add_product(name, category, buy, sell, cond_val, warranty)
                        st.success("Đã lưu!")
                        st.rerun()

    if not df.empty:
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)
        df['sell_price'] = pd.to_numeric(df['sell_price'], errors='coerce').fillna(0)
        df['Lợi nhuận'] = df['sell_price'] - df['buy_price']
        inventory = df[df['status'] == 'Sẵn hàng']
        sold = df[df['status'] == 'Đã bán']
        
        if st.session_state.is_admin:
            profit = sold['Lợi nhuận'].sum()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("TỒN KHO", f"{len(inventory)}")
            m2.metric("VỐN TỒN", f"{inventory['buy_price'].sum():,.0f} đ")
            m3.metric("ĐÃ BÁN", f"{len(sold)}")
            m4.metric("LỢI NHUẬN", f"{profit:,.0f} đ")
        else:
            m1, m2 = st.columns(2)
            st.caption("Liên hệ mua hàng: **0931863070** (Zalo/Mess)")
            st.caption(f"Facebook: [{link_text}]({url})")
    

    if not df.empty:
        df_display = df.copy()
        if search_query and search_query != "#login#":
            df_display = df_display[df_display['name'].astype(str).str.lower().str.contains(search_query.lower())]
        if view_category != "Tất cả":
            df_display = df_display[df_display['category'] == view_category]
        if not st.session_state.is_admin:
            df_display = df_display[df_display['status'] == 'Sẵn hàng']
        rows = [df_display.iloc[i:i + 3] for i in range(0, len(df_display), 3)]

        for row in rows:
            cols = st.columns(3)
            for col, item in zip(cols, row.iterrows()):
                item_data = item[1]
                with col:
                    with st.container(border=True):
                        is_sold = item_data['status'] == "Đã bán"
                        st_text = "ĐÃ BÁN" if is_sold else "SẴN HÀNG"
                        st_color = "#00c853" if is_sold else "#29b5e8"
                        
                        st.markdown(f"""
                            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                                <span style="color:{st_color}; font-weight:bold; border:1px solid {st_color}; padding:2px 8px; border-radius:4px; font-size:0.7rem; letter-spacing: 1px;">{st_text}</span>
                                <span style="color:#9e9e9e; font-size:0.7rem; text-transform:uppercase;">{item_data['category']}</span>
                            </div>""", unsafe_allow_html=True)
                        
                        st.markdown(f"#### {item_data['name']}")
                        cond_display = item_data['condition'] if item_data['condition'] else "---"
                        st.caption(f"Tình trạng: {cond_display}  |  BH: {item_data['warranty_info']}")
                        st.markdown("---")
                        if st.session_state.is_admin:
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
                            
                            b1, b2 = st.columns([2, 1])
                            if b1.button("HOÀN TÁC" if is_sold else "BÁN NGAY", key=f"btn_s_{item_data['id']}", type="secondary" if is_sold else "primary"):
                                with st.spinner("..."): update_status(item_data['id'], "Sẵn hàng" if is_sold else "Đã bán")
                                st.rerun()
                            if b2.button("XÓA", key=f"btn_d_{item_data['id']}", type="secondary"):
                                with st.spinner("..."): delete_product(item_data['id'])
                                st.rerun()
                        else:
                            st.caption("GIÁ BÁN")
                            st.markdown(f"<h3 style='color: #29b5e8; margin:0'>{item_data['sell_price']:,.0f} VNĐ</h3>", unsafe_allow_html=True)
                            
    else:
        st.info("Chưa có dữ liệu.")

if __name__ == "__main__":
    main()