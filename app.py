import streamlit as st
import pandas as pd
import backend as db  
import styles
import base64
import os

st.set_page_config(page_title="PGear", layout="wide", initial_sidebar_state="collapsed")
st.markdown(styles.CSS, unsafe_allow_html=True)

if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'show_login' not in st.session_state: st.session_state.show_login = False

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
    st.markdown(f"""
        <div style="border-radius: 12px; overflow: hidden; margin-bottom: 20px; border: 1px solid #30363d;">
            <img src="{img_url}" style="width: 100%; object-fit: fill;">
        </div>
    """, unsafe_allow_html=True)
    
    admin_html = ""
    if st.session_state.is_admin:
        admin_html = f"""
            <div class="detail-info-row">
                <span class="detail-label">Giá vốn (Admin)</span>
                <span class="detail-value">{item['buy_price']:,.0f} VNĐ</span>
            </div>
        """

    st.markdown(f"""
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

        <div class="detail-price-box" style="margin-top: 12px; margin-bottom: 12px;">
            <div class="detail-price-label" style="font-size: 0.9rem;">Giá bán niêm yết</div>
            <div class="detail-price-value" style="font-size: 1.5rem;">{item['sell_price']:,.0f} đ</div>
        </div>

        <div class="detail-contact-bar" style="padding: 10px; font-size: 0.9rem;">
            <span><b>LH MUA HÀNG: &nbsp;</span>
            <span>Zalo/ SĐT: <b>0931863070</b></span>
            <span style="margin: 0 10px; color: #555;">|</span>
            <a href="https://www.facebook.com/thanh.phat.114166" target="_blank" 
               style="text-decoration: none; color: var(--primary); font-weight: bold;">
                Thanh Phat
            </a>
        </div>
    """, unsafe_allow_html=True)

@st.fragment
def render_single_card(data, key_prefix):
    unique_key = f"{key_prefix}_{data['id']}"
    
    with st.container(border=True):
        img = str(data['image_url']).strip() or "https://via.placeholder.com/400x300"
        st.markdown(f"""
            <div style="
                width: 100%; height: 220px; 
                background: url('{img}') center center / cover no-repeat; 
                border-bottom: 1px solid #252a30;
                margin-bottom: 12px;
                border-radius: 5px;
            "></div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='padding: 0 8px;'>
                <div style='font-weight:700; color:white; font-size:1.1rem; 
                            line-height:1.4; height:50px; overflow:hidden; 
                            display: -webkit-box; -webkit-line-clamp: 2; 
                            -webkit-box-orient: vertical; margin-bottom: 8px;
                            margin-left: -7px'>
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
            # [MỚI] Nút bật Popup chi tiết
            if st.button("Chi tiết", key=f"view_{unique_key}", use_container_width=True):
                show_product_detail(data)

        if st.session_state.is_admin:
            st.markdown("<div style='margin: 10px 8px; border-top: 1px solid #30363d;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='padding: 0 8px; color: #888; font-size: 0.8rem;'>Vốn: {data['buy_price']:,.0f}</div>", unsafe_allow_html=True)
            
            ab1, ab2, ab3 = st.columns(3)
            is_sold = data['status'] == "Đã bán"
            lbl_status = "Mở lại" if is_sold else "Đã bán"
            
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
        st.caption("Chưa có sản phẩm.")
        return

    cols = st.columns(3) 
    for i, (_, data) in enumerate(df_data.iterrows()):
        with cols[i % 3]:
            render_single_card(data, key_prefix)

def main():
    df = db.load_data()
    if not df.empty:
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)
        df['sell_price'] = pd.to_numeric(df['sell_price'], errors='coerce').fillna(0)
        
        if not st.session_state.is_admin:
            df = df[df['status'] == 'Sẵn hàng']

    h1, h2 = st.columns([4,1])
    with h1: st.markdown('<div style="font-family:\'BBH Bartle\'; font-size:2.5rem; color:white; text-shadow: 0 0 15px var(--primary-glow);">PGEAR</div>', unsafe_allow_html=True)
    with h2:
        if st.session_state.is_admin and st.button("Thoát Admin"):
            st.session_state.is_admin = False
            st.rerun()

    if st.session_state.show_login and not st.session_state.is_admin:
        with st.popover("Bảo mật", use_container_width=True):
            pwd = st.text_input("Password", type="password")
            if st.button("Login", type="primary", use_container_width=True):
                if pwd == db.get_admin_password():
                    st.session_state.is_admin = True
                    st.session_state.show_login = False
                    st.rerun()
                else: st.error("Sai mật khẩu")

    render_banner("images/banner_main.jpg", "PGEAR", "Gaming Gear.")
    df_random = df.sample(n=min(6, len(df)))
    render_product_grid(df_random, "highlight")
    st.write("") 

    render_banner("images/banner_main.jpg", "GAMING MOUSE", "Percise.")
    render_product_grid(df[df['category'] == 'Chuột'], "mouse")

    render_banner("images/banner_keyboard.jpg", "KEYBOARD", "Performance.")
    render_product_grid(df[df['category'] == 'Bàn phím'], "kb")

    render_banner("images/banner_pad.jpg", "PAD & AUDIO", "Pure Experience.")

    render_product_grid(df[df['category'].isin(['Lót chuột', 'Tai nghe', 'Ghế', 'Khác'])], "pad")

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

    if not st.session_state.is_admin:
        st.markdown("---")
        c1, c2, c3 = st.columns([1,10,1])
        if c1.button(".", key="secret"): st.session_state.show_login = True
        c2.markdown("<div style='text-align:center; color:#666; font-size: 0.9rem;'>PGEAR. Hotline: 0931.863.070</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()