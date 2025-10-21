from crewai.tools import BaseTool


class SupabaseUpdater(BaseTool):
    name: str = "Name of my tool"
    description: str = "What this tool does. It's vital for effective utilization."

    def _run(self, argument: str) -> str:
        # Your tool's logic here
        return "Tool's result"
from crewai_tools import BaseTool
import requests
import os
from typing import Dict, Any


class SupabaseUpdater(BaseTool):
    """
    Atualiza a tabela public.imoveis_leilao no Supabase com os resultados da análise.
    Argumentos esperados no _run:
      - id (str): UUID do imóvel na tabela
      - analise_json (dict): dicionário com campos da análise (ex.: recomendacao, desconto_pct, racional)
    """

    name = "Supabase Updater Tool"
    description = (
        "Atualiza imóveis no Supabase com os resultados da análise de IA. "
        "Use com argumentos: id (str) e analise_json (dict)."
    )

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

            # Monte o payload a partir do seu esquema
            payload = {
                "analise_status": "concluida",
                "score_geral": analise_json.get("recomendacao"),
                "roi_percentual": analise_json.get("desconto_pct"),
                "justificativa_ia": analise_json.get("racional"),
                # Se tiver mais campos, adicione aqui:
                # "risco_legal": analise_json.get("risco_legal"),
                # "nota_localizacao": analise_json.get("nota_localizacao"),
                # ...
            }

            resp = requests.patch(url, headers=headers, json=payload, timeout=30)

            if resp.status_code in (200, 204):
                return f"✅ Atualizado com sucesso (ID: {id})."
            else:
                return f"⚠️ Erro {resp.status_code}: {resp.text}"

        except Exception as e:
            return f"❌ Erro ao atualizar Supabase: {e}"
