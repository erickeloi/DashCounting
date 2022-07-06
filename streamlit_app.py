import streamlit as st
import requests
import backoff
import json 

import pandas as pd

import xlsxwriter
from io import BytesIO

from busca_na_api import *

# Podemos usar estado de sessão, session state do streamlit para manter variáveis persistentes entre apps do app

# TO-DO
# Create a Pandas dataframe with the cnpj data and concat with the posteriors cnpj's.

# Create a session state that don't loss the 'cnpj dataframe' beetween pages.

# Create the pages and buttons/interaction to download the xlsx of the dataframe 

# Create the integration with the donwload button to get the xlsx of the dataframe.
if 'empresas' not in st.session_state:
    st.session_state.empresas = None

if 'cnpj_empresas' not in st.session_state:
    st.session_state.cnpj_empresas = None

def cnpj_json_to_dataframe(json_infos):
    if json_infos == 'CNPJ Invalido':
        st.write("CNPJ inválido !")
        return None
    elif json_infos == 'Servidor Indisponivel':
        st.write("Tente novamente mais tarde! Servidor indisponível")
        return None
    else:
        lista_empresa_info = list()
        lista_empresa_info.append(json_infos["cnpj"])
        lista_empresa_info.append(json_infos["nome"])
        
        atividade_principal = json_infos["atividade_principal"][0]["text"]
        lista_empresa_info.append(atividade_principal)
        atividade_principal = ''

        atividade_secundaria = ''
        for key, infos in enumerate(json_infos["atividades_secundarias"]):
            atividade_secundaria += f'{key+1}. {json_infos["atividades_secundarias"][key]["text"]} | '
        lista_empresa_info.append(atividade_secundaria)
        atividade_secundaria = ''

        lista_empresa_info.append(json_infos["uf"])
        lista_empresa_info.append(json_infos["telefone"])
        lista_empresa_info.append(json_infos["email"])
        lista_empresa_info.append(json_infos["abertura"])
        lista_empresa_info.append(json_infos["situacao"])
        nome_colunas = ['cnpj', 'nome', 'atividade principal', 'atividades secundarias', 'uf', 'telefone', 'email', 'abertura', 'situacao']
        empresa_df = pd.DataFrame(data=[lista_empresa_info], columns=nome_colunas)
        return empresa_df

def homepage():

    st.header("Bem vindo ao DashCounting app!")
    st.write("Escolha uma página acima ")

    mostrar = st.checkbox("Mostrar empresas na lista de interesse")
    if mostrar:
        if st.session_state['empresas'] is not None:
            st.write(st.session_state.empresas)
            
        else:
            st.write("Nenhuma empresa Adicionada na lista de interesse")
            adicionar_empresa_teste = st.button("Clique aqui para adicionar uma empresa de teste para ver como ela será mostrada !")
            if adicionar_empresa_teste:
                cnpj = 17895646000187
                json_infos = None
                while json_infos is None:
                    json_infos = get_api_info(cnpj)

                empresa_df: pd.DataFrame = cnpj_json_to_dataframe(json_infos=json_infos)
                st.session_state.empresas =  empresa_df
                st.write(empresa_df)

def search_info_predef_cnpj():
    st.header("Buscando informações dos CNPJ's de teste...")
    st.subheader("17895646000187, 18033552000161, 1365284000104\n")
    CNPJS = [17895646000187, 18033552000161, 1365284000104]
    st.write("---")
    for cnpj in CNPJS:
        json_infos = get_api_info(cnpj)
        empresa_df = cnpj_json_to_dataframe(json_infos=json_infos)
        if empresa_df is not None:
            st.write(empresa_df)
        st.write(f"--- Fim da Ficha do CNPJ: {cnpj} ---\n\n")
    

def search_info_new_cnpj():
    st.header("Busca por CNPJ: ")

    cnpj = st.text_input(
        label="Digite o CNPJ: ",
        placeholder="Exemplo: 12.345.678/0001-10 ou 12345678912345",
        max_chars=18
    )

    
    pesquisar = st.checkbox("Pesquisar")
    if cnpj.find('/') != -1 or cnpj.find('.') != -1:
        cnpj = cnpj[:2] + cnpj[3:6] + cnpj[7:10] + cnpj[11:15] + cnpj[16:]

    if pesquisar:
        st.write("Procurando o CNPJ desejado...")
        json_infos = get_api_info(cnpj)
        empresa_df = cnpj_json_to_dataframe(json_infos=json_infos)
        if empresa_df is not None:
            st.write(empresa_df)
        st.write(f"--- Fim da Ficha do CNPJ: {cnpj} ---\n\n")

        adicionar = st.checkbox("Adicionar essa empresa na lista de interesse?")
        if adicionar:
            if st.session_state.empresas is not None:
                st.session_state.empresas = pd.concat([st.session_state.empresas, empresa_df])
            else:
                st.session_state.empresas = empresa_df
            
            st.warning('Empresa Adicionada com sucesso, clique em pesquisar para procurar outro cnpj')

def search_and_download():
    ver_lista_interesse = st.checkbox("Verificar empresas na lista de interesse")
    if ver_lista_interesse:

        #for empresa in st.session_state.local_storage:
        #    print(empresa['nome'])
        #    print(type(empresa))
        #    final_df = pd.concat([final_df], [empresa])

        # GET the dataframe working
       
        st.write(st.session_state.empresas)
        buffer = BytesIO()
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            # Write each dataframe to a different worksheet.
            st.session_state.empresas.to_excel(writer, sheet_name='Sheet1', index=False)

            # Close the Pandas Excel writer and output the Excel file to the buffer
            writer.save()

        st.download_button(
            label="Download Excel Empresas",
            data=buffer,
            file_name="Empresas.xlsx",
            mime="application/vnd.ms-excel"
        )


pages = {"Homepage": homepage,
"Buscar informações dos CNPJ's padrões": search_info_predef_cnpj,
"Buscar informações de um novo CNPJ": search_info_new_cnpj,
"Verificar e Fazer donwload das empresas na lista de interesse": search_and_download
}

select_page = st.selectbox(
    "Escolha a Página",
    pages.keys()
)

pages[select_page]()
