"""Testes do gerador ``atividades_adaptaveis.py``.

Verifica que o HTML gerado é válido:

- estrutura HTML (doctype, charset, viewport);
- sintaxe JavaScript de todos os blocos <script> via ``node --check``;
- JSON embutido (SYNDROMES/ACTIVITIES/SVGS) parseável;
- SVG bem formados (abrem e fecham);
- UTF-8 estrito, sem surrogate pairs;
- sem escapes inválidos de apóstrofo (\\');
- emojis e caracteres especiais preservados;
- auditoria do código-fonte (sem str()/repr()/replace para gerar JS).
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


# Garante que a raiz do projeto esteja no sys.path independentemente
# de como o pytest for invocado.
PROJETO = Path(__file__).resolve().parents[1]
if str(PROJETO) not in sys.path:
    sys.path.insert(0, str(PROJETO))

import atividades_adaptaveis as gerador  # noqa: E402


SURROGATE_RE = re.compile(r"[\ud800-\udfff]")


@pytest.fixture(scope="module")
def html_gerado():
    """Chama build_html() + _fix_surrogates() (mesmo fluxo do main())."""
    return gerador._fix_surrogates(gerador.build_html())


def _extrai_json_var(html: str, var: str, fim: str) -> dict:
    """Extrai o literal JSON de ``var NAME = ...;`` e o faz parseável."""
    inicio = html.index(f"var {var} = ") + len(f"var {var} = ")
    fim_idx = html.index(fim, inicio)
    literal = html[inicio:fim_idx].strip()
    # O gerador protege "</" como "<\/" (válido em JSON); restaura p/ JSON.parse
    return json.loads(literal.replace("<\\/", "</"))


# ---------------------------------------------------------------------------
# 1. Estrutura do HTML
# ---------------------------------------------------------------------------
def test_gera_html_com_estrutura_valida(html_gerado):
    assert html_gerado.startswith("<!DOCTYPE html>")
    assert "<html" in html_gerado
    assert "</html>" in html_gerado
    assert 'charset="UTF-8"' in html_gerado
    assert 'name="viewport"' in html_gerado
    assert "<title>" in html_gerado and "</title>" in html_gerado


def test_html_nao_vazio_e_completo(html_gerado):
    assert len(html_gerado) > 10000
    assert html_gerado.count("<script>") >= 1
    assert html_gerado.count("</script>") == html_gerado.count("<script>")


# ---------------------------------------------------------------------------
# 2. UTF-8, surrogates e escapes
# ---------------------------------------------------------------------------
def test_utf8_estrito(html_gerado):
    # Dispara UnicodeEncodeError se houver surrogates ou code points inválidos
    html_gerado.encode("utf-8")


def test_sem_surrogate_pairs(html_gerado):
    assert SURROGATE_RE.search(html_gerado) is None


def test_sem_apostrofo_escapado_invalido(html_gerado):
    # Antes da correção, str().replace("'", "\\'") gerava dezenas de \'
    assert "\\'" not in html_gerado


def test_emojis_preservados(html_gerado):
    assert "🧩" in html_gerado  # ícone TEA (surrogate pair convertido)
    assert "📝" in html_gerado  # ícone do box de instruções
    assert "🖐️" in html_gerado


def test_caracteres_especiais_preservados(html_gerado):
    # Título e textos com acentuação/cedilha devem sair decodificados
    assert "Educação Inclusiva" in html_gerado
    assert "Atividades Adaptáveis" in html_gerado
    assert "Selecione a condição" in html_gerado


# ---------------------------------------------------------------------------
# 3. JSON embutido
# ---------------------------------------------------------------------------
def test_json_syndromes_valido(html_gerado):
    dados = _extrai_json_var(html_gerado, "SYNDROMES", ";\nvar ACTIVITIES")
    assert len(dados) == 11
    ids = {s["id"] for s in dados}
    assert {"tea", "down", "xfragil", "turner"} <= ids
    for s in dados:
        assert s["name"] and s["icon"] and s["colors"]
        assert len(s["levels"]) == 3
        assert len(s["adaptations"]) >= 1


def test_json_activities_valido(html_gerado):
    dados = _extrai_json_var(html_gerado, "ACTIVITIES", ";\nvar SVGS")
    assert len(dados) == 7
    for a in dados:
        assert a["name"] and a["desc"]
        assert len(a["steps"]) >= 1
        assert len(a["cards"]) >= 1


def test_json_svgs_valido(html_gerado):
    dados = _extrai_json_var(html_gerado, "SVGS", ";\n\nvar currentSyndrome")
    assert len(dados) >= 20
    for k, v in dados.items():
        assert isinstance(v, str) and v.strip().startswith("<svg")
        assert v.strip().endswith("</svg>")


def test_svgs_referenciados_existem(html_gerado):
    svgs = _extrai_json_var(html_gerado, "SVGS", ";\n\nvar currentSyndrome")
    atvs = _extrai_json_var(html_gerado, "ACTIVITIES", ";\nvar SVGS")
    faltando = [
        card["svg"] for atv in atvs for card in atv["cards"] if card["svg"] not in svgs
    ]
    assert not faltando, f"SVGs referenciados mas inexistentes: {faltando}"


# ---------------------------------------------------------------------------
# 4. Sintaxe JavaScript (node --check)
# ---------------------------------------------------------------------------
def test_sintaxe_js_blocos(html_gerado):
    if shutil.which("node") is None:
        pytest.skip("node não instalado")
    blocos = re.findall(r"<script[^>]*>(.*?)</script>", html_gerado, re.S)
    assert blocos, "nenhum bloco <script> inline encontrado"
    for i, js in enumerate(blocos, 1):
        if not js.strip():
            continue
        r = subprocess.run(
            ["node", "--check", "-"],
            input=js,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"bloco {i}: SyntaxError\n{r.stderr[:500]}"


# ---------------------------------------------------------------------------
# 5. Auditoria do código-fonte (regressão)
# ---------------------------------------------------------------------------
def test_fonte_nao_usa_str_para_gerar_js():
    fonte = (PROJETO / "atividades_adaptaveis.py").read_text(encoding="utf-8")
    # Nenhuma serialização via str()/repr() com escape manual de aspas
    assert '.replace("\'", "\\\\\'")' not in fonte
    assert "str(syndromes)" not in fonte
    assert "str(activities)" not in fonte
    assert "str(svgs)" not in fonte
    # A serialização correta existe
    assert "json.dumps" in fonte
    assert "ensure_ascii=False" in fonte


def test_fonte_nao_usa_surrogatepass():
    fonte = (PROJETO / "atividades_adaptaveis.py").read_text(encoding="utf-8")
    # O truque frágil encode/decode com surrogatepass foi removido
    assert "surrogatepass" not in fonte


def test_js_json_produz_json_valido():
    dado = {"nome": "João", "emoji": "🧩", "html": "</script><!--x--><b>x</b>"}
    literal = gerador.js_json(dado)
    # Válido para o interpretador JSON (com as proteções restauradas)
    assert (
        json.loads(literal.replace("<\\/", "</").replace("<\\u0021--", "<!--")) == dado
    )
    # As proteções anti-injeção estão presentes
    assert "</script>" not in literal
    assert "<!--" not in literal
    assert "<\\/script>" in literal
    assert "<\\u0021--" in literal


def test_fix_surrogates_combina_pares():
    texto = "\ud83d\udcdd e \ud83d\udfe3"  # 📝 e 🟣 como pares isolados no teste
    saida = gerador._fix_surrogates(texto)
    assert "📝" in saida
    assert "🟣" in saida
    assert SURROGATE_RE.search(saida) is None


def test_fix_surrogates_trata_isolado():
    texto = "a\ud83db"  # surrogate alto isolado
    saida = gerador._fix_surrogates(texto)
    assert "\ufffd" in saida
    assert SURROGATE_RE.search(saida) is None


def test_main_gera_arquivo_valido(tmp_path, monkeypatch):
    """End-to-end: main() escreve o arquivo com UTF-8 estrito."""
    monkeypatch.chdir(tmp_path)
    gerador.main()
    destino = tmp_path / "atividades_adaptaveis.html"
    assert destino.exists()
    conteudo = destino.read_text(encoding="utf-8")
    conteudo.encode("utf-8")  # UTF-8 estrito, sem surrogates
    assert SURROGATE_RE.search(conteudo) is None
    assert "<!DOCTYPE html>" in conteudo
    assert 'var SYNDROMES = [{"id":' in conteudo
