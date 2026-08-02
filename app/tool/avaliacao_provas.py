"""
Ferramenta OpenManus para o Sistema de Avaliação de Provas Objetivas (V/F).

Permite que o agente de IA gerencie avaliações de provas de História:
criar disciplinas, adicionar alunos, definir gabarito, calcular notas
e gerar relatórios pedagógicos.
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from app.avaliacao.core import SistemaAvaliacao
from app.exceptions import ToolError
from app.tool.base import BaseTool, ToolResult


_DESCRIPTION = """
Sistema de Avaliação de Provas Objetivas (V/F) — ferramenta para professores
gerenciarem avaliações de múltipla escolha (Verdadeiro/Falso).

Comandos disponíveis:
- criar: Cria uma nova disciplina com alunos e opcionalmente gabarito
- adicionar_alunos: Adiciona alunos a uma disciplina existente
- definir_gabarito: Define o gabarito da prova
- gerar_resultados: Calcula notas e gera relatórios
- listar: Lista todas as disciplinas cadastradas
- ver_disciplina: Exibe dados detalhados de uma disciplina
- ver_resultados: Exibe resultados cacheados de uma disciplina
- backup: Cria um backup zip dos dados
"""


class AvaliacaoProvas(BaseTool):
    """Ferramenta para gerenciar avaliações de provas objetivas (V/F)."""

    name: str = "avaliacao_provas"
    description: str = _DESCRIPTION

    parameters: dict = {
        "type": "object",
        "properties": {
            "command": {
                "description": (
                    "Comando a executar: criar, adicionar_alunos, definir_gabarito, "
                    "gerar_resultados, listar, ver_disciplina, ver_resultados, backup"
                ),
                "enum": [
                    "criar",
                    "adicionar_alunos",
                    "definir_gabarito",
                    "gerar_resultados",
                    "listar",
                    "ver_disciplina",
                    "ver_resultados",
                    "backup",
                ],
                "type": "string",
            },
            "disciplina": {
                "description": "Nome da disciplina (usado nos comandos que operam sobre uma disciplina específica).",
                "type": "string",
            },
            "num_questoes": {
                "description": "Número de questões da prova (usado com o comando 'criar').",
                "type": "integer",
            },
            "alunos": {
                "description": (
                    "Lista de alunos para adicionar. Cada aluno é um objeto com "
                    "'nome' (string) e 'respostas' (lista de strings 'V'/'F'). "
                    "Usado com os comandos 'criar' e 'adicionar_alunos'."
                ),
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string"},
                        "respostas": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["nome", "respostas"],
                },
            },
            "gabarito": {
                "description": (
                    "Lista de respostas do gabarito (ex: ['V', 'F', 'V', 'F']). "
                    "Usado com os comandos 'criar' e 'definir_gabarito'."
                ),
                "type": "array",
                "items": {"type": "string"},
            },
            "sobrescrever": {
                "description": "Se True, sobrescreve dados existentes ao criar uma disciplina.",
                "type": "boolean",
            },
        },
        "required": ["command"],
    }

    sistema: SistemaAvaliacao = Field(default_factory=SistemaAvaliacao, exclude=True)

    async def execute(  # type: ignore[override]
        self,
        *,
        command: str,
        disciplina: Optional[str] = None,
        num_questoes: Optional[int] = None,
        alunos: Optional[List[Dict[str, Any]]] = None,
        gabarito: Optional[List[str]] = None,
        sobrescrever: Optional[bool] = False,
        **kwargs,
    ) -> ToolResult:
        """Executes a command of the evaluation system via the OpenManus tool interface.

        Args:
            command: Command to execute.
            disciplina: Subject name.
            num_questoes: Number of questions.
            alunos: List of students with answers.
            gabarito: Answer key.
            sobrescrever: Whether to overwrite existing data.

        Returns:
            ToolResult with the command output.
        """
        try:
            if command == "criar":
                return self._cmd_criar(
                    disciplina, num_questoes, alunos, gabarito, bool(sobrescrever)
                )
            if command == "adicionar_alunos":
                return self._cmd_adicionar_alunos(disciplina, alunos)
            if command == "definir_gabarito":
                return self._cmd_definir_gabarito(disciplina, gabarito)
            if command == "gerar_resultados":
                return self._cmd_gerar_resultados(disciplina)
            if command == "listar":
                return self._cmd_listar()
            if command == "ver_disciplina":
                return self._cmd_ver_disciplina(disciplina)
            if command == "ver_resultados":
                return self._cmd_ver_resultados(disciplina)
            if command == "backup":
                return self._cmd_backup()
            raise ToolError(
                f"Comando '{command}' não reconhecido. "
                "Comandos válidos: criar, adicionar_alunos, definir_gabarito, "
                "gerar_resultados, listar, ver_disciplina, ver_resultados, backup"
            )
        except ToolError:
            raise
        except Exception as e:
            return ToolResult(error=f"Erro ao executar '{command}': {str(e)}")

    # -- Implementação dos comandos --

    def _cmd_criar(
        self,
        disciplina: Optional[str],
        num_questoes: Optional[int],
        alunos: Optional[List[Dict[str, Any]]],
        gabarito: Optional[List[str]],
        sobrescrever: bool,
    ) -> ToolResult:
        if not disciplina:
            raise ToolError(
                "Parâmetro 'disciplina' é obrigatório para o comando 'criar'."
            )
        if not num_questoes or num_questoes <= 0:
            raise ToolError(
                "Parâmetro 'num_questoes' deve ser um número positivo para o comando 'criar'."
            )

        resultado = self.sistema.criar_disciplina(
            nome=disciplina,
            num_questoes=num_questoes,
            alunos=alunos or [],
            gabarito=gabarito,
            sobrescrever=sobrescrever,
        )

        if resultado["status"] == "erro":
            return ToolResult(error=resultado["mensagem"])

        output = f"✅ {resultado['mensagem']}\n\n"
        output += f"📚 Disciplina: {resultado['disciplina']}\n"
        output += f"📝 Questões: {resultado['num_questoes']}\n"
        output += f"👥 Total de alunos: {resultado['total_alunos']}\n"

        if resultado.get("alunos_adicionados"):
            output += "\nAlunos adicionados:\n"
            for nome in resultado["alunos_adicionados"]:
                output += f"  • {nome}\n"

        return ToolResult(output=output)

    def _cmd_adicionar_alunos(
        self,
        disciplina: Optional[str],
        alunos: Optional[List[Dict[str, Any]]],
    ) -> ToolResult:
        if not disciplina:
            raise ToolError(
                "Parâmetro 'disciplina' é obrigatório para o comando 'adicionar_alunos'."
            )
        if not alunos:
            raise ToolError(
                "Parâmetro 'alunos' é obrigatório para o comando 'adicionar_alunos'."
            )

        resultado = self.sistema.adicionar_alunos(disciplina, alunos)

        if resultado["status"] == "erro":
            return ToolResult(error=resultado["mensagem"])

        output = f"✅ {resultado['mensagem']}\n"
        output += f"📚 Disciplina: {resultado['disciplina']}\n"
        output += f"👥 Total de alunos agora: {resultado['total_alunos']}\n"

        if resultado.get("alunos_adicionados"):
            output += "\nAlunos adicionados:\n"
            for nome in resultado["alunos_adicionados"]:
                output += f"  • {nome}\n"

        return ToolResult(output=output)

    def _cmd_definir_gabarito(
        self,
        disciplina: Optional[str],
        gabarito: Optional[List[str]],
    ) -> ToolResult:
        if not disciplina:
            raise ToolError(
                "Parâmetro 'disciplina' é obrigatório para o comando 'definir_gabarito'."
            )
        if not gabarito:
            raise ToolError(
                "Parâmetro 'gabarito' é obrigatório para o comando 'definir_gabarito'."
            )

        resultado = self.sistema.definir_gabarito(disciplina, gabarito)

        if resultado["status"] == "erro":
            return ToolResult(error=resultado["mensagem"])

        output = f"✅ {resultado['mensagem']}\n"
        output += f"📚 Disciplina: {resultado['disciplina']}\n"
        output += f"✅ Gabarito: {' '.join(resultado['gabarito'])}"

        return ToolResult(output=output)

    def _cmd_gerar_resultados(self, disciplina: Optional[str]) -> ToolResult:
        if not disciplina:
            raise ToolError(
                "Parâmetro 'disciplina' é obrigatório para o comando 'gerar_resultados'."
            )

        resultado = self.sistema.gerar_resultados(disciplina)

        if resultado["status"] == "erro":
            return ToolResult(error=resultado["mensagem"])

        output = f"✅ Resultados gerados para '{resultado['disciplina']}'!\n\n"
        output += "📊 Estatísticas:\n"
        output += f"  • Total de alunos: {resultado['total_alunos']}\n"
        output += f"  • Média: {resultado['media']:.2f}\n"
        output += f"  • Maior nota: {resultado['maior_nota']}\n"
        output += f"  • Menor nota: {resultado['menor_nota']}\n\n"

        output += "📈 Acertos por questão:\n"
        for q in range(1, resultado["num_questoes"] + 1):
            acertos = resultado["estatisticas_questoes"].get(q, 0)
            pct = (
                (acertos / resultado["total_alunos"]) * 100
                if resultado["total_alunos"] > 0
                else 0
            )
            barra = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            output += (
                f"  Q{q}: {barra} {acertos}/{resultado['total_alunos']} ({pct:.1f}%)\n"
            )

        output += "\n🏆 Ranking:\n"
        por_nota = sorted(
            resultado["resultados"], key=lambda r: (-r["pontuacao"], r["nome"].lower())
        )
        posicao, nota_ant = 0, None
        for i, r in enumerate(por_nota, 1):
            if r["pontuacao"] != nota_ant:
                posicao = i
                nota_ant = r["pontuacao"]
            medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(posicao, "  ")
            output += (
                f"  {medalha} {posicao:>2}º  {r['nome']:<30} {r['pontuacao']:>2} pts\n"
            )

        output += "\n📁 Arquivos gerados:\n"
        for tipo, caminho in resultado["arquivos"].items():
            output += f"  • {tipo}: {caminho}\n"

        return ToolResult(output=output)

    def _cmd_listar(self) -> ToolResult:
        disciplinas = self.sistema.listar_disciplinas()

        if not disciplinas:
            return ToolResult(output="📭 Nenhuma disciplina cadastrada ainda.")

        output = "📚 **Disciplinas Cadastradas**\n\n"
        for d in disciplinas:
            status = (
                "✅" if d["tem_resultado"] else ("📝" if d["tem_gabarito"] else "⏳")
            )
            output += (
                f"{status} **{d['nome']}**\n"
                f"   Questões: {d['num_questoes']} | Alunos: {d['total_alunos']}\n"
                f"   Gabarito: {'✅ definido' if d['tem_gabarito'] else '❌ pendente'}\n"
                f"   Resultado: {'✅ calculado' if d['tem_resultado'] else '❌ pendente'}\n"
            )
            if d.get("ultima_atualizacao"):
                output += f"   Última atualização: {d['ultima_atualizacao']}\n"
            output += "\n"

        output += f"Total: {len(disciplinas)} disciplina(s)"
        return ToolResult(output=output)

    def _cmd_ver_disciplina(self, disciplina: Optional[str]) -> ToolResult:
        if not disciplina:
            raise ToolError(
                "Parâmetro 'disciplina' é obrigatório para o comando 'ver_disciplina'."
            )

        dados = self.sistema.obter_dados_completos(disciplina)
        if not dados:
            return ToolResult(error=f"Disciplina '{disciplina}' não encontrada.")

        output = f"📚 **{dados['disciplina'].upper()}**\n"
        output += f"   Questões: {dados['num_questoes']}\n"
        output += f"   Alunos: {len(dados['alunos'])}\n"

        if dados.get("gabarito"):
            output += f"   Gabarito: {' '.join(dados['gabarito'])}\n"

        output += "\n👥 **Alunos cadastrados:**\n"
        for a in dados["alunos"]:
            resp_str = " ".join(a["respostas"])
            output += f"  • {a['nome']:<30} [{resp_str}]\n"

        if dados.get("resultados"):
            r = dados["resultados"]
            output += f"\n📊 **Resultados** (gerado em {r.get('gerado_em', 'N/A')}):\n"
            output += f"   Média: {r['media']:.2f} | Maior: {r['maior']} | Menor: {r['menor']}\n"

        return ToolResult(output=output)

    def _cmd_ver_resultados(self, disciplina: Optional[str]) -> ToolResult:
        if not disciplina:
            raise ToolError(
                "Parâmetro 'disciplina' é obrigatório para o comando 'ver_resultados'."
            )

        cache = self.sistema.obter_resultados(disciplina)
        if not cache:
            return ToolResult(
                error=f"Ainda não há resultados para '{disciplina}'. Use o comando 'gerar_resultados' primeiro."
            )

        output = f"📊 **Resultados: {disciplina}**\n"
        output += f"   Gerado em: {cache.get('gerado_em', 'N/A')}\n"
        output += f"   Média: {cache['media']:.2f} | Maior: {cache['maior']} | Menor: {cache['menor']}\n\n"

        output += "📈 **Acertos por questão:**\n"
        total = len(cache["resultados"])
        for q_str, acertos in sorted(
            cache["estatisticas_questoes"].items(), key=lambda x: int(x[0])
        ):
            pct = (acertos / total) * 100 if total > 0 else 0
            barra = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            output += f"  Q{q_str}: {barra} {acertos}/{total} ({pct:.1f}%)\n"

        output += "\n🏆 **Ranking:**\n"
        por_nota = sorted(
            cache["resultados"], key=lambda r: (-r["pontuacao"], r["nome"].lower())
        )
        posicao, nota_ant = 0, None
        for i, r in enumerate(por_nota, 1):
            if r["pontuacao"] != nota_ant:
                posicao = i
                nota_ant = r["pontuacao"]
            medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(posicao, "  ")
            output += f"  {medalha} {posicao:>2}º  {r['nome']:<30} {r['pontuacao']:>2} pts — {r['observacao']}\n"

        return ToolResult(output=output)

    def _cmd_backup(self) -> ToolResult:
        resultado = self.sistema.fazer_backup()
        if resultado["status"] == "erro":
            return ToolResult(error=resultado["mensagem"])
        return ToolResult(output=f"✅ {resultado['mensagem']}")
