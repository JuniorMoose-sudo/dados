📊 Dashboard de Análise de Serviços
Este projeto é um dashboard interativo desenvolvido com Streamlit que permite a análise visual e dinâmica de dados oriundos de planilhas Excel contendo protocolos ou solicitações de serviços. Ele é ideal para equipes que desejam monitorar status de atendimentos, prazos de vencimento, cumprimento de SLA e demais métricas operacionais de forma simples e eficaz.

🔧 Funcionalidades
Upload de Planilha (.xlsx): Interface para carregar arquivos Excel.

Correção Automática de Colunas Duplicadas: Renomeia colunas repetidas para evitar erros.

Mapeamento Inteligente de Colunas: Detecta automaticamente colunas com base em palavras-chave (ex: "status", "vencimento", "conclusão" etc).

Mapeamento Manual de Colunas: Interface lateral permite ao usuário corrigir ou ajustar manualmente os mapeamentos.

Conversão de Datas: Colunas de datas são automaticamente convertidas para formato datetime.

Filtros Interativos: Filtros por área, localidade, tipo de serviço, data de criação e vencimento.

Cálculo de Métricas Operacionais:

Total de protocolos

Protocolos atrasados

Tempo médio de resolução

Percentual de SLA atendido

Visualizações com Plotly:

Gráficos de pizza (status)

Barras horizontais (responsáveis, bairros)

Série temporal de criação de protocolos

Comparativo por áreas, tipos, etc.

Gráficos sobre cumprimento de SLA


📦 Estrutura esperada do arquivo Excel
A planilha deve conter colunas com informações como:

Data de criação ou abertura

Prazo ou vencimento

Data de conclusão (opcional)

Status do protocolo

Responsável

Área ou setor

Tipo de serviço

Localidade

O sistema reconhece nomes similares automaticamente, como por exemplo: “data_abertura”, “prazo”, “fim”, “responsável”, etc.

✨ Exemplos de Uso
Análise de protocolos de atendimento de chamados técnicos

Gestão de ordens de serviço por área ou bairro

Acompanhamento de prazos e desempenho de equipes

Monitoramento de SLA e eficiência de atendimento
