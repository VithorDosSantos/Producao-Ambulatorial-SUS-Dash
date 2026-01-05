"""
Gerenciador de estado da aplicação (armazenamento em memória)
"""
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime


class AppState:
    """
    Classe singleton para gerenciar estado da aplicação em memória.
    
    Em produção, isso deve ser substituído por Redis ou banco de dados.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa o estado vazio"""
        self.df_papa: Optional[pd.DataFrame] = None
        self.df_teto: Optional[pd.DataFrame] = None
        self.df_consolidado: Optional[pd.DataFrame] = None
        self.mapa_categorias: Optional[Dict[str, str]] = None
        self.num_meses: int = 0
        self.timestamp_upload: Optional[datetime] = None
        self.arquivos_papa: List[str] = []
        self.arquivo_espelho: Optional[str] = None
    
    def reset(self):
        """Limpa todos os dados"""
        self._initialize()
    
    def tem_dados(self) -> bool:
        """Verifica se há dados carregados"""
        return (
            self.df_papa is not None and 
            not self.df_papa.empty and 
            self.df_teto is not None and 
            not self.df_teto.empty
        )
    
    def set_dados_papa(self, df: pd.DataFrame, arquivos: List[str]):
        """Define dados PAPA"""
        self.df_papa = df
        self.arquivos_papa = arquivos
        self.timestamp_upload = datetime.now()
    
    def set_dados_teto(self, df: pd.DataFrame, arquivo: str):
        """Define dados Teto/Espelho"""
        self.df_teto = df
        self.arquivo_espelho = arquivo
    
    def set_consolidado(self, df: pd.DataFrame):
        """Define dados consolidados"""
        self.df_consolidado = df
    
    def set_mapa_categorias(self, mapa: Dict[str, str]):
        """Define mapeamento de categorias"""
        self.mapa_categorias = mapa
    
    def get_competencias(self) -> List[dict]:
        """Retorna lista de competências disponíveis"""
        if self.df_papa is None or self.df_papa.empty:
            return []
        
        comps = self.df_papa[['MES_NOME', 'MES_ORDEM_NUMERICA', 'MES_NOME_FORMATADO']].drop_duplicates()
        comps['MES_ORDEM_NUM_INT'] = pd.to_numeric(comps['MES_ORDEM_NUMERICA'], errors='coerce').fillna(999999).astype(int)
        comps = comps.sort_values('MES_ORDEM_NUM_INT')
        
        resultado = []
        for _, row in comps.iterrows():
            display_name = row['MES_NOME_FORMATADO'].replace(row['MES_NOME'] + ' - ', '')
            resultado.append({
                'codigo': row['MES_NOME'],
                'nome': display_name,
                'ordem': row['MES_ORDEM_NUMERICA']
            })
        
        return resultado
    
    def get_categorias(self) -> List[str]:
        """Retorna lista de categorias disponíveis (sem emoji)"""
        if self.df_consolidado is None or self.df_consolidado.empty:
            return []
        
        # Remove emojis das categorias para os filtros
        categorias = self.df_consolidado['Categoria'].unique().tolist()
        categorias_sem_emoji = []
        
        for cat in categorias:
            # Remove emojis (primeiros caracteres até encontrar letra)
            cat_limpa = cat
            for i, c in enumerate(cat):
                if c.isalpha():
                    cat_limpa = cat[i:].strip()
                    break
            categorias_sem_emoji.append(cat_limpa)
        
        return sorted(list(set(categorias_sem_emoji)))
    
    def get_unidades(self, categorias: Optional[List[str]] = None) -> List[dict]:
        """
        Retorna lista de unidades (opcionalmente filtradas por categoria).
        
        Args:
            categorias: Lista de categorias para filtrar (opcional)
            
        Returns:
            Lista de dicionários com unidade e CNES
        """
        if self.df_consolidado is None or self.df_consolidado.empty:
            return []
        
        df = self.df_consolidado.copy()
        
        if categorias:
            # Remove emojis das categorias para comparação
            df['Categoria_Limpa'] = df['Categoria'].apply(lambda x: ''.join([c for i, c in enumerate(x) if c.isalpha() or i > 0]).strip())
            df = df[df['Categoria_Limpa'].isin(categorias)]
        
        resultado = []
        for _, row in df[['Unidade', 'CNES_KEY']].drop_duplicates().iterrows():
            resultado.append({
                'nome': row['Unidade'],
                'cnes': row['CNES_KEY']
            })
        
        return sorted(resultado, key=lambda x: x['nome'])
    
    def filtrar_papa_por_competencias(self, competencias: List[str]) -> pd.DataFrame:
        """
        Filtra dados PAPA por competências selecionadas.
        
        Args:
            competencias: Lista de códigos de competência
            
        Returns:
            DataFrame filtrado
        """
        if self.df_papa is None or self.df_papa.empty:
            return pd.DataFrame()
        
        return self.df_papa[self.df_papa['MES_NOME'].isin(competencias)].copy()
    
    def get_info(self) -> dict:
        """Retorna informações sobre o estado atual"""
        return {
            'tem_dados': self.tem_dados(),
            'num_linhas_papa': len(self.df_papa) if self.df_papa is not None else 0,
            'num_unidades_teto': len(self.df_teto) if self.df_teto is not None else 0,
            'num_arquivos_papa': len(self.arquivos_papa),
            'arquivo_espelho': self.arquivo_espelho,
            'timestamp_upload': self.timestamp_upload.isoformat() if self.timestamp_upload else None
        }


# Instância global
app_state = AppState()
