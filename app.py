import streamlit as st
import pandas as pd
import backend as db  
import styles
import base64
import os
import time
from datetime import datetime

st.set_page_config(page_title="PGear", layout="wide")
st.markdown(styles.CSS, unsafe_allow_html=True)

if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'show_login' not in st.session_state: st.session_state.show_login = False
if 'search_term' not in st.session_state: st.session_state.search_term = ""
if 'selected_category' not in st.session_state: st.session_state.selected_category = "Trang chủ"

if 'master_df' not in st.session_state:
    st.session_state.master_df = db.fetch_data_from_sheet()

def force_refresh_data():
    st.session_state.master_df = db.fetch_data_from_sheet()
    st.toast("Da cap nhat du lieu tu Sheet")

BANNER_MAP = {
    "Trang chủ": {"img": "images/pgear.jpg", "title": "PGEAR", "sub": ""},
    "Tất cả":   {"img": "images/banner_main.jpg", "title": "ALL PRODUCTS", "sub": ""},
    "Chuột":    {"img": "images/banner_mouse.jpg", "title": "GAMING MOUSE", "sub": "precision"},
    "Bàn phím": {"img": "images/banner_keyboard.jpg", "title": "KEYBOARD", "sub": "performance"},
    "Tai nghe": {"img": "images/banner_audio.jpg", "title": "AUDIO", "sub": "sound"},
    "Lót chuột": {"img": "images/banner_pad.jpg", "title": "MOUSEPAD", "sub": "glide"},
    "Khác":     {"img": "images/banner_accessories.jpg", "title": "ACCESSORIES", "sub": "support"}
}

def get_base64_image(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

def render_banner(img_file, title, subtitle):
    bin_str = get_base64_image(img_file)
    img_url = f"data:image/jpeg;base64,{bin_str}" if bin_str else "https://via.placeholder.com/1200x400"
    st.markdown(f"""
        <div class="hero-box" style="background-image: url('{img_url}');">
            <div class="hero-overlay">
                <div class="hero-title">{title}</div>
                <div class="hero-subtitle">{subtitle}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

@st.dialog("Thông tin sản phẩm", width="small")
def show_product_detail(item):
    raw_img = str(item.get('image_url', '')).strip()
    img_url = raw_img if raw_img.lower() not in ['nan', 'none', ''] else "https://via.placeholder.com/600x400?text=No+Image"

    try:
        sell_price = float(item.get('sell_price', 0))
    except: 
        sell_price = 0
    st.image(img_url, use_container_width=True)
    
    st.markdown(f"## {item['name']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Loại:** {item['category']}")
    with col2:
        st.markdown(f"**Tình trạng:** {item['condition']}")
    
    st.markdown(f"**Bảo hành:** {item['warranty_info']}")
    
    st.success(f"Giá bán: {sell_price:,.0f} d")
        
    st.markdown("### Liên hệ đặt hàng")
    st.markdown("**HOTLINE / ZALO:** 0931863070")
    st.link_button("Messenger/ Facebook", "https://www.facebook.com/thanh.phat.114166", use_container_width=True)

def render_single_card(data, key_prefix):
    unique_key = f"{key_prefix}_{data['id']}"
    with st.container(border=True):
        img = str(data['image_url']).strip() or "https://via.placeholder.com/400x300"
        st.markdown(f"""
            <div style="width: 100%; height: 220px; position: relative; border-bottom: 1px solid #252a30; margin-bottom: 12px; border-radius: 5px 5px 0 0; overflow: hidden;">
                <div style="position: absolute; inset: 0; background-image: url('{img}'); background-size: cover; background-position: center; filter: blur(20px) brightness(0.4); transform: scale(1.2);"></div>
                <div style="position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
                <img src="{img}" style="max-width: 100%; border-radius: 8px; max-height: 100%; object-fit: contain; z-index: 1;">
                </div>
            </div>
            <div style='padding: 0 8px;'>
                <div style='font-weight:700; color:white; font-size:1.1rem; line-height:1.4; height:50px; overflow:hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; margin-bottom: 8px;'>{data['name']}</div>
                <span style="font-size: 0.75rem; background: #252a30; color: #b0b3b8; padding: 4px 8px; border-radius: 4px; font-weight: 600; margin-left:-10px">{data['category']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        c_price, c_btn = st.columns([1.5, 1])
        with c_price:
            st.markdown(f"<div style='font-size:1.2rem; font-weight:bold; color:#00c853; margin-top:5px;'>{data['sell_price']:,.0f} d</div>", unsafe_allow_html=True)
        with c_btn:
            if st.button("Chi Tiết", key=f"view_{unique_key}", use_container_width=True):
                show_product_detail(data)

def render_product_grid(df_data, key_prefix):
    if df_data.empty:
        st.info("Khong tim thay san pham nao.")
        return
    df_data = df_data.sort_values(by='id', ascending=False)
    cols = st.columns(3) 
    for i, (_, data) in enumerate(df_data.iterrows()):
        with cols[i % 3]:
            render_single_card(data, key_prefix)

def on_search_change():
    query = st.session_state.main_search_input
    if query.strip() == "#login#":
        st.session_state.show_login = True
        st.session_state.main_search_input = "" 
        st.session_state.search_term = ""
    else:
        st.session_state.search_term = query
        if query: st.session_state.selected_category = None 

def on_category_change():
    st.session_state.main_search_input = ""
    st.session_state.search_term = ""

def render_shop_interface(df_full):
    c_search, c_filter = st.columns([1, 2])
    with c_search:
        if "main_search_input" in st.session_state and st.session_state.main_search_input == "#login#":
             st.session_state.main_search_input = ""
        st.text_input("Tim kiem", placeholder="Tim kiem ...", label_visibility="collapsed", key="main_search_input", on_change=on_search_change)

    with c_filter:
        cats = ["Trang chủ", "Tất cả", "Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Khác"]
        st.pills("Danh muc", cats, selection_mode="single", label_visibility="collapsed", key="selected_category", on_change=on_category_change)

    st.markdown("---")
    
    if not df_full.empty:
        df_visible = df_full[df_full['status'] == 'Sẵn hàng'].copy()
    else:
        df_visible = pd.DataFrame()

    view_mode = "home"
    if st.session_state.search_term:
        view_mode = "search"
        df_visible = df_visible[df_visible['name'].str.contains(st.session_state.search_term, case=False, na=False, regex=False)]
    elif st.session_state.selected_category and st.session_state.selected_category != "Trang chủ":
        view_mode = "category"
        if st.session_state.selected_category != "Tất cả":
            df_visible = df_visible[df_visible['category'] == st.session_state.selected_category]

    if view_mode in ["search", "category"]:
        banner_info = {"img": "images/banner_main.jpg", "title": f"SEARCH", "sub": f"Ket qua cho: {st.session_state.search_term}"} if view_mode == "search" else BANNER_MAP.get(st.session_state.selected_category, BANNER_MAP["Tất cả"])
        render_banner(banner_info["img"], banner_info["title"], banner_info["sub"])
        st.write("")
        render_product_grid(df_visible, f"grid_{view_mode}")
    else:
        render_banner(BANNER_MAP["Trang chủ"]["img"], BANNER_MAP["Trang chủ"]["title"], BANNER_MAP["Trang chủ"]["sub"])
        
        if not df_visible.empty:
            st.subheader("Có thể bạn thích")
            if 'suggested_ids' not in st.session_state:
                sample_size = min(6, len(df_visible))
                st.session_state.suggested_ids = df_visible.sample(n=sample_size)['id'].tolist()
            render_product_grid(df_visible[df_visible['id'].isin(st.session_state.suggested_ids)], "highlight")
            st.markdown("---")
            
            categories_to_show = [
                {"name": "Chuột", "banner_key": "Chuột"},
                {"name": "Bàn phím", "banner_key": "Bàn phím"},
                {"name": "Tai nghe", "banner_key": "Tai nghe"},
                {"name": "Lót chuột", "banner_key": "Lót chuột"},
                {"name": "Khác", "banner_key": "Khác"}
            ]
            
            for cat_info in categories_to_show:
                cat_name = cat_info["name"]
                cat_data = df_visible[df_visible['category'] == cat_name]
                if not cat_data.empty:
                    banner_info = BANNER_MAP.get(cat_info["banner_key"], BANNER_MAP["Tất cả"])
                    render_banner(banner_info["img"], banner_info["title"], banner_info["sub"])
                    render_product_grid(cat_data, f"{cat_name.lower().replace(' ', '_')}_home")
                    st.markdown("---")

@st.dialog("Sua san pham")
def edit_product_dialog(item, real_index):
    with st.form("edit_form_dialog"):
        e_name = st.text_input("Ten", value=item['name'])
        cat_list = ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"]
        e_idx = cat_list.index(item['category']) if item['category'] in cat_list else 0
        e_category = st.selectbox("Danh Mục:", cat_list, index=e_idx)
        
        c1, c2 = st.columns(2)
        e_buy = c1.number_input("Von", value=int(item['buy_price']), step=50000)
        e_sell = c2.number_input("Ban", value=int(item['sell_price']), step=50000)
        e_cond = st.text_input("Tinh trang", value=item['condition'])
        e_warr = st.text_input("Bao hanh", value=item['warranty_info'])
        
        e_file = st.file_uploader("Tai anh moi")

        if st.form_submit_button("Luu thay doi", type="primary"):
            url = item['image_url']
            if e_file: 
                with st.spinner("Dang tai anh..."):
                    url = db.upload_image_to_drive(e_file, e_name)
            
            db.update_product_full(item['id'], e_name, e_category, e_buy, e_sell, e_cond, e_warr, url)
            
            st.session_state.master_df.at[real_index, 'name'] = e_name
            st.session_state.master_df.at[real_index, 'category'] = e_category
            st.session_state.master_df.at[real_index, 'buy_price'] = e_buy
            st.session_state.master_df.at[real_index, 'sell_price'] = e_sell
            st.session_state.master_df.at[real_index, 'condition'] = e_cond
            st.session_state.master_df.at[real_index, 'warranty_info'] = e_warr
            if url: st.session_state.master_df.at[real_index, 'image_url'] = url
            
            st.success("Da sua")
            time.sleep(0.5)
            st.rerun()

def render_admin_dashboard():
    col_header, col_logout = st.columns([6, 1])
    col_header.title("TRANG QUAN TRI ADMIN")
    
    if col_logout.button("Dang xuat", type="primary", use_container_width=True):
        st.session_state.is_admin = False
        if 'edit_id' in st.session_state: del st.session_state.edit_id
        st.rerun()

    tab_list, tab_add = st.tabs(["DANH SACH", "NHAP HANG"])

    with tab_add:
        st.write("### Nhap thong tin san pham moi")
        with st.form("add_product_tab"):
            c_name, c_cat = st.columns([2, 1])
            n = c_name.text_input("Ten SP")
            c = c_cat.selectbox("Loai", ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"])
            
            f = st.file_uploader("Anh minh hoa", type=['jpg', 'png', 'jpeg'])
            
            c1, c2, c3, c4 = st.columns(4)
            b = c1.number_input("Von", step=50000, format="%d")
            s = c2.number_input("Ban", step=50000, format="%d")
            cond = c3.text_input("Tinh trang", placeholder="Like new...")
            w = c4.text_input("Bao hanh", placeholder="1 thang...")
            
            if st.form_submit_button("Luu san pham", type="primary", use_container_width=True):
                if n:
                    with st.spinner("Dang luu du lieu..."):
                        url = ""
                        if f: url = db.upload_image_to_drive(f, n)
                        
                        new_id = db.add_product(n, c, b, s, cond or "2nd", w or "Bao test", url)
                        
                        new_row = {
                            'id': new_id, 'name': n, 'category': c, 'buy_price': b, 'sell_price': s,
                            'status': 'Sẵn hàng', 'condition': cond or "2nd", 'warranty_info': w or "Bao test",
                            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'image_url': url
                        }
                        st.session_state.master_df = pd.concat([pd.DataFrame([new_row]), st.session_state.master_df], ignore_index=True)
                        st.success(f"Da them: {n}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.warning("Vui long nhap ten san pham")

    with tab_list:
        c_search, c_refresh = st.columns([5, 1])
        search_query = c_search.text_input("Tim kiem ten hoac ID", label_visibility="collapsed", placeholder="Tim kiem...")
        
        if c_refresh.button("Lam moi", use_container_width=True):
            force_refresh_data()
            st.rerun()

        df = st.session_state.master_df.copy()
        if search_query:
            df = df[
                df['name'].str.contains(search_query, case=False, na=False, regex=False) | 
                df['id'].astype(str).str.contains(search_query, regex=False)
            ]
        df = df.sort_values(by='id', ascending=False)
        
        st.markdown("""
        <div style="display: flex; background: #21262d; padding: 10px; border-radius: 6px; font-weight: bold; color: #b0b3b8; margin-top: 10px;">
            <div style="width: 5%;">ID</div>
            <div style="width: 8%;">Anh</div>
            <div style="width: 30%;">Ten san pham</div>
            <div style="width: 10%;">Loai</div>
            <div style="width: 15%; text-align: right;">Von</div>
            <div style="width: 15%; text-align: right;">Ban</div>
            <div style="width: 10%; text-align: center;">Tinh trang</div>
            <div style="width: 7%; text-align: center;">Menu</div>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, row in df.iterrows():
            real_matches = st.session_state.master_df[st.session_state.master_df['id'] == row['id']].index
            if len(real_matches) == 0: continue
            real_index = real_matches[0]
            
            status_text = "San" if row['status'] == 'Sẵn hàng' else "Da ban"
            img_src = row['image_url'] if row['image_url'] else "https://via.placeholder.com/50"
            
            with st.container():
                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([0.5, 0.8, 3, 1, 1.5, 1.5, 1, 0.7])
                
                c1.markdown(f"<div style='padding-top: 15px; color: #888;'>{row['id']}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                        <div style="width: 50px; height: 50px; overflow: hidden; border-radius: 4px; border: 1px solid #30363d; display: flex; align-items: center; justify-content: center; background: #000;">
                            <img src="{img_src}" style="width: 100%; height: 100%; object-fit: cover;">
                        </div>
                    """, unsafe_allow_html=True)
                c3.markdown(f"<div style='padding-top: 15px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{row['name']}</div>", unsafe_allow_html=True)
                c4.markdown(f"<div style='padding-top: 15px; font-size: 0.85rem; color: #888;'>{row['category']}</div>", unsafe_allow_html=True)
                c5.markdown(f"<div style='padding-top: 15px; text-align: right; color: #b0b3b8;'>{row['buy_price']:,.0f}</div>", unsafe_allow_html=True)
                c6.markdown(f"<div style='padding-top: 15px; text-align: right; color: #29b5e8; font-weight: bold;'>{row['sell_price']:,.0f}</div>", unsafe_allow_html=True)
                with c7:
                    st.write("")
                    if st.button(status_text, key=f"st_{row['id']}", use_container_width=True):
                        new_val = "Đã bán" if row['status'] == 'Sẵn hàng' else "Sẵn hàng"
                        db.update_status(row['id'], new_val)
                        st.session_state.master_df.at[real_index, 'status'] = new_val
                        st.rerun()
                with c8:
                    st.write("")
                    pop = st.popover("...", use_container_width=True)
                    if pop.button("Sua", key=f"ed_{row['id']}", use_container_width=True):
                         edit_product_dialog(row, real_index)

                    if pop.button("Xoa", key=f"del_{row['id']}", type="primary", use_container_width=True):
                        db.delete_product(row['id'])
                        st.session_state.master_df = st.session_state.master_df.drop(real_index)
                        st.rerun()
                st.markdown("<div style='border-bottom: 1px solid #30363d; margin: 4px 0;'></div>", unsafe_allow_html=True)

def main():
    if not st.session_state.master_df.empty:
        st.session_state.master_df['buy_price'] = pd.to_numeric(st.session_state.master_df['buy_price'], errors='coerce').fillna(0)
        st.session_state.master_df['sell_price'] = pd.to_numeric(st.session_state.master_df['sell_price'], errors='coerce').fillna(0)

    if st.session_state.is_admin:
        render_admin_dashboard()
    else:
        if st.session_state.show_login:
            with st.popover("Dang nhap Admin", use_container_width=True):
                pwd = st.text_input("Mat khau", type="password")
                if st.button("Vao", type="primary", use_container_width=True):
                    if pwd == db.get_admin_password():
                        st.session_state.is_admin = True
                        st.session_state.show_login = False
                        st.rerun()
                    else: st.error("Sai mat khau")
        
        render_shop_interface(st.session_state.master_df)
        st.markdown("---")
        st.markdown("""
            <div style="text-align:center; color:#888; font-size:0.9rem;">
                <div>PGEAR - Hotline: 0931863070</div>
                <a href="https://www.facebook.com/thanh.phat.114166" target="_blank" style="color: #29b5e8; text-decoration: none;">Thanh Phat</a>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()