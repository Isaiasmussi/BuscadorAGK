import streamlit as st
import requests
import pandas as pd
import io

# --- Configuração da Página ---
st.set_page_config(page_title="Buscador de Informações", page_icon="🔎", layout="wide")

# --- Gerenciamento de Chaves de API (Secrets) ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    SEARCH_ID_WEB = st.secrets["GOOGLE_SEARCH_ENGINE_ID_WEB"]
    SEARCH_ID_LINKEDIN = st.secrets["GOOGLE_SEARCH_ENGINE_ID_LINKEDIN"]
except KeyError as e:
    st.error(f"Erro ao carregar as chaves de API. Verifique a chave: {e}")
    st.stop()

# --- Função de Busca ---
def perform_search(query: str, engine_id: str):
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={engine_id}&q={query}"
    try:
        response = requests.get(url)
        if response.status_code == 429:
            return "QUOTA_EXCEEDED"
        response.raise_for_status()
        return response.json().get('items', [])
    except requests.exceptions.RequestException:
        return None

# --- UI - Título Principal ---
st.title("🔎 Buscador de Informações Agrolink")

# --- Abas para Organização ---
tab1, tab2, tab3, tab4 = st.tabs(["🏢 Busca de Empresas", "👤 Busca de Pessoas", "👔 Busca por Cargos", "✍️ Busca Manual"])

# --- Funcionalidade 1: Busca de Empresas em Lote ---
with tab1:
    st.header("Busca de Empresas em Lote no LinkedIn")
    st.markdown("Faça o upload de um arquivo `.txt` ou `.csv` com um nome de empresa por linha.")
    uploaded_file_companies = st.file_uploader(
        "Escolha o arquivo de empresas", type=['txt', 'csv'], 
        key="companies_uploader" # O 'key' é crucial para o Streamlit diferenciar os uploaders em cada aba
    )
    if uploaded_file_companies:
        stringio = io.StringIO(uploaded_file_companies.getvalue().decode("utf-8"))
        companies = [line.strip() for line in stringio.readlines() if line.strip()]
        st.success(f"Arquivo lido! {len(companies)} empresas encontradas.")

        if st.button(f"Buscar LinkedIn para as {len(companies)} empresas", key="btn_companies"):
            results_list = []
            progress_bar = st.progress(0, text="Iniciando busca...")
            for i, company_name in enumerate(companies):
                query = f'"{company_name}" site:linkedin.com/company/'
                search_results = perform_search(query, engine_id=SEARCH_ID_LINKEDIN)
                result_link = search_results[0].get('link') if search_results and isinstance(search_results, list) else "Nenhum resultado"
                results_list.append({"Empresa Buscada": company_name, "Link Encontrado": result_link})
                progress_bar.progress((i + 1) / len(companies), text=f"Buscando: {company_name}")
            st.success("Busca finalizada!")
            df_results = pd.DataFrame(results_list)
            st.dataframe(df_results, use_container_width=True)
            csv = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 Baixar CSV", data=csv, file_name="empresas_linkedin.csv", mime="text/csv")

# --- Funcionalidade 2: Busca de Pessoas em Lote ---
with tab2:
    st.header("Busca de Pessoas em Lote no LinkedIn")
    st.markdown("Faça o upload de um arquivo `.csv` com as colunas `Nome`, `Empresa` e `Cargo`.")
    uploaded_file_people = st.file_uploader(
        "Escolha o arquivo CSV de pessoas", type=['csv'], key="people_uploader"
    )
    if uploaded_file_people:
        try:
            df_pessoas = pd.read_csv(uploaded_file_people)
            if 'Nome' not in df_pessoas.columns:
                st.error("O arquivo CSV precisa ter pelo menos uma coluna chamada 'Nome'.")
            else:
                st.success(f"Arquivo lido! {len(df_pessoas)} pessoas para buscar.")
                if st.button(f"Buscar perfis para as {len(df_pessoas)} pessoas", key="btn_people"):
                    results_list = []
                    progress_bar = st.progress(0, text="Iniciando busca...")
                    for index, row in df_pessoas.iterrows():
                        nome = row.get('Nome', '')
                        empresa = str(row.get('Empresa', '')) if pd.notna(row.get('Empresa')) else ""
                        cargo = str(row.get('Cargo', '')) if pd.notna(row.get('Cargo')) else ""
                        query = f'"{nome}" "{empresa}" "{cargo}" site:linkedin.com/in/'
                        search_results = perform_search(query, engine_id=SEARCH_ID_LINKEDIN)
                        if search_results and isinstance(search_results, list):
                            first_result = search_results[0]
                            result_link, result_title = first_result.get('link'), first_result.get('title')
                        else:
                            result_link, result_title = "Nenhum resultado", "-"
                        results_list.append({"Nome Buscado": nome, "Empresa": empresa, "Cargo": cargo, "Perfil Encontrado": result_link, "Título do Perfil": result_title})
                        progress_bar.progress((index + 1) / len(df_pessoas), text=f"Buscando: {nome}")
                    st.success("Busca finalizada!")
                    df_results = pd.DataFrame(results_list)
                    st.dataframe(df_results, use_container_width=True)
                    csv = df_results.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Baixar CSV", data=csv, file_name="perfis_linkedin.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")

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
                if st.button(f"Buscar perfis para os {len(df_cargos)} cargos", key="btn_cargos"):
                    results_list = []
                    progress_bar = st.progress(0, text="Iniciando busca...")
                    for index, row in df_cargos.iterrows():
                        cargo = row.get('Cargo', '').strip()
                        empresa_raw = row.get('Empresa', '')
                        empresa = str(empresa_raw).strip() if pd.notna(empresa_raw) else ""
                        query = f'"{cargo}" "{empresa}" site:linkedin.com/in/'
                        search_results = perform_search(query, engine_id=SEARCH_ID_LINKEDIN)
                        if search_results and isinstance(search_results, list):
                            links = [res.get('link') for res in search_results[:3]]
                            titles = [res.get('title') for res in search_results[:3]]
                            results_list.append({"Cargo Buscado": cargo, "Empresa": empresa if empresa else "Qualquer", "Resultado 1": links[0] if len(links) > 0 else "N/A", "Título 1": titles[0] if len(titles) > 0 else "N/A", "Resultado 2": links[1] if len(links) > 1 else "N/A", "Título 2": titles[1] if len(titles) > 1 else "N/A", "Resultado 3": links[2] if len(links) > 2 else "N/A", "Título 3": titles[2] if len(titles) > 2 else "N/A"})
                        else:
                            results_list.append({"Cargo Buscado": cargo, "Empresa": empresa, "Resultado 1": "Nenhum resultado", "Título 1": "-", "Resultado 2": "-", "Título 2": "-", "Resultado 3": "-", "Título 3": "-"})
                        progress_bar.progress((index + 1) / len(df_cargos), text=f"Buscando: {cargo} na {empresa}")
                    st.success("Busca finalizada!")
                    df_results = pd.DataFrame(results_list)
                    st.dataframe(df_results, use_container_width=True)
                    csv = df_results.to_csv(index=False).encode('utf-8')
                    st.download_button(label="📥 Baixar CSV", data=csv, file_name="cargos_linkedin.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar o arquivo: {e}")

# --- Funcionalidade 4: Busca Manual ---
with tab4:
    st.header("Busca Manual Avulsa")
    search_option = st.radio("Onde pesquisar?", ('Toda a Web', 'Apenas no LinkedIn'), horizontal=True, key="manual_radio")
    with st.form(key='manual_search_form'):
        search_query = st.text_input("Digite sua busca", placeholder="Ex: Cotação do milho...")
        submit_button = st.form_submit_button(label='Buscar')
    if submit_button and search_query:
        engine_id = SEARCH_ID_WEB if search_option == 'Toda a Web' else SEARCH_ID_LINKEDIN
        with st.spinner(f'Pesquisando por "{search_query}"...'):
            results = perform_search(search_query, engine_id=engine_id)
        st.subheader("Resultados:")
        if results and isinstance(search_results, list):
            for item in results:
                st.markdown(f"### [{item.get('title')}]({item.get('link')})")
                st.write(item.get('snippet'))
                st.info(f"Link: {item.get('link')}")
        elif results == "QUOTA_EXCEEDED":
            st.error("⚠️ Limite diário de 100 buscas da API do Google foi atingido!")
        else:
            st.warning("Nenhum resultado encontrado.")
