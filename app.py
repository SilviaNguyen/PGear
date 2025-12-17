import streamlit as st
import pandas as pd
import backend as db  
import styles
import base64
import os

# [FIX]: Xóa initial_sidebar_state="collapsed" để sidebar tự mở khi là Admin
st.set_page_config(page_title="PGear", layout="wide")
st.markdown(styles.CSS, unsafe_allow_html=True)

BANNER_MAP = {
    "Trang chủ": {"img": "images/pgear.jpg", "title": "PGEAR", "sub": ""},
    "Tất cả":   {"img": "images/banner_main.jpg", "title": "ALL PRODUCTS", "sub": ""},
    "Chuột":    {"img": "images/banner_mouse.jpg", "title": "GAMING MOUSE", "sub": "pre·ci·sion."},
    "Bàn phím": {"img": "images/banner_keyboard.jpg", "title": "KEYBOARD", "sub": "per·for·mance."},
    "Tai nghe": {"img": "images/banner_audio.jpg", "title": "AUDIO", "sub": "sound."},
    "Lót chuột": {"img": "images/banner_pad.jpg", "title": "MOUSEPAD", "sub": "glide."},
    "Khác":     {"img": "images/banner_accessories.jpg", "title": "ACCESSORIES", "sub": "sup·port."}
}

if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'show_login' not in st.session_state: st.session_state.show_login = False
if 'search_term' not in st.session_state: st.session_state.search_term = ""
if 'selected_category' not in st.session_state: st.session_state.selected_category = "Trang chủ"

def on_search_change():
    query = st.session_state.main_search_input
    
    if query.strip() == "#login#":
        st.session_state.show_login = True
        st.session_state.main_search_input = "" # Xóa ngay lập tức
        st.session_state.search_term = ""
    else:
        st.session_state.search_term = query
        if query: 
            st.session_state.selected_category = None 

def on_category_change():
    st.session_state.main_search_input = ""
    st.session_state.search_term = ""

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
    img_url = str(item['image_url']).strip() or "https://via.placeholder.com/600x400"
    
    admin_html = ""
    if st.session_state.is_admin:
        admin_html = (f"""<div class="detail-info-row">
                <span class="detail-label">Giá vốn (Admin)</span>
                <span class="detail-value">{item['buy_price']:,.0f} VNĐ</span>
            </div>""")

    st.markdown(f"""
        <div style="border-radius: 12px; overflow: hidden; margin-bottom: 20px; border: 1px solid #30363d;">
        <div style="width: 100%; height: 350px; display: flex; align-items: center; justify-content: center; background: #161b22;">
            <img src="{img_url}" style="max-width: 100%; max-height: 100%; object-fit: contain;">
        </div>
        <h2 style='font-weight: 800; margin-bottom: 8px; font-size: 1.5rem; line-height: 1.2;'>{item['name']}</h2>
        
        <div style="margin-bottom: 12px;">
            <span class="detail-badge badge-blue">{item['category']}</span>
            <span class="detail-badge badge-green">{item['condition']}</span>
        </div>

        <div class="detail-info-row" style="padding: 8px 0; border-top: 1px solid #30363d;">
            <span class="detail-label">Bảo hành</span>
            <span class="detail-value" style="color: var(--primary);">{item['warranty_info']}</span>
        </div>
        
        {admin_html}

        <div class="detail-price-box">
            <div class="detail-price-label">Giá bán niêm yết</div>
            <div class="detail-price-value">{item['sell_price']:,.0f} đ</div>
        </div>

        <div class="detail-contact-bar">
            <span>LH MUA HÀNG: &nbsp;</span>
            <b style="color:var(--success);">0931863070</b>
            <span style="margin: 0 10px; color: #555;">|</span>
            <a href="https://www.facebook.com/thanh.phat.114166" target="_blank" 
               style="text-decoration: none; color: var(--primary); font-weight: bold;">
                Facebook
            </a>
        </div>
    """, unsafe_allow_html=True)

def render_single_card(data, key_prefix):
    unique_key = f"{key_prefix}_{data['id']}"
    with st.container(border=True):
        img = str(data['image_url']).strip() or "https://via.placeholder.com/400x300"
        
        st.markdown(f"""
            <div style=
                "width: 100%; height: 220px; position: relative;
                border-bottom: 1px solid #252a30; margin-bottom: 12px; 
                border-radius: 5px 5px 0 0; overflow: hidden;">
                <div style="position: absolute; inset: 0; background-image: url('{img}');
                background-size: cover; background-position: center;
                filter: blur(20px) brightness(0.4); transform: scale(1.2);"></div>
                <div style="position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
                <img src="{img}" style="max-width: 100%; border-radius: 8px; max-height: 100%; object-fit: contain; 
                transition: transform 0.3s ease; z-index: 1;">
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='padding: 0 8px;'>
                <div style='font-weight:700; color:white; font-size:1.1rem; line-height:1.4; height:50px; 
                            overflow:hidden; display: -webkit-box; -webkit-line-clamp: 2; 
                            -webkit-box-orient: vertical; margin-bottom: 8px; margin-left: -7px'>
                    {data['name']}
                </div>
                <span style="font-size: 0.75rem; background: #252a30; color: #b0b3b8; padding: 4px 8px; border-radius: 4px; font-weight: 600; margin-left: -11px">
                    {data['category']}
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        c_price, c_btn = st.columns([1.5, 1])
        with c_price:
            st.markdown(f"<div style='font-size:1.2rem; font-weight:bold; color:#00c853; margin-top:5px;'>{data['sell_price']:,.0f} đ</div>", unsafe_allow_html=True)
        
        with c_btn:
            if st.button("Chi tiết", key=f"view_{unique_key}", use_container_width=True):
                show_product_detail(data)

        if st.session_state.is_admin:
            st.markdown("<div style='margin: 10px 8px; border-top: 1px solid #30363d;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='padding: 0 8px; color: #888; font-size: 0.8rem;'>Vốn: {data['buy_price']:,.0f}</div>", unsafe_allow_html=True)
            
            ab1, ab2, ab3 = st.columns(3)
            is_sold = data['status'] == "Đã bán"
            lbl_status = "Mở" if is_sold else "Bán"
            
            if ab1.button(lbl_status, key=f"st_{unique_key}"):
                db.update_status(data['id'], "Sẵn hàng" if is_sold else "Đã bán")
                st.rerun()
            if ab2.button("Sửa", key=f"ed_{unique_key}"):
                st.session_state.edit_id = data['id']
                st.rerun()
            if ab3.button("Xóa", key=f"del_{unique_key}"):
                db.delete_product(data['id'])
                st.rerun()

def render_product_grid(df_data, key_prefix):
    if df_data.empty:
        st.info("Không tìm thấy sản phẩm nào.")
        return

    df_data = df_data.sort_values(by='id', ascending=False)
    cols = st.columns(3) 
    for i, (_, data) in enumerate(df_data.iterrows()):
        with cols[i % 3]:
            render_single_card(data, key_prefix)

def render_shop_interface(df_full):
    c_search, c_filter = st.columns([1, 2])
    
    with c_search:
        # Cơ chế dọn dẹp từ khóa #login# triệt để
        if "main_search_input" in st.session_state and st.session_state.main_search_input == "#login#":
             st.session_state.main_search_input = ""
             
        st.text_input("Tìm kiếm", 
                      placeholder="Tìm kiếm ...", 
                      label_visibility="collapsed",
                      key="main_search_input",
                      on_change=on_search_change)

    with c_filter:
        cats = ["Trang chủ", "Tất cả", "Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Khác"]
        st.pills("Danh mục", cats, 
                 selection_mode="single", 
                 label_visibility="collapsed",
                 key="selected_category",
                 on_change=on_category_change)

    st.markdown("---")

    filtered_df = df_full.copy()
    
    if st.session_state.search_term:
        view_mode = "search"
        filtered_df = filtered_df[filtered_df['name'].str.contains(st.session_state.search_term, case=False, na=False)]
    elif st.session_state.selected_category and st.session_state.selected_category != "Trang chủ":
        view_mode = "category"
        if st.session_state.selected_category != "Tất cả":
            filtered_df = filtered_df[filtered_df['category'] == st.session_state.selected_category]
    else:
        view_mode = "home"

    if view_mode in ["search", "category"]:
        if view_mode == "search":
            banner_info = {"img": "images/banner_main.jpg", "title": f"SEARCH", "sub": f"Kết quả cho: {st.session_state.search_term}"}
        else:
            banner_info = BANNER_MAP.get(st.session_state.selected_category, BANNER_MAP["Tất cả"])
            
        render_banner(banner_info["img"], banner_info["title"], banner_info["sub"])
        st.write("")
        render_product_grid(filtered_df, f"grid_{view_mode}")
        
    else:
        render_banner(BANNER_MAP["Trang chủ"]["img"], BANNER_MAP["Trang chủ"]["title"], BANNER_MAP["Trang chủ"]["sub"])
        
        if not filtered_df.empty:
                    st.subheader("Có thể bạn thích")
                    if 'suggested_ids' not in st.session_state:
                        sample_size = min(6, len(filtered_df))
                        st.session_state.suggested_ids = filtered_df.sample(n=sample_size)['id'].tolist()
                    df_random = filtered_df[filtered_df['id'].isin(st.session_state.suggested_ids)]
                    render_product_grid(df_random, "highlight")
                    st.write("")
                    st.markdown("---")

        render_banner("images/banner_mouse.jpg", "GAMING MOUSE", "Precise.")
        render_product_grid(filtered_df[filtered_df['category'] == 'Chuột'], "mouse_home")

        render_banner("images/banner_keyboard.jpg", "KEYBOARD", "Performance.")
        render_product_grid(filtered_df[filtered_df['category'] == 'Bàn phím'], "kb_home")

        render_banner("images/banner_pad.jpg", "PAD & AUDIO", "Experience.")
        render_product_grid(filtered_df[filtered_df['category'].isin(['Lót chuột', 'Tai nghe', 'Ghế', 'Khác'])], "other_home")


def main():
    df = db.load_data()
    if not df.empty:
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)
        df['sell_price'] = pd.to_numeric(df['sell_price'], errors='coerce').fillna(0)
        if not st.session_state.is_admin:
            df = df[df['status'] == 'Sẵn hàng']

    # --- ADMIN SIDEBAR (RENDER TRƯỚC ĐỂ ĐẢM BẢO HIỂN THỊ) ---
    if st.session_state.is_admin:
        with st.sidebar:
            st.title("QUẢN LÝ KHO")
            if 'edit_id' in st.session_state and st.session_state.edit_id:
                st.info(f"Đang sửa ID: {st.session_state.edit_id}")
                curr_df = db.load_data()
                
                if st.session_state.edit_id in curr_df['id'].values:
                    edit_item = curr_df[curr_df['id'] == st.session_state.edit_id].iloc[0]
                    with st.form("edit_form"):
                        e_name = st.text_input("Tên", value=edit_item['name'])
                        e_category = st.selectbox("Loại", ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"], index=["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"].index(edit_item['category']) if edit_item['category'] in ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"] else 0)
                        e_file = st.file_uploader("Ảnh mới", type=['jpg','png'])
                        c1, c2 = st.columns(2)
                        e_buy = c1.number_input("Vốn", value=int(edit_item['buy_price']))
                        e_sell = c2.number_input("Bán", value=int(edit_item['sell_price']))
                        e_cond = st.text_input("Tình trạng", value=edit_item['condition'])
                        e_warr = st.text_input("Bảo hành", value=edit_item['warranty_info'])
                        
                        if st.form_submit_button("Lưu Thay Đổi", type="primary"):
                            url = ""
                            if e_file: url = db.upload_image_to_drive(e_file, e_name)
                            db.update_product_full(st.session_state.edit_id, e_name, e_category, e_buy, e_sell, e_cond, e_warr, url)
                            del st.session_state.edit_id
                            st.rerun()
                else:
                    st.warning("Sản phẩm không tồn tại (có thể đã bị xóa).")
                    if st.button("Quay lại"):
                        del st.session_state.edit_id
                        st.rerun()
                        
                if st.button("Hủy bỏ"):
                    del st.session_state.edit_id
                    st.rerun()
            else:
                st.subheader("Thêm Sản Phẩm")
                with st.form("add"):
                    n = st.text_input("Tên SP")
                    c = st.selectbox("Loại", ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"])
                    f = st.file_uploader("Ảnh")
                    c1, c2 = st.columns(2)
                    b = c1.number_input("Vốn", step=50000)
                    s = c2.number_input("Bán", step=50000)
                    cond = st.text_input("Tình trạng")
                    w = st.text_input("Bảo hành")
                    if st.form_submit_button("Thêm Mới", type="primary"):
                        if n:
                            url = ""
                            if f: url = db.upload_image_to_drive(f, n)
                            db.add_product(n, c, b, s, cond or "-", w, url)
                            st.rerun()

    # --- HEADER ---
    h1, h2 = st.columns([4,1])
    with h1: st.markdown('', unsafe_allow_html=True)
    with h2:
        if st.session_state.is_admin and st.button("Thoát Admin"):
            st.session_state.is_admin = False
            st.rerun()

    # --- LOGIN MODAL ---
    if st.session_state.show_login and not st.session_state.is_admin:
        with st.popover("Bảo mật (Đang mở)", use_container_width=True):
            st.markdown("### Đăng nhập Admin")
            pwd = st.text_input("Mật khẩu", type="password")
            if st.button("Xác thực", type="primary", use_container_width=True):
                if pwd == db.get_admin_password():
                    st.session_state.is_admin = True
                    st.session_state.show_login = False
                    st.rerun()
                else: st.error("Sai mật khẩu")

    # --- MAIN SHOP ---
    render_shop_interface(df)

    if not st.session_state.is_admin:
        st.markdown("---")
        st.markdown("""
            <div style="text-align:center; color:#888; font-size:0.9rem;">
                <div>PGEAR - Hotline: 0931863070</div>
                <a href="https://www.facebook.com/thanh.phat.114166" target="_blank" style="color: #29b5e8; text-decoration: none;">Thanh Phat</a>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()