import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Phat Gear", layout="wide")

# --- CSS GIAO DIỆN (GIỮ NGUYÊN BẢN ĐẸP NHẤT) ---
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
    .stButton button[type="primary"] { background-color: var(--primary) !important; color: #000 !important; }
    .stButton button[type="secondary"] { background-color: #2d333b !important; color: #c9d1d9 !important; border: 1px solid #30363d !important; }
    div[data-testid="InputInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- KẾT NỐI GOOGLE SHEETS ---
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_NAME = "PhatGear_DB" # Đảm bảo tên file trên Google Drive đúng y hệt thế này

# Hàm kết nối (có cache để không phải kết nối lại liên tục)
@st.cache_resource
def connect_to_sheet():
    # Cách 1: Chạy Local (Dùng file json)
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        # Cách 2: Chạy trên Streamlit Cloud (Dùng Secrets)
        try:
            # Tạo dict từ secrets
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            client = gspread.authorize(creds)
            sheet = client.open(SHEET_NAME).sheet1
            return sheet
        except:
            st.error("Lỗi kết nối: Không tìm thấy file 'service_account.json' hoặc cấu hình Secrets.")
            st.stop()

def load_data():
    sheet = connect_to_sheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    # Nếu sheet trống, trả về dataframe rỗng với đúng cột
    if df.empty:
        return pd.DataFrame(columns=['id', 'name', 'category', 'buy_price', 'sell_price', 'status', 'condition', 'warranty_info', 'date_added'])
    
    # Sắp xếp ID giảm dần (Mới nhất lên đầu)
    if 'id' in df.columns:
        df = df.sort_values(by='id', ascending=False)
    return df

def add_product(name, category, buy_price, sell_price, condition, warranty_info):
    sheet = connect_to_sheet()
    data = sheet.get_all_records()
    
    # Tự động tạo ID mới (Max ID + 1)
    if not data:
        new_id = 1
    else:
        ids = [row['id'] for row in data if str(row['id']).isdigit()]
        new_id = max(ids) + 1 if ids else 1
        
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Thêm dòng mới vào sheet
    new_row = [new_id, name, category, buy_price, sell_price, "Sẵn hàng", condition, warranty_info, date_added]
    sheet.append_row(new_row)
    st.cache_data.clear() # Xóa cache để load lại dữ liệu mới

def update_status(product_id, new_status):
    sheet = connect_to_sheet()
    # Tìm dòng chứa ID (Lưu ý: Sheet tính dòng 1 là Header, nên +2 nếu tính index từ 0 của python tìm thấy)
    cell = sheet.find(str(product_id), in_column=1) 
    if cell:
        # Cập nhật cột Status (Cột thứ 6)
        sheet.update_cell(cell.row, 6, new_status)
        st.cache_data.clear()

def delete_product(product_id):
    sheet = connect_to_sheet()
    cell = sheet.find(str(product_id), in_column=1)
    if cell:
        sheet.delete_rows(cell.row)
        st.cache_data.clear()

# --- MAIN APP ---
def main():
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("NHẬP KHO")
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("Tên sản phẩm", placeholder="VD: Chuột Logitech...")
            category = st.selectbox("Loại", ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"])
            c1, c2 = st.columns(2)
            buy = c1.number_input("Giá nhập", step=50000, format="%d")
            sell = c2.number_input("Giá bán", step=50000, format="%d")
            condition = st.text_input("Tình trạng", placeholder="VD: Fullbox...")
            warranty = st.text_input("Bảo hành", placeholder="VD: 12T Hãng")
            
            if st.form_submit_button("LƯU SẢN PHẨM", type="primary"):
                if name:
                    cond_val = condition if condition else "---"
                    with st.spinner("Đang lưu lên mây..."):
                        add_product(name, category, buy, sell, cond_val, warranty)
                    st.success("Đã lưu thành công!")
                    st.rerun()

    # --- HEADER ---
    c_head_1, c_head_2 = st.columns([6, 1])
    with c_head_1:
        st.title("PGear")
    with c_head_2:
        if st.button("REFRESH"):
            st.cache_data.clear() # Xóa cache để ép tải lại từ Google Sheet
            st.rerun()

    df = load_data()

    # --- METRICS ---
    if not df.empty:
        # Đảm bảo cột giá là số (phòng khi nhập sai trên sheet)
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)
        df['sell_price'] = pd.to_numeric(df['sell_price'], errors='coerce').fillna(0)
        
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

    # --- SEARCH & LIST ---
    c_search, c_filter = st.columns([3, 1])
    with c_search:
        search_query = st.text_input("", placeholder="Tìm kiếm tên sản phẩm...", label_visibility="collapsed").lower()
    with c_filter:
        view_filter = st.selectbox("", ["Tất cả", "Sẵn hàng", "Đã bán"], label_visibility="collapsed")

    if not df.empty:
        df_display = df.copy()
        if search_query:
            df_display = df_display[df_display['name'].astype(str).str.lower().str.contains(search_query)]
        if view_filter != "Tất cả":
            df_display = df_display[df_display['status'] == view_filter]

        rows = [df_display.iloc[i:i + 3] for i in range(0, len(df_display), 3)]

        for row in rows:
            cols = st.columns(3)
            for col, item in zip(cols, row.iterrows()):
                item_data = item[1]
                with col:
                    with st.container(border=True):
                        # STATUS
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
                            with st.spinner("Đang cập nhật..."):
                                update_status(item_data['id'], "Sẵn hàng" if is_sold else "Đã bán")
                            st.rerun()
                        
                        if b2.button("XÓA", key=f"btn_d_{item_data['id']}", type="secondary"):
                            with st.spinner("Đang xóa..."):
                                delete_product(item_data['id'])
                            st.rerun()
    else:
        st.info("Empty")

if __name__ == "__main__":
    main()