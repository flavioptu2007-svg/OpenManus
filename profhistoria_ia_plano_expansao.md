# ProfHistória IA — Plano de Expansão de Ferramentas para Ensino de História

**Foco:** Anos Finais do Ensino Fundamental (6º–9º), Ensino Médio, EJA e preparação ENEM/SAEB
**Alinhamento curricular:** BNCC + Currículo Referência de Minas Gerais (CRMG)
**Contexto de origem:** expansão do motor multiagente já em construção (HistóriaIA Copilot — LangGraph + RAG/Qdrant + NestJS)

---

## Nota metodológica

O prompt original lista **78 ferramentas** em 10 categorias, embora o texto final peça a classificação de "50 ferramentas". Este documento cobre as 78 listadas e ajusta as classificações (impacto pedagógico, potencial comercial, indispensáveis) para esse total real — restringir a 50 significaria descartar arbitrariamente 28 ferramentas já especificadas.

Os códigos BNCC citados por ferramenta são **ilustrativos** (mapeiam a competência/habilidade-tipo mais próxima da família EF06HI–EF09HI e das competências gerais de Ciências Humanas). Para uso documental formal, os códigos exatos devem ser validados contra o documento oficial da BNCC e o CRMG — isso, aliás, é o papel natural do RAG `historia_paracatu`/BNCC que você está populando no Qdrant: ele deveria ser a fonte de verdade que essas ferramentas consultam em tempo real, não um mapeamento estático.

Cada ferramenta é descrita em formato compacto: **Objetivo • Público • BNCC** na primeira linha, **Funcionalidades** na segunda, **Diferencial • Exemplo de uso • Monetização** na terceira.

**Revisão v1.1 — guardrails de risco aplicados:** após revisão crítica desta versão, quatro pontos de risco foram endereçados diretamente no catálogo abaixo (não apenas citados em texto à parte): (1) revisão humana obrigatória para Adaptadores de inclusão e Gerador de PEI (#50–56), (2) validação comunitária obrigatória para o Criador de Estudos sobre Quilombos Regionais (#61), (3) prazo realista de ciclo de venda institucional/licitatória na Fase 4 do roadmap, (4) protocolo de guardrail anti-alucinação específico para simuladores conversacionais (#63–68). Ver marcações ⚠️ nas seções correspondentes.


---

## 1. Catálogo de Ferramentas por Categoria

### 1.1 Planejamento (7 ferramentas)

**1. Planejamento Anual de História**
*Objetivo:* Gerar a distribuição de unidades temáticas ao longo dos bimestres/trimestres de um ano letivo. *Público:* 6º–9º ano. *BNCC:* todas as unidades temáticas do ano (visão macro).
*Funcionalidades:* geração por série, distribuição automática por bimestre/trimestre, ajuste a calendário escolar real (feriados, eventos), exportação para grade da escola.
*Diferencial:* parte do calendário real da escola, não de um template genérico. *Exemplo:* gerar o ano do 8º ano da Coraci Meireles já considerando os trimestres de Minas Gerais. *Monetização:* incluído no plano base (gancho de entrada).

**2. Planejamento Trimestral/Bimestral de História**
*Objetivo:* Detalhar um recorte do planejamento anual em unidades didáticas. *Público:* 6º–9º, EJA. *BNCC:* habilidades do recorte escolhido.
*Funcionalidades:* quebra de unidades temáticas em semanas, sugestão de avaliações no período, alinhamento automático ao planejamento anual já gerado.
*Diferencial:* nunca conflita com o que já foi planejado no anual (estado compartilhado). *Exemplo:* detalhar o 3º trimestre do 6º ano (Antiguidade Oriental). *Monetização:* plano base.

**3. Sequência Didática de História**
*Objetivo:* Estruturar uma sequência de aulas conectadas (não aulas isoladas) sobre um tema. *Público:* todas as séries. *BNCC:* habilidades do tema + competências gerais (pensamento crítico, argumentação).
*Funcionalidades:* geração de 3–8 aulas encadeadas, progressão de complexidade, avaliação final integrada, sugestão de fontes históricas por aula.
*Diferencial:* pensa em progressão pedagógica, não aulas soltas. *Exemplo:* sequência de 5 aulas sobre Revolução Francesa terminando em debate simulado. *Monetização:* plano intermediário.

**4. Plano de Aula de História**
*Objetivo:* Gerar plano de aula individual, pronto para uso. *Público:* todas as séries. *BNCC:* habilidades específicas da aula.
*Funcionalidades:* já existe no seu backend atual (`materials/lesson-plan`) — competências, objetivos, sequência didática, avaliação, atividades.
*Diferencial:* integrado ao RAG curricular real, não genérico. *Exemplo:* plano sobre República Velha para o 9º ano. *Monetização:* plano base (já entregue).

**5. Planejamento por Habilidades BNCC**
*Objetivo:* Planejar a partir de uma habilidade específica (ex: EF08HI10), não de um tema livre. *Público:* coordenadores e professores. *BNCC:* habilidade-alvo escolhida pelo usuário.
*Funcionalidades:* busca de habilidade por código ou descrição, geração de conteúdo/atividades que atendem especificamente aquela habilidade, rastreamento de cobertura curricular no ano.
*Diferencial:* única ferramenta pensada para auditoria de cobertura BNCC (útil para coordenação pedagógica). *Exemplo:* coordenador verifica quais habilidades do 7º ano ainda não foram cobertas em outubro. *Monetização:* plano institucional/escola.

**6. Planejamento para EJA**
*Objetivo:* Adaptar planejamento ao perfil andragógico da EJA (adultos, tempo reduzido, experiência de vida). *Público:* EJA. *BNCC:* habilidades equivalentes adaptadas + foco em letramento histórico funcional.
*Funcionalidades:* linguagem adulta, conexão com experiência de vida do aluno, formato compacto para carga horária reduzida da EJA.
*Diferencial:* a maioria das plataformas EdTech ignora EJA completamente — nicho pouco atendido. *Exemplo:* aula sobre ditadura militar conectando com memórias dos próprios alunos adultos. *Monetização:* plano base (alto valor percebido, baixo custo de produção).

**7. Planejamento de Recuperação**
*Objetivo:* Gerar plano de recuperação focado nas lacunas específicas de um aluno ou turma. *Público:* todas as séries. *BNCC:* habilidades não consolidadas.
*Funcionalidades:* input de habilidades não atingidas, geração de atividades de reforço direcionadas, reavaliação sugerida.
*Diferencial:* recuperação direcionada por lacuna, não repetição do conteúdo original. *Exemplo:* recuperação para 4 alunos que não consolidaram "causas da Revolução Industrial". *Monetização:* plano base.


---

### 1.2 Produção de Material (9 ferramentas)

**8. Gerador de Apostilas de História**
*Objetivo:* Compilar conteúdo de um bimestre em apostila completa. *Público:* todas as séries. *BNCC:* todas as habilidades do período.
*Funcionalidades:* compilação de texto-base + exercícios + glossário, exportação em PDF/DOCX formatado, capa personalizável.
*Diferencial:* gera material editorial completo, não só texto solto. *Exemplo:* apostila do 1º bimestre do 9º ano (Era Vargas a Guerra Fria). *Monetização:* plano intermediário (alto valor de produto físico).

**9. Criador de Cadernos do Professor**
*Objetivo:* Versão do material com gabaritos, dicas de mediação e observações pedagógicas. *Público:* professor. *BNCC:* habilidades do conteúdo.
*Funcionalidades:* gabarito comentado, sugestões de mediação de debate, alertas de erros conceituais comuns dos alunos.
*Diferencial:* antecipa dificuldades reais de sala de aula. *Exemplo:* caderno do professor sobre Iluminismo com erros conceituais comuns de alunos do 8º ano. *Monetização:* plano intermediário.

**10. Criador de Cadernos do Aluno**
*Objetivo:* Versão do material para entrega direta ao estudante. *Público:* alunos 6º–9º/EM/EJA. *BNCC:* habilidades do conteúdo.
*Funcionalidades:* linguagem adequada à faixa etária, espaços para anotação, atividades intercaladas com teoria.
*Diferencial:* par natural do caderno do professor (consistência de conteúdo garantida). *Exemplo:* caderno do aluno sobre Egito Antigo para o 6º ano. *Monetização:* plano base.

**11. Criador de Guias de Estudo**
*Objetivo:* Material de estudo autônomo para revisão fora da sala de aula. *Público:* alunos de todas as séries, foco em EM/ENEM. *BNCC:* síntese de habilidades de um período.
*Funcionalidades:* resumos + mapas mentais + perguntas-guia, formato para autoestudo.
*Diferencial:* pensado para uso sem mediação do professor. *Exemplo:* guia de estudo sobre Guerra Fria para revisão pré-prova. *Monetização:* plano base.

**12. Criador de Revisões**
*Objetivo:* Gerar material de revisão pré-avaliação. *Público:* todas as séries. *BNCC:* habilidades do período avaliado.
*Funcionalidades:* lista de tópicos-chave, questões de fixação, identificação de pontos de maior peso na prova.
*Diferencial:* conectado à avaliação que será aplicada (não revisão genérica). *Exemplo:* revisão de Brasil Colônia antes da prova bimestral. *Monetização:* plano base.

**13. Gerador de Resumos Históricos**
*Objetivo:* Sintetizar um tema histórico em texto compacto e didático. *Público:* todas as séries. *BNCC:* habilidade do tema.
*Funcionalidades:* controle de tamanho/profundidade, ajuste de linguagem por faixa etária, inclusão de datas/personagens-chave.
*Diferencial:* ajuste fino de nível de leitura (6º ano ≠ EM). *Exemplo:* resumo de "Independência do Brasil" em 3 níveis de complexidade. *Monetização:* plano base (alto volume de uso, baixo custo).

**14. Gerador de Mapas Conceituais**
*Objetivo:* Visualizar relações causais/conceituais entre eventos históricos. *Público:* todas as séries. *BNCC:* habilidades de relação causa-consequência.
*Funcionalidades:* geração automática de nós e conexões a partir de um tema, exportação como imagem/SVG.
*Diferencial:* História é uma disciplina de relações causais — mapa conceitual é mais natural que linha do tempo simples para isso. *Exemplo:* mapa conceitual conectando crise de 1929 → ascensão de regimes totalitários → Segunda Guerra. *Monetização:* plano intermediário.

**15. Gerador de Linhas do Tempo**
*Objetivo:* Visualizar sequência cronológica de eventos. *Público:* todas as séries. *BNCC:* habilidades de noção de tempo histórico (centrais no 6º ano).
*Funcionalidades:* geração automática a partir de um período/tema, suporte a múltiplas linhas paralelas (ex: Brasil x Mundo), interatividade.
*Diferencial:* tempo histórico é habilidade fundante da disciplina — ferramenta de uso recorrente, não pontual. *Exemplo:* linha do tempo comparando processos de independência na América Latina. *Monetização:* plano base.

**16. Criador de Infográficos Históricos**
*Objetivo:* Material visual de alto impacto para um conceito ou comparação. *Público:* todas as séries. *BNCC:* habilidades de síntese e comparação.
*Funcionalidades:* templates visuais (comparação, processo, estatística), exportação em alta resolução para impressão/mural.
*Diferencial:* qualidade visual "pronta para imprimir e colar na parede", não rascunho. *Exemplo:* infográfico comparando Atenas x Esparta. *Monetização:* plano intermediário.


---

### 1.3 Fontes Históricas (7 ferramentas)

**17. Laboratório de Fontes Históricas**
*Objetivo:* Treinar leitura crítica de fontes primárias (texto, imagem, objeto). *Público:* todas as séries, foco 8º–9º/EM. *BNCC:* habilidades de crítica documental (núcleo do "pensar historicamente").
*Funcionalidades:* banco de fontes categorizadas por tema/período, roteiro de análise guiada (autoria, contexto, intencionalidade), perguntas progressivas de interpretação.
*Diferencial:* é a habilidade mais subestimada e mais cobrada em avaliações de larga escala (ENEM/SAEB). *Exemplo:* análise de uma carta de escravizado liberto do século XIX. *Monetização:* plano intermediário/premium.

**18. Analisador de Documentos Históricos**
*Objetivo:* Apoiar leitura de documentos textuais longos (leis, tratados, discursos). *Público:* 8º–9º/EM. *BNCC:* leitura e contextualização de fontes escritas.
*Funcionalidades:* upload de documento, glossário automático de termos de época, perguntas de compreensão contextualizadas.
*Diferencial:* funciona com documentos que o próprio professor sobe (não só banco fechado). *Exemplo:* análise da Lei Áurea com glossário de termos jurídicos do período. *Monetização:* plano premium.

**19. Interpretador de Charges Históricas**
*Objetivo:* Decodificar linguagem simbólica/satírica de charges políticas. *Público:* 7º–9º/EM, forte em ENEM. *BNCC:* leitura de linguagens não-verbais, ironia, crítica social.
*Funcionalidades:* banco de charges por tema/período, roteiro de leitura de elementos visuais + contexto histórico, geração de perguntas estilo ENEM.
*Diferencial:* charge é o tipo de fonte mais recorrente em provas de larga escala. *Exemplo:* charge sobre a crise do petróleo de 1973. *Monetização:* plano premium.

**20. Interpretador de Cartazes Históricos**
*Objetivo:* Analisar cartazes de propaganda (política, guerra, movimentos sociais). *Público:* 8º–9º/EM. *BNCC:* leitura de propaganda e construção de discurso ideológico.
*Funcionalidades:* banco categorizado (propaganda de guerra, regimes totalitários, movimentos sociais), roteiro de desconstrução de mensagem.
*Diferencial:* trabalha diretamente competência de combate à desinformação. *Exemplo:* cartaz de propaganda nazista vs. cartaz da resistência francesa. *Monetização:* plano premium.

**21. Analisador de Fotografias Históricas**
*Objetivo:* Ler fotografia como fonte histórica (enquadramento, intenção, contexto de produção). *Público:* todas as séries. *BNCC:* leitura de imagem como documento.
*Funcionalidades:* banco de fotos históricas datadas/contextualizadas, roteiro de análise (o que está dentro/fora do quadro, quem fotografou e por quê).
*Diferencial:* trabalha "foto não é neutra" — habilidade crítica essencial na era da imagem digital. *Exemplo:* fotografias da Guerra do Vietnã e o impacto na opinião pública americana. *Monetização:* plano intermediário.

**22. Oficina de História Oral**
*Objetivo:* Estruturar projetos de coleta de depoimentos (memória de familiares, moradores antigos). *Público:* todas as séries, forte em projetos de história local. *BNCC:* metodologia de pesquisa histórica, fontes orais.
*Funcionalidades:* roteiro de entrevista por tema, termo de consentimento simplificado, estrutura de transcrição e análise do depoimento coletado.
*Diferencial:* conecta sala de aula com a comunidade real do aluno. *Exemplo:* entrevistar moradores antigos de Paracatu sobre a mineração na cidade. *Monetização:* plano intermediário.

**23. Oficina de Patrimônio Histórico**
*Objetivo:* Trabalhar reconhecimento e valorização de patrimônio material/imaterial local. *Público:* todas as séries. *BNCC:* patrimônio histórico-cultural, identidade.
*Funcionalidades:* roteiro de identificação de patrimônio na cidade, ficha de catalogação simplificada, conexão com políticas de preservação.
*Diferencial:* ponte direta para a categoria "História Local" abaixo. *Exemplo:* catalogação de casarões históricos do centro de Paracatu. *Monetização:* plano intermediário/institucional.


---

### 1.4 Gamificação (11 ferramentas)

**24. Criador de RPG Histórico**
*Objetivo:* Imersão narrativa em um período histórico via personagem jogável. *Público:* 6º–9º. *BNCC:* empatia histórica, múltiplas perspectivas.
*Funcionalidades:* geração de fichas de personagem por contexto histórico, mestre de jogo assistido por IA, ramificações de decisão.
*Diferencial:* mesma lógica do seu jogo *Origins* — reaproveitamento direto de design conceitual. *Exemplo:* RPG ambientado na corte de Dom João VI no Brasil. *Monetização:* plano premium.

**25. Criador de Escape Room Histórico**
*Objetivo:* Resolução de enigmas conectados a conteúdo histórico sob pressão de tempo. *Público:* 7º–9º/EM. *BNCC:* aplicação de conhecimento, raciocínio lógico-histórico.
*Funcionalidades:* geração de enigmas temáticos, sistema de pistas progressivas, kit de impressão para sala física.
*Diferencial:* altíssimo engajamento para revisão pré-prova. *Exemplo:* escape room sobre decifrar pistas da Revolução Industrial para "escapar" da fábrica. *Monetização:* plano premium.

**26. Criador de Caça ao Tesouro Histórico**
*Objetivo:* Atividade investigativa com pistas históricas sequenciais. *Público:* 6º–7º. *BNCC:* sequenciamento e localização espaço-temporal.
*Funcionalidades:* geração de pistas conectadas a locais físicos da escola/cidade, integração opcional com história local.
*Diferencial:* pode ser 100% física, boa para escolas com pouco acesso digital em sala. *Exemplo:* caça ao tesouro pelos prédios históricos do centro de Paracatu. *Monetização:* plano base.

**27. Criador de Missões Históricas**
*Objetivo:* Estrutura de gamificação por progressão (XP, níveis, badges) aplicada ao conteúdo do bimestre. *Público:* 6º–9º. *BNCC:* habilidades do período transformadas em "missões".
*Funcionalidades:* conversão automática de objetivos de aprendizagem em missões com recompensa, painel de progresso do aluno.
*Diferencial:* gamificação estrutural do bimestre inteiro, não só de uma atividade isolada. *Exemplo:* missões do 3º bimestre do 8º ano sobre Revoluções Industriais. *Monetização:* plano premium.

**28. Criador de Quiz Histórico**
*Objetivo:* Avaliação rápida e gamificada de conteúdo. *Público:* todas as séries. *BNCC:* habilidades do tema do quiz.
*Funcionalidades:* já em uso no seu projeto (quiz com 40+ sets temáticos) — geração por tema/série, modo competitivo, banco de questões reaproveitável.
*Diferencial:* uso diário, baixíssimo atrito de adoção. *Exemplo:* quiz relâmpago sobre Idade Média no início da aula. *Monetização:* plano base.

**29. Criador de Show do Milhão Histórico**
*Objetivo:* Formato de quiz com dificuldade progressiva e "ajudas". *Público:* 7º–9º/EM. *BNCC:* habilidades do tema escolhido.
*Funcionalidades:* perguntas em ordem crescente de dificuldade/valor, cartas de ajuda (eliminar alternativa, pular pergunta), modo projeção para turma toda.
*Diferencial:* formato extremamente familiar aos alunos, zero curva de aprendizado da mecânica. *Exemplo:* Show do Milhão sobre Brasil República. *Monetização:* plano intermediário.

**30. Criador de UNO Histórico**
*Objetivo:* Jogo de cartas com regras adaptadas a categorias históricas. *Público:* 6º–9º. *BNCC:* já mapeado no seu projeto (série UNO História Viva, 22 decks).
*Funcionalidades:* geração de novos decks temáticos, regras adaptadas (cartas de "ação" ligadas a eventos), versão impressa e digital.
*Diferencial:* você já validou esse formato com 22 decks — reaproveitamento direto de produto que já funciona. *Exemplo:* deck UNO sobre Era Vargas. *Monetização:* plano base.

**31. Criador de Dominó Histórico**
*Objetivo:* Associação de pares conceituais (evento-data, causa-consequência, personagem-feito). *Público:* 6º–7º. *BNCC:* associação e sequenciamento.
*Funcionalidades:* geração de pares por tema, dificuldade ajustável, formato impresso.
*Diferencial:* mecânica simples e barata de produzir. *Exemplo:* dominó associando faraós a seus feitos. *Monetização:* plano base.

**32. Criador de Trilha Histórica**
*Objetivo:* Tabuleiro de percurso com desafios temáticos por casa. *Público:* 6º–9º. *BNCC:* habilidades do tema do tabuleiro.
*Funcionalidades:* geração de tabuleiro com casas de desafio/bônus/perigo, cartas de pergunta por casa.
*Diferencial:* reaproveita lógica de design de tabuleiro que você já domina (*Origins*). *Exemplo:* trilha sobre Grandes Navegações. *Monetização:* plano base.

**33. Criador de Batalha Naval Histórica**
*Objetivo:* Jogo de localização espacial aplicado a geografia histórica. *Público:* 7º–9º. *BNCC:* espacialidade histórica.
*Funcionalidades:* tabuleiro com mapa histórico real, perguntas para "atirar", adaptação de regras clássicas.
*Diferencial:* conecta História e Geografia de forma lúdica. *Exemplo:* batalha naval sobre rotas de navegação do império português. *Monetização:* plano base.

**34. Criador de Bingo Histórico**
*Objetivo:* Fixação de vocabulário/datas/personagens em formato leve. *Público:* 6º–9º. *BNCC:* habilidades de vocabulário histórico.
*Funcionalidades:* geração de cartelas únicas por turma, sorteio com explicação de cada item sorteado.
*Diferencial:* zero atrito de aplicação. *Exemplo:* bingo de personagens da Independência do Brasil. *Monetização:* plano base.


---

### 1.5 Avaliações (9 ferramentas)

**35. Banco de Questões de História**
*Objetivo:* Repositório central de questões reutilizáveis por tema/habilidade/dificuldade. *Público:* todas as séries. *BNCC:* tag por habilidade.
*Funcionalidades:* busca por tema/série/dificuldade/tipo, tags BNCC automáticas, exportação para qualquer outra ferramenta de avaliação do catálogo.
*Diferencial:* infraestrutura que todas as outras ferramentas de avaliação consomem. *Exemplo:* montar uma prova nova puxando questões já validadas do banco. *Monetização:* plano base.

**36. Simulados SAEB História**
*Objetivo:* Simular formato e nível de exigência do SAEB. *Público:* 9º ano (foco), EM. *BNCC:* habilidades avaliadas pelo SAEB.
*Funcionalidades:* questões no padrão de matriz de referência do SAEB, relatório de desempenho por habilidade, comparação com médias de referência.
*Diferencial:* conecta diretamente a métricas que a gestão escolar acompanha. *Exemplo:* simulado SAEB para o 9º ano em outubro. *Monetização:* plano institucional/escola.

**37. Simulados ENEM Ciências Humanas**
*Objetivo:* Simular questões de História no formato ENEM. *Público:* EM. *BNCC:* competências de Ciências Humanas do ENEM.
*Funcionalidades:* questões com texto-base + charge/imagem (padrão ENEM), gabarito com explicação da competência avaliada.
*Diferencial:* maior mercado endereçável entre todas as ferramentas. *Exemplo:* simulado de 10 questões sobre processos de redemocratização. *Monetização:* plano premium.

**38. Avaliação Diagnóstica**
*Objetivo:* Mapear conhecimento prévio antes de iniciar um conteúdo. *Público:* todas as séries. *BNCC:* habilidades-base do tema a ser iniciado.
*Funcionalidades:* questões de sondagem rápida, relatório de lacunas por turma, sugestão automática de ajuste no plano de aula.
*Diferencial:* fecha o ciclo com "Planejamento de Recuperação". *Exemplo:* diagnóstico antes de iniciar Idade Média no 7º ano. *Monetização:* plano intermediário.

**39. Avaliação Formativa**
*Objetivo:* Avaliação contínua de processo. *Público:* todas as séries. *BNCC:* habilidades em desenvolvimento durante a unidade.
*Funcionalidades:* checkpoints curtos ao longo da sequência didática, feedback qualitativo automático, registro de evolução do aluno.
*Diferencial:* atende exigência crescente de avaliação por competências. *Exemplo:* checkpoints semanais durante a sequência sobre Revolução Francesa. *Monetização:* plano intermediário.

**40. Avaliação Somativa**
*Objetivo:* Avaliação formal de fechamento de período. *Público:* todas as séries. *BNCC:* habilidades do período completo.
*Funcionalidades:* já parcialmente em uso no seu projeto (exames bimestrais .docx) — geração de prova completa com gabarito.
*Diferencial:* formato já validado e testado em produção. *Exemplo:* prova bimestral do 8º ano sobre Era Napoleônica. *Monetização:* plano base.

**41. Recuperação Paralela**
*Objetivo:* Avaliação de segunda chamada para alunos com desempenho insuficiente. *Público:* todas as séries. *BNCC:* habilidades não consolidadas na avaliação original.
*Funcionalidades:* geração de prova equivalente (mesma habilidade, questões diferentes), relatório de evolução comparado à avaliação original.
*Diferencial:* garante isonomia. *Exemplo:* recuperação paralela de 6 alunos do 9º ano sobre Guerra Fria. *Monetização:* plano base.

**42. Corretor de Questões Discursivas**
*Objetivo:* Apoiar (não substituir) a correção de respostas abertas/dissertativas. *Público:* professor, EM/9º ano. *BNCC:* habilidades de argumentação escrita.
*Funcionalidades:* sugestão de nota por critério, identificação de lacunas conceituais na resposta, feedback redigido automaticamente para o aluno.
*Diferencial:* maior economia de tempo do catálogo inteiro. *Exemplo:* correção assistida de 30 respostas sobre "causas da Revolução Industrial". *Monetização:* plano premium.

**43. Criador de Rubricas de História**
*Objetivo:* Gerar critérios de avaliação claros e por níveis de desempenho. *Público:* professor. *BNCC:* habilidades e competências gerais avaliadas.
*Funcionalidades:* geração de rubrica por critério (conteúdo, argumentação, uso de fontes), níveis de desempenho descritos, versão para compartilhar com o aluno antes da atividade.
*Diferencial:* transparência avaliativa. *Exemplo:* rubrica para um seminário sobre civilizações antigas. *Monetização:* plano intermediário.


---

### 1.6 Produção Visual (6 ferramentas)

**44. Criador de Histórias em Quadrinhos Históricas**
*Objetivo:* Narrar um evento histórico em formato de HQ. *Público:* 6º–8º. *BNCC:* narrativa histórica, sequenciamento.
*Funcionalidades:* geração de roteiro + painéis, diálogos de época, exportação para impressão.
*Diferencial:* formato de altíssima adesão entre adolescentes. *Exemplo:* HQ sobre a chegada dos portugueses ao Brasil contada por dois pontos de vista. *Monetização:* plano premium.

**45. Criador de Charges Educacionais**
*Objetivo:* Sintetizar crítica/análise histórica em charge original produzida pelo aluno. *Público:* 7º–9º/EM. *BNCC:* linguagem satírica e crítica social, produção de charge.
*Funcionalidades:* gerador de roteiro visual de charge a partir de um tema, banco de elementos simbólicos por período.
*Diferencial:* complementa o "Interpretador de Charges" (#19) com o lado de produção. *Exemplo:* aluno cria charge própria sobre desigualdade social na Era Vargas. *Monetização:* plano premium.

**46. Criador de Cartazes Históricos**
*Objetivo:* Produção de cartaz temático para mural/exposição. *Público:* todas as séries. *BNCC:* síntese visual de conteúdo.
*Funcionalidades:* templates por tema, geração de texto-síntese + sugestão de imagem, formato para impressão A3.
*Diferencial:* baixo custo de produção, alto uso em feiras/exposições escolares. *Exemplo:* cartaz sobre o Dia da Consciência Negra. *Monetização:* plano base.

**47. Criador de Murais Temáticos**
*Objetivo:* Estruturar um painel coletivo sobre um tema amplo. *Público:* todas as séries, atividade de turma. *BNCC:* síntese coletiva de conteúdo, trabalho colaborativo.
*Funcionalidades:* divisão automática do tema em seções para grupos, checklist de itens obrigatórios no mural.
*Diferencial:* organiza atividade coletiva que normalmente é caótica de coordenar. *Exemplo:* mural sobre "500 anos de resistência indígena" dividido em 5 grupos. *Monetização:* plano base.

**48. Criador de Lapbooks Históricos**
*Objetivo:* Material manipulável e dobrável que organiza conteúdo de forma visual/tátil. *Público:* 6º–7º. *BNCC:* síntese e organização de conteúdo.
*Funcionalidades:* moldes de dobradura prontos para imprimir, conteúdo pré-formatado para cada "aba" do lapbook.
*Diferencial:* pouco explorado em História especificamente. *Exemplo:* lapbook sobre o Egito Antigo com abas de "deuses", "faraós", "pirâmides". *Monetização:* plano intermediário.

**49. Criador de Revistas Históricas**
*Objetivo:* Compilar produções da turma em formato de revista/jornal de época. *Público:* todas as séries, projeto de encerramento de unidade. *BNCC:* síntese, produção textual, letramento midiático.
*Funcionalidades:* template de revista editável, seções (reportagem, entrevista, anúncio de época), exportação em PDF.
*Diferencial:* produto final tangível de alto orgulho para o aluno. *Exemplo:* "Jornal da Belle Époque" produzido pela turma do 8º ano. *Monetização:* plano premium.


---

### 1.7 Inclusão (7 ferramentas)

> ⚠️ **Requisito de produto, não nota de rodapé:** todo output desta categoria — especialmente #55 (PEI) — é uma **sugestão de ponto de partida**, não um documento pronto para uso. PEI de aluno com laudo é, por lei/norma da rede, responsabilidade de validação da equipe de AEE (Atendimento Educacional Especializado) ou profissional habilitado. A plataforma deve impor um passo de revisão humana obrigatório antes de qualquer exportação/impressão desses materiais — não apenas recomendá-lo. Isso vale tanto por responsabilidade pedagógica quanto por exposição legal da escola/rede que adotar o produto.


**50. Adaptador para TEA**
*Objetivo:* Adaptar qualquer material do catálogo para alunos com Transtorno do Espectro Autista. *Público:* todas as séries. *BNCC:* mesma habilidade-alvo, formato adaptado.
*Funcionalidades:* linguagem literal e objetiva, estrutura previsível e sequencial, redução de sobrecarga sensorial visual, apoio com pistas visuais/rotina.
*Diferencial:* adapta material já existente em vez de exigir criação do zero. *Exemplo:* adaptar o plano sobre Revolução Industrial com rotina visual de etapas. *Monetização:* plano institucional.

**51. Adaptador para TDAH**
*Objetivo:* Adaptar material para sustentar atenção e reduzir sobrecarga cognitiva. *Público:* todas as séries. *BNCC:* mesma habilidade-alvo, formato adaptado.
*Funcionalidades:* fragmentação em blocos curtos, inserção de pausas ativas, redução de texto corrido, destaque visual de informação-chave.
*Diferencial:* mesma arquitetura do #50, altíssima incidência em sala comum. *Exemplo:* quebrar uma aula de 50min em blocos de 10-12min com check-ins. *Monetização:* plano institucional.

**52. Adaptador para Deficiência Intelectual**
*Objetivo:* Simplificar nível de abstração mantendo o conceito histórico central. *Público:* todas as séries. *BNCC:* habilidade-alvo com nível de exigência adaptado.
*Funcionalidades:* simplificação conceitual com manutenção do essencial, exemplos concretos no lugar de abstrações, redução de vocabulário.
*Diferencial:* difícil de fazer manualmente bem (risco de infantilizar) — IA pode equilibrar simplicidade sem perder respeito à idade do aluno. *Exemplo:* adaptar "Revolução Francesa" para currículo funcional do 8º ano. *Monetização:* plano institucional.

**53. Adaptador para Baixa Visão**
*Objetivo:* Adaptar material para legibilidade e contraste adequados. *Público:* todas as séries. *BNCC:* habilidade-alvo, formato adaptado.
*Funcionalidades:* ajuste automático de contraste/tamanho de fonte, descrição textual de imagens/mapas/linhas do tempo, formato compatível com leitor de tela.
*Diferencial:* cobre o ponto mais frágil do catálogo visual. *Exemplo:* descrição textual de um mapa de expansão do Império Romano. *Monetização:* plano institucional.

**54. Adaptador para Não Alfabetizados**
*Objetivo:* Tornar conteúdo histórico acessível a alunos (frequentemente EJA) ainda não alfabetizados plenamente. *Público:* EJA, alfabetização tardia. *BNCC:* habilidade-alvo via linguagem oral/visual.
*Funcionalidades:* conversão de texto em roteiro de apoio oral, uso intensivo de imagem sequencial, redução à estrutura de narrativa simples.
*Diferencial:* nicho quase não atendido pelo mercado EdTech de História — alinhado ao seu próprio trabalho com EJA. *Exemplo:* contar a história da abolição por sequência de imagens com apoio oral. *Monetização:* plano institucional/social.

**55. Gerador de PEI para História**
*Objetivo:* Gerar a seção específica de História dentro do Plano Educacional Individualizado de um aluno. *Público:* professor + equipe de AEE. *BNCC:* habilidades adaptadas ao perfil do aluno.
*Funcionalidades:* geração de objetivos individualizados a partir do laudo/perfil, sugestão de estratégias e recursos específicos para História, integração com os "Adaptadores" acima.
*Diferencial:* PEI geralmente é genérico/multidisciplinar — profundidade específica de História é diferencial real. *Exemplo:* seção de História do PEI de um aluno com TEA no 7º ano. *Monetização:* plano institucional.
*Guardrail obrigatório:* saída sempre marcada como "rascunho — pendente de validação da equipe de AEE"; sistema bloqueia exportação/impressão em formato final até um profissional habilitado confirmar revisão. Log de quem revisou e quando, para efeito de responsabilidade documentada da escola.

**56. Gerador de Avaliações Adaptadas**
*Objetivo:* Versão de qualquer avaliação do banco ajustada a um perfil de inclusão específico. *Público:* todas as séries. *BNCC:* mesma habilidade avaliada, formato adaptado.
*Funcionalidades:* conversão automática de formato de questão (objetiva simplificada, apoio visual, tempo estendido), manutenção da habilidade avaliada original.
*Diferencial:* fecha o ciclo de inclusão conectando #35 e os "Adaptadores" — sistema, não ferramenta isolada. *Exemplo:* versão adaptada da prova bimestral para aluno com baixa visão. *Monetização:* plano institucional.


---

### 1.8 História Local (6 ferramentas)

**57. Investigador da História Local**
*Objetivo:* Estruturar pesquisa sobre a história do município/região do aluno. *Público:* todas as séries. *BNCC:* habilidades de história local/regional.
*Funcionalidades:* roteiro de pesquisa por fonte disponível (arquivo público, jornal antigo, memória oral), conexão entre história local e processos nacionais/mundiais.
*Diferencial:* é exatamente o território que sua coleção `historia_paracatu` no Qdrant já começa a cobrir. *Exemplo:* investigar o papel de Paracatu no ciclo do ouro em Minas Gerais. *Monetização:* plano institucional.

**58. Criador de Roteiros Históricos da Cidade**
*Objetivo:* Estruturar um passeio guiado por pontos históricos da cidade. *Público:* todas as séries, atividade de campo. *BNCC:* patrimônio e espacialidade histórica local.
*Funcionalidades:* geração de roteiro por pontos de interesse, ficha histórica de cada ponto, versão para impressão e versão para app de visita guiada.
*Diferencial:* viabiliza aula de campo com preparo pedagógico real. *Exemplo:* roteiro pelo centro histórico de Paracatu conectando casarões ao ciclo do ouro. *Monetização:* plano institucional.

**59. Criador de Inventários Patrimoniais**
*Objetivo:* Catalogação formal de bens patrimoniais pelos próprios alunos. *Público:* 8º–9º/EM, projetos de longa duração. *BNCC:* metodologia de pesquisa e preservação patrimonial.
*Funcionalidades:* ficha de catalogação padronizada, banco de dados colaborativo da turma/escola, exportação para órgãos de patrimônio.
*Diferencial:* produto com utilidade real fora da escola. *Exemplo:* inventário de imóveis históricos do centro de Paracatu pelo 9º ano. *Monetização:* plano institucional/projeto.

**60. Criador de Projetos de Memória Local**
*Objetivo:* Estruturar projeto de longa duração sobre a memória de uma comunidade/grupo local. *Público:* todas as séries, projeto interdisciplinar. *BNCC:* memória, identidade, fontes orais e documentais combinadas.
*Funcionalidades:* cronograma de projeto, integração com "Oficina de História Oral" (#22) e "Investigador da História Local" (#57), estrutura de produto final.
*Diferencial:* projeto "guarda-chuva" que une várias ferramentas do catálogo. *Exemplo:* projeto de memória sobre bairros antigos de Paracatu ao longo de um semestre. *Monetização:* plano institucional.

**61. Criador de Estudos sobre Quilombos Regionais**
*Objetivo:* Estruturar conteúdo sobre comunidades quilombolas da região do aluno. *Público:* todas as séries. *BNCC:* história e cultura afro-brasileira, história regional (Lei 10.639/03).
*Funcionalidades:* base direta no seu seed de currículo CRMG (competência CRMG-PCT-01 sobre ciclo do ouro e quilombos em Paracatu) — geração de conteúdo conectando história regional a processos nacionais de escravidão e resistência.
*Diferencial:* atende exigência legal (Lei 10.639/03) com profundidade regional real. *Exemplo:* estudo sobre comunidades quilombolas no entorno de Paracatu. *Monetização:* plano institucional.
*Guardrail obrigatório:* isto é conteúdo cultural sensível sobre comunidades reais e vivas, não um período histórico encerrado. Conteúdo gerado por RAG/BNCC não deve ser publicado como material "pronto" sem contato prévio com lideranças/associações quilombolas locais (ex: articulação com a comunidade certificada pela Fundação Cultural Palmares na região de Paracatu, quando existente). A ferramenta deve gerar rascunho pedagógico para uso em sala + roteiro de validação externa — nunca posicionar a IA como fonte final sobre a história de uma comunidade específica.

**62. Criador de Guias Turísticos Históricos**
*Objetivo:* Produzir material de divulgação do patrimônio histórico local. *Público:* 8º–9º/EM, projeto de produto final. *BNCC:* produção textual, patrimônio, comunicação.
*Funcionalidades:* template de guia turístico, integração com roteiros já criados (#58), versão digital e impressa.
*Diferencial:* alto orgulho de produção e potencial de parceria com turismo municipal. *Exemplo:* guia turístico do centro histórico de Paracatu produzido pelos alunos. *Monetização:* plano institucional/projeto.


---

### 1.9 Inteligência Artificial para História (6 ferramentas)

> ⚠️ **Guardrail obrigatório desta categoria:** simuladores conversacionais e de cenário (#63–68) têm risco de anacronismo, invenção de falas/eventos e viés de simplificação histórica muito maior que ferramentas de geração de material estático — o modelo está "improvisando" em tempo real, não recuperando de um RAG curado. Antes de liberar qualquer ferramenta desta categoria em produção, adaptar o **Protocolo Zero Alucinação v2.0** (já existente no seu repertório) especificamente para diálogo/simulação: (1) todo output de personagem/cenário histórico deve citar a base factual usada quando perguntado, (2) o sistema deve recusar afirmar como fato o que é reconstrução plausível não documentada, sinalizando isso explicitamente ao aluno, (3) revisão humana amostral periódica das transcrições geradas, não só teste no lançamento. Isso vale com força extra para #68 (Simulador de Revoluções) e #72 (Cenários Contrafactuais), onde "e se" pode escorregar para revisionismo histórico sem essa disciplina.


**63. Tutor Virtual de História**
*Objetivo:* Apoio individualizado de estudo fora do horário de aula. *Público:* todas as séries. *BNCC:* habilidades sob demanda do aluno.
*Funcionalidades:* chat com tutor especializado em História, respostas ancoradas no RAG curricular (BNCC/CRMG), limites pedagógicos (não faz a atividade pelo aluno, guia o raciocínio).
*Diferencial:* extensão direta do seu motor LangGraph atual voltada ao aluno em vez do professor. *Exemplo:* aluno tira dúvida sobre causas da Primeira Guerra Mundial antes da prova. *Monetização:* plano premium.

**64. Debate Histórico com Personagens**
*Objetivo:* Simular diálogo/debate com uma figura histórica (com avisos claros de que é uma reconstrução). *Público:* 7º–9º/EM. *BNCC:* múltiplas perspectivas, empatia histórica, argumentação.
*Funcionalidades:* personagens com posição histórica definida, aluno argumenta e recebe contra-argumentos no estilo da época, encerramento com reflexão sobre os limites da reconstrução.
*Diferencial:* alto engajamento emocional/narrativo — requer curadoria cuidadosa para não escorregar em anacronismo. *Exemplo:* debate entre posições de um jacobino e um girondino. *Monetização:* plano premium.

**65. Simulador de Julgamentos Históricos**
*Objetivo:* Recriar julgamento de um evento/decisão histórica com papéis (acusação, defesa, júri formado pela turma). *Público:* 8º–9º/EM. *BNCC:* argumentação, múltiplas perspectivas, juízo histórico fundamentado.
*Funcionalidades:* geração de papéis e argumentos-base por posição, estrutura de júri simulado, mediação de tempo de fala.
*Diferencial:* transforma juízo histórico em atividade estruturada e observável. *Exemplo:* "julgamento" do Tratado de Versalhes. *Monetização:* plano premium.

**66. Simulador de Assembleias Históricas**
*Objetivo:* Recriar processo de tomada de decisão coletiva de um momento histórico. *Público:* 8º–9º/EM. *BNCC:* processos políticos, representação, negociação.
*Funcionalidades:* papéis representando grupos/facções históricas reais, pauta de votação baseada em decisões históricas reais, registro de "ata" da simulação.
*Diferencial:* ensina processo político, não só resultado. *Exemplo:* simulação da Assembleia Constituinte de 1987-88. *Monetização:* plano premium.

**67. Simulador de Civilizações**
*Objetivo:* Gerenciar decisões estratégicas de uma civilização ao longo de um período. *Público:* 6º–7º. *BNCC:* fatores de desenvolvimento civilizacional.
*Funcionalidades:* cenário inicial baseado em civilização real, decisões com consequências simuladas, comparação final com o que de fato aconteceu.
*Diferencial:* mecânica de jogo de estratégia aplicada a conteúdo curricular sério. *Exemplo:* gerenciar decisões do Egito Antigo diante de cheias do Nilo. *Monetização:* plano premium.

**68. Simulador de Revoluções**
*Objetivo:* Explorar condições, atores e pontos de decisão de um processo revolucionário. *Público:* 8º–9º/EM. *BNCC:* causas estruturais e conjunturais, papel dos diferentes grupos sociais.
*Funcionalidades:* cenário com tensões sociais pré-revolução, decisões dos diferentes grupos, múltiplos desfechos possíveis conforme decisões tomadas.
*Diferencial:* combate determinismo histórico ingênuo. *Exemplo:* simular pontos de decisão da Revolução Russa de 1917. *Monetização:* plano premium.


---

### 1.10 Ferramentas Exclusivas Inovadoras (10 ferramentas)

**69. Máquina do Tempo Educacional**
*Objetivo:* Experiência imersiva de "visita" a um período histórico. *Público:* todas as séries. *BNCC:* contextualização sensorial de período histórico.
*Funcionalidades:* narrativa imersiva em primeira pessoa, descrição multissensorial do cotidiano da época, ramificação simples de escolhas.
*Diferencial:* peça de marketing tão forte quanto pedagógica — ótimo gancho de demonstração comercial. *Exemplo:* "visitar" um dia de mercado na Roma Antiga. *Monetização:* plano premium.

**70. Reconstrutor de Civilizações Antigas**
*Objetivo:* Reconstruir, com base em evidência arqueológica/histórica, a vida cotidiana em uma civilização antiga. *Público:* 6º ano (foco). *BNCC:* civilizações antigas, vida cotidiana, fontes arqueológicas.
*Funcionalidades:* reconstrução temática (moradia, alimentação, trabalho, crença), citação do tipo de evidência usada para cada reconstrução.
*Diferencial:* ensina que história antiga é reconstruída por evidência, não "sabida" magicamente. *Exemplo:* reconstrução do cotidiano de uma família mesopotâmica. *Monetização:* plano intermediário.

**71. Comparador de Sociedades Históricas**
*Objetivo:* Comparar estrutura, valores e organização de duas ou mais sociedades históricas. *Público:* 7º–9º/EM. *BNCC:* análise comparativa, relativização cultural.
*Funcionalidades:* seleção de dois períodos/sociedades, geração de comparação estruturada por eixo (política, economia, cultura, papel social).
*Diferencial:* combate etnocentrismo e anacronismo. *Exemplo:* comparar organização social de Esparta e Atenas. *Monetização:* plano intermediário.

**72. Gerador de Cenários Contrafactuais ("E se?")**
*Objetivo:* Explorar raciocínio contrafactual. *Público:* 8º–9º/EM. *BNCC:* causalidade histórica, multicausalidade.
*Funcionalidades:* geração de cenário alternativo plausível a partir de uma mudança de premissa, análise de quais fatores seriam mais/menos afetados.
*Diferencial:* ensina causalidade histórica de forma ativa. *Exemplo:* "e se a Revolução Industrial tivesse começado na China?". *Monetização:* plano premium.

**73. Atlas Histórico Interativo**
*Objetivo:* Visualizar mudanças territoriais/políticas ao longo do tempo em mapa interativo. *Público:* todas as séries. *BNCC:* espacialidade histórica, processos de expansão/fragmentação territorial.
*Funcionalidades:* linha do tempo conectada a mapa, comparação de fronteiras entre períodos, camadas temáticas (rotas comerciais, conflitos, impérios).
*Diferencial:* combina tempo + espaço em uma única ferramenta visual. *Exemplo:* expansão e fragmentação do Império Romano ao longo dos séculos. *Monetização:* plano premium.

**74. Museu Virtual Escolar**
*Objetivo:* Espaço digital para "expor" produções dos alunos como acervo de museu. *Público:* todas as séries, produto de encerramento de projeto. *BNCC:* curadoria, síntese, comunicação.
*Funcionalidades:* templates de "sala" temática, upload de produções da turma, modo de visita compartilhável com a família.
*Diferencial:* dá visibilidade pública ao trabalho da turma. *Exemplo:* museu virtual sobre história de Paracatu produzido pelo 9º ano. *Monetização:* plano institucional.

**75. Criador de Exposições Históricas**
*Objetivo:* Estruturar exposição física com curadoria pedagógica. *Público:* todas as séries, projeto coletivo. *BNCC:* curadoria, síntese, comunicação.
*Funcionalidades:* roteiro de curadoria, ficha técnica de cada item exposto.
*Diferencial:* par físico do "Museu Virtual" (#74). *Exemplo:* exposição sobre "100 anos da Semana de Arte Moderna" no corredor da escola. *Monetização:* plano institucional.

**76. Criador de Podcasts Históricos**
*Objetivo:* Estruturar roteiro e produção de episódio de podcast sobre um tema histórico. *Público:* 8º–9º/EM. *BNCC:* produção oral, síntese, comunicação digital.
*Funcionalidades:* roteiro de episódio, sugestão de perguntas em formato entrevista, checklist de produção.
*Diferencial:* trabalha cultura digital e oralidade. *Exemplo:* episódio sobre a Lei Áurea. *Monetização:* plano intermediário.

**77. Criador de Jornais Históricos**
*Objetivo:* Recriar uma edição de jornal como se publicada no momento de um evento histórico. *Público:* 7º–9º. *BNCC:* narrativa em primeira pessoa do período, letramento midiático.
*Funcionalidades:* template de jornal de época, geração de manchetes/notícias coerentes com a linguagem do período, seção de "anúncios" de época.
*Diferencial:* exercício de empatia histórica através de estilo jornalístico. *Exemplo:* "Jornal da Proclamação" simulando 16 de novembro de 1889. *Monetização:* plano intermediário.

**78. Criador de Documentários Históricos**
*Objetivo:* Estruturar roteiro de documentário curto produzido pelos alunos. *Público:* 8º–9º/EM, projeto de maior duração. *BNCC:* síntese, narrativa audiovisual, pesquisa.
*Funcionalidades:* roteiro de documentário (abertura, desenvolvimento, conclusão), sugestão de fontes visuais/depoimentos a incluir, checklist de produção.
*Diferencial:* produto final de maior prestígio do catálogo. *Exemplo:* documentário sobre a história do garimpo em Paracatu. *Monetização:* plano premium.


---

## 2. Classificação por Impacto Pedagógico

*(Critério: contribuição para pensamento histórico, habilidades BNCC centrais, frequência de uso possível em sala)*

**Impacto Muito Alto** — uso recorrente + habilidade fundante da disciplina
4, 13, 15, 17, 28, 35, 38, 39, 42, 50–56 (Inclusão completa), 57, 61, 63

**Impacto Alto** — fortalece habilidades centrais com frequência moderada
1, 2, 3, 5, 6, 7, 14, 18–21, 22, 30, 36, 37, 40, 41, 43, 58–60, 62, 65, 66, 68, 71, 72, 73

**Impacto Médio-Alto** — forte engajamento, contribuição pedagógica real mas mais pontual
8–12, 16, 24–27, 29, 31–34, 44–49, 67, 69, 70, 74–78

**Impacto Médio** — alto valor de engajamento/marca, contribuição pedagógica mais difusa
64 (alto risco de anacronismo se mal curado)


---

## 3. Classificação por Potencial Comercial

**Premium / Alto ARPU** (assinatura individual de professor ou add-on caro)
17, 18, 19, 20, 24, 25, 27, 36, 37, 42, 44, 45, 49, 63–68, 69, 72, 73, 78

**Core / Padrão** (incluído no plano principal, motor de retenção diária)
3, 4, 13, 14, 15, 16, 28, 30, 35, 38, 39, 40, 41, 43

**Aquisição / Freemium** (baixo custo de produção, alto volume, gancho de entrada)
1, 2, 6, 7, 12, 26, 31, 32, 33, 34, 46, 47

**Institucional / B2B Escola-Secretaria** (decisão de compra não é do professor individual)
5, 22, 23, 50–56, 57–62, 74, 75

**Nicho de Alto Valor Social** (baixo volume, alto impacto de marca/relações institucionais)
54, 61


---

## 4. As 20 Ferramentas Indispensáveis para um Professor de História

Critério: uso semanal real + cobertura das três frentes que mais consomem tempo do professor (planejar, avaliar, incluir) + alinhamento direto ao seu próprio contexto (6º–9º, EJA, BNCC/CRMG, Paracatu).

1. **Plano de Aula de História (#4)** — já o núcleo do seu backend atual.
2. **Planejamento por Habilidades BNCC (#5)** — garante cobertura curricular real, não intuitiva.
3. **Banco de Questões de História (#35)** — infraestrutura de tudo que é avaliação.
4. **Avaliação Formativa (#39)** — atende exigência crescente de avaliação por competência.
5. **Criador de Rubricas de História (#43)** — transparência avaliativa, baixo custo de implementação.
6. **Corretor de Questões Discursivas (#42)** — maior economia de tempo possível no catálogo.
7. **Gerador de Resumos Históricos (#13)** — uso diário, baixíssimo atrito.
8. **Gerador de Linhas do Tempo (#15)** — habilidade fundante (noção de tempo histórico).
9. **Laboratório de Fontes Históricas (#17)** — núcleo do "pensar historicamente", forte em ENEM/SAEB.
10. **Interpretador de Charges Históricas (#19)** — maior retorno específico para preparação de exames.
11. **Criador de Quiz Histórico (#28)** — uso recorrente, já validado em produção no seu projeto.
12. **Criador de UNO Histórico (#30)** — formato já testado e funcionando (22 decks).
13. **Simulados SAEB História (#36)** — forte argumento institucional/gestão.
14. **Tutor Virtual de História (#63)** — extensão natural do seu motor LangGraph para o aluno.
15. **Adaptador para TEA (#50)** — inclusão de maior demanda prática em sala regular.
16. **Adaptador para TDAH (#51)** — mesma arquitetura do #50, altíssima incidência em sala comum.
17. **Gerador de PEI para História (#55)** — exigência legal recorrente, pouco atendida com profundidade.
18. **Investigador da História Local (#57)** — interface pedagógica natural do seu RAG `historia_paracatu`.
19. **Criador de Estudos sobre Quilombos Regionais (#61)** — compliance Lei 10.639/03, já tem base na sua seed CRMG.
20. **Planejamento de Recuperação (#7)** — fecha o ciclo diagnóstico → recuperação que toda escola cobra.


---

## 5. Roadmap de Desenvolvimento em 4 Fases

Ancorado na arquitetura que já existe (LangGraph + RAG/Qdrant + NestJS + cache + observabilidade), não em um produto do zero.

### Fase 1 — Consolidação do Núcleo (já ~70% construído)
**Objetivo:** fechar o ciclo planejar → avaliar com qualidade de produção.
- Ferramentas: #1–7, #13, #15, #28, #35, #38–43
- Trabalho técnico: os endpoints `materials/lesson-plan`, `materials/activities`, `materials/assessment` já cobrem boa parte disso — falta principalmente #42 (Corretor Discursivo, maior valor) e #5 (Planejamento por Habilidades, exige rastreamento de cobertura curricular no Postgres — o schema `CurriculumCompetency` já criado é a base disso).
- Critério de saída: professor consegue planejar o bimestre inteiro e fechar o ciclo de avaliação sem saída da plataforma.

### Fase 2 — Fontes, Inclusão e História Local (diferenciação real)
**Objetivo:** entrar nos três blocos que nenhum concorrente genérico de "IA para professores" cobre bem.
- Ferramentas: #17–23, #50–56, #57–62
- Trabalho técnico: a coleção `historia_paracatu` no Qdrant é literalmente a infraestrutura de #57 e #61 — a prioridade aqui é interface, não dados. Os "Adaptadores" de inclusão (#50–54) compartilham uma única arquitetura de transformação de conteúdo (mesmo nó do grafo, parâmetro de perfil diferente).
- Critério de saída: plataforma tem um diferencial defensável que um concorrente genérico não replica em poucos meses.

### Fase 3 — Gamificação e Produção Visual (engajamento e retenção)
**Objetivo:** transformar uso utilitário em uso desejado pelo aluno, não só pelo professor.
- Ferramentas: #24–34, #44–49, #63–68
- Trabalho técnico: reaproveitar diretamente o design de *Origins* para #24, #32, #33; os simuladores (#63–68) precisam de guardrails de curadoria histórica mais rígidos — vale um prompt de revisão dedicado, não só geração direta.
- Critério de saída: NPS de alunos sobe de forma mensurável, não só de professores.

### Fase 4 — Inovação e Comercialização Institucional
**Objetivo:** converter profundidade de produto em modelo de negócio escalável.
- Ferramentas: #69–78, #36–37 em escala institucional, multi-tenant para redes/secretarias
- Trabalho técnico: multi-tenant real no Postgres (hoje o schema já tem `User`/`school`, falta isolamento por instituição e relatórios agregados), faturamento por escola, exportação de relatórios para gestão (SAEB/cobertura BNCC).
- Realidade do ciclo de venda: venda institucional para secretaria municipal/rede pública normalmente passa por processo licitatório formal (Lei 14.133/2021) ou, no mínimo, ciclo de aprovação orçamentária — isso é medido em **meses**, não semanas, e costuma ter janela fixa no calendário (início de ano letivo/exercício fiscal). O critério de saída abaixo deve ser lido com esse prazo em mente; não é sinal de execução lenta se a Fase 4 levar mais tempo de calendário que as fases técnicas anteriores.
- Critério de saída: primeira venda institucional fechada (secretaria municipal ou rede de escolas) — ou, como marco intermediário mais realista dentro do próprio ano letivo, uma escola/rede usando em piloto pago ou gratuito com compromisso formal de avaliação, não só assinatura individual de professor.


---

## 6. ProfHistória IA — Descrição da Plataforma

**Posicionamento:** a única plataforma de IA educacional **exclusivamente** dedicada a História — não um produto multidisciplinar genérico com um módulo de História encaixado.

**Relação com o que já existe:** ProfHistória IA é o nome voltado ao professor/escola (marca comercial); o **HistóriaIA Copilot** já em construção — agentes LangGraph, RAG sobre Qdrant, backend NestJS com cache/observabilidade — é o motor por trás dela. Não são dois projetos: é produto (ProfHistória IA) sobre engine (HistóriaIA Copilot).

**Os quatro pilares:**

1. **Rigor curricular real** — toda geração é ancorada em BNCC + CRMG via RAG, não em conhecimento genérico do modelo. A coleção `historia_paracatu` é o protótipo de um padrão replicável: cada município/rede pode ter sua própria camada de história local sobre a mesma base nacional.
2. **Inclusão como infraestrutura, não recurso à parte** — os "Adaptadores" (TEA, TDAH, DI, baixa visão, não alfabetizados) não são uma ferramenta isolada num canto do catálogo: são uma camada que atravessa todo o catálogo.
3. **Gamificação com fundamento pedagógico** — jogos e mecânicas não são "enfeite de engajamento": cada um é desenhado a partir de uma habilidade BNCC específica, com avaliação de aprendizagem embutida.
4. **História local como diferencial estrutural** — nenhum concorrente nacional genérico vai investir em cobrir um município específico com profundidade. É o tipo de fosso competitivo que uma rede grande de EdTech não reproduz rápido — e é o que mais conecta a sala de aula à comunidade real do aluno.

**Modelo de negócio:**
- **Plano Professor** (freemium → premium individual): planejamento, resumos, quiz, UNO — gancho de adoção, baixo custo marginal de geração.
- **Plano Professor Premium**: corretor discursivo, laboratório de fontes, simuladores de IA conversacional, produção visual de maior acabamento.
- **Plano Institucional/Escola**: inclusão completa (Adaptadores + PEI), simulados SAEB/ENEM com relatório de gestão, rastreamento de cobertura BNCC.
- **Plano Rede/Secretaria**: história local customizada por município, multi-tenant, relatórios agregados entre escolas, parcerias de patrimônio/turismo cultural.

**O que evita ser:** mais um "ChatGPT com prompt de professor". A defesa competitiva não é "ter IA" — qualquer concorrente tem. É ter (1) curadoria curricular verificável via RAG, (2) inclusão como arquitetura e não feature, e (3) profundidade de história local que exige trabalho real de curadoria por região, não só prompt engineering genérico.
