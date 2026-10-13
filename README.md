<div align="center">

# 🎓 furg-ava-mcp

**Conecte sua IA ao AVA da FURG.**
Pergunte "o que vence essa semana?", "qual minha nota em Cálculo?" ou "tem aviso novo no fórum?" direto no seu assistente.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![MCP](https://img.shields.io/badge/protocolo-MCP-8A2BE2)
![License](https://img.shields.io/badge/licen%C3%A7a-MIT-green)

</div>

---

## ✨ O que é

Um servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io) que conversa com o
[AVA FURG](https://ava.furg.br) (Moodle) pela **API oficial de Web Services** do Moodle, a mesma que o app
*Moodle Mobile* usa. Sem scraping, sem navegador.

Como o MCP é um padrão aberto, funciona com **Claude, Cursor, VS Code (Copilot), Gemini CLI, Codex CLI, Windsurf, Zed**
e qualquer outro cliente que rode servidores MCP locais.

## 🧰 Ferramentas

| Ferramenta | O que faz |
|---|---|
| `whoami` | Mostra o usuário logado e a versão do AVA |
| `list_courses` | Lista suas disciplinas |
| `course_contents` | Seções, atividades e arquivos (com links) de uma disciplina |
| `upcoming_events` | Próximos prazos e eventos do calendário |
| `assignments` | Tarefas de uma disciplina, com prazo e descrição |
| `grades` | Suas notas em uma disciplina |
| `forum_discussions` | Avisos e discussões recentes dos fóruns |
| `notifications` | Notificações do AVA |
| `search_courses` | Busca disciplinas no catálogo |

## 🚀 Instalação

Você precisa de **Python 3.10+**.

```bash
git clone https://github.com/romulo-maciel/furg-ava-mcp.git
cd furg-ava-mcp
pip install -r requirements.txt
```

### 1. Faça login (uma vez só)

```bash
python login.py
```

Digite seu usuário (matrícula) e sua senha do AVA. A senha fica oculta e **não é salva**.
O script guarda apenas um *token* em `~/.config/furg-ava-mcp/token` (permissão `600`).
A senha é enviada somente para `ava.furg.br`.

### 2. Registre no seu cliente

Use o **caminho completo** do `python` e do `server.py`.

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add furg-ava -- python /caminho/para/furg-ava-mcp/server.py
```
</details>

<details>
<summary><b>Claude Desktop</b></summary>

Edite o `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "furg-ava": {
      "command": "python",
      "args": ["/caminho/para/furg-ava-mcp/server.py"]
    }
  }
}
```
</details>

<details>
<summary><b>Cursor</b></summary>

Em `~/.cursor/mcp.json` (ou `.cursor/mcp.json` no projeto):

```json
{
  "mcpServers": {
    "furg-ava": {
      "command": "python",
      "args": ["/caminho/para/furg-ava-mcp/server.py"]
    }
  }
}
```
</details>

<details>
<summary><b>VS Code (Copilot)</b></summary>

Em `.vscode/mcp.json`:

```json
{
  "servers": {
    "furg-ava": {
      "type": "stdio",
      "command": "python",
      "args": ["/caminho/para/furg-ava-mcp/server.py"]
    }
  }
}
```
</details>

<details>
<summary><b>Gemini CLI</b></summary>

Em `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "furg-ava": {
      "command": "python",
      "args": ["/caminho/para/furg-ava-mcp/server.py"]
    }
  }
}
```
</details>

<details>
<summary><b>Codex CLI</b></summary>

Em `~/.codex/config.toml`:

```toml
[mcp_servers.furg-ava]
command = "python"
args = ["/caminho/para/furg-ava-mcp/server.py"]
```
</details>

> **Windows:** use barras duplas ou invertidas escapadas no caminho (`C:\\Users\\voce\\furg-ava-mcp\\server.py`).
> **Conda/venv:** se instalou as dependências num ambiente, use o `python` desse ambiente (caminho completo).

Reinicie o cliente e pergunte algo como:

- *"Quais disciplinas estou cursando neste semestre?"*
- *"O que tenho para entregar nos próximos 7 dias?"*
- *"Resuma os avisos recentes do fórum de Redes de Computadores."*
- *"Quais são minhas notas em Compiladores?"*

## 🔑 Autenticação: outras opções

O servidor procura o token nesta ordem:

1. variável `AVA_TOKEN`
2. arquivo `~/.config/furg-ava-mcp/token` (criado pelo `login.py`)
3. variáveis `AVA_USER` + `AVA_PASSWORD` (faz login sozinho e salva o token)

Outra variável: `AVA_URL` (padrão `https://ava.furg.br`), para usar com outro Moodle.

> 💡 Prefira o `login.py`. Evita deixar a senha em arquivos de configuração.

## 🔒 Segurança e privacidade

- Tudo roda **na sua máquina**. Não existe servidor intermediário.
- Seu token dá acesso à sua conta. **Nunca compartilhe** o arquivo `token` nem o publique.
- Para revogar, troque a senha do AVA. O servidor apaga o token inválido e pede login de novo.
- As respostas das ferramentas são enviadas ao modelo de IA que você usa. Considere isso ao perguntar sobre dados sensíveis.

## 🛠️ Problemas comuns

| Sintoma | Solução |
|---|---|
| `Login falhou: Nome de usuário ou senha inválidos` | Confira matrícula e senha. Se você entra no AVA por SSO, tente a senha do AVA, não a do gov.br |
| `invalidtoken` | Token expirou. Rode `python login.py` de novo |
| Ferramenta retorna `accessexception` | A FURG pode ter desativado essa função da API. Abra uma issue |
| Cliente não mostra o servidor | Use caminhos absolutos e reinicie o cliente |

## 🤝 Contribuindo

PRs e issues são bem-vindos. Ideias: download de arquivos das disciplinas, envio de tarefas, modo HTTP para clientes remotos.

## ⚠️ Aviso

Projeto independente e não oficial, sem vínculo com a FURG. Use por sua conta e risco, respeitando os termos de uso do AVA.

## 📄 Licença

[MIT](LICENSE)
