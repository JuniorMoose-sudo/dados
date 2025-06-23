📊 Análise de Serviços - Dashboard Streamlit
Um dashboard interativo feito com Python, Streamlit e Plotly, para análise, filtragem, visualização de indicadores e exportação de dados de atendimento/serviços, com foco em SLA, área, localidade, status e muito mais.

🚀 Funcionalidades
✅ Upload de planilhas .xlsx com estrutura flexível (o sistema tenta reconhecer colunas automaticamente)
✅ Mapeamento manual de colunas caso os nomes estejam diferentes
✅ Filtros por Área, Localidade, Data de Criação, Data de Vencimento, Tipo de Serviço
✅ Cálculo de métricas principais:

Total de protocolos

Protocolos atrasados

Tempo médio de resolução

Percentual dentro do SLA

✅ Gráficos interativos:

Distribuição por Status

Top 10 Responsáveis

Solicitações por Bairro

Evolução temporal

Comparativo entre áreas ou tipos de serviço

SLA por Localidade ou Responsável

✅ Visualização e exportação dos dados filtrados para Excel ou CSV

🖥️ Tecnologias Utilizadas
Python 🐍

Streamlit 🚀

Pandas 🐼

Plotly 📊

NumPy

OpenPyXL (para exportação em Excel)

📂 Estrutura Esperada da Planilha de Entrada
O sistema é flexível e tenta detectar automaticamente colunas por palavras-chave como:

Campo	Exemplos de nomes aceitos
Status	status, situação
Responsável	responsável, analista
Data de Abertura	abertura, data_abertura
Área	área, setor
Localidade	localidade, regional
Data de Criação	criação, cadastro
Data de Vencimento	vencimento, prazo
Data de Conclusão	conclusão, encerramento
Tipo de Serviço	tipo de serviço, natureza

Você pode fazer o mapeamento manual nas configurações laterais (sidebar) se preferir.

🛠️ Como Executar Localmente
Clone o repositório:

git clone https://github.com/JuniorMoose-sudo/dados

Crie um ambiente virtual (opcional, mas recomendado):

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

Instale as dependências:

pip install -r requirements.txt

Execute o Streamlit:

streamlit run app.py

📥 Exemplo de Planilha

Status
Responsável
Data de Abertura
Área
Localidade
Data de Criação
Data de Vencimento
Data de Conclusão
Tipo de Serviço
