#!/usr/bin/env python3
"""Adiciona links de ícone no <head> dos HTMLs do portal: favicon-emoji + apple-touch-icon.

Para cada projeto do portal o script garante dois links no <head>:

  - favicon-emoji (data-URI SVG, sem arquivo extra):
      <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg'
      viewBox='0 0 100 100'><text y='.9em' font-size='90'>EMOJI</text></svg>">

  - apple-touch-icon (aponta para o PNG 180x180 gerado por gerar_favicon.py):
      <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">

Assim a aba do navegador mostra o emoji do projeto e o atalho de tela inicial
no iPhone/iPad usa o capelo em alta resolução.

Uso:
    python3 scripts/adicionar_favicons.py                 # aplica em todos
    python3 scripts/adicionar_favicons.py --check         # só reporta (não edita)
    python3 scripts/adicionar_favicons.py --only quiz     # só projetos com 'quiz'

Idempotente: arquivos que já têm apple-touch-icon são pulados. O script edita os
arquivos reais em OpenManus/ — os symlinks do portal apontam para eles.
"""

import argparse
import glob
import os
import re
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /OpenManus
HTML_DIR = os.path.join(ROOT, "*.html")

# Mapa projeto -> emoji (extraído do index.html do portal).
EMOJIS = {
    "atividades_adaptaveis.html": "🧩",
    "atividades_interativas.html": "📄",
    "corretor_gabaritos_pro.html": "✅",
    "debate_argumentativo.html": "🗣️",
    "diariopro.html": "🏫",
    "escola_organizada.html": "🏫",
    "gestao_escolar.html": "🏫",
    "guia_notebooklm_claude.html": "📄",
    "historiagames.html": "📜",
    "jogo_bingo_reforma.html": "🎱",
    "jogo_domino_reforma.html": "🎮",
    "jogo_memoria_brasil_colonia.html": "🧠",
    "jogo_memoria_holandesas_digital.html": "🧠",
    "jogo_memoria_holandesas.html": "🧠",
    "jogo_memoria_reforma.html": "🧠",
    "jogo_perguntas_historia.html": "🎮",
    "jogos_historicos.html": "🎮",
    "labirinto_aldeia_indigena.html": "🌀",
    "minha_historia_pessoal.html": "📜",
    "omredu_corretor_gabaritos.html": "✅",
    "omredu_corretor_hibrido.html": "✅",
    "pipeline_multi_ia.html": "📄",
    "prova_adaptada_1_historia_9ano.html": "📝",
    "prova_adaptada_2_historia_9ano.html": "📝",
    "quiz_historico_en.html": "❓",
    "quiz_historico.html": "❓",
    "quiz_roma_cidade_eterna.html": "❓",
    "test_adapt.html": "🧩",
    "uno_egito_antigo.html": "🃏",
}

# Pequenos emojis de fallback caso o arquivo não esteja no mapa.
FALLBACK_EMOJI = "📘"

TITLE_RE = re.compile(r"(<title[^>]*>[^<]*</title>)", re.IGNORECASE)
APPLE_RE = re.compile(r'rel="apple-touch-icon"', re.IGNORECASE)

# Casa a tag <link rel="icon" ...> COMPLETA, incluindo o data-URI SVG que
# contém < e > internos. O fechamento do atributo href é o `"` antes do `>`
# final da tag. "[^"]*" para o href (aspas duplas fecham o atributo).
ICON_TAG_RE = re.compile(r'<link rel="icon" href="[^"]*"[^>]*>', re.IGNORECASE)

APPLE_TAG = '<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">'


def link_favicon(emoji: str) -> str:
    """Gera a tag <link rel=icon> com o emoji em data-URI SVG."""
    return (
        '<link rel="icon" href="data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' '
        f"viewBox='0 0 100 100'><text y='.9em' font-size='90'>{emoji}</text></svg>\">"
    )


def processar(arquivo: str, check_only: bool) -> str:
    """Retorna 'editado', 'ja_tem' ou 'sem_title'."""
    with open(arquivo, encoding="utf-8") as fh:
        html = fh.read()

    if APPLE_RE.search(html):
        return "ja_tem"

    m = TITLE_RE.search(html)
    if not m:
        return "sem_title"

    base = os.path.basename(arquivo)
    emoji = EMOJIS.get(base, FALLBACK_EMOJI)
    if base not in EMOJIS:
        print(
            f"  ⚠ aviso: '{base}' não está no mapa EMOJIS — usou fallback {FALLBACK_EMOJI}"
        )

    # Ponto de inserção: após a última TAG COMPLETA de ícone existente (agrupa
    # os links), ou após </title> se o arquivo ainda não tem favicon.
    # Usa a MESMA regex para decidir o ponto e se insere o emoji — assim o
    # guard e o ponto de inserção nunca divergem.
    icones = list(ICON_TAG_RE.finditer(html))
    if icones:
        insercao = icones[-1].end()
    else:
        insercao = m.end()

    # Tags a inserir no ponto escolhido.
    tags = []
    if not icones:
        tags.append(link_favicon(emoji))
    tags.append(APPLE_TAG)

    novo = html[:insercao] + "\n" + "\n".join(tags) + html[insercao:]

    if not check_only:
        with open(arquivo, "w", encoding="utf-8") as fh:
            fh.write(novo)
    return "editado"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="apenas reporta o que seria feito, sem editar",
    )
    parser.add_argument(
        "--only",
        default=None,
        help="processa apenas arquivos cujo nome contém este texto",
    )
    args = parser.parse_args()

    arquivos = sorted(glob.glob(HTML_DIR))
    if args.only:
        arquivos = [a for a in arquivos if args.only in os.path.basename(a)]

    if not arquivos:
        print("Nenhum arquivo .html encontrado em", HTML_DIR, file=sys.stderr)
        return 2

    contagem = {"editado": 0, "ja_tem": 0, "sem_title": 0}
    for a in arquivos:
        status = processar(a, args.check)
        contagem[status] = contagem.get(status, 0) + 1
        acao = "simularia" if args.check else "edita"
        print(f"  [{status:>8}] {acao} {os.path.basename(a)}")
        if status == "sem_title":
            print(
                f"  ⚠ aviso: {os.path.basename(a)} não tem <title> — insira os links manualmente"
            )

    print()
    print(
        f"Editados: {contagem['editado']} · Já tinham: {contagem['ja_tem']} · Sem <title>: {contagem['sem_title']}"
    )
    print(
        "(modo --check: nada foi alterado)" if args.check else "(arquivos atualizados)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
