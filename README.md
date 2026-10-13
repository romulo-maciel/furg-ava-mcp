<div align="center">

# 🎓 furg-ava-mcp

**Conecte sua IA ao AVA da FURG.**
Pergunte "o que vence essa semana?", "o que o professor escreveu no tópico 3?" ou "baixa todas as listas de Sistemas Operacionais" direto no seu assistente.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![MCP](https://img.shields.io/badge/protocolo-MCP-8A2BE2)
![License](https://img.shields.io/badge/licen%C3%A7a-MIT-green)

</div>

---

## ✨ O que é

Um servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io) que conversa com o
[AVA FURG](https://ava.furg.br) (Moodle) pela **API oficial de Web Services** do Moodle, a mesma que o app
*Moodle Mobile* usa. Sem scraping, sem navegador.

Ele permite que a IA:

- 📅 veja **prazos, eventos, notificações e notas**;
- 📖 **leia o conteúdo dos tópicos** das disciplinas (resumos, avisos, descrições, páginas, livros, links);
- 📥 **baixe os arquivos** (PDFs, listas, slides) para uma pasta do seu computador.

Como o MCP é um padrão aberto, funciona com **Claude, Cursor, VS Code (Copilot), Gemini CLI, Codex CLI, Windsurf, Zed**
e qualquer outro cliente que rode servidores MCP locais.

## 🧰 Ferramentas

| Ferramenta | O que faz |
|---|---|
| `whoami` | Mostra o usuário logado e a versão do AVA |
| `list_courses` | Lista suas disciplinas (com `id`) |
| `course_contents` | **Visão geral** de uma disciplina: tópicos, resumo de cada um, atividades, links e arquivos |
| `read_topic` | **Lê o conteúdo** de um tópico: textos, descrições, páginas, capítulos de livros, links externos |
| `download_file` | Baixa **um** arquivo do AVA para a sua pasta de downloads |
| `download_course_files` | Baixa **todos** os arquivos de uma disciplina, organizados por tópico |
| `upcoming_events` | Próximos prazos e eventos do calendário |
| `assignments` | Tarefas de uma disciplina, com prazo e descrição |
| `grades` | Suas notas em uma disciplina |
| `forum_discussions` | Avisos e discussões recentes dos fóruns |
| `notifications` | Notificações do AVA |
| `search_courses` | Busca disciplinas no catálogo |

### 📖 Ler os tópicos: `course_contents` e `read_topic`

Cada disciplina no AVA é dividida em **tópicos** (seções numeradas: "Informações", "Semana 1", "Listas"...).

- `course_contents(course_id)` devolve **todos** os tópicos de uma vez, cada um com o texto de resumo
  (onde os professores costumam colocar nome, horário e sala), as atividades e os arquivos.
  Use para ter o panorama.
- `read_topic(course_id, topic)` lê **um** tópico em detalhe. `topic` pode ser o número (`"3"`),
  parte do nome (`"Semana 2"`, `"Listas"`) ou vazio para todos. Se o tópico não existir, a resposta
  lista os tópicos disponíveis.

O que é lido como texto:

| Tipo no AVA | O que você recebe |
|---|---|
| Resumo do tópico | Texto limpo (HTML convertido, links preservados) |
| Rótulo / descrição de atividade | Texto da descrição |
| Página (`page`) | Conteúdo da página |
| Livro (`book`) | Texto de cada capítulo, com os títulos |
| Link (`url`) | O endereço externo (`link_externo`) |
| Arquivos (`resource`, `folder`) | Nome, tamanho e URL (para baixar) |

> ⚠️ **Limites:** imagens, vídeos, SCORM e o *conteúdo dos PDFs* não viram texto aqui. Para ler um PDF,
> baixe com `download_file` / `download_course_files` e peça para a IA abrir o arquivo.
> Tarefas têm ferramenta própria (`assignments`) e fóruns também (`forum_discussions`).

### 📥 Baixar arquivos: `download_file` e `download_course_files`

```text
download_course_files(course_id=24950)                      # tudo da disciplina
download_course_files(course_id=24950, only="Lista")        # só o que tem "Lista" no nome do arquivo ou do tópico
download_course_files(course_id=24950, subdir="SO")         # salva na pasta SO
download_file(url="<url de course_contents>", subdir="SO")  # um arquivo só
```

- **Onde salva:** na pasta definida por `AVA_DOWNLOAD_DIR` (padrão `~/FURG`), em
  `<pasta>/<subdir ou nome da disciplina>/<tópico>/<arquivo>`. Use `subdir` para cair numa pasta que
  você já tem (ex.: `subdir="PDS-I"`).
- **Não baixa duas vezes:** arquivos que já existem com o mesmo tamanho são pulados
  (`overwrite=True` força baixar de novo). A resposta informa baixados, pulados e erros.
- **Limite:** 300 MB por arquivo (`AVA_MAX_MB`).
- **Só arquivos do AVA:** `download_file` recusa URLs de outros sites, e nenhum caminho consegue
  escapar da pasta de downloads (`../` é neutralizado).

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
- *"Leia o tópico de introdução de Sistemas Operacionais e me resuma."*
- *"Baixe todas as listas de exercícios de Sistemas Operacionais na pasta SO."*
- *"Qual o cronograma e a sala da disciplina de Redes?"*
- *"Resuma os avisos recentes do fórum de Compiladores."*
- *"Quais são minhas notas em Compiladores?"*

## ⚙️ Configuração (variáveis de ambiente)

Todas opcionais. Em clientes MCP, vão no bloco `env` do servidor.

| Variável | Padrão | Para quê |
|---|---|---|
| `AVA_DOWNLOAD_DIR` | `~/FURG` | Pasta onde os downloads são salvos |
| `AVA_MAX_MB` | `300` | Tamanho máximo por arquivo baixado |
| `AVA_URL` | `https://ava.furg.br` | Endereço do Moodle (para usar outro) |
| `AVA_TOKEN` | – | Token já pronto (pula o login) |
| `AVA_USER` / `AVA_PASSWORD` | – | Login automático (veja abaixo) |

Exemplo, salvando downloads em outra pasta:

```json
{
  "mcpServers": {
    "furg-ava": {
      "command": "python",
      "args": ["/caminho/para/furg-ava-mcp/server.py"],
      "env": { "AVA_DOWNLOAD_DIR": "/home/voce/faculdade" }
    }
  }
}
```

## 🔑 Autenticação

O servidor procura o token nesta ordem:

1. variável `AVA_TOKEN`
2. arquivo `~/.config/furg-ava-mcp/token` (criado pelo `login.py`)
3. variáveis `AVA_USER` + `AVA_PASSWORD` (faz login sozinho e salva o token)

> 💡 Prefira o `login.py`. Evita deixar a senha em arquivos de configuração.

## 🔒 Segurança e privacidade

- Tudo roda **na sua máquina**. Não existe servidor intermediário.
- Seu token dá acesso à sua conta. **Nunca compartilhe** o arquivo `token` nem o publique.
- O token **não aparece nos logs** nem nas URLs devolvidas pelas ferramentas. Ele só é anexado
  na hora de baixar, e **apenas** para o host do AVA.
- Os downloads ficam presos à pasta de downloads configurada.
- Para revogar o acesso, troque a senha do AVA. O servidor apaga o token inválido e pede login de novo.
- As respostas das ferramentas (textos de tópicos, notas, avisos) são enviadas ao modelo de IA que você usa.
  Considere isso ao perguntar sobre dados sensíveis.

## 🛠️ Problemas comuns

| Sintoma | Solução |
|---|---|
| `Login falhou: Nome de usuário ou senha inválidos` | Confira matrícula e senha. Se você entra no AVA por SSO, tente a senha do AVA, não a do gov.br |
| `invalidtoken` | Token expirou. Rode `python login.py` de novo |
| Ferramenta retorna `accessexception` | A FURG pode ter desativado essa função da API. Abra uma issue |
| `read_topic` volta sem texto | O conteúdo do tópico é imagem, vídeo ou PDF. Baixe o arquivo e peça para a IA ler |
| Download: `HTTP 403/404` | O arquivo pode ter sido removido ou exige permissão. Confira no AVA |
| Respostas lentas | O AVA às vezes demora (~20 s por chamada). Baixar disciplinas grandes leva tempo |
| Cliente não mostra o servidor | Use caminhos absolutos e reinicie o cliente |
| Ferramentas novas não aparecem | Reinicie o cliente depois de `git pull` |

## 🤝 Contribuindo

PRs e issues são bem-vindos. Ideias: envio de tarefas, ler texto de PDFs, modo HTTP para clientes remotos.

## ⚠️ Aviso

Projeto independente e não oficial, sem vínculo com a FURG. Use por sua conta e risco, respeitando os termos de uso do AVA.

## 📄 Licença

[MIT](LICENSE)
