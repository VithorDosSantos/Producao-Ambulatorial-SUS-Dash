# --- IMPORTS BÁSICOS NECESSÁRIOS ---
import streamlit as st
import pandas as pd
import numpy as np
import os 
import re
import unicodedata
from datetime import datetime
import plotly.graph_objects as go 
import plotly.express as px
# ------------------------------------

# --- CONFIGURAÇÃO DA PÁGINA (WIDE & INITIAL SIDEBAR) ---
st.set_page_config(
    page_title="Gestão SUS | Executive Dashboard",  
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNÇÕES DE UTILIDADE (COMPLETAS) ---

def normalizar_texto(texto):
    if not isinstance(texto, str): return str(texto)
    text_norm = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return ''.join(e for e in text_norm if e.isalnum() or e.isspace() or e == '_').strip().upper()

def apenas_digitos(texto):
    return ''.join(filter(str.isdigit, str(texto)))

def classificar_unidade(nome, cnes=None, mapa_categorias=None):
    """Classifica unidade por categoria usando o CSV filtro_CATEGORIA ou lógica padrão."""
    # Se houver mapeamento e CNES, usa o mapeamento
    if mapa_categorias and cnes and cnes in mapa_categorias:
        categoria = mapa_categorias[cnes]
        # Adiciona emojis às categorias
        emojis = {
            'UPA': '🚨 UPA',
            'HOSPITAL': '🏥 HOSPITAL',
            'SAMU': '🚑 SAMU',
            'CASA ESPECIALIZADA': '🏢 CASA ESPECIALIZADA',
            'DEPARTAMENTO': '📋 DEPARTAMENTO',
            'UNIDADE BASICA DE SAUDE': '💉 UNIDADE BASICA DE SAUDE'
        }
        return emojis.get(categoria, f'📍 {categoria}')
    
    # Lógica padrão (fallback)
    nome = normalizar_texto(nome)
    if 'UPA' in nome: return '🚨 UPA'
    if 'HOSP' in nome or 'SANTA CASA' in nome: return '🏥 HOSPITAL'
    if 'SAMU' in nome or 'USA' in nome or 'USB' in nome or 'MOTOLANCIA' in nome or 'AMBULANCHA' in nome: return '🚑 SAMU'
    if 'CAPS' in nome or 'CASA' in nome or 'CEO' in nome or 'CENTRO DE ESPECIALIDADES' in nome or 'CTA' in nome: return '🏢 CASA ESPECIALIZADA'
    if 'DERE' in nome or 'DEPARTAMENTO' in nome or 'CENTRAL DE REGULACAO' in nome: return '📋 DEPARTAMENTO'
    if 'UBS' in nome or 'UMS' in nome or 'ESF' in nome or 'UNIDADE' in nome: return '💉 UNIDADE BASICA DE SAUDE'
    return '📍 OUTROS'

def formatar_brl(valor):
    if pd.isna(valor) or valor == 0: return "R$ 0,00"
    try:
        return "R$ {:,.2f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return "R$ 0,00"

def formatar_geral(valor):
    if pd.isna(valor) or valor == 0: return "0"
    try:
        return "{:,.0f}".format(valor).replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return "0"

def formatar_competencia_nome(comp_code):
    comp_limpo = apenas_digitos(str(comp_code).strip())
    if len(comp_limpo) == 4: mes_num = comp_limpo[2:]; prefix_display = comp_limpo[:2]
    elif len(comp_limpo) == 6: mes_num = comp_limpo[4:]; prefix_display = comp_limpo[2:4]
    else: return comp_code
    
    meses_abrev = {'01': 'JAN', '02': 'FEV', '03': 'MAR', '04': 'ABR', '05': 'MAI', '06': 'JUN', '07': 'JUL', '08': 'AGO', '09': 'SET', '10': 'OUT', '11': 'NOV', '12': 'DEZ'}
    nome_mes = meses_abrev.get(mes_num.zfill(2), 'INV')
    return f"{comp_limpo} - {nome_mes}/{prefix_display}"

def get_mes_ano_competencia(cmp_value):
    try:
        cmp_str = apenas_digitos(str(cmp_value))
        if len(cmp_str) == 4: cmp_str = "20" + cmp_str
        if len(cmp_str) != 6: return "999999" 
        return cmp_str
    except:
        return "999999"

def encontrar_coluna_valor(df_columns):
    """ Busca robusta para a coluna de valor no Teto. """
    # Prioridade 1: Total Orçado (aceita 'ORAADO', 'ORCADO', etc.)
    for col_orig in df_columns:
        col_limpo = normalizar_texto(col_orig).replace(' ', '')  # Remove espaços também
        # 'Total OrÃ§ado' vira 'TOTALORAADO'
        if 'TOTAL' in col_limpo and ('ORAADO' in col_limpo or 'ORCADO' in col_limpo):
            return col_orig
    
    # Prioridade 2: Orçamentario (aceita 'ORAAMENTARIO', 'ORCAMENTARIO')
    for col_orig in df_columns:
        col_limpo = normalizar_texto(col_orig).replace(' ', '')
        if 'ORAAMENTARIO' in col_limpo or 'ORCAMENTARIO' in col_limpo:
            return col_orig
        
    # Prioridade 3: Outras variações
    for col_orig in df_columns:
        col_limpo = normalizar_texto(col_orig).replace(' ', '')
        if 'TETO' in col_limpo and 'VALOR' in col_limpo: return col_orig
        if 'VLRTOTAL' in col_limpo or 'VALORTOTAL' in col_limpo: return col_orig
        if 'VALORMON' in col_limpo: return col_orig
        if 'VALORFINANCEIRO' in col_limpo: return col_orig
        
    return None

def quebrar_texto_unidade(texto, limite=15):
    if not isinstance(texto, str): return str(texto)
    palavras = texto.split()
    linhas = []
    linha_atual = []
    contagem = 0
    for p in palavras:
        if contagem + len(p) > limite:
            linhas.append(" ".join(linha_atual)); linha_atual = [p]; contagem = len(p)
        else: linha_atual.append(p); contagem += len(p) + 1
    if linha_atual: linhas.append(" ".join(linha_atual))
    return "<br>".join(linhas)

def get_color_hex(execucao_perc):
    if execucao_perc >= 80: return '#2ecc71' # Verde
    elif execucao_perc >= 50: return '#f39c12' # Laranja
    else: return '#e74c3c' # Vermelho

def render_compact_progress_bar(perc):
    perc_clamped = max(0, min(100, perc))
    color = get_color_hex(perc)
    return f"""<div class="metric-progress-bar"><div class="metric-progress-bar-fill" style="width: {perc_clamped}%; background-color: {color};"></div></div>"""


@st.cache_data
def convert_df_to_csv(df):
    """Converte o DataFrame para CSV no formato Latin-1 (padrão BR) para download."""
    df_export = df.copy()
    for col in df_export.columns:
        if 'BRL' in col or 'Monetário' in col:
            df_export[col] = df_export[col].astype(str).str.replace('.', '', regex=False).str.replace('R$', '', regex=False).str.strip()
        elif 'Execução %' in col:
            df_export[col] = df_export[col].round(1)
            
    return df_export.to_csv(index=False, sep=';', decimal=',', encoding='latin1').encode('latin1')

# --------------------------------------------------------------------------------------------------
# FUNÇÃO DE DEBUG DE COLUNAS
# --------------------------------------------------------------------------------------------------
def diagnostico_colunas(df, prefixo):
    """Retorna uma string formatada com colunas relevantes para debug."""
    if df.empty:
        return f"**{prefixo}**: DataFrame vazio ou leitura falhou."
    
    col_dict = {
        'CNES/Unidade': next((c for c in df.columns if 'CNES_KEY' in c), 'N/A'),
        'Competência': next((c for c in df.columns if 'MES_ORDEM_NUMERICA' in c), 'N/A'),
        'Proc. Code': next((c for c in df.columns if 'PA_PROC_ID' in c), 'N/A'),
    }
    
    if 'Valor_Teto' in df.columns:
        col_dict['Valor Teto (Lido)'] = 'Valor_Teto (OK)'
    elif 'Valor_Aprovado_Bruto' in df.columns:
        col_dict['Valor Aprovado (Lido)'] = 'Valor_Aprovado_Bruto (OK)'

    col_str = " | ".join([f"**{k}**: `{v}`" for k, v in col_dict.items()])
    
    return f"**{prefixo}** ({len(df):,} linhas): {col_str} | **Colunas Originais**: {df.columns.tolist()[:5]}..."

# --- FUNÇÃO AUXILIAR PARA OTIMIZAÇÃO DE DTYPES (NOVO) ---
def optimize_dtypes(df):
    """Reduz o uso de memória de um DataFrame convertendo colunas numéricas para tipos menores."""
    for col in df.columns:
        # Downcast floats
        if df[col].dtype == 'float64':
            df[col] = pd.to_numeric(df[col], downcast='float', errors='ignore')
        # Downcast integers
        elif df[col].dtype == 'int64':
            df[col] = pd.to_numeric(df[col], downcast='integer', errors='ignore')
    return df
# ---------------------------------------------------------

# --- ESTRUTURA DE CARREGAMENTO DE DADOS (REESTRUTURADA E CORRIGIDA) ---

class DataLoader:
    def __init__(self, papa_files_uploaded, espelho_file_uploaded, filtro_adm_tipo):
        self.papa_files_uploaded = papa_files_uploaded
        self.espelho_file_uploaded = espelho_file_uploaded
        self.filtro_adm_tipo = filtro_adm_tipo 
        self.dict_procedimentos = {}
        
    def _clean_numeric_col(self, s):
        """ Limpa e prepara colunas monetárias/numéricas brasileiras para conversão float. """
        s_str = s.astype(str)
        s_clean = s_str.str.replace('R$', '', regex=False).str.strip()
        s_clean = s_clean.str.replace('.', '', regex=False)
        s_clean = s_clean.str.replace(',', '.', regex=False)
        return s_clean.fillna('0')





    @st.cache_data(show_spinner="Carregando e processando arquivos de dados...")
    def load_data_raw(_self):
        df_papa, df_espelho, teto_agrupado, dict_procedimentos_local = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), {}
        papa_dfs = []
        espelho_dfs = []

        minimal_cols = [
            'PA_CODUNI', 'PA_NAT_JUR', 'PA_CMP', 'PA_MVM', 'PA_PROC_ID', 
            'PA_QTDPRO', 'PA_QTDAPR', 'PA_VALPRO', 'PA_VALAPR',
            'QTDAPR', 'QTDPROD', 'QT_PROC', 'QUANTIDADE', 
            'PROCEDIMENTO', 'DS_PROC', 'NOME_PROCEDIMENTO', 
            'ORÇAMENTARIO', 'FISICO', 'CODIGO', 'NUM_CNES' 
        ]
        
        # --- 1. CARREGAMENTO PAPA (PRODUÇÃO) ---
        if not _self.papa_files_uploaded: 
            return df_papa, pd.DataFrame(), pd.DataFrame(), _self.dict_procedimentos
        
        for uploaded_file in _self.papa_files_uploaded:
            try:
                # Lê o conteúdo completo uma única vez
                uploaded_file.seek(0)
                content = uploaded_file.read()
                
                if not content or len(content) == 0:
                    st.warning(f"⚠️ Arquivo {uploaded_file.name} está vazio!")
                    continue
                
                # Detecta separador na primeira linha
                first_line = content.split(b'\n')[0].decode('latin1', errors='ignore')
                sep = ';' if first_line.count(';') > first_line.count(',') else ','
                
                # Lê o CSV a partir do conteúdo em memória
                from io import BytesIO
                df_temp = pd.read_csv(BytesIO(content), dtype=str, encoding='latin1', sep=sep, on_bad_lines='skip')
                
                if df_temp.empty:
                    st.warning(f"⚠️ Arquivo {uploaded_file.name} resultou em DataFrame vazio!")
                    continue
                
                # Limpa caracteres não alfanuméricos do início dos nomes das colunas
                import re
                cleaned_columns = []
                for col in df_temp.columns:
                    match = re.search(r'[A-Za-z0-9_]', col)
                    if match:
                        cleaned_col = col[match.start():]
                    else:
                        cleaned_col = col
                    cleaned_columns.append(cleaned_col.strip())
                df_temp.columns = cleaned_columns
                
            except Exception as e:
                st.error(f"❌ Erro ao processar {uploaded_file.name}: {str(e)}")
                continue
            
            # Debug: mostra arquivo, separador, colunas e competências
            comp_col = next((c for c in df_temp.columns if 'PA_CMP' in c.upper() or 'PA_MVM' in c.upper()), None)
            if comp_col:
                comps_unicas = df_temp[comp_col].unique()[:5]
                st.write(f"📁 {uploaded_file.name} (sep='{sep}', {len(df_temp)} linhas, {len(df_temp.columns)} colunas) | Competências: {comps_unicas.tolist()}")
            else:
                st.error(f"❌ {uploaded_file.name}: Coluna PA_CMP não encontrada! Colunas: {df_temp.columns.tolist()[:10]}")
            
            cols_map_norm = {normalizar_texto(c): c for c in df_temp.columns}
            
            cols_to_keep = [c for c in df_temp.columns if any(mc.upper() in c.upper() for mc in minimal_cols)]
            df_temp = df_temp[cols_to_keep].copy()
            
            def find_col_name(candidates):
                for key in candidates:
                    if key in cols_map_norm:
                        return cols_map_norm[key]
                    literal_lower = next((c for c in df_temp.columns if c.lower() == key.lower()), None)
                    if literal_lower:
                        return literal_lower
                return None
            
            # PA_MVM = mês de movimento (quando aprovado) - PRIORIDADE
            # PA_CMP = competência original (quando realizado) - FALLBACK
            comp_col_name = find_col_name(['PA_MVM', 'MVM', 'PA_CMP', 'CMP'])
            
            if comp_col_name:
                comp_value = df_temp[comp_col_name].iloc[0] if not df_temp.empty and df_temp[comp_col_name].any() else "999999"
                mes_nome_simplificado = apenas_digitos(str(comp_value))
                df_temp['MES_NOME'] = mes_nome_simplificado
                df_temp['MES_ORDEM_NUMERICA'] = get_mes_ano_competencia(mes_nome_simplificado)
                df_temp['MES_NOME_FORMATADO'] = formatar_competencia_nome(mes_nome_simplificado)
                
            else:
                df_temp['MES_ORDEM_NUMERICA'] = '999999'
                df_temp['MES_NOME'] = 'Desconhecido'
                df_temp['MES_NOME_FORMATADO'] = 'Desconhecido'
            
            
            col_val_aprovado = find_col_name(['PA_VALAPR', 'VALAPR'])
            if col_val_aprovado is None: continue 
            df_temp['Valor_Aprovado_Bruto'] = pd.to_numeric(_self._clean_numeric_col(df_temp[col_val_aprovado]), errors='coerce').fillna(0).astype('float32')
            
            
            col_val_apresentado = find_col_name(['PA_VALPRO', 'VALPRO'])
            df_temp['Valor_Apresentado_Bruto'] = pd.to_numeric(_self._clean_numeric_col(df_temp[col_val_apresentado]), errors='coerce').fillna(0).astype('float32') if col_val_apresentado else df_temp['Valor_Aprovado_Bruto'].copy()


            col_qtd = find_col_name(['PA_QTDAPR', 'QTDAPR', 'QUANTIDADE'])
            df_temp['QTD_APROVADA'] = pd.to_numeric(_self._clean_numeric_col(df_temp[col_qtd]), errors='coerce').fillna(0).astype('int32') if col_qtd else np.int32(0)


            col_qtd_apresentada = find_col_name(['PA_QTDPROD', 'PA_QTDPRO', 'QTDPROD'])
            df_temp['QTD_APRESENTADA'] = pd.to_numeric(_self._clean_numeric_col(df_temp[col_qtd_apresentada]), errors='coerce').fillna(0).astype('int32') if col_qtd_apresentada else df_temp['QTD_APROVADA'].copy()

            
            col_cnes = find_col_name(['PA_CODUNI', 'CODUNI', 'CNES'])
            if col_cnes is None:
                st.error(f"❌ Coluna CNES não encontrada no PAPA! Colunas disponíveis: {df_temp.columns.tolist()[:10]}")
                df_temp['CNES_KEY'] = 'CNES_MISSING'
            else:
                df_temp['CNES_KEY'] = df_temp[col_cnes].astype(str).str.strip().str.replace('"', '').str.zfill(7)
            
            col_nat_jur = find_col_name(['PA_NAT_JUR'])
            
            if col_nat_jur in df_temp.columns:
                if _self.filtro_adm_tipo == "Somente Municipal (1031)":
                    linhas_antes = len(df_temp)
                    df_temp = df_temp[df_temp[col_nat_jur].astype(str) == '1031'].copy()
                    if len(df_temp) < linhas_antes:
                        st.write(f"⚠️ {uploaded_file.name}: Filtro 1031 removeu {linhas_antes - len(df_temp)} linhas (restam {len(df_temp)})")
                
                del df_temp[col_nat_jur]

            df_temp = optimize_dtypes(df_temp)
            
            # Debug: mostra quantas linhas o arquivo tem antes de adicionar
            if 'MES_NOME' in df_temp.columns:
                mes_arquivo = df_temp['MES_NOME'].iloc[0] if not df_temp.empty else 'VAZIO'
                st.write(f"📦 {uploaded_file.name} → {len(df_temp)} linhas | Mês: {mes_arquivo}")
            
            papa_dfs.append(df_temp)

        if papa_dfs:
            df_papa = pd.concat(papa_dfs, ignore_index=True)
            
            # Debug: mostra quantas linhas cada mês tem
            if 'MES_NOME' in df_papa.columns:
                meses_count = df_papa['MES_NOME'].value_counts().sort_index()
                st.write(f"📊 Linhas por mês após concat: {meses_count.to_dict()}")
            
        # --- 2. CARREGAMENTO ESPELHO (TETO) ---
        if _self.espelho_file_uploaded:
            df_temp = pd.read_csv(_self.espelho_file_uploaded, dtype=str, encoding='latin1', sep=';', on_bad_lines='skip')
            if not df_temp.empty: 
                espelho_dfs.append(df_temp)

        if espelho_dfs:
            df_espelho = pd.concat(espelho_dfs, ignore_index=True)
            
            col_teto = encontrar_coluna_valor(df_espelho.columns)
            
            if col_teto is None:
                col_teto_fallback = next((c for c in df_espelho.columns if 'ORCAMENTARIO' == normalizar_texto(c)), None)
                col_teto = col_teto_fallback
            
            col_qtd_teto = next((c for c in df_espelho.columns if 'FISICO' == normalizar_texto(c)), None)
            if col_qtd_teto is None:
                qtd_fisico_cands = [c for c in df_espelho.columns if 'QTD_TETO' in c.upper() or 'QTD' in c.upper()]
                col_qtd_teto = qtd_fisico_cands[0] if qtd_fisico_cands else None
            
            df_espelho['Valor_Teto'] = pd.to_numeric(_self._clean_numeric_col(df_espelho[col_teto]), errors='coerce').fillna(0).astype('float32') if col_teto else np.float32(0.0)
            df_espelho['QTD_TETO_FISICO'] = pd.to_numeric(_self._clean_numeric_col(df_espelho[col_qtd_teto]), errors='coerce').fillna(0).astype('int32') if col_qtd_teto else np.int32(0)

            headers_esp = [normalizar_texto(c) for c in df_espelho.columns]
            idx_cnes = next((i for i, h in enumerate(headers_esp) if 'NUM_CNES' in h or 'CNES' in h or 'COD_UNIDADE' in h), None)
            idx_nome = next((i for i, h in enumerate(headers_esp) if ('NOME' in h and 'ESTAB' in h) or 'UNIDADE' in h), None)
            
            if idx_cnes is not None:
                col_cnes = df_espelho.columns[idx_cnes]
                col_nome = df_espelho.columns[idx_nome] if idx_nome is not None else col_cnes
                
                df_espelho['CNES_KEY'] = df_espelho[col_cnes].astype(str).str.strip().str.replace('"', '').str.zfill(7)
                df_espelho['Unidade_Str'] = df_espelho[col_nome].astype(str)
                
                teto_agrupado = df_espelho.groupby(['CNES_KEY', 'Unidade_Str']).agg(
                    Valor_Teto=('Valor_Teto', 'sum'),
                    QTD_TETO_FISICO=('QTD_TETO_FISICO', 'sum')
                ).reset_index()
                teto_agrupado.rename(columns={'Unidade_Str': 'Unidade'}, inplace=True)
                
                teto_agrupado = optimize_dtypes(teto_agrupado)
        else:
            df_espelho = pd.DataFrame()
            teto_agrupado = pd.DataFrame()
        
        return df_papa, df_espelho, teto_agrupado, _self.dict_procedimentos 

# --- FUNÇÕES DE PROCESSAMENTO E CÁLCULO (MANTIDAS COM @st.cache_data) ---

@st.cache_data
def processar_consolidado(df_papa_filtrado, df_teto_agrupado):
    """
    Agrupa a produção por CNES (CNES_KEY) e faz o merge com o Teto Base LIDO.
    
    Usa INNER JOIN para mostrar APENAS estabelecimentos que têm Teto selecionado E Produção.
    """
    col_valor_aprovado = 'Valor_Aprovado_Bruto'
    col_valor_apresentado = 'Valor_Apresentado_Bruto'

    if df_papa_filtrado.empty or df_teto_agrupado.empty:
        # Se um dos lados estiver vazio, retorna DF vazio com colunas esperadas
        return pd.DataFrame(columns=['CNES_KEY', 'Unidade', 'Categoria', 'Valor_Teto', 'Valor_Produzido', 'Valor_Apresentado_Final', 'QTD_APROVADA', 'QTD_APRESENTADA', 'Saldo', '% Execucao'])

    prod_data = df_papa_filtrado.groupby('CNES_KEY').agg(
        Valor_Produzido=(col_valor_aprovado, 'sum'), 
        Valor_Apresentado_Final=(col_valor_apresentado, 'sum'), 
        QTD_APROVADA=('QTD_APROVADA', 'sum'),
        QTD_APRESENTADA=('QTD_APRESENTADA', 'sum') 
    ).reset_index()
    
    # UNIÃO DAS TABELAS PELA CHAVE CNES_KEY (INNER JOIN)
    final = pd.merge(df_teto_agrupado, prod_data, on='CNES_KEY', how='inner').fillna(0)
    
    if final.empty:
        return pd.DataFrame(columns=['CNES_KEY', 'Unidade', 'Categoria', 'Valor_Teto', 'Valor_Produzido', 'Valor_Apresentado_Final', 'QTD_APROVADA', 'QTD_APRESENTADA', 'Saldo', '% Execucao'])
    
    final['Unidade'] = final['Unidade'].astype(str).replace(['0', '0.0'], 'Unidade Desconhecida')
    
    # Carrega o mapa de categorias do CSV (se disponível)
    mapa_cat = None
    try:
        caminho_filtro = os.path.join(os.path.dirname(__file__), 'filtro_CATEGORIA.csv')
        if os.path.exists(caminho_filtro):
            df_cat = pd.read_csv(caminho_filtro, sep=';', encoding='latin1', dtype=str)
            # Normaliza os nomes das colunas
            df_cat.columns = [c.strip() for c in df_cat.columns]
            if 'Num_CNES' in df_cat.columns and 'Categoria' in df_cat.columns:
                df_cat['Num_CNES'] = df_cat['Num_CNES'].astype(str).str.strip()
                df_cat['Categoria'] = df_cat['Categoria'].str.strip().str.upper()
                mapa_cat = dict(zip(df_cat['Num_CNES'], df_cat['Categoria']))
    except Exception as e:
        pass  # Se falhar, usa a lógica padrão
    
    # Aplica a classificação com o mapa de categorias
    final['Categoria'] = final.apply(
        lambda row: classificar_unidade(row['Unidade'], cnes=row['CNES_KEY'], mapa_categorias=mapa_cat), 
        axis=1
    ) 

    final['Saldo'] = final['Valor_Teto'] - final['Valor_Produzido']
    final['% Execucao'] = final.apply(lambda x: (x['Valor_Produzido'] / x['Valor_Teto'] * 100) if x['Valor_Teto'] > 0 else 0, axis=1)
    
    final = optimize_dtypes(final)
        
    return final

@st.cache_data
def processar_tendencia_mensal(df_papa_filtrado_mes, df_teto_agrupado, selected_cnes_keys):
    
    if selected_cnes_keys and not df_papa_filtrado_mes.empty:
        df_papa_tendencia = df_papa_filtrado_mes[df_papa_filtrado_mes['CNES_KEY'].isin(selected_cnes_keys)].copy()
    else:
        df_papa_tendencia = df_papa_filtrado_mes.copy()

    tendencia_prod = df_papa_tendencia.groupby(['MES_NOME', 'MES_ORDEM_NUMERICA', 'MES_NOME_FORMATADO']).agg(
        Valor_Produzido=('Valor_Aprovado_Bruto', 'sum'),
        Valor_Apresentado_Final=('Valor_Apresentado_Bruto', 'sum') # Adicionado Valor Apresentado
    ).reset_index()
    
    if selected_cnes_keys:
        teto_mensal_base = df_teto_agrupado[df_teto_agrupado['CNES_KEY'].isin(selected_cnes_keys)]['Valor_Teto'].sum()
    else:
        teto_mensal_base = df_teto_agrupado['Valor_Teto'].sum()

    tendencia_prod['Valor_Teto_Mensal'] = teto_mensal_base
    
    tendencia_prod['% Execucao'] = tendencia_prod.apply(
        lambda x: (x['Valor_Produzido'] / x['Valor_Teto_Mensal'] * 100) if x['Valor_Teto_Mensal'] > 0 else 0, axis=1
    )
    
    tendencia_prod = tendencia_prod.sort_values(by='MES_ORDEM_NUMERICA', ascending=True)
    
    # Adicionando as colunas formatadas para a tabela de detalhes (abaixo do gráfico)
    tendencia_prod['Valor_Produzido_BRL'] = tendencia_prod['Valor_Produzido'].apply(formatar_brl)
    tendencia_prod['Valor_Apresentado_Final_BRL'] = tendencia_prod['Valor_Apresentado_Final'].apply(formatar_brl) # Formatação
    tendencia_prod['Valor_Teto_Mensal_BRL'] = tendencia_prod['Valor_Teto_Mensal'].apply(formatar_brl)
    tendencia_prod['Mês/Ano'] = tendencia_prod['MES_NOME_FORMATADO'].str.replace(r'^\d{4,6} - ', '', regex=True)
    
    tendencia_prod = optimize_dtypes(tendencia_prod)
    
    return tendencia_prod

@st.cache_data
def calcular_metricas_globais(df_view, num_meses_papa):
    
    teto_base_valor = df_view['Valor_Teto'].sum()
    teto_total_valor = teto_base_valor * num_meses_papa 
    
    teto_base_qtd = df_view['QTD_TETO_FISICO'].sum()
    teto_total_qtd = teto_base_qtd * num_meses_papa
    
    prod = df_view['Valor_Produzido'].sum() 
    valor_apresentado = df_view['Valor_Apresentado_Final'].sum() 
    
    qtd_aprovada = df_view['QTD_APROVADA'].sum()
    qtd_apresentada = df_view['QTD_APRESENTADA'].sum()
    
    saldo = teto_total_valor - prod
    perc = (prod / teto_total_valor * 100) if teto_total_valor > 0 else 0
    
    return {
        'teto_total': teto_total_valor,
        'prod': prod, 
        'valor_apresentado': valor_apresentado, 
        'saldo': saldo,
        'perc': perc,
        'saldo_perc': 100 - perc,
        'saldo_delta_color': "inverse" if saldo < 0 else "normal", 
        'prod_delta_color': "normal" if perc >= 100 else "off", 
        'teto_total_qtd': teto_total_qtd,
        'qtd_aprovada': qtd_aprovada,
        'qtd_apresentada': qtd_apresentada,
    }


# --- ESTILO CSS AVANÇADO (v23.1 - CLARO E COMPACTO) ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Orbitron:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fundo Principal CLARO */
    .stApp { background-color: #f4f7f6; } /* Fundo claro original */
    
    /* Header (Destaque principal) */
    .header-container { 
        background: linear-gradient(90deg, #3498db 0%, #2c3e50 100%); /* Gradiente azul/escuro */
        padding: 2rem; 
        border-radius: 15px; 
        color: white; 
        margin-bottom: 2rem; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.15); 
        text-align: center; 
    }
    .header-container h1 { 
        font-family: 'Inter', sans-serif;
        font-weight: 700; 
        margin: 0; 
        font-size: 2.5rem; 
        color: #ffffff !important; 
    }
    .header-container p { 
        font-weight: 300; 
        font-size: 1.1rem; 
        opacity: 0.9; 
        margin-top: 5px; 
        color: #e0e0e0;
    }

    /* Cards de Métricas (KPIs) - Estilo Vidro/Prateado Compacto */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.95); /* Fundo quase branco com leve transparência */
        backdrop-filter: blur(5px); /* Efeito de vidro sutil */
        padding: 15px 5px;
        border-radius: 16px; /* Borda mais arredondada */
        box-shadow: 0 8px 16px rgba(100, 100, 100, 0.1), inset 0 0 5px rgba(255, 255, 255, 0.8); /* Sombra suave e brilho prateado */
        border: 1px solid rgba(220, 220, 220, 0.7); /* Borda prateada/cinza clara */
        height: 180px; /* Altura aumentada para 180px */
        display: flex;
        flex-direction: column;
        justify-content: space-between; 
        color: #1f2a38;
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px); /* Efeito de elevação ao passar o mouse */
        box-shadow: 0 10px 20px rgba(100, 100, 100, 0.2);
    }
    
    div[data-testid^="stColumn"] div[data-testid="stMetric"] {
        border-top: none !important;
    }
    
    /* Fontes dos títulos principais */
    div[data-testid="stMetric"] label {
        font-size: 1.2rem;
        font-weight: 700;
        color: #2c3e50; 
        text-align: center !important; 
        display: block; 
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }

    /* ESTILOS DE LINHA ÚNICA (COMPACTO) */
    .kpi-content-wrapper {
        display: flex;
        justify-content: space-around; 
        align-items: flex-start;
        width: 100%; 
        margin-top: 5px;
        flex-grow: 1;
    }
    .kpi-item {
        width: 50%; 
        text-align: center; 
        padding: 0 2px;
    }
    
    /* Títulos dentro dos cards (Qtd/Valor) */
    .kpi-title {
        font-size: 0.9rem; /* Levemente maior */
        color: #7f8c8d; /* Cinza neutro */
        font-weight: 600;
        margin-bottom: 2px;
    }
    .kpi-value {
        font-size: 1.3rem; /* Valor maior */
        font-weight: 700;
        color: #1f2a38;
        white-space: nowrap;
    }


    /* Cores Específicas dos Títulos Principal (mantidas para diferenciação) */
    div[data-testid="stMetric"]:nth-child(1) label { color: #3498db; } /* ORÇADO - Azul */
    div[data-testid="stMetric"]:nth-child(2) label { color: #f39c12; } /* APRESENTADO - Laranja */
    div[data-testid="stMetric"]:nth-child(3) label { color: #2ecc71; } /* APROVADO - Verde */

    /* Cores Específicas dos Valores Secundários (usando as cores primárias das métricas) */
    [data-testid="stMetric"]:nth-child(1) .kpi-value { color: #3498db !important; } 
    [data-testid="stMetric"]:nth-child(2) .kpi-value { color: #f39c12 !important; } 
    [data-testid="stMetric"]:nth-child(3) .kpi-value { color: #2ecc71 !important; } 


    /* Barras e Tabs */
    .metric-progress-bar { height: 8px; width: 100%; background-color: #e0e0e0; border-radius: 4px; overflow: hidden; margin-top: 5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #e0e0e0; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        background-color: #ffffff; 
        border-radius: 8px 8px 0px 0px; 
        padding: 0 20px; 
        border: 1px solid #e0e0e0; 
        color: #2c3e50;
        font-weight: 600; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #f4f7f6; /* Fundo principal */
        border-bottom: 3px solid #3498db; 
        color: #3498db !important; 
        box-shadow: none; 
    }
    
    /* Input/Sidebar look */
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; color: #2c3e50; }
    .stTextInput label, .stMultiSelect label { color: #2c3e50; }
    .stTextInput input, .stMultiSelect [data-baseweb="select"] { 
        background-color: #ffffff; 
        border: 1px solid #ccc;
        color: #2c3e50;
    }
    .stButton > button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }

    /* ESTILO FUTURISTA DARK PARA SIDEBAR */
    section[data-testid="stSidebar"] { 
        background-color: #1f2a38; /* Fundo Escuro */
        color: #fff;
        border-right: 1px solid #00bcd4; /* Borda Neon Ciano */
    }
    section[data-testid="stSidebar"] * { 
        color: #ccc; 
    }
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #00bcd4;
        color: #1f2a38;
        font-weight: 700;
        border: none;
    }
    section[data-testid="stSidebar"] h4 { /* Títulos de Navegação */
        color: #00bcd4 !important; /* Texto Neon */
        text-shadow: 0 0 5px rgba(0, 188, 212, 0.4);
    }
    section[data-testid="stSidebar"] hr { /* Divisores */
        border-top: 1px solid rgba(0, 188, 212, 0.3);
    }
    section[data-testid="stSidebar"] .stRadio > label { /* Itens do Radio Button */
        color: #f0f0f0 !important;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] .stRadio div[data-testid="stDecoration"] { /* Cor da bolinha selecionada */
        border-color: #00bcd4 !important;
    }
    section[data-testid="stSidebar"] .stRadio div[data-testid="stDecoration"]::after {
        background-color: #00bcd4 !important;
    }
    section[data-testid="stSidebar"] .stExpander header { /* Estilo do Expander (Caminhos) */
        background-color: #2a3542; 
        border-radius: 8px;
        border: 1px solid #333;
        color: #00bcd4;
        font-weight: 700;
        padding: 10px;
    }
    section[data-testid="stSidebar"] .stExpander div[data-testid="stVerticalBlock"] > div:nth-child(2) { /* Conteúdo do Expander */
        background-color: #1f2a38;
        border: 1px solid #333;
        border-top: none;
        padding: 10px;
        border-radius: 0 0 8px 8px;
    }
    
</style>
""", unsafe_allow_html=True)


# --- CÓDIGO DO DASHBOARD ---

# --- SIDEBAR (Upload de Arquivos) ---
with st.sidebar:
    st.markdown("### 📤 Upload de Dados")
    
    st.markdown("#### 📊 Arquivos PAPA (Produção)")
    papa_files_uploaded = st.file_uploader(
        "Selecione os arquivos PAPA (.csv)",
        type=['csv'],
        accept_multiple_files=True,
        key="papa_upload",
        help="Selecione todos os arquivos PAPA dos meses que deseja analisar"
    )
    
    st.markdown("#### 💰 Arquivo Espelho (Teto)")
    espelho_file_uploaded = st.file_uploader(
        "Selecione o arquivo Espelho (.csv)",
        type=['csv'],
        accept_multiple_files=False,
        key="espelho_upload",
        help="Arquivo com os valores de teto orçamentário"
    )
    
    st.markdown("---")
    st.caption("🔒 Seus arquivos não são armazenados. Os dados são processados apenas durante a sessão.")
    
    st.markdown("---")
    st.markdown("#### 🧭 Navegação Rápida")
    # Menu de navegação para simular o acesso direto às abas
    navigation_option = st.radio(
        "Ir para:", 
        options=["Filtros e Indicadores de Fluxo", "Visão Geral", "Dados Detalhados", "Tendência Mensal"], # Indicadores de Fluxo incluído
        index=0,
        key="navigation_menu"
    )
    
    dicionario_source = None 
    
# --- PRÉ-CARREGAMENTO PARA OBTER CNES DISPONÍVEIS ---
df_papa_raw = pd.DataFrame()
df_espelho_raw = pd.DataFrame()
df_teto_full = pd.DataFrame()
filtro_adm_tipo = "Somente Municipal (1031)"

if papa_files_uploaded and espelho_file_uploaded:
    with st.spinner("🔄 Carregando e processando arquivos..."):
        loader_pre = DataLoader(papa_files_uploaded, espelho_file_uploaded, filtro_adm_tipo)
        
        df_papa_raw_temp, df_espelho_raw, df_teto_full, _ = loader_pre.load_data_raw()
        
        # Debug
        st.success(f"✅ Arquivos carregados! PAPA: {len(df_papa_raw_temp)} linhas | Teto: {len(df_teto_full)} unidades")
        
        if not df_teto_full.empty:
            df_teto_filter_display = df_teto_full.copy()
        else:
            df_teto_full = pd.DataFrame()
else:
    df_teto_full = pd.DataFrame()
    df_papa_raw_temp = pd.DataFrame()
    st.warning("⚠️ Por favor, faça upload dos arquivos PAPA e Espelho para começar a análise.")
    st.stop()


# --- MAIN LAYOUT EXECUTION ---

st.markdown('<div class="header-container"><h1>Gestão Estratégica SIA/SUS | Relatório Executivo</h1><p>Intelligence Dashboard • Teto vs Produção • Tendências</p></div>', unsafe_allow_html=True)


if not df_teto_full.empty and not df_papa_raw_temp.empty: 
    
    # ----------------------------------------------------------------------
    # 2. DEFINIÇÃO DO TETO E PAPA RAW
    # ----------------------------------------------------------------------
    
    df_teto_agrupado = df_teto_full.copy()
    unidades_teto_selecionadas_cnes = df_teto_agrupado['CNES_KEY'].tolist()

    if not unidades_teto_selecionadas_cnes:
        st.warning("Nenhuma unidade de Teto encontrada nos arquivos Espelho. O cálculo do Teto será R$ 0,00.")
        df_papa_raw = pd.DataFrame() 
    else:
        # Debug antes do filtro
        st.write(f"🔍 Debug ANTES filtro: df_papa_raw_temp tem {len(df_papa_raw_temp)} linhas")
        st.write(f"🔍 CNES únicos no PAPA (primeiros 5): {df_papa_raw_temp['CNES_KEY'].unique()[:5].tolist()}")
        st.write(f"🔍 CNES únicos no TETO (primeiros 5): {unidades_teto_selecionadas_cnes[:5]}")
        
        df_papa_raw = df_papa_raw_temp[df_papa_raw_temp['CNES_KEY'].isin(unidades_teto_selecionadas_cnes)].copy()
        st.write(f"🔍 Debug DEPOIS filtro: df_papa_raw tem {len(df_papa_raw)} linhas")

    
    # AVISO SOBRE UNIDADES BASE (MANTIDO SIMPLES, SEM TÍTULO 2)
    st.info(f"O Teto Orçado está sendo calculado com base em **{len(df_teto_agrupado)}** unidades encontradas no arquivo Espelho. A Produção (PAPA) já foi pré-filtrada pela Natureza Jurídica **1031** (Municipal).")
    
    st.markdown("---")
    
    # Debug da condição
    st.write(f"🔍 Verificando condições: df_teto_agrupado empty={df_teto_agrupado.empty}, df_papa_raw empty={df_papa_raw.empty}, tem coluna Valor_Aprovado_Bruto={'Valor_Aprovado_Bruto' in df_papa_raw.columns if not df_papa_raw.empty else False}")
    
    if not df_teto_agrupado.empty and not df_papa_raw.empty and 'Valor_Aprovado_Bruto' in df_papa_raw.columns:
        
        # ----------------------------------------------------------------------
        # 1. PREPARAÇÃO DO FILTRO DE MÊS (UNICIDADE GARANTIDA)
        # ----------------------------------------------------------------------
        
        df_papa_raw['MES_ORDEM_NUMERICA'] = df_papa_raw['MES_ORDEM_NUMERICA'].astype(str).str.strip()
        df_papa_raw['MES_NOME'] = df_papa_raw['MES_NOME'].astype(str).str.strip()
        df_papa_raw['MES_NOME_FORMATADO'] = df_papa_raw['MES_NOME_FORMATADO'].astype(str).str.strip()
        
        meses_para_filtro = df_papa_raw[['MES_NOME', 'MES_ORDEM_NUMERICA', 'MES_NOME_FORMATADO']].drop_duplicates(
            subset=['MES_ORDEM_NUMERICA'], keep='first'
        ).copy()
        
        # Garante que MES_ORDEM_NUMERICA seja numérico para ordenação correta
        meses_para_filtro['MES_ORDEM_NUM_INT'] = pd.to_numeric(meses_para_filtro['MES_ORDEM_NUMERICA'], errors='coerce').fillna(999999).astype(int)
        meses_para_filtro = meses_para_filtro.sort_values(by='MES_ORDEM_NUM_INT', ascending=True)
        
        meses_para_filtro['DISPLAY_KEY'] = meses_para_filtro['MES_NOME_FORMATADO'].str.replace(r'^\d{4,6} - ', '', regex=True) 
        map_nome_para_codigo = meses_para_filtro.set_index('DISPLAY_KEY')['MES_NOME'].to_dict()
        meses_ordenados_display = meses_para_filtro['DISPLAY_KEY'].tolist()
        
        # Debug: Mostra informação sobre competências carregadas
        meses_info = ", ".join(meses_ordenados_display[:5]) + ("..." if len(meses_ordenados_display) > 5 else "")
        if len(meses_ordenados_display) > 0 and 'JAN' not in meses_ordenados_display[0].upper():
            st.info(f"📅 **{len(meses_ordenados_display)} competências carregadas**: {meses_info}. ℹ️ Se janeiro estiver faltando, verifique se há arquivos PAPA para este mês na pasta de dados.")
        else:
            st.info(f"📅 **{len(meses_ordenados_display)} competências carregadas**: {meses_info}") 
        
        
        # ----------------------------------------------------------------------
        # 3. FILTROS DE ANÁLISE (SEMPRE RENDERIZADOS)
        # ----------------------------------------------------------------------
        
        filter_expanded = (navigation_option == "Filtros e Indicadores de Fluxo")
        
        # O BLOCO DE FILTROS é renderizado primeiro
        with st.expander("⚙️ Filtros de Análise (Mês, Categoria, Unidade)", expanded=filter_expanded):
            filter_row = st.container()
            col_m, col_c, col_u = filter_row.columns([1, 1, 2.5]) 
            
            with col_m:
                sel_meses_display = st.multiselect("📅 Competência (Mês):", meses_ordenados_display, default=meses_ordenados_display)
            
            if sel_meses_display:
                sel_meses_codes = [map_nome_para_codigo[nome] for nome in sel_meses_display if nome in map_nome_para_codigo]
                
                df_papa_final = df_papa_raw[df_papa_raw['MES_NOME'].isin(sel_meses_codes)].copy()
                num_meses_papa_filtrado = len(sel_meses_codes)
            else:
                st.warning("Selecione pelo menos uma Competência (Mês) para visualizar os dados.")
                st.stop()
            
            # PROCESSAMENTO DO CONSOLIDADO
            df = processar_consolidado(df_papa_final, df_teto_agrupado)
            
            cats = sorted(df['Categoria'].unique())
            with col_c:
                sel_cat = st.multiselect("🏷️ Filtrar Categoria:", cats)
                df_filtered = df[df['Categoria'].isin(sel_cat)] if sel_cat else df
            
            units = sorted(df_filtered['Unidade'].unique())
            with col_u:
                sel_unit = st.multiselect("🏥 Filtrar Unidade:", units)
                df_view = df_filtered[df_filtered['Unidade'].isin(sel_unit)] if sel_unit else df_filtered
            
            selected_cnes_keys_for_trend = df_view['CNES_KEY'].unique().tolist()


        st.markdown("---")
        
        # CÁLCULO DAS MÉTRICAS GLOBAIS (MOVIDO AQUI PARA SER SEMPRE ACESSÍVEL)
        metrics = calcular_metricas_globais(df_view, num_meses_papa_filtrado)
        
        # ----------------------------------------------------------------------
        # 4. INDICADORES DE FLUXO (KPIs) (Controlado pela Navegação Rápida)
        # ----------------------------------------------------------------------

        if navigation_option == "Filtros e Indicadores de Fluxo":
            st.markdown('### Indicadores de Fluxo 🚀') 
            kpi_container = st.container()

            
            with kpi_container:
                c1, c2, c3 = st.columns(3)

                # --- Card 1: ORÇADO (Qtd + Valor) ---
                with c1:
                    st.markdown(
                        f"""
                        <div data-testid="stMetric">
                            <label>ORÇADO 💰</label>
                            <div class="kpi-content-wrapper">
                                <div class="kpi-item">
                                    <div class="kpi-title">Qtd. Orçada</div>
                                    <div class="kpi-value">{formatar_geral(metrics['teto_total_qtd'])}</div>
                                </div>
                                <div class="kpi-item">
                                    <div class="kpi-title">Valor Teto</div>
                                    <div class="kpi-value">{formatar_brl(metrics['teto_total'])}</div>
                                </div>
                            </div>
                            <div style="height: 20px;"></div>
                        </div>
                        """, unsafe_allow_html=True
                    )

                # --- Card 2: APRESENTADO (Qtd + Valor) ---
                with c2:
                    st.markdown(
                        f"""
                        <div data-testid="stMetric">
                            <label>PRODUÇÃO APRESENTADA 📈</label>
                            <div class="kpi-content-wrapper">
                                <div class="kpi-item">
                                    <div class="kpi-title">Qtd. Apres.</div>
                                    <div class="kpi-value">{formatar_geral(metrics['qtd_apresentada'])}</div>
                                </div>
                                <div class="kpi-item">
                                    <div class="kpi-title">Valor Apres.</div>
                                    <div class="kpi-value">{formatar_brl(metrics['valor_apresentado'])}</div>
                                </div>
                            </div>
                            <div style="height: 20px;"></div>
                        </div>
                        """, unsafe_allow_html=True
                    )
                
                # --- Card 3: APROVADO (Qtd + Valor + Execução) ---
                with c3:
                    delta_color = get_color_hex(metrics['perc'])
                    
                    st.markdown(
                        f"""
                        <div data-testid="stMetric">
                            <label>PRODUÇÃO APROVADA ✅</label>
                            <div class="kpi-content-wrapper">
                                <div class="kpi-item">
                                    <div class="kpi-title">Qtd. Aprov.</div>
                                    <div class="kpi-value">{formatar_geral(metrics['qtd_aprovada'])}</div>
                                </div>
                                <div class="kpi-item">
                                    <div class="kpi-title">Valor Aprov.</div>
                                    <div class="kpi-value">{formatar_brl(metrics['prod'])}</div>
                                </div>
                            </div>
                            <div style="font-size: 0.8rem; font-weight: 600; color: #7f8c8d; text-align: center; margin-top: 5px;">
                                Execução: <span style="color: {delta_color};">{metrics['perc']:.1f}%</span>
                            </div>
                            {render_compact_progress_bar(metrics['perc'])}
                        </div>
                        """, unsafe_allow_html=True
                    )
            
            st.markdown("---") # Separador final dos KPIs
        
        # ----------------------------------------------------------------------
        # 5. CONTEÚDO PRINCIPAL (Controlado pela Navegação Rápida)
        # ----------------------------------------------------------------------
        
        # --- VISÃO GERAL ---
        if navigation_option == "Visão Geral":
            
            st.markdown("## 📊 Visão Geral")
            
            col_charts_1 = st.columns([2, 1])

            with col_charts_1[0]:
                st.subheader("Performance por Unidade: Valor Aprovado vs. Valor Orçado (Top 10)") # Título ajustado
                
                df_chart = df_view.sort_values('Valor_Teto', ascending=False).head(10).copy()
                df_chart['Valor_Teto_Acumulado'] = df_chart['Valor_Teto'] * num_meses_papa_filtrado
                
                df_chart['Unidade_Wrap'] = df_chart['Unidade'].apply(lambda x: quebrar_texto_unidade(x, 15))
                
                fig = go.Figure()
                
                # SÉRIE 1: VALOR ORÇADO (Teto Acumulado)
                fig.add_trace(go.Bar(
                    x=df_chart['Unidade_Wrap'], 
                    y=df_chart['Valor_Teto_Acumulado'], 
                    name='Valor Orçado (Teto)', 
                    marker_color='#e74c3c', # Cor Vermelha/Teto
                    opacity=0.7,
                    text=df_chart['Valor_Teto_Acumulado'].apply(formatar_brl),
                    textposition='outside'
                ))
                
                # SÉRIE 2: VALOR APROVADO (Produção Aprovada)
                fig.add_trace(go.Bar(
                    x=df_chart['Unidade_Wrap'], 
                    y=df_chart['Valor_Produzido'], 
                    name='Valor Aprovado', 
                    marker_color='#3498db', # Cor Azul/Produção
                    opacity=0.9,
                    text=df_chart['Valor_Produzido'].apply(formatar_brl), 
                    textposition='outside'
                ))
                
                fig.update_layout(
                    barmode='group', # Agrupado para comparação lado a lado
                    xaxis_tickangle=45, 
                    legend=dict(orientation="h", y=1.1, x=0.5, xanchor='center', font=dict(color='#2c3e50')), 
                    margin=dict(t=50, b=10, l=10, r=10),
                    height=500, 
                    plot_bgcolor='white', 
                    paper_bgcolor='white', 
                    font=dict(color="#84bef8"), # Cor do texto do gráfico
                    yaxis=dict(title="Valor (R$)", showgrid=True, gridcolor='#f0f0f0'), # Grid mais claro
                    xaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig, use_container_width=True)


            with col_charts_1[1]:
                st.subheader("Distribuição por Categoria")
                
                df_donut = df_view.groupby('Categoria').agg(
                    Total_Produzido=('Valor_Produzido', 'sum')
                ).reset_index().sort_values('Total_Produzido', ascending=False)
                
                exec_cat = df_view.groupby('Categoria').agg(
                    Teto=('Valor_Teto', 'sum'),
                    Producao=('Valor_Produzido', 'sum')
                ).apply(lambda x: (x['Producao'] / (x['Teto'] * num_meses_papa_filtrado) * 100) if (x['Teto'] * num_meses_papa_filtrado) > 0 else 0, axis=1)
                
                df_donut['% Execução'] = df_donut['Categoria'].map(exec_cat.to_dict()).fillna(0)
                df_donut['Execução Formatada'] = df_donut.apply(
                    lambda row: f"{row['% Execução']:.1f}%", axis=1
                )

                fig_donut = go.Figure(data=[go.Pie(
                    labels=df_donut['Categoria'], 
                    values=df_donut['Total_Produzido'], 
                    hole=.3, 
                    marker_colors=px.colors.qualitative.Pastel,
                    hovertemplate="%{label}: %{value:$,.2f} (%{percent})<extra>Execução Média: %{customdata[0]}</extra>",
                    customdata=df_donut[['Execução Formatada']].values 
                )])
                
                fig_donut.update_layout(
                    margin=dict(t=50, b=50, l=10, r=10),
                    showlegend=True,
                    height=500,
                    plot_bgcolor='white', 
                    paper_bgcolor='white',
                    font=dict(color='#2c3e50')
                )
                
                fig_donut.add_annotation(
                    text=f"Execução<br>Total<br><span style='font-size: 1.5rem; color:{get_color_hex(metrics['perc'])}; font-weight: 700;'>{metrics['perc']:.1f}%</span>",
                    x=0.5, y=0.5, font_size=12, showarrow=False,
                    align="center",
                    font=dict(color='#2c3e50')
                )
                
                st.plotly_chart(fig_donut, use_container_width=True)


        # --- DADOS DETALHADOS ---
        elif navigation_option == "Dados Detalhados":
            
            st.markdown("## 📋 Dados Detalhados")
            st.subheader("Detalhes da Execução por Unidade")
            col_title, col_download = st.columns([3, 1])
            
            df_interactive = processar_consolidado(df_papa_final, df_teto_agrupado)
            
            if df_interactive.empty:
                st.warning("Nenhum dado encontrado. A combinação (INNER JOIN) das Unidades de Teto com a Produção (PAPA) não retornou resultados. Verifique os filtros de Mês e as colunas de CNES nos arquivos de origem.")
            else:
                
                df_interactive['QTD_Teto_Acumulado'] = df_interactive['QTD_TETO_FISICO'] * num_meses_papa_filtrado
                df_interactive['Teto Acumulado'] = df_interactive['Valor_Teto'] * num_meses_papa_filtrado
                df_interactive['Saldo Monetário'] = df_interactive['Teto Acumulado'] - df_interactive['Valor_Produzido']
                df_interactive['Execução %'] = df_interactive.apply(
                    lambda row: (row['Valor_Produzido'] / row['Teto Acumulado'] * 100) if row['Teto Acumulado'] > 0 else 0,
                    axis=1
                ).clip(0, 100)
                
                df_interactive['QTD_Teto_Acumulado_GERAL'] = df_interactive['QTD_TETO_FISICO'].apply(formatar_geral) # Usando QTD base (mensal)
                df_interactive['QTD_APRESENTADA_GERAL'] = df_interactive['QTD_APRESENTADA'].apply(formatar_geral)
                df_interactive['QTD_APROVADA_GERAL'] = df_interactive['QTD_APROVADA'].apply(formatar_geral)
                
                df_interactive['Teto Acumulado_BRL'] = df_interactive['Teto Acumulado'].apply(formatar_brl)
                df_interactive['Produção Apresentada_BRL'] = df_interactive['Valor_Apresentado_Final'].apply(formatar_brl) 
                df_interactive['Produção Total_BRL'] = df_interactive['Valor_Produzido'].apply(formatar_brl)
                df_interactive['Saldo Monetário_BRL'] = df_interactive['Saldo Monetário'].apply(formatar_brl)
                df_interactive['Saldo_Numérico'] = df_interactive['Saldo Monetário'] 
                
                df_display = df_interactive[[
                    'Unidade', 'CNES_KEY', 
                    'QTD_Teto_Acumulado_GERAL', 'Teto Acumulado_BRL',
                    'QTD_APRESENTADA_GERAL', 'Produção Apresentada_BRL',
                    'QTD_APROVADA_GERAL', 'Produção Total_BRL', 
                    'Saldo Monetário_BRL', 'Execução %'
                ]].copy()

                df_display.rename(columns={
                    'QTD_Teto_Acumulado_GERAL': 'QTD Orçada',
                    'Teto Acumulado_BRL': 'Valor Orçado',
                    'QTD_APRESENTADA_GERAL': 'QTD Apresentada',
                    'Produção Apresentada_BRL': 'Valor Apresentado',
                    'QTD_APROVADA_GERAL': 'QTD Aprovada',
                    'Produção Total_BRL': 'Valor Aprovado',
                    'Saldo Monetário_BRL': 'Saldo Monetário',
                    'CNES_KEY': 'CNES' 
                }, inplace=True)
                
                csv_data = convert_df_to_csv(df_display.copy()) 

                with col_download:
                    st.download_button(
                        label="⬇️ Baixar Tabela Completa (CSV)",
                        data=csv_data,
                        file_name='detalhe_execucao_sus.csv',
                        mime='text/csv',
                        key='download_detalhe_unidade'
                    )
                
                def color_saldo(val):
                    try:
                        saldo_original = df_interactive.loc[df_interactive['Saldo Monetário_BRL'] == val, 'Saldo_Numérico'].iloc[0] 
                    except:
                        saldo_original = 0.0
                    
                    if saldo_original <= -0.01: 
                        return 'color: #1abc9c; font-weight: 600' # Verde para Saldo Negativo (produção > teto)
                    elif saldo_original >= 0.01: 
                        return 'color: #e74c3c; font-weight: 600' # Vermelho para Saldo Positivo (produção < teto)
                    return 'color: #7f8c8d'

                column_config = {
                    "Execução %": st.column_config.ProgressColumn(
                        "Execução (%)", format="%.1f%%", min_value=0, max_value=100, color='auto' 
                    ),
                    "CNES": st.column_config.TextColumn("CNES", help="Código CNES da Unidade de Saúde"),
                    "QTD Orçada": st.column_config.TextColumn("QTD Orçada"),
                    "Valor Orçado": st.column_config.TextColumn("Valor Orçado"),
                    "QTD Apresentada": st.column_config.TextColumn("QTD Apresentada"),
                    "Valor Apresentado": st.column_config.TextColumn("Valor Apresentado"),
                    "QTD Aprovada": st.column_config.TextColumn("QTD Aprovada"),
                    "Valor Aprovado": st.column_config.TextColumn("Valor Aprovado"),
                    "Saldo Monetário": st.column_config.TextColumn("Saldo Monetário", 
                                                                 help="Saldo restante (positivo = falta produzir, negativo = excedeu a meta)") 
                }
                
                st.dataframe(
                    df_display.style.applymap(color_saldo, subset=['Saldo Monetário']),
                    column_config=column_config,
                    use_container_width=True,
                    hide_index=True,
                    key='unit_selection_data_stable' 
                )


        # --- TENDÊNCIA MENSAL ---
        elif navigation_option == "Tendência Mensal":
            
            st.markdown("## 📈 Tendência Mensal")
            st.subheader("Tendência Mensal de Execução (Teto vs. Produção)")
            st.caption("A Tendência reflete os filtros de Categoria e Unidade aplicados acima.")

            df_tendencia = processar_tendencia_mensal(df_papa_final, df_teto_agrupado, selected_cnes_keys_for_trend)

            if not df_tendencia.empty:
                
                fig_line = px.line(
                    df_tendencia,
                    x='Mês/Ano',
                    y=['Valor_Produzido', 'Valor_Apresentado_Final', 'Valor_Teto_Mensal'],
                    title='Histórico Mensal de Produção Aprovada, Apresentada vs. Teto Orçado',
                    labels={
                        'value': 'Valor (R$)',
                        'Mês/Ano': 'Competência',
                        'variable': 'Métrica'
                    },
                    color_discrete_map={
                        'Valor_Produzido': '#3498db', # Azul (Aprovado)
                        'Valor_Apresentado_Final': '#f39c12', # Laranja (Apresentado)
                        'Valor_Teto_Mensal': '#e74c3c' # Vermelho (Teto)
                    }
                )
                
                fig_line.update_traces(
                    mode='lines+markers',
                    hovertemplate='Mês: %{x}<br>Valor: %{y:$,.2f}<extra></extra>'
                )
                
                fig_line.update_layout(
                    hovermode="x unified",
                    legend_title_text='Legenda',
                    height=500,
                    plot_bgcolor='white', 
                    paper_bgcolor='white',
                    font=dict(color='#2c3e50'),
                    yaxis=dict(title="Valor (R$)", showgrid=True, gridcolor='#f0f0f0'), 
                    xaxis=dict(showgrid=False)
                )
                
                st.plotly_chart(fig_line, use_container_width=True)
                
                st.markdown("##### Detalhe da Execução Mensal")
                df_tendencia_disp = df_tendencia[[
                    'Mês/Ano', 'Valor_Teto_Mensal_BRL', 'Valor_Apresentado_Final_BRL', 'Valor_Produzido_BRL', '% Execucao'
                ]].rename(columns={
                    'Valor_Teto_Mensal_BRL': 'Teto Mensal',
                    'Valor_Apresentado_Final_BRL': 'Valor Apresentado',
                    'Valor_Produzido_BRL': 'Produção Aprovada',
                })
                
                column_config_tendencia = {
                    "Execução %": st.column_config.ProgressColumn(
                        "Execução (%)", format="%.1f%%", min_value=0, max_value=100, color='auto' 
                    ),
                    "Teto Mensal": st.column_config.TextColumn("Teto Mensal"),
                    "Valor Apresentado": st.column_config.TextColumn("Valor Apresentado"),
                    "Produção Aprovada": st.column_config.TextColumn("Produção Aprovada"),
                }
                
                csv_tendencia = convert_df_to_csv(df_tendencia_disp)
                st.download_button(
                    label="⬇️ Baixar Detalhe da Tendência (CSV)",
                    data=csv_tendencia,
                    file_name='detalhe_tendencia_mensal.csv',
                    mime='text/csv',
                    key='download_tendencia'
                )
                
                st.dataframe(df_tendencia_disp, use_container_width=True, hide_index=True, column_config=column_config_tendencia)
                
            else:
                st.warning("Não há dados de produção para os filtros de Categoria/Unidade e Mês selecionados.")
            
# --- Corrigindo o bloco de verificação de carregamento ---
# Os blocos abaixo devem estar no mesmo nível do IF principal

else:
    st.markdown("""
    <div style='text-align: center; margin-top: 100px; padding: 30px; border: 2px dashed #3498db; border-radius: 15px; background-color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
        <h2><span style="color: #3498db;">Aguardando Inicialização...</span></h2>
        <p style='font-size: 1.1rem; color: #7f8c8d;'>
            Verifique o estado de carregamento dos arquivos.
        </p>
    </div>
    """, unsafe_allow_html=True)