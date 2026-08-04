#!/usr/bin/env python3
"""Gera ~60 novas perguntas focadas em temas do 8º e 9º ano com deficit."""

NOVAS_PERGUNTAS = """
      // ── NOVAS PERGUNTAS 8º ANO (temas com deficit) ──

      // América Latina (tinha 3)
      { id:"q258", tema:"8amerlat", ano:"8º Ano", pergunta:"A Guerra do Paraguai foi o conflito entre a Tríplice Aliança e:", dif:"facil",
        opts:["Argentina","Brasil","Paraguai de Solano López","Uruguai"],
        resp:2, exp:"A Tríplice Aliança (Brasil, Argentina, Uruguai) lutou contra o Paraguai de Solano López (1864-1870)." },
      { id:"q259", tema:"8amerlat", ano:"8º Ano", pergunta:"O Uruguai tornou-se independente em 1828 após:", dif:"dificil",
        opts:["Guerra contra o Brasil","Guerra da Cisplatina entre Brasil e Argentina","Tratado com a Inglaterra","Revolução local"],
        resp:1, exp:"O Uruguai (Província Cisplatina) tornou-se independente após a Guerra da Cisplatina (1825-1828)." },
      { id:"q260", tema:"8amerlat", ano:"8º Ano", pergunta:"Qual país latino-americano aboliu a escravatura primeiro?", dif:"dificil",
        opts:["Brasil","Haiti","Cuba","México"],
        resp:1, exp:"O Haiti aboliu a escravatura em 1804, após a Revolução Haitiana." },
      { id:"q261", tema:"8amerlat", ano:"8º Ano", pergunta:"O caudilhismo na América Latina era caracterizado por:", dif:"dificil",
        opts:["Governo democrático","Líderes regionais com poder militar e personalista","Governo parlamentar","República socialista"],
        resp:1, exp:"Caudilhos eram líderes militares e políticos que exerciam poder autoritário em regiões da América Latina." },

      // Antecedentes da 1ª Guerra (tinha 3)
      { id:"q262", tema:"8ante1gm", ano:"8º Ano", pergunta:"O assassinato de Francisco Ferdinando ocorreu em qual cidade?", dif:"medio",
        opts:["Viena","Berlim","Sarajevo","Paris"],
        resp:2, exp:"O arquiduque austríaco foi assassinado em Sarajevo (Bósnia) em 28 de junho de 1914 por Gavrilo Princip." },
      { id:"q263", tema:"8ante1gm", ano:"8º Ano", pergunta:"O pan-eslavismo era um movimento que defendia:", dif:"dificil",
        opts:["União dos povos germânicos","União dos povos eslavos sob liderança russa","Expansão alemã","Colonialismo"],
        resp:1, exp:"O pan-eslavismo defendia a união dos povos eslavos, apoiado pela Rússia contra o Império Austro-Húngaro." },
      { id:"q264", tema:"8ante1gm", ano:"8º Ano", pergunta:"A Alemanha unificou-se em 1871 sob a liderança de:", dif:"medio",
        opts:["Bismarck","Hitler","Frederico, o Grande","Kaiser Wilhelm II"],
        resp:0, exp:"Otto von Bismarck unificou a Alemanha após a Guerra Franco-Prussiana (1870-1871)." },
      { id:"q265", tema:"8ante1gm", ano:"8º Ano", pergunta:"O revanchismo francês (após 1871) era o desejo de:", dif:"dificil",
        opts:["Paz com a Alemanha","Revanche contra a Alemanha pela perda da Alsácia-Lorena","Aliança com a Alemanha","Colonizar a África"],
        resp:1, exp:"A França perdeu Alsácia-Lorena para a Alemanha em 1871, gerando desejo de revanche que alimentou a 1ª Guerra." },

      // Crise do Império (tinha 3)
      { id:"q266", tema:"8criseimp", ano:"8º Ano", pergunta:"A Questão Militar envolveu a insatisfação dos militares com:", dif:"dificil",
        opts:["Baixos salários","Falta de promoções e punições a oficiais que criticavam o governo","Derrotas em guerra","Extinção do exército"],
        resp:1, exp:"Militares insatisfeitos com o governo imperial e influenciados pelo positivismo aderiram à causa republicana." },
      { id:"q267", tema:"8criseimp", ano:"8º Ano", pergunta:"O Manifesto Republicano (1870) defendia:", dif:"dificil",
        opts:["Monarquia federal","República federativa baseada no modelo americano","Volta da monarquia absoluta","Independência das províncias"],
        resp:1, exp:"O Manifesto Republicano (1870) propunha a República federativa como alternativa à monarquia centralizada." },

      // Imperialismo (tinha 3)
      { id:"q268", tema:"8imperial", ano:"8º Ano", pergunta:"O neocolonialismo do séc. XIX diferenciava-se do colonialismo dos séc. XVI-XVII porque:", dif:"dificil",
        opts:["Visava povoar","Visava controlar mercados e fontes de matéria-prima para a indústria","Visava apenas difundir a religião","Era pacífico"],
        resp:1, exp:"O neocolonialismo buscava mercados consumidores, matérias-primas e áreas de investimento para a indústria europeia." },
      { id:"q269", tema:"8imperial", ano:"8º Ano", pergunta:"A Guerra dos Boxers (1900) na China foi:", dif:"dificil",
        opts:["Revolução comunista","Revolta contra a influência estrangeira na China","Guerra civil","Conflito com o Japão"],
        resp:1, exp:"Os Boxers foram uma sociedade secreta chinesa que se rebelou contra a influência imperialista europeia." },

      // Primeiro Reinado (tinha 3)
      { id:"q270", tema:"8primeiro", ano:"8º Ano", pergunta:"A Confederação do Equador (1824) foi uma revolta:", dif:"medio",
        opts:["Monarquista no Sul","Republicana no Nordeste contra o autoritarismo de D. Pedro I","Federalista no Rio Grande do Sul","Abolicionista na Bahia"],
        resp:1, exp:"A Confederação do Equador foi uma revolta republicana no Nordeste contra o fechamento da Assembleia por D. Pedro I." },
      { id:"q271", tema:"8primeiro", ano:"8º Ano", pergunta:"A dívida externa brasileira começou com:", dif:"dificil",
        opts:["Guerra do Paraguai","Empréstimo português para pagar indenização do reconhecimento da independência","Crise de 1929","Construção de Brasília"],
        resp:1, exp:"O Brasil assumiu dívidas de Portugal (empréstimo de 1823) como condição para o reconhecimento da independência." },
      { id:"q272", tema:"8primeiro", ano:"8º Ano", pergunta:"D. Pedro I abdicou em 1831 devido a:", dif:"medio",
        opts:["Golpe militar","Pressões políticas, crise econômica e impopularidade","Doença","Invasão estrangeira"],
        resp:1, exp:"D. Pedro I abdicou devido à crise política, econômica e à sua impopularidade crescente entre os brasileiros." },

      // Independência do Brasil (tinha 4)
      { id:"q273", tema:"8indbr", ano:"8º Ano", pergunta:"O Grito do Ipiranga (7/9/1822) foi:", dif:"facil",
        opts:["A coroação de D. Pedro","A declaração formal de independência às margens do rio Ipiranga","A batalha final","A assinatura do tratado"],
        resp:1, exp:"D. Pedro I declarou a independência às margens do Rio Ipiranga, em São Paulo." },
      { id:"q274", tema:"8indbr", ano:"8º Ano", pergunta:"As Cortes Portuguesas (1820) exigiam:", dif:"dificil",
        opts:["Independência do Brasil","Volta de D. João VI e recolonização do Brasil","Aliança com a Inglaterra","Fim da monarquia"],
        resp:1, exp:"As Cortes exigiram o retorno de D. João VI a Portugal e tentaram recolonizar o Brasil." },
      { id:"q275", tema:"8indbr", ano:"8º Ano", pergunta:"D. João VI voltou a Portugal em 1821 devido:", dif:"medio",
        opts:["Guerra na Europa","Pressão das Cortes Portuguesas que exigiam seu retorno","Doença","Invasão francesa"],
        resp:1, exp:"As Cortes portuguesas exigiram o retorno de D. João VI para limitar seu poder e recolonizar o Brasil." },

      // Independências (EUA/Haiti) (tinha 4)
      { id:"q276", tema:"8indep", ano:"8º Ano", pergunta:"A Declaração de Independência dos EUA foi redigida por:", dif:"facil",
        opts:["George Washington","Thomas Jefferson","Benjamin Franklin","John Adams"],
        resp:1, exp:"Thomas Jefferson redigiu a Declaração de Independência, proclamada em 4 de julho de 1776." },
      { id:"q277", tema:"8indep", ano:"8º Ano", pergunta:"A Guerra de Independência dos EUA contou com ajuda de:", dif:"medio",
        opts:["Inglaterra","França e Espanha","Alemanha","Rússia"],
        resp:1, exp:"A França e a Espanha apoiaram os colonos americanos contra a Inglaterra na Guerra de Independência." },

      // ── NOVAS PERGUNTAS 9º ANO (temas com deficit) ──

      // Brasil na 2ª Guerra (tinha 1)
      { id:"q278", tema:"9brasil2gm", ano:"9º Ano", pergunta:"Navios mercantes brasileiros foram torpedeados por submarinos alemães em:", dif:"facil",
        opts:["1939","1941","1942","1944"],
        resp:2, exp:"O torpedeamento de navios brasileiros em 1942 levou o Brasil a declarar guerra ao Eixo." },
      { id:"q279", tema:"9brasil2gm", ano:"9º Ano", pergunta:"A FEB lutou ao lado dos Aliados na campanha da:", dif:"facil",
        opts:["França","Itália (Monte Castello, Castelnuovo)","Alemanha","Inglaterra"],
        resp:1, exp:"A Força Expedicionária Brasileira lutou na Itália, participando de batalhas como Monte Castello." },
      { id:"q280", tema:"9brasil2gm", ano:"9º Ano", pergunta:"Os pracinhas da FEB eram:", dif:"medio",
        opts:["Oficiais alemães","Soldados brasileiros que lutaram na 2ª Guerra","Civis convocados","Médicos voluntários"],
        resp:1, exp:"'Pracinhas' era o nome popular dos soldados brasileiros que lutaram na Itália durante a 2ª Guerra." },
      { id:"q281", tema:"9brasil2gm", ano:"9º Ano", pergunta:"A base aérea de Natal foi importante na 2ª Guerra porque:", dif:"dificil",
        opts:["Abastecia navios","Servia como base para voos dos Aliados para o Norte da África e Europa","Era quartel-general","Produzia armas"],
        resp:1, exp:"A Base de Natal (RN) foi fundamental para o transporte aéreo dos Aliados entre América e África durante a guerra." },

      // Fim do Estado Novo (tinha 1)
      { id:"q282", tema:"9fimestnovo", ano:"9º Ano", pergunta:"Vargas foi deposto em 1945 por:", dif:"medio",
        opts:["Revolta popular","Golpe militar (Forças Armadas)","Eleições","Greve geral"],
        resp:1, exp:"Vargas foi deposto pelos militares em 29 de outubro de 1945, encerrando o Estado Novo." },
      { id:"q283", tema:"9fimestnovo", ano:"9º Ano", pergunta:"A Constituição de 1946 foi promulgada durante o governo de:", dif:"medio",
        opts:["Vargas","Dutra","Gaspar Dutra","JK"],
        resp:1, exp:"Eurico Gaspar Dutra foi o primeiro presidente eleito após o Estado Novo, e promulgou a Constituição de 1946." },
      { id:"q284", tema:"9fimestnovo", ano:"9º Ano", pergunta:"O queremismo (1945) foi um movimento popular que defendia:", dif:"dificil",
        opts:["A saída de Vargas","A permanência de Vargas no poder ('Queremos Getúlio')","Eleições imediatas","Impeachment"],
        resp:1, exp:"O queremismo foi um movimento popular que pedia a permanência de Vargas no poder em 1945." },

      // Crise de 1930 (tinha 3)
      { id:"q285", tema:"9crise30", ano:"9º Ano", pergunta:"A Aliança Liberal foi a coligação que apoiou a candidatura de:", dif:"dificil",
        opts:["Washington Luís","Getúlio Vargas em 1930","Júlio Prestes","Luís Carlos Prestes"],
        resp:1, exp:"A Aliança Liberal (1929) uniu oposições de MG, RS e PB em apoio à candidatura de Getúlio Vargas." },
      { id:"q286", tema:"9crise30", ano:"9º Ano", pergunta:"O tenentismo foi um movimento de:", dif:"medio",
        opts:["Oficiais do Exército que exigiam reformas políticas e sociais","Grandes fazendeiros","Operários","Políticos civis"],
        resp:0, exp:"O tenentismo (1920s) foi um movimento de jovens oficiais do Exército que criticava a República Velha e exigia reformas." },
      { id:"q287", tema:"9crise30", ano:"9º Ano", pergunta:"A Coluna Prestes (1925-1927) foi:", dif:"medio",
        opts:["Uma revolta militar vitoriosa","Uma marcha de militares tenentistas pelo interior do Brasil","Uma greve operária","Um partido político"],
        resp:1, exp:"A Coluna Prestes percorreu o interior do Brasil pregando reformas e denunciando as oligarquias." },

      // Entre Guerras / 1929 (tinha 3)
      { id:"q288", tema:"9entreguer", ano:"9º Ano", pergunta:"A Semana de Arte Moderna (1922) no Brasil foi:", dif:"facil",
        opts:["Um evento político","Um movimento cultural que renovou a arte brasileira","Uma revolta","Uma feira comercial"],
        resp:1, exp:"A Semana de 22 foi um marco do Modernismo brasileiro, buscando uma arte autêntica e nacional." },
      { id:"q289", tema:"9entreguer", ano:"9º Ano", pergunta:"O cangaço no Nordeste brasileiro foi um fenômeno de:", dif:"medio",
        opts:["Revolta política organizada","Banditismo social liderado por figuras como Lampião","Movimento religioso","Reforma agrária"],
        resp:1, ext:"O cangaço foi um fenômeno de banditismo social no sertão nordestino, com líderes como Lampião e Maria Bonita." },

      // Sociedade Rep. Velha (tinha 3)
      { id:"q290", tema:"9socrep", ano:"9º Ano", pergunta:"O Rio de Janeiro passou por reformas urbanas no início da República Velha conhecidas como:", dif:"dificil",
        opts:["Reforma Pereira Passos (bota-abaixo)","Plano Piloto","Construção de Brasília","Reforma Agrária"],
        resp:0, exp:"O prefeito Pereira Passos (1902-1906) reformou o Rio, derrubando cortiços e modernizando a cidade." },
      { id:"q291", tema:"9socrep", ano:"9º Ano", pergunta:"A imigração europeia para São Paulo na República Velha visava:", dif:"facil",
        opts:["Povoar o Sul","Substituir mão de obra escrava nas lavouras de café","Explorar o Nordeste","Mineração"],
        resp:1, exp:"A imigração europeia (italianos, espanhóis, alemães) foi incentivada para trabalhar nas fazendas de café." },
      { id:"q292", tema:"9socrep", ano:"9º Ano", pergunta:"Os anarquistas no Brasil da República Velha defendiam:", dif:"dificil",
        opts:["Participação eleitoral","Luta contra o Estado e o capitalismo através de greves e sindicatos","Monarquia","Ditadura"],
        resp:1, exp:"O anarquismo organizou greves operárias e sindicatos, especialmente entre imigrantes em São Paulo." },

      // Descolonização (tinha 4)
      { id:"q293", tema:"9descolon", ano:"9º Ano", pergunta:"A independência da Argélia (1962) foi conquistada após guerra contra:", dif:"medio",
        opts:["Inglaterra","França","Portugal","Espanha"],
        resp:1, exp:"A Argélia lutou uma guerra sangrenta contra a França (1954-1962) para conquistar sua independência." },
      { id:"q294", tema:"9descolon", ano:"9º Ano", pergunta:"Kwame Nkrumah liderou a independência de qual país africano?", dif:"dificil",
        opts:["Nigéria","Gana (antiga Costa do Ouro)","Quênia","África do Sul"],
        resp:1, exp:"Nkrumah liderou Gana à independência em 1957, sendo um dos primeiros países africanos a se libertar do colonialismo." },
      { id:"q295", tema:"9descolon", ano:"9º Ano", pergunta:"A Partilha da África (Conferência de Berlim, 1885) dividiu o continente ignorando:", dif:"facil",
        opts:["Recursos naturais","Fronteiras étnicas e culturais pré-existentes","Clima","Relevo"],
        resp:1, exp:"As fronteiras coloniais ignoraram divisões étnicas e culturais, gerando conflitos após as independências." },

      // Holocausto (tinha 4)
      { id:"q296", tema:"9holoc", ano:"9º Ano", pergunta:"O campo de Auschwitz-Birkenau foi o maior campo de:", dif:"facil",
        opts:["Trabalho","Extermínio nazista","Prisão política","Treinamento militar"],
        resp:1, exp:"Auschwitz-Birkenau (Polônia) foi o maior campo de extermínio nazista, onde morreram mais de 1 milhão de pessoas." },
      { id:"q297", tema:"9holoc", ano:"9º Ano", pergunta:"O julgamento de Adolf Eichmann (1961) em Israel foi importante porque:", dif:"dificil",
        opts:["Reabilitou nazistas","Expôs ao mundo a burocracia do Holocausto","Absolveu os culpados","Criou a ONU"],
        resp:1, exp:"O julgamento de Eichmann documentou detalhadamente a 'Solução Final' e educou o mundo sobre o Holocausto." },

      // Pós-1ª Guerra (tinha 4)
      { id:"q298", tema:"9pos1gm", ano:"9º Ano", pergunta:"O mapa da Europa foi redesenhado após a 1ª Guerra com:", dif:"medio",
        opts:["Unificação de países","Criação de novos países (Polônia, Tchecoslováquia, Iugoslávia)","Fim de todas as fronteiras","Apenas mudanças na Alemanha"],
        resp:1, exp:"O Tratado de Versalhes e outros tratados criaram novos países na Europa Central e Oriental." },
      { id:"q299", tema:"9pos1gm", ano:"9º Ano", pergunta:"As reparações de guerra impostas à Alemanha causaram:", dif:"medio",
        opts:["Prosperidade","Hiperinflação, crise econômica e ressentimento na Alemanha","Estabilidade política","Fortalecimento da democracia"],
        resp:1, exp:"As indenizações bilionárias contribuíram para a hiperinflação alemã (1923) e o descontentamento que alimentou o nazismo." },

      // Primeira República (tinha 4)
      { id:"q300", tema:"9primeira", ano:"9º Ano", pergunta:"O ciclo da borracha na Amazônia (1879-1912) enriqueceu a região com:", dif:"facil",
        opts:["Mineração","Extração de látex para produção de borracha","Pecuária","Agricultura"],
        resp:1, exp:"A borracha extraída da seringueira foi essencial para a indústria automobilística, enriquecendo a Amazônia." },
      { id:"q301", tema:"9primeira", ano:"9º Ano", pergunta:"O Messianismo no Brasil da República Velha (Canudos, Contestado) expressava:", dif:"dificil",
        opts:["Apoio ao governo","Revolta social com liderança religiosa contra a miséria e o abandono","Movimento político","Reforma agrária"],
        resp:1, exp:"Líderes messiânicos como Antônio Conselheiro e José Maria organizaram comunidades de excluídos contra o Estado." },

      // Revoltas (tinha 4)
      { id:"q302", tema:"9revoltas", ano:"9º Ano", pergunta:"A Revolta dos 18 do Forte de Copacabana (1922) foi:", dif:"dificil",
        opts:["Revolta monarquista","Primeiro levante tenentista contra o governo republicano","Greve operária","Revolta abolicionista"],
        resp:1, exp:"O Forte de Copacabana foi o primeiro levante tenentista, marcando o início dos movimentos militares contra a República Velha." },
      { id:"q303", tema:"9revoltas", ano:"9º Ano", pergunta:"A Greve Geral de 1917 em São Paulo foi:", dif:"medio",
        opts:["Greve de estudantes","Paralisação operária por melhores condições de trabalho","Greve de funcionários públicos","Movimento camponês"],
        resp:1, exp:"A Greve Geral de 1917 foi a maior greve operária do período, com dezenas de milhares de trabalhadores paralisando São Paulo." },

      // ── MAIS PERGUNTAS 8º ANO ──

      // Abolicionismo (tinha 5, adicionar 2)
      { id:"q304", tema:"8abolic", ano:"8º Ano", pergunta:"Luís Gama foi um importante abolicionista que:", dif:"dificil",
        opts:["Era ministro","Atuou como advogado na defesa de escravizados e denunciou a escravidão","Era senador","Liderou revoltas"],
        resp:1, exp:"Luís Gama, ex-escravizado, tornou-se advogado e atuou na defesa legal de escravizados." },
      { id:"q305", tema:"8abolic", ano:"8º Ano", pergunta:"Joaquim Nabuco foi líder do movimento abolicionista e escreveu:", dif:"medio",
        opts:["'Casa-Grande & Senzala'","'O Abolicionismo' (1883)","'Os Sertões'","'O Cortiço'"],
        resp:1, exp:"Joaquim Nabuco escreveu 'O Abolicionismo' (1883), obra fundamental na luta contra a escravidão." },

      // Período Regencial (tinha 5, adicionar 2)
      { id:"q306", tema:"8regencia", ano:"8º Ano", pergunta:"A Balaiada (1838-1841) foi uma revolta popular no:", dif:"facil",
        opts:["Maranhão","Pará","Rio Grande do Sul","Bahia"],
        resp:0, exp:"A Balaiada foi uma revolta popular no Maranhão, com participação de vaqueiros, artesãos e escravizados." },
      { id:"q307", tema:"8regencia", ano:"8º Ano", pergunta:"O Padre Diogo Feijó foi um dos regentes que defendia:", dif:"dificil",
        opts:["Volta de D. Pedro I","Reformas liberais e descentralização do poder","Monarquia absoluta","Independência de São Paulo"],
        resp:1, exp:"Feijó (Regente 1835-1837) defendia reformas liberais e mais autonomia para as províncias." },

      // Segundo Reinado (tinha 5, adicionar 2)
      { id:"q308", tema:"8segundo", ano:"8º Ano", pergunta:"A imigração europeia para o Brasil no Segundo Reinado foi subsidiada por:", dif:"facil",
        opts:["Inglaterra","Governo brasileiro (para substituir escravos nas lavouras)","Portugal","Espanha"],
        resp:1, exp:"O governo brasileiro financiou a vinda de imigrantes europeus para trabalhar nas lavouras de café." },
      { id:"q309", tema:"8segundo", ano:"8º Ano", pergunta:"A Guerra do Paraguai terminou com a vitória da Tríplice Aliança e:", dif:"medio",
        opts:["Anexação do Paraguai","Destruição do Paraguai e morte de Solano López","Independência do Paraguai","Paz duradoura"],
        resp:1, exp:"A guerra devastou o Paraguai, que perdeu grande parte de sua população masculina." },

      // ── MAIS PERGUNTAS 9º ANO ──

      // Nova República (tinha 5, adicionar 2)
      { id:"q310", tema:"9novarepub", ano:"9º Ano", pergunta:"O governo Fernando Henrique Cardoso (1995-2002) foi marcado por:", dif:"medio",
        opts:["Estatizações","Privatizações, Plano Real e estabilidade econômica","Reformas socialistas","Ditadura"],
        resp:1, exp:"O governo FHC consolidou o Plano Real, privatizou estatais e atraiu investimentos externos." },
      { id:"q311", tema:"9novarepub", ano:"9º Ano", pergunta:"O Mensalão foi um escândalo político do governo:", dif:"facil",
        opts:["FHC","Lula (denunciado em 2005)","Dilma","Collor"],
        resp:1, exp:"O Mensalão (2005) foi um esquema de compra de votos no Congresso denunciado durante o governo Lula." },
"""

if __name__ == "__main__":
    import re
    import sys

    html_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "/home/flavio/OpenManus/quiz_historico.html"
    )

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Insert new questions before the closing ]; of PERGUNTAS
    target = "    ];\n\n    // ─── Conquistas"
    new_content = content.replace(
        target, NOVAS_PERGUNTAS + "    ];\n\n    // ─── Conquistas", 1
    )

    if content == new_content:
        print("ERROR: Could not find insertion point!")
        sys.exit(1)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    q_count = len(re.findall(r'id:"q\d+"', new_content))
    print(f"✅ {q_count} perguntas totais no arquivo!")
    print(
        f"   Inseridas {len(re.findall(r'id:"q\d+"', NOVAS_PERGUNTAS))} novas perguntas"
    )
