import streamlit as st
import requests
import pandas as pd
import io

# --- Configuração da Página ---
st.set_page_config(page_title="Buscador Agrolink", page_icon="🔎", layout="wide")

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
        return response.json().get('items', [])
    except requests.exceptions.RequestException:
        return None

# --- UI - Título Principal ---
st.title("🔎 Buscador de Informações Agrolink")

# --- Abas para Organização ---
tab1, tab2, tab3 = st.tabs(["📁 Busca em Lote", "👤 Busca de Pessoas", "👔 Busca por Cargos"])

# --- Funcionalidade 1: Busca de Empresas em Lote ---
with tab1:
    st.header("Busca de Empresas em Lote no LinkedIn")
    st.markdown("Faça o upload de um arquivo `.txt` ou `.csv` com um nome de empresa por linha.")
    uploaded_file_companies = st.file_uploader(
        "Escolha o arquivo de empresas", type=['txt', 'csv'], key="companies_uploader"
    )
    if uploaded_file_companies:
        stringio = io.StringIO(uploaded_file_companies.getvalue().decode("utf-8"))
        companies = [line.strip() for line in stringio.readlines() if line.strip()]
        if st.button(f"Buscar LinkedIn para as {len(companies)} empresas"):
            # (Lógica da busca de empresas aqui, como na versão anterior)
            # ...

# --- Funcionalidade 2: Busca de Pessoas em Lote ---
with tab2:
    st.header("Busca de Pessoas em Lote no LinkedIn")
    st.markdown("Faça o upload de um arquivo `.csv` com as colunas `Nome`, `Empresa` e `Cargo`.")
    uploaded_file_people = st.file_uploader(
        "Escolha o arquivo CSV de pessoas", type=['csv'], key="people_uploader"
    )
    if uploaded_file_people:
        # (Lógica da busca de pessoas aqui, como na versão anterior)
        # ...

# --- Funcionalidade 3: Busca por Cargos em Lote ---
with tab3:
    st.header("Busca por Cargos em Lote no LinkedIn")
    st.markdown("Faça o upload de um arquivo `.csv` com as colunas `Cargo` e `Empresa` (opcional).")
    uploaded_file_cargos = st.file_uploader(
        "Escolha o arquivo CSV de cargos", type=['csv'], key="cargos_uploader"
    )
    if uploaded_file_cargos:
        try:
            df_cargos = pd.read_csv(uploaded_file_cargos)
            if 'Cargo' not in df_cargos.columns:
                st.error("O arquivo CSV precisa ter pelo menos uma coluna chamada 'Cargo'.")
            else:
                st.success(f"Arquivo lido! {len(df_cargos)} cargos para buscar.")
                if st.button(f"Buscar perfis para os {len(df_cargos)} cargos"):
                    results_list = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for index, row in df_cargos.iterrows():
                        cargo = row.get('Cargo', '').strip()
                        empresa = row.get('Empresa', '').strip()
                        
                        # Constrói a query de busca
                        query = f'"{cargo}" "{empresa}" site:linkedin.com/in/'
                        
                        search_results = perform_search(query, engine_id=SEARCH_ID_LINKEDIN)
                        
                        if search_results:
                            # Pega os 3 primeiros resultados para dar mais opções
                            links = [res.get('link') for res in search_results[:3]]
                            titles = [res.get('title') for res in search_results[:3]]
                            
                            results_list.append({
                                "Cargo Buscado": cargo,
                                "Empresa": empresa if empresa else "Qualquer",
                                "Resultado 1": links[0] if len(links) > 0 else "N/A",
                                "Título 1": titles[0] if len(titles) > 0 else "N/A",
                                "Resultado 2": links[1] if len(links) > 1 else "N/A",
                                "Título 2": titles[1] if len(titles) > 1 else "N/A",
                                "Resultado 3": links[2] if len(links) > 2 else "N/A",
                                "Título 3": titles[2] if len(titles) > 2 else "N/A",
                            })
                        else:
                             results_list.append({
                                "Cargo Buscado": cargo, "Empresa": empresa, "Resultado 1": "Nenhum resultado", "Título 1": "-", "Resultado 2": "-", "Título 2": "-", "Resultado 3": "-", "Título 3": "-",
                            })
                        
                        progress_bar.progress((index + 1) / len(df_cargos))
                        status_text.text(f"Buscando: {cargo} ({index+1}/{len(df_cargos)})")
                    
                    status_text.success("Busca por cargos finalizada!")
                    df_results = pd.DataFrame(results_list)
                    st.dataframe(df_results, use_container_width=True)

                    @st.cache_data
                    def convert_df_to_csv(df):
                        return df.to_csv(index=False).encode('utf-8')

                    csv = convert_df_to_csv(df_results)
                    st.download_button(
                        label="📥 Baixar resultados como CSV",
                        data=csv,
                        file_name="resultados_cargos_linkedin.csv",
                        mime="text/csv",
                    )
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")

st.markdown("---")

# --- Funcionalidade 4: Busca Manual (como antes) ---
st.header("Busca Manual Avulsa")
# (O código da busca manual continua aqui, sem alterações)
# ...
