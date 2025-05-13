import streamlit as st
import pandas as pd
from utils.google_sheets import read_sheet_to_dataframe

# Configurações
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1VZpV97NIhd16jAyzMpVE_8VhSs-bSqi4DXmySsx2Kc4/edit#gid=761491838"
WORKSHEET_NAME = "Cronograma"

st.set_page_config(
    page_title="Florestal | Cronograma PPR", 
    page_icon="📅", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Adicionamos esta linha
)


if 'sidebar_visible' not in st.session_state:
    st.session_state.sidebar_visible = False  # Começa oculta



# Estilos CSS personalizados (cores: verde escuro #20643f e verde claro #40b049)
st.markdown("""
    <style>
        .header-style {
            font-size: 24px;
            font-weight: bold;
            color: #20643f;
            margin-bottom: 10px;
        }
        .subheader-style {
            font-size: 18px;
            font-weight: 600;
            color: #40b049;
            margin-bottom: 5px;
        }

        .card:hover {
            transform: translateY(-2px);
        }
        .status-box {
            border-left: 4px solid #40b049;
            padding-left: 10px;
            margin: 5px 0;
        }
        .filter-box {
            background-color: #f1f3f6;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #20643f;
        }
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            padding: 8px 0;
            font-weight: 500;
            color: white;
            background-color: #40b049;
            border: none;
        }
        .stButton>button:hover {
            background-color: #20643f;
            transition: 0.3s;
        }
        .divider {
            margin: 20px 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, #40b049, transparent);
        }
    </style>
""", unsafe_allow_html=True)

# Verificação de login
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Você precisa estar logado para acessar esta página.")

    if st.button("🔐 Fazer login"):
        st.switch_page("pages/auth.py")  # Certifique-se de que o caminho está correto

    st.stop()

# Cabeçalho melhorado
st.markdown("<div class='header-style'>📅 Florestal | Cronograma PPR</div>", unsafe_allow_html=True)

# Barra de informações do usuário
user_info = st.container()
with user_info:
    cols = st.columns([3, 3, 3, 1])
    with cols[0]:
        st.markdown(f"<div class='subheader-style'>👤 Usuário: {st.session_state.get('user_info', {}).get('Login', 'Desconhecido')}</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='subheader-style'>📧 E-mail: {st.session_state.get('email', 'Desconhecido')}</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='subheader-style'>🔑 Tipo: {st.session_state.get('tipo_usuario', 'Não definido')}</div>", unsafe_allow_html=True)
    with cols[3]:
        if st.button("🔄 Atualizar", help="Atualizar dados da planilha"):
            st.cache_data.clear()
            st.rerun()

# Carrega os dados
@st.cache_data(ttl=300)
def load_data():
    df = read_sheet_to_dataframe(SPREADSHEET_URL, WORKSHEET_NAME)
    
    # Verifica se o usuário está logado e filtra pelo e-mail
    if "email" in st.session_state:
        user_email = str(st.session_state.email).strip().lower()

        #APLICAR LÓGICA DE FILTRO
        df = df[df['E-mail'] == user_email]
    
    return df

df = load_data()

if df is not None:
    # --- SEÇÃO DE FILTROS DINÂMICOS ---
    with st.expander("🔍 Filtros Avançados", expanded=True):
        with st.container():
            st.markdown("<div class='filter-box'>", unsafe_allow_html=True)
            
            # Função auxiliar para opções de filtro
            def get_filter_options(column, base_df):
                options = base_df[column].unique()
                return ["Todos"] + sorted(filter(None, set(str(x) for x in options)))

            # Layout dos filtros (3 colunas)
            col1, col2, col3 = st.columns(3)
            
            # Dicionário para armazenar seleções
            selections = {}
            
            with col1:
                selections['Referência'] = st.selectbox(
                    "Referência",
                    options=get_filter_options('Referência', df),
                    index=0
                )
                
                temp_df = df[df['Referência'] == selections['Referência']] if selections['Referência'] != "Todos" else df
                selections['Setor'] = st.selectbox(
                    "Setor",
                    options=get_filter_options('Setor', temp_df),
                    index=0
                )

            with col2:
                if selections['Setor'] != "Todos":
                    temp_df = temp_df[temp_df['Setor'] == selections['Setor']]
                
                selections['Responsável'] = st.selectbox(
                    "Responsável",
                    options=get_filter_options('Responsável', temp_df),
                    index=0
                )
                
                if selections['Responsável'] != "Todos":
                    temp_df = temp_df[temp_df['Responsável'] == selections['Responsável']]
                
                selections['Descrição Meta'] = st.selectbox(
                    "Descrição Meta",
                    options=get_filter_options('Descrição Meta', temp_df),
                    index=0
                )

            with col3:
                if selections['Descrição Meta'] != "Todos":
                    temp_df = temp_df[temp_df['Descrição Meta'] == selections['Descrição Meta']]
                
                selections['Responsável Área'] = st.selectbox(
                    "Responsável Área",
                    options=get_filter_options('Responsável Área', temp_df),
                    index=0
                )
                
                if selections['Responsável Área'] != "Todos":
                    temp_df = temp_df[temp_df['Responsável Área'] == selections['Responsável Área']]
                
                selections['E-mail'] = st.selectbox(
                    "E-mail",
                    options=get_filter_options('E-mail', temp_df),
                    index=0
                )
            
            st.markdown("</div>", unsafe_allow_html=True)

    # --- APLICA FILTROS ---
    filtered_df = df.copy()
    for col, val in selections.items():
        if val != "Todos":
            filtered_df = filtered_df[filtered_df[col] == val]
    
    # --- EXIBIÇÃO DOS RESULTADOS ---
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='header-style'>📊 Resultados: {len(filtered_df)} registros encontrados</div>", unsafe_allow_html=True)

    if not filtered_df.empty:
        for index, row in filtered_df.iterrows():
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                
                # Cabeçalho do card
                cols_header = st.columns([4, 1, 1, 1, 1, 1, 1])
                with cols_header[0]:
                    st.markdown(f"<div class='subheader-style'>📑 {row['Descrição Meta']}</div>", unsafe_allow_html=True)
                
                # Conteúdo principal
                cols_content = st.columns([4, 1, 1, 1, 1, 1, 1])
                
                with cols_content[0]:
                    st.markdown(f"""
                        <div class='status-box'>
                            <p><strong>Referência:</strong> {row['Referência']}</p>
                            <p><strong>Setor:</strong> {row['Setor']}</p>
                            <p><strong>Responsável:</strong> {row['Responsável']}</p>
                            <p><strong>Responsável Área:</strong> {row['Responsável Área']}</p>
                            <p><strong>E-mail:</strong> {row['E-mail']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Colunas de entregas
                entregas = [
                    ('1º Entrega', '1º Avaliação', 'Validação 1º Entrega', "pages/Entrega1.py"),
                    ('2º Entrega', '2º Avaliação', 'Validação 2º Entrega', "pages/Entrega2.py"),
                    ('3º Entrega', '3º Avaliação', 'Validação 3º Entrega', "pages/Entrega3.py"),
                    ('4º Entrega', '4º Avaliação', 'Validação 4º Entrega', "pages/Entrega4.py"),
                    ('5º Entrega', '5º Avaliação', 'Validação 5º Entrega', "pages/Entrega5.py"),
                    ('6º Entrega', '6º Avaliação', 'Validação 6º Entrega', "pages/Entrega6.py")
                ]
                
                for i, (entrega, avaliacao, validacao, page) in enumerate(entregas, start=1):
                    with cols_content[i]:
                        st.markdown(f"""
                                        <div style="
                                            border: 1px solid #ccc;
                                            border-radius: 10px;
                                            padding: 16px;
                                            margin-bottom: 10px;
                                            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                                            height: 180px;
                                            display: flex;
                                            flex-direction: column;
                                            justify-content: space-between;
                                            overflow: auto;  /* Adiciona scroll se necessário */
                                        ">
                                            <p style="margin: 0;"><strong>{entrega.split('º')[0]}º Entrega:</strong> {row[entrega]}</p>
                                            <p style="margin: 0;"><strong>→ </strong> {row[avaliacao]}</p>
                                            <p style="margin: 0;"><strong>Status: </strong> {row[validacao]}</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                        
                        if st.button(f"✏️ {entrega.split('º')[0]}º", key=f"editar_{i}_entrega_{index} Entrega"):
                            st.session_state.selected_row_index = index
                            st.switch_page(page)
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    else:
        st.warning("Nenhum registro encontrado com os filtros selecionados!")

elif df is not None and df.empty:
    st.warning("A planilha está vazia!")
else:
    st.error("❌ Falha ao carregar os dados. Verifique:")
    st.markdown("""
    - Conexão com a internet
    - Permissões da planilha
    - Nome correto da aba ('Cronograma')
    - Configuração do service account
    """)
