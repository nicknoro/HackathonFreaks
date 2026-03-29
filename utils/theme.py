THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=Instrument+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Instrument Sans', sans-serif;
    background-color: #080c14;
    color: #dde3ed;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
    color: #f0f4ff !important;
}

code, .mono {
    font-family: 'DM Mono', monospace !important;
}

section[data-testid="stSidebar"] {
    background: #060910 !important;
    border-right: 1px solid #141c2e;
}
section[data-testid="stSidebar"] .stSlider > div > div > div {
    background: #3b6ff5 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p {
    color: #6b7fa3 !important;
    font-size: 0.78rem;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #a8b8d8 !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-family: 'DM Mono', monospace !important;
}

div[data-testid="metric-container"] {
    background: linear-gradient(145deg, #0d1321 0%, #111827 100%);
    border: 1px solid #1a2540;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.06);
}
div[data-testid="metric-container"] label {
    color: #4a5f85 !important;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: 'DM Mono', monospace !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #f0f4ff !important;
    line-height: 1.1;
}
div[data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
}

.stButton > button {
    background: transparent !important;
    border: 1px solid #1e2d4a !important;
    color: #7a8fba !important;
    border-radius: 10px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 0.82rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.02em;
}
.stButton > button:hover {
    background: #0f1c35 !important;
    border-color: #3b6ff5 !important;
    color: #c5d5f5 !important;
}
.stButton > button[kind="primary"] {
    background: #3b6ff5 !important;
    border-color: #3b6ff5 !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    background: #2d5de0 !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background: #0d1321 !important;
    border: 1px solid #1a2540 !important;
    color: #dde3ed !important;
    border-radius: 10px !important;
    font-family: 'Instrument Sans', sans-serif !important;
}
.stSelectbox > div > div:hover {
    border-color: #3b6ff5 !important;
}

div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #3b6ff5, #22c55e) !important;
    border-radius: 4px !important;
}

hr { border-color: #141c2e !important; }

div[data-testid="stAlert"] {
    background: #0d1321 !important;
    border-radius: 10px !important;
    border-left-width: 3px !important;
}

.stDataFrame {
    border: 1px solid #1a2540 !important;
    border-radius: 12px !important;
    overflow: hidden;
}
thead th {
    background: #0d1321 !important;
    color: #4a5f85 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #4a5f85;
    border-radius: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
}
.stTabs [aria-selected="true"] {
    background: #0f1c35 !important;
    color: #c5d5f5 !important;
    border-bottom: 2px solid #3b6ff5 !important;
}

.card {
    background: linear-gradient(145deg, #0d1321, #111827);
    border: 1px solid #1a2540;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: transform 0.2s ease;
}
.card:hover { transform: translateY(-2px); }

.tag {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 8px;
}
.tag-green  { background: #052010; color: #22c55e; border: 1px solid #15532e; }
.tag-amber  { background: #1a1100; color: #f59e0b; border: 1px solid #4d3000; }
.tag-red    { background: #1a0505; color: #ef4444; border: 1px solid #4d1111; }
.tag-blue   { background: #05102a; color: #3b6ff5; border: 1px solid #1a3070; }

.hero-line {
    font-family: 'Syne', sans-serif;
    font-size: 0.82rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #3b6ff5;
    margin-bottom: 4px;
}
.hero-tagline {
    font-family: 'Instrument Sans', sans-serif;
    font-size: 1rem;
    color: #4a5f85;
    margin-top: 4px;
    font-weight: 300;
}
</style>
"""
