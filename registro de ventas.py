import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Tu JSON de service account (sube a Replit o secrets)
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
)
gc = gspread.authorize(creds)
sh = gc.open("Ventas Modelos Simple 2026")

# Cargar modelos
ws_modelos = sh.worksheet("Modelos")
modelos = ws_modelos.col_values(1)[1:]  # Desde A
2
# Cargar ventas
ws_ventas = sh.worksheet("Ventas")
ventas = pd.DataFrame(ws_ventas.get_all_records())

st.title("Ventas Modelos")

# Pantalla 1: Lista de modelos clickable
st.header("Modelos")
for modelo in modelos:
    if st.button(modelo, key=modelo):
        st.session_state.selected_modelo = modelo

# Pantalla 2: Formulario de registro
if "selected_modelo" in st.session_state:
    st.header(f"Registro para {st.session_state.selected_modelo}")
    monto = st.number_input("Monto USD", min_value=0.0)
    servicio = st.selectbox("Servicio", ["Sexting", "Llamada", "Custom Video", "GFE"])
    metodo = st.selectbox("Método de Pago", ["CashApp", "Venmo", "PayPal", "Zelle", "Throne", "Amazon Gift Card", "Crypto"])
    if st.button("Guardar"):
        if monto > 0:
            nueva = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), st.session_state.selected_modelo, monto, servicio, metodo]
            ws_ventas.append_row(nueva)
            st.success("Guardado!")
            del st.session_state.selected_modelo
        else:
            st.error("Monto inválido")

# Pantalla 3: Reporte
st.header("Reporte")
fecha_desde = st.date_input("Desde")
fecha_hasta = st.date_input("Hasta")
report_modelo = st.selectbox("Modelo", modelos + ["Todos"])
if st.button("Ver Reporte"):
    ventas['Fecha'] = pd.to_datetime(ventas['Fecha'])
    mask = (ventas['Fecha'] >= pd.to_datetime(fecha_desde)) & (ventas['Fecha'] <= pd.to_datetime(fecha_hasta))
    report_df = ventas[mask]
    if report_modelo != "Todos":
        report_df = report_df[report_df['Modelo'] == report_modelo]
    total = report_df['Monto USD'].sum()
    st.write(f"Total USD: ${total:.2f}")
    st.dataframe(report_df)