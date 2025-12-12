import streamlit as st
import pandas as pd
import gspread
import os
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
from google.oauth2.credentials import Credentials as UserCredentials

# --- CẤU HÌNH ---
DRIVE_FOLDER_ID_RAW = "1qJD-JyJokrD5tRcp_AR6raVQAwnFNPuQ" 

st.set_page_config(page_title="PGear", layout="wide", initial_sidebar_state="collapsed")
url_fb = "https://www.facebook.com/thanh.phat.114166"
link_text = "Thanh Phat"

st.markdown("""
<style>
    .stApp { overflow-y: auto !important; height: 100vh; }
    :root { --primary: #29b5e8; --success: #00c853; --danger: #ff5252; --text-sub: #9e9e9e; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #1e252b; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { background-color: #0e1117 !important; color: white !important; border: 1px solid #30363d !important; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: var(--primary) !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { color: var(--text-sub) !important; font-size: 0.8rem !important; text-transform: uppercase; }
    .stButton button { border-radius: 4px; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; }
    section[data-testid="stSidebar"][aria-expanded="false"] { display: none; }
    div[data-testid="InputInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'show_login' not in st.session_state: st.session_state.show_login = False

# --- HÀM XỬ LÝ ID DRIVE THÔNG MINH ---
def get_clean_folder_id(raw_id):
    match = re.search(r'folders/([a-zA-Z0-9_-]+)', raw_id)
    if match:
        return match.group(1)
    if "?" in raw_id:
        return raw_id.split("?")[0]
    return raw_id.strip()

REAL_FOLDER_ID = get_clean_folder_id(DRIVE_FOLDER_ID_RAW)

# --- KẾT NỐI GOOGLE ---
@st.cache_resource
def get_credentials():
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    if os.path.exists('token.json'):
        return UserCredentials.from_authorized_user_file('token.json', SCOPES)
    
    elif "token_json" in st.secrets:
        import json
        token_info = json.loads(st.secrets["token_json"])
        return UserCredentials.from_authorized_user_info(token_info, SCOPES)
        
    else:
        st.error("Chưa có chứng chỉ xác thực (token.json). Hãy chạy file get_token.py trước!")
        st.stop()

def connect_to_sheet():
    creds = get_credentials()
    client = gspread.authorize(creds)
    return client.open("PhatGear_DB").sheet1

def upload_image_to_drive(image_file, product_name):
    if "PASTE" in REAL_FOLDER_ID:
        st.error("Bạn chưa điền ID Folder trong code!")
        return ""
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': f"{product_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            'parents': [REAL_FOLDER_ID]
        }
        
        media = MediaIoBaseUpload(image_file, mimetype=image_file.type, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        
        service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
        
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    except Exception as e:
        if "File not found" in str(e):
            st.error(f"Lỗi: Không tìm thấy thư mục ID: {REAL_FOLDER_ID}. Bạn đã Share quyền cho email trong JSON chưa?")
        else:
            st.error(f"Lỗi upload: {e}")
        return ""

# --- LOGIC DỮ LIỆU ---
def load_data():
    try:
        sheet = connect_to_sheet()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        required_cols = ['id', 'name', 'category', 'buy_price', 'sell_price', 'status', 'condition', 'warranty_info', 'date_added', 'image_url']
        if df.empty: return pd.DataFrame(columns=required_cols)
        
        for col in required_cols:
            if col not in df.columns: df[col] = ""
        
        if 'id' in df.columns: df = df.sort_values(by='id', ascending=False)
        return df
    except: return pd.DataFrame()

def add_product(name, category, buy_price, sell_price, condition, warranty_info, image_url):
    sheet = connect_to_sheet()
    data = sheet.get_all_records()
    ids = [row['id'] for row in data if str(row['id']).isdigit()]
    new_id = max(ids) + 1 if ids else 1
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([new_id, name, category, buy_price, sell_price, "Sẵn hàng", condition, warranty_info, date_added, image_url])
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
        if "admin_password" in st.secrets: return st.secrets["admin_password"]
        elif "general" in st.secrets: return st.secrets["general"].get("admin_password")
    except: pass
    return None

def update_product_full(p_id, name, category, buy, sell, condition, warranty, image_url):
    try:
        sheet = connect_to_sheet()
        cell = sheet.find(str(p_id), in_column=1)
        if cell:
            row_idx = cell.row
            sheet.update_cell(row_idx, 2, name)
            sheet.update_cell(row_idx, 3, category)
            sheet.update_cell(row_idx, 4, buy)
            sheet.update_cell(row_idx, 5, sell)
            sheet.update_cell(row_idx, 7, condition)
            sheet.update_cell(row_idx, 8, warranty)
            if image_url:
                sheet.update_cell(row_idx, 10, image_url)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Lỗi update: {e}")
        return False

# --- GIAO DIỆN CHÍNH ---
def main():
    c_head_1, c_head_2 = st.columns([6, 1])
    with c_head_1: st.title("PGEAR")
    
    df = load_data()

    c_search, c_filter = st.columns([3, 1])
    with c_search:
        search_query = st.text_input("", placeholder="Tìm kiếm...", label_visibility="collapsed", key="search_input", autocomplete="off")
    with c_filter:
        categories = ["Tất cả"] + sorted(df['category'].dropna().unique().tolist()) if not df.empty else ["Tất cả"]
        view_category = st.selectbox("", categories, label_visibility="collapsed")

    # LOGIN
    if search_query == "#login#":
        st.session_state.show_login = True
        search_query = ""
    
    if st.session_state.show_login and not st.session_state.is_admin:
        with st.expander("Hi Phát", expanded=True):
            password = st.text_input("", type="password")
            if st.button("Xác nhận"):
                correct_pass = get_admin_password()
                if correct_pass and password == correct_pass:
                    st.session_state.is_admin = True
                    st.session_state.show_login = False
                    st.rerun()
                else: st.error("Sai mật khẩu!")

    # ADMIN SIDEBAR
    if st.session_state.is_admin:
        with st.sidebar:
            if st.button("ĐĂNG XUẤT"):
                st.session_state.is_admin = False
                st.rerun()
            st.markdown("---")
            
            # Kiểm tra chế độ sửa hay thêm mới
            if 'edit_id' in st.session_state and st.session_state.edit_id:
                st.header(f"CẬP NHẬT: ID {st.session_state.edit_id}")
                
                edit_item = df[df['id'] == st.session_state.edit_id].iloc[0]
                
                with st.form("edit_form"):
                    e_name = st.text_input("Tên sản phẩm", value=edit_item['name'])
                    e_category = st.selectbox("Loại", ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"], 
                                             index=["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"].index(edit_item['category']) if edit_item['category'] in ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"] else 0)
                    
                    st.caption("Hình ảnh (Để trống nếu không đổi)")
                    e_uploaded_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed", key="e_img")
                    
                    c1, c2 = st.columns(2)
                    e_buy = c1.number_input("Giá nhập", step=50000, format="%d", value=int(edit_item['buy_price']) if edit_item['buy_price'] else 0)
                    e_sell = c2.number_input("Giá bán", step=50000, format="%d", value=int(edit_item['sell_price']) if edit_item['sell_price'] else 0)
                    e_condition = st.text_input("Tình trạng", value=edit_item['condition'])
                    e_warranty = st.text_input("Bảo hành", value=edit_item['warranty_info'])
                    
                    col_save, col_cancel = st.columns(2)
                    submitted = col_save.form_submit_button("LƯU", type="primary")
                    cancelled = col_cancel.form_submit_button("HỦY BỎ")

                    if cancelled:
                        del st.session_state.edit_id
                        st.rerun()
                    
                    if submitted:
                        with st.spinner("Đang cập nhật..."):
                            final_img = ""
                            if e_uploaded_file:
                                final_img = upload_image_to_drive(e_uploaded_file, e_name)
                            
                            update_product_full(st.session_state.edit_id, e_name, e_category, e_buy, e_sell, e_condition, e_warranty, final_img)
                        
                        st.success("Đã cập nhật!")
                        del st.session_state.edit_id
                        st.rerun()

            else:
                # FORM THÊM MỚI
                st.header("NHẬP KHO")
                with st.form("add_form", clear_on_submit=True):
                    name = st.text_input("Tên sản phẩm")
                    category = st.selectbox("Loại", ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"])
                    
                    st.caption("Hình ảnh (Google Drive)")
                    uploaded_file = st.file_uploader("", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
                    
                    c1, c2 = st.columns(2)
                    buy = c1.number_input("Giá nhập", step=50000, format="%d")
                    sell = c2.number_input("Giá bán", step=50000, format="%d")
                    condition = st.text_input("Tình trạng")
                    warranty = st.text_input("Bảo hành")
                    
                    if st.form_submit_button("LƯU SẢN PHẨM", type="primary"):
                        if name:
                            with st.spinner("Đang upload Drive & lưu..."):
                                final_img_url = ""
                                if uploaded_file:
                                    final_img_url = upload_image_to_drive(uploaded_file, name)
                                    if not final_img_url: st.stop()
                                
                                cond_val = condition if condition else "---"
                                add_product(name, category, buy, sell, cond_val, warranty, final_img_url)
                            st.success("Đã lưu!")
                            st.rerun()
                        else: st.warning("Thiếu tên sản phẩm!")

    # HIỂN THỊ DASHBOARD
    if not df.empty:
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)
        df['sell_price'] = pd.to_numeric(df['sell_price'], errors='coerce').fillna(0)
        inventory = df[df['status'] == 'Sẵn hàng']
        sold = df[df['status'] == 'Đã bán']
        
        if st.session_state.is_admin:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("KHO", f"{len(inventory)}")
            m2.metric("VỐN", f"{inventory['buy_price'].sum()/1000000:,.1f}M")
            m3.metric("ĐÃ BÁN", f"{len(sold)}")
            profit = (sold['sell_price'] - sold['buy_price']).sum()
            m4.metric("LÃI", f"{profit/1000000:,.1f}M")
        else:
            st.caption("Liên hệ mua hàng: **0931863070** (Zalo/Mess)")
            st.caption(f"Facebook: [{link_text}]({url_fb})")

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
                        c_info, c_img = st.columns([7, 3])
                        is_sold = item_data['status'] == "Đã bán"
                        st_text, st_color = ("ĐÃ BÁN", "#00c853") if is_sold else ("SẴN HÀNG", "#29b5e8")
                        
                        with c_info:
                            st.markdown(f"""
                                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                                    <span style="color:{st_color}; font-weight:bold; border:1px solid {st_color}; padding:2px 6px; border-radius:4px; font-size:0.6rem;">{st_text}</span>
                                    <span style="color:#9e9e9e; font-size:0.6rem; text-transform:uppercase;">{item_data['category']}</span>
                                </div>""", unsafe_allow_html=True)
                            st.markdown(f"<h4 style='margin:0; font-size:1rem; min-height:40px'>{item_data['name']}</h4>", unsafe_allow_html=True)
                            st.caption(f"BH: {item_data['warranty_info']} | {item_data['condition']}")

                        with c_img:
                            img_link = str(item_data['image_url']).strip()
                            if not img_link: img_link = "https://via.placeholder.com/150/1e252b/FFFFFF?text=PGEAR"
                            st.markdown(f"""
                                <div style="width:100%; padding-top:100%; background:url('{img_link}') center/cover no-repeat; border-radius:8px; border:1px solid #30363d;"></div>
                            """, unsafe_allow_html=True)

                        st.markdown("---")
                        if st.session_state.is_admin:
                            p1, p2, p3 = st.columns(3)
                            profit = item_data['sell_price'] - item_data['buy_price']
                            p_color = "#00c853" if profit > 0 else "#ff5252"
                            p1.markdown(f"<div style='font-size:0.8rem; color:#9e9e9e'>GỐC<br><b style='color:white'>{item_data['buy_price']/1000:,.0f}k</b></div>", unsafe_allow_html=True)
                            p2.markdown(f"<div style='font-size:0.8rem; color:#9e9e9e'>BÁN<br><b style='color:white'>{item_data['sell_price']/1000:,.0f}k</b></div>", unsafe_allow_html=True)
                            p3.markdown(f"<div style='font-size:0.8rem; color:#9e9e9e'>LÃI<br><b style='color:{p_color}'>{profit/1000:,.0f}k</b></div>", unsafe_allow_html=True)
                            
                            st.write("")
                            b1, b2, b3 = st.columns([1.5, 1, 1])
                            if b1.button("ĐỔI TT", key=f"s_{item_data['id']}", type="secondary" if is_sold else "primary", use_container_width=True):
                                update_status(item_data['id'], "Sẵn hàng" if is_sold else "Đã bán")
                                st.rerun()
                            if b2.button("SỬA", key=f"e_{item_data['id']}", type="secondary", use_container_width=True):
                                st.session_state.edit_id = item_data['id']
                                st.rerun()
                            if b3.button("XÓA", key=f"d_{item_data['id']}", type="secondary", use_container_width=True):
                                delete_product(item_data['id'])
                                st.rerun()
                        else:
                            c_price_1, c_price_2 = st.columns([1, 2])
                            c_price_1.caption("GIÁ")
                            c_price_2.markdown(f"<h3 style='color:#29b5e8; margin:0; text-align:right'>{item_data['sell_price']:,.0f}</h3>", unsafe_allow_html=True)
    else: 
        st.info("Chưa có dữ liệu.")

if __name__ == "__main__":
    main()