import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
from collections import Counter

st.title('📊 Análise de Serviços')

# Função para corrigir colunas duplicadas
def corrigir_colunas_duplicadas(colunas):
    contador = Counter()
    novas_colunas = []
    for col in colunas:
        contador[col] += 1
        if contador[col] == 1:
            novas_colunas.append(col)
        else:
            novas_colunas.append(f"{col}_{contador[col]}")
    return novas_colunas

# Upload da planilha
arquivo = st.file_uploader("Carregue sua planilha XLSX", type="xlsx")

if arquivo:
    df_raw = pd.read_excel(arquivo, header=0)
    df_raw.columns = corrigir_colunas_duplicadas(df_raw.columns.tolist())
    df = df_raw.copy()

    # Tentativa de detecção automática de colunas
    col_status = next((c for c in df.columns if 'status' in c.lower()), None)
    col_resp = next((c for c in df.columns if 'responsa' in c.lower()), None)
    col_abertura = next((c for c in df.columns if 'abertura' in c.lower()), None)
    col_area = next((c for c in df.columns if 'área' in c.lower()), None)
    col_localidade = next((c for c in df.columns if 'localidade' in c.lower()), None)
    col_criacao = next((c for c in df.columns if 'cria' in c.lower()), None)
    col_venc = next((c for c in df.columns if 'venc' in c.lower()), None)

    # Converter colunas de data
    for col_data in [col_abertura, col_criacao, col_venc]:
        if col_data:
            df[col_data] = pd.to_datetime(df[col_data], errors='coerce')

    # Renomear para uso interno
    if col_abertura: df.rename(columns={col_abertura: 'Abertura'}, inplace=True)
    if col_criacao: df.rename(columns={col_criacao: 'Criacao'}, inplace=True)
    if col_venc: df.rename(columns={col_venc: 'Vencimento'}, inplace=True)

    # Filtros adicionais
    st.sidebar.header("🎯 Filtros")

    if col_area:
        filtro_area = st.sidebar.multiselect("Filtrar por Área:", df[col_area].dropna().unique())
    else:
        filtro_area = []

    if col_localidade:
        filtro_local = st.sidebar.multiselect("Filtrar por Localidade:", df[col_localidade].dropna().unique())
    else:
        filtro_local = []

    if 'Criacao' in df.columns:
        data_min = df['Criacao'].min()
        data_max = df['Criacao'].max()
        data_ini, data_fim = st.sidebar.date_input("Filtrar por Data de Criação:", [data_min, data_max])
    else:
        data_ini, data_fim = None, None

    if 'Vencimento' in df.columns:
        venc_min = df['Vencimento'].min()
        venc_max = df['Vencimento'].max()
        venc_ini, venc_fim = st.sidebar.date_input("Filtrar por Vencimento:", [venc_min, venc_max])
    else:
        venc_ini, venc_fim = None, None

    if 'Tipo de Serviço' in df.columns:
        filtro_servico = st.sidebar.multiselect("Filtrar por Tipo de Serviço:", df['Tipo de Serviço'].dropna().unique())
    else:
        filtro_servico = []

    # Aplicar filtros
    df_filtrado = df.copy()

    if filtro_area and col_area:
        df_filtrado = df_filtrado[df_filtrado[col_area].isin(filtro_area)]

    if filtro_local and col_localidade:
        df_filtrado = df_filtrado[df_filtrado[col_localidade].isin(filtro_local)]

    if 'Criacao' in df_filtrado.columns and data_ini and data_fim:
        df_filtrado = df_filtrado[df_filtrado['Criacao'].between(pd.to_datetime(data_ini), pd.to_datetime(data_fim))]

    if 'Vencimento' in df_filtrado.columns and venc_ini and venc_fim:
        df_filtrado = df_filtrado[df_filtrado['Vencimento'].between(pd.to_datetime(venc_ini), pd.to_datetime(venc_fim))]

    if filtro_servico:
        df_filtrado = df_filtrado[df_filtrado['Tipo de Serviço'].isin(filtro_servico)]


    # Métricas principais
    st.header("📈 Métricas Principais")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total de Protocolos", df_filtrado.shape[0])
        if col_status:
            st.write("**Status:**", df_filtrado[col_status].value_counts().to_frame())

    with col2:
        if 'Abertura' in df_filtrado.columns and not df_filtrado['Abertura'].dropna().empty:
            ultima_data = df_filtrado['Abertura'].dropna().max()
            st.metric("Última Atualização", ultima_data.strftime('%d/%m/%Y %H:%M'))
        if col_resp:
            st.write("**Responsabilidade:**", df_filtrado[col_resp].value_counts().to_frame())

    # Dados filtrados
    st.header("📋 Dados Filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

    # Exportação
    st.header("📥 Exportar Dados Corrigidos")
    buffer = BytesIO()
    df_filtrado.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.download_button(
        label="📥 Baixar Excel Filtrado",
        data=buffer,
        file_name="planilha_filtrada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Por favor, carregue um arquivo XLSX para iniciar a análise.")
