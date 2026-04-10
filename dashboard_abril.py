import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from io import BytesIO

# =========================
# CONFIG
# =========================
st.set_page_config(layout="wide")

# =========================
# ESTILO HUAWEI 🔴
# =========================
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    h1, h2, h3 {
        color: white;
    }
    .stMetric {
        background-color: #1c1f26;
        padding: 10px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# NAVEGACIÓN
# =========================
if "pagina" not in st.session_state:
    st.session_state.pagina = "portada"

# =========================
# PORTADA
# =========================
if st.session_state.pagina == "portada":

    st.markdown("""
        <div style='text-align: center; padding-top: 100px;'>
            <h1 style='color:red;'>HUAWEI</h1>
            <h2>Dashboard_Ejecutivo</h2>
            <h3>Avances_Exclusiones - Mes de Abril 2026</h3>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<h4 style='text-align:center;'>Fecha: {datetime.today().strftime('%d %B %Y')}</h4>", unsafe_allow_html=True)

    if st.button("🚀 Ver Dashboard"):
        st.session_state.pagina = "dashboard"
        st.rerun()

# =========================
# DASHBOARD
# =========================
if st.session_state.pagina == "dashboard":

    if st.button("⬅ Volver a Portada"):
        st.session_state.pagina = "portada"
        st.rerun()

    st.markdown("""
    # 🔴 Dashboard Ejecutivo
    ### Exclusiones Red Telecomunicaciones – Abril 2026
    """)

    archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx"])

    if archivo:
        df = pd.read_excel(archivo)

        # =========================
        # LIMPIEZA AUTOMÁTICA
        # =========================
        df.columns = df.columns.str.strip().str.lower()

        def buscar_columna(palabra):
            for col in df.columns:
                if palabra in col:
                    return col
            return None

        col_fecha = buscar_columna("fecha")
        col_excluido = buscar_columna("exclu")
        col_regional = buscar_columna("region")
        col_clasif = buscar_columna("clasif")
        col_ambito = buscar_columna("ambit")
        col_tiempo = buscar_columna("tiempo")

        if not all([col_fecha, col_excluido, col_regional, col_clasif, col_ambito, col_tiempo]):
            st.error("❌ No se encontraron todas las columnas necesarias")
            st.write(df.columns)
            st.stop()

        df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")

        # =========================
        # KPIs
        # =========================
        total = len(df)
        excluidos = len(df[df[col_excluido].str.upper() == "SI"])
        no_excluidos = len(df[df[col_excluido].str.upper() == "NO"])

        pct_excluidos = (excluidos / total) * 100
        pct_no_excluidos = (no_excluidos / total) * 100
        tiempo_prom = df[col_tiempo].mean()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Eventos Totales", total)
        col2.metric("Efectividad", f"{pct_excluidos:.1f}%")
        col3.metric("No Excluidos", f"{pct_no_excluidos:.1f}%")
        col4.metric("Tiempo Promedio", f"{tiempo_prom:.1f} h")

        # Barra visual
        st.progress(pct_excluidos / 100)
        st.caption(f"Efectividad de exclusión: {pct_excluidos:.1f}%")

        # =========================
        # ALERTA
        # =========================
        if pct_no_excluidos > 20:
            st.error("⚠️ Alto volumen de eventos NO excluidos – requiere acción inmediata")
        elif pct_no_excluidos > 10:
            st.warning("⚠️ Nivel medio de eventos NO excluidos")
        else:
            st.success("✅ Nivel controlado de exclusiones")

        # =========================
        # GRÁFICOS
        # =========================
        colg1, colg2 = st.columns(2)

        fig_estado = px.pie(df, names=col_excluido, color_discrete_sequence=["red", "gray"])
        colg1.plotly_chart(fig_estado, use_container_width=True)

        clasif = df[col_clasif].value_counts().reset_index()
        clasif.columns = ["Clasificación", "Casos"]

        fig_clasif = px.bar(clasif.head(7), x="Casos", y="Clasificación",
                            orientation="h", color="Casos", color_continuous_scale="Reds")
        colg2.plotly_chart(fig_clasif, use_container_width=True)

        # =========================
        # NO EXCLUIDOS
        # =========================
        st.markdown("## 🚨 Análisis NO Excluidos")

        df_no = df[df[col_excluido].str.upper() == "NO"]

        coln1, coln2 = st.columns(2)

        reg_no = df_no[col_regional].value_counts().reset_index()
        reg_no.columns = ["Regional", "Casos"]

        fig_reg = px.bar(reg_no, x="Casos", y="Regional",
                         orientation="h", color="Casos", color_continuous_scale="Reds")
        coln1.plotly_chart(fig_reg, use_container_width=True)

        amb_no = df_no[col_ambito].value_counts().reset_index()
        amb_no.columns = ["Ambito", "Casos"]

        fig_amb = px.pie(amb_no, names="Ambito", values="Casos")
        coln2.plotly_chart(fig_amb, use_container_width=True)

        # =========================
        # CAUSA RAÍZ
        # =========================
        st.markdown("## 🧠 Causa Raíz")

        matriz = df_no.groupby([col_clasif, col_ambito]).size().reset_index(name="Casos")

        fig_matriz = px.sunburst(matriz, path=[col_clasif, col_ambito], values="Casos")
        st.plotly_chart(fig_matriz, use_container_width=True)

        # =========================
        # CONCLUSIONES
        # =========================
        st.markdown("## 🧭 Conclusiones y Plan de Mejora")

        top_clasif = df_no[col_clasif].value_counts().idxmax()
        top_ambito = df_no[col_ambito].value_counts().idxmax()
        top_reg = df_no[col_regional].value_counts().idxmax()

        st.markdown(f"""
        ### 🔎 Hallazgos

        - Clasificación crítica: **{top_clasif}**
        - Ámbito dominante: **{top_ambito}**
        - Regional crítica: **{top_reg}**
        - % NO excluidos: **{pct_no_excluidos:.2f}%**

        ### 🚀 Plan de Mejora

        - Estandarizar criterios de exclusión  
        - Mejorar documentación de eventos  
        - Seguimiento a regional crítica  
        - Auditoría semanal  
        - Reducir NO excluidos en 10%  

        ### 🎯 Impacto

        - Mejora en indicadores  
        - Reducción de penalizaciones  
        """)

        # Mensaje ejecutivo
        st.markdown("""
        ---
        ### 📌 Mensaje Ejecutivo

        El análisis evidencia oportunidades claras de mejora en la gestión de exclusiones, 
        especialmente en la estandarización operativa y control de calidad.
        """)

        # =========================
        # DESCARGAS
        # =========================
        st.markdown("## 📥 Descargar")

        @st.cache_data
        def convertir_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        st.download_button("📊 Descargar Base", convertir_excel(df), "reporte.xlsx")
        st.download_button("🚨 Descargar NO Excluidos", convertir_excel(df_no), "no_excluidos.xlsx")