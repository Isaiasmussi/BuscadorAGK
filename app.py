import streamlit as st
import requests
import os

# --- Configuração da Página ---
# st.set_page_config define o título que aparece na aba do navegador e o ícone.
# É bom colocar no início do script.
st.set_page_config(page_title="Buscador Agrolink", page_icon="🔗")

# --- Gerenciamento de Chaves de API (Segredo) ---
# A FORMA CORRETA NO STREAMLIT é usar o st.secrets
# Crie uma pasta chamada .streamlit e dentro dela um arquivo secrets.toml
#
# Conteúdo do arquivo .streamlit/secrets.toml:
# GOOGLE_API_KEY = "SUA_CHAVE_DE_API_AQUI"
# GOOGLE_SEARCH_ENGINE_ID = "SEU_ID_DE_BUSCA_AQUI"

try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SEARCH_ENGINE_ID = st.secrets["GOOGLE_SEARCH_ENGINE_ID"]
except FileNotFoundError:
    st.error("Arquivo de segredos (.streamlit/secrets.toml) não encontrado. Por favor, crie-o.")
    st.stop() # Interrompe a execução se as chaves não forem encontradas


# --- Função para Realizar a Busca ---
def perform_search(query: str):
    """
    Função que chama a API do Google e retorna os resultados formatados.
    """
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança um erro para respostas HTTP ruins (ex: 403, 500)
        
        search_results = response.json().get('items', [])
        
        # Formata os resultados para extrair apenas o que precisamos
        formatted_results = []
        for item in search_results:
            formatted_results.append({
                'title': item.get('title'),
                'link': item.get('link'),
                'snippet': item.get('snippet')
            })
        return formatted_results

    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API de busca: {e}")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        return None

# --- Interface do Usuário (UI) ---
st.image('https://www.agrolink.com.br/upload/logo-rodape.png', width=200) # Adicionando o logo
st.title("Buscador de Informações Agrolink")

# Cria um formulário para agrupar o campo de busca e o botão
# Isso evita que a página recarregue ao digitar
with st.form(key='search_form'):
    search_query = st.text_input("O que você deseja buscar?", placeholder="Ex: Cotação do milho, defensivos para soja...")
    submit_button = st.form_submit_button(label='Buscar')

# --- Lógica de Execução ---
if submit_button and search_query:
    # Mostra uma mensagem de "carregando" enquanto a busca é feita
    with st.spinner(f'Buscando por "{search_query}"...'):
        results = perform_search(search_query)

    st.subheader("Resultados da Busca:")
    
    if results:
        # Itera sobre os resultados e os exibe na tela
        for result in results:
            st.markdown(f"### [{result['title']}]({result['link']})") # Título clicável
            st.write(result['snippet']) # Descrição
            st.info(f"Link: {result['link']}")
            st.markdown("---") # Linha divisória
    else:
        st.warning("Nenhum resultado foi encontrado para a sua busca.")
elif submit_button and not search_query:
    st.error("Por favor, digite algo para buscar.")
