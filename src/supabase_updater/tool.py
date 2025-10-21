# tool.py
# Import compatível com várias versões
try:
    from crewai.tools import BaseTool
except Exception:
    try:
        from crewai_tools.tools.base_tool import BaseTool
    except Exception:
        from crewai_tools import BaseTool

from pydantic import BaseModel, Field
from typing import Any, Dict
import os
import requests
import json

class SupabaseUpdaterArgs(BaseModel):
    id: str = Field(..., description="UUID do imóvel na tabela imoveis_leilao")
    analise_json: Dict[str, Any] = Field(
        ..., description="Resultado da análise de IA em formato dict/JSON"
    )

class SupabaseUpdater(BaseTool):
    name: str = "Supabase Updater Tool"
    description: str = "Atualiza imóveis no Supabase com resultados da análise de IA."
    args_schema: type = SupabaseUpdaterArgs

    def _run(self, id: str, analise_json: Dict[str, Any]) -> str:
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            if not supabase_url or not service_key:
                return "❌ Variáveis SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não configuradas."

            url = f"{supabase_url}/rest/v1/imoveis_leilao?id=eq.{id}"
            headers = {
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            }

            payload = {
                "analise_status": "concluida",
                "score_geral": analise_json.get("recomendacao"),
                "roi_percentual": analise_json.get("desconto_pct"),
                "justificativa_ia": analise_json.get("racional"),
                "updated_at": "now()",
            }

            resp = requests.patch(url, headers=headers, json=payload, timeout=30)

            if resp.status_code in (200, 204):
                try:
                    body = resp.json() if resp.content else None
                except Exception:
                    body = None
                if body == []:
                    return f"⚠️ Nenhum imóvel encontrado para ID {id}."
                return f"✅ Atualizado com sucesso (ID: {id})."
            else:
                return f"⚠️ Erro ({resp.status_code}): {resp.text}"

        except Exception as e:
            return f"❌ Erro ao atualizar Supabase: {e}"

