import streamlit as st
import pandas as pd
import gspread
import os
import re
from google.oauth2.credentials import Credentials as UserCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime

# --- CẤU HÌNH ---
DRIVE_FOLDER_ID_RAW = "1qJD-JyJokrD5tRcp_AR6raVQAwnFNPuQ"

def get_clean_folder_id(raw_id):
    match = re.search(r'folders/([a-zA-Z0-9_-]+)', raw_id)
    if match: return match.group(1)
    if "?" in raw_id: return raw_id.split("?")[0]
    return raw_id.strip()

REAL_FOLDER_ID = get_clean_folder_id(DRIVE_FOLDER_ID_RAW)

@st.cache_resource
def get_credentials():
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if os.path.exists('token.json'):
        return UserCredentials.from_authorized_user_file('token.json', SCOPES)
    elif "token_json" in st.secrets:
        import json
        token_info = json.loads(st.secrets["token_json"])
        return UserCredentials.from_authorized_user_info(token_info, SCOPES)
    else:
        st.error("Chưa có chứng chỉ xác thực! Vui lòng kiểm tra token.json hoặc secrets.")
        st.stop()

def connect_to_sheet():
    creds = get_credentials()
    client = gspread.authorize(creds)
    return client.open("PhatGear_DB").sheet1

# --- HÀM UPLOAD ẢNH (Đã tối ưu permission) ---
def upload_image_to_drive(image_file, product_name):
    if not REAL_FOLDER_ID or "PASTE" in REAL_FOLDER_ID:
        st.error("Chưa cấu hình Folder ID!")
        return ""
    try:
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': f"{product_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            'parents': [REAL_FOLDER_ID]
        }
        
        # Upload file
        media = MediaIoBaseUpload(image_file, mimetype=image_file.type, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        
        # CẤP QUYỀN TRUY CẬP (QUAN TRỌNG ĐỂ HIỆN ẢNH)
        service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
        
        # Trả về link Thumbnail chuẩn
        return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    except Exception as e:
        st.error(f"Lỗi upload ảnh: {e}")
        return ""

# --- CÁC HÀM XỬ LÝ DỮ LIỆU ---
def load_data():
    try:
        sheet = connect_to_sheet()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        # Định nghĩa đúng thứ tự cột để tránh lỗi
        required_cols = ['id', 'name', 'category', 'buy_price', 'sell_price', 'status', 'condition', 'warranty_info', 'date_added', 'image_url']
        if df.empty: return pd.DataFrame(columns=required_cols)
        
        for col in required_cols:
            if col not in df.columns: df[col] = ""
        
        if 'id' in df.columns: 
            df['id'] = pd.to_numeric(df['id'], errors='coerce')
            df = df.sort_values(by='id', ascending=False)
        return df
    except Exception as e:
        return pd.DataFrame()

def add_product(name, category, buy_price, sell_price, condition, warranty_info, image_url):
    sheet = connect_to_sheet()
    data = sheet.get_all_records()
    # Tìm ID lớn nhất để tăng tự động
    ids = [int(row['id']) for row in data if str(row['id']).isdigit()]
    new_id = max(ids) + 1 if ids else 1
    
    date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Lưu ý: Thứ tự này phải khớp với tiêu đề trong Google Sheet
    sheet.append_row([new_id, name, category, buy_price, sell_price, "Sẵn hàng", condition, warranty_info, date_added, image_url])
    st.cache_data.clear()

def find_cell_by_id(sheet, product_id):
    try:
        cell = sheet.find(str(product_id), in_column=1)
        return cell
    except:
        return None

def update_product_full(p_id, name, category, buy, sell, condition, warranty, image_url):
    try:
        sheet = connect_to_sheet()
        cell = find_cell_by_id(sheet, p_id)
        
        if cell:
            r = cell.row
            # --- CẬP NHẬT ĐÚNG CỘT (QUAN TRỌNG) ---
            # Cột 1: ID (Không sửa)
            sheet.update_cell(r, 2, name)          # Name
            sheet.update_cell(r, 3, category)      # Category
            sheet.update_cell(r, 4, int(buy) if buy else 0)   # Buy
            sheet.update_cell(r, 5, int(sell) if sell else 0) # Sell
            # Cột 6: Status (Không sửa ở đây)
            sheet.update_cell(r, 7, condition)     # Condition
            sheet.update_cell(r, 8, warranty)      # Warranty
            # Cột 9: Date (Không sửa)
            
            # Cột 10: Image URL (Chỉ update nếu có link mới)
            if image_url and image_url.strip() != "":
                sheet.update_cell(r, 10, image_url) # SỬA LẠI TỪ CỘT 8 THÀNH CỘT 10
                
            st.cache_data.clear()
            return True
        else:
            st.error(f"Không tìm thấy ID: {p_id}")
            return False
    except Exception as e:
        st.error(f"Lỗi khi lưu: {e}")
        return False

def update_status(product_id, new_status):
    try:
        sheet = connect_to_sheet()
        cell = find_cell_by_id(sheet, product_id)
        if cell: 
            sheet.update_cell(cell.row, 6, new_status) # Cột 6 là Status
            st.cache_data.clear()
    except Exception as e:
        st.error(f"Lỗi đổi trạng thái: {e}")

def delete_product(product_id):
    try:
        sheet = connect_to_sheet()
        cell = find_cell_by_id(sheet, product_id)
        if cell: 
            sheet.delete_rows(cell.row)
            st.cache_data.clear()
    except: pass

def get_admin_password():
    try:
        if "admin_password" in st.secrets: return st.secrets["admin_password"]
        elif "general" in st.secrets: return st.secrets["general"].get("admin_password")
    except: pass
    return None