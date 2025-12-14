import streamlit as st
import pandas as pd
import backend as db  
import styles
import base64
import os

st.set_page_config(page_title="PGear", layout="wide", initial_sidebar_state="collapsed")
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

# --- CÁC HÀM HỖ TRỢ (GIỮ NGUYÊN) ---
def get_base64_image(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

def render_banner(img_file, title, subtitle):
    bin_str = get_base64_image(img_file)
    # Fallback nếu ảnh không tồn tại
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
        admin_html = f"""
            <div class="detail-info-row">
                <span class="detail-label">Giá vốn (Admin)</span>
                <span class="detail-value">{item['buy_price']:,.0f} VNĐ</span>
            </div>
        """

    st.markdown(f"""
        <div style="border-radius: 12px; overflow: hidden; margin-bottom: 20px; border: 1px solid #30363d;">
            <img src="{img_url}" style="width: 100%; object-fit: fill;">
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

# Helper render card (Không dùng fragment ở đây để tránh lồng nhau phức tạp)
def render_single_card(data, key_prefix):
    unique_key = f"{key_prefix}_{data['id']}"
    with st.container(border=True):
        img = str(data['image_url']).strip() or "https://via.placeholder.com/400x300"
        # Card Image
        st.markdown(f"""
            <div style="width: 100%; height: 220px; background: url('{img}') center center / cover no-repeat; 
                border-bottom: 1px solid #252a30; margin-bottom: 12px; border-radius: 5px;"></div>
        """, unsafe_allow_html=True)

        # Card Title
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

        # Admin Actions
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
        st.info("Không tìm thấy sản phẩm nào phù hợp.")
        return

    # Sắp xếp sản phẩm mới nhất lên đầu
    df_data = df_data.sort_values(by='id', ascending=False)
    
    cols = st.columns(3) 
    for i, (_, data) in enumerate(df_data.iterrows()):
        with cols[i % 3]:
            render_single_card(data, key_prefix)

# --- CORE FEATURE: SHOP INTERFACE (DÙNG FRAGMENT ĐỂ TỐI ƯU) ---
@st.fragment
def render_shop_interface(df_full):
    # 1. SEARCH BAR & FILTERS
    c_search, c_filter = st.columns([1, 2])
    
    with c_search:
        search_query = st.text_input("Tìm kiếm sản phẩm...", placeholder="Nhập tên sản phẩm...", label_visibility="collapsed")
    
    with c_filter:
        # Danh sách categories, thêm 'Trang chủ' và 'Tất cả'
        cats = ["Trang chủ", "Tất cả", "Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Khác"]
        # Sử dụng pills (nếu streamlit version mới) hoặc radio horizontal
        # Selection state sẽ được giữ trong fragment này
        selected_cat = st.pills("Danh mục", cats, default="Trang chủ", selection_mode="single", label_visibility="collapsed")

    st.markdown("---") # Ngăn cách khu vực điều khiển và hiển thị

    # 2. XỬ LÝ LOGIC LỌC DỮ LIỆU
    # Ưu tiên Search: Nếu có search text -> Tìm trên TOÀN BỘ dữ liệu, bỏ qua category
    filtered_df = df_full.copy()
    
    view_mode = "home" # default
    
    if search_query:
        view_mode = "search"
        filtered_df = filtered_df[filtered_df['name'].str.contains(search_query, case=False, na=False)]
    elif selected_cat and selected_cat != "Trang chủ":
        view_mode = "category"
        if selected_cat != "Tất cả":
            filtered_df = filtered_df[filtered_df['category'] == selected_cat]
    else:
        view_mode = "home"

    # 3. HIỂN THỊ DỮ LIỆU THEO CHẾ ĐỘ (VIEW MODE)
    
    # --- MODE: TÌM KIẾM HOẶC DANH MỤC CỤ THỂ ---
    if view_mode in ["search", "category"]:
        # Lấy banner từ config, nếu search thì dùng banner chung
        if view_mode == "search":
            banner_info = {"img": "images/banner_main.jpg", "title": f"TÌM KIẾM: {search_query}", "sub": "Search Results"}
        else:
            banner_info = BANNER_MAP.get(selected_cat, BANNER_MAP["Tất cả"])
            
        render_banner(banner_info["img"], banner_info["title"], banner_info["sub"])
        st.write("")
        render_product_grid(filtered_df, f"grid_{view_mode}")
        
    # --- MODE: TRANG CHỦ (LAYOUT CŨ - CÓ NHIỀU SECTION) ---
    else:
        # 1. Random Highlight
        render_banner(BANNER_MAP["Trang chủ"]["img"], BANNER_MAP["Trang chủ"]["title"], BANNER_MAP["Trang chủ"]["sub"])
        st.subheader("Có thể bạn thích")
        df_random = filtered_df.sample(n=min(6, len(filtered_df)))
        render_product_grid(df_random, "highlight")
        
        st.write("")
        st.markdown("---")

        # 2. Section Chuột
        render_banner("images/banner_main.jpg", "GAMING MOUSE", "Precise.")
        render_product_grid(filtered_df[filtered_df['category'] == 'Chuột'], "mouse_home")

        # 3. Section Phím
        render_banner("images/banner_keyboard.jpg", "KEYBOARD", "Performance.")
        render_product_grid(filtered_df[filtered_df['category'] == 'Bàn phím'], "kb_home")

        # 4. Section Còn lại
        render_banner("images/banner_pad.jpg", "PAD & AUDIO", "Experience.")
        render_product_grid(filtered_df[filtered_df['category'].isin(['Lót chuột', 'Tai nghe', 'Ghế', 'Khác'])], "other_home")


def main():
    # Load Data
    df = db.load_data()
    
    # Pre-process Data Types
    if not df.empty:
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)
        df['sell_price'] = pd.to_numeric(df['sell_price'], errors='coerce').fillna(0)
        # Nếu không phải admin, lọc sản phẩm đã bán
        if not st.session_state.is_admin:
            df = df[df['status'] == 'Sẵn hàng']

    # --- HEADER ---
    h1, h2 = st.columns([4,1])
    with h1: st.markdown('<div style="font-family:\'BBH Bartle\'; font-size:2.5rem; color:white; text-shadow: 0 0 15px var(--primary-glow);">PGEAR</div>', unsafe_allow_html=True)
    with h2:
        if st.session_state.is_admin and st.button("Thoát Admin"):
            st.session_state.is_admin = False
            st.rerun()

    # --- LOGIN MODAL ---
    if st.session_state.show_login and not st.session_state.is_admin:
        with st.popover("Bảo mật", use_container_width=True):
            pwd = st.text_input("Password", type="password")
            if st.button("Login", type="primary", use_container_width=True):
                if pwd == db.get_admin_password():
                    st.session_state.is_admin = True
                    st.session_state.show_login = False
                    st.rerun()
                else: st.error("Sai mật khẩu")

    # --- GỌI FRAGMENT GIAO DIỆN CHÍNH ---
    # Truyền dataframe vào để fragment xử lý lọc và hiển thị
    render_shop_interface(df)

    # --- ADMIN SIDEBAR (Giữ nguyên) ---
    if st.session_state.is_admin:
        with st.sidebar:
            st.title("QUẢN LÝ KHO")
            if 'edit_id' in st.session_state and st.session_state.edit_id:
                st.info(f"Đang sửa ID: {st.session_state.edit_id}")
                # Lấy item hiện tại từ DB để đảm bảo mới nhất
                curr_df = db.load_data()
                edit_item = curr_df[curr_df['id'] == st.session_state.edit_id].iloc[0]
                with st.form("edit_form"):
                    e_name = st.text_input("Tên", value=edit_item['name'])
                    e_category = st.selectbox("Loại", ["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"], index=["Chuột", "Bàn phím", "Tai nghe", "Lót chuột", "Ghế", "Khác"].index(edit_item['category']))
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

    # --- FOOTER ---
    if not st.session_state.is_admin:
        st.markdown("---")
        f_left, f_mid, f_right = st.columns([1, 8, 1])
        with f_left:
            if st.button(".", key="secret_login_btn"): st.session_state.show_login = True
        with f_mid:
            st.markdown("""
                <div style="text-align:center; color:#888; font-size:0.9rem;">
                    <div>PGEAR - Hotline: 0931863070</div>
                    <a href="https://www.facebook.com/thanh.phat.114166" target="_blank" style="color: #29b5e8; text-decoration: none;">Thanh Phat</a>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()