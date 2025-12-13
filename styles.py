CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=BBH+Bartle&display=swap');
            
    .stApp { overflow-y: auto !important; height: 100vh; }
    :root { --primary: #29b5e8; --success: #00c853; --danger: #ff5252; --text-sub: #9e9e9e; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #1e252b; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { background-color: #0e1117 !important; color: white !important; border: 1px solid #30363d !important; }
    
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; color: var(--primary) !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { color: var(--text-sub) !important; font-size: 0.8rem !important; text-transform: uppercase; }
    .stButton button { border-radius: 4px; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; }
    
    section[data-testid="stSidebar"][aria-expanded="false"] { display: none; }
    div[data-testid="InputInstructions"] { display: none !important; }
    
    /* Font tùy chỉnh cho tiêu đề */
    .bbh-bartle-regular {
        font-family: "BBH Bartle", sans-serif;
        font-weight: 400;
        font-style: normal;
        font-size: 6rem !important;
        color: white;
        margin: 0;
        line-height: 1.0; 
        padding-bottom: 20px;
    }
    
    /* Style cho thông tin liên hệ */
    .contact {
        font-weight: bold;
        font-size: 1rem !important;        
    }
</style>
"""