CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=BBH+Bartle&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            
    /* --- CẤU HÌNH CHUNG --- */
    .stApp { 
        background-color: #0b0e11; /* Nền tối hơn một chút */
        font-family: 'Inter', sans-serif;
    }
    
    div.block-container {
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        max-width: 95% !important;
    }

    :root { 
        --primary: #29b5e8; 
        --primary-glow: rgba(41, 181, 232, 0.5);
        --success: #00e676; /* Xanh lá tươi hơn */
        --success-glow: rgba(0, 230, 118, 0.4);
        --text-sub: #b0b3b8; 
        --bg-card: #161b22; /* Màu card mới */
        --bg-card-hover: #1c2128;
        --border-color: #30363d;
    }

    /* Tùy chỉnh thanh cuộn cho chất gaming */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: #0b0e11; }
    ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

    /* --- MOBILE RESPONSIVE --- */
    @media only screen and (max-width: 600px) {
        .hero-title { font-size: 2.5rem !important; }
        .hero-box { height: 220px !important; }
        button { min-height: 48px !important; font-weight: 600 !important;}
    }
    
    /* --- BANNER STYLE (MỚI) --- */
    .hero-box {
        position: relative;
        width: 100%;
        height: 380px;
        overflow: hidden;
        background-position: center;
        background-size: cover;
        background-repeat: no-repeat;
        margin-top: 1rem;
        margin-bottom: 2.5rem;
        border-radius: 16px;
        /* Hiệu ứng viền sáng nhẹ */
        box-shadow: 0 0 20px rgba(0,0,0,0.5), inset 0 0 0 1px rgba(255,255,255,0.1);
    }
    
    .hero-overlay {
        position: absolute; inset: 0;
        /* Gradient chéo hiện đại hơn */
        background: linear-gradient(to top right, rgba(11,14,17, 0.95), rgba(11,14,17, 0.2));
        display: flex; flex-direction: column;
        justify-content: flex-end; padding: 3rem;
    }

    .hero-title {
        font-family: 'BBH Bartle', sans-serif;
        font-size: 4rem; color: white;
        text-shadow: 0 0 25px var(--primary-glow);
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem; color: var(--primary);
        font-weight: 700; letter-spacing: 3px; text-transform: uppercase;
        text-shadow: 0 0 10px var(--primary-glow);
    }

    /* --- CARD STYLE (REMASTERED) --- */
    /* Loại bỏ border cứng, dùng shadow và màu nền để tạo khối */
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        background-color: var(--bg-card); 
        border: 1px solid transparent; /* Ẩn border mặc định */
        border-radius: 16px; 
        padding: 0px; 
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Hiệu ứng Hover: Nổi lên và phát sáng neon */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px) scale(1.01);
        background-color: var(--bg-card-hover);
        border-color: var(--primary);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3), 0 0 15px var(--primary-glow);
    }

    /* Style cho các nút bấm */
    .stButton button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    /* Nút Primary (Chi tiết) sẽ sáng hơn */
    .stButton button[kind="primary"] {
        background-color: var(--primary) !important;
        border: none !important;
        box-shadow: 0 0 10px var(--primary-glow);
    }
    .stButton button[kind="primary"]:hover {
        box-shadow: 0 0 20px var(--primary-glow);
    }

    /* --- STYLE CHO POPUP DIALOG (MỚI) --- */
    /* Badge (Huy hiệu) cho Category/Condition */
    .detail-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .badge-blue { background: rgba(41, 181, 232, 0.15); color: var(--primary); border: 1px solid var(--primary-glow); }
    .badge-green { background: rgba(0, 230, 118, 0.15); color: var(--success); border: 1px solid var(--success-glow); }
    .badge-gray { background: rgba(255, 255, 255, 0.1); color: var(--text-sub); }

    /* Info Row trong popup */
    .detail-info-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #30363d;
        font-size: 0.95rem;
    }
    .detail-label { color: var(--text-sub); }
    .detail-value { color: white; font-weight: 600; }

    /* Giá trong popup */
    .detail-price-box {
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin: 10px 0;
        border: 1px solid var(--success-glow);
    }
    .detail-price-label { color: var(--success); font-size: 1.2rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;}
    .detail-price-value { color: var(--success); font-size: 1.2rem; font-weight: 800; text-shadow: 0 0 15px var(--success-glow); }

    /* Contact bar trong popup */
    .detail-contact-bar {
        background: #1c2128;
        padding: 15px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: 500;
        border: 1px solid #30363d;
    }

    /* Ẩn các thành phần thừa */
    section[data-testid="stSidebar"][aria-expanded="false"] { display: none; }
    div[data-testid="InputInstructions"] { display: none !important; }
    header { visibility: hidden; }
</style>
"""