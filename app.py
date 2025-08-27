import streamlit as st
import requests

# --- Configuração da Página ---
st.set_page_config(page_title="Buscador Agrolink", page_icon="🔗")

# --- Gerenciamento de Chaves de API (Secrets) ---
# Tenta carregar as três chaves necessárias do Streamlit Secrets.
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SEARCH_ID_WEB = st.secrets["GOOGLE_SEARCH_ENGINE_ID_WEB"]
    SEARCH_ID_LINKEDIN = st.secrets["GOOGLE_SEARCH_ENGINE_ID_LINKEDIN"]
except KeyError as e:
    st.error(f"Erro ao carregar as chaves de API dos Secrets. Verifique a chave: {e}")
    st.error("Certifique-se de que todas as 3 chaves (API_KEY, ..._WEB, ..._LINKEDIN) estão configuradas corretamente no painel do Streamlit Cloud.")
    st.stop()

# --- Função para Realizar a Busca ---
# A função agora recebe o ID do mecanismo de busca como um parâmetro.
def perform_search(query: str, engine_id: str):
    """Chama a API do Google Custom Search e retorna os resultados formatados."""
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={engine_id}&q={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança um erro para respostas HTTP ruins (4xx ou 5xx)
        
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
st.title("Buscador de Informações Agrolink")

# Seletor para o usuário escolher onde buscar
search_option = st.radio(
    "Onde você deseja pesquisar?",
    ('Toda a Web', 'Apenas no LinkedIn'),
    horizontal=True,
    label_visibility="collapsed" # Esconde o rótulo para um visual mais limpo
)

# Formulário para a barra de busca e o botão
with st.form(key='search_form'):
    search_query = st.text_input("Digite sua busca", placeholder="Ex: Diretor de Marketing, Vagas Agronomia...")
    submit_button = st.form_submit_button(label='Buscar')

# --- Lógica de Execução ---
if submit_button and search_query:
    # Escolhe o ID do mecanismo de busca correto baseado na seleção do usuário
    if search_option == 'Toda a Web':
        selected_engine_id = SEARCH_ID_WEB
        st.info("Buscando em toda a Web...")
    else:
        selected_engine_id = SEARCH_ID_LINKEDIN
        st.info("Buscando apenas no LinkedIn...")

    # Mostra uma mensagem de "carregando" enquanto a busca é feita
    with st.spinner(f'Pesquisando por "{search_query}"...'):
        results = perform_search(search_query, engine_id=selected_engine_id)

    st.subheader("Resultados da Busca:")
    
    if results:
        # Itera sobre os resultados e os exibe na tela
        for result in results:
            st.markdown(f"### [{result['title']}]({result['link']})")
            st.write(result['snippet'])
            st.info(f"Link: {result['link']}")
            st.markdown("---") # Linha divisória
    else:
        st.warning("Nenhum resultado foi encontrado para a sua busca.")
elif submit_button and not search_query:
    st.error("Por favor, digite algo para buscar.")
