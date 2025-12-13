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
        st.error("Chưa có chứng chỉ xác thực!")
        st.stop()

def connect_to_sheet():
    creds = get_credentials()
    client = gspread.authorize(creds)
    return client.open("PhatGear_DB").sheet1

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