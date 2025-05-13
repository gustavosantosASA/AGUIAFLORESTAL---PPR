import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

def get_google_sheet_by_url(url):
    """Conecta ao Google Sheets usando a URL e retorna a planilha"""
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials/service_account.json', scope)
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open_by_url(url)
        return sheet
    except Exception as e:
        print(f"Erro ao acessar a planilha: {e}")
        return None

def get_worksheet(url, worksheet_name):
    """Obtém uma aba específica da planilha"""
    sheet = get_google_sheet_by_url(url)
    if sheet:
        try:
            worksheet = sheet.worksheet(worksheet_name)
            return worksheet
        except:
            print(f"Aba '{worksheet_name}' não encontrada")
            return None
    return None


def read_sheet_to_dataframe(spreadsheet_url, worksheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["google_sheets"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    gc = gspread.authorize(creds)
    
    spreadsheet = gc.open_by_url(spreadsheet_url)
    worksheet = spreadsheet.worksheet(worksheet_name)
    data = worksheet.get_all_records()
    return pd.DataFrame(data)


def write_dataframe_to_sheet(url, worksheet_name, dataframe):
    """Escreve um DataFrame em uma planilha"""
    worksheet = get_worksheet(url, worksheet_name)
    if worksheet:
        # Limpa a planilha existente
        worksheet.clear()
        
        # Adiciona cabeçalhos
        headers = dataframe.columns.tolist()
        worksheet.append_row(headers)
        
        # Adiciona dados
        for _, row in dataframe.iterrows():
            worksheet.append_row(row.tolist())
        return True
    return False

def append_row_to_sheet(url, worksheet_name, row_data):
    """Adiciona uma nova linha à planilha"""
    worksheet = get_worksheet(url, worksheet_name)
    if worksheet:
        worksheet.append_row(row_data)
        return True
    return False

def update_row_in_sheet(url, worksheet_name, row_index, new_values):
    """Atualiza uma linha específica na planilha"""
    worksheet = get_worksheet(url, worksheet_name)
    if worksheet:
        for col, value in enumerate(new_values, start=1):
            worksheet.update_cell(row_index, col, value)
        return True
    return False

def update_1st_aval_column(url, worksheet_name, row_identifier, new_value):
    """
    Atualiza apenas a coluna '1º Avaliação' de uma linha específica
    com base em um identificador único (row_identifier).
    
    :param url: URL da planilha Google Sheets
    :param worksheet_name: Nome da aba da planilha
    :param row_identifier: Identificador único (ex: 'Descrição Meta', 'ID', etc.)
    :param new_value: Novo valor para a coluna '1º Avaliação'
    """
    worksheet = get_worksheet(url, worksheet_name)
    if worksheet:
        # Encontra todas as linhas da planilha
        rows = worksheet.get_all_records()
        
        for i, row in enumerate(rows, start=2):  # Começando da linha 2 (a 1 é de cabeçalho)
            if row['key'] == row_identifier:  # Supondo que 'Descrição Meta' seja única
                # Atualiza o valor da célula '1º Avaliação' na linha encontrada
                worksheet.update_cell(i, rows[0].keys().index('1º Avaliação') + 1, new_value)
                print(f"Coluna '1º Avaliação' atualizada para: {new_value} na linha {i}")
                return True  # Retorna True se a atualização foi bem-sucedida
        print("Identificador não encontrado.")
        return False  # Retorna False se não encontrar o identificador
    else:
        print("Erro ao acessar a planilha.")
        return False
