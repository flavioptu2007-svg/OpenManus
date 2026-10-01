// Gera o projeto interdisciplinar "Raízes que Falam" (EJA – Cultura Afro-Brasileira) em .docx
// Uso: node gerar_projeto_afro_eja.js  → cria projeto_cultura_afro_brasileira_eja.docx nesta pasta
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, HeadingLevel, BorderStyle, ShadingType, LevelFormat, PageBreak,
  Header, Footer, PageNumber, HeightRule, VerticalAlign, TableOfContents,
} = require("docx");

const FONT = "Arial";
const W = 9638; // largura útil A4 com margens de 2 cm (DXA)
const CINZA = "D9D9D9";
const CINZA_CLARO = "F2F2F2";

// ---------- helpers ----------
const t = (text, o = {}) => new TextRun({ text, font: FONT, ...o });
const p = (content, o = {}) =>
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 120, line: 300 },
    ...o,
    children: (Array.isArray(content) ? content : [content]).map((c) => (typeof c === "string" ? t(c) : c)),
  });
const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [t(text)] });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [t(text)] });
const h3 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [t(text)] });
const bullet = (content, level = 0) =>
  new Paragraph({
    numbering: { reference: "bullets", level },
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 60, line: 288 },
    children: (Array.isArray(content) ? content : [content]).map((c) => (typeof c === "string" ? t(c) : c)),
  });
const num = (ref, content) =>
  new Paragraph({
    numbering: { reference: ref, level: 0 },
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 60, line: 288 },
    children: (Array.isArray(content) ? content : [content]).map((c) => (typeof c === "string" ? t(c) : c)),
  });
const lb = (label, text) => p([t(label, { bold: true }), t(text)]);
const pl = (text) => p(text, { alignment: AlignmentType.LEFT });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });
const blank = () => new Paragraph({ children: [t("")] });

const border = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const borders = { top: border, bottom: border, left: border, right: border };

function cell(content, width, o = {}) {
  const paras = (Array.isArray(content) ? content : [content]).map((c) =>
    c instanceof Paragraph
      ? c
      : new Paragraph({
          alignment: o.align || AlignmentType.LEFT,
          spacing: { after: 40 },
          children: [typeof c === "string" ? t(c, { bold: !!o.bold, size: o.size || 20 }) : c],
        })
  );
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 80, bottom: 80, left: 110, right: 110 },
    verticalAlign: o.vAlign || VerticalAlign.TOP,
    columnSpan: o.span,
    children: paras,
  });
}

// tabela simples: header = array de títulos (ou null), rows = array de arrays de strings
function table(widths, header, rows) {
  const trs = [];
  if (header)
    trs.push(
      new TableRow({
        tableHeader: true,
        children: header.map((h, i) => cell(h, widths[i], { bold: true, fill: CINZA })),
      })
    );
  rows.forEach((r) => trs.push(new TableRow({ children: r.map((c, i) => cell(c, widths[i])) })));
  return new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: widths, rows: trs });
}

// tabela de identificação: rótulo | valor
function kv(rows, wl = 2900) {
  const widths = [wl, W - wl];
  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map(
      ([k, v]) =>
        new TableRow({ children: [cell(k, widths[0], { bold: true, fill: CINZA_CLARO }), cell(v, widths[1])] })
    ),
  });
}

// moldura para inserção de foto + legenda
function fotoFrame(rotulo, altura = 3600) {
  return [
    new Table({
      width: { size: W, type: WidthType.DXA },
      columnWidths: [W],
      rows: [
        new TableRow({
          height: { value: altura, rule: HeightRule.EXACT },
          children: [
            new TableCell({
              borders: {
                top: { style: BorderStyle.DASHED, size: 8, color: "7F7F7F" },
                bottom: { style: BorderStyle.DASHED, size: 8, color: "7F7F7F" },
                left: { style: BorderStyle.DASHED, size: 8, color: "7F7F7F" },
                right: { style: BorderStyle.DASHED, size: 8, color: "7F7F7F" },
              },
              width: { size: W, type: WidthType.DXA },
              verticalAlign: VerticalAlign.CENTER,
              children: [
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [t(`[ ${rotulo} ]`, { color: "7F7F7F", size: 20 })],
                }),
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [t("Clique aqui e use Inserir > Imagens", { color: "A6A6A6", size: 16, italics: true })],
                }),
              ],
            }),
          ],
        }),
      ],
    }),
    new Paragraph({
      spacing: { before: 60, after: 40 },
      children: [t("Legenda: ", { bold: true, size: 18 }), t("_______________________________________________________________________", { size: 18 })],
    }),
    new Paragraph({
      spacing: { after: 200 },
      children: [
        t("Data: ", { bold: true, size: 18 }),
        t("____/____/2026     ", { size: 18 }),
        t("Fotografado por: ", { bold: true, size: 18 }),
        t("________________________________________", { size: 18 }),
      ],
    }),
  ];
}

// duas molduras lado a lado
function fotoDupla(r1, r2, altura = 3000) {
  const half = W / 2;
  const dashed = { style: BorderStyle.DASHED, size: 8, color: "7F7F7F" };
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const mk = (r, side) =>
    new TableCell({
      borders: { top: dashed, bottom: dashed, left: dashed, right: dashed },
      width: { size: half, type: WidthType.DXA },
      verticalAlign: VerticalAlign.CENTER,
      children: [
        new Paragraph({ alignment: AlignmentType.CENTER, children: [t(`[ ${r} ]`, { color: "7F7F7F", size: 18 })] }),
      ],
    });
  return [
    new Table({
      width: { size: W, type: WidthType.DXA },
      columnWidths: [half, half],
      rows: [new TableRow({ height: { value: altura, rule: HeightRule.EXACT }, children: [mk(r1), mk(r2)] })],
    }),
    new Paragraph({
      spacing: { before: 60, after: 200 },
      children: [t("Legendas: ", { bold: true, size: 18 }), t("(1) ______________________________   (2) ______________________________", { size: 18 })],
    }),
  ];
}

// cabeçalho pedagógico obrigatório de cada oficina
function cabecalhoOficina(dados) {
  return kv([
    ["Público", dados.publico],
    ["Componentes", dados.componentes],
    ["Unidade temática", dados.unidade],
    ["Objeto de conhecimento", dados.objeto],
    ["Habilidades (código)", dados.habilidades],
    ["Objetivo de aprendizagem", dados.objetivo],
    ["Duração", dados.duracao],
    ["Metodologia", dados.metodologia],
    ["Recursos", dados.recursos],
    ["Avaliação", dados.avaliacao],
  ]);
}

// registro de evento realizado (campos a preencher, sem dados inventados)
function registroEvento() {
  return kv([
    ["Data de realização", "____/____/2026"],
    ["Turmas / nº de participantes", ""],
    ["Docentes envolvidos", ""],
    ["Estudantes protagonistas (funções)", ""],
    ["O que funcionou bem", ""],
    ["O que ajustar na próxima etapa", ""],
    ["Falas marcantes dos estudantes", ""],
  ]);
}

// linhas para resposta escrita
const linhas = (n) =>
  Array.from({ length: n }, () =>
    new Paragraph({
      spacing: { after: 0, line: 400 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "A6A6A6", space: 1 } },
      children: [t("")],
    })
  );

// ---------- conteúdo ----------
const ESCOLA = "E. M. Cacilda Caetano de Souza";
const TITULO = "RAÍZES QUE FALAM";
const SUBTITULO = "Estudantes da EJA como protagonistas da cultura afro-brasileira na escola";

const capa = [
  new Paragraph({ spacing: { before: 600 }, alignment: AlignmentType.CENTER, children: [t("PREFEITURA MUNICIPAL DE PARACATU – MG", { bold: true, size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t(ESCOLA.toUpperCase(), { bold: true, size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [t("Educação de Jovens e Adultos – EJA", { size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t("PROJETO INTERDISCIPLINAR", { size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 120 }, children: [t(TITULO, { bold: true, size: 56 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [t(SUBTITULO, { italics: true, size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [t("Arte • Língua Portuguesa • História  |  Lei nº 10.639/2003", { size: 22 })] }),
  ...fotoFrame("Foto de capa: estudantes com as máscaras produzidas na oficina", 4300),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 400 }, children: [t("Paracatu – MG", { size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t("2026", { size: 22 })] }),
  pageBreak(),
];

const sumario = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [t("SUMÁRIO", { bold: true, size: 28 })] }),
  new TableOfContents("Sumário", { hyperlink: true, headingStyleRange: "1-2" }),
  p([t("Se o sumário aparecer vazio, clique com o botão direito sobre ele e escolha “Atualizar campo”.", { italics: true, size: 18, color: "7F7F7F" })]),
  pageBreak(),
];

const identificacao = [
  h1("1. Identificação do projeto"),
  kv([
    ["Título", `${TITULO} – ${SUBTITULO}`],
    ["Escola", `${ESCOLA} – Paracatu/MG`],
    ["Modalidade / público", "Educação de Jovens e Adultos (EJA) – Ciclos (1º ao 4º período)"],
    ["Componentes curriculares", "Arte, Língua Portuguesa e História"],
    ["Professor de História", "Flávio Alexandre dos Santos"],
    ["Professor(a) de Arte", "_____________________________________________"],
    ["Professor(a) de Língua Portuguesa", "_____________________________________________"],
    ["Período de execução", "____/____/2026 a ____/____/2026 (3º trimestre)"],
    ["Carga horária prevista", "Aproximadamente 8 horas-aula, distribuídas em 3 encontros e na culminância"],
    ["Base legal central", "Lei nº 10.639/2003 (arts. 26-A e 79-B da LDB, Lei nº 9.394/1996)"],
  ]),
  blank(),
  h1("2. Apresentação"),
  p("O projeto “Raízes que Falam” coloca os estudantes da EJA no centro do estudo das matrizes culturais africanas e afro-brasileiras. Em vez de apenas receberem informações, eles produzem objetos artísticos, conduzem conversas, compartilham memórias de vida e de comunidade, analisam um filme e transformam o que aprenderam em textos, exposição e debate para a escola."),
  p("A proposta articula três componentes curriculares. A Arte trabalha a produção e a leitura de máscaras africanas como objetos culturais com função social e religiosa. A História situa a África como continente de sociedades complexas, discute a escravidão, suas consequências e as políticas de ação afirmativa. A Língua Portuguesa desenvolve a oralidade argumentativa, a escuta respeitosa e a produção escrita."),
  p("O percurso é composto por três momentos já definidos: (1) oficina de confecção de máscaras africanas; (2) roda de conversa sobre as consequências da escravidão; (3) momento fílmico com “O Menino que Descobriu o Vento” (2019), seguido de debate, produção textual e exposição dos trabalhos."),
  h1("3. Justificativa"),
  p("A Lei nº 10.639/2003 incluiu na LDB a obrigatoriedade do ensino de História e Cultura Afro-Brasileira, com o estudo da História da África e dos africanos, da luta dos negros no Brasil, da cultura negra brasileira e do negro na formação da sociedade nacional. A mesma lei determina que esses conteúdos sejam trabalhados em todo o currículo, “em especial nas áreas de Educação Artística e de Literatura e História Brasileiras” – exatamente os três componentes que se unem neste projeto. Em 2008, a Lei nº 11.645 ampliou o art. 26-A para incluir também a história e a cultura dos povos indígenas."),
  p("Na EJA, o tema tem sentido particular. Muitos estudantes trazem experiências de trabalho, de migração, de fé e de enfrentamento de desigualdades que dialogam diretamente com a história da população negra no Brasil. Tratar esses saberes como conhecimento legítimo fortalece a autoestima, o sentimento de pertencimento e a permanência escolar, além de combater o racismo e a intolerância religiosa a partir da informação e do diálogo."),
  p("O projeto também responde às Diretrizes Curriculares Nacionais para a Educação das Relações Étnico-Raciais (Parecer CNE/CP nº 3/2004 e Resolução CNE/CP nº 1/2004), que orientam a valorização da história e da cultura afro-brasileira e africana e a educação para relações étnico-raciais positivas."),
  h1("4. Fundamentação legal"),
  table(
    [2600, 7038],
    ["Norma", "O que estabelece e como se relaciona ao projeto"],
    [
      ["Constituição Federal de 1988 – art. 5º, VI e XLII", "Garante a liberdade de consciência e de crença e o livre exercício dos cultos religiosos (inciso VI); define a prática do racismo como crime inafiançável e imprescritível (inciso XLII)."],
      ["Lei nº 9.394/1996 (LDB) – arts. 26-A e 79-B", "Incluídos pela Lei nº 10.639/2003: obrigatoriedade do ensino de História e Cultura Afro-Brasileira e inclusão do dia 20 de novembro no calendário escolar como “Dia Nacional da Consciência Negra”."],
      ["Lei nº 10.639, de 9 de janeiro de 2003", "Lei que fundamenta o projeto. Determina o estudo da História da África e dos africanos, da luta dos negros no Brasil e da cultura negra brasileira em todo o currículo."],
      ["Lei nº 11.645, de 10 de março de 2008", "Dá nova redação ao art. 26-A, incluindo a história e a cultura dos povos indígenas."],
      ["Parecer CNE/CP nº 3/2004 e Resolução CNE/CP nº 1/2004", "Diretrizes Curriculares Nacionais para a Educação das Relações Étnico-Raciais e para o Ensino de História e Cultura Afro-Brasileira e Africana."],
      ["Lei nº 12.288, de 20 de julho de 2010", "Estatuto da Igualdade Racial: define ações afirmativas e trata da garantia do direito à liberdade de consciência e de crença e ao livre exercício dos cultos de matriz africana."],
      ["Lei nº 12.711, de 29 de agosto de 2012 (atualizada pela Lei nº 14.723/2023)", "Reserva de vagas (cotas) nas universidades e institutos federais, com critérios sociais e étnico-raciais. Base para discutir ações afirmativas na roda de conversa."],
      ["STF – ADPF 186 (julgada em 2012)", "O Supremo Tribunal Federal declarou constitucional a política de cotas étnico-raciais para ingresso em universidade pública."],
      ["Lei nº 7.716/1989 e Lei nº 14.532/2023", "Definem os crimes resultantes de preconceito de raça ou de cor; a Lei nº 14.532/2023 tipificou a injúria racial como crime de racismo."],
      ["Lei nº 11.635, de 27 de dezembro de 2007", "Institui o dia 21 de janeiro como Dia Nacional de Combate à Intolerância Religiosa."],
      ["Lei nº 14.759, de 21 de dezembro de 2023", "Declara feriado nacional o Dia Nacional de Zumbi e da Consciência Negra (20 de novembro)."],
      ["Resolução CNE/CEB nº 1/2021", "Diretrizes Operacionais para a EJA, incluindo seu alinhamento à BNCC."],
      ["Lei nº 13.709/2018 (LGPD)", "Proteção de dados pessoais. Fundamenta o termo de autorização de uso de imagem (Anexo C)."],
    ]
  ),
  p([t("Observação: ", { bold: true }), t("conferir o texto atualizado de cada norma no Portal da Legislação (planalto.gov.br) antes de citá-las em documentos oficiais da escola.", { italics: true })], { spacing: { before: 120, after: 120 } }),
];

const objetivos = [
  h1("5. Objetivos"),
  h2("5.1 Objetivo geral"),
  p("Promover o protagonismo dos estudantes da EJA no estudo, na produção e na divulgação de conhecimentos sobre a História da África, as matrizes culturais africanas e afro-brasileiras, as consequências da escravidão, as ações afirmativas e as religiões de matriz africana, em cumprimento à Lei nº 10.639/2003 e na perspectiva da educação antirracista."),
  h2("5.2 Objetivos específicos"),
  bullet("Reconhecer a África como continente diverso, com sociedades, línguas, saberes, tecnologias e expressões artísticas próprias, superando a ideia de uma “história única”."),
  bullet("Compreender as máscaras africanas como objetos culturais ligados a rituais, à memória dos ancestrais, à vida comunitária e à religiosidade, e não apenas como objetos decorativos."),
  bullet("Produzir máscaras inspiradas em tradições de povos africanos específicos, identificando a origem, a função e os significados de cada referência."),
  bullet("Relacionar a escravidão e o pós-abolição às desigualdades raciais que permanecem na sociedade brasileira atual."),
  bullet("Discutir a finalidade das ações afirmativas, com base na legislação e em argumentos fundamentados."),
  bullet("Conhecer as religiões de matriz africana como patrimônio cultural brasileiro e combater a intolerância religiosa, respeitando a liberdade de crença de todos."),
  bullet("Desenvolver a oralidade argumentativa, a escuta respeitosa e a produção de textos (relato, resenha e carta aberta)."),
  bullet("Organizar e apresentar à comunidade escolar os resultados do projeto, com os estudantes como mediadores."),
];

const habilidades = [
  h1("6. Habilidades da BNCC mobilizadas"),
  p([t("Nota sobre a EJA: ", { bold: true }), t("a BNCC organiza as habilidades por ano do Ensino Fundamental e não traz um quadro próprio para a EJA. A Resolução CNE/CEB nº 1/2021 orienta o alinhamento da EJA à BNCC; por isso, as habilidades abaixo, dos anos finais do Ensino Fundamental, servem de referência e devem ser ajustadas ao período/ciclo de cada turma. Os textos das habilidades foram conferidos com reproduções da BNCC; recomenda-se a conferência final no documento oficial do MEC.")]),
  table(
    [1500, 1450, 6688],
    ["Componente", "Código", "Habilidade"],
    [
      ["Arte", "EF69AR05", "Experimentar e analisar diferentes formas de expressão artística (desenho, pintura, colagem, quadrinhos, dobradura, escultura, modelagem, instalação, vídeo, fotografia, performance etc.)."],
      ["Arte", "EF69AR31", "Relacionar as práticas artísticas às diferentes dimensões da vida social, cultural, política, histórica, econômica, estética e ética."],
      ["Arte", "EF69AR33", "Analisar aspectos históricos, sociais e políticos da produção artística, problematizando as narrativas eurocêntricas e as diversas categorizações da arte (arte, artesanato, folclore, design etc.)."],
      ["História", "EF07HI03", "Identificar aspectos e processos específicos das sociedades africanas e americanas antes da chegada dos europeus, com destaque para as formas de organização social e o desenvolvimento de saberes e técnicas."],
      ["História", "EF08HI20", "Identificar e relacionar aspectos das estruturas sociais da atualidade com os legados da escravidão no Brasil e discutir a importância de ações afirmativas."],
      ["História", "EF09HI03", "Identificar os mecanismos de inserção dos negros na sociedade brasileira pós-abolição e avaliar os seus resultados."],
      ["História", "EF09HI04", "Discutir a importância da participação da população negra na formação econômica, política e social do Brasil."],
      ["Língua Portuguesa", "EF69LP13", "Engajar-se e contribuir com a busca de conclusões comuns relativas a problemas, temas ou questões polêmicas de interesse da turma e/ou de relevância social."],
      ["Língua Portuguesa", "EF69LP15", "Apresentar argumentos e contra-argumentos coerentes, respeitando os turnos de fala, na participação em discussões sobre temas controversos e/ou polêmicos."],
    ]
  ),
  p([t("Religiões de matriz africana: ", { bold: true }), t("não há, nos componentes de Arte, Língua Portuguesa e História, habilidade da BNCC dedicada especificamente a esse tema. Ele é trabalhado com base na própria Lei nº 10.639/2003 (cultura negra brasileira), nas DCN para a Educação das Relações Étnico-Raciais, no Estatuto da Igualdade Racial e na Constituição Federal (liberdade de crença), articulado às habilidades EF69AR31 e EF69AR33 (dimensão cultural e religiosa das máscaras) e EF09HI04.")], { spacing: { before: 120, after: 120 } }),
  p([t("Currículo Referência de Minas Gerais (CRMG): ", { bold: true }), t("o CRMG incorpora as habilidades da BNCC; registrar aqui eventuais habilidades específicas do CRMG adotadas pela rede: ______________________________________________.")]),
];

const eixos = [
  h1("7. Eixos temáticos"),
  table(
    [2500, 7138],
    ["Eixo", "Conteúdos e conceitos centrais"],
    [
      ["História da África", "Diversidade de povos, línguas e reinos; saberes, técnicas e expressões artísticas; crítica à visão da África como lugar “sem história”; África contemporânea (o Malaui retratado no filme, independente do domínio britânico desde 1964)."],
      ["Matrizes culturais e arte", "Máscaras como objetos rituais e comunitários (exemplos: Gelede, dos iorubás – Nigéria, Benin e Togo; Pwo, dos chokwe – Angola; Ci Wara, dos bamanas – Mali; Gule Wamkulu, dos chewa – Malaui, Moçambique e Zâmbia); influência africana na arte moderna europeia e a crítica ao rótulo de “arte primitiva”."],
      ["Escravidão e suas consequências", "Tráfico atlântico; resistência (quilombos, revoltas, irmandades, compra de alforrias); abolição sem políticas de inclusão; racismo, desigualdades no trabalho, na renda, na educação e na moradia; memória e reparação."],
      ["Ações afirmativas", "Conceito de ação afirmativa (Estatuto da Igualdade Racial); cotas nas universidades federais (Lei nº 12.711/2012 e Lei nº 14.723/2023); decisão do STF na ADPF 186; argumentos e contra-argumentos presentes no debate público."],
      ["Religiões de matriz africana", "Candomblé, umbanda e outras tradições afro-brasileiras como patrimônio cultural; o sagrado, os ancestrais e a natureza; intolerância religiosa e racismo religioso; liberdade de crença como direito de todos (CF/88, art. 5º, VI)."],
    ]
  ),
];

const metodologia = [
  h1("8. Metodologia e protagonismo estudantil"),
  p("O projeto adota metodologias ativas: oficina de criação, roda de conversa, análise de fontes, sessão de cinema comentada, produção textual e exposição. O professor atua como mediador; os estudantes assumem funções reais, definidas em comum acordo no início do projeto e registradas no quadro abaixo. As funções podem ser assumidas individualmente ou em duplas e podem mudar a cada etapa."),
  table(
    [2600, 4638, 2400],
    ["Comissão / função", "Responsabilidades", "Estudantes"],
    [
      ["Pesquisa", "Buscar informações sobre os povos e as máscaras escolhidas; trazer reportagens, músicas e relatos para a roda de conversa.", ""],
      ["Mediação", "Abrir e conduzir a roda de conversa e o debate pós-filme; controlar o tempo de fala e garantir o respeito aos turnos.", ""],
      ["Memória e registro", "Fotografar (com autorização), anotar falas marcantes, organizar o diário de bordo do projeto.", ""],
      ["Curadoria e exposição", "Organizar a mostra das máscaras com fichas técnicas (povo, região, função, autor da releitura).", ""],
      ["Comunicação", "Produzir convites e cartazes; apresentar o projeto às demais turmas e à comunidade.", ""],
      ["Recepção e cinema", "Preparar o espaço da exibição, distribuir o roteiro de observação e conduzir o lanche coletivo, se houver.", ""],
    ]
  ),
  h3("Princípios para o trabalho com adultos"),
  bullet("Partir das experiências dos estudantes: trabalho, família, migração, fé, música, culinária e lutas por direitos."),
  bullet("Usar linguagem adulta e respeitosa; evitar materiais infantilizados."),
  bullet("Oferecer diferentes meios de participação (fala, escrita, desenho, produção manual) para incluir estudantes em diferentes níveis de leitura e escrita."),
  bullet("Ninguém é obrigado a expor sua religião ou experiências pessoais de discriminação; a participação nesses temas é sempre voluntária."),
  bullet("Combinar regras de convivência no primeiro encontro: escuta, respeito às crenças, nenhum tipo de ridicularização."),
];

const cronograma = [
  h1("9. Cronograma"),
  table(
    [1300, 3438, 2500, 2400],
    ["Etapa", "Atividade", "Componentes", "Data / situação"],
    [
      ["0", "Apresentação do projeto, levantamento de conhecimentos prévios e formação das comissões", "Todos", "____/____  (  ) realizada"],
      ["1", "Oficina de confecção de máscaras africanas", "Arte e História", "____/____  ( X ) realizada"],
      ["2", "Roda de conversa: as consequências da escravidão", "História e Língua Portuguesa", "____/____  ( X ) realizada"],
      ["3", "Momento fílmico: “O Menino que Descobriu o Vento”, debate e produção textual", "Língua Portuguesa, História e Arte", "____/____  (  ) prevista"],
      ["4", "Culminância: exposição das máscaras e dos textos (sugestão: semana de 20 de novembro)", "Todos", "____/____  (  ) prevista"],
      ["5", "Avaliação final do projeto com os estudantes", "Todos", "____/____  (  ) prevista"],
    ]
  ),
  p([t("Ajuste os status conforme o andamento real; as etapas 1 e 2 foram informadas como já realizadas.", { italics: true, size: 18, color: "595959" })], { spacing: { before: 80 } }),
];

// ---------- OFICINA 1 ----------
const oficina1 = [
  pageBreak(),
  h1("10. Etapa 1 – Oficina de confecção de máscaras africanas"),
  cabecalhoOficina({
    publico: "EJA – Ciclos (1º ao 4º período)",
    componentes: "Arte (condução) e História",
    unidade: "Arte: Matrizes estéticas e culturais; Processos de criação. História: O mundo moderno e a conexão entre sociedades africanas, americanas e europeias",
    objeto: "Máscaras africanas: função social, ritual e estética; saberes dos povos africanos expressos na cultura material e imaterial",
    habilidades: "EF69AR05, EF69AR31, EF69AR33, EF07HI03",
    objetivo: "Produzir uma máscara inspirada na tradição de um povo africano, explicando sua origem, sua função na comunidade e os significados de suas formas, cores e materiais.",
    duracao: "2 a 3 aulas (aprox. 100 a 150 minutos)",
    metodologia: "Exposição dialogada com imagens; estudo em grupos por povo/máscara; oficina de criação; partilha oral das produções",
    recursos: "Imagens de máscaras de acervos de museus (com referência completa); papelão, papel machê ou pratos de papel; tinta guache ou acrílica; cola; tesoura; barbante; sementes, palha, tecidos e retalhos",
    avaliacao: "Participação, ficha técnica da máscara, explicação oral do significado e cuidado com a origem cultural da referência",
  }),
  h2("10.1 Desenvolvimento"),
  num("passos1", [t("Acolhida e chamada (10 min). ", { bold: true }), t("Pergunta disparadora: “Para que serve uma máscara? Em que situações da nossa vida as pessoas usam máscaras?”")]),
  num("passos1", [t("Contextualização (25 min). ", { bold: true }), t("Apresentação de 3 ou 4 máscaras de povos diferentes, sempre com o nome do povo, a região e a função. Destacar que não existe “a máscara africana”, mas milhares de tradições distintas, ligadas a ritos de passagem, colheitas, funerais, homenagem a ancestrais, justiça e celebrações.")]),
  num("passos1", [t("Crítica à visão eurocêntrica (10 min). ", { bold: true }), t("Discutir por que, durante muito tempo, museus e livros europeus chamaram essas obras de “arte primitiva”, enquanto artistas modernos europeus se inspiravam nelas. Pergunta: quem decide o que é “arte” e o que é “artesanato”? (EF69AR33)")]),
  num("passos1", [t("Pesquisa em grupos (15 min). ", { bold: true }), t("Cada grupo escolhe uma referência e preenche a ficha técnica (Anexo A).")]),
  num("passos1", [t("Criação (40 a 60 min). ", { bold: true }), t("Produção da máscara. Estudantes com mais habilidade manual podem atuar como monitores dos colegas.")]),
  num("passos1", [t("Partilha (15 min). ", { bold: true }), t("Cada grupo apresenta sua máscara e explica o que ela representa. A comissão de memória registra as falas.")]),
  h2("10.2 Cuidados conceituais"),
  bullet("Máscaras rituais são, para muitos povos, objetos sagrados. Na oficina, os estudantes produzem releituras com finalidade educativa, e isso deve ser dito com clareza."),
  bullet("Evitar generalizações como “os africanos acreditam que...”; sempre nomear o povo e a região."),
  bullet("Usar imagens de acervos de museus com título, povo, data aproximada, instituição e link direto do item; a fonte deve ficar abaixo de cada imagem."),
  bullet("Ponte com a Etapa 3: a tradição Gule Wamkulu, com dançarinos mascarados do povo chewa, é praticada no Malaui, país onde se passa o filme, e foi reconhecida pela UNESCO como Patrimônio Cultural Imaterial da Humanidade."),
  h2("10.3 Registro do evento"),
  registroEvento(),
  blank(),
  h2("10.4 Registro fotográfico"),
  ...fotoFrame("Foto 1: estudantes durante a confecção das máscaras"),
  ...fotoDupla("Foto 2: detalhe de uma máscara", "Foto 3: apresentação dos grupos"),
];

// ---------- OFICINA 2 ----------
const oficina2 = [
  pageBreak(),
  h1("11. Etapa 2 – Roda de conversa: as consequências da escravidão"),
  cabecalhoOficina({
    publico: "EJA – Ciclos (1º ao 4º período)",
    componentes: "História (condução) e Língua Portuguesa",
    unidade: "História: O Brasil no século XIX (8º ano); O nascimento da República no Brasil e os processos históricos até a metade do século XX (9º ano). Língua Portuguesa: Oralidade – discussão oral",
    objeto: "Escravismo no Brasil, legados da escravidão, pós-abolição, ações afirmativas, racismo e intolerância religiosa",
    habilidades: "EF08HI20, EF09HI03, EF09HI04, EF69LP13, EF69LP15",
    objetivo: "Relacionar a escravidão e o pós-abolição às desigualdades raciais atuais e argumentar, com respeito aos turnos de fala, sobre ações afirmativas e combate ao racismo e à intolerância religiosa.",
    duracao: "2 aulas (aprox. 100 minutos)",
    metodologia: "Roda de conversa mediada por estudantes, com fontes disparadoras e registro coletivo das conclusões",
    recursos: "Cadeiras em círculo; trechos da Lei nº 10.639/2003, da Lei Áurea e do Estatuto da Igualdade Racial; dados oficiais (por exemplo, a publicação do IBGE “Desigualdades Sociais por Cor ou Raça no Brasil”); cartolina para o mural de conclusões",
    avaliacao: "Qualidade da participação oral (argumentos, uso de exemplos, respeito aos turnos) e contribuição para o mural coletivo",
  }),
  h2("11.1 Desenvolvimento"),
  num("passos2", [t("Combinados (5 min). ", { bold: true }), t("Os mediadores relembram as regras: uma pessoa fala por vez, escutar até o fim, discordar de ideias e não de pessoas, ninguém é obrigado a expor experiências pessoais.")]),
  num("passos2", [t("Fonte disparadora (15 min). ", { bold: true }), t("Leitura em voz alta da Lei Áurea (Lei nº 3.353, de 13 de maio de 1888), que tem apenas dois artigos. Pergunta: “O que a lei diz e o que ela não diz? O que aconteceu com as pessoas libertas no dia seguinte?”")]),
  num("passos2", [t("Rodada 1 – Consequências (25 min). ", { bold: true }), t("Discussão orientada pelas perguntas do item 11.2, blocos A e B.")]),
  num("passos2", [t("Rodada 2 – Ações afirmativas e religiões de matriz africana (30 min). ", { bold: true }), t("Perguntas dos blocos C e D. Os mediadores incentivam que os estudantes apresentem argumentos e contra-argumentos (EF69LP15).")]),
  num("passos2", [t("Síntese coletiva (15 min). ", { bold: true }), t("A turma elabora o mural “O que aprendemos e o que queremos mudar”, buscando conclusões comuns (EF69LP13).")]),
  num("passos2", [t("Encerramento (10 min). ", { bold: true }), t("Cada participante diz uma palavra que resume a roda. A comissão de memória registra.")]),
  h2("11.2 Roteiro de perguntas para os mediadores"),
  h3("Bloco A – Escravidão e resistência"),
  bullet("Por quanto tempo houve escravidão legal no Brasil? O que isso significa para a formação do país?"),
  bullet("Como as pessoas escravizadas resistiram? (fugas, quilombos, revoltas, irmandades, compra de alforrias, preservação de línguas, religiões e saberes)"),
  bullet("Existem comunidades quilombolas em Paracatu ou na região? O que sabemos sobre elas? (pesquisar na lista oficial de comunidades certificadas pela Fundação Cultural Palmares)"),
  h3("Bloco B – Consequências no presente"),
  bullet("Após 1888, quais políticas o Estado criou para garantir terra, trabalho e escola às pessoas libertas? Quais foram os resultados? (EF09HI03)"),
  bullet("Que marcas da escravidão percebemos hoje no trabalho, na renda, na moradia, na educação e na violência? (EF08HI20)"),
  bullet("O que é racismo? Qual a diferença entre preconceito, discriminação e racismo? O que diz a lei brasileira sobre o tema?"),
  h3("Bloco C – Ações afirmativas"),
  bullet("O que são ações afirmativas? Por que existem? (Estatuto da Igualdade Racial)"),
  bullet("Quais argumentos aparecem a favor e contra as cotas? Como o STF decidiu na ADPF 186?"),
  bullet("A EJA também pode ser vista como uma política de reparação do direito à educação? Por quê?"),
  h3("Bloco D – Religiões de matriz africana"),
  bullet("Que religiões de matriz africana existem no Brasil? O que sabemos e o que ouvimos falar sobre elas? De onde vêm essas informações?"),
  bullet("Por que essas religiões foram perseguidas no passado e ainda sofrem ataques? O que significa “racismo religioso”?"),
  bullet("O que a Constituição garante sobre liberdade de crença? Como podemos respeitar uma fé diferente da nossa?"),
  p([t("Atenção do mediador: ", { bold: true }), t("o objetivo do Bloco D não é discutir qual religião é verdadeira, mas compreender essas tradições como parte da cultura brasileira e defender o direito de todos à sua própria fé.")], { spacing: { before: 120 } }),
  h2("11.3 Registro do evento"),
  registroEvento(),
  blank(),
  h2("11.4 Mural de conclusões da turma"),
  p("Transcrever aqui as conclusões registradas no mural coletivo:"),
  ...linhas(6),
  blank(),
  h2("11.5 Registro fotográfico"),
  ...fotoFrame("Foto 4: roda de conversa"),
  ...fotoDupla("Foto 5: mediadores em ação", "Foto 6: mural de conclusões"),
];

// ---------- OFICINA 3 ----------
const oficina3 = [
  pageBreak(),
  h1("12. Etapa 3 – Momento fílmico: “O Menino que Descobriu o Vento”"),
  cabecalhoOficina({
    publico: "EJA – Ciclos (1º ao 4º período)",
    componentes: "Língua Portuguesa (condução), História e Arte",
    unidade: "História: História da África contemporânea. Língua Portuguesa: Leitura e produção de textos; Oralidade. Arte: Artes visuais/audiovisual",
    objeto: "Leitura crítica de obra cinematográfica; representação da África; protagonismo, ciência e educação; argumentação oral e escrita",
    habilidades: "EF69LP13, EF69LP15, EF69AR31, EF09HI04 (por analogia com o protagonismo negro)",
    objetivo: "Analisar criticamente o filme, identificando o contexto histórico do Malaui, as formas de protagonismo do personagem e as representações da África, e produzir um texto de opinião sobre a obra.",
    duracao: "3 aulas (exibição de aprox. 1h53 + debate e produção textual); se necessário, dividir a exibição em dois encontros",
    metodologia: "Sessão de cinema comentada, com roteiro de observação, debate mediado por estudantes e produção textual",
    recursos: "Projetor ou TV, caixa de som, acesso ao filme por meio legal, roteiro de observação (item 12.3), cópias da proposta de produção textual",
    avaliacao: "Roteiro de observação preenchido, participação no debate e produção textual (resenha ou carta)",
  }),
  h2("12.1 Ficha técnica"),
  kv([
    ["Título no Brasil", "O Menino que Descobriu o Vento"],
    ["Título original", "The Boy Who Harnessed the Wind"],
    ["Ano", "2019"],
    ["Direção e roteiro", "Chiwetel Ejiofor"],
    ["Elenco principal", "Maxwell Simba (William Kamkwamba), Chiwetel Ejiofor (Trywell Kamkwamba), Aïssa Maïga (Agnes Kamkwamba)"],
    ["Base", "Livro autobiográfico de William Kamkwamba e Bryan Mealer (2009), publicado no Brasil com o mesmo título"],
    ["Ambientação", "Malaui, início dos anos 2000, durante uma grave crise de fome"],
    ["Idiomas", "Inglês e chichewa (assistir com legendas ou dublado, conforme a turma)"],
    ["Duração", "Aproximadamente 113 minutos"],
    ["Classificação indicativa", "Conferir na plataforma de exibição antes da sessão: ________________"],
  ], 2600),
  h2("12.2 Por que este filme no projeto"),
  bullet("Apresenta um protagonista africano que transforma sua realidade por meio do conhecimento, da leitura e da ciência, contrariando a imagem da África apenas como lugar de carência."),
  bullet("Mostra a importância da escola e o drama de quem precisa abandoná-la por falta de condições – experiência próxima de muitos estudantes da EJA."),
  bullet("Permite discutir a relação entre clima, política, economia e fome, além da organização comunitária."),
  bullet("Dialoga com a Etapa 1: observe se aparecem no filme dançarinos mascarados e relacione-os às tradições de máscaras estudadas na oficina."),
  h2("12.3 Roteiro de observação (para os estudantes)"),
  h3("Antes do filme"),
  bullet("Localizar o Malaui no mapa da África. Quais países fazem fronteira com ele?"),
  bullet("Pergunta de expectativa: o que você imagina que vai ver em um filme sobre um país africano? Anote e compare depois."),
  h3("Durante o filme – anote"),
  bullet("Uma cena que mostra a vida em comunidade."),
  bullet("Uma cena que mostra a importância da escola ou da leitura."),
  bullet("Uma cena que mostra conflito entre gerações ou entre tradição e mudança."),
  bullet("Uma cena com música, dança, ritual ou máscaras."),
  h3("Depois do filme – debate mediado pelos estudantes"),
  num("debate", "Quais obstáculos William enfrentou? Quais pessoas e saberes o ajudaram?"),
  num("debate", "Por que William não pôde continuar na escola? Isso acontece no Brasil? Alguém aqui já viveu algo parecido? (resposta voluntária)"),
  num("debate", "O filme confirmou ou mudou o que você imaginava sobre a África? Por quê?"),
  num("debate", "Qual a relação entre a fome mostrada no filme e as decisões políticas e econômicas? A fome é apenas um problema natural?"),
  num("debate", "Trywell, o pai, resiste à ideia do filho no começo. Que argumentos cada um usa? Quem tinha razão? (EF69LP15)"),
  num("debate", "Que relação podemos fazer entre a história de William e o tema do projeto: protagonismo, conhecimento e superação de desigualdades?"),
  h2("12.4 Produção textual (Língua Portuguesa)"),
  p("Cada estudante escolhe uma das propostas. Estudantes em processo de alfabetização podem produzir o texto oralmente, com registro feito por um colega escriba ou gravado em áudio."),
  table(
    [2400, 7238],
    ["Proposta", "Orientação"],
    [
      ["A – Resenha do filme", "Apresente o filme (título, ano, diretor, assunto), resuma a história sem contar o final e dê sua opinião com pelo menos dois argumentos. Recomende ou não o filme para outras turmas da EJA."],
      ["B – Carta a William Kamkwamba", "Escreva uma carta ao personagem real contando o que você aprendeu com a história dele e relacionando-a com a sua própria trajetória de estudos."],
      ["C – Carta aberta à comunidade", "Com base em todo o projeto, escreva uma carta aberta defendendo uma ação concreta de combate ao racismo ou à intolerância religiosa na escola ou no bairro."],
    ]
  ),
  h2("12.5 Culminância"),
  p("No dia da exibição, ou em data próxima a 20 de novembro, a comissão de curadoria organiza a exposição das máscaras com suas fichas técnicas e dos textos produzidos. A comissão de comunicação convida outras turmas e a comunidade. Os estudantes atuam como guias da exposição, explicando o significado de cada máscara."),
  h2("12.6 Registro do evento"),
  registroEvento(),
  blank(),
  h2("12.7 Registro fotográfico"),
  ...fotoFrame("Foto 7: sessão de cinema"),
  ...fotoDupla("Foto 8: debate após o filme", "Foto 9: exposição das máscaras e dos textos"),
];

// ---------- AVALIAÇÃO ----------
const avaliacao = [
  pageBreak(),
  h1("13. Avaliação"),
  p("A avaliação é processual e formativa, considerando a participação em todas as etapas, os registros produzidos e a autoavaliação dos estudantes. Os critérios abaixo podem ser usados por todos os componentes envolvidos."),
  table(
    [2500, 2380, 2380, 2378],
    ["Critério", "Plenamente atingido", "Parcialmente atingido", "Ainda não atingido"],
    [
      ["Compreensão histórica", "Relaciona escravidão, pós-abolição e desigualdades atuais com exemplos.", "Reconhece a relação, mas com poucos exemplos.", "Ainda não relaciona passado e presente."],
      ["Produção artística", "Produz máscara e explica povo, função e significados.", "Produz máscara com explicação incompleta.", "Produz sem relacionar à referência cultural."],
      ["Oralidade e argumentação", "Apresenta argumentos e contra-argumentos e respeita os turnos de fala.", "Opina com argumentos pouco desenvolvidos.", "Participa pouco ou sem argumentar."],
      ["Produção textual", "Atende à proposta, com opinião fundamentada e organização clara.", "Atende parcialmente à proposta.", "Não atende à proposta."],
      ["Protagonismo e respeito", "Assume função na comissão e respeita a diversidade de crenças e opiniões.", "Participa quando solicitado.", "Não se envolve nas funções."],
    ]
  ),
  h2("13.1 Autoavaliação do estudante"),
  table(
    [6638, 1000, 1000, 1000],
    ["Afirmação", "Sim", "Em parte", "Não"],
    [
      ["Aprendi coisas novas sobre a história e as culturas da África.", "", "", ""],
      ["Entendo melhor as consequências da escravidão no Brasil de hoje.", "", "", ""],
      ["Sei explicar o que são ações afirmativas.", "", "", ""],
      ["Respeito religiões diferentes da minha.", "", "", ""],
      ["Participei ativamente de uma comissão do projeto.", "", "", ""],
    ]
  ),
  p("O que mais marcou você neste projeto?", { spacing: { before: 160 } }),
  ...linhas(3),
  blank(),
  h1("14. Resultados esperados"),
  bullet("Estudantes capazes de explicar a diversidade cultural africana e a contribuição africana e afro-brasileira para a formação do Brasil."),
  bullet("Ampliação da autoestima, do sentimento de pertencimento e da participação dos estudantes da EJA na vida da escola."),
  bullet("Redução de manifestações de preconceito racial e religioso no ambiente escolar."),
  bullet("Exposição das produções e registro documental do projeto, que pode servir de referência para os próximos anos."),
];

// ---------- ANEXOS ----------
const anexos = [
  pageBreak(),
  h1("Anexo A – Ficha técnica da máscara"),
  p("Preencha com o seu grupo e coloque a ficha ao lado da máscara na exposição."),
  kv([
    ["Nome da máscara / tradição", ""],
    ["Povo", ""],
    ["País / região", ""],
    ["Função na comunidade", ""],
    ["Significado das formas e cores", ""],
    ["Materiais originais", ""],
    ["Materiais usados na releitura", ""],
    ["Fonte da imagem de referência (museu, link)", ""],
    ["Autores da releitura", ""],
  ], 3600),
  blank(),
  ...fotoFrame("Foto da máscara produzida pelo grupo", 3000),
  pageBreak(),
  h1("Anexo B – Diário de bordo da comissão de memória"),
  table(
    [1500, 3200, 4938],
    ["Data", "Etapa / atividade", "O que aconteceu e falas marcantes"],
    Array.from({ length: 8 }, () => ["", "", ""])
  ),
  blank(),
  h1("Anexo C – Termo de autorização de uso de imagem"),
  pl("Eu, ________________________________________________, documento nº ____________________, estudante da EJA da " + ESCOLA + ", AUTORIZO o uso da minha imagem e voz, captadas durante as atividades do projeto “Raízes que Falam”, exclusivamente para fins pedagógicos e de divulgação institucional da escola e da Secretaria Municipal de Educação de Paracatu, sem fins lucrativos, em conformidade com a Lei nº 13.709/2018 (LGPD)."),
  p("Esta autorização pode ser revogada a qualquer momento, mediante comunicação à direção da escola."),
  p("(   ) Autorizo          (   ) Não autorizo"),
  p("Paracatu/MG, ____ de ____________________ de 2026.", { spacing: { before: 240 } }),
  new Paragraph({ spacing: { before: 480 }, alignment: AlignmentType.CENTER, children: [t("_________________________________________________")] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [t("Assinatura do(a) estudante (ou do responsável legal, se menor de 18 anos)")] }),
  pageBreak(),
  h1("15. Referências"),
  pl("BRASIL. Constituição da República Federativa do Brasil de 1988. Brasília, DF: Presidência da República. Disponível em: https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm."),
  pl("BRASIL. Lei nº 9.394, de 20 de dezembro de 1996. Estabelece as diretrizes e bases da educação nacional. Disponível em: https://www.planalto.gov.br/ccivil_03/leis/l9394.htm."),
  pl("BRASIL. Lei nº 10.639, de 9 de janeiro de 2003. Disponível em: https://www.planalto.gov.br/ccivil_03/leis/2003/l10.639.htm."),
  pl("BRASIL. Lei nº 11.645, de 10 de março de 2008. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11645.htm."),
  pl("BRASIL. Lei nº 12.288, de 20 de julho de 2010. Institui o Estatuto da Igualdade Racial. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12288.htm."),
  pl("BRASIL. Lei nº 12.711, de 29 de agosto de 2012. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12711.htm."),
  pl("BRASIL. Ministério da Educação. Base Nacional Comum Curricular. Brasília: MEC, 2018. Disponível em: http://basenacionalcomum.mec.gov.br/."),
  pl("BRASIL. Conselho Nacional de Educação. Parecer CNE/CP nº 3/2004 e Resolução CNE/CP nº 1/2004. Diretrizes Curriculares Nacionais para a Educação das Relações Étnico-Raciais e para o Ensino de História e Cultura Afro-Brasileira e Africana."),
  pl("BRASIL. Conselho Nacional de Educação. Resolução CNE/CEB nº 1, de 25 de maio de 2021. Diretrizes Operacionais para a Educação de Jovens e Adultos."),
  pl("IBGE. Desigualdades Sociais por Cor ou Raça no Brasil. Rio de Janeiro: IBGE (Estudos e Pesquisas – Informação Demográfica e Socioeconômica). Disponível em: https://www.ibge.gov.br/."),
  pl("KAMKWAMBA, William; MEALER, Bryan. The Boy Who Harnessed the Wind. New York: William Morrow, 2009."),
  pl("O MENINO que descobriu o vento (The Boy Who Harnessed the Wind). Direção e roteiro: Chiwetel Ejiofor. Reino Unido/Malaui, 2019. 1 filme (aprox. 113 min)."),
  pl("UNESCO. Coleção História Geral da África. 8 v. Brasília: UNESCO; MEC; UFSCar, 2010. Disponível em: https://www.unesco.org/pt."),
  pl("UNESCO. Gule Wamkulu. Lista Representativa do Patrimônio Cultural Imaterial da Humanidade. Disponível em: https://ich.unesco.org/."),
  pl("ADICHIE, Chimamanda Ngozi. O perigo de uma história única. São Paulo: Companhia das Letras, 2019. (Também disponível como palestra TED, 2009.)"),
];

// ---------- documento ----------
const doc = new Document({
  creator: "Flávio Alexandre dos Santos",
  title: "Raízes que Falam – Projeto interdisciplinar EJA",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: "000000" },
        paragraph: { spacing: { before: 300, after: 160 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: "404040", space: 2 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: FONT, color: "262626" },
        paragraph: { spacing: { before: 220, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, italics: true, font: FONT, color: "404040" },
        paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 283 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1134, hanging: 283 } } } },
      ] },
      ...["passos1", "passos2", "debate"].map((ref) => ({
        reference: ref,
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 340 } } } }],
      })),
    ],
  },
  sections: [
    {
      properties: {
        page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 } },
        titlePage: true,
      },
      headers: {
        default: new Header({
          children: [
            new Paragraph({
              alignment: AlignmentType.RIGHT,
              border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "A6A6A6", space: 2 } },
              children: [t(`${ESCOLA} – EJA  |  Projeto “Raízes que Falam”`, { size: 16, color: "595959" })],
            }),
          ],
        }),
        first: new Header({ children: [new Paragraph({ children: [] })] }),
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [t("Página ", { size: 16, color: "595959" }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "595959" })],
            }),
          ],
        }),
        first: new Footer({ children: [new Paragraph({ children: [] })] }),
      },
      children: [
        ...capa, ...sumario, ...identificacao, ...objetivos, ...habilidades, ...eixos,
        ...metodologia, ...cronograma, ...oficina1, ...oficina2, ...oficina3, ...avaliacao, ...anexos,
      ],
    },
  ],
});

const out = path.join(__dirname, "projeto_cultura_afro_brasileira_eja.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(out, buf);
  console.log("Gerado:", out);
});
