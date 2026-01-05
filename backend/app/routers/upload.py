"""
Router para upload de arquivos PAPA e Espelho
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import pandas as pd

from ..models.schemas import UploadResponse
from ..services.leitura_csv import ler_csv_papa, ler_csv_espelho
from ..services.regras_sus import processar_papa, processar_espelho
from ..services.limpeza_dados import carregar_mapa_categorias
from ..services.agregacoes import consolidar_producao_teto
from ..utils.state import app_state

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/papa", response_model=UploadResponse)
async def upload_papa(files: List[UploadFile] = File(...)):
    """
    Upload de múltiplos arquivos PAPA (produção).
    
    - Aceita múltiplos arquivos CSV
    - Aplica todas as regras SUS
    - Filtra por Natureza Jurídica 1031 (Municipal)
    - Armazena em memória para processamento
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")
        
        papa_dfs = []
        nomes_arquivos = []
        
        for file in files:
            # Lê conteúdo
            conteudo = await file.read()
            nome_arquivo = file.filename
            
            # Lê CSV
            df_temp = ler_csv_papa(conteudo, nome_arquivo)
            
            # Processa com regras SUS
            df_processado = processar_papa(df_temp, nome_arquivo, filtrar_municipal=True)
            
            papa_dfs.append(df_processado)
            nomes_arquivos.append(nome_arquivo)
        
        # Concatena todos os arquivos
        df_papa_final = pd.concat(papa_dfs, ignore_index=True)
        
        # Carrega mapa de categorias ANTES de armazenar
        mapa_cat = carregar_mapa_categorias()
        if mapa_cat:
            app_state.set_mapa_categorias(mapa_cat)
        
        # Armazena no estado
        app_state.set_dados_papa(df_papa_final, nomes_arquivos)
        
        # Se já tem teto, consolida
        if app_state.df_teto is not None:
            df_consolidado = consolidar_producao_teto(app_state.df_papa, app_state.df_teto)
            app_state.set_consolidado(df_consolidado)
        
        return UploadResponse(
            success=True,
            message=f"{len(files)} arquivo(s) PAPA processado(s) com sucesso",
            detalhes={
                "total_linhas": len(df_papa_final),
                "arquivos": nomes_arquivos,
                "competencias_unicas": len(df_papa_final['MES_NOME'].unique())
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivos: {str(e)}")


@router.post("/espelho", response_model=UploadResponse)
async def upload_espelho(file: UploadFile = File(...)):
    """
    Upload de arquivo Espelho (teto orçamentário).
    
    - Aceita um único arquivo CSV
    - Processa e agrupa por CNES
    - Calcula teto base mensal
    """
    try:
        # Lê conteúdo
        conteudo = await file.read()
        nome_arquivo = file.filename
        
        # Lê CSV
        df_temp = ler_csv_espelho(conteudo)
        
        # Processa com regras SUS
        mapa_cat = app_state.mapa_categorias
        df_processado = processar_espelho(df_temp, mapa_categorias=mapa_cat)
        
        # Armazena no estado
        app_state.set_dados_teto(df_processado, nome_arquivo)
        
        # Se já tem PAPA, consolida
        if app_state.df_papa is not None:
            df_consolidado = consolidar_producao_teto(app_state.df_papa, app_state.df_teto)
            app_state.set_consolidado(df_consolidado)
        
        return UploadResponse(
            success=True,
            message="Arquivo Espelho processado com sucesso",
            detalhes={
                "total_unidades": len(df_processado),
                "arquivo": nome_arquivo
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@router.get("/status")
async def get_status():
    """
    Retorna status do upload e dados carregados.
    """
    return app_state.get_info()


@router.delete("/reset")
async def reset_dados():
    """
    Limpa todos os dados armazenados.
    """
    app_state.reset()
    return {"success": True, "message": "Dados resetados com sucesso"}
