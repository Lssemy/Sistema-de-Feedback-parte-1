import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

st.set_page_config(page_title="Plataforma de Feedback - Cursos Livres", layout="wide")

st.title("Plataforma de Feedback - Cursos Livres")

DB_NAME = "feedback.db"

def init_db():
    """Inicializa a conexão com o banco de dados e cria a tabela se não existir."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_curso TEXT NOT NULL,
            qualidade_conteudo INTEGER NOT NULL,
            qualidade_instrutor INTEGER NOT NULL,
            recomendacao TEXT NOT NULL,
            comentario TEXT,
            data_feedback TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@st.cache_data
def load_data_from_db():
    """Carrega todos os feedbacks do banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM feedbacks", conn)
    conn.close()

    if df.empty:
        return generate_initial_data_and_populate_db()

    df['qualidade_conteudo_str'] = df['qualidade_conteudo'].apply(lambda x: '★' * x)
    df['qualidade_instrutor_str'] = df['qualidade_instrutor'].apply(lambda x: '★' * x)
    return df

def generate_initial_data_and_populate_db():
    """Gera dados simulados apenas na primeira vez e os insere no DB."""
    np.random.seed(42)
    cursos_list = ['Python Básico', 'Streamlit & Dashboard', 'Análise de Dados com Pandas', 'Introdução ao SQL', 'Machine Learning Básico'] # MAIS CURSOS AQUI
    
    data = {
        'id_curso': np.random.choice(cursos_list, 50),
        'qualidade_conteudo': np.random.randint(1, 6, 50),
        'qualidade_instrutor': np.random.randint(1, 6, 50),
        'recomendacao': np.random.choice(['Sim', 'Não', 'Talvez'], 50),
        'data_feedback': pd.to_datetime(pd.date_range(start='2025-01-01', periods=50, freq='W')).strftime('%Y-%m-%d')
    }
    df_initial = pd.DataFrame(data)
    df_initial['comentario'] = '' 

    conn = sqlite3.connect(DB_NAME)
    df_initial.to_sql('feedbacks', conn, if_exists='replace', index=False)
    conn.close()

    df_initial['qualidade_conteudo_str'] = df_initial['qualidade_conteudo'].apply(lambda x: '★' * x)
    df_initial['qualidade_instrutor_str'] = df_initial['qualidade_instrutor'].apply(lambda x: '★' * x)
    return df_initial


st.header("📝 Deixar seu Feedback")
with st.form("feedback_form"):
    df_atual = load_data_from_db()
    cursos_unicos = df_atual['id_curso'].unique().tolist()
    
    curso = st.selectbox("Selecione o Curso:", cursos_unicos)
    conteudo_rating = st.slider("Qualidade do Conteúdo (1-5)", 1, 5, 5)
    instrutor_rating = st.slider("Qualidade do Instrutor (1-5)", 1, 5, 5)
    recomendacao = st.radio("Você recomendaria este curso?", ['Sim', 'Não', 'Talvez'])
    comentario = st.text_area("Comentário (Opcional)")

    submitted = st.form_submit_button("Enviar Feedback")

    if submitted:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO feedbacks (id_curso, qualidade_conteudo, qualidade_instrutor, recomendacao, comentario, data_feedback) VALUES (?, ?, ?, ?, ?, ?)",
            (curso, conteudo_rating, instrutor_rating, recomendacao, comentario, datetime.now().strftime('%Y-%m-%d'))
        )
        conn.commit()
        conn.close()
        
        st.success(f"Feedback enviado e salvo no banco de dados para o curso '{curso}'!")
        load_data_from_db.clear() 
        st.rerun()

st.markdown("---")

st.header("📊 Análise Consolidada dos Feedbacks")

df_filtered = load_data_from_db()

st.sidebar.title("Filtro de Cursos")
selected_course = st.sidebar.selectbox(
    "Filtrar por Curso",
    ['Todos'] + df_filtered['id_curso'].unique().tolist()
)

df_filtered_by_selection = df_filtered
if selected_course != 'Todos':
    df_filtered_by_selection = df_filtered[df_filtered['id_curso'] == selected_course]

st.subheader(f"Resultados para: {selected_course}")

col1, col2, col3, col4 = st.columns(4)

total_feedbacks = len(df_filtered_by_selection)
media_conteudo = df_filtered_by_selection['qualidade_conteudo'].mean()
media_instrutor = df_filtered_by_selection['qualidade_instrutor'].mean()
percent_sim = (df_filtered_by_selection['recomendacao'].value_counts(normalize=True).get('Sim', 0) * 100)

with col1:
    st.metric("Total de Feedbacks", total_feedbacks)
with col2:
    st.metric("Média Conteúdo", f"★ {media_conteudo:.2f}" if not pd.isna(media_conteudo) else "N/A")
with col3:
    st.metric("Média Instrutor", f"★ {media_instrutor:.2f}" if not pd.isna(media_instrutor) else "N/A")
with col4:
    st.metric("% Recomendação Positiva", f"{percent_sim:.1f}%" if not pd.isna(percent_sim) else "N/A")

st.markdown("---")


st.subheader("Média de Qualidade por Mês")

if not df_filtered_by_selection.empty:
    df_filtered_by_selection['data_feedback'] = pd.to_datetime(df_filtered_by_selection['data_feedback'])
    df_monthly = df_filtered_by_selection.set_index('data_feedback').resample('M')[['qualidade_conteudo', 'qualidade_instrutor']].mean().reset_index()
    df_monthly['Mês'] = df_monthly['data_feedback'].dt.strftime('%b/%y')

    df_chart = df_monthly.rename(columns={
        'qualidade_conteudo': 'Média Conteúdo',
        'qualidade_instrutor': 'Média Instrutor'
    }).set_index('Mês')
    st.line_chart(df_chart)
else:
    st.info("Não há dados de feedback suficientes para mostrar a tendência mensal.")


st.subheader("Distribuição das Notas de 1 a 5")
col_grafico1, col_grafico2 = st.columns(2)

with col_grafico1:
    st.text("Distribuição Qualidade do Conteúdo")
    conteudo_dist = df_filtered_by_selection['qualidade_conteudo'].value_counts().sort_index()
    st.bar_chart(conteudo_dist)

with col_grafico2:
    st.text("Distribuição Qualidade do Instrutor")
    instrutor_dist = df_filtered_by_selection['qualidade_instrutor'].value_counts().sort_index()
    st.bar_chart(instrutor_dist)

st.markdown("---")

st.subheader("Dados Brutos de Feedback")
st.dataframe(df_filtered_by_selection[['id_curso', 'qualidade_conteudo_str', 'qualidade_instrutor_str', 'recomendacao', 'data_feedback']])