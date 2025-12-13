import streamlit as st
import pandas as pd
import backend as db  
import styles
import base64
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="PGear", layout="wide", initial_sidebar_state="collapsed")
st.markdown(styles.CSS, unsafe_allow_html=True)

# --- QUẢN LÝ SESSION ---
if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'show_login' not in st.session_state: st.session_state.show_login = False

# --- HÀM HỖ TRỢ ẢNH ---
def get_base64_image(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

# --- HÀM RENDER BANNER ---
def render_banner(img_file, title, subtitle):
    bin_str = get_base64_image(img_file)
    if bin_str:
        img_url = f"data:image/jpeg;base64,{bin_str}"
    else:
        img_url = "https://via.placeholder.com/1200x400/30363d/ffffff?text=BANNER"
    
    st.markdown(f"""
        <div class="hero-box" style="background-image: url('{img_url}');">
            <div class="hero-overlay">
                <div class="hero-title">{title}</div>
                <div class="hero-subtitle">{subtitle}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- HÀM HIỂN THỊ LƯỚI SẢN PHẨM ---
def render_product_grid(df_data, key_prefix):
    if df_data.empty:
        st.caption("Chưa có sản phẩm.")
        return

    rows = [df_data.iloc[i:i + 3] for i in range(0, len(df_data), 3)]
    for row_idx, row in enumerate(rows):
        cols = st.columns(3)
        for col_idx, (col, item) in enumerate(zip(cols, row.iterrows())):
            data = item[1]
            unique_key = f"{key_prefix}_{data['id']}_{row_idx}_{col_idx}"
            
            with col:
                with st.container(border=True):
                    # Layout: Text bên trái (2.2) - Ảnh bên phải (1)
                    c_info, c_img = st.columns([2.2, 1])
                    
                    with c_info:
                        st.markdown(f"""
                            <div style='font-weight:700; color:white; font-size:1.05rem; 
                                        line-height:1.3; min-height:42px; 
                                        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;'>
                                {data['name']}
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown(f"<div style='font-size:0.75rem; color:#888; margin-top:4px; margin-bottom:8px;'>{data['category']}</div>", unsafe_allow_html=True)
                        
                        # Giá hiển thị cho khách
                        if not st.session_state.is_admin:
                            st.markdown(f"<div style='font-size:1.1rem; font-weight:bold; color:var(--success);'>{data['sell_price']:,.0f} đ</div>", unsafe_allow_html=True)
                            st.caption(f"BH: {data['warranty_info']}")

                    with c_img:
                        img = str(data['image_url']).strip() or "https://via.placeholder.com/150"
                        st.markdown(f"""
                            <div style="
                                width: 100%; height: 100px; 
                                background: url('{img}') center center / cover no-repeat; 
                                border-radius: 8px; border: 1px solid #333;
                            "></div>
                        """, unsafe_allow_html=True)

                    # --- PHẦN ADMIN (CHỈ HIỆN KHI ĐĂNG NHẬP) ---
                    if st.session_state.is_admin:
                        st.markdown("---")
                        
                        # 1. TÍNH TOÁN LÃI/LỖ
                        buy = data['buy_price']
                        sell = data['sell_price']
                        profit = sell - buy
                        
                        # Hiển thị 3 cột thông số
                        ad_c1, ad_c2, ad_c3 = st.columns(3)
                        ad_c1.markdown(f"<div style='font-size:0.7rem; color:#888'>VỐN</div><div style='color:white; font-weight:bold'>{buy:,.0f}</div>", unsafe_allow_html=True)
                        ad_c2.markdown(f"<div style='font-size:0.7rem; color:#888'>BÁN</div><div style='color:white; font-weight:bold'>{sell:,.0f}</div>", unsafe_allow_html=True)
                        ad_c3.markdown(f"<div style='font-size:0.7rem; color:#888'>LÃI</div><div style='color:#00c853; font-weight:bold'>{profit:,.0f}</div>", unsafe_allow_html=True)
                        
                        st.write("") # Khoảng cách nhỏ

                        # 2. NÚT CHỨC NĂNG
                        b1, b2, b3 = st.columns(3)
                        is_sold = data['status'] == "Đã bán"
                        
                        if b1.button("TT", key=f"s_{unique_key}", type="secondary", help="Đổi trạng thái Bán/Còn"): 
                            db.update_status(data['id'], "Sẵn hàng" if is_sold else "Đã bán")
                            st.rerun()
                        if b2.button("Sửa", key=f"e_{unique_key}"):
                            st.session_state.edit_id = data['id']
                            st.rerun()
                        if b3.button("Xóa", key=f"d_{unique_key}"):
                            db.delete_product(data['id'])
                            st.rerun()

# --- MAIN APP ---
def main():
    # Load data
    df = db.load_data()
    if not df.empty:
        # Ép kiểu số để tính toán
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)
        df['sell_price'] = pd.to_numeric(df['sell_price'], errors='coerce').fillna(0)
        
        # Nếu không phải admin thì ẩn hàng đã bán
        if not st.session_state.is_admin:
            df = df[df['status'] == 'Sẵn hàng']

    # Header Logo (Bỏ nút Login ở đây)
    st.markdown('<div style="font-family:\'BBH Bartle\'; font-size:2rem; color:white; margin-bottom:10px;">PGEAR</div>', unsafe_allow_html=True)

    # Nút Đăng xuất (Chỉ hiện khi ĐÃ đăng nhập)
    if st.session_state.is_admin:
        if st.button("Đăng xuất Admin", type="primary"):
            st.session_state.is_admin = False
            st.rerun()

    # Form Login Popup (Hiện khi bấm nút bí mật)
    if st.session_state.show_login and not st.session_state.is_admin:
        with st.popover("Bảo mật", use_container_width=True):
            pwd = st.text_input("Mật khẩu", type="password")
            if st.button("Truy cập", type="primary", use_container_width=True):
                if pwd == db.get_admin_password():
                    st.session_state.is_admin = True
                    st.session_state.show_login = False
                    st.rerun()
                else:
                    st.error("Sai mật khẩu")

    # --- NỘI DUNG TRANG ---
    
    # 1. Main Banner
    render_banner("images/banner_main.jpg", "PGEAR", "Gaming Gear")
    df_random = df.sample(n=min(6, len(df)))
    render_product_grid(df_random, "all")
    st.write("") 

    # 2. Mouse
    render_banner("images/banner_mouse.jpg", "GAMING MOUSE", "Precise.")
    df_mouse = df[df['category'] == 'Chuột']
    render_product_grid(df_mouse, "mouse")
    st.write("")

    # 3. Keyboard
    render_banner("images/banner_keyboard.jpg", "KEYBOARD", "Performance")
    df_kb = df[df['category'] == 'Bàn phím']
    render_product_grid(df_kb, "kb")
    st.write("")

    # 4. Other
    render_banner("images/banner_pad.jpg", "MOUSEPAD & AUDIO", "Pure Experience.")
    df_other = df[df['category'].isin(['Lót chuột', 'Tai nghe', 'Ghế', 'Khác'])]
    render_product_grid(df_other, "pad")

    # --- SIDEBAR ADMIN (Sửa/Thêm) ---
    if st.session_state.is_admin:
        with st.sidebar:
            st.title("QUẢN LÝ KHO")
            if 'edit_id' in st.session_state and st.session_state.edit_id:
                st.info(f"Đang sửa ID: {st.session_state.edit_id}")
                edit_item = df[df['id'] == st.session_state.edit_id].iloc[0]
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

    # --- FOOTER & NÚT LOGIN ẨN ---
    if not st.session_state.is_admin:
        st.markdown("---")
        
        # Chia cột Footer: Cột trái (Nút ẩn) - Cột giữa (Thông tin) - Cột phải (Rỗng)
        f_left, f_mid, f_right = st.columns([1, 8, 1])
        
        with f_left:
            # NÚT BÍ MẬT: Chỉ hiện dấu chấm ".", bấm vào sẽ hiện popup login
            if st.button(".", key="secret_login_btn"):
                st.session_state.show_login = True
        
        with f_mid:
            st.markdown("""
                <div style="text-align:center; color:#888; font-size:0.9rem; font-family:'Inter', sans-serif;">
                    <div style="margin-bottom: 8px;">PGEAR</div>
                    <div style="margin-bottom: 8px;">Hotline/ Zalo: 0931863070</div>
                    <div>
                        Facebook/ Messenger: 
                        <a href="https://www.facebook.com/thanh.phat.114166" target="_blank" 
                           style="color: #29b5e8; text-decoration: none; font-weight: 700; transition: color 0.3s;">
                            Thanh Phat
                        </a>
                    </div>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()