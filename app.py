import streamlit as st
import requests
import pandas as pd
import io

# --- Configuração da Página ---
st.set_page_config(page_title="Buscador Agrolink", page_icon="🔗", layout="wide")

# --- Gerenciamento de Chaves de API (Secrets) ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SEARCH_ID_WEB = st.secrets["GOOGLE_SEARCH_ENGINE_ID_WEB"]
    SEARCH_ID_LINKEDIN = st.secrets["GOOGLE_SEARCH_ENGINE_ID_LINKEDIN"]
except KeyError as e:
    st.error(f"Erro ao carregar as chaves de API. Verifique a chave: {e}")
    st.stop()

# --- Função de Busca (sem alterações) ---
def perform_search(query: str, engine_id: str):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={engine_id}&q={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        search_results = response.json().get('items', [])
        return search_results
    except requests.exceptions.RequestException:
        return None

# --- UI - Título Principal ---
st.title("🔎 Buscador de Informações Agrolink")

# --- Funcionalidade 1: Busca em Lote por Arquivo ---
st.header("Busca de Empresas em Lote no LinkedIn")
st.markdown("Faça o upload de um arquivo `.txt` ou `.csv` com um nome de empresa por linha.")

uploaded_file = st.file_uploader(
    "Escolha o arquivo", type=['txt', 'csv'], label_visibility="collapsed"
)

if uploaded_file is not None:
    # Ler as empresas do arquivo
    try:
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        companies = [line.strip() for line in stringio.readlines() if line.strip()]
        st.success(f"Arquivo lido com sucesso! {len(companies)} empresas encontradas.")
        
        if st.button(f"Buscar LinkedIn para as {len(companies)} empresas"):
            results_list = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, company_name in enumerate(companies):
                # Para cada empresa, montamos uma query de busca otimizada
                query = f'"{company_name}" site:linkedin.com/company/'
                
                # Usamos a função de busca com o ID do LinkedIn
                search_results = perform_search(query, engine_id=SEARCH_ID_LINKEDIN)
                
                # Pegamos o primeiro resultado, que geralmente é o mais relevante
                if search_results:
                    first_result = search_results[0]
                    result_link = first_result.get('link')
                else:
                    result_link = "Nenhum resultado encontrado"

                results_list.append({
                    "Empresa Buscada": company_name,
                    "Link Encontrado": result_link
                })
                
                # Atualiza a barra de progresso
                progress_bar.progress((i + 1) / len(companies))
                status_text.text(f"Buscando: {company_name} ({i+1}/{len(companies)})")
            
            status_text.success("Busca em lote finalizada!")

            # Exibe os resultados em uma tabela
            df_results = pd.DataFrame(results_list)
            st.dataframe(df_results, use_container_width=True)

            # Oferece a opção de download
            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df_to_csv(df_results)
            st.download_button(
                label="📥 Baixar resultados como CSV",
                data=csv,
                file_name="resultados_linkedin.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")

st.markdown("---")

# --- Funcionalidade 2: Busca Manual (como antes) ---
st.header("Busca Manual")

search_option = st.radio(
    "Onde pesquisar?", ('Toda a Web', 'Apenas no LinkedIn'), horizontal=True
)

with st.form(key='manual_search_form'):
    search_query = st.text_input("Digite sua busca", placeholder="Ex: Cotação do milho, Vagas Agronomia...")
    submit_button = st.form_submit_button(label='Buscar')

if submit_button and search_query:
    engine_id = SEARCH_ID_WEB if search_option == 'Toda a Web' else SEARCH_ID_LINKEDIN
    with st.spinner(f'Pesquisando por "{search_query}"...'):
        results = perform_search(search_query, engine_id=engine_id)

    st.subheader("Resultados:")
    if results:
        for item in results:
            st.markdown(f"### [{item.get('title')}]({item.get('link')})")
            st.write(item.get('snippet'))
            st.info(f"Link: {item.get('link')}")
    else:
        st.warning("Nenhum resultado encontrado.")
