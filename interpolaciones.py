
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



def obtener_ipc_inicial_final(fecha_inicial, fecha_final, df_ipc):
    """Obtiene el IPC inicial y final sin interpolar, solo extrayendo de la tabla."""
    
    ipc_inicial = df_ipc.loc[df_ipc['fecha'] == pd.Timestamp(fecha_inicial), 'IPCac'].values
    ipc_final = df_ipc.loc[df_ipc['fecha'] == pd.Timestamp(fecha_final), 'IPCac'].values
    
    return (ipc_inicial[0] if len(ipc_inicial) > 0 else None, 
            ipc_final[0] if len(ipc_final) > 0 else None)





def calcular_ipc_final_sin_interpolacion(fecha_fin, df_ipc):
    """Obtiene el IPC final sin interpolación, tomando el valor más cercano disponible en la tabla."""
    
    anio = fecha_fin.year
    mes = fecha_fin.month

    # Seleccionar la fecha clave para el IPC final
    F2 = obtener_ultimo_dia_mes(anio, mes)  # Último día del mes

    # Obtener el valor de IPC sin interpolación
    ipc_f2 = df_ipc.loc[df_ipc['fecha'] == pd.Timestamp(F2), 'IPCac'].values

    # Devolver el IPC encontrado en la tabla
    return ipc_f2[0] if len(ipc_f2) > 0 else None



def calcular_ipc_inicial_sin_interpolacion(fecha, df_ipc):
    """Obtiene el IPC inicial sin interpolación, tomando el valor del último día del mes anterior o el primer día del mes actual."""
    
    anio = fecha.year
    mes = fecha.month

    # Si el mes es enero, tomamos el IPC de diciembre del año anterior
    if mes == 1:
        F1 = date(anio - 1, 12, 31)  # Último día de diciembre del año anterior
    else:
        # Si no es enero, tomamos el IPC del último día del mes anterior
        F1 = obtener_ultimo_dia_mes(anio, mes - 1)

    # Obtener el IPC sin interpolación
    ipc_f1 = df_ipc.loc[df_ipc['fecha'] == pd.Timestamp(F1), 'IPCac'].values

    # Devolver el IPC encontrado en la tabla
    return ipc_f1[0] if len(ipc_f1) > 0 else None
