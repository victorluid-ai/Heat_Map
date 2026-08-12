import streamlit as st

from ..design.tokens import (
    ACCENT_GRADIENT,
    ACCENT_PRIMARY,
    ACCENT_SECONDARY,
    BG_ELEVATED,
    BG_PRIMARY,
    BG_SECONDARY,
    BORDER_ACCENT,
    BORDER_DEFAULT,
    CHART_GRID,
    RADIUS_LG,
    RADIUS_MD,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


def inject_global_styles() -> None:
    """Inject global CSS for a modern tech dashboard look."""
    st.markdown(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet">
        <style>
            html, body, [class*="css"] {{
                font-family: 'Inter', system-ui, sans-serif;
            }}

            /* Hide default Streamlit header/footer chrome */
            header[data-testid="stHeader"] {{
                background: transparent;
            }}
            #MainMenu, footer {{
                visibility: hidden;
            }}

            /* Sidebar styling */
            section[data-testid="stSidebar"] {{
                background: linear-gradient(180deg, {BG_SECONDARY} 0%, {BG_PRIMARY} 100%);
                border-right: 1px solid {BORDER_DEFAULT};
            }}
            section[data-testid="stSidebar"] .stMarkdown h1 {{
                font-size: 1.25rem;
                font-weight: 700;
                background: {ACCENT_GRADIENT};
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.25rem;
            }}

            /* Page titles */
            h1 {{
                font-weight: 700 !important;
                letter-spacing: -0.02em;
            }}

            /* Metric cards */
            div[data-testid="stMetric"] {{
                background: {BG_ELEVATED};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_MD};
                padding: 1rem 1.25rem;
                box-shadow: 0 4px 24px rgba(0, 212, 255, 0.04);
            }}
            div[data-testid="stMetric"] label {{
                color: {TEXT_SECONDARY} !important;
                font-size: 0.8rem !important;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
                color: {ACCENT_PRIMARY} !important;
                font-weight: 700 !important;
            }}

            /* Buttons */
            .stButton > button {{
                border-radius: {RADIUS_MD};
                border: 1px solid {BORDER_DEFAULT};
                transition: all 0.2s ease;
            }}
            .stButton > button[kind="primary"],
            .stButton > button[data-testid="baseButton-primary"] {{
                background: {ACCENT_GRADIENT};
                border: none;
                color: {BG_PRIMARY};
                font-weight: 600;
            }}
            .stButton > button:hover {{
                border-color: {ACCENT_PRIMARY};
                box-shadow: 0 0 16px rgba(0, 212, 255, 0.15);
            }}

            /* Forms & inputs */
            .stTextInput input, .stSelectbox div[data-baseweb="select"] > div,
            .stDateInput input, .stMultiSelect div[data-baseweb="select"] > div {{
                background: {BG_ELEVATED} !important;
                border-color: {BORDER_DEFAULT} !important;
                border-radius: {RADIUS_SM} !important;
                color: {TEXT_PRIMARY} !important;
            }}
            .stTextInput input:focus {{
                border-color: {ACCENT_PRIMARY} !important;
                box-shadow: 0 0 0 1px {ACCENT_PRIMARY} !important;
            }}

            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {{
                gap: 8px;
                background: transparent;
            }}
            .stTabs [data-baseweb="tab"] {{
                background: {BG_ELEVATED};
                border-radius: {RADIUS_SM};
                border: 1px solid {BORDER_DEFAULT};
                color: {TEXT_SECONDARY};
                padding: 0.5rem 1.25rem;
            }}
            .stTabs [aria-selected="true"] {{
                background: {BG_ELEVATED} !important;
                border-color: {ACCENT_PRIMARY} !important;
                color: {ACCENT_PRIMARY} !important;
            }}

            /* Dataframes */
            div[data-testid="stDataFrame"] {{
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_MD};
                overflow: hidden;
            }}

            /* Expanders */
            .streamlit-expanderHeader {{
                background: {BG_ELEVATED};
                border-radius: {RADIUS_SM};
                border: 1px solid {BORDER_DEFAULT};
            }}

            /* Dividers */
            hr {{
                border-color: {BORDER_DEFAULT} !important;
                opacity: 0.5;
            }}

            /* Info/warning/error boxes */
            .stAlert {{
                border-radius: {RADIUS_MD};
                border: 1px solid {BORDER_DEFAULT};
            }}

            /* Custom utility classes */
            .hm-brand-subtitle {{
                color: {TEXT_MUTED};
                font-size: 0.75rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-top: 0;
            }}
            .hm-page-header {{
                margin-bottom: 1.5rem;
            }}
            .hm-page-header h2 {{
                margin: 0;
                font-size: 1.75rem;
                font-weight: 700;
                color: {TEXT_PRIMARY};
            }}
            .hm-page-header p {{
                margin: 0.25rem 0 0;
                color: {TEXT_SECONDARY};
                font-size: 0.95rem;
            }}
            .hm-panel {{
                background: {BG_ELEVATED};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_LG};
                padding: 1.25rem;
                margin-bottom: 1rem;
            }}
            .hm-panel-title {{
                color: {TEXT_PRIMARY};
                font-weight: 600;
                font-size: 1rem;
                margin-bottom: 0.75rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            .hm-icon {{
                font-family: 'Material Symbols Outlined';
                font-size: 1.25rem;
                color: {ACCENT_PRIMARY};
                vertical-align: middle;
            }}
            .hm-login-card {{
                max-width: 420px;
                margin: 2rem auto;
                background: {BG_ELEVATED};
                border: 1px solid {BORDER_ACCENT};
                border-radius: {RADIUS_LG};
                padding: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 40px rgba(0, 212, 255, 0.05);
            }}
            .hm-login-brand {{
                text-align: center;
                margin-bottom: 1.5rem;
            }}
            .hm-login-brand h1 {{
                font-size: 1.75rem;
                background: {ACCENT_GRADIENT};
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.25rem;
            }}
            .hm-user-badge {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 0.75rem;
                background: {BG_ELEVATED};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_SM};
                font-size: 0.8rem;
                color: {TEXT_SECONDARY};
                margin-bottom: 0.5rem;
            }}
            .hm-user-badge .hm-icon {{
                font-size: 1rem;
                color: {ACCENT_SECONDARY};
            }}
            .hm-filter-bar {{
                background: {BG_ELEVATED};
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_MD};
                padding: 1rem 1.25rem;
                margin-bottom: 1.5rem;
            }}
            .hm-stream-frame {{
                border: 1px solid {BORDER_DEFAULT};
                border-radius: {RADIUS_MD};
                overflow: hidden;
                background: {BG_PRIMARY};
            }}
            .hm-stream-frame img {{
                display: block;
                width: 100%;
            }}

            /* Option menu overrides (streamlit-option-menu) */
            .nav-link {{
                font-size: 0.9rem !important;
                font-weight: 500 !important;
            }}
            .nav-link-selected {{
                background: {BG_ELEVATED} !important;
                border: 1px solid {ACCENT_PRIMARY} !important;
                border-radius: {RADIUS_SM} !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, icon: str) -> None:
    """Render a consistent page header with Material icon."""
    st.markdown(
        f"""
        <div class="hm-page-header">
            <h2><span class="hm-icon">{icon}</span> {title}</h2>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def panel_title(title: str, icon: str) -> None:
    """Render a section panel title with icon."""
    st.markdown(
        f'<div class="hm-panel-title"><span class="hm-icon">{icon}</span> {title}</div>',
        unsafe_allow_html=True,
    )


def filter_bar_start() -> None:
    st.markdown('<div class="hm-filter-bar">', unsafe_allow_html=True)


def filter_bar_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)
