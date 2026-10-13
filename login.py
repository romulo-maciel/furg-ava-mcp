"""Login único: pede usuário/senha, obtém o token do AVA e salva em ~/.config/furg-ava-mcp/token."""
import getpass, os
import httpx
from server import BASE, TOKEN_FILE

user = input("Usuário AVA: ").strip()
pw = getpass.getpass("Senha (oculta): ")
data = httpx.post(f"{BASE}/login/token.php", data={
    "username": user, "password": pw, "service": "moodle_mobile_app"}, timeout=30).json()
if "token" not in data:
    raise SystemExit(f"Falhou: {data.get('error', data)}")
TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
TOKEN_FILE.write_text(data["token"])
TOKEN_FILE.chmod(0o600)
print("Token salvo em", TOKEN_FILE)
