
from datetime import datetime, date, timedelta
import pandas as pd


def interpolar_valor(v1, v2, t1, t2):
    """Realiza interpolación lineal entre dos valores según la norma"""
    return ((t1 * v2) + (t2 * v1)) / (t1 + t2)



def obtener_ultimo_dia_mes(anio, mes):
    """Devuelve el último día válido del mes dado."""
    if mes == 12:
        return date(anio, mes, 31)
    siguiente_mes = date(anio, mes + 1, 1)
    return siguiente_mes - timedelta(days=1)


def calcular_ipc_inicial_interpolado(fecha, df_ipc):
    """Calcula el IPC inicial interpolando correctamente según la fecha específica."""
    anio = fecha.year
    mes = fecha.month
    
    F1 = obtener_ultimo_dia_mes(anio, mes - 1) if mes > 1 else date(anio - 1, 12, 31)
    F2 = obtener_ultimo_dia_mes(anio, mes)
    F0 = fecha
    
    ipc_f1 = df_ipc.loc[df_ipc['fecha'] == pd.Timestamp(F1), 'IPCac'].values
    ipc_f2 = df_ipc.loc[df_ipc['fecha'] == pd.Timestamp(F2), 'IPCac'].values
    
    if len(ipc_f1) > 0 and len(ipc_f2) > 0:
        t1 = (F0 - F1).days  # Días desde F1 hasta F0 (exclusivo)
        t2 = (F2 - F0).days  # Días desde F0 hasta F2 (inclusivo)
        return interpolar_valor(ipc_f1[0], ipc_f2[0], t1, t2)
    
    return ipc_f2[0] if len(ipc_f2) > 0 else None
def calcular_ipc_final_interpolado(fecha_fin, df_ipc):
    """Calcula el IPC final interpolado correctamente según la fecha de finalización."""
    
    anio = fecha_fin.year
    mes = fecha_fin.month
    
    # Seleccionar las fechas de referencia
    F1 = obtener_ultimo_dia_mes(anio, mes - 1) if mes > 1 else date(anio - 1, 12, 31)
    F2 = obtener_ultimo_dia_mes(anio, mes)
    F0 = fecha_fin  # Fecha intermedia
    
    # Extraer los valores de IPC
    ipc_f1 = df_ipc.loc[df_ipc['fecha'] == pd.Timestamp(F1), 'IPCac'].values
    ipc_f2 = df_ipc.loc[df_ipc['fecha'] == pd.Timestamp(F2), 'IPCac'].values
    
    if len(ipc_f1) > 0 and len(ipc_f2) > 0:
        t1 = (F0 - F1).days  # Días desde F1 hasta F0 (exclusivo)
        t2 = (F2 - F0).days  # Días desde F0 hasta F2 (inclusivo)
        return interpolar_valor(ipc_f1[0], ipc_f2[0], t1, t2)  # Aplicar interpolación
    
    return ipc_f2[0] if len(ipc_f2) > 0 else None  # Si no hay interpolación, devolver último IPC disponible
