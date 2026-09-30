import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Detección de Fallos Eléctricos",
    page_icon="⚡",
    layout="wide"
)

# Título y encabezado
st.title("⚡ Detección y Clasificación de Fallos Eléctricos")
st.write("Prototipo de diagnóstico en tiempo real mediante Machine Learning e IA Explicable (XAI).")

# Sidebar para ingreso de lecturas
st.sidebar.header("Lecturas Trifásicas")
va = st.sidebar.number_input("Voltaje Fase A (Va p.u.)", value=1.0)
ia = st.sidebar.number_input("Corriente Fase A (Ia A)", value=100.0)

# Botón de prueba
if st.sidebar.button("Ejecutar Diagnóstico"):
    st.success(f"Diagnóstico procesado correctamente para Va = {va} p.u. e Ia = {ia} A")