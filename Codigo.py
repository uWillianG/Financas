import ofxparse #para realizar a leitura dos arquivos ofx 
import pandas as pd #para organizar em tabelas
import os #para navegar nos arquivos
from datetime import datetime #para poder fazer conversões de data


df = pd.DataFrame()
for extrato in os.listdir("extratos"):
    with open(f'extratos/{extrato}') as ofx_file:  
        ofx = ofxparse.OfxParser.parse(ofx_file)
    #cria uma lista, para armazenar as transações
    transactions_data = [] 

    for account in ofx.accounts:
        for transaction in account.statement.transactions: #lista de todas as transações
            transactions_data.append({
                "Data": transaction.date,
                "Valor": transaction.amount,
                "Descrição": transaction.id,
                "Forma de pagamento": transaction.memo,
            })

    df_temp = pd.DataFrame(transactions_data) #converte para um dataframe temporário
    df_temp["Valor"] = df_temp["Valor"].astype(float)
    df_temp["Data"] = df_temp["Data"].apply(lambda x: x.date()) #para puxar apenas a data, sem a hora
    df = pd.concat([df, df_temp])
    df = df.set_index("Forma de pagamento") #define como índice

#LLM
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

template = """
Você é um analista de dados, trabalhando em um projeto de limpeza de dados.
Seu trabalho é escolher uma categoria adequada para cada lançamento financeiro
que vou te enviar.

Todos são transações financeiras de uma pessoa física.

Escolha uma dentre as seguintes categorias:
- Alimentação - tudo que tem "chopp" e "ifood" na descrição
- Salário - tudo que tem "Ost" na descrição
- Mercado - tudo que tem "macromix" na descrição
- Saúde - tudo que tem "academia" na descrição
- Educação - tudo que tem "liberato" na descrição
- Compras
- Transporte
- Investimento
- Aparência - tudo que tem "Joana" e "AUGUSTO DIAS" na descrição
- Telefone
- Transferência para terceiros - tudo que tem nome de pessoa, menos Joana e Augusto na descrição
- Entretenimento
- Lazer
- Pagamento de contas - tudo que tem "FATURA" na descrição

Escolha a categoria deste item:
{text}

Responda apenas com a categoria.
"""

prompt = PromptTemplate.from_template(template=template)


# Groq
chat = ChatGroq(model="llama-3.1-70b-versatile")
chain = prompt | chat | StrOutputParser()

categorias = chain.batch(list(df["Descrição"].values))
df["Categoria"] = categorias #armazena o resultado de cada classificação e adiciona ao df na coluna categoria
df.to_excel("finanças2.xlsx")
