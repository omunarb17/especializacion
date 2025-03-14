import pandas as pd
from datetime import datetime, date, timedelta
import openpyxl



def cargar_datos_excel():
    """Carga el archivo Excel estático desde la carpeta 'static'"""
    archivo = "static/PensionesTools.xlsx"
    df = pd.read_excel(archivo, sheet_name='IPC')
    df['fecha'] = pd.to_datetime(df['fecha'])  # Asegurar formato correcto de fecha
    return df