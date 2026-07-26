#!/usr/bin/env python3
"""Gera 150 novas perguntas e insere no quiz_historico.html."""

NOVAS_PERGUNTAS = """
      // ── NOVAS PERGUNTAS 6º ANO ──

      // Introdução à História
      { id:"q108", tema:"6intro", ano:"6º Ano", pergunta:"Qual é a diferença entre história e pré-história?", dif:"facil",
        opts:["Não há diferença","A história começa com a escrita","A pré-história é mais recente","A história estuda o futuro"],
        resp:1, exp:"A história inicia com o surgimento da escrita (c. 3500 a.C.); antes disso é chamado de pré-história." },
      { id:"q109", tema:"6intro", ano:"6º Ano", pergunta:"O que são fontes orais na pesquisa histórica?", dif:"medio",
        opts:["Documentos escritos","Relatos transmitidos pela fala","Objetos de museu","Fósseis"],
        resp:1, exp:"Fontes orais são depoimentos, entrevistas e tradições transmitidas oralmente de geração em geração." },
      { id:"q110", tema:"6intro", ano:"6º Ano", pergunta:"Qual destes NÃO é um tipo de fonte histórica?", dif:"facil",
        opts:["Documentos escritos","Fotografias","Previsões do futuro","Vestígios arqueológicos"],
        resp:2, exp:"Fontes históricas são vestígios do passado, não previsões do futuro." },
      { id:"q111", tema:"6intro", ano:"6º Ano", pergunta:"O que significa periodizar a história?", dif:"medio",
        opts:["Apagar períodos","Dividir o tempo em períodos para estudar","Acelerar o tempo","Criar previsões"],
        resp:1, exp:"Periodizar é dividir o tempo histórico em períodos (Antiga, Medieval, Moderna, Contemporânea) para facilitar o estudo." },

      // Origem da Humanidade
      { id:"q112", tema:"6hum", ano:"6º Ano", pergunta:"Qual espécie do gênero Homo desenvolveu a capacidade de fabricar ferramentas de pedra?", dif:"medio",
        opts:["Homo sapiens","Homo habilis","Homo erectus","Homo neanderthalensis"],
        resp:1, exp:"Homo habilis (2,4-1,4 mi anos) foi o primeiro a fabricar ferramentas de pedra lascada (Olduvaiense)." },
      { id:"q113", tema:"6hum", ano:"6º Ano", pergunta:"Qual a principal diferença entre nomadismo e sedentarismo?", dif:"facil",
        opts:["Nômades plantam, sedentários caçam","Nômades se deslocam constantemente; sedentários fixam-se em um lugar","Não há diferença","Nômades constroem cidades"],
        resp:1, exp:"Nômades deslocam-se seguindo recursos; sedentários fixam-se e praticam agricultura." },
      { id:"q114", tema:"6hum", ano:"6º Ano", pergunta:"A domesticação de animais no Neolítico permitiu:", dif:"medio",
        opts:["Apenas caça","Fonte estável de alimento, transporte e trabalho","Extinção de espécies","Guerras"],
        resp:1, exp:"A domesticação garantiu alimento (carne, leite), transporte e força de trabalho, transformando as sociedades." },

      // África Antiga
      { id:"q115", tema:"6africa", ano:"6º Ano", pergunta:"O Reino de Kush influenciou culturalmente qual civilização?", dif:"medio",
        opts:["Grécia","Roma","Egito","China"],
        resp:2, exp:"Kush foi fortemente influenciado pelo Egito, chegando a governá-lo durante a 25ª Dinastia." },
      { id:"q116", tema:"6africa", ano:"6º Ano", pergunta:"A cidade de Meroé, capital de Kush, era conhecida por:", dif:"dificil",
        opts:["Produção de papiro","Indústria de ferro","Construção naval","Mineração de ouro"],
        resp:1, exp:"Meroé foi um importante centro de produção de ferro na África antiga." },
      { id:"q117", tema:"6africa", ano:"6º Ano", pergunta:"O comércio transaariano conectava:", dif:"medio",
        opts:["África do Sul e Europa","África Ocidental e Norte da África","África Oriental e Ásia","Egito e Mesopotâmia"],
        resp:1, exp:"Rotas transaarianas ligavam o Sahel e a África Ocidental ao Norte da África, trocando ouro, sal e escravos." },

      // Oriente Médio Antigo
      { id:"q118", tema:"6oriente", ano:"6º Ano", pergunta:"A principal contribuição dos fenícios para as civilizações foi:", dif:"facil",
        opts:["A democracia","O alfabeto fonético","A roda","A agricultura"],
        resp:1, exp:"Os fenícios criaram o alfabeto fonético de 22 letras, base dos alfabetos ocidentais." },
      { id:"q119", tema:"6oriente", ano:"6º Ano", pergunta:"O que foi o Zigurate na Mesopotâmia?", dif:"medio",
        opts:["Um tipo de barco","Um templo em forma de torre escalonada","Uma arma de guerra","Um instrumento musical"],
        resp:1, exp:"Zigurates eram templos mesopotâmicos em forma de pirâmide escalonada, dedicados aos deuses." },
      { id:"q120", tema:"6oriente", ano:"6º Ano", pergunta:"Qual povo da Mesopotâmia criou o primeiro império conhecido?", dif:"dificil",
        opts:["Sumérios","Acadianos","Babilônios","Assírios"],
        resp:1, exp:"Sargão da Acádia (c. 2334 a.C.) criou o primeiro império conhecido, unificando cidades-estado sumérias." },
      { id:"q121", tema:"6oriente", ano:"6º Ano", pergunta:"A escrita cuneiforme era feita em qual material?", dif:"facil",
        opts:["Papiro","Pergaminho","Tabletes de argila","Pedra"],
        resp:2, exp:"A escrita cuneiforme era gravada em tabletes de argila com estiletes em forma de cunha." },

      // Pré-Colombianos
      { id:"q122", tema:"6precolomb", ano:"6º Ano", pergunta:"Os astecas fundaram sua capital Tenochtitlán em:", dif:"medio",
        opts:["Uma montanha","Uma ilha no lago Texcoco","Um deserto","Uma floresta"],
        resp:1, exp:"Tenochtitlán foi construída sobre uma ilha no lago Texcoco, atual Cidade do México." },
      { id:"q123", tema:"6precolomb", ano:"6º Ano", pergunta:"O império Inca era governado por um imperador chamado:", dif:"facil",
        opts:["Faraó","Sapa Inca","Cacique","Rei"],
        resp:1, exp:"O imperador inca era chamado Sapa Inca ('filho do Sol'), considerado divino." },
      { id:"q124", tema:"6precolomb", ano:"6º Ano", pergunta:"A economia maia baseava-se principalmente em:", dif:"medio",
        opts:["Pecuária","Mineração","Agricultura (milho, feijão, abóbora)","Comércio marítimo"],
        resp:2, exp:"A base da economia maia era a agricultura, especialmente milho, feijão e abóbora." },
      { id:"q125", tema:"6precolomb", ano:"6º Ano", pergunta:"Qual destas NÃO era uma civilização pré-colombiana?", dif:"facil",
        opts:["Inca","Maia","Asteca","Romana"],
        resp:3, exp:"A civilização romana é europeia, não pré-colombiana." },

      // Povos Originários do Brasil
      { id:"q126", tema:"6origbr", ano:"6º Ano", pergunta:"Qual era a principal atividade econômica dos tupis?", dif:"facil",
        opts:["Mineração","Agricultura (mandioca, milho)","Pecuária","Comércio"],
        resp:1, exp:"Os tupis praticavam agricultura de subsistência, cultivando mandioca, milho, feijão e batata-doce." },
      { id:"q127", tema:"6origbr", ano:"6º Ano", pergunta:"O que era a 'maloca' para os povos indígenas?", dif:"facil",
        opts:["Um tipo de arma","A grande casa coletiva","Uma canoa","Um ritual"],
        resp:1, exp:"Maloca era a grande habitação coletiva onde várias famílias viviam juntas." },
      { id:"q128", tema:"6origbr", ano:"6º Ano", pergunta:"Os povos Jê (Tapuia) habitavam principalmente:", dif:"dificil",
        opts:["Litoral","Amazônia","Planalto Central","Pampas"],
        resp:2, exp:"Os Jê ocupavam o Planalto Central brasileiro, regiões de cerrado." },
      { id:"q129", tema:"6origbr", ano:"6º Ano", pergunta:"Qual destes instrumentos os indígenas usavam para plantar?", dif:"facil",
        opts:["Arado","Enxada de metal","Covão (pau de cavar)","Trator"],
        resp:2, exp:"O pau de cavar era o principal instrumento agrícola dos povos indígenas, usado para fazer buracos na terra para plantar." },

      // Grécia Antiga
      { id:"q130", tema:"6grecia", ano:"6º Ano", pergunta:"O teatro grego originou-se de festivais em homenagem a qual deus?", dif:"dificil",
        opts:["Zeus","Apolo","Dionísio","Atena"],
        resp:2, exp:"O teatro grego surgiu das festividades em homenagem a Dionísio, deus do vinho e do teatro." },
      { id:"q131", tema:"6grecia", ano:"6º Ano", pergunta:"Qual filósofo grego foi condenado a beber cicuta?", dif:"medio",
        opts:["Platão","Aristóteles","Sócrates","Pitágoras"],
        resp:2, exp:"Sócrates foi condenado à morte por 'corromper a juventude' e introduzir novos deuses." },
      { id:"q132", tema:"6grecia", ano:"6º Ano", pergunta:"A Guerra do Peloponeso foi entre:", dif:"medio",
        opts:["Grécia e Pérsia","Atenas e Esparta","Roma e Cartago","Macedônia e Grécia"],
        resp:1, exp:"A Guerra do Peloponeso (431-404 a.C.) foi o conflito entre Atenas e Esparta pela hegemonia grega." },
      { id:"q133", tema:"6grecia", ano:"6º Ano", pergunta:"Alexandre, o Grande, foi discípulo de qual filósofo?", dif:"facil",
        opts:["Sócrates","Platão","Aristóteles","Pitágoras"],
        resp:2, exp:"Alexandre foi educado por Aristóteles, que lhe ensinou filosofia, ciência e política." },

      // Roma Antiga
      { id:"q134", tema:"6roma", ano:"6º Ano", pergunta:"Júlio César foi assassinado no Senado romano em:", dif:"medio",
        opts:["44 a.C.","27 a.C.","14 d.C.","64 d.C."],
        resp:0, exp:"Júlio César foi assassinado em 44 a.C. por senadores republicanos liderados por Brutus." },
      { id:"q135", tema:"6roma", ano:"6º Ano", pergunta:"Os gladiadores romanos eram:", dif:"facil",
        opts:["Soldados profissionais","Escravos que lutavam em espetáculos públicos","Senadores","Sacerdotes"],
        resp:1, exp:"Gladiadores eram geralmente escravos ou prisioneiros que lutavam até a morte em arenas como o Coliseu." },
      { id:"q136", tema:"6roma", ano:"6º Ano", pergunta:"O Cristianismo tornou-se religião oficial do Império Romano sob qual imperador?", dif:"dificil",
        opts:["Nero","Constantino","Teodósio","Augusto"],
        resp:2, exp:"O imperador Teodósio tornou o Cristianismo religião oficial do Império Romano em 380 d.C. (Édito de Tessalônica)." },
      { id:"q137", tema:"6roma", ano:"6º Ano", pergunta:"As lutas entre patrícios e plebeus em Roma resultaram em:", dif:"medio",
        opts:["Fim da república","Conquista de direitos para os plebeus","Expulsão dos patrícios","Escravidão dos plebeus"],
        resp:1, exp:"As lutas levaram à criação do Tribuno da Plebe e à Lei das Doze Tábuas (450 a.C.), conquistando direitos." },

      // Crise do Império Romano
      { id:"q138", tema:"6crise", ano:"6º Ano", pergunta:"O imperador Constantino fundou qual cidade como segunda capital romana?", dif:"facil",
        opts:["Roma","Constantinopla","Alexandria","Tróia"],
        resp:1, exp:"Constantino fundou Constantinopla (330 d.C.) sobre a antiga Bizâncio, capital do Império Romano do Oriente." },
      { id:"q139", tema:"6crise", ano:"6º Ano", pergunta:"Os hunos, liderados por Átila, eram um povo:", dif:"medio",
        opts:["Germânico","Mongol de origem nômade","Eslavo","Celta"],
        resp:1, exp:"Os hunos eram um povo nômade da Ásia Central que invadiu a Europa no séc. V." },
      { id:"q140", tema:"6crise", ano:"6º Ano", pergunta:"O Império Romano do Ocidente caiu em qual ano?", dif:"facil",
        opts:["395 d.C.","410 d.C.","476 d.C.","568 d.C."],
        resp:2, exp:"O Império Romano do Ocidente caiu em 476 d.C. quando o último imperador, Rômulo Augusto, foi deposto." },

      // Reinos Africanos
      { id:"q141", tema:"6africa2", ano:"6º Ano", pergunta:"O Grande Zimbábue foi uma importante civilização africana conhecida por:", dif:"dificil",
        opts:["Suas pirâmides","Suas construções de pedra sem argamassa","Seus templos subterrâneos","Suas estátuas gigantes"],
        resp:1, exp:"O Grande Zimbábue (séc. XI-XV) construiu impressionantes estruturas de pedra sem uso de argamassa." },
      { id:"q142", tema:"6africa2", ano:"6º Ano", pergunta:"O Reino de Songai sucedeu qual império na África Ocidental?", dif:"dificil",
        opts:["Gana","Mali","Axum","Cuxe"],
        resp:1, exp:"Songai (séc. XV-XVI) tornou-se o maior império da África Ocidental, sucedendo o Império do Mali." },

      // ── NOVAS PERGUNTAS 7º ANO ──

      // Crise do Feudalismo
      { id:"q143", tema:"7feudo", ano:"7º Ano", pergunta:"A relação de suserania e vassalagem no feudalismo baseava-se em:", dif:"medio",
        opts:["Compra e venda de terras","Lealdade pessoal e troca de feudos","Parentesco sanguíneo","Eleições"],
        resp:1, exp:"Suserano concedia terras (feudo) ao vassalo em troca de lealdade, serviço militar e conselhos." },
      { id:"q144", tema:"7feudo", ano:"7º Ano", pergunta:"A Guerra dos Cem Anos (1337-1453) foi entre:", dif:"facil",
        opts:["Inglaterra e Espanha","França e Inglaterra","Alemanha e Itália","Portugal e França"],
        resp:1, exp:"A Guerra dos Cem Anos foi o conflito entre França e Inglaterra pelo trono francês." },
      { id:"q145", tema:"7feudo", ano:"7º Ano", pergunta:"Joana D'Arc foi uma camponesa que liderou tropas francesas durante:", dif:"facil",
        opts:["Guerra dos Cem Anos","Guerra dos Trinta Anos","Cruzadas","Revolução Francesa"],
        resp:0, exp:"Joana D'Arc liderou tropas francesas contra os ingleses na Guerra dos Cem Anos." },
      { id:"q146", tema:"7feudo", ano:"7º Ano", pergunta:"O movimento das Cruzadas teve como consequência:", dif:"dificil",
        opts:["Enfraquecimento do comércio","Reabertura do Mediterrâneo e reavivamento comercial","Fim da religião cristã","Isolamento da Europa"],
        resp:1, exp:"As Cruzadas reabriram o Mediterrâneo ao comércio europeu, revitalizando rotas comerciais com o Oriente." },

      // Grandes Navegações
      { id:"q147", tema:"7naveg", ano:"7º Ano", pergunta:"Vasco da Gama chegou às Índias em:", dif:"facil",
        opts:["1488","1492","1498","1500"],
        resp:2, exp:"Vasco da Gama chegou a Calicute, Índia, em 1498, estabelecendo a rota marítima para as Índias." },
      { id:"q148", tema:"7naveg", ano:"7º Ano", pergunta:"Fernão de Magalhães liderou a primeira expedição a:", dif:"medio",
        opts:["Chegar à Índia","Circunavegar o globo","Descobrir o Brasil","Chegar à América"],
        resp:1, exp:"A expedição de Magalhães-Elcano (1519-1522) completou a primeira circum-navegação do globo." },
      { id:"q149", tema:"7naveg", ano:"7º Ano", pergunta:"O que motivou os europeus a buscarem uma rota marítima para as Índias?", dif:"medio",
        opts:["Curiosidade científica","Bloqueio das rotas terrestres pelos turcos e necessidade de especiarias","Busca de novas religiões","Fuga de perseguições"],
        resp:1, exp:"A queda de Constantinopla (1453) bloqueou as rotas terrestres, levando à busca de uma rota marítima para as Índias." },
      { id:"q150", tema:"7naveg", ano:"7º Ano", pergunta:"A Escola de Sagres, em Portugal, foi importante para:", dif:"dificil",
        opts:["Formar padres","Desenvolver técnicas de navegação","Produzir armas","Criar leis"],
        resp:1, exp:"A Escola de Sagres (séc. XV) foi um centro de estudos náuticos que desenvolveu técnicas avançadas de navegação." },

      // Renascimento Cultural
      { id:"q151", tema:"7renas", ano:"7º Ano", pergunta:"A imprensa de Gutenberg (1450) foi revolucionária porque:", dif:"medio",
        opts:["Imprimia apenas imagens","Permitiu a produção em massa de livros, difundindo conhecimento","Era mais cara que os manuscritos","Impressionava apenas a nobreza"],
        resp:1, exp:"A imprensa de tipos móveis barateou e acelerou a produção de livros, difundindo ideias renascentistas e científicas." },
      { id:"q152", tema:"7renas", ano:"7º Ano", pergunta:"Michelangelo esculpiu qual famosa obra renascentista?", dif:"facil",
        opts:["Mona Lisa","Davi","A Primavera","Escola de Atenas"],
        resp:1, exp:"Michelangelo esculpiu o Davi (1504), símbolo do Renascimento florentino." },
      { id:"q153", tema:"7renas", ano:"7º Ano", pergunta:"A pintura 'A Escola de Atenas' de Rafael retrata:", dif:"dificil",
        opts:["Uma escola medieval","Filósofos gregos como Platão e Aristóteles","Uma batalha","A corte de Luís XIV"],
        resp:1, exp:"'A Escola de Atenas' (1511) reúne filósofos da Grécia Antiga, simbolizando o humanismo renascentista." },
      { id:"q154", tema:"7renas", ano:"7º Ano", pergunta:"Quem escreveu 'O Príncipe', obra sobre política e poder?", dif:"facil",
        opts:["Erasmo de Roterdã","Maquiavel","Thomas Morus","Cervantes"],
        resp:1, exp:"Nicolau Maquiavel escreveu 'O Príncipe' (1513), analisando como conquistar e manter o poder político." },

      // Saberes Africanos e Pré-Colombianos
      { id:"q155", tema:"7saberes", ano:"7º Ano", pergunta:"Os conhecimentos astronômicos maias permitiam:", dif:"facil",
        opts:["Prever o tempo","Criar calendários precisos","Navegar nos oceanos","Construir máquinas"],
        resp:1, exp:"Os maias criaram um calendário solar de 365 dias e um calendário ritual de 260 dias." },
      { id:"q156", tema:"7saberes", ano:"7º Ano", pergunta:"A medicina tradicional africana utilizava:", dif:"medio",
        opts:["Apenas cirurgia","Plantas medicinais, rituais e conhecimentos empíricos","Máquinas avançadas","Apenas rezas"],
        resp:1, exp:"A medicina africana combinava conhecimento empírico de plantas medicinais com práticas espirituais." },

      // Absolutismo
      { id:"q157", tema:"7absol", ano:"7º Ano", pergunta:"Luís XIV, o 'Rei Sol', governou qual país?", dif:"facil",
        opts:["Inglaterra","Espanha","França","Portugal"],
        resp:2, exp:"Luís XIV governou a França de 1643 a 1715, símbolo máximo do absolutismo monárquico." },
      { id:"q158", tema:"7absol", ano:"7º Ano", pergunta:"O palácio de Versalhes foi construído por Luís XIV para:", dif:"medio",
        opts:["Proteger-se de invasões","Centralizar a nobreza e demonstrar poder","Servir como mosteiro","Abrigar o parlamento"],
        resp:1, exp:"Versalhes centralizou a nobreza francesa na corte, permitindo que o rei a controlasse." },
      { id:"q159", tema:"7absol", ano:"7º Ano", pergunta:"Qual teórico defendeu a origem divina do poder real?", dif:"dificil",
        opts:["Hobbes","Bossuet","Locke","Voltaire"],
        resp:1, exp:"Bossuet defendia o Direito Divino dos Reis, teoria segundo a qual o poder real vinha diretamente de Deus." },

      // Conquista da América
      { id:"q160", tema:"7conq", ano:"7º Ano", pergunta:"Qual povo indígena ajudou Cortés a derrotar os astecas?", dif:"dificil",
        opts:["Incas","Tlaxcaltecas","Tupis","Maias"],
        resp:1, exp:"Os tlaxcaltecas, inimigos dos astecas, aliaram-se a Cortés e foram cruciais para a conquista." },
      { id:"q161", tema:"7conq", ano:"7º Ano", pergunta:"O imperador inca Atahualpa foi executado por:", dif:"facil",
        opts:["Cortés","Pizarro","Colombo","Cabral"],
        resp:1, exp:"Pizarro capturou e executou Atahualpa em 1533, após cobrar um resgate em ouro." },
      { id:"q162", tema:"7conq", ano:"7º Ano", pergunta:"A 'Leyenda Negra' sobre a colonização espanhola refere-se:", dif:"dificil",
        opts:["À riqueza das colônias","Às denúncias de violência e exploração contra os indígenas","Às navegações","Às leis coloniais"],
        resp:1, exp:"A Leyenda Negra foi a difusão de denúncias sobre as violências cometidas pelos espanhóis contra os povos americanos." },

      // Escravidão Moderna
      { id:"q163", tema:"7escrav", ano:"7º Ano", pergunta:"O tráfico negreiro para o Brasil começou por volta de:", dif:"medio",
        opts:["1500","1550","1600","1700"],
        resp:1, exp:"O tráfico negreiro intensificou-se a partir de meados do séc. XVI com a instalação dos engenhos de açúcar." },
      { id:"q164", tema:"7escrav", ano:"7º Ano", pergunta:"O quilombo de Palmares foi liderado por:", dif:"facil",
        opts:["Zumbi e Ganga Zumba","Tiradentes","Lampião","Antônio Conselheiro"],
        resp:0, exp:"Palmares, o maior quilombo do Brasil, foi liderado por Ganga Zumba e depois por Zumbi." },

      // Reforma e Contrarreforma
      { id:"q165", tema:"7reform", ano:"7º Ano", pergunta:"João Calvino defendia a doutrina da:", dif:"medio",
        opts:["Salvação pelas obras","Predestinação","Salvação universal","Livre-arbítrio"],
        resp:1, exp:"Calvino defendia a predestinação: Deus já teria escolhido quem seria salvo ou condenado." },
      { id:"q166", tema:"7reform", ano:"7º Ano", pergunta:"Henrique VIII rompeu com a Igreja Católica para:", dif:"facil",
        opts:["Tornar-se protestante","Anular seu casamento e criar a Igreja Anglicana","Apoiar Lutero","Fundar uma nova religião"],
        resp:1, exp:"Henrique VIII criou a Igreja Anglicana (1534) quando o papa recusou anular seu casamento com Catarina de Aragão." },
      { id:"q167", tema:"7reform", ano:"7º Ano", pergunta:"O Concílio de Trento (1545-1563) foi a resposta católica à Reforma, conhecida como:", dif:"facil",
        opts:["Reforma Católica","Contrarreforma","Reforma Anglicana","Cisma do Ocidente"],
        resp:1, exp:"O Concílio de Trento reafirmou dogmas católicos e iniciou reformas na Igreja (Contrarreforma)." },
      { id:"q168", tema:"7reform", ano:"7º Ano", pergunta:"O Index Librorum Prohibitorum era:", dif:"dificil",
        opts:["Uma lista de livros sagrados","Uma lista de livros proibidos pela Igreja Católica","Um código de leis","Um manual de inquisição"],
        resp:1, exp:"O Index (1559) era a lista de livros proibidos pela Igreja, parte da Contrarreforma." },

      // Comércio Atlântico
      { id:"q169", tema:"7comercio", ano:"7º Ano", pergunta:"O comércio triangular no Atlântico envolvia:", dif:"medio",
        opts:["Europa, África e Américas","Europa, Ásia e África","Américas, Ásia e Europa","Apenas Europa e América"],
        resp:0, exp:"O comércio triangular conectava: Europa (manufaturas) -> África (escravizados) -> Américas (açúcar, tabaco)." },

      // Colonização Portuguesa
      { id:"q170", tema:"7colonias", ano:"7º Ano", pergunta:"O pau-brasil era usado pelos portugueses para:", dif:"facil",
        opts:["Construção naval","Extrair tinta vermelha para tingir tecidos","Alimentação","Medicina"],
        resp:1, exp:"O pau-brasil fornecia uma tinta vermelha valiosa para tingir tecidos na Europa." },
      { id:"q171", tema:"7colonias", ano:"7º Ano", pergunta:"O sistema de capitanias hereditárias no Brasil foi criado em:", dif:"facil",
        opts:["1500","1534","1549","1580"],
        resp:1, exp:"O sistema de capitanias hereditárias foi implantado em 1534 para efetivar a colonização do Brasil." },
      { id:"q172", tema:"7colonias", ano:"7º Ano", pergunta:"O Governo-Geral foi criado em 1549 para:", dif:"medio",
        opts:["Abolir as capitanias","Centralizar a administração colonial","Aumentar impostos","Independência do Brasil"],
        resp:1, exp:"O Governo-Geral, com sede em Salvador, visava centralizar e coordenar a administração colonial." },

      // ── NOVAS PERGUNTAS 8º ANO ──

      // Iluminismo
      { id:"q173", tema:"8ilumin", ano:"8º Ano", pergunta:"Voltaire ficou famoso por defender:", dif:"medio",
        opts:["Monarquia absoluta","Liberdade de expressão e tolerância religiosa","Ditadura","Fim da religião"],
        resp:1, exp:"Voltaire defendia a liberdade de pensamento, tolerância religiosa e criticava a Igreja e o Absolutismo." },
      { id:"q174", tema:"8ilumin", ano:"8º Ano", pergunta:"O despotismo esclarecido foi uma tentativa de:", dif:"medio",
        opts:["Fortalecer o poder da Igreja","Conciliar ideias iluministas com a manutenção do absolutismo","Estabelecer a democracia","Abolir a monarquia"],
        resp:1, exp:"Déspotas esclarecidos (como Frederico II e D. Maria I) adotaram reformas iluministas sem abrir mão do poder absoluto." },
      { id:"q175", tema:"8ilumin", ano:"8º Ano", pergunta:"A Enciclopédia de Diderot e d'Alembert buscava:", dif:"dificil",
        opts:["Registrar apenas ciência","Reunir e difundir todo o conhecimento disponível","Ser apenas religiosa","Registrar leis"],
        resp:1, exp:"A Enciclopédia (1751-1772) reuniu artigos de diversos pensadores iluministas sobre ciência, arte e filosofia." },

      // Revolução Industrial
      { id:"q176", tema:"8revol", ano:"8º Ano", pergunta:"O que era o sistema putting-out na Revolução Industrial?", dif:"dificil",
        opts:["Trabalho em fábricas","Trabalho doméstico descentralizado antes das fábricas","Sistema de transportes","Greve operária"],
        resp:1, exp:"No putting-out, comerciantes entregavam matéria-prima para artesãos produzirem em casa." },
      { id:"q177", tema:"8revol", ano:"8º Ano", pergunta:"O cartismo foi um movimento operário que exigia:", dif:"dificil",
        opts:["Fim da industrialização","Reformas políticas como voto universal masculino","Aumento da jornada","Retorno ao artesanato"],
        resp:1, exp:"O cartismo (1838-1848) reivindicava reformas políticas como o sufrágio universal masculino e o voto secreto." },
      { id:"q178", tema:"8revol", ano:"8º Ano", pergunta:"A produção em série (fordismo) foi introduzida por:", dif:"facil",
        opts:["Henry Ford","James Watt","Karl Marx","Adam Smith"],
        resp:0, exp:"Henry Ford implementou a linha de montagem para produção em série de automóveis, reduzindo custos." },

      // Rev. Francesa e Napoleão
      { id:"q179", tema:"8fran", ano:"8º Ano", pergunta:"Os Três Estados na França pré-revolucionária eram:", dif:"facil",
        opts:["Nobreza, Clero e Povo","Rei, Nobreza e Burguesia","Católicos, Protestantes e Judeus","Ricos, Médios e Pobres"],
        resp:0, exp:"O Primeiro Estado (clero), Segundo (nobreza) e Terceiro (povo + burguesia) formavam a sociedade estamental." },
      { id:"q180", tema:"8fran", ano:"8º Ano", pergunta:"O período do Terror (1793-1794) foi liderado por:", dif:"medio",
        opts:["Napoleão","Robespierre","Luís XVI","Danton"],
        resp:1, exp:"Robespierre e os jacobinos lideraram o Terror, executando milhares de 'inimigos da revolução' na guilhotina." },
      { id:"q181", tema:"8fran", ano:"8º Ano", pergunta:"O Bloqueio Continental de Napoleão visava:", dif:"medio",
        opts:["Isolar a França","Impedir o comércio europeu com a Inglaterra","Proteger a economia francesa","Abrir portos brasileiros"],
        resp:1, exp:"O Bloqueio Continental (1806) proibia que países europeus comerciassem com a Inglaterra." },

      // Independências (EUA/Haiti)
      { id:"q182", tema:"8indep", ano:"8º Ano", pergunta:"O lema da Independência dos EUA era:", dif:"facil",
        opts:["Liberdade, Igualdade, Fraternidade","No taxation without representation","Ordem e Progresso","Independência ou Morte"],
        resp:1, exp:"O lema 'No taxation without representation' expressava a revolta contra os impostos britânicos." },
      { id:"q183", tema:"8indep", ano:"8º Ano", pergunta:"Toussaint Louverture foi líder da independência de:", dif:"facil",
        opts:["Estados Unidos","Haiti","Brasil","México"],
        resp:1, exp:"Toussaint Louverture liderou a Revolução Haitiana (1791-1802), a única revolta de escravizados bem-sucedida." },

      // Independência do Brasil
      { id:"q184", tema:"8indbr", ano:"8º Ano", pergunta:"Dom Pedro I foi proclamado imperador do Brasil em:", dif:"facil",
        opts:["1822","1823","1824","1825"],
        resp:0, exp:"Após a independência, D. Pedro foi aclamado imperador do Brasil em 12 de outubro de 1822." },
      { id:"q185", tema:"8indbr", ano:"8º Ano", pergunta:"O Dia do Fico (9 de janeiro de 1822) foi:", dif:"facil",
        opts:["A declaração de independência","A decisão de D. Pedro de permanecer no Brasil","A volta de D. João VI","A proclamação da República"],
        resp:1, exp:"D. Pedro decidiu ficar no Brasil contrariando as Cortes portuguesas, marcando o caminho para a independência." },

      // América Latina
      { id:"q186", tema:"8amerlat", ano:"8º Ano", pergunta:"Simón Bolívar liderou a independência de vários países:", dif:"facil",
        opts:["América do Sul (Colômbia, Venezuela, Equador, etc.)","América Central","México","Brasil"],
        resp:0, exp:"Simón Bolívar libertou Venezuela, Colômbia, Equador, Peru e Bolívia do domínio espanhol." },
      { id:"q187", tema:"8amerlat", ano:"8º Ano", pergunta:"José de San Martín lutou pela independência de:", dif:"medio",
        opts:["México e América Central","Argentina, Chile e Peru","Brasil e Uruguai","Colômbia e Venezuela"],
        resp:1, exp:"San Martín liderou as independências da Argentina (1816), Chile (1818) e Peru (1821)." },

      // Primeiro Reinado
      { id:"q188", tema:"8primeiro", ano:"8º Ano", pergunta:"A Guerra da Cisplatina (1825-1828) resultou em:", dif:"dificil",
        opts:["Anexação do Uruguai ao Brasil","Independência do Uruguai","Derrota argentina","Paz com a Inglaterra"],
        resp:1, exp:"A Guerra da Cisplatina terminou com a independência da Província Cisplatina, formando o Uruguai (1828)." },

      // Período Regencial
      { id:"q189", tema:"8regencia", ano:"8º Ano", pergunta:"A Cabanagem (1835-1840) ocorreu em qual província?", dif:"facil",
        opts:["Maranhão","Pará","Rio Grande do Sul","Bahia"],
        resp:1, exp:"A Cabanagem foi uma revolta popular no Pará, com participação de indígenas, negros e cabanos." },
      { id:"q190", tema:"8regencia", ano:"8º Ano", pergunta:"A Farroupilha (1835-1845) foi uma revolta no:", dif:"facil",
        opts:["Rio Grande do Sul","Pernambuco","Minas Gerais","São Paulo"],
        resp:0, exp:"A Revolução Farroupilha (ou Guerra dos Farrapos) foi uma revolta republicana no Rio Grande do Sul." },
      { id:"q191", tema:"8regencia", ano:"8º Ano", pergunta:"A Sabinada (1837-1838) foi uma revolta em:", dif:"medio",
        opts:["Salvador (BA)","Recife (PE)","São Luís (MA)","Rio de Janeiro"],
        resp:0, exp:"A Sabinada foi uma revolta republicana em Salvador, liderada pelo médico Francisco Sabino." },

      // Segundo Reinado
      { id:"q192", tema:"8segundo", ano:"8º Ano", pergunta:"A Guerra do Paraguai (1864-1870) foi o conflito entre:", dif:"facil",
        opts:["Paraguai e Argentina","Brasil, Argentina, Uruguai vs Paraguai","Brasil e Paraguai apenas","Paraguai e Uruguai"],
        resp:1, exp:"A Guerra do Paraguai foi o maior conflito sul-americano: Tríplice Aliança (Brasil, Argentina, Uruguai) contra o Paraguai." },
      { id:"q193", tema:"8segundo", ano:"8º Ano", pergunta:"A Lei de Terras (1850) estabelecia que terras devolutas só poderiam ser adquiridas por:", dif:"dificil",
        opts:["Doação do governo","Compra","Ocupação","Herança"],
        resp:1, exp:"A Lei de Terras (1850) determinou que terras públicas só poderiam ser compradas, impedindo o acesso de ex-escravizados." },
      { id:"q194", tema:"8segundo", ano:"8º Ano", pergunta:"O Paraguai era governado por Solano López, que:", dif:"medio",
        opts:["Aliou-se ao Brasil","Modernizou o exército e a economia paraguaia","Aboliu a escravatura","Entregou terras à Argentina"],
        resp:1, exp:"Solano López modernizou o Paraguai com ferrovias, indústria e um exército forte, gerando conflitos na região." },

      // Abolicionismo
      { id:"q195", tema:"8abolic", ano:"8º Ano", pergunta:"A Lei Saraiva-Cotegipe (Lei dos Sexagenários, 1885) concedia:", dif:"facil",
        opts:["Liberdade imediata a todos","Liberdade a escravizados com mais de 60 anos","Fim do tráfico","Indenização aos senhores"],
        resp:1, exp:"A Lei dos Sexagenários libertava escravizados com mais de 65 anos (depois 60) mediante indenização." },
      { id:"q196", tema:"8abolic", ano:"8º Ano", pergunta:"O movimento abolicionista contou com a participação de:", dif:"medio",
        opts:["Apenas escravizados","Intelectuais, jornalistas, advogados e ex-escravizados","Apenas políticos","Apenas estrangeiros"],
        resp:1, exp:"O abolicionismo envolveu diversos setores: José do Patrocínio, Joaquim Nabuco, André Rebouças e Luís Gama." },

      // Crise do Império
      { id:"q197", tema:"8criseimp", ano:"8º Ano", pergunta:"A Questão Religiosa (1872-1875) foi um conflito entre:", dif:"dificil",
        opts:["Império e Inglaterra","Igreja Católica e Império (intervenção do Estado)","Império e Argentina","Império e EUA"],
        resp:1, exp:"D. Pedro II prendeu bispos que cumpriram ordens papais (bula Syllabus) desobedecendo leis imperiais." },
      { id:"q198", tema:"8criseimp", ano:"8º Ano", pergunta:"A Questão Militar contribuiu para a queda do Império porque:", dif:"dificil",
        opts:["Militares apoiaram a monarquia","Militares insatisfeitos aderiram à causa republicana","Militares foram presos","Exército foi extinto"],
        resp:1, exp:"A insatisfação dos militares com o governo imperial e sua adesão ao positivismo fortaleceu o movimento republicano." },

      // Imperialismo
      { id:"q199", tema:"8imperial", ano:"8º Ano", pergunta:"A Conferência de Berlim (1884-1885) dividiu:", dif:"facil",
        opts:["A Ásia entre potências","A África entre potências europeias","A América entre Inglaterra e França","A Oceania"],
        resp:1, exp:"A Conferência de Berlim estabeleceu regras para a partilha da África entre as potências europeias." },
      { id:"q200", tema:"8imperial", ano:"8º Ano", pergunta:"O rei Leopoldo II da Bélgica fez do Congo sua propriedade privada, praticando:", dif:"medio",
        opts:["Desenvolvimento sustentável","Violenta exploração de borracha e trabalho forçado","Educação universal","Construção de hospitais"],
        resp:1, exp:"Leopoldo II explorou brutalmente o Congo, matando milhões de congoleses na extração de borracha." },

      // Antecedentes da 1ª Guerra
      { id:"q201", tema:"8ante1gm", ano:"8º Ano", pergunta:"A Tríplice Aliança e a Tríplice Entente eram:", dif:"facil",
        opts:["Alianças comerciais","Blocos militares rivais antes da 1ª Guerra","Tratados de paz","Organizações culturais"],
        resp:1, exp:"Tríplice Aliança (Alemanha, Áustria-Hungria, Itália) e Tríplice Entente (Inglaterra, França, Rússia)." },
      { id:"q202", tema:"8ante1gm", ano:"8º Ano", pergunta:"A corrida armamentista na Europa antes de 1914 foi causada por:", dif:"dificil",
        opts:["Paz duradoura","Nacionalismo, rivalidades imperialistas e alianças militares","Desarmamento geral","Acordos de paz"],
        resp:1, exp:"As potências europeias competiam em armamentos, criando tensões que explodiram na 1ª Guerra." },

      // ── NOVAS PERGUNTAS 9º ANO ──

      // Primeira República
      { id:"q203", tema:"9primeira", ano:"9º Ano", pergunta:"O convênio de Taubaté (1906) foi um acordo para:", dif:"dificil",
        opts:["Industrializar o Brasil","Valorizar o café com compra federal dos excedentes","Exportar açúcar","Construir ferrovias"],
        resp:1, exp:"O Convênio de Taubaté foi um acordo entre estados produtores de café para valorizar o produto comprando excedentes." },
      { id:"q204", tema:"9primeira", ano:"9º Ano", pergunta:"A política do café-com-leite alternava presidentes de:", dif:"facil",
        opts:["São Paulo e Rio de Janeiro","São Paulo e Minas Gerais","Minas e Rio Grande do Sul","Bahia e Pernambuco"],
        resp:1, exp:"O café-com-leite era o acordo entre São Paulo (café) e Minas Gerais (leite) para alternância na presidência." },

      // Sociedade Rep. Velha
      { id:"q205", tema:"9socrep", ano:"9º Ano", pergunta:"O coronelismo na República Velha caracterizava-se por:", dif:"dificil",
        opts:["Governo militar","Controle de votos por grandes fazendeiros (curral eleitoral)","Democracia plena","Voto universal"],
        resp:1, exp:"Coronéis controlavam votos em suas regiões através do poder econômico e da violência (voto de cabresto)." },
      { id:"q206", tema:"9socrep", ano:"9º Ano", pergunta:"O voto de cabresto era:", dif:"facil",
        opts:["Voto secreto","Voto controlado à força pelos coronéis","Voto feminino","Voto universal"],
        resp:1, exp:"O voto de cabresto era a prática dos coronéis de obrigar eleitores a votar em seus candidatos." },

      // Revoltas (Canudos/Contestado)
      { id:"q207", tema:"9revoltas", ano:"9º Ano", pergunta:"A Revolta da Vacina (1904) no Rio de Janeiro foi contra:", dif:"medio",
        opts:["Aumento de impostos","Vacinação obrigatória determinada por Oswaldo Cruz","Mudança de capital","Alistamento militar"],
        resp:1, exp:"A população revoltou-se contra a vacinação obrigatória contra varíola, vista como invasão do Estado." },
      { id:"q208", tema:"9revoltas", ano:"9º Ano", pergunta:"A Revolta da Chibata (1910) foi liderada por:", dif:"medio",
        opts:["Antônio Conselheiro","João Cândido (Marinheiro Negro)","Lampião","Luís Carlos Prestes"],
        resp:1, exp:"João Cândido liderou a revolta de marinheiros contra os castigos físicos (chibatadas) na Marinha brasileira." },

      // Crise de 1930
      { id:"q209", tema:"9crise30", ano:"9º Ano", pergunta:"Getúlio Vargas tornou-se presidente provisório após a Revolução de 1930:", dif:"facil",
        opts:["Por eleições diretas","Liderando um movimento armado que depôs Washington Luís","Por indicação de Júlio Prestes","Por herança"],
        resp:1, exp:"A Revolução de 1930 depôs o presidente Washington Luís e impediu a posse de Júlio Prestes." },

      // Revolução Russa
      { id:"q210", tema:"9revrussa", ano:"9º Ano", pergunta:"O Domingo Sangrento (1905) foi:", dif:"dificil",
        opts:["Uma batalha","Manifestação pacífica reprimida pelo czar","Greve geral","Jornada de 8 horas"],
        resp:1, exp:"O Domingo Sangrento (22/01/1905) foi o massacre de manifestantes pacíficos no Palácio de Inverno." },
      { id:"q211", tema:"9revrussa", ano:"9º Ano", pergunta:"A NEP (Nova Política Econômica) de Lenin permitia:", dif:"dificil",
        opts:["Apenas comércio estatal","Pequena propriedade privada e comércio livre controlado","Capitalismo total","Comunismo de guerra"],
        resp:1, exp:"A NEP (1921) permitiu pequenas empresas privadas e comércio para recuperar a economia russa devastada." },

      // 1ª Guerra (consequências)
      { id:"q212", tema:"9pos1gm", ano:"9º Ano", pergunta:"A Alemanha foi considerada culpada pela 1ª Guerra e obrigada a pagar:", dif:"facil",
        opts:["Indenizações bilionárias (Tratado de Versalhes)","Nada","Apenas danos simbólicos","Territórios apenas"],
        resp:0, exp:"O Tratado de Versalhes (1919) impôs à Alemanha a culpa pela guerra e indenizações de 132 bilhões de marcos." },
      { id:"q213", tema:"9pos1gm", ano:"9º Ano", pergunta:"A 1ª Guerra causou aproximadamente:", dif:"medio",
        opts:["1 milhão de mortos","10 milhões de mortos e 20 milhões de feridos","100 milhões de mortos","500 mil mortos"],
        resp:1, exp:"A 1ª Guerra causou cerca de 10 milhões de mortos e 20 milhões de feridos, sendo uma das guerras mais mortais." },

      // Entre Guerras / 1929
      { id:"q214", tema:"9entreguer", ano:"9º Ano", pergunta:"A Quebra da Bolsa de Nova York (1929) ocorreu em qual dia?", dif:"facil",
        opts:["24 de outubro (Quinta-Feira Negra)","29 de outubro (Terça-Feira Negra)","14 de março","1º de setembro"],
        resp:1, exp:"Em 29 de outubro de 1929 (Terça-Feira Negra), a Bolsa de NY quebrou, iniciando a Grande Depressão." },
      { id:"q215", tema:"9entreguer", ano:"9º Ano", pergunta:"O New Deal de Franklin Roosevelt foi:", dif:"medio",
        opts:["Um plano de guerra","Um conjunto de programas para recuperar a economia dos EUA","Uma aliança militar","Uma reforma agrária"],
        resp:1, exp:"O New Deal (1933) foi um pacote de reformas econômicas e sociais para combater a Grande Depressão." },
      { id:"q216", tema:"9entreguer", ano:"9º Ano", pergunta:"O período entreguerras foi marcado por:", dif:"medio",
        opts:["Paz e prosperidade geral","Crise econômica e ascensão de regimes totalitários","Desarmamento global","União europeia"],
        resp:1, exp:"O período entreguerras combinou a Grande Depressão (1929) com a ascensão do fascismo, nazismo e stalinismo." },

      // Fascismo e Nazismo
      { id:"q217", tema:"9fascismo", ano:"9º Ano", pergunta:"A Marcha sobre Roma (1922) foi:", dif:"dificil",
        opts:["Revolução socialista","Manifestação fascista que levou Mussolini ao poder","Greve geral","Protesto pacífico"],
        resp:1, exp:"A Marcha sobre Roma foi a demonstração de força dos fascistas que resultou na nomeação de Mussolini como primeiro-ministro." },
      { id:"q218", tema:"9fascismo", ano:"9º Ano", pergunta:"As Leis de Nuremberg (1935) na Alemanha nazista:", dif:"medio",
        opts:["Protegiam os judeus","Tiravam direitos civis dos judeus e proibiam casamentos mistos","Estabeleciam a democracia","Criavam campos de concentração"],
        resp:1, exp:"As Leis de Nuremberg excluíram judeus da cidadania alemã e proibiram casamentos entre judeus e não-judeus." },
      { id:"q219", tema:"9fascismo", ano:"9º Ano", pergunta:"A Noite dos Cristais (1938) foi:", dif:"facil",
        opts:["Uma comemoração nazista","Um pogrom contra judeus com destruição de sinagogas e lojas","Um festival cultural","Um tratado de paz"],
        resp:1, exp:"A Kristallnacht (9-10/11/1938) foi um ataque violento contra judeus, lojas e sinagogas na Alemanha." },

      // Era Vargas
      { id:"q220", tema:"9vargas", ano:"9º Ano", pergunta:"Vargas esteve à frente do Brasil em três fases:", dif:"facil",
        opts:["Governo Provisório, Constitucional e Estado Novo","Monarquia e República","Primeira e Segunda República","Ditadura e Democracia"],
        resp:0, exp:"As fases do governo Vargas: Provisório (1930-34), Constitucional (1934-37) e Estado Novo (1937-45)." },
      { id:"q221", tema:"9vargas", ano:"9º Ano", pergunta:"A Intentona Comunista (1935) foi:", dif:"medio",
        opts:["Revolução socialista bem-sucedida","Tentativa de revolta comunista liderada pela ANL e Prestes","Greve operária","Revolta militar"],
        resp:1, exp:"A Intentona Comunista de 1935 foi uma insurreição liderada pela Aliança Nacional Libertadora." },
      { id:"q222", tema:"9vargas", ano:"9º Ano", pergunta:"A FEB (Força Expedicionária Brasileira) lutou na:", dif:"facil",
        opts:["1ª Guerra Mundial","2ª Guerra Mundial (Itália)","Guerra do Paraguai","Guerra Fria"],
        resp:1, exp:"A FEB enviou cerca de 25 mil soldados para lutar na Itália ao lado dos Aliados na 2ª Guerra." },

      // 2ª Guerra Mundial
      { id:"q223", tema:"9segundagm", ano:"9º Ano", pergunta:"O Plano Marshall (1948) foi:", dif:"medio",
        opts:["Um plano militar","Um programa de ajuda econômica dos EUA para reconstruir a Europa","Tratado de paz","Aliança militar"],
        resp:1, exp:"O Plano Marshall investiu cerca de 13 bilhões de dólares na reconstrução da Europa Ocidental pós-guerra." },
      { id:"q224", tema:"9segundagm", ano:"9º Ano", pergunta:"A Batalha de Stalingrado (1942-1943) foi importante porque:", dif:"facil",
        opts:["Foi a primeira vitória alemã","Foi a primeira grande derrota alemã na 2ª Guerra","Não teve importância","Ocorreu no Pacífico"],
        resp:1, exp:"Stalingrado marcou a virada na 2ª Guerra: o Exército Vermelho derrotou os alemães, iniciando a ofensiva soviética." },
      { id:"q225", tema:"9segundagm", ano:"9º Ano", pergunta:"O Tribunal de Nuremberg (1945-1946) julgou:", dif:"facil",
        opts:["Aliados","Criminosos de guerra nazistas","Líderes soviéticos","Japoneses"],
        resp:1, exp:"O Tribunal de Nuremberg julgou 24 líderes nazistas por crimes contra a humanidade durante a 2ª Guerra." },

      // Holocausto
      { id:"q226", tema:"9holoc", ano:"9º Ano", pergunta:"A 'Solução Final' nazista era:", dif:"dificil",
        opts:["Expulsão dos judeus","O plano de extermínio sistemático de todos os judeus europeus","Prisão de judeus","Conversão forçada"],
        resp:1, exp:"A 'Solução Final' (1942) foi o plano de extermínio sistemático dos judeus europeus nos campos de extermínio." },
      { id:"q227", tema:"9holoc", ano:"9º Ano", pergunta:"O diário de Anne Frank documentou:", dif:"facil",
        opts:["A vida no campo de concentração","O cotidiano de uma menina judia escondida dos nazistas","A guerra na Europa","A resistência francesa"],
        resp:1, exp:"Anne Frank, aos 13 anos, escreveu um diário enquanto se escondia dos nazistas em Amsterdã." },

      // Guerra Fria
      { id:"q228", tema:"9guerrafria", ano:"9º Ano", pergunta:"A Doutrina Truman (1947) estabelecia:", dif:"medio",
        opts:["Isolamento dos EUA","Conter o avanço do comunismo no mundo","Aliança com a URSS","Desarmamento nuclear"],
        resp:1, exp:"A Doutrina Truman comprometia os EUA a conter o expansionismo soviético durante a Guerra Fria." },
      { id:"q229", tema:"9guerrafria", ano:"9º Ano", pergunta:"A Guerra da Coreia (1950-1953) dividiu a Coreia em:", dif:"facil",
        opts:["Norte comunista e Sul capitalista","Leste e Oeste","Três partes","Uma única Coreia"],
        resp:0, exp:"A Guerra da Coreia consolidou a divisão entre Coreia do Norte (socialista) e Coreia do Sul (capitalista)." },
      { id:"q230", tema:"9guerrafria", ano:"9º Ano", pergunta:"A corrida espacial entre EUA e URSS resultou:", dif:"facil",
        opts:["Fim da Guerra Fria","Chegada do homem à Lua (1969)","Destruição de satélites","Paz mundial"],
        resp:1, exp:"Em 1969, a missão Apollo 11 pousou na Lua, vitória dos EUA na corrida espacial contra a URSS." },
      { id:"q231", tema:"9guerrafria", ano:"9º Ano", pergunta:"A Guerra do Vietnã (1955-1975) terminou com:", dif:"medio",
        opts:["Vitória americana","Derrota dos EUA e reunificação do Vietnã sob regime comunista","Empate","Independência do Vietnã"],
        resp:1, exp:"O Vietnã foi reunificado sob governo comunista em 1976, após a retirada dos EUAS e a queda de Saigon." },

      // Brasil na 2ª Guerra / Fim Estado Novo
      { id:"q232", tema:"9brasil2gm", ano:"9º Ano", pergunta:"O Brasil declarou guerra ao Eixo (Alemanha/Itália) em:", dif:"medio",
        opts:["1939","1941","1942","1944"],
        resp:2, exp:"O Brasil declarou guerra ao Eixo em agosto de 1942, após torpedeamento de navios brasileiros." },
      { id:"q233", tema:"9fimestnovo", ano:"9º Ano", pergunta:"A redemocratização de 1945 no Brasil resultou em:", dif:"facil",
        opts:["Continuidade de Vargas","Eleição de Eurico Gaspar Dutra e nova Constituição","Volta da monarquia","Ditadura militar"],
        resp:1, exp:"Em 1945, Vargas foi deposto e Eurico Gaspar Dutra eleito presidente, com nova Constituição democrática em 1946." },

      // Descolonização
      { id:"q234", tema:"9descolon", ano:"9º Ano", pergunta:"Mahatma Gandhi liderou a independência da Índia usando:", dif:"facil",
        opts:["Guerra armada","Resistência pacífica e desobediência civil","Negociações comerciais","Aliança com o Japão"],
        resp:1, exp:"Gandhi liderou a independência indiana (1947) através da não-violência, desobediência civil e jejuns." },
      { id:"q235", tema:"9descolon", ano:"9º Ano", pergunta:"Nelson Mandela foi um líder na luta contra:", dif:"facil",
        opts:["Colonialismo na Índia","Apartheid na África do Sul","Ditadura no Brasil","Guerra Fria"],
        resp:1, exp:"Mandela lutou contra o apartheid (segregação racial) na África do Sul, tornando-se presidente em 1994." },
      { id:"q236", tema:"9descolon", ano:"9º Ano", pergunta:"A Guerra de Independência de Angola (1961-1975) foi contra:", dif:"dificil",
        opts:["França","Bélgica","Portugal","Inglaterra"],
        resp:2, exp:"Angola lutou contra o domínio colonial português, conquistando independência em 1975." },
      { id:"q237", tema:"9descolon", ano:"9º Ano", pergunta:"A Conferência de Bandung (1955) reuniu:", dif:"dificil",
        opts:["Países europeus","Países asiáticos e africanos recém-independentes","Países americanos","Potências coloniais"],
        resp:1, exp:"Bandung (Indonésia) reuniu 29 países afro-asiáticos para discutir descolonização e cooperação." },

      // Regime Militar
      { id:"q238", tema:"9regmilitar", ano:"9º Ano", pergunta:"O Golpe de 1964 foi justificado pelos militares como:", dif:"medio",
        opts:["Revolução socialista","Defesa contra o comunismo e restauração da ordem","Golpe democrático","Reforma política"],
        resp:1, exp:"Os militares alegaram combater a 'ameaça comunista' de João Goulart e restaurar a ordem no país." },
      { id:"q239", tema:"9regmilitar", ano:"9º Ano", pergunta:"O 'Milagre Econômico' brasileiro (1968-1973) caracterizou-se por:", dif:"medio",
        opts:["Alto crescimento econômico com aumento da dívida e concentração de renda","Distribuição igualitária de renda","Queda do PIB","Nacionalização de empresas"],
        resp:0, exp:"O Milagre Econômico teve altas taxas de crescimento, mas com aumento da dívida externa e desigualdade social." },
      { id:"q240", tema:"9regmilitar", ano:"9º Ano", pergunta:"O Diretas Já (1984) foi:", dif:"facil",
        opts:["Movimento por reforma agrária","Campanha popular por eleições presidenciais diretas","Greve geral","Revolta armada"],
        resp:1, exp:"Diretas Já foi a maior campanha popular da história brasileira, exigindo eleições diretas para presidente." },

      // Nova República
      { id:"q241", tema:"9novarepub", ano:"9º Ano", pergunta:"O Plano Real (1994) foi um plano econômico que:", dif:"facil",
        opts:["Aumentou a inflação","Estabilizou a economia e criou o Real como moeda","Desvalorizou a moeda","Privatizou bancos"],
        resp:1, exp:"O Plano Real (governo Itamar Franco/FHC) controlou a inflação crônica e estabilizou a economia brasileira." },
      { id:"q242", tema:"9novarepub", ano:"9º Ano", pergunta:"Luiz Inácio Lula da Silva foi eleito presidente em 2002 pelo partido:", dif:"facil",
        opts:["PSDB","PT","PMDB","DEM"],
        resp:1, exp:"Lula foi eleito pelo Partido dos Trabalhadores (PT) em 2002, assumindo em 2003." },

      // ── MAIS PERGUNTAS 6º ANO (completar temas com menos questões) ──
      { id:"q243", tema:"6intro", ano:"6º Ano", pergunta:"Heródoto, considerado 'Pai da História', era:", dif:"dificil",
        opts:["Romano","Grego","Egípcio","Persa"],
        resp:1, exp:"Heródoto (séc. V a.C.) foi o primeiro historiador grego a investigar e narrar eventos de forma sistemática." },
      { id:"q244", tema:"6hum", ano:"6º Ano", pergunta:"Os hominídeos desenvolveram a linguagem articulada, o que permitiu:", dif:"dificil",
        opts:["Apenas comunicação básica","Comunicação complexa, transmissão de conhecimento e cooperação social","Guerras","Construção de cidades"],
        resp:1, exp:"A linguagem articulada foi crucial para a transmissão de conhecimento e organização social complexa." },
      { id:"q245", tema:"6precolomb", ano:"6º Ano", pergunta:"A civilização maia declinou antes da chegada dos europeus. Uma causa foi:", dif:"dificil",
        opts:["Invasão europeia","Crise ecológica e colapso do comércio","Guerra civil permanente","Peste negra"],
        resp:1, exp:"O colapso maia clássico (séc. IX) envolveu superpopulação, degradação ambiental e conflitos internos." },

      // ── MAIS PERGUNTAS 7º ANO ──
      { id:"q246", tema:"7saberes", ano:"7º Ano", pergunta:"O povo Dogon (Mali) possui conhecimento astronômico sobre:", dif:"dificil",
        opts:["O sistema solar","A estrela Sirius (Sistema Sirius)","A Via Láctea","Buracos negros"],
        resp:1, exp:"Os Dogon possuem conhecimento tradicional sobre Sirius B (invisível a olho nu), documentado por antropólogos." },
      { id:"q247", tema:"7absol", ano:"7º Ano", pergunta:"O mercantilismo no Absolutismo defendia:", dif:"dificil",
        opts:["Livre comércio","Intervenção do Estado na economia, protecionismo e metalismo","Socialismo","Cooperativismo"],
        resp:1, exp:"O mercantilismo caracterizava-se por balança comercial favorável, protecionismo e acúmulo de metais preciosos." },
      { id:"q248", tema:"7absol", ano:"7º Ano", pergunta:"Oliver Cromwell liderou a Revolução Inglesa (1640-1688) que:", dif:"medio",
        opts:["Fortalecimento do rei","Limitou o poder real e fortaleceu o Parlamento","Instaurou a monarquia absoluta","Fim da monarquia"],
        resp:1, exp:"A Revolução Inglesa resultou na Declaração de Direitos (Bill of Rights, 1689), limitando o poder real." },
      { id:"q249", tema:"7colonias", ano:"7º Ano", pergunta:"O primeiro governador-geral do Brasil foi:", dif:"facil",
        opts:["Mem de Sá","Tomé de Sousa","Duarte da Costa","Martim Afonso de Sousa"],
        resp:1, exp:"Tomé de Sousa foi o primeiro governador-geral (1549-1553), fundador de Salvador." },
      { id:"q250", tema:"7religiao", ano:"7º Ano", pergunta:"A Inquisição foi um tribunal religioso que:", dif:"medio",
        opts:["Defendia a liberdade religiosa","Julgava e punia hereges na Europa e colônias","Promovia a ciência","Apoiava a Reforma"],
        resp:1, exp:"A Inquisição perseguia e punia aqueles considerados hereges pela Igreja Católica." },

      // ── MAIS PERGUNTAS 8º ANO ──
      { id:"q251", tema:"8regencia", ano:"8º Ano", pergunta:"O Ato Adicional de 1834 criou:", dif:"dificil",
        opts:["O fim da monarquia","Assembleias legislativas provinciais e Regência Una","A República","O Parlamentarismo"],
        resp:1, exp:"O Ato Adicional de 1834 criou Assembleias Legislativas Provinciais e estabeleceu a Regência Una." },
      { id:"q252", tema:"8amerlat", ano:"8º Ano", pergunta:"A Doutrina Monroe (1823) resumia-se em:", dif:"facil",
        opts:["'A América para os europeus'","'A América para os americanos' (oposição à colonização europeia)","'A América unida'","'América livre'"],
        resp:1, exp:"A Doutrina Monroe pregava 'América para os americanos', opondo-se à intervenção europeia nas Américas." },
      { id:"q253", tema:"8criseimp", ano:"8º Ano", pergunta:"A Proclamação da República (1889) foi liderada por:", dif:"facil",
        opts:["Deodoro da Fonseca","Benjamin Constant","Quintino Bocaiuva","Prudente de Morais"],
        resp:0, exp:"O Marechal Deodoro da Fonseca liderou o golpe que proclamou a República em 15 de novembro de 1889." },

      // ── MAIS PERGUNTAS 9º ANO ──
      { id:"q254", tema:"9revrussa", ano:"9º Ano", pergunta:"Stálin, após a morte de Lenin, estabeleceu:", dif:"facil",
        opts:["Democracia socialista","Ditadura pessoal com terror, planos quinquenais e coletivização","Capitalismo","Anarquismo"],
        resp:1, exp:"Stálin implantou planos quinquenais, coletivização forçada e um regime de terror na URSS." },
      { id:"q255", tema:"9fascismo", ano:"9º Ano", pergunta:"A Guerra Civil Espanhola (1936-1939) resultou em:", dif:"medio",
        opts:["Democracia","Ditadura de Francisco Franco","República socialista","Anarquismo"],
        resp:1, exp:"A Guerra Civil Espanhola terminou com a vitória dos nacionalistas de Franco, que estabeleceu uma ditadura até 1975." },
      { id:"q256", tema:"9guerrafria", ano:"9º Ano", pergunta:"A Perestroika (reestruturação) de Gorbachev na URSS visava:", dif:"medio",
        opts:["Fortalecer o comunismo","Reformar a economia soviética com elementos de mercado","Aumentar o poder militar","Isolar a URSS"],
        resp:1, exp:"A Perestroika (1985) buscava reformar a economia soviética, combinando planejamento central com mecanismos de mercado." },
      { id:"q257", tema:"9novarepub", ano:"9º Ano", pergunta:"Dilma Rousseff, primeira mulher presidente do Brasil, sofreu impeachment em:", dif:"facil",
        opts:["2014","2015","2016","2018"],
        resp:2, exp:"Dilma Rousseff sofreu impeachment (2016) por crime de responsabilidade fiscal (pedaladas fiscais)." },
"""

if __name__ == "__main__":
    import sys
    html_path = sys.argv[1] if len(sys.argv) > 1 else "/home/flavio/OpenManus/quiz_historico.html"

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the ]; that closes PERGUNTAS array
    target = "      { id:\"q107\","
    pos = content.find(target)
    if pos == -1:
        print("ERROR: Could not find q107 insertion point")
        sys.exit(1)

    # Find the closing ]; after q107
    end_pos = content.find("];", pos)
    if end_pos == -1:
        print("ERROR: Could not find closing ];")
        sys.exit(1)

    # Insert new questions before the ];
    new_content = content[:end_pos] + NOVAS_PERGUNTAS + "    ];\n"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # Count questions
    import re
    q_count = len(re.findall(r'id:"q\d+"', new_content))
    print(f"✅ {q_count} perguntas totais no arquivo!")
    print(f"   Inseridas {len(re.findall(r'id:"q\d+"', NOVAS_PERGUNTAS))} novas perguntas")
