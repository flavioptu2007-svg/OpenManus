#!/usr/bin/env python3
"""Gera os ícones do portal (capelo de formatura sobre gradiente índigo→violeta).

Produz, no diretório do portal:

  - favicon.ico           — ICO multirresolução (16 a 256px) para as abas
  - favicon.png           — PNG 64x64 (link rel=icon moderno)
  - apple-touch-icon.png  — PNG 180x180 SEM transparência (exigência do iOS:
                            cantos transparentes apareceriam pretos no atalho
                            de tela inicial; o iOS arredonda os cantos sozinho)
  - icon-192.png          — PNG 192x192 (PWA / Android)
  - icon-512.png          — PNG 512x512 (PWA / Android)
  - icon-maskable-512.png — PNG 512x512 com zona segura para o ícone adaptável
                            do Android (fundo cheio + desenho centralizado)

Uso:
    python3 scripts/gerar_favicon.py [--portal /caminho/do/portal]

Requisitos: Pillow (PIL) no venv do projeto.
"""

import argparse
import os
import sys


try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    print("ERRO: Pillow não está instalado no ambiente.", file=sys.stderr)
    sys.exit(2)

DEFAULT_PORTAL = os.environ.get("PORTAL_DIR", "/home/flavio/portal_projetos")

# Resolução do desenho base — os tamanhos finais saem por downsample LANCZOS.
ALVO = 512


def desenhar_icone(fundo_cheio: bool, escala: float = 1.0) -> Image.Image:
    """Desenha o capelo de formatura.

    fundo_cheio=True  → quadrado cheio (iOS/apple-touch e maskable).
    escala < 1        → reduz o desenho em torno do centro (zona segura do
                        ícone adaptável do Android, que corta ~20% nas bordas).
    """
    S = ALVO
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # Gradiente vertical índigo -> violeta
    grad = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    top = (79, 70, 229)  # indigo #4f46e5
    bot = (124, 58, 237)  # violet #7c3aed
    for y in range(S):
        t = y / (S - 1)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,)
        gd.line([(0, y), (S, y)], fill=c)

    # Brilho diagonal sutil (aplicado ANTES da máscara para não vazar nos cantos)
    brilho = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(brilho)
    bd.polygon([(S, 0), (S, S * 0.55), (S * 0.78, S)], fill=(255, 255, 255, 26))
    grad = Image.alpha_composite(grad, brilho)

    if fundo_cheio:
        # iOS: quadrado cheio, sem cantos transparentes.
        img.paste(grad, (0, 0))
    else:
        mask = Image.new("L", (S, S), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([8, 8, S - 8, S - 8], radius=int(S * 0.22), fill=255)
        img.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(img)

    # ---- Capelo de formatura (mortarboard) ----
    # Escala as coordenadas em torno do centro quando escala < 1 (maskable).
    def px(x: float) -> float:
        return S / 2 + (x * S - S / 2) * escala

    placa = [
        (px(0.10), px(0.34)),
        (px(0.50), px(0.16)),
        (px(0.90), px(0.34)),
        (px(0.50), px(0.52)),
    ]
    d.polygon(
        placa,
        fill=(255, 255, 255, 245),
        outline=(13, 15, 20, 90),
        width=max(2, S // 64),
    )
    d.polygon(
        [
            (px(0.22), px(0.33)),
            (px(0.50), px(0.22)),
            (px(0.62), px(0.28)),
            (px(0.34), px(0.40)),
        ],
        fill=(255, 255, 255, 120),
    )
    d.rounded_rectangle(
        [px(0.30), px(0.52), px(0.70), px(0.74)],
        radius=max(3, S // 26),
        fill=(255, 255, 255, 245),
        outline=(13, 15, 20, 90),
        width=max(2, S // 64),
    )
    d.rectangle([px(0.30), px(0.60), px(0.70), px(0.66)], fill=(13, 15, 20, 60))
    d.line(
        [(px(0.90), px(0.36)), (px(0.80), px(0.70))],
        fill=(255, 255, 255, 255),
        width=max(4, S // 32),
    )
    d.ellipse(
        [px(0.74), px(0.66), px(0.86), px(0.78)],
        fill=(255, 255, 255, 255),
        outline=(13, 15, 20, 90),
        width=max(2, S // 64),
    )

    return img.filter(ImageFilter.SMOOTH_MORE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portal", default=DEFAULT_PORTAL, help="Diretório do portal")
    args = parser.parse_args()

    if not os.path.isdir(args.portal):
        print(
            f"ERRO: diretório do portal não encontrado: {args.portal}", file=sys.stderr
        )
        return 2

    # Desenha em alta resolução para qualidade (anti-aliasing natural).
    base = desenhar_icone(fundo_cheio=False)
    base_cheio = desenhar_icone(fundo_cheio=True)
    base_maskable = desenhar_icone(fundo_cheio=True, escala=0.80)

    # favicon.ico — multirresolução
    ico = base.resize((256, 256), Image.LANCZOS)
    ico.save(
        os.path.join(args.portal, "favicon.ico"),
        format="ICO",
        sizes=[
            (16, 16),
            (24, 24),
            (32, 32),
            (48, 48),
            (64, 64),
            (128, 128),
            (256, 256),
        ],
    )

    # favicon.png — 64x64
    base.resize((64, 64), Image.LANCZOS).save(
        os.path.join(args.portal, "favicon.png"), format="PNG"
    )

    # apple-touch-icon.png — 180x180, fundo cheio, RGB sem transparência
    ati = base_cheio.resize((180, 180), Image.LANCZOS).convert("RGB")
    ati.save(os.path.join(args.portal, "apple-touch-icon.png"), format="PNG")

    # PWA: 192x192, 512x512 e maskable com zona segura
    base.resize((192, 192), Image.LANCZOS).save(
        os.path.join(args.portal, "icon-192.png"), format="PNG"
    )
    base_cheio.resize((512, 512), Image.LANCZOS).save(
        os.path.join(args.portal, "icon-512.png"), format="PNG"
    )
    base_maskable.resize((512, 512), Image.LANCZOS).convert("RGB").save(
        os.path.join(args.portal, "icon-maskable-512.png"), format="PNG"
    )

    for nome in (
        "favicon.ico",
        "favicon.png",
        "apple-touch-icon.png",
        "icon-192.png",
        "icon-512.png",
        "icon-maskable-512.png",
    ):
        caminho = os.path.join(args.portal, nome)
        print(f"  ✓ {caminho} ({os.path.getsize(caminho)} bytes)")
    print("Ícones gerados com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
