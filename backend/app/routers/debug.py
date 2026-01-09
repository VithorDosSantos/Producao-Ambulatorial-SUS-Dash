"""
Router para debug e informações de estado
"""
from fastapi import APIRouter
from ..utils.state import app_state

router = APIRouter(prefix="/debug", tags=["Debug"])


@router.get("/state")
async def get_state_info():
    """
    Retorna informações sobre o estado atual da aplicação
    """
    return {
        "tem_dados": app_state.tem_dados(),
        "df_papa_exists": app_state.df_papa is not None,
        "df_papa_rows": len(app_state.df_papa) if app_state.df_papa is not None else 0,
        "df_teto_exists": app_state.df_teto is not None,
        "df_teto_rows": len(app_state.df_teto) if app_state.df_teto is not None else 0,
        "df_consolidado_exists": app_state.df_consolidado is not None,
        "df_consolidado_rows": len(app_state.df_consolidado) if app_state.df_consolidado is not None else 0,
        "arquivos_papa": app_state.arquivos_papa,
        "arquivo_espelho": app_state.arquivo_espelho,
        "timestamp_upload": app_state.timestamp_upload.isoformat() if app_state.timestamp_upload else None
    }
