import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MasterSAT Waldner", layout="wide")

# --- ESTILOS CSS (Interfaz Fiel) ---
st.markdown("""
    <style>
    .w-label { font-family: 'Arial', sans-serif; font-size: 24px; font-style: italic; margin-bottom: -5px; }
    .w-caudal { background-color: #90EE90; color: #2e7d32; font-size: 26px; font-weight: bold; text-align: center; padding: 15px; border-radius: 8px; border: 2px solid #2e7d32; margin-bottom: 20px; }
    .w-factor { background-color: #E3F2FD; color: #1976D2; font-size: 22px; font-weight: bold; text-align: center; padding: 10px; border-radius: 8px; border: 1px solid #2196F3; }
    .w-factor-val { font-size: 28px; display: block; margin-top: 5px; }
    .w-xtras-container { border: 1px solid black; padding: 15px; border-radius: 5px; margin-top: 20px; background-color: white; }
    .w-xtras-title { color: red; font-style: italic; font-weight: bold; font-size: 18px; text-align: center; margin-bottom: 5px; }
    .w-xtras-text { font-size: 16px; text-align: center; }
    
    /* Colores fijos para botones de Serie */
    div.stButton > button { font-weight: bold; border: 1px solid #333 !important; }
    </style>
""", unsafe_allow_html=True)

# --- DICCIONARIO DE TRADUCCIONES ---
TEXTOS = {
    'ES': {
        'nav': "Navegación", 'caudales': "📊 Caudales", 'averias': "🛠 Averías", 'botonera': "🎹 Botonera",
        'serie': "Serie", 'dim': "Dimensión (mm)", 'mod': "Modelo", 'ano': "Año", 'consigna': "Caudal Consigna (m³/h)",
        'sintoma': "Síntoma", 'solucion': "Solución", 'diag': "Diagnóstico", 'accion': "Acción",
        'buscar': "Búsqueda por palabra clave", 'logout': "Cerrar Sesión", 'lang_sel': "Idioma / Language"
    },
    'EN': {
        'nav': "Navigation", 'caudales': "📊 Airflows", 'averias': "🛠 Troubleshooting", 'botonera': "🎹 Control Panel",
        'serie': "Series", 'dim': "Dimension (mm)", 'mod': "Model", 'ano': "Year", 'consigna': "Setpoint Airflow (m³/h)",
        'sintoma': "Symptom", 'solucion': "Solution", 'diag': "Diagnosis", 'accion': "Action",
        'buscar': "Keyword search", 'logout': "Logout", 'lang_sel': "Language / Idioma"
    }
}

# --- SEGURIDAD (SECRETS) ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
    st.session_state["lang"] = "ES"

if not st.session_state["auth"]:
    st.title("🔐 MasterSAT - Acceso Restringido")
    pwd = st.text_input("Contraseña / Password:", type="password")
    if st.button("Entrar / Login"):
        if pwd == st.secrets["password_full"]:
            st.session_state["auth"] = True
            st.session_state["access_level"] = "full"
            st.rerun()
        elif pwd == st.secrets["password_guest"]:
            st.session_state["auth"] = True
            st.session_state["access_level"] = "guest"
            st.rerun()
        else:
            st.error("Incorrecto / Incorrect")
    st.stop()

# --- SELECTOR DE IDIOMA ---
st.sidebar.title(TEXTOS[st.session_state.lang]['lang_sel'])
c_l1, c_l2 = st.sidebar.columns(2)
if c_l1.button("Español 🇪🇸"): 
    st.session_state.lang = "ES"
    st.rerun()
if c_l2.button("English 🇬🇧"): 
    st.session_state.lang = "EN"
    st.rerun()

T = TEXTOS[st.session_state.lang]

# --- CARGA DE DATOS ---
@st.cache_data
def load_all_data(lang):
    df_c = pd.read_excel("datos_caudales.xlsx", sheet_name=lang).fillna("N/A").astype(str)
    df_c.columns = [str(c).strip().lower() for c in df_c.columns]
    df_a = pd.read_excel("averias.xlsx", sheet_name=lang).astype(str)
    df_b = pd.read_excel("botonera.xlsx", sheet_name=lang, dtype=str)
    return df_c, df_a, df_b

df_c, df_a, df_b = load_all_data(st.session_state.lang)

# --- MENÚ LATERAL ---
st.sidebar.divider()
st.sidebar.title(T['nav'])
opciones = [T['botonera']]
if st.session_state["access_level"] == "full":
    opciones = [T['caudales'], T['averias']] + opciones

choice = st.sidebar.radio("Ir a:", opciones)

if st.sidebar.button(T['logout']):
    st.session_state["auth"] = False
    st.rerun()

# --- FIRMA ---
st.sidebar.markdown("---")
st.sidebar.markdown('<div style="text-align: center; color: gray; font-style: italic;">By C@renasM</div>', unsafe_allow_html=True)

# --- CONTENIDO PRINCIPAL ---

if choice == T['caudales']:
    st.title(T['caudales'])
    st.markdown(f'<p class="w-label">{T["serie"]}</p>', unsafe_allow_html=True)
    series = sorted(df_c['serie'].unique())
    if "serie_sel" not in st.session_state: st.session_state.serie_sel = series[0]
    
    cols_s = st.columns(len(series))
    for i, s in enumerate(series):
        if cols_s[i].button(s, key=f"btn_{s}", use_container_width=True):
            st.session_state.serie_sel = s
            st.rerun()

    st.write("")
    col_izq, col_der = st.columns([1, 1.5])

    with col_izq:
        df_f = df_c[df_c['serie'] == st.session_state.serie_sel]
        st.markdown(f'<p class="w-label">{T["dim"]}</p>', unsafe_allow_html=True)
        sel_dim = st.selectbox("dim", sorted(df_f['dimension'].unique()), label_visibility="collapsed")
        df_f = df_f[df_f['dimension'] == sel_dim]
        
        st.markdown(f'<p class="w-label">{T["mod"]}</p>', unsafe_allow_html=True)
        sel_mod = st.selectbox("mod", sorted(df_f['modelo'].unique()), label_visibility="collapsed")
        df_f = df_f[df_f['modelo'] == sel_mod]
        
        st.markdown(f'<p class="w-label">{T["ano"]}</p>', unsafe_allow_html=True)
        sel_ano = st.selectbox("ano", df_f['año'].unique(), label_visibility="collapsed")
        df_f = df_f[df_f['año'] == sel_ano]

    with col_der:
        if not df_f.empty:
            res = df_f.iloc[0]
            st.markdown(f'<div style="text-align:right;"><b>{T["consigna"]}</b><div class="w-caudal">{res["consigna"]}</div></div>', unsafe_allow_html=True)
            f_cols = st.columns(2)
            with f_cols[0]:
                st.markdown(f'<div class="w-factor">Factor-Bypass<br><span class="w-factor-val">{res["factor-bypass"]}</span></div>', unsafe_allow_html=True)
                st.image("fotos_caudales/bypass.jpg")
            with f_cols[1]:
                st.markdown(f'<div class="w-factor">Factor-Lower<br><span class="w-factor-val">{res["factor-lower"]}</span></div>', unsafe_allow_html=True)
                st.image("fotos_caudales/lower.jpg")
            st.markdown(f'<div class="w-xtras-container"><div class="w-xtras-title">Xtras</div><div class="w-xtras-text">{res["xtras"]}</div></div>', unsafe_allow_html=True)

elif choice == T['averias']:
    st.title(T['averias'])
    q = st.text_input(T['buscar'])
    if q:
        mask = df_a.iloc[:, 2].str.contains(q, case=False, na=False)
        res = df_a[mask]
        for _, r in res.iterrows():
            with st.expander(f"🚨 {r.iloc[2]}"):
                st.write(f"**{T['solucion']}:**")
                st.success(r.iloc[3])

elif choice == T['botonera']:
    st.title(T['botonera'])
    st.image("fotos_botonera/mosaico.jpg")
    idx = st.selectbox("#", ["..."] + sorted(df_b.iloc[:, 0].unique().tolist(), key=int))
    if idx != "...":
        fila = df_b[df_b.iloc[:, 0] == idx].iloc[0]
        st.divider()
        st.subheader(fila.iloc[1])
        st.image(f"fotos_botonera/{idx}.jpg", width=400)
        st.info(f"**{T['diag']}:** {fila.iloc[2]}")
        st.success(f"**{T['accion']}:** {fila.iloc[3]}")