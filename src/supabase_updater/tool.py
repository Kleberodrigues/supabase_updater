# imports compatíveis com diferentes versões
try:
    # CrewAI 1.x (recomendado)
    from crewai.tools import BaseTool
except Exception:
    try:
        # Algumas versões do crewai-tools
        from crewai_tools.tools.base_tool import BaseTool
    except Exception:
        # Outras versões antigas do crewai-tools
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
    name = "Supabase Updater Tool"
    description = "Atualiza imóveis no Supabase com resultados da análise de IA."
    args_schema = SupabaseUpdaterArgs  # <- importante!

    # Use com argumentos: id (str) e analise_json (dict)
    def _run(self, id: str, analise_json: Dict[str, Any]) -> str:
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            if not supabase_url or not service_key:
                return "❌ Variáveis SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não configuradas."

            # Endpoint REST do Supabase para atualizar por id
            url = f"{supabase_url}/rest/v1/imoveis_leilao?id=eq.{id}"

            headers = {
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            }

            # Monta o payload conforme o seu esquema
            payload = {
                "analise_status": "concluida",
                "score_geral": analise_json.get("recomendacao"),
                "roi_percentual": analise_json.get("desconto_pct"),
                "justificativa_ia": analise_json.get("racional"),
                "updated_at": "now()",
                # Campos adicionais, se existirem:
                # "nota_localizacao": analise_json.get("nota_localizacao"),
                # "risco_legal": analise_json.get("risco_legal"),
            }

            # Envia PATCH para o Supabase
            resp = requests.patch(url, headers=headers, json=payload, timeout=30)

            # Trata a resposta
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
