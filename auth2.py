import streamlit as st
import pandas as pd
from utils.google_sheets import read_sheet_to_dataframe
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1VZpV97NIhd16jAyzMpVE_8VhSs-bSqi4DXmySsx2Kc4/edit#gid=0"
USERS_SHEET = "Usuários"

# --- Funções ---
def append_user_to_sheet(new_user):
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials/service_account.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SPREADSHEET_URL)
    worksheet = sheet.worksheet(USERS_SHEET)
    worksheet.append_row(new_user)

def authenticate_user(login, senha, df_users):
    user = df_users[(df_users['Login'] == login) & (df_users['Senha'] == senha)]
    if not user.empty:
        return user.iloc[0].to_dict()
    return None

# --- Inicialização da sessão ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- Lê dados da planilha ---
df_users = read_sheet_to_dataframe(SPREADSHEET_URL, USERS_SHEET)

st.title("🔐 Portal de Acesso")

# --- Conteúdo baseado no estado de login ---
if not st.session_state["logged_in"]:
    modo = st.radio("Escolha uma opção:", ["Login", "Cadastrar Novo Usuário"])

    if modo == "Login":
        login = st.text_input("Login")
        senha = st.text_input("Senha", type="password")

        if st.button("🔓 Entrar"):
            user_info = authenticate_user(login, senha, df_users)
            if user_info:
                st.session_state["logged_in"] = True
                st.session_state["user_info"] = user_info
                st.session_state["email"] = user_info["Email"]
                st.session_state["tipo_usuario"] = user_info["Tipo de Usuário"]
                st.success(f"Bem-vindo, {user_info['Login']}!")

                st.switch_page("app.py")  # ⬅️ muda aqui

            else:
                st.error("❌ Login ou senha inválidos.")

    else:  # Cadastro
        with st.form("form_cadastro"):
            novo_login = st.text_input("Novo Login")
            novo_email = st.text_input("Email")
            nova_senha = st.text_input("Senha", type="password")
            tipo_usuario = st.selectbox("Tipo de Usuário", ["Gestor | Avaliador", "Avaliador"])
            submit = st.form_submit_button("✅ Cadastrar")

            if submit:
                if novo_login in df_users['Login'].values:
                    st.warning("⚠️ Este login já existe.")
                else:
                    data = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                    append_user_to_sheet([novo_login, novo_email, nova_senha, tipo_usuario, data])
                    st.success("✅ Usuário cadastrado com sucesso. Faça login na aba anterior.")
else:
    # --- Conteúdo para usuário logado ---
    user_info = st.session_state["user_info"]
    st.success(f"👋 Bem-vindo, {user_info['Login']} ({user_info['Email']})")
    st.write("Tipo de usuário:", user_info["Tipo de Usuário"])

    if st.button("🚪 Sair"):
        st.session_state.clear()
        st.experimental_rerun()
