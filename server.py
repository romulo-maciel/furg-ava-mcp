"""Servidor MCP para o AVA FURG (Moodle) via Web Services.

Variáveis de ambiente:
  AVA_USER, AVA_PASSWORD  credenciais (usadas só para obter o token)
  AVA_TOKEN               alternativa: token já obtido (pular user/senha)
  AVA_URL                 padrão https://ava.furg.br
"""
import json
import os
import time
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

BASE = os.environ.get("AVA_URL", "https://ava.furg.br").rstrip("/")
TOKEN_FILE = Path.home() / ".config" / "furg-ava-mcp" / "token"
mcp = FastMCP("furg-ava")
_state: dict = {}


def _token() -> str:
    if _state.get("token"):
        return _state["token"]
    tok = os.environ.get("AVA_TOKEN")
    if not tok and TOKEN_FILE.exists():
        tok = TOKEN_FILE.read_text().strip()
    if not tok:
        user, pw = os.environ.get("AVA_USER"), os.environ.get("AVA_PASSWORD")
        if not (user and pw):
            raise RuntimeError("Defina AVA_USER/AVA_PASSWORD ou AVA_TOKEN.")
        r = httpx.post(f"{BASE}/login/token.php", data={
            "username": user, "password": pw, "service": "moodle_mobile_app"}, timeout=30)
        data = r.json()
        if "token" not in data:
            raise RuntimeError(f"Login falhou: {data.get('error', data)}")
        tok = data["token"]
        TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_FILE.write_text(tok)
        TOKEN_FILE.chmod(0o600)
    _state["token"] = tok
    return tok


def call(fn: str, **params):
    data = {"wstoken": _token(), "wsfunction": fn, "moodlewsrestformat": "json"}
    for k, v in params.items():
        if isinstance(v, list):
            for i, x in enumerate(v):
                data[f"{k}[{i}]"] = x
        else:
            data[k] = v
    r = httpx.post(f"{BASE}/webservice/rest/server.php", data=data, timeout=60)
    out = r.json()
    if isinstance(out, dict) and "exception" in out:
        if out.get("errorcode") == "invalidtoken":
            _state.clear()
            TOKEN_FILE.unlink(missing_ok=True)
        raise RuntimeError(f"{out.get('errorcode')}: {out.get('message')}")
    return out


def _userid() -> int:
    if "uid" not in _state:
        _state["uid"] = call("core_webservice_get_site_info")["userid"]
    return _state["uid"]


def _ts(t):
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(t)) if t else None


def _j(o):
    return json.dumps(o, ensure_ascii=False, indent=1)


@mcp.tool()
def whoami() -> str:
    """Dados do usuário logado e do site."""
    i = call("core_webservice_get_site_info")
    return _j({k: i.get(k) for k in ("fullname", "username", "userid", "sitename", "release")})


@mcp.tool()
def list_courses() -> str:
    """Lista as disciplinas (cursos) em que o usuário está matriculado."""
    cs = call("core_enrol_get_users_courses", userid=_userid())
    return _j([{"id": c["id"], "nome": c["fullname"], "curto": c["shortname"],
                "progresso": c.get("progress"), "fim": _ts(c.get("enddate"))} for c in cs])


@mcp.tool()
def course_contents(course_id: int) -> str:
    """Seções e atividades/recursos de uma disciplina (com URLs de arquivos)."""
    out = []
    for s in call("core_course_get_contents", courseid=course_id):
        mods = []
        for m in s.get("modules", []):
            e = {"id": m["id"], "tipo": m["modname"], "nome": m["name"], "url": m.get("url")}
            if m.get("contents"):
                e["arquivos"] = [{"nome": f["filename"], "tamanho": f.get("filesize"),
                                  "url": f["fileurl"]} for f in m["contents"] if f.get("fileurl")]
            mods.append(e)
        out.append({"secao": s["name"], "itens": mods})
    return _j(out)


@mcp.tool()
def upcoming_events(days: int = 30, limit: int = 30) -> str:
    """Próximos prazos e eventos do calendário (tarefas, questionários etc.)."""
    now = int(time.time())
    r = call("core_calendar_get_action_events_by_timesort", timesortfrom=now,
             timesortto=now + days * 86400, limitnum=limit)
    return _j([{"nome": e["name"], "quando": _ts(e["timesort"]),
                "curso": (e.get("course") or {}).get("fullname"), "url": e.get("url")}
               for e in r["events"]])


@mcp.tool()
def assignments(course_id: int) -> str:
    """Tarefas de uma disciplina com prazos e descrição."""
    r = call("mod_assign_get_assignments", courseids=[course_id])
    out = []
    for c in r["courses"]:
        for a in c["assignments"]:
            out.append({"id": a["id"], "nome": a["name"], "prazo": _ts(a["duedate"]),
                        "descricao": a.get("intro")})
    return _j(out)


@mcp.tool()
def grades(course_id: int) -> str:
    """Notas do usuário em uma disciplina."""
    r = call("gradereport_user_get_grade_items", courseid=course_id, userid=_userid())
    items = r["usergrades"][0]["gradeitems"] if r.get("usergrades") else []
    return _j([{"item": g["itemname"], "nota": g.get("gradeformatted"),
                "faixa": g.get("rangeformatted")} for g in items])


@mcp.tool()
def forum_discussions(course_id: int, limit: int = 15) -> str:
    """Discussões recentes dos fóruns (avisos etc.) de uma disciplina."""
    out = []
    for f in call("mod_forum_get_forums_by_courses", courseids=[course_id]):
        d = call("mod_forum_get_forum_discussions", forumid=f["id"], perpage=limit)
        for x in d.get("discussions", []):
            out.append({"forum": f["name"], "assunto": x["name"], "autor": x.get("userfullname"),
                        "data": _ts(x.get("timemodified")), "mensagem": x.get("message")})
    return _j(out)


@mcp.tool()
def notifications(limit: int = 20) -> str:
    """Notificações recentes do AVA."""
    r = call("message_popup_get_popup_notifications", useridto=_userid(), limit=limit)
    return _j([{"assunto": n["subject"], "texto": n.get("smallmessage"),
                "lida": n["read"], "quando": _ts(n["timecreated"]), "url": n.get("contexturl")}
               for n in r["notifications"]])


@mcp.tool()
def search_courses(query: str) -> str:
    """Busca disciplinas no catálogo do AVA."""
    r = call("core_course_search_courses", criterianame="search", criteriavalue=query)
    return _j([{"id": c["id"], "nome": c["fullname"]} for c in r["courses"]])


if __name__ == "__main__":
    mcp.run()
