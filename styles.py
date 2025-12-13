CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=BBH+Bartle&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
            
    .stApp { 
        background-color: #0e1117;
    }
    
    div.block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        max-width: 95% !important;
    }

    :root { 
        --primary: #29b5e8; 
        --success: #00c853; 
        --text-sub: #9e9e9e; 
        --bg-card: #1e252b;
        --border-color: #30363d;
    }
    
    /* --- BANNER STYLE --- */
    .hero-box {
        position: relative;
        width: 100%;
        height: 350px;
        overflow: hidden;
        background-position: center;
        background-size: cover;
        background-repeat: no-repeat;
        margin-top: 1.5rem;
        margin-bottom: 2rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border-radius: 12px;
    }
    
    .hero-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to right, rgba(14,17,23, 0.95) 0%, rgba(14,17,23, 0.3) 60%, transparent 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding-left: 3rem;
    }

    .hero-title {
        font-family: 'BBH Bartle', sans-serif;
        font-size: 3.5rem;
        color: white;
        line-height: 1;
        text-shadow: 0 0 20px rgba(41, 181, 232, 0.6);
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        color: var(--primary);
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    /* --- INPUT STYLE --- */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] { 
        background-color: var(--bg-card) !important; 
        color: white !important; 
        border: 1px solid var(--border-color) !important; 
        border-radius: 8px !important;
    }
    
    /* --- CARD STYLE (KHUNG SẢN PHẨM) --- */
    div[data-testid="stVerticalBlockBorderWrapper"] { 
        background-color: var(--bg-card); 
        border: 1px solid var(--border-color); 
        border-radius: 12px; 
        padding: 12px; /* Tăng khoảng cách đệm bên trong */
        margin-bottom: 0.5rem;
        transition: all 0.2s ease-in-out;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--primary);
        transform: translateY(-2px);
    }
    
    section[data-testid="stSidebar"][aria-expanded="false"] { display: none; }
    div[data-testid="InputInstructions"] { display: none !important; }
    header { visibility: hidden; }
</style>
"""