#!/usr/bin/env python3
"""
Autonomous Profile & Visibility Engine for Tiago Torres Stanis (@TiagoTStanis)
Runs autonomously on GitHub Actions or locally to keep the profile fresh,
dynamic, and highly visible.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import subprocess
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

USERNAME = "TiagoTStanis"
README_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")

ENGINEERING_INSIGHTS = [
    {
        "topic": "Arquitetura & Sistemas Concorrentes",
        "insight": "Manter limites claros entre I/O assíncrono e computação intensiva previne saturação do event loop. Em terminais e agentes, buffers com backpressure evitam overflow de memória."
    },
    {
        "topic": "Segurança & Criptografia em Trânsito",
        "insight": "Chaves privadas e credenciais nunca devem transitar pelo estado central da aplicação. Assinaturas GPG e verificação de hashes SHA-256 garantem integridade na distribuição de binários."
    },
    {
        "topic": "Clean Code & Idempotência de APIs",
        "insight": "Endpoints críticos devem suportar chaves de idempotência para suportar reconexões transparentes e retries exponenciais sem duplicação de dados."
    },
    {
        "topic": "Reserva Temporária de Recursos",
        "insight": "Em sistemas de reservas e pedidos, a expiração sob demanda (lazy evaluation) reduz overhead de daemons contínuos, garantindo liberação imediata ao consultar o item."
    },
    {
        "topic": "Sistemas Multi-Protocolo (SSH, RDP, VNC)",
        "insight": "Túneis dinâmicos SOCKS5 aliados a encaminhamento de agentes SSH fornecem pontes seguras para redes corporativas sem expor credenciais na camada intermediária."
    },
    {
        "topic": "Agentes Autônomos & Observabilidade",
        "insight": "Agentes de produção necessitam de loops orientados a feedback contínuo, limites de retries bem definidos e trilhas de auditoria para garantir reprodutibilidade sem supervisão manual."
    },
    {
        "topic": "Otimização de Bancos & Índices",
        "insight": "Consultas textuais insensíveis a acentos e ordenações compostas demandam índices parciais e trigramas no PostgreSQL para evitar full table scans em catálogos volumosos."
    }
]

def fetch_github_data():
    headers = {
        "User-Agent": f"Agent-{USERNAME}-Visibility-Bot",
        "Accept": "application/vnd.github.v3+json"
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    user_url = f"https://api.github.com/users/{USERNAME}"
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"

    user_data = {}
    repos_data = []

    try:
        req = urllib.request.Request(user_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            user_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[!] Warning: Could not fetch user data: {e}", file=sys.stderr)

    try:
        req = urllib.request.Request(repos_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            repos_data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[!] Warning: Could not fetch repos data: {e}", file=sys.stderr)

    return user_data, repos_data

def get_daily_insight():
    # Deterministic rotation based on day of the year
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    return ENGINEERING_INSIGHTS[day_of_year % len(ENGINEERING_INSIGHTS)]

def generate_dynamic_block(user_data, repos):
    now_utc = datetime.now(timezone.utc).strftime("%d/%m/%Y às %H:%M UTC")
    public_repos_count = user_data.get("public_repos", len(repos))
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    
    insight = get_daily_insight()

    # Find top recent repos
    filtered_repos = [r for r in repos if not r.get("fork") and r.get("name") != USERNAME]
    
    block = f"""<!-- AUTONOMOUS-AGENT:START -->
<div align="center">
  <table>
    <tr>
      <td align="center">
        <b>🤖 Agente Autônomo de Visibilidade & Engenharia</b><br>
        <i>Status: Operacional • Sincronização 24/7 sem supervisão</i>
      </td>
    </tr>
    <tr>
      <td>
        <p><b>⏱️ Última Atualização do Hub:</b> <code>{now_utc}</code></p>
        <p><b>📊 Métricas Rastreadas em Tempo Real:</b></p>
        <ul>
          <li><b>Repositórios Públicos Monitorados:</b> {public_repos_count}</li>
          <li><b>Engenharia Ativa:</b> Full Stack, Sistemas Distribuídos, Automação & IA</li>
          <li><b>Ambientes em Produção:</b> Web, Desktop (Windows x64), Nuvem</li>
        </ul>
        <hr>
        <p><b>💡 Pílula Diária de Engenharia & Arquitetura ({insight['topic']}):</b></p>
        <blockquote>
          "{insight['insight']}"
        </blockquote>
      </td>
    </tr>
  </table>
</div>
<!-- AUTONOMOUS-AGENT:END -->"""
    return block

def update_readme():
    if not os.path.exists(README_PATH):
        print(f"[!] Erro: README.md não encontrado em {README_PATH}", file=sys.stderr)
        return False

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start_tag = "<!-- AUTONOMOUS-AGENT:START -->"
    end_tag = "<!-- AUTONOMOUS-AGENT:END -->"

    user_data, repos = fetch_github_data()
    dynamic_block = generate_dynamic_block(user_data, repos)

    if start_tag in content and end_tag in content:
        prefix = content.split(start_tag)[0]
        suffix = content.split(end_tag)[1]
        new_content = prefix + dynamic_block + suffix
    else:
        # Append at the end if tags don't exist yet
        new_content = content + "\n\n" + dynamic_block + "\n"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[OK] README.md atualizado com sucesso em {datetime.now(timezone.utc).isoformat()}")
    return True

if __name__ == "__main__":
    update_readme()
