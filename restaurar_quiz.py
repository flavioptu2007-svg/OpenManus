#!/usr/bin/env python3
"""Append missing React components to quiz_historico.html after corruption."""
import re


html_path = "/home/flavio/OpenManus/quiz_historico.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# The PERGUNTAS array ends with `    ];` at the end of the file
# We need to add CONQUISTAS, helpers, SoundFX, App, and ReactDOM.render

CODA = """

    // ---- Conquistas -------------------------------------------------------
    const CONQUISTAS = [
      { id:"c1", nome:"Primeiros Passos", desc:"Complete seu primeiro quiz", icone:"fa-star", cond:p=>p.totalJogadas>=1 },
      { id:"c2", nome:"Historiador Iniciante", desc:"Complete 5 quizzes", icone:"fa-book", cond:p=>p.totalJogadas>=5 },
      { id:"c3", nome:"Historiador Dedicado", desc:"Complete 20 quizzes", icone:"fa-graduation-cap", cond:p=>p.totalJogadas>=20 },
      { id:"c4", nome:"Mestre da Historia", desc:"Complete 50 quizzes", icone:"fa-crown", cond:p=>p.totalJogadas>=50 },
      { id:"c5", nome:"Nota Maxima", desc:"Tire 100% em um quiz", icone:"fa-trophy", cond:p=>p.perfeitos>=1 },
      { id:"c6", nome:"Sequencia de Ouro", desc:"Acima de 90% em 3 quizzes seguidos", icone:"fa-fire", cond:p=>p.sequencias>=1 },
      { id:"c7", nome:"Explorador do 6 Ano", desc:"Complete todos os temas do 6 ano", icone:"fa-archway", cond:p=>p.anosCompletos.includes("6 Ano") },
      { id:"c8", nome:"Explorador do 7 Ano", desc:"Complete todos os temas do 7 ano", icone:"fa-ship", cond:p=>p.anosCompletos.includes("7 Ano") },
      { id:"c9", nome:"Explorador do 8 Ano", desc:"Complete todos os temas do 8 ano", icone:"fa-industry", cond:p=>p.anosCompletos.includes("8 Ano") },
      { id:"c10", nome:"Explorador do 9 Ano", desc:"Complete todos os temas do 9 ano", icone:"fa-globe", cond:p=>p.anosCompletos.includes("9 Ano") },
      { id:"c11", nome:"Mestre dos Temas", desc:"Complete todos os anos", icone:"fa-earth-americas", cond:p=>p.anosCompletos.length>=4 },
      { id:"c12", nome:"Velocista", desc:"Complete um quiz no modo Tempo em menos de 60s", icone:"fa-stopwatch", cond:p=>p.temposRapidos>=1 },
    ];

    // ---- SoundFX (Web Audio API) -------------------------------------------
    const SoundFX = (() => {
      let ctx = null, enabled = true;
      function getCtx() {
        if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (ctx.state === "suspended") ctx.resume();
        return ctx;
      }
      function playTone(freq, dur, type, vol) {
        if (!enabled) return;
        try {
          const c = getCtx(), o = c.createOscillator(), g = c.createGain();
          o.type = type || "sine"; o.frequency.value = freq;
          g.gain.setValueAtTime(vol||0.15, c.currentTime);
          g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + dur);
          o.connect(g); g.connect(c.destination);
          o.start(c.currentTime); o.stop(c.currentTime + dur);
        } catch(e) {}
      }
      function playNoise(dur) {
        if (!enabled) return;
        try {
          const c = getCtx(), buf = c.createBuffer(1, c.sampleRate * dur, c.sampleRate);
          const d = buf.getChannelData(0);
          for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (1 - i/d.length);
          const s = c.createBufferSource(), g = c.createGain();
          s.buffer = buf; g.gain.setValueAtTime(0.08, c.currentTime);
          g.gain.exponentialRampToValueAtTime(0.001, c.currentTime + dur);
          s.connect(g); g.connect(c.destination); s.start();
        } catch(e) {}
      }
      return {
        correct() { playTone(523, 0.15, "sine", 0.12); setTimeout(() => playTone(659, 0.15, "sine", 0.12), 120); setTimeout(() => playTone(784, 0.25, "sine", 0.12), 240); },
        wrong() { playTone(300, 0.12, "triangle", 0.1); setTimeout(() => playTone(200, 0.2, "triangle", 0.1), 130); },
        win() { [523, 659, 784, 1047].forEach((f,i) => setTimeout(() => playTone(f, 0.2, "sine", 0.12), i*150)); setTimeout(() => playNoise(0.4), 600); },
        conquista() { playTone(880, 0.1, "sine", 0.1); setTimeout(() => playTone(1100, 0.15, "sine", 0.1), 100); setTimeout(() => playTone(1320, 0.2, "sine", 0.1), 200); },
        toggle() { enabled = !enabled; return (enabled = !enabled); },
        get enabled() { return enabled; }
      };
    })();

    // ---- Helpers -----------------------------------------------------------
    const shuffle = (arr) => { const a=[...arr]; for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; };
    const LS = { quiz: "profhistoria_quiz_progresso" };
    const carregarProgresso = () => {
      try { const d = localStorage.getItem(LS.quiz); return d ? JSON.parse(d) : null; } catch { return null; }
    };

    // ---- Componente Principal ----------------------------------------------
    function App() {
      const [ano, setAno] = React.useState("all");
      const [tema, setTema] = React.useState("all");
      const [dificuldade, setDificuldade] = React.useState("all");
      const [modo, setModo] = React.useState("estudo");
      const [perguntaAtual, setPerguntaAtual] = React.useState(0);
      const [acertos, setAcertos] = React.useState(0);
      const [respondido, setRespondido] = React.useState(false);
      const [feedback, setFeedback] = React.useState(null);
      const [jogoAtivo, setJogoAtivo] = React.useState(false);
      const [jogoFinalizado, setJogoFinalizado] = React.useState(false);
      const [tempoRestante, setTempoRestante] = React.useState(60);
      const [tempoTotal, setTempoTotal] = React.useState(0);
      const [progresso, setProgresso] = React.useState(carregarProgresso() || {
        totalJogadas:0, perfeitos:0, sequencias:0, temposRapidos:0,
        anosCompletos:[], temasCompletos:[], conquistas:[], ultimosAcertos:[], historico:[]
      });
      const [mostrarConquistas, setMostrarConquistas] = React.useState(false);
      const [novasConquistas, setNovasConquistas] = React.useState([]);
      const timerRef = React.useRef(null);

      // Perguntas filtradas
      const perguntas = React.useMemo(() => {
        let p = PERGUNTAS;
        if (ano !== "all") p = p.filter(q => q.ano === ano);
        if (tema !== "all") p = p.filter(q => q.tema === tema);
        if (dificuldade !== "all") p = p.filter(q => q.dif === dificuldade);
        if (!jogoAtivo) return p;
        return shuffle(p);
      }, [ano, tema, dificuldade, jogoAtivo]);

      const q = perguntas[perguntaAtual];

      // Verificar conquistas
      const verificarConquistas = (prog) => {
        const novas = [];
        CONQUISTAS.forEach(c => {
          if (!prog.conquistas.includes(c.id) && c.cond(prog)) novas.push(c);
        });
        return novas;
      };

      // Responder pergunta
      const responder = (idx) => {
        if (respondido || !q) return;
        setRespondido(true);
        const correto = idx === q.resp;
        const fb = correto ? "correto" : "errado";
        setFeedback(fb);

        if (correto) { SoundFX.correct(); setAcertos(a => a+1); }
        else { SoundFX.wrong(); }

        const novoProg = { ...progresso };
        if (perguntaAtual + 1 >= perguntas.length) {
          // Quiz completo
          if (correto) { setAcertos(a => a+1); }
          setTimeout(() => finalizarQuiz(novoProg), 1200);
        }
      };

      const finalizarQuiz = (prog) => {
        clearInterval(timerRef.current);
        setJogoFinalizado(true);
        SoundFX.win();
        prog.totalJogadas++;
        prog.ultimosAcertos.push(acertos/perguntas.length);
        if (acertos === perguntas.length) prog.perfeitos++;
        if (modo === "tempo" && tempoRestante > 0) prog.temposRapidos++;
        // Check achievements
        const novas = verificarConquistas(prog);
        if (novas.length > 0) {
          setNovasConquistas(novas);
          setMostrarConquistas(true);
          prog.conquistas = [...prog.conquistas, ...novas.map(c=>c.id)];
          setTimeout(() => novas.forEach(c => SoundFX.conquista()), 300);
        }
        localStorage.setItem(LS.quiz, JSON.stringify(prog));
        setProgresso(prog);
      };

      const iniciarQuiz = () => {
        setPerguntaAtual(0); setAcertos(0); setRespondido(false);
        setFeedback(null); setJogoFinalizado(false); setJogoAtivo(true);
        setNovasConquistas([]); setMostrarConquistas(false);
        if (modo === "tempo") {
          setTempoRestante(60);
          const start = Date.now();
          timerRef.current = setInterval(() => {
            const elapsed = Math.floor((Date.now() - start) / 1000);
            setTempoRestante(60 - elapsed);
            setTempoTotal(elapsed);
            if (elapsed >= 60) finalizarQuiz({...progresso});
          }, 1000);
        }
      };

      const reiniciar = () => { setJogoAtivo(false); setPerguntaAtual(0); setAcertos(0); setRespondido(false); setFeedback(null); setJogoFinalizado(false); clearInterval(timerRef.current); SoundFX.correct(); };

      const avancar = () => {
        if (perguntaAtual + 1 < perguntas.length) {
          setPerguntaAtual(p => p+1);
          setRespondido(false);
          setFeedback(null);
        } else {
          finalizarQuiz({...progresso});
        }
      };

      // Sound toggle button
      const soundBtn = React.createElement("button", {
        onClick: () => { SoundFX.toggle(); },
        className: "fixed top-2 right-2 z-50 text-xl bg-white rounded-full w-9 h-9 flex items-center justify-center shadow hover:scale-110 transition",
        title: "Ativar/Desativar som"
      }, SoundFX.enabled ? "\\u{1F50A}" : "\\u{1F507}");

      // Nao iniciado - tela de configuracao
      if (!jogoAtivo) {
        const anos = Object.keys(TEMAS);
        const temasList = ano !== "all" ? TEMAS[ano] : [];
        return React.createElement("div", { className: "max-w-3xl mx-auto p-4 space-y-4" },
          soundBtn,
          React.createElement("div", { className: "bg-white rounded-xl shadow-lg p-6 space-y-4" },
            React.createElement("h1", { className: "text-2xl font-bold text-center text-indigo-900" }, "\\u{1F3AF} Quiz Historico"),
            React.createElement("p", { className: "text-sm text-center text-gray-500" }, perguntas.length + " perguntas disponiveis"),
            // Ano filter
            React.createElement("div", { className: "flex flex-wrap gap-2 justify-center" },
              React.createElement("button", { onClick: () => { setAno("all"); setTema("all"); }, className: "px-3 py-1 rounded-full text-sm " + (ano==="all"?"bg-indigo-800 text-white":"bg-gray-200") }, "Todos"),
              anos.map(a => React.createElement("button", { key: a, onClick: () => { setAno(a); setTema("all"); }, className: "px-3 py-1 rounded-full text-sm " + (ano===a?"bg-indigo-800 text-white":"bg-gray-200") }, a))
            ),
            // Tema filter (if ano selected)
            ano !== "all" && React.createElement("div", { className: "flex flex-wrap gap-2 justify-center" },
              React.createElement("button", { onClick: () => setTema("all"), className: "px-3 py-1 rounded-full text-sm " + (tema==="all"?"bg-indigo-800 text-white":"bg-gray-200") }, "Todos temas"),
              temasList.map(t => React.createElement("button", { key: t.id, onClick: () => setTema(t.id), className: "px-3 py-1 rounded-full text-sm " + (tema===t.id?"bg-indigo-800 text-white":"bg-gray-200") }, t.nome))
            ),
            // Dificuldade
            React.createElement("div", { className: "flex flex-wrap gap-2 justify-center" },
              ["all","facil","medio","dificil"].map(d => React.createElement("button", {
                key: d, onClick: () => setDificuldade(d),
                className: "px-3 py-1 rounded-full text-sm " + (dificuldade===d?"bg-indigo-800 text-white":"bg-gray-200")
              }, d==="all"?"Todas":d.charAt(0).toUpperCase()+d.slice(1)))
            ),
            // Modo
            React.createElement("div", { className: "flex gap-2 justify-center" },
              ["estudo","quiz","tempo"].map(m => React.createElement("button", {
                key: m, onClick: () => setModo(m),
                className: "px-4 py-2 rounded-lg text-sm font-medium " + (modo===m?"bg-indigo-600 text-white":"bg-gray-100 border")
              }, m==="estudo"? "\\u{1F4D6} Estudo" : m==="quiz"? "\\u{1F3AF} Quiz" : "\\u{23F1} Tempo"))
            ),
            (perguntas.length > 0) && React.createElement("button", {
              onClick: iniciarQuiz,
              className: "w-full py-3 bg-indigo-700 text-white rounded-lg font-bold text-lg hover:bg-indigo-800 transition"
            }, "\\u{25B6} Iniciar " + (modo==="estudo"?"Estudo":modo==="quiz"?"Quiz":"Tempo") + " (" + perguntas.length + " perguntas)")
          ),
          // Progress summary
          React.createElement("div", { className: "bg-white rounded-xl shadow-lg p-4 text-sm text-gray-600" },
            "Progresso: " + progresso.totalJogadas + " jogos completados, " + progresso.conquistas.length + "/" + CONQUISTAS.length + " conquistas desbloqueadas"
          )
        );
      }

      // Finalizado
      if (jogoFinalizado) {
        const pct = Math.round((acertos / perguntas.length) * 100);
        return React.createElement("div", { className: "max-w-md mx-auto p-4 space-y-4" },
          soundBtn,
          React.createElement("div", { className: "bg-white rounded-xl shadow-lg p-8 text-center space-y-4" },
            React.createElement("div", { className: "text-5xl" }, pct >= 80 ? "\\u{1F3C6}" : "\\u{1F4DA}"),
            React.createElement("h2", { className: "text-2xl font-bold" }, "Quiz Finalizado!"),
            React.createElement("p", { className: "text-lg" }, "Acertou " + acertos + " de " + perguntas.length + " perguntas"),
            React.createElement("div", { className: "w-full bg-gray-200 rounded-full h-4" },
              React.createElement("div", { className: "h-4 rounded-full transition-all duration-700 " + (pct>=60?"bg-green-500":"bg-orange-500"), style: {width: pct+"%"} })
            ),
            React.createElement("p", { className: "text-3xl font-bold " + (pct>=60?"text-green-600":"text-orange-600") }, pct + "%"),
            mostrarConquistas && React.createElement("div", { className: "space-y-2" },
              React.createElement("h3", { className: "font-bold text-yellow-600" }, "\\u{1F3C6} Novas Conquistas!"),
              novasConquistas.map(c => React.createElement("div", { key: c.id, className: "bg-yellow-50 rounded-lg p-2 border border-yellow-300 flex items-center gap-2" },
                React.createElement("i", { className: "fas " + c.icone + " text-yellow-500" }), React.createElement("span", null, c.nome + ": " + c.desc)
              ))
            ),
            React.createElement("button", { onClick: reiniciar, className: "w-full py-2 bg-indigo-700 text-white rounded-lg font-bold hover:bg-indigo-800 transition" }, "\\u{1F504} Novo Quiz")
          )
        );
      }

      // Jogo ativo
      const pct = ((perguntaAtual + 1) / perguntas.length) * 100;
      return React.createElement("div", { className: "max-w-2xl mx-auto p-4 space-y-4" },
        soundBtn,
        // Progress bar
        React.createElement("div", { className: "bg-white rounded-lg shadow p-3 flex items-center gap-4 text-sm" },
          React.createElement("div", { className: "flex-1" },
            React.createElement("div", { className: "w-full bg-gray-200 rounded-full h-2" },
              React.createElement("div", { className: "h-2 rounded-full bg-indigo-500 transition-all", style: {width: pct+"%"} })
            )
          ),
          React.createElement("span", { className: "font-medium" }, (perguntaAtual+1) + "/" + perguntas.length),
          React.createElement("span", null, "Acertos: " + acertos),
          modo==="tempo" && React.createElement("span", { className: "font-mono text-orange-600" }, tempoRestante + "s")
        ),
        // Question card
        q && React.createElement("div", { className: "bg-white rounded-xl shadow-lg p-6 space-y-4" },
          React.createElement("div", { className: "flex justify-between items-start" },
            React.createElement("span", { className: "text-xs px-2 py-1 rounded bg-gray-100 text-gray-600" }, q.dif === "facil" ? "Facil" : q.dif === "medio" ? "Medio" : "Dificil"),
            React.createElement("span", { className: "text-xs text-gray-400" }, q.ano)
          ),
          React.createElement("p", { className: "text-lg font-medium" }, q.pergunta),
          React.createElement("div", { className: "space-y-2" },
            q.opts.map((o, i) => React.createElement("button", {
              key: i, onClick: () => responder(i), disabled: respondido,
              className: "w-full text-left p-3 rounded-lg border transition " +
                (respondido
                  ? (i === q.resp ? "bg-green-100 border-green-400" : (i === q.resp ? "" : "bg-red-50 border-red-300"))
                  : "hover:bg-indigo-50 hover:border-indigo-300 border-gray-200")
            }, o))
          ),
          respondido && React.createElement("div", { className: "p-3 rounded-lg " + (feedback==="correto"?"bg-green-50 text-green-800":"bg-red-50 text-red-800") },
            React.createElement("p", { className: "font-medium" }, feedback === "correto" ? "\\u{2705} Correto!" : "\\u{274C} Errado!"),
            React.createElement("p", { className: "text-sm mt-1" }, q.exp)
          ),
          respondido && React.createElement("button", {
            onClick: perguntaAtual + 1 < perguntas.length ? avancar : () => finalizarQuiz({...progresso}),
            className: "w-full py-2 bg-indigo-700 text-white rounded-lg font-bold hover:bg-indigo-800 transition"
          }, perguntaAtual + 1 < perguntas.length ? "\\u{25B6} Proxima" : "\\u{1F3C1} Finalizar")
        )
      );
    }

    // ---- Render ------------------------------------------------------------
    const root = ReactDOM.createRoot(document.getElementById("root"));
    root.render(React.createElement(App));
  </script>
</body>
</html>
"""

with open(html_path, "r+", encoding="utf-8") as f:
    content = f.read()
    # Verify the file ends with ];
    if content.rstrip().endswith("];"):
        f.write(CODA)
        print(f"✅ Appended {len(CODA)} chars of React components")
        print(
            f"   File now has {len(re.findall(r'id:\"q\\d+\"', content + CODA))} questions"
        )
    else:
        print("ERROR: File does not end with ]; - unexpected format")
