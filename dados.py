import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO
from collections import Counter
import numpy as np

st.set_page_config(page_title='📊 Análise de Serviços', layout='wide')
st.title('📊 Análise de Serviços - Dashboard')


# Função para corrigir colunas duplicadas
def corrigir_colunas_duplicadas(colunas):
    try:
        contador = Counter()
        novas_colunas = []
        for col in colunas:
            if pd.isna(col):
                col = "Coluna_Desconhecida"
            contador[col] += 1
            if contador[col] == 1:
                novas_colunas.append(col)
            else:
                novas_colunas.append(f"{col}_{contador[col]}")
        return novas_colunas
    except Exception as e:
        st.error(f"Erro ao corrigir colunas duplicadas: {str(e)}")
        return colunas


# Função para calcular métricas de SLA
def calcular_metricas_tempo(df, data_criacao, data_vencimento, data_conclusao=None):
    metricas = {}

    if data_criacao and data_vencimento and data_criacao in df.columns and data_vencimento in df.columns:
        df['Tempo_para_Vencimento'] = (df[data_vencimento] - df[data_criacao]).dt.days

        metricas['Tempo_Médio_Vencimento'] = df['Tempo_para_Vencimento'].mean()
        metricas['Protocolos_Atrasados'] = df[df[data_vencimento] < datetime.now()].shape[0]

        if data_conclusao and data_conclusao in df.columns:
            df['Tempo_Resolução'] = (df[data_conclusao] - df[data_criacao]).dt.days
            metricas['Tempo_Médio_Resolução'] = df['Tempo_Resolução'].mean()
            df['Dentro_SLA'] = df[data_conclusao] <= df[data_vencimento]
            metricas['Percentual_SLA'] = df['Dentro_SLA'].mean() * 100

    return metricas, df


# Upload da planilha
arquivo = st.file_uploader("Carregue uma planilha XLSX", type="xlsx")

if arquivo:
    try:
        df_raw = pd.read_excel(arquivo, header=0)
        df_raw.columns = corrigir_colunas_duplicadas(df_raw.columns.tolist())
        df = df_raw.copy()

        # Dicionário para mapeamento de colunas
        mapeamento_colunas = {
            'status': None,
            'responsavel': None,
            'abertura': None,
            'area': None,
            'localidade': None,
            'criacao': None,
            'vencimento': None,
            'conclusao': None,
            'tipo_servico': None
        }

        # Padrões para detecção automática
        padroes_colunas = {
            'status': ['status', 'situação', 'estado'],
            'responsavel': ['responsa', 'responsável', 'analista', 'atendente'],
            'abertura': ['abertura', 'data_abertura', 'dt_abertura'],
            'area': ['área', 'setor', 'departamento'],
            'localidade': ['localidade', 'regional', 'filial', 'unidade'],
            'criacao': ['cria', 'data_cadastro', 'dt_cadastro'],
            'vencimento': ['venc', 'prazo', 'dt_vencimento'],
            'conclusao': ['conclu', 'fim', 'encerramento', 'dt_conclusao'],
            'tipo_servico': ['tipo de serviço', 'serviço', 'natureza', 'tipo']
        }

        # Detecção automática de colunas
        for chave in padroes_colunas:
            for padrao in padroes_colunas[chave]:
                col_candidata = next((c for c in df.columns if padrao in c.lower()), None)
                if col_candidata:
                    mapeamento_colunas[chave] = col_candidata
                    break

        # Sidebar para mapeamento manual
        st.sidebar.header("🔧 Configurações de Colunas")
        if st.sidebar.checkbox("Definir mapeamento manual de colunas"):
            for chave in mapeamento_colunas:
                mapeamento_colunas[chave] = st.sidebar.selectbox(
                    f"Selecione coluna para {chave}:",
                    [None] + df.columns.tolist(),
                    index=([None] + df.columns.tolist()).index(mapeamento_colunas[chave]) if mapeamento_colunas[
                        chave] else 0
                )

        # Converter colunas de data
        for col_data in ['abertura', 'criacao', 'vencimento', 'conclusao']:
            if mapeamento_colunas[col_data]:
                try:
                    df[mapeamento_colunas[col_data]] = pd.to_datetime(
                        df[mapeamento_colunas[col_data]], errors='coerce'
                    )
                except Exception as e:
                    st.warning(
                        f"Não foi possível converter a coluna {mapeamento_colunas[col_data]} para data: {str(e)}")

        # Filtros
        st.sidebar.header("🎯 Filtros")
        filtros = {}

        if mapeamento_colunas['area']:
            areas = df[mapeamento_colunas['area']].dropna().unique()
            filtros['area'] = st.sidebar.multiselect(
                f"Filtrar por {mapeamento_colunas['area']}:",
                areas
            )

        if mapeamento_colunas['localidade']:
            locais = df[mapeamento_colunas['localidade']].dropna().unique()
            filtros['localidade'] = st.sidebar.multiselect(
                f"Filtrar por {mapeamento_colunas['localidade']}:",
                locais
            )

        if mapeamento_colunas['criacao']:
            data_min = df[mapeamento_colunas['criacao']].min().date()
            data_max = df[mapeamento_colunas['criacao']].max().date()
            data_ini, data_fim = st.sidebar.date_input(
                f"Filtrar por {mapeamento_colunas['criacao']}:",
                [data_min, data_max]
            )
            filtros['data_criacao'] = (data_ini, data_fim)

        if mapeamento_colunas['vencimento']:
            venc_min = df[mapeamento_colunas['vencimento']].min().date()
            venc_max = df[mapeamento_colunas['vencimento']].max().date()
            venc_ini, venc_fim = st.sidebar.date_input(
                f"Filtrar por {mapeamento_colunas['vencimento']}:",
                [venc_min, venc_max]
            )
            filtros['data_vencimento'] = (venc_ini, venc_fim)

        if mapeamento_colunas['tipo_servico']:
            tipos = df[mapeamento_colunas['tipo_servico']].dropna().unique()
            filtros['tipo_servico'] = st.sidebar.multiselect(
                f"Filtrar por {mapeamento_colunas['tipo_servico']}:",
                tipos
            )

        # Aplicar filtros
        df_filtrado = df.copy()

        if 'area' in filtros and filtros['area']:
            df_filtrado = df_filtrado[df_filtrado[mapeamento_colunas['area']].isin(filtros['area'])]

        if 'localidade' in filtros and filtros['localidade']:
            df_filtrado = df_filtrado[df_filtrado[mapeamento_colunas['localidade']].isin(filtros['localidade'])]

        if 'data_criacao' in filtros and filtros['data_criacao']:
            data_ini, data_fim = filtros['data_criacao']
            df_filtrado = df_filtrado[
                df_filtrado[mapeamento_colunas['criacao']].dt.date.between(data_ini, data_fim)
            ]

        if 'data_vencimento' in filtros and filtros['data_vencimento']:
            venc_ini, venc_fim = filtros['data_vencimento']
            df_filtrado = df_filtrado[
                df_filtrado[mapeamento_colunas['vencimento']].dt.date.between(venc_ini, venc_fim)
            ]

        if 'tipo_servico' in filtros and filtros['tipo_servico']:
            df_filtrado = df_filtrado[
                df_filtrado[mapeamento_colunas['tipo_servico']].isin(filtros['tipo_servico'])
            ]

        # Métricas principais
        st.header("📈 Métricas")

        metricas_tempo, df_filtrado = calcular_metricas_tempo(
            df_filtrado,
            mapeamento_colunas['criacao'],
            mapeamento_colunas['vencimento'],
            mapeamento_colunas['conclusao']
        )

        cols = st.columns(4)
        with cols[0]:
            st.metric("Total de Protocolos", df_filtrado.shape[0])

        with cols[1]:
            st.metric("Protocolos Atrasados",
                      metricas_tempo.get('Protocolos_Atrasados', 'N/D'),
                      help="Protocolos com data de vencimento anterior à data atual")

        with cols[2]:
            valor = metricas_tempo.get('Tempo_Médio_Resolução', 'N/D')
            st.metric("Tempo Médio Resolução (dias)",
                      f"{valor:.1f}" if isinstance(valor, (int, float)) else valor,
                      help="Tempo médio entre criação e conclusão do protocolo")

        with cols[3]:
            valor = metricas_tempo.get('Percentual_SLA', 'N/D')
            st.metric("Dentro do SLA",
                      f"{valor:.1f}%" if isinstance(valor, (int, float)) else valor,
                      help="Percentual de protocolos concluídos dentro do prazo")

        # Visualizações gráficas
        st.header("📊 Visualizações")

        tab1, tab2, tab3, tab4 = st.tabs([
            "Distribuição", "Temporal", "Comparativo", "Análise SLA"
        ])

        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                if mapeamento_colunas['status']:
                    st.subheader("Distribuição por Status")
                    df_status = df_filtrado[mapeamento_colunas['status']].value_counts().reset_index()
                    df_status.columns = ['Status', 'Quantidade']

                    fig_status = px.pie(
                        df_status,
                        names='Status',
                        values='Quantidade',
                        hole=0.3
                    )
                    st.plotly_chart(fig_status, use_container_width=True)

            with col2:
                if mapeamento_colunas['responsavel']:
                    st.subheader("Top 10 Responsáveis")
                    top_resp = df_filtrado[mapeamento_colunas['responsavel']].value_counts().nlargest(10).reset_index()
                    top_resp.columns = ['Responsável', 'Quantidade']

                    fig_resp = px.bar(
                        top_resp,
                        x='Quantidade',
                        y='Responsável',
                        orientation='h',
                        labels={'Quantidade': 'Quantidade', 'Responsável': 'Responsável'},
                        color='Quantidade',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig_resp, use_container_width=True)
            with st.container():
                if mapeamento_colunas['localidade']:
                    st.subheader("Solicitações por Bairro (Localidade)")
                    df_bairros = df_filtrado[mapeamento_colunas['localidade']].value_counts().reset_index()
                    df_bairros.columns = ['Bairro', 'Quantidade']

                    fig_bairros = px.bar(
                        df_bairros,
                        x='Quantidade',
                        y='Bairro',
                        orientation='h',
                        title='Quantidade de Solicitações por Bairro',
                        color='Quantidade',
                        color_continuous_scale='Greens',
                        labels={'Quantidade': 'Solicitações', 'Bairro': 'Bairro'}
                    )

                    st.plotly_chart(fig_bairros, use_container_width=True)

        with tab2:
            if mapeamento_colunas['criacao']:
                st.subheader("Evolução Temporal")

                df_temporal = df_filtrado.copy()
                df_temporal['Mês'] = df_temporal[mapeamento_colunas['criacao']].dt.to_period('M').dt.to_timestamp()

                opcoes_agrupamento = [k for k in ['status', 'area', 'localidade', 'tipo_servico'] if
                                      mapeamento_colunas[k]]
                if opcoes_agrupamento:
                    agg_col = st.selectbox(
                        "Agrupar por:",
                        options=opcoes_agrupamento,
                        format_func=lambda x: mapeamento_colunas[x]
                    )

                    df_grouped = df_temporal.groupby(['Mês', mapeamento_colunas[agg_col]]).size().reset_index(name='Quantidade')

                    fig_temporal = px.line(
                        df_grouped,
                        x='Mês',
                        y='Quantidade',
                        color=mapeamento_colunas[agg_col],
                        markers=True,
                        title=f"Evolução Temporal por {mapeamento_colunas[agg_col]}"
                    )
                    st.plotly_chart(fig_temporal, use_container_width=True)
                else:
                    df_grouped = df_temporal.groupby('Mês').size().reset_index(name='Quantidade')
                    fig_temporal = px.line(
                        df_grouped,
                        x='Mês',
                        y='Quantidade',
                        markers=True,
                        title="Evolução Temporal de Solicitações"
                    )
                    st.plotly_chart(fig_temporal, use_container_width=True)

        with tab3:
            st.subheader("Comparativo entre Áreas ou Tipos de Serviço")
            if mapeamento_colunas['area'] and mapeamento_colunas['tipo_servico']:
                col_comparar = st.radio("Comparar por:", ['Área', 'Tipo de Serviço'])
                col_escolhida = mapeamento_colunas['area'] if col_comparar == 'Área' else mapeamento_colunas['tipo_servico']
                comparativo = df_filtrado[col_escolhida].value_counts().reset_index()
                comparativo.columns = [col_comparar, 'Quantidade']

                fig_comp = px.bar(
                    comparativo,
                    x='Quantidade',
                    y=col_comparar,
                    orientation='h',
                    color='Quantidade',
                    color_continuous_scale='Viridis',
                    title=f"Solicitações por {col_comparar}"
                )
                st.plotly_chart(fig_comp, use_container_width=True)

        with tab4:
            st.subheader("Análise de SLA por Localidade ou Responsável")
            opcao = None
            if mapeamento_colunas['localidade']:
                opcao = 'Localidade'
            elif mapeamento_colunas['responsavel']:
                opcao = 'Responsável'

            if opcao:
                col_base = mapeamento_colunas['localidade'] if opcao == 'Localidade' else mapeamento_colunas['responsavel']
                df_sla = df_filtrado.dropna(subset=['Dentro_SLA'])

                df_group_sla = df_sla.groupby(col_base)['Dentro_SLA'].mean().reset_index()
                df_group_sla['Dentro_SLA'] = df_group_sla['Dentro_SLA'] * 100
                df_group_sla = df_group_sla.sort_values(by='Dentro_SLA', ascending=False)

                fig_sla = px.bar(
                    df_group_sla,
                    x='Dentro_SLA',
                    y=col_base,
                    orientation='h',
                    title=f"Percentual Dentro do SLA por {opcao}",
                    labels={'Dentro_SLA': '% Dentro do SLA', col_base: opcao},
                    color='Dentro_SLA',
                    color_continuous_scale='Tealgrn'
                )
                st.plotly_chart(fig_sla, use_container_width=True)
            else:
                st.info("Nenhuma coluna de localidade ou responsável mapeada para análise de SLA.")

        # Dados filtrados
        st.header("📋 Dados Detalhados")

        with st.expander("Opções de Visualização"):
            cols_to_show = st.multiselect(
                "Selecione colunas para exibir:",
                df_filtrado.columns.tolist(),
                default=df_filtrado.columns.tolist()[:10]
            )
            num_rows = st.slider("Número de linhas para exibir:", 5, 100, 20)

        st.dataframe(df_filtrado[cols_to_show].head(num_rows), use_container_width=True)

        # Exportação
        st.header("📥 Exportação de Dados")

        export_cols = st.multiselect(
            "Selecione colunas para exportar:",
            df_filtrado.columns.tolist(),
            default=df_filtrado.columns.tolist()
        )

        col1, col2 = st.columns(2)

        with col1:
            buffer = BytesIO()
            df_filtrado[export_cols].to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)
            st.download_button(
                label="📊 Exportar para Excel",
                data=buffer,
                file_name="dados_filtrados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            st.download_button(
                label="📈 Exportar para CSV",
                data=df_filtrado[export_cols].to_csv(index=False).encode('utf-8'),
                file_name="dados_filtrados.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {str(e)}")
        st.error("Por favor, verifique o formato do arquivo e tente novamente.")
else:
    st.info("Por favor, carregue um arquivo XLSX para iniciar a análise.")