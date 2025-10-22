# test_supabase_updater.py

import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

try:
    from src.supabase_updater.tool import SupabaseUpdater, SupabaseUpdaterArgs
except Exception as e:
    print("❌ Erro ao importar a ferramenta:", e)
    exit(1)

# Preencha com um ID real existente na sua tabela do Supabase
TEST_ID = "substitua_por_um_id_real"

analise_teste = {
    "recomendacao": 8.9,
    "desconto_pct": 23.7,
    "racional": "Boa margem de lucro e localização com alta valorização."
}

# Checa se variáveis estão definidas
if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
    print("❌ SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não estão definidos.")
    exit(1)

# Instancia a ferramenta e executa
tool = SupabaseUpdater()
args = SupabaseUpdaterArgs(id=TEST_ID, analise_json=analise_teste)

print("⏳ Enviando atualização para Supabase...")
resposta = tool.run(**args.dict())
print("📦 Resultado:", resposta)
