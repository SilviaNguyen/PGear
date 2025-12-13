import streamlit as st
import pandas as pd
import backend as db  
import styles         

# --- CẤU HÌNH ---
DRIVE_FOLDER_ID_RAW = "1qJD-JyJokrD5tRcp_AR6raVQAwnFNPuQ" 

st.set_page_config(page_title="PGear", layout="wide", initial_sidebar_state="collapsed")
url_fb = "https://www.facebook.com/thanh.phat.114166"
link_text = "Thanh Phat"

st.markdown(styles.CSS, unsafe_allow_html=True)

if 'is_admin' not in st.session_state: st.session_state.is_admin = False
if 'show_login' not in st.session_state: st.session_state.show_login = False

# --- HÀM XỬ LÝ ID DRIVE THÔNG MINH ---

# --- GIAO DIỆN CHÍNH ---
def main():
    c_head_1, c_head_2 = st.columns([6, 1])
    with c_head_1: st.markdown('<p class="bbh-bartle-regular">PGEAR</p>', unsafe_allow_html=True)
    
    df = db.load_data()

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
                correct_pass = db.get_admin_password()
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
                                final_img = db.upload_image_to_drive(e_uploaded_file, e_name)
                            
                            db.update_product_full(st.session_state.edit_id, e_name, e_category, e_buy, e_sell, e_condition, e_warranty, final_img)
                        
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
                                    final_img_url = db.upload_image_to_drive(uploaded_file, name)
                                    if not final_img_url: st.stop()
                                
                                cond_val = condition if condition else "---"
                                db.add_product(name, category, buy, sell, cond_val, warranty, final_img_url)
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
            st.markdown('<p class="contact">Liên hệ mua hàng: 0931863070 (Zalo/ SMS)</p>', unsafe_allow_html=True)
            st.markdown("""
            <p class="contact">
                Facebook/ Messenger: 
                <a href="https://www.facebook.com/thanh.phat.114166" target="_blank" style="text-decoration:bold; color:inherit;">
                    Thanh Phat
                </a>
            </p>
            """, unsafe_allow_html=True)

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
                            # 1. Dòng trạng thái (Sẵn hàng/Đã bán) - Bỏ category ở đây đi
                            st.markdown(f"""
                                <div style="margin-bottom:5px;">
                                    <span style="color:{st_color}; font-weight:bold; border:1px solid {st_color}; padding:2px 6px; border-radius:4px; font-size:0.6rem;">{st_text}</span>
                                </div>""", unsafe_allow_html=True)
                            
                            # 2. Tên sản phẩm + Category nằm phía trước
                            # Tạo html cho category (màu xanh, trong ngoặc vuông)
                            cat_html = f"<span style='color:#29b5e8; font-size:0.9em; font-weight:bold'>{item_data['category']}</span>"
                            
                            # Ghép vào trước tên sản phẩm
                            st.markdown(f"<h4 style='margin:0; font-size:1rem; min-height:40px; line-height:1.4'>{cat_html} {item_data['name']}</h4>", unsafe_allow_html=True)
                            
                            # 3. Thông tin bảo hành (Giữ nguyên)
                            st.caption(f"BH: {item_data['warranty_info']} | {item_data['condition']}")

                        with c_img:
                            img_link = str(item_data['image_url']).strip()
                            if not img_link: img_link = "https://via.placeholder.com/150/1e252b/FFFFFF?text=PGEAR"
                            st.markdown(f"""
                                <div style="width:100%; padding-top:100%; background:url('{img_link}') center/cover no-repeat; border-radius:8px; border:1px solid #30363d;"></div>
                            """, unsafe_allow_html=True)

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
                                db.update_status(item_data['id'], "Sẵn hàng" if is_sold else "Đã bán")
                                st.rerun()
                            if b2.button("SỬA", key=f"e_{item_data['id']}", type="secondary", use_container_width=True):
                                st.session_state.edit_id = item_data['id']
                                st.rerun()
                            if b3.button("XÓA", key=f"d_{item_data['id']}", type="secondary", use_container_width=True):
                                db.delete_product(item_data['id'])
                                st.rerun()
                        else:
                            st.markdown("---")
                            c_price_1, c_price_2 = st.columns([1, 2])
                            c_price_1.caption("GIÁ:")
                            c_price_2.markdown(f"<h3 style='color:#29b5e8; margin:0; text-align:right'>{item_data['sell_price']:,.0f}</h3>", unsafe_allow_html=True)
    else: 
        st.info("Chưa có dữ liệu.")

if __name__ == "__main__":
    main()