import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import openpyxl
from cargue_datos import cargar_datos_excel
from interpolaciones import calcular_ipc_inicial_interpolado, calcular_ipc_final_interpolado, obtener_ipc_inicial_final, calcular_ipc_inicial_sin_interpolacion, calcular_ipc_final_sin_interpolacion


from datetime import timedelta
import pandas as pd

def generar_tabla_periodos(fecha_inicio, fecha_fin, df_ipc, periodos_laborales):
    """Genera una tabla con los periodos desglosados por mes incluyendo datos de IPC y cotización sin interpolación."""
    periodos = []
    fecha_actual = fecha_inicio

    # Calcular IPC Final una sola vez usando la fecha de fin seleccionada por el usuario
    ipc_final = calcular_ipc_final_sin_interpolacion(fecha_fin, df_ipc)

    while fecha_actual <= fecha_fin:
        anio = fecha_actual.year
        mes = fecha_actual.month

        # Ajustar las fechas de inicio y fin según los periodos laborales
        desde = fecha_actual
        hasta = min(fecha_fin, (fecha_actual + timedelta(days=32)).replace(day=1) - timedelta(days=1))

        # Ajustar la fecha de inicio para que coincida con la fecha de inicio del periodo laboral
        for periodo in periodos_laborales:
            if periodo['fecha_inicio'] <= fecha_actual <= periodo['fecha_fin']:
                desde = max(desde, periodo['fecha_inicio'])
                break

        # Ajustar la fecha de fin para que coincida con la fecha de fin del periodo laboral
        for periodo in periodos_laborales:
            if periodo['fecha_inicio'] <= desde <= periodo['fecha_fin']:
                hasta = min(hasta, periodo['fecha_fin'])
                break

        dias_cotizados = (hasta - desde).days + 1
        if dias_cotizados >= 31:
            dias_cotizados = 30
        elif mes == 2 and dias_cotizados >= 28:
            dias_cotizados = 30

        semanas_cotizados = round(dias_cotizados / 7, 2)

        # Determinar el salario base para el periodo actual
        salario_base = 0
        for periodo in periodos_laborales:
            if periodo['fecha_inicio'] <= desde <= periodo['fecha_fin']:
                salario_base = periodo['salario']
                break

        # Si el salario base es 0, los días y semanas cotizadas también deben ser 0
        if salario_base == 0:
            dias_cotizados = 0
            semanas_cotizados = 0

        # Calcular IPC Inicial individualmente para cada mes sin interpolación
        ipc_inicial = calcular_ipc_inicial_sin_interpolacion(desde, df_ipc)

        salario_actualizado = None
        if ipc_inicial and ipc_final:
            salario_actualizado = round(salario_base * (ipc_final / ipc_inicial), 2)

        periodos.append({
            "Año": anio, "Mes": mes, "Desde": desde.strftime('%d/%m/%Y'), "Hasta": hasta.strftime('%d/%m/%Y'),
            "Salario": f"${salario_base:,.2f}", "Días Cotizados": dias_cotizados, "Semanas Cotizadas": semanas_cotizados,
            "IPC Final": ipc_final, "IPC Inicial": ipc_inicial, "Salario Actualizado": f"${salario_actualizado:,.2f}" if salario_actualizado else None
        })

        fecha_actual = hasta + timedelta(days=1)

    return pd.DataFrame(periodos)


def calcular_resumen_ibl(df_periodos):
    """Calcula el total de días cotizados, semanas cotizadas y el IBL basado en los últimos 120 meses con cotización."""

    # Convertir 'Días Cotizados' y 'Salario Actualizado' a valores numéricos
    df_periodos["Días Cotizados"] = pd.to_numeric(df_periodos["Días Cotizados"], errors='coerce').fillna(0)
    df_periodos["Salario Actualizado Numérico"] = df_periodos["Salario Actualizado"].replace({'\$': '', ',': ''}, regex=True).astype(float)

    # Agregar columna 'Fecha' combinando 'Año' y 'Mes' para ordenar
    df_periodos["Fecha"] = pd.to_datetime(df_periodos["Año"].astype(str) + "-" + df_periodos["Mes"].astype(str) + "-01")

    # Filtrar los últimos 120 meses donde haya al menos 1 día cotizado
    df_periodos_con_cotizacion = df_periodos[df_periodos["Días Cotizados"] > 0]

    # Ordenar por fecha en orden descendente
    df_periodos_con_cotizacion = df_periodos_con_cotizacion.sort_values(by="Fecha", ascending=False)

    # Tomar los últimos 120 meses con cotización (si existen)
    df_periodos_relevantes = df_periodos_con_cotizacion.head(120)

    # Cálculo del total de días y semanas cotizadas
    total_dias_cotizados = df_periodos["Días Cotizados"].sum()
    total_semanas_cotizados = df_periodos["Semanas Cotizadas"].sum()

    # Calcular el IBL promedio en los últimos 120 meses con cotización
    if not df_periodos_relevantes.empty:
        ibl_promedio = df_periodos_relevantes["Salario Actualizado Numérico"].mean()
    else:
        ibl_promedio = 0  # Si no hay datos suficientes, se considera 0

    # Tabla compacta con formato bonito
    return pd.DataFrame({
        "📅 Días Cotizados": [f"{total_dias_cotizados:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        "📊 Semanas Cotizadas": [f"{total_semanas_cotizados:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        "💰 IBL (Últimos 120 meses)": [f"${ibl_promedio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")]
    })



st.set_page_config(page_title="Calculadora IBL", page_icon="📊", layout="wide")
st.title("📊 Calculadora de Índice de Base de Liquidaciones (IBL)-OMB")
st.write("Seleccione Periodo de Historia Laboral")

df = cargar_datos_excel()

hoy = date.today()
primer_dia_mes_actual = hoy.replace(day=1)
ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)

tamaño_col = 2
col1, col2, _ = st.columns([tamaño_col, tamaño_col, 4])
with col1:
    fecha_inicio = st.date_input("📅 Primera Cotización", min_value=df['fecha'].min().date(), max_value=ultimo_dia_mes_anterior)
with col2:
    fecha_fin = st.date_input("📅 Última Cotización", min_value=df['fecha'].min().date(), max_value=ultimo_dia_mes_anterior)

num_periodos = st.number_input("Número de periodos laborales", min_value=1, max_value=100, value=1)

periodos_laborales = []
for i in range(num_periodos):
    st.write(f"### Periodo Laboral {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_inicio_periodo = st.date_input(f"Fecha Inicio Periodo {i+1}", min_value=fecha_inicio, max_value=fecha_fin)
    with col2:
        fecha_fin_periodo = st.date_input(f"Fecha Fin Periodo {i+1}", min_value=fecha_inicio, max_value=fecha_fin)
    with col3:
        salario_periodo = st.number_input(f"Salario Periodo {i+1}", min_value=0, format="%d")
    periodos_laborales.append({"fecha_inicio": fecha_inicio_periodo, "fecha_fin": fecha_fin_periodo, "salario": salario_periodo})

generar = st.button("Aplicar")

if generar:
    if fecha_inicio > fecha_fin:
        st.error("⚠️ La Fecha de Inicio no puede ser posterior a la Fecha de Fin.")
    else:
        tabla_periodos = generar_tabla_periodos(fecha_inicio, fecha_fin, df, periodos_laborales)

         # Mostrar resumen en la parte superior
        resumen_ibl = calcular_resumen_ibl(tabla_periodos)
        st.write("### 📌 Resumen del periodo seleccionado")
        st.dataframe(resumen_ibl, height=80, use_container_width=True)


      
        # Mostrar desglose mensual abajo
        st.write("### 📋 Desglose mensual del periodo seleccionado:")
        st.dataframe(tabla_periodos.drop(columns=["Salario Actualizado Numérico","Fecha"], errors="ignore"))

        # Imprimir la fecha de inicio del segundo período laboral
        if len(periodos_laborales) > 1:
            fecha_inicio_segundo_periodo = periodos_laborales[1]["fecha_inicio"]
            st.write(f"Fecha de inicio del segundo período laboral: {fecha_inicio_segundo_periodo.strftime('%d/%m/%Y')}")
