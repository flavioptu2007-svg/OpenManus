#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Planos de Aula - 7º Ano História 2026 (Prefeitura de Paracatu/MG)

Recria o formato institucional do modelo oficial (PLANO DE AULA 7º ANO HISTÓRIA 2026.docx)
- Arquivo BIMESTRAL: 4 tabelas x 30 aulas (2º bimestre reescrito com estrutura completa)
- Arquivo TRIMESTRAL: 3 tabelas x 40 aulas (padrão da rede de Paracatu)

Estratégia: clona a TABELA 1 do original (a mais completa) como template e substitui
título, conteúdos, habilidades, objetivos, cronograma, contextualização e data,
preservando 100% da formatação (brasão, fontes, larguras, checkboxes, bibliografia).

Uso:
    python3 gerar_planos_7ano.py
"""

import os
import re
import shutil
import sys
import zipfile


ORIG = "/home/flavio/Documentos/Escola/00-Inbox/PLANO DE AULA 7º ANO HISTÓRIA 2026.docx"
OUT_DIR = "/home/flavio/Documentos/Escola/00-Inbox"
OUT_BIMESTRAL = os.path.join(
    OUT_DIR, "PLANO DE AULA 7º ANO HISTÓRIA 2026 - BIMESTRAL 4x30.docx"
)
OUT_TRIMESTRAL = os.path.join(
    OUT_DIR, "PLANO DE AULA 7º ANO HISTÓRIA 2026 - TRIMESTRAL 3x40.docx"
)

DATA_2026 = "Paracatu, 02/02/2026"


# ---------------------------------------------------------------------------
# Helpers de XML (parsing top-level balanceado)
# ---------------------------------------------------------------------------


def read_document_xml(path):
    with zipfile.ZipFile(path) as z:
        return z.read("word/document.xml").decode("utf-8")


def write_document_xml(path, xml, src=ORIG):
    """Copia o zip original e substitui apenas word/document.xml (preserva mídia)."""
    shutil.copy(src, path)
    # reescreve o zip com o novo document.xml
    tmp = path + ".tmp"
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(
        tmp, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    os.replace(tmp, path)
    print(f"  -> {os.path.basename(path)}")


def top_level_slices(xml, tag):
    """Retorna lista de (start, end) dos elementos <w:tag>...</w:tag> de nível topo."""
    pattern = re.compile(rf"<w:{tag}(?:\s[^>]*)?>|</w:{tag}>")
    results = []
    depth = 0
    start = None
    for m in pattern.finditer(xml):
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0 and start is not None:
                results.append((start, m.end()))
                start = None
        else:
            if depth == 0:
                start = m.start()
            depth += 1
    return results


def replace_slices(xml, slices, replacements):
    """replacements: dict {indice_slice: novo_texto}. Mantém os demais intactos."""
    out = []
    prev = 0
    for i, (s, e) in enumerate(slices):
        out.append(xml[prev:s])
        out.append(replacements.get(i, xml[s:e]))
        prev = e
    out.append(xml[prev:])
    return "".join(out)


def cell_text(cell_xml):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", cell_xml))


def para_texts(cell_xml):
    """Lista de textos, um por parágrafo da célula."""
    out = []
    for p in re.findall(r"<w:p(?:\s[^>]*)?>.*?</w:p>|<w:p/>", cell_xml, re.S):
        out.append("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)))
    return out


def escape(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def make_p(ppr, rpr, text):
    return (
        f"<w:p><w:pPr>{ppr}</w:pPr>"
        f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'
    )


# ---------------------------------------------------------------------------
# Extração do template (Tabela 1) e dos conteúdos originais por período
# ---------------------------------------------------------------------------


def get_table_slices(xml):
    return top_level_slices(xml, "tbl")


def get_row_slices(tbl_xml):
    return top_level_slices(tbl_xml, "tr")


def get_cell_slices(row_xml):
    return top_level_slices(row_xml, "tc")


def extract_table(xml, idx):
    slices = get_table_slices(xml)
    return xml[slices[idx][0] : slices[idx][1]]


def extract_rows(tbl_xml):
    return [tbl_xml[s:e] for s, e in get_row_slices(tbl_xml)]


def extract_cells(row_xml):
    return [row_xml[s:e] for s, e in get_cell_slices(row_xml)]


def find_row_with_text(rows, needle):
    for i, r in enumerate(rows):
        if needle in cell_text(extract_cells(r)[0]):
            return i
    return None


def texts_of_row_cell(rows, row_idx, cell_idx):
    cells = extract_cells(rows[row_idx])
    if cell_idx >= len(cells):
        return []
    return para_texts(cells[cell_idx])


# ---------------------------------------------------------------------------
# Construção de períodos a partir do template
# ---------------------------------------------------------------------------


class Template:
    """Encapsula a Tabela 1 (modelo completo) e expõe os templates de formatação."""

    def __init__(self, xml):
        self.xml = xml
        self.rows = extract_rows(xml)

        # índices estruturais (validados empiricamente)
        self.idx_cab = 0
        self.idx_dados = 1
        self.idx_conteudos = 2
        self.idx_habilidades = 3
        self.idx_objetivos = 4
        self.idx_1a_semana = 5  # SEMANA 1
        self.idx_desenv = find_row_with_text(self.rows, "DESENVOLVIMENTO DA AULA")
        self.idx_context = find_row_with_text(
            self.rows, "CONTEXTUALIZAÇÃO / PROBLEMATIZAÇÃO"
        )
        self.idx_acao = find_row_with_text(self.rows, "AÇÃO PROPOSITIVA")
        self.idx_sist = find_row_with_text(self.rows, "SISTEMATIZAÇÃO")
        self.idx_metod = find_row_with_text(self.rows, "METODOLOGIA DE ENSINO")
        self.idx_biblio = find_row_with_text(self.rows, "BIBLIOGRAFIA")
        # última linha (data) = última com texto de data
        self.idx_data = len(self.rows) - 1

        # --- templates de formatação ---
        # 1) Cabeçalho: título "PLANO DE AULA BIMESTRAL: 1º BIMESTRE"
        cab_cells = extract_cells(self.rows[self.idx_cab])
        title_p = None
        for p in re.findall(r"<w:p(?:\s[^>]*)?>.*?</w:p>", cab_cells[0], re.S):
            if "BIMESTRE" in "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)):
                title_p = p
                break
        m = re.search(r"<w:pPr>.*?</w:pPr>", title_p, re.S)
        self.PPR_TITLE = m.group(0) if m else ""
        mr = re.search(r"<w:rPr>.*?</w:rPr>", title_p, re.S)
        self.RPR_TITLE = mr.group(0) if mr else ""

        # 2) Célula de conteúdo (Conteúdos Relacionados, célula 1 da linha 2)
        cont_cells = extract_cells(self.rows[self.idx_conteudos])
        self.RPR_CONTEUDO = self._first_rpr(cont_cells[1])
        self.PPR_CONTEUDO = self._first_ppr(cont_cells[1])

        # 3) Habilidades
        hab_cells = extract_cells(self.rows[self.idx_habilidades])
        self.RPR_HAB = self._first_rpr(hab_cells[1])
        self.PPR_HAB = self._first_ppr(hab_cells[1])

        # 4) Objetivos
        obj_cells = extract_cells(self.rows[self.idx_objetivos])
        self.RPR_OBJ = self._first_rpr(obj_cells[1])
        self.PPR_OBJ = self._first_ppr(obj_cells[1])

        # 5) Linha de semana (SEMANA 1) - extrai pPr/rPr do título e da 1ª aula
        semana_row = self.rows[self.idx_1a_semana]
        semana_cells = extract_cells(semana_row)
        self.TC_WEEK = re.search(r"<w:tcPr>.*?</w:tcPr>", semana_cells[0], re.S).group(
            0
        )
        ps = re.findall(r"<w:p(?:\s[^>]*)?>.*?</w:p>", semana_cells[0], re.S)
        self.PPR_WEEK_TITLE = self._first_ppr(ps[0])
        self.RPR_WEEK_TITLE = self._first_rpr(ps[0])
        # procura parágrafo "Aula N –" para rPr de aula (em qualquer linha de semana)
        self.RPR_AULA = self.RPR_WEEK_TITLE
        self.PPR_AULA = self.PPR_WEEK_TITLE
        for row in self.rows[self.idx_1a_semana : self.idx_desenv]:
            for cell in extract_cells(row):
                for p in re.findall(r"<w:p(?:\s[^>]*)?>.*?</w:p>", cell, re.S):
                    t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
                    if t.startswith("Aula "):
                        self.RPR_AULA = self._first_rpr(p)
                        self.PPR_AULA = self._first_ppr(p)
                        break
                if self.RPR_AULA != self.RPR_WEEK_TITLE:
                    break
            if self.RPR_AULA != self.RPR_WEEK_TITLE:
                break

        # 6) Contextualização: mantém o 1º parágrafo (título) e usa rPr dos itens
        ctx_cells = extract_cells(self.rows[self.idx_context])
        ctx_ps = re.findall(r"<w:p(?:\s[^>]*)?>.*?</w:p>", ctx_cells[0], re.S)
        self.CTX_TITLE = ctx_ps[0]
        self.PPR_CTX_ITEM = self._first_ppr(ctx_ps[1]) if len(ctx_ps) > 1 else ""
        self.RPR_CTX_ITEM = self._first_rpr(ctx_ps[1]) if len(ctx_ps) > 1 else ""

        # 7) Ação propositiva: guarda o bloco completo (título + texto padrão)
        acao_cells = extract_cells(self.rows[self.idx_acao])
        self.ACAO_XML = acao_cells[0]

    @staticmethod
    def _first_ppr(block):
        m = re.search(r"<w:pPr>.*?</w:pPr>", block, re.S)
        return m.group(0) if m else ""

    @staticmethod
    def _first_rpr(block):
        m = re.search(r"<w:rPr>.*?</w:rPr>", block, re.S)
        return m.group(0) if m else ""

    # ---------------------------------------------------------------
    def build(
        self,
        titulo,
        conteudos,
        habilidades,
        objetivos,
        semanas,
        contextualizacao,
        acao_xml=None,
        data=DATA_2026,
    ):
        """Gera uma tabela completa a partir do template."""
        xml = self.xml

        # --- 1) Título do cabeçalho ---
        novo_titulo = (
            self.PPR_TITLE
            + f'<w:r><w:rPr>{self.RPR_TITLE}</w:rPr><w:t xml:space="preserve">{escape(titulo)}</w:t></w:r>'
        )
        novo_p = f"<w:p>{novo_titulo}</w:p>"
        row_slices = get_row_slices(xml)
        cab_0 = row_slices[self.idx_cab]
        cab_xml = xml[cab_0[0] : cab_0[1]]

        # substitui o parágrafo do título dentro da 1ª célula do cabeçalho
        def repl_title(m):
            return novo_p

        cab_novo = re.sub(
            r"<w:p(?:\s[^>]*)?>.*?PLANO DE AULA.*?</w:p>",
            repl_title,
            cab_xml,
            count=1,
            flags=re.S,
        )
        xml = xml[: cab_0[0]] + cab_novo + xml[cab_0[1] :]

        # --- 2) Conteúdos / Habilidades / Objetivos ---
        row_slices = get_row_slices(xml)
        # Conteúdos
        i = self.idx_conteudos
        rs = row_slices[i]
        row_xml = xml[rs[0] : rs[1]]
        cells = extract_cells(row_xml)
        nova_cel = self._cell_with_paras(
            cells[0], conteudos, self.PPR_CONTEUDO, self.RPR_CONTEUDO
        )
        row_novo = row_xml.replace(cells[1], nova_cel)
        xml = xml[: rs[0]] + row_novo + xml[rs[1] :]

        # Habilidades
        row_slices = get_row_slices(xml)
        i = self.idx_habilidades
        rs = row_slices[i]
        row_xml = xml[rs[0] : rs[1]]
        cells = extract_cells(row_xml)
        nova_cel = self._cell_with_paras(
            cells[0], habilidades, self.PPR_HAB, self.RPR_HAB
        )
        row_novo = row_xml.replace(cells[1], nova_cel)
        xml = xml[: rs[0]] + row_novo + xml[rs[1] :]

        # Objetivos
        row_slices = get_row_slices(xml)
        i = self.idx_objetivos
        rs = row_slices[i]
        row_xml = xml[rs[0] : rs[1]]
        cells = extract_cells(row_xml)
        nova_cel = self._cell_with_paras(
            cells[0], objetivos, self.PPR_OBJ, self.RPR_OBJ
        )
        row_novo = row_xml.replace(cells[1], nova_cel)
        xml = xml[: rs[0]] + row_novo + xml[rs[1] :]

        # --- 3) Cronograma: substitui as linhas de semana (entre objetivos e desenvolvimento) ---
        row_slices = get_row_slices(xml)
        start = self.idx_1a_semana
        end = self.idx_desenv
        # remove as linhas originais de semana
        head = xml[: row_slices[start][0]]
        tail = xml[row_slices[end][0] :]
        # gera novas linhas de semana
        novas = "".join(self._make_week_row(sw) for sw in semanas)
        xml = head + novas + tail

        # reindexa as linhas posteriores (LOCAL — o nº de semanas mudou em relação
        # ao template; nunca mutar self.*, pois build() é chamado várias vezes)
        rows_now = extract_rows(xml)
        find_row_with_text(rows_now, "DESENVOLVIMENTO DA AULA")
        idx_context = find_row_with_text(rows_now, "CONTEXTUALIZAÇÃO / PROBLEMATIZAÇÃO")
        idx_acao = find_row_with_text(rows_now, "AÇÃO PROPOSITIVA")
        idx_data = len(rows_now) - 1

        # --- 4) Contextualização ---
        row_slices = get_row_slices(xml)
        i = idx_context
        rs = row_slices[i]
        row_xml = xml[rs[0] : rs[1]]
        cells = extract_cells(row_xml)
        paras = [self.CTX_TITLE] + [
            make_p(self.PPR_CTX_ITEM, self.RPR_CTX_ITEM, t) for t in contextualizacao
        ]
        nova_cel = f"<w:tc>{self.TC_WEEK}{''.join(paras)}</w:tc>"
        row_novo = row_xml.replace(cells[0], nova_cel)
        xml = xml[: rs[0]] + row_novo + xml[rs[1] :]

        # --- 5) Ação propositiva (substitui os itens, mantém o título) ---
        if acao_xml:
            row_slices = get_row_slices(xml)
            i = idx_acao
            rs = row_slices[i]
            row_xml = xml[rs[0] : rs[1]]
            cells = extract_cells(row_xml)
            row_novo = row_xml.replace(cells[0], acao_xml)
            xml = xml[: rs[0]] + row_novo + xml[rs[1] :]

        # --- 6) Data: substitui SOMENTE o parágrafo da data dentro da célula.
        # A célula final contém BIBLIOGRAFIA + tabela aninhada com a data — nunca
        # reconstruir a célula inteira (descartaria a bibliografia).
        row_slices = get_row_slices(xml)
        i = idx_data
        rs = row_slices[i]
        row_xml = xml[rs[0] : rs[1]]
        cells = extract_cells(row_xml)
        # localiza o parágrafo (em qualquer profundidade) que contém "Paracatu"
        p_orig = None
        for p in re.findall(r"<w:p(?:\s[^>]*)?>.*?</w:p>", cells[0], re.S):
            if "Paracatu" in "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)):
                p_orig = p
                break
        if p_orig:
            ppr = re.search(r"<w:pPr>.*?</w:pPr>", p_orig, re.S)
            rpr = re.search(r"<w:rPr>.*?</w:rPr>", p_orig, re.S)
            ppr = ppr.group(0) if ppr else ""
            rpr = rpr.group(0) if rpr else ""
            novo_p = make_p(ppr, rpr, data)
            row_novo = row_xml.replace(p_orig, novo_p, 1)
        else:
            # fallback: célula sem "Paracatu" — acrescenta a data no fim, preservando o tcPr
            tcpr = re.search(r"<w:tcPr>.*?</w:tcPr>", cells[0], re.S)
            tcpr = tcpr.group(0) if tcpr else ""
            nova_cel = f"<w:tc>{tcpr}{make_p(self.PPR_CONTEUDO, self.RPR_CONTEUDO, data)}</w:tc>"
            row_novo = row_xml.replace(cells[0], nova_cel)
        xml = xml[: rs[0]] + row_novo + xml[rs[1] :]

        return xml

    # ---------------------------------------------------------------
    def _cell_with_paras(self, template_cell, textos, ppr, rpr):
        """Constrói célula com um parágrafo por texto, usando tcPr do template."""
        tcpr = re.search(r"<w:tcPr>.*?</w:tcPr>", template_cell, re.S)
        tcpr = tcpr.group(0) if tcpr else self.TC_WEEK
        paras = "".join(make_p(ppr, rpr, t) for t in textos)
        return f"<w:tc>{tcpr}{paras}</w:tc>"

    def _make_week_row(self, sw):
        """sw: dict(titulo=..., aulas=[...], obs=...) -> <w:tr> com 1 célula."""
        paras = [make_p(self.PPR_WEEK_TITLE, self.RPR_WEEK_TITLE, sw["titulo"])]
        ppr_aula = getattr(self, "PPR_AULA", self.PPR_WEEK_TITLE)
        for a in sw["aulas"]:
            paras.append(make_p(ppr_aula, self.RPR_AULA, a))
        if sw.get("obs"):
            paras.append(make_p(self.PPR_AULA, self.RPR_AULA, sw["obs"]))
        return f"<w:tr><w:tc>{self.TC_WEEK}{''.join(paras)}</w:tc></w:tr>"


# ---------------------------------------------------------------------------
# Dados dos períodos
# ---------------------------------------------------------------------------


def build_bimestral(tpl, orig_xml, orig_tables):
    """Arquivo BIMESTRAL: 4 tabelas; 2º bimestre reescrito com 30 aulas."""
    # Conteúdos originais do 2º bimestre (tabela 2 do original)
    t2 = orig_tables[1]
    rows2 = extract_rows(t2)
    conteudos = texts_of_row_cell(rows2, 2, 1)
    habilidades = texts_of_row_cell(rows2, 3, 1)
    objetivos = texts_of_row_cell(rows2, 4, 1)

    # Cronograma 30 aulas = 10 semanas x 3 aulas (04/05 a 10/07/2026)
    semanas = [
        {
            "titulo": "SEMANA 1 – 04/05/2026 – 08/05/2026 (Avaliação Trimestral) – Renascimento urbano e comercial.",
            "aulas": [
                "Aula 1 – Aula expositiva dialogada sobre o renascimento urbano e comercial.",
                "Aula 2 – Trabalho com textos do livro didático sobre guildas e feiras medievais.",
                "Aula 3 – Atividade do livro didático sobre rotas comerciais.",
            ],
            "obs": "Observação: Feriado no dia 01/05 – Dia Mundial do Trabalho.",
        },
        {
            "titulo": "SEMANA 2 – 11/05/2026 – 15/05/2026 (Recuperação trimestral) – Cidades medievais e burguesia.",
            "aulas": [
                "Aula 4 – Correção de atividades do livro didático.",
                "Aula 5 – Debate dialogado sobre o papel das cidades e da burguesia, com conexões locais.",
                "Aula 6 – Aplicação e correção coletiva de atividades.",
            ],
        },
        {
            "titulo": "SEMANA 3 – 18/05/2026 – 22/05/2026 (Conselho de classe 20/05) – Crises da Baixa Idade Média.",
            "aulas": [
                "Aula 7 – Aula expositiva dialogada sobre a peste negra e as guerras do século XIV.",
                "Aula 8 – Aplicação de atividades do livro didático com gráficos e cronologias.",
                "Aula 9 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 4 – 25/05/2026 – 29/05/2026 – Crise do feudalismo: revoltas camponesas.",
            "aulas": [
                "Aula 10 – Aula expositiva dialogada sobre as revoltas camponesas e o declínio feudal.",
                "Aula 11 – Análise de fontes históricas (documentos e imagens do século XIV).",
                "Aula 12 – Correção das atividades e sistematização.",
            ],
        },
        {
            "titulo": "SEMANA 5 – 01/06/2026 – 05/06/2026 (Corpus Christi 04/06) – Formação dos reinos ibéricos.",
            "aulas": [
                "Aula 13 – Aula expositiva dialogada sobre Portugal e Espanha na Idade Média.",
                "Aula 14 – Aplicação de atividades do livro didático com mapas de reconquistas.",
                "Aula 15 – Correção das atividades.",
            ],
            "obs": "Observação: Feriado de Corpus Christi no dia 04/06.",
        },
        {
            "titulo": "SEMANA 6 – 08/06/2026 – 12/06/2026 – Expansão marítima europeia.",
            "aulas": [
                "Aula 16 – Aula expositiva dialogada sobre motivações e técnicas náuticas.",
                "Aula 17 – Aplicação de atividades do livro didático com rotas marítimas.",
                "Aula 18 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 7 – 15/06/2026 – 19/06/2026 – História local de Paracatu e comércio medieval.",
            "aulas": [
                "Aula 19 – Aula dialogada sobre o comércio medieval e as expedições ibéricas em Paracatu.",
                "Aula 20 – Pesquisa orientada com fontes locais (documentos coloniais e mapas).",
                "Aula 21 – Correção coletiva das atividades, com fontes locais.",
            ],
        },
        {
            "titulo": "SEMANA 8 – 22/06/2026 – 26/06/2026 – Impactos da expansão em Paracatu.",
            "aulas": [
                "Aula 22 – Aula expositiva dialogada sobre a colonização e a exploração do ouro em Paracatu.",
                "Aula 23 – Aplicação de atividades do livro didático com mapas e documentos locais.",
                "Aula 24 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 9 – 29/06/2026 – 03/07/2026 – Revisão e consolidação do bimestre.",
            "aulas": [
                "Aula 25 – Aula dialogada sobre o conteúdo, com resolução de exercícios de comparação.",
                "Aula 26 – Correção coletiva das atividades da aula anterior.",
                "Aula 27 – Atividade coletiva de revisão da semana, incluindo Paracatu.",
            ],
        },
        {
            "titulo": "SEMANA 10 – 06/07/2026 – 10/07/2026 – Preparação para as provas bimestrais.",
            "aulas": [
                "Aula 28 – Aula dialogada sobre o conteúdo, com resolução de exercícios.",
                "Aula 29 – Correção coletiva das atividades da aula anterior, com foco local.",
                "Aula 30 – Atividade coletiva de revisão da semana.",
            ],
        },
    ]

    t2_novo = tpl.build(
        titulo="PLANO DE AULA BIMESTRAL:    2º BIMESTRE",
        conteudos=conteudos,
        habilidades=habilidades,
        objetivos=objetivos,
        semanas=semanas,
        contextualizacao=[
            "Alta e Baixa Idade Média.",
            "Renascimento comercial e urbano.",
            "Crises do século XIV.",
            "Reinos ibéricos.",
            "Expansão marítima europeia.",
            "História local de Paracatu (comércio e colonização).",
        ],
    )

    slices = get_table_slices(orig_xml)
    novo_body = (
        orig_xml[: slices[0][0]]
        + orig_tables[0]
        + orig_xml[slices[0][1] : slices[1][0]]
        + t2_novo
        + orig_xml[slices[1][1] :]
    )
    return novo_body


def build_trimestral(tpl, orig_xml, orig_tables):
    """Arquivo TRIMESTRAL: 3 tabelas completas x 40 aulas."""
    t1, t2, t3, t4 = orig_tables
    r1, r2, r3, r4 = (extract_rows(t) for t in orig_tables)

    # ----- 1º TRIMESTRE: Idade Média europeia (conteúdo do 1º bimestre) -----
    conteudos_1 = texts_of_row_cell(r1, 2, 1)
    habilidades_1 = texts_of_row_cell(r1, 3, 1)
    objetivos_1 = texts_of_row_cell(r1, 4, 1)
    semanas_1 = [
        {
            "titulo": "SEMANA 1 – 04/02/2026 – 06/02/2026 (Início do ano letivo) – Apresentação e diagnóstico.",
            "aulas": [
                "Aula 1 – Acolhida e dinâmica de boas-vindas.",
                'Aula 2 – Discussão sobre "O que é Idade Média?" e introdução ao feudalismo.',
            ],
        },
        {
            "titulo": "SEMANA 2 – 09/02/2026 – 13/02/2026 (Avaliação diagnóstica) – Feudalismo na Europa.",
            "aulas": [
                "Aula 3 – Aula expositiva dialogada sobre o feudalismo e a economia agrária.",
                "Aula 4 – Análise de fontes históricas (documentos sobre suserania e vassalagem).",
                "Aula 5 – Atividade de revisão diagnóstica sobre conhecimentos prévios.",
            ],
        },
        {
            "titulo": "SEMANA 3 – 16/02/2026 – 20/02/2026 (Recesso 16/02 – Carnaval 17 e 18/02) – Feudalismo e sociedade estamental.",
            "aulas": [
                "Aula 6 – Aula expositiva dialogada sobre a sociedade estamental.",
                "Aula 7 – Aplicação de atividades do livro didático.",
                "Aula 8 – Correção coletiva das atividades revisionais.",
            ],
        },
        {
            "titulo": "SEMANA 4 – 23/02/2026 – 27/02/2026 – Igreja Católica na Idade Média.",
            "aulas": [
                "Aula 9 – Aula expositiva dialogada sobre o poder da Igreja e as cruzadas.",
                "Aula 10 – Aplicação de atividades do livro didático com imagens de catedrais.",
                "Aula 11 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 5 – 02/03/2026 – 06/03/2026 – Cultura medieval.",
            "aulas": [
                "Aula 12 – Aula expositiva dialogada sobre arte românica, gótica e literatura medieval.",
                "Aula 13 – Aplicação de atividades com iluminuras e textos literários.",
                "Aula 14 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 6 – 09/03/2026 – 13/03/2026 – Invasões bárbaras e Império Carolíngio.",
            "aulas": [
                "Aula 15 – Aula expositiva dialogada sobre as invasões bárbaras e Carlos Magno.",
                "Aula 16 – Aplicação de atividades do livro didático com mapas e cronologias.",
                "Aula 17 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 7 – 16/03/2026 – 20/03/2026 (Avaliação das aprendizagens) – O Islã na Idade Média.",
            "aulas": [
                "Aula 18 – Aula dialogada sobre a expansão islâmica e os Califados.",
                "Aula 19 – Correção coletiva das atividades da aula anterior.",
                "Aula 20 – Atividade coletiva de revisão da semana.",
            ],
        },
        {
            "titulo": "SEMANA 8 – 23/03/2026 – 27/03/2026 – Comércio e cultura islâmica.",
            "aulas": [
                "Aula 21 – Aula expositiva dialogada sobre o comércio e as contribuições culturais islâmicas.",
                "Aula 22 – Aplicação de atividades do livro didático com mapas de rotas comerciais.",
                "Aula 23 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 9 – 30/03/2026 – 03/04/2026 (Paixão de Cristo 03/04) – Comparação Europa e Islã medieval.",
            "aulas": [
                "Aula 24 – Aula dialogada sobre o conteúdo, com resolução de exercícios de comparação.",
                "Aula 25 – Correção coletiva das atividades da aula anterior.",
                "Aula 26 – Atividade coletiva de revisão da semana.",
            ],
        },
        {
            "titulo": "SEMANA 10 – 06/04/2026 – 10/04/2026 – Preparação para as provas trimestrais.",
            "aulas": [
                "Aula 27 – Atividade coletiva de revisão do bimestre.",
                "Aula 28 – Atividade coletiva de revisão do bimestre.",
                "Aula 29 – Atividade coletiva de revisão do bimestre.",
            ],
        },
        {
            "titulo": "SEMANA 11 – 13/04/2026 – 17/04/2026 (Avaliação Global 15/04) – Avaliação trimestral.",
            "aulas": [
                "Aula 30 – Aplicação de provas.",
                "Aula 31 – Aplicação de provas.",
                "Aula 32 – Aplicação de provas.",
            ],
        },
        {
            "titulo": "SEMANA 12 – 20/04/2026 – 24/04/2026 (Tiradentes 21/04 / Recesso 20/04) – Recuperação e conselho de classe.",
            "aulas": [
                "Aula 33 – Atividades de Reensino / Recuperação.",
                "Aula 34 – Atividades de Reensino / Recuperação.",
                "Aula 35 – Atividades de Reensino / Recuperação.",
            ],
            "obs": "Observação: Feriado de Tiradentes no dia 21/04.",
        },
        {
            "titulo": "SEMANA 13 – 27/04/2026 – 30/04/2026 – Estudos de consolidação da Idade Média.",
            "aulas": [
                "Aula 36 – Aula dialogada de revisão dos conteúdos do trimestre.",
                "Aula 37 – Atividade coletiva de consolidação com fontes históricas.",
            ],
        },
        {
            "titulo": "SEMANA 14 – 04/05/2026 – 08/05/2026 – Renascimento urbano e comercial (início do 2º período).",
            "aulas": [
                "Aula 38 – Aula expositiva dialogada sobre o renascimento urbano e comercial.",
                "Aula 39 – Trabalho com textos do livro didático sobre guildas e feiras medievais.",
                "Aula 40 – Atividade do livro didático sobre rotas comerciais.",
            ],
        },
    ]

    # ----- 2º TRIMESTRE: renascimento/comércio/expansão/Paracatu -----
    conteudos_2 = texts_of_row_cell(r2, 2, 1)
    habilidades_2 = texts_of_row_cell(r2, 3, 1)
    objetivos_2 = texts_of_row_cell(r2, 4, 1)
    semanas_2 = [
        {
            "titulo": "SEMANA 1 – 11/05/2026 – 15/05/2026 (Recuperação trimestral) – Cidades medievais e burguesia.",
            "aulas": [
                "Aula 1 – Correção de atividades do livro didático.",
                "Aula 2 – Debate dialogado sobre o papel das cidades e da burguesia, com conexões locais.",
                "Aula 3 – Aplicação e correção coletiva de atividades.",
            ],
        },
        {
            "titulo": "SEMANA 2 – 18/05/2026 – 22/05/2026 (Conselho de classe 20/05) – Crises da Baixa Idade Média.",
            "aulas": [
                "Aula 4 – Aula expositiva dialogada sobre a peste negra e as guerras do século XIV.",
                "Aula 5 – Aplicação de atividades do livro didático com gráficos e cronologias.",
                "Aula 6 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 3 – 25/05/2026 – 29/05/2026 – Crise do feudalismo: revoltas camponesas.",
            "aulas": [
                "Aula 7 – Aula expositiva dialogada sobre as revoltas camponesas e o declínio feudal.",
                "Aula 8 – Análise de fontes históricas (documentos e imagens do século XIV).",
                "Aula 9 – Correção das atividades e sistematização.",
            ],
        },
        {
            "titulo": "SEMANA 4 – 01/06/2026 – 05/06/2026 (Corpus Christi 04/06) – Formação dos reinos ibéricos.",
            "aulas": [
                "Aula 10 – Aula expositiva dialogada sobre Portugal e Espanha na Idade Média.",
                "Aula 11 – Aplicação de atividades do livro didático com mapas de reconquistas.",
                "Aula 12 – Correção das atividades.",
            ],
            "obs": "Observação: Feriado de Corpus Christi no dia 04/06.",
        },
        {
            "titulo": "SEMANA 5 – 08/06/2026 – 12/06/2026 – Expansão marítima europeia.",
            "aulas": [
                "Aula 13 – Aula expositiva dialogada sobre motivações e técnicas náuticas.",
                "Aula 14 – Aplicação de atividades do livro didático com rotas marítimas.",
                "Aula 15 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 6 – 15/06/2026 – 19/06/2026 – História local de Paracatu e comércio medieval.",
            "aulas": [
                "Aula 16 – Aula dialogada sobre o comércio medieval e as expedições ibéricas em Paracatu.",
                "Aula 17 – Pesquisa orientada com fontes locais (documentos coloniais e mapas).",
                "Aula 18 – Correção coletiva das atividades, com fontes locais.",
            ],
        },
        {
            "titulo": "SEMANA 7 – 22/06/2026 – 26/06/2026 – Impactos da expansão em Paracatu.",
            "aulas": [
                "Aula 19 – Aula expositiva dialogada sobre a colonização e a exploração do ouro em Paracatu.",
                "Aula 20 – Aplicação de atividades do livro didático com mapas e documentos locais.",
                "Aula 21 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 8 – 29/06/2026 – 03/07/2026 – Revisão e consolidação do bimestre.",
            "aulas": [
                "Aula 22 – Aula dialogada sobre o conteúdo, com resolução de exercícios de comparação.",
                "Aula 23 – Correção coletiva das atividades da aula anterior.",
                "Aula 24 – Atividade coletiva de revisão da semana, incluindo Paracatu.",
            ],
        },
        {
            "titulo": "SEMANA 9 – 06/07/2026 – 10/07/2026 – Preparação para as provas trimestrais.",
            "aulas": [
                "Aula 25 – Aula dialogada sobre o conteúdo, com resolução de exercícios.",
                "Aula 26 – Correção coletiva das atividades da aula anterior, com foco local.",
                "Aula 27 – Atividade coletiva de revisão da semana.",
            ],
        },
        {
            "titulo": "SEMANA 10 – 13/07/2026 – 17/07/2026 – SEMANA DE PROVAS TRIMESTRAIS.",
            "aulas": [
                "Aula 28 – Aplicação de provas.",
                "Aula 29 – Aplicação de provas.",
                "Aula 30 – Aplicação de provas.",
            ],
        },
        {
            "titulo": "SEMANA 11 – 20/07/2026 – 24/07/2026 – Semana de recuperação bimestral e conselho de classe.",
            "aulas": [
                "Aula 31 – Atividades de Reensino / Recuperação, com foco em Paracatu.",
                "Aula 32 – Atividades de Reensino / Recuperação, revisando crises medievais.",
                "Aula 33 – Atividades de Reensino / Recuperação, com análise de fontes locais.",
            ],
        },
        {
            "titulo": "SEMANA 12 – 27/07/2026 – 31/07/2026 – América pré-colombiana: maias e astecas (início do 3º período).",
            "aulas": [
                "Aula 34 – Aula expositiva sobre as civilizações maias e astecas.",
                "Aula 35 – Trabalho com textos do livro didático.",
                "Aula 36 – Atividade do livro didático.",
            ],
        },
        {
            "titulo": "SEMANA 13 – 03/08/2026 – 07/08/2026 – Civilizações pré-colombianas: incas.",
            "aulas": [
                "Aula 37 – Correção de atividades e debate sobre a organização incaica.",
                "Aula 38 – Aplicação e correção coletiva de atividades.",
                "Aula 39 – Atividade de revisão da semana.",
            ],
        },
        {
            "titulo": "SEMANA 14 – 10/08/2026 – 14/08/2026 – Consolidação e conselho de classe.",
            "aulas": ["Aula 40 – Conselho de classe e entrega de resultados."],
        },
    ]

    # ----- 3º TRIMESTRE: Américas/África/Ásia + colonização do Brasil -----
    conteudos_3 = texts_of_row_cell(r3, 2, 1) + texts_of_row_cell(r4, 2, 1)
    habilidades_3 = texts_of_row_cell(r3, 3, 1) + texts_of_row_cell(r4, 3, 1)
    objetivos_3 = texts_of_row_cell(r3, 4, 1) + texts_of_row_cell(r4, 4, 1)
    semanas_3 = [
        {
            "titulo": "SEMANA 1 – 17/08/2026 – 21/08/2026 – América pré-colombiana: maias e astecas.",
            "aulas": [
                "Aula 1 – Aula expositiva sobre as civilizações maias e astecas.",
                "Aula 2 – Trabalho com textos do livro didático.",
                "Aula 3 – Atividade do livro didático.",
            ],
        },
        {
            "titulo": "SEMANA 2 – 24/08/2026 – 28/08/2026 – Civilizações pré-colombianas: incas.",
            "aulas": [
                "Aula 4 – Correção de atividades do livro didático.",
                "Aula 5 – Debate dialogado sobre a organização incaica e agricultura.",
                "Aula 6 – Aplicação e correção coletiva de atividades.",
            ],
        },
        {
            "titulo": "SEMANA 3 – 31/08/2026 – 04/09/2026 – Cultura indígena americana.",
            "aulas": [
                "Aula 7 – Aula expositiva dialogada sobre religião, mitologia e arte.",
                "Aula 8 – Aplicação de atividades do livro didático com imagens e mapas.",
                "Aula 9 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 4 – 07/09/2026 – 11/09/2026 (Independência do Brasil 07/09) – Impérios africanos: Gana e Mali.",
            "aulas": [
                "Aula 10 – Aula dialogada sobre o conteúdo, com análise de fontes sobre comércio de ouro.",
                "Aula 11 – Correção coletiva das atividades da aula anterior.",
                "Aula 12 – Atividade coletiva de revisão da semana.",
            ],
            "obs": "Observação: Feriado da Independência no dia 07/09.",
        },
        {
            "titulo": "SEMANA 5 – 14/09/2026 – 18/09/2026 – Império Songai e islamização.",
            "aulas": [
                "Aula 13 – Aula expositiva dialogada sobre Songai e islamização.",
                "Aula 14 – Aplicação de atividades do livro didático com mapas de rotas comerciais.",
                "Aula 15 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 6 – 21/09/2026 – 25/09/2026 – Ásia medieval: Rota da Seda.",
            "aulas": [
                "Aula 16 – Aula dialogada sobre o conteúdo, com resolução de exercícios de comparação.",
                "Aula 17 – Correção coletiva das atividades da aula anterior.",
                "Aula 18 – Atividade coletiva de revisão da semana.",
            ],
        },
        {
            "titulo": "SEMANA 7 – 28/09/2026 – 02/10/2026 – Expansão portuguesa e espanhola; Tratado de Tordesilhas.",
            "aulas": [
                "Aula 19 – Aula dialogada sobre tratados de Tordesilhas, com impacto em Paracatu.",
                "Aula 20 – Correção coletiva das atividades, com fontes locais.",
                "Aula 21 – Atividade coletiva de revisão da semana.",
            ],
        },
        {
            "titulo": "SEMANA 8 – 05/10/2026 – 09/10/2026 – Colonização do Brasil: exploração e bandeirantes.",
            "aulas": [
                "Aula 22 – Aula expositiva dialogada sobre a exploração e os bandeirantes.",
                "Aula 23 – Trabalho com textos do livro didático sobre bandeirantes.",
                "Aula 24 – Atividade do livro didático.",
            ],
        },
        {
            "titulo": "SEMANA 9 – 12/10/2026 – 16/10/2026 (Nossa Senhora Aparecida 12/10) – Engenhos de açúcar e mão de obra escrava.",
            "aulas": [
                "Aula 25 – Correção de atividades do livro didático.",
                "Aula 26 – Debate dialogado sobre os engenhos e a escravidão, com conexões locais.",
                "Aula 27 – Videoaula sobre a economia açucareira.",
            ],
            "obs": "Observação: Feriado de Nossa Senhora Aparecida no dia 12/10.",
        },
        {
            "titulo": "SEMANA 10 – 19/10/2026 – 23/10/2026 – Resistência indígena e africana: quilombos.",
            "aulas": [
                "Aula 28 – Aula expositiva dialogada sobre guerras, quilombos e culturas híbridas.",
                "Aula 29 – Aplicação de atividades do livro didático com mapas e narrativas.",
                "Aula 30 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 11 – 26/10/2026 – 30/10/2026 – Economia colonial: ouro e diamantes em Minas Gerais (Paracatu).",
            "aulas": [
                "Aula 31 – Aula expositiva dialogada sobre ouro e diamantes, com foco em Paracatu.",
                "Aula 32 – Aplicação de atividades do livro didático com mapas e documentos locais.",
                "Aula 33 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 12 – 02/11/2026 – 06/11/2026 (Finados 02/11) – Sociedade colonial brasileira.",
            "aulas": [
                "Aula 34 – Aula dialogada sobre hierarquia, patriarcado e Igreja, com exemplos locais.",
                "Aula 35 – Correção coletiva das atividades da aula anterior.",
                "Aula 36 – Atividade coletiva de revisão da semana.",
            ],
            "obs": "Observação: Feriado de Finados no dia 02/11.",
        },
        {
            "titulo": "SEMANA 13 – 09/11/2026 – 13/11/2026 – Iluminismo e influências coloniais.",
            "aulas": [
                "Aula 37 – Aula expositiva dialogada sobre o Iluminismo e suas ideias.",
                "Aula 38 – Aplicação de atividades do livro didático com textos iluministas.",
                "Aula 39 – Correção das atividades.",
            ],
        },
        {
            "titulo": "SEMANA 14 – 16/11/2026 – 20/11/2026 (Consciência Negra 20/11) – SEMANA DE PROVAS TRIMESTRAIS.",
            "aulas": ["Aula 40 – Aplicação de provas e recuperação final."],
            "obs": "Observação: Feriado da Consciência Negra no dia 20/11.",
        },
    ]

    t_novo_1 = tpl.build(
        titulo="PLANO DE AULA TRIMESTRAL:    1º TRIMESTRE",
        conteudos=conteudos_1,
        habilidades=habilidades_1,
        objetivos=objetivos_1,
        semanas=semanas_1,
        contextualizacao=[
            "Idade Média na Europa.",
            "Feudalismo.",
            "Igreja Católica.",
            "Cultura medieval.",
            "Invasões bárbaras.",
            "Império Carolíngio.",
            "Expansão do Islã.",
        ],
    )
    t_novo_2 = tpl.build(
        titulo="PLANO DE AULA TRIMESTRAL:    2º TRIMESTRE",
        conteudos=conteudos_2,
        habilidades=habilidades_2,
        objetivos=objetivos_2,
        semanas=semanas_2,
        contextualizacao=[
            "Alta e Baixa Idade Média.",
            "Renascimento comercial e urbano.",
            "Crises do século XIV.",
            "Reinos ibéricos.",
            "Expansão marítima europeia.",
            "História local de Paracatu (comércio e colonização).",
        ],
    )
    t_novo_3 = tpl.build(
        titulo="PLANO DE AULA TRIMESTRAL:    3º TRIMESTRE",
        conteudos=conteudos_3,
        habilidades=habilidades_3,
        objetivos=objetivos_3,
        semanas=semanas_3,
        contextualizacao=[
            "Civilizações pré-colombianas.",
            "Cultura indígena americana.",
            "Impérios africanos medievais.",
            "Ásia medieval.",
            "Expansão ibérica.",
            "Colonização do Brasil.",
            "História local de Paracatu (influências coloniais).",
        ],
    )

    slices = get_table_slices(orig_xml)
    # TRIMESTRAL tem 3 tabelas: remove a 4ª tabela original, preservando o
    # separador entre a 3ª e a 4ª e o sectPr que vem depois da 4ª.
    novo_body = (
        orig_xml[: slices[0][0]]
        + t_novo_1
        + orig_xml[slices[0][1] : slices[1][0]]
        + t_novo_2
        + orig_xml[slices[1][1] : slices[2][0]]
        + t_novo_3
        + orig_xml[slices[2][1] : slices[3][0]]
        + orig_xml[slices[3][1] :]
    )
    return novo_body


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    if not os.path.exists(ORIG):
        print("ERRO: arquivo original não encontrado:", ORIG)
        sys.exit(1)

    print("Lendo modelo original:", os.path.basename(ORIG))
    xml = read_document_xml(ORIG)
    slices = get_table_slices(xml)
    print("Tabelas top-level encontradas:", len(slices))
    if len(slices) != 4:
        print("AVISO: esperava 4 tabelas, encontrei", len(slices))

    orig_tables = [xml[s:e] for s, e in slices]
    tpl = Template(orig_tables[0])
    print("Template (Tabela 1): linhas =", len(tpl.rows))
    print(
        "  índices: conteudos=%s hab=%s obj=%s 1a_semana=%s desenv=%s context=%s acao=%s data=%s"
        % (
            tpl.idx_conteudos,
            tpl.idx_habilidades,
            tpl.idx_objetivos,
            tpl.idx_1a_semana,
            tpl.idx_desenv,
            tpl.idx_context,
            tpl.idx_acao,
            tpl.idx_data,
        )
    )

    # ---- BIMESTRAL ----
    print("\nGerando BIMESTRAL (4×30)...")
    body_bim = build_bimestral(tpl, xml, orig_tables)
    write_document_xml(OUT_BIMESTRAL, body_bim)

    # ---- TRIMESTRAL ----
    print("Gerando TRIMESTRAL (3×40)...")
    body_tri = build_trimestral(tpl, xml, orig_tables)
    write_document_xml(OUT_TRIMESTRAL, body_tri)

    print("\nConcluído.")
    print("  BIMESTRAL :", OUT_BIMESTRAL)
    print("  TRIMESTRAL:", OUT_TRIMESTRAL)


if __name__ == "__main__":
    main()
