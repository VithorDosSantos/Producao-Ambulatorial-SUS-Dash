"""
Script para atualizar (refresh) as views materializadas
Execute este script quando novos dados forem inseridos no banco
"""
import subprocess
import sys

if __name__ == "__main__":
    print("🔄 Atualizando views materializadas...\n")
    result = subprocess.run([sys.executable, "create_views.py", "--refresh"])
    sys.exit(result.returncode)
