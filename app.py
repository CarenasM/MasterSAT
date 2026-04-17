import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="MasterSAT Waldner", layout="wide")

# --- ESTILOS CSS (Fiel al Excel de Caudales) ---
st.markdown("""
    <style>
    .w-label { font-family: 'Arial', sans-serif; font-size: 24px; font-style: italic; margin-bottom: -5px; }
    .w-caudal { background-color: #90EE90; color: #2e7d32; font-size: 26px; font-weight: bold; text-align: center; padding: 15px; border-radius: 8px; border: 2px solid #2e7d32; margin-bottom: 20px; }
    .w-factor { background-color: #E3F2FD; color: #1976D2; font-size: 22px; font-weight: bold; text-align: center; padding: 10px; border-radius: 8px; border: 1px solid #2196F3; }
    .w-factor-val { font-size: 28px; display: block; margin-top: 5px; }
    .w-xtras-container { border: 1px solid black; padding: 15px; border-radius: 5px; margin-top: 20px; background-color: white; }
    .w-xtras-title { color: red; font-style: italic; font-weight: bold; font-size: 18px; text-align: center; margin-bottom: 5px; }
    .w-xtras-text { font-size: 16px; text-align: center; }
    
    /* Colores dinámicos para botones de Serie */
    :root {
        --st-btn-w90-bg: #E6B89C; --st-btn-mc6-bg: #E6E6E6;
        --st-btn-scala-bg: #737373; --st-btn-si3-bg: #DDE2EC;
    }
    </style>
""", unsafe_allow_html=True)

# --- SEGURIDAD (SECRETS) ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False
    st.session_state["access_level"] = None

if not st.session_state["auth"]:
    st.title("🔐 MasterSAT - Acceso Restringido")
    pwd = st.text_input("Introduce la contraseña:", type="password")
    if st.button("Entrar"):
        if pwd == st.secrets["password_full"]:
            st.session_state["auth"] = True
            st.session_state["access_level"] = "full"
            st.rerun()
        elif pwd == st.secrets["password_guest"]:
            st.session_state["auth"] = True
            st.session_state["access_level"] = "guest"
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# --- CARGA DE DATOS ---
@st.cache_data
def load_all_data():
    # Cargamos caudales con limpieza para la interfaz fiel
    df_c = pd.read_excel("datos_caudales.xlsx").fillna("N/A").astype(str)
    df_c.columns = [str(c).strip().lower() for c in df_c.columns]
    
    df_a = pd.read_excel("averias.xlsx", sheet_name="ES").astype(str)
    df_b = pd.read_excel("botonera.xlsx", sheet_name="ES", dtype=str)
    return df_c, df_a, df_b

df_c, df_a, df_b = load_all_data()

# --- NAVEGACIÓN LATERAL ---
st.sidebar.title("MasterSAT 🛠")
opciones = ["🎹 Botonera"]
if st.session_state["access_level"] == "full":
    opciones = ["📊 Caudales", "🛠 Averías"] + opciones

choice = st.sidebar.radio("Herramienta:", opciones)

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["auth"] = False
    st.rerun()

# --- CONTENIDO ---

if choice == "📊 Caudales":
    st.title("📊 Configurador de Caudales")
    
    # Botones de Serie (Lógica fiel)
    st.markdown('<p class="w-label">Serie</p>', unsafe_allow_html=True)
    series_disponibles = sorted(df_c['serie'].unique())
    if "serie_sel" not in st.session_state: st.session_state.serie_sel = series_disponibles[0]
    
    cols_s = st.columns(len(series_disponibles))
    for i, s in enumerate(series_disponibles):
        if cols_s[i].button(s, key=f"btn_{s}", use_container_width=True):
            st.session_state.serie_sel = s
            st.rerun()

    st.write("")
    col_izq, col_der = st.columns([1, 1.5])

    with col_izq:
        df_f = df_c[df_c['serie'] == st.session_state.serie_sel]
        st.markdown('<p class="w-label">Dimensión (mm)</p>', unsafe_allow_html=True)
        sel_dim = st.selectbox("", sorted(df_f['dimension'].unique()), label_visibility="collapsed")
        df_f = df_f[df_f['dimension'] == sel_dim]
        
        st.markdown('<p class="w-label">Modelo</p>', unsafe_allow_html=True)
        sel_mod = st.selectbox("", sorted(df_f['modelo'].unique()), label_visibility="collapsed")
        df_f = df_f[df_f['modelo'] == sel_mod]
        
        st.markdown('<p class="w-label">Año</p>', unsafe_allow_html=True)
        sel_ano = st.selectbox("", df_f['año'].unique(), label_visibility="collapsed")
        df_f = df_f[df_f['año'] == sel_ano]

    with col_der:
        if not df_f.empty:
            res = df_f.iloc[0]
            st.markdown(f'<div style="text-align:right;"><b>Caudal Consigna (m³/h)</b><div class="w-caudal">{res["consigna"]}</div></div>', unsafe_allow_html=True)
            
            f1, f2 = st.columns(2)
            # Nota: Asegúrate de tener la carpeta 'fotos_caudales' en tu GitHub
            with f1:
                st.markdown(f'<div class="w-factor">Factor-Bypass<br><span class="w-factor-val">{res["factor-bypass"]}</span></div>', unsafe_allow_html=True)
                path_bp = "fotos_caudales/bypass.jpg"
                st.image(path_bp if os.path.exists(path_bp) else "https://via.placeholder.com/200?text=Bypass")
            with f2:
                st.markdown(f'<div class="w-factor">Factor-Lower<br><span class="w-factor-val">{res["factor-lower"]}</span></div>', unsafe_allow_html=True)
                path_lw = "fotos_caudales/lower.jpg"
                st.image(path_lw if os.path.exists(path_lw) else "https://via.placeholder.com/200?text=Lower")
            
            st.markdown(f'<div class="w-xtras-container"><div class="w-xtras-title">Xtras</div><div class="w-xtras-text">{res["xtras"]}</div></div>', unsafe_allow_html=True)

elif choice == "🛠 Averías":
    st.title("🛠 Resolución de Averías")
    modo = st.radio("Búsqueda:", ["Filtros", "Palabra Clave"], horizontal=True)
    if modo == "Filtros":
        c1, c2 = st.columns(2)
        with c1:
            cont = st.selectbox("Controlador:", sorted(df_a.iloc[:, 0].unique()))
            df_af = df_a[df_a.iloc[:, 0] == cont]
        with c2:
            amod = st.selectbox("Modelo:", sorted(df_af.iloc[:, 1].unique()))
            df_af = df_af[df_af.iloc[:, 1] == amod]
        sintoma = st.selectbox("Síntoma:", sorted(df_af.iloc[:, 2].unique()))
        final = df_af[df_af.iloc[:, 2] == sintoma]
        for _, r in final.iterrows():
            st.warning(f"🚨 **SÍNTOMA:** {r.iloc[2]}")
            st.success(f"✅ **SOLUCIÓN:** {r.iloc[3]}")
    else:
        q = st.text_input("Escribe el síntoma:")
        if q:
            res = df_a[df_a.iloc[:, 2].str.contains(q, case=False, na=False)]
            for _, r in res.iterrows():
                with st.expander(f"🚨 {r.iloc[2]}"): st.write(r.iloc[3])

elif choice == "🎹 Botonera":
    st.title("🎹 Guía de Botonera")
    st.image("fotos_botonera/mosaico.jpg")
    idx = st.selectbox("Selecciona Número:", ["..."] + sorted(df_b.iloc[:, 0].unique().tolist(), key=int))
    if idx != "...":
        fila = df_b[df_b.iloc[:, 0] == idx].iloc[0]
        st.divider()
        st.subheader(fila.iloc[1])
        path_bot = f"fotos_botonera/{idx}.jpg"
        if os.path.exists(path_bot): st.image(path_bot, width=400)
        st.info(f"**Diagnóstico:** {fila.iloc[2]}")
        st.success(f"**Acción:** {fila.iloc[3]}")