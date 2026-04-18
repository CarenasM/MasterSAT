import streamlit as st
import pandas as pd
import os

# =============================================================================
# CONFIGURACIÓN DE PÁGINA
# =============================================================================
st.set_page_config(page_title="MasterSAT Waldner", layout="wide")

# =============================================================================
# ESTILOS CSS MEJORADOS
# =============================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo general suave */
    .stApp {
        background-color: #F5F7FA;
    }

    /* Labels: uppercase, compactos, profesionales */
    .w-label {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-style: normal;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #6B7280;
        margin-bottom: 4px;
        margin-top: 12px;
    }

    /* Caudal consigna: tarjeta verde con gradiente */
    .w-caudal {
        background: linear-gradient(135deg, #D1FAE5, #A7F3D0);
        color: #065F46;
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        padding: 22px 16px;
        border-radius: 14px;
        border: none;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.25);
        margin-bottom: 20px;
        letter-spacing: -0.5px;
    }

    /* Factores: tarjetas blancas con sombra */
    .w-factor {
        background: #ffffff;
        color: #374151;
        font-size: 13px;
        font-weight: 600;
        text-align: center;
        padding: 18px 12px;
        border-radius: 14px;
        border: none;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .w-factor-val {
        font-size: 32px;
        font-weight: 800;
        display: block;
        margin-top: 8px;
        color: #1D4ED8;
        letter-spacing: -1px;
    }

    /* Xtras: tarjeta ámbar suave */
    .w-xtras-container {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        padding: 16px 20px;
        border-radius: 14px;
        margin-top: 20px;
    }
    .w-xtras-title {
        color: #92400E;
        font-weight: 700;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }
    .w-xtras-text {
        font-size: 15px;
        color: #78350F;
        text-align: center;
    }

    /* Botones de serie */
    div.stButton > button {
        font-weight: 600;
        border-radius: 10px;
        border: 2px solid #E5E7EB !important;
        background: #ffffff;
        color: #374151;
        transition: all 0.15s ease;
        font-size: 14px;
    }
    div.stButton > button:hover {
        border-color: #3B82F6 !important;
        color: #1D4ED8;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.18);
    }

    /* Tarjeta síntoma (averías) */
    .w-sintoma {
        background: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 15px;
        color: #7F1D1D;
    }

    /* Tarjeta solución (averías) */
    .w-solucion {
        background: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 14px 18px;
        border-radius: 10px;
        margin-bottom: 24px;
        font-size: 15px;
        color: #14532D;
    }

    /* Login hero */
    .w-login-hero {
        text-align: center;
        padding: 60px 0 30px;
    }
    .w-login-hero .icon { font-size: 52px; }
    .w-login-hero h1 {
        font-size: 30px;
        font-weight: 800;
        margin: 10px 0 4px;
        color: #111827;
    }
    .w-login-hero p {
        color: #6B7280;
        font-size: 15px;
        margin: 0;
    }

    /* Firma sidebar */
    .w-firma {
        text-align: center;
        padding: 16px 0 8px;
        color: #9CA3AF;
        font-size: 12px;
        letter-spacing: 0.05em;
        line-height: 1.6;
    }
    .w-firma span {
        font-weight: 700;
        color: #6B7280;
    }

    /* Icono botonera */
    .w-bot-icon img {
        border-radius: 12px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.15);
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# DICCIONARIO DE TRADUCCIONES
# =============================================================================
TEXTOS = {
    'ES': {
        'nav': "Navegación", 'caudales': "📊 Caudales", 'averias': "🛠 Averías", 'botonera': "🎹 Botonera",
        'serie': "Serie", 'dim': "Dimensión (mm)", 'mod': "Modelo", 'ano': "Año",
        'consigna': "Caudal Consigna (m³/h)",
        'sintoma': "Síntoma", 'solucion': "Solución", 'diag': "Diagnóstico", 'accion': "Acción",
        'buscar': "Búsqueda por palabra clave", 'logout': "Cerrar Sesión", 'lang_sel': "Idioma / Language",
        'modo_b': "Método de búsqueda", 'cascada': "Filtros Cascada", 'keyword': "Palabra Clave",
        'cont': "Controlador", 'login_sub': "Waldner · Acceso Restringido",
        'login_btn': "Entrar →", 'login_pwd': "Contraseña",
        'login_err': "❌ Contraseña incorrecta", 'sel_num': "Selecciona un número del mosaico"
    },
    'EN': {
        'nav': "Navigation", 'caudales': "📊 Airflows", 'averias': "🛠 Troubleshooting", 'botonera': "🎹 Control Panel",
        'serie': "Series", 'dim': "Dimension (mm)", 'mod': "Model", 'ano': "Year",
        'consigna': "Setpoint Airflow (m³/h)",
        'sintoma': "Symptom", 'solucion': "Solution", 'diag': "Diagnosis", 'accion': "Action",
        'buscar': "Keyword search", 'logout': "Logout", 'lang_sel': "Language / Idioma",
        'modo_b': "Search method", 'cascada': "Cascading Filters", 'keyword': "Keyword",
        'cont': "Controller", 'login_sub': "Waldner · Restricted Access",
        'login_btn': "Login →", 'login_pwd': "Password",
        'login_err': "❌ Incorrect password", 'sel_num': "Select a number from the mosaic"
    }
}

# =============================================================================
# HELPER: label + selectbox
# =============================================================================
def labeled_select(label: str, options, key: str):
    st.markdown(f'<p class="w-label">{label}</p>', unsafe_allow_html=True)
    return st.selectbox("", options, key=key, label_visibility="collapsed")

# =============================================================================
# SEGURIDAD — LOGIN
# =============================================================================
if "auth" not in st.session_state:
    st.session_state["auth"] = False
    st.session_state["lang"] = "ES"

if not st.session_state["auth"]:
    _, col_c, _ = st.columns([1, 1.6, 1])
    with col_c:
        st.markdown("""
            <div class="w-login-hero">
                <div class="icon">🔐</div>
                <h1>MasterSAT</h1>
                <p>Waldner · Acceso Restringido / Restricted Access</p>
            </div>
        """, unsafe_allow_html=True)
        pwd = st.text_input("", placeholder="Contraseña / Password", type="password")
        if st.button("Entrar / Login →", use_container_width=True):
            if pwd in [st.secrets["password_full"], st.secrets["password_guest"]]:
                st.session_state["auth"] = True
                st.session_state["access_level"] = "full" if pwd == st.secrets["password_full"] else "guest"
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta / Incorrect password")
    st.stop()

# =============================================================================
# SELECTOR DE IDIOMA EN SIDEBAR
# =============================================================================
st.sidebar.title(TEXTOS[st.session_state.lang]['lang_sel'])
c_l1, c_l2 = st.sidebar.columns(2)
if c_l1.button("Español 🇪🇸"):
    st.session_state.lang = "ES"; st.rerun()
if c_l2.button("English 🇬🇧"):
    st.session_state.lang = "EN"; st.rerun()

T = TEXTOS[st.session_state.lang]

# =============================================================================
# CARGA DE DATOS (cacheada)
# =============================================================================
@st.cache_data
def load_all_data(lang):
    df_c = pd.read_excel("datos_caudales.xlsx", sheet_name=lang).fillna("N/A").astype(str)
    df_c.columns = ['serie', 'dimension', 'modelo', 'año', 'consigna', 'factor-bypass', 'factor-lower', 'xtras']
    df_a = pd.read_excel("averias.xlsx", sheet_name=lang).fillna("N/A").astype(str)
    df_a.columns = ['controlador', 'modelo', 'sintoma', 'solucion']
    df_b = pd.read_excel("botonera.xlsx", sheet_name=lang, dtype=str).fillna("N/A")
    df_b.columns = ['id', 'situacion', 'texto', 'accion']
    return df_c, df_a, df_b

df_c, df_a, df_b = load_all_data(st.session_state.lang)

# =============================================================================
# MENÚ LATERAL
# =============================================================================
st.sidebar.divider()
st.sidebar.title(T['nav'])
opciones = [T['botonera']]
if st.session_state["access_level"] == "full":
    opciones = [T['caudales'], T['averias']] + opciones

choice = st.sidebar.radio("Ir a:", opciones)

if st.sidebar.button(T['logout']):
    st.session_state["auth"] = False; st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div class="w-firma">
        Desarrollado por<br>
        <span>C@renasM</span>
    </div>
""", unsafe_allow_html=True)

# =============================================================================
# SECCIÓN: CAUDALES
# =============================================================================
if choice == T['caudales']:
    st.title(T['caudales'])

    # Botones de serie
    st.markdown(f'<p class="w-label">{T["serie"]}</p>', unsafe_allow_html=True)
    series = sorted(df_c['serie'].unique())
    if "serie_sel" not in st.session_state:
        st.session_state.serie_sel = series[0]
    cols_s = st.columns(len(series))
    for i, s in enumerate(series):
        if cols_s[i].button(s, key=f"btn_{s}", use_container_width=True):
            st.session_state.serie_sel = s; st.rerun()

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    col_izq, col_der = st.columns([1, 1.5])

    with col_izq:
        df_f = df_c[df_c['serie'] == st.session_state.serie_sel]
        sel_dim = labeled_select(T['dim'], sorted(df_f['dimension'].unique()), key="sel_dim")
        df_f = df_f[df_f['dimension'] == sel_dim]
        sel_mod = labeled_select(T['mod'], sorted(df_f['modelo'].unique()), key="sel_mod")
        df_f = df_f[df_f['modelo'] == sel_mod]
        sel_ano = labeled_select(T['ano'], df_f['año'].unique(), key="sel_ano")
        df_f = df_f[df_f['año'] == sel_ano]

    with col_der:
        if not df_f.empty:
            res = df_f.iloc[0]
            st.markdown(f"""
                <p class="w-label" style="text-align:right">{T['consigna']}</p>
                <div class="w-caudal">{res['consigna']}</div>
            """, unsafe_allow_html=True)

            f_cols = st.columns(2)
            with f_cols[0]:
                st.markdown(f'<div class="w-factor">Factor-Bypass<span class="w-factor-val">{res["factor-bypass"]}</span></div>', unsafe_allow_html=True)
                st.image("fotos_caudales/bypass.jpg", use_container_width=True)
            with f_cols[1]:
                st.markdown(f'<div class="w-factor">Factor-Lower<span class="w-factor-val">{res["factor-lower"]}</span></div>', unsafe_allow_html=True)
                st.image("fotos_caudales/lower.jpg", use_container_width=True)

            if res['xtras'] not in ('N/A', ''):
                st.markdown(f"""
                    <div class="w-xtras-container">
                        <div class="w-xtras-title">✦ Xtras</div>
                        <div class="w-xtras-text">{res['xtras']}</div>
                    </div>
                """, unsafe_allow_html=True)

# =============================================================================
# SECCIÓN: AVERÍAS
# =============================================================================
elif choice == T['averias']:
    st.title(T['averias'])
    modo = st.radio(T['modo_b'], [T['cascada'], T['keyword']], horizontal=True)

    if modo == T['cascada']:
        c1, c2 = st.columns(2)
        with c1:
            cont_sel = st.selectbox(T['cont'], sorted(df_a['controlador'].unique()))
            df_af = df_a[df_a['controlador'] == cont_sel]
        with c2:
            mod_sel = st.selectbox(T['mod'], sorted(df_af['modelo'].unique()))
            df_af = df_af[df_af['modelo'] == mod_sel]

        sintoma_sel = st.selectbox(T['sintoma'], sorted(df_af['sintoma'].unique()))
        final = df_af[df_af['sintoma'] == sintoma_sel]

        for _, r in final.iterrows():
            st.markdown(f'<div class="w-sintoma">🚨 <b>{T["sintoma"]}:</b> {r["sintoma"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="w-solucion">✅ <b>{T["solucion"]}:</b> {r["solucion"]}</div>', unsafe_allow_html=True)

    else:
        q = st.text_input(T['buscar'])
        if q:
            res = df_a[df_a['sintoma'].str.contains(q, case=False, na=False)]
            if res.empty:
                st.info("No se encontraron resultados.")
            for _, r in res.iterrows():
                with st.expander(f"🚨 {r['sintoma']}"):
                    st.write(f"**{T['mod']}:** {r['modelo']}")
                    st.markdown(f'<div class="w-solucion">✅ <b>{T["solucion"]}:</b> {r["solucion"]}</div>', unsafe_allow_html=True)

# =============================================================================
# SECCIÓN: BOTONERA
# =============================================================================
elif choice == T['botonera']:
    st.title(T['botonera'])
    st.image("fotos_botonera/mosaico.jpg", use_container_width=True)

    st.markdown(f'<p class="w-label">{T["sel_num"]}</p>', unsafe_allow_html=True)
    idx = st.selectbox("", ["..."] + sorted(df_b['id'].unique().tolist(), key=int), label_visibility="collapsed")

    if idx != "...":
        fila = df_b[df_b['id'] == idx].iloc[0]
        st.divider()
        st.subheader(fila['situacion'])

        foto_path = f"fotos_botonera/{idx}.jpg"
        if os.path.exists(foto_path):
            st.markdown('<div class="w-bot-icon">', unsafe_allow_html=True)
            st.image(foto_path, width=80)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="w-sintoma">📝 <b>{T["diag"]}:</b> {fila["texto"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="w-solucion">🛠 <b>{T["accion"]}:</b> {fila["accion"]}</div>', unsafe_allow_html=True)
