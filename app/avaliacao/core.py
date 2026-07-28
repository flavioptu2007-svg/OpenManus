"""
Núcleo do Sistema de Avaliação de Provas Objetivas (V/F).

Refatorado a partir do CLI original para uso programático e como ferramenta OpenManus.
Mantém compatibilidade: dados em JSON, mesmo formato de arquivos.
"""

import datetime
import json
import os
import re
import zipfile
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple


class SistemaAvaliacao:
    """Sistema de avaliação de provas objetivas (V/F).

    Operações principais: criar/editar disciplinas, adicionar alunos,
    definir gabarito, calcular notas, gerar relatórios, visualizar resultados.
    """

    def __init__(self, diretorio_dados: str = "dados_avaliacoes"):
        self.diretorio_dados = diretorio_dados
        os.makedirs(self.diretorio_dados, exist_ok=True)

    # ── Utilitários ──────────────────────────────────────────────

    def _caminho(self, nome_arquivo: str) -> str:
        return os.path.join(self.diretorio_dados, nome_arquivo)

    def _sanitizar_nome(self, nome: str) -> str:
        return re.sub(r'[\\/*?:"<>|]', "_", nome.strip())

    def _caminho_json(self, disciplina: str) -> str:
        return self._caminho(f"{disciplina}.json")

    def carregar(self, disciplina: str) -> Optional[dict]:
        """Carrega os dados de uma disciplina do disco."""
        caminho = self._caminho_json(disciplina)
        if not os.path.exists(caminho):
            return None
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            return None

    def salvar(self, disciplina: str, dados: dict) -> bool:
        """Salva os dados de uma disciplina no disco."""
        try:
            with open(self._caminho_json(disciplina), "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            return True
        except IOError:
            return False

    # ── Operações principais ─────────────────────────────────────

    def criar_disciplina(
        self,
        nome: str,
        num_questoes: int,
        alunos: Optional[List[Dict[str, Any]]] = None,
        gabarito: Optional[List[str]] = None,
        sobrescrever: bool = False,
    ) -> dict:
        """Cria uma nova disciplina ou adiciona alunos a uma existente.

        Args:
            nome: Nome da disciplina.
            num_questoes: Quantidade de questões da prova.
            alunos: Lista de dicts com 'nome' e 'respostas'.
            gabarito: Lista de respostas V/F.
            sobrescrever: Se True, sobrescreve dados existentes.

        Returns:
            Dict com status e mensagem.
        """
        disciplina = self._sanitizar_nome(nome)
        dados_existentes = self.carregar(disciplina) if not sobrescrever else None

        if dados_existentes and not sobrescrever:
            # Modo adição: mescla alunos novos com existentes
            if dados_existentes["num_questoes"] != num_questoes:
                return {
                    "status": "erro",
                    "mensagem": (
                        f"A disciplina '{disciplina}' já existe com "
                        f"{dados_existentes['num_questoes']} questões. "
                        f"Não é possível alterar para {num_questoes}."
                    ),
                }
            nomes_existentes = {a["nome"].lower() for a in dados_existentes["alunos"]}
        else:
            nomes_existentes = set()
            dados_existentes = None

        alunos_final = dados_existentes["alunos"] if dados_existentes else []
        alunos_novos = []

        if alunos:
            for aluno in alunos:
                nome_aluno = aluno.get("nome", "").strip()
                respostas = [r.upper() for r in aluno.get("respostas", [])]

                if not nome_aluno:
                    continue
                if len(respostas) != num_questoes:
                    continue
                if any(r not in ("V", "F") for r in respostas):
                    continue
                if nome_aluno.lower() in nomes_existentes:
                    continue

                alunos_final.append({"nome": nome_aluno, "respostas": respostas})
                alunos_novos.append(nome_aluno)
                nomes_existentes.add(nome_aluno.lower())

        dados = {
            "disciplina": disciplina,
            "num_questoes": num_questoes,
            "alunos": alunos_final,
            "gabarito": (
                gabarito
                if gabarito
                else (dados_existentes.get("gabarito") if dados_existentes else None)
            ),
            "ultima_atualizacao": datetime.datetime.now().isoformat(),
        }

        if not self.salvar(disciplina, dados):
            return {"status": "erro", "mensagem": f"Erro ao salvar '{disciplina}'."}

        return {
            "status": "sucesso",
            "disciplina": disciplina,
            "total_alunos": len(alunos_final),
            "alunos_novos": len(alunos_novos),
            "alunos_adicionados": alunos_novos,
            "num_questoes": num_questoes,
            "mensagem": (
                f"Disciplina '{disciplina}' salva com {len(alunos_final)} aluno(s) "
                f"({len(alunos_novos)} novo(s))."
            ),
        }

    def adicionar_alunos(
        self, disciplina: str, alunos: List[Dict[str, Any]]
    ) -> dict:
        """Adiciona alunos a uma disciplina existente.

        Args:
            disciplina: Nome da disciplina.
            alunos: Lista de dicts com 'nome' e 'respostas'.

        Returns:
            Dict com status e resultado.
        """
        dados = self.carregar(disciplina)
        if not dados:
            return {
                "status": "erro",
                "mensagem": f"Disciplina '{disciplina}' não encontrada.",
            }

        num_questoes = dados["num_questoes"]
        nomes_existentes = {a["nome"].lower() for a in dados["alunos"]}
        adicionados = []

        for aluno in alunos:
            nome = aluno.get("nome", "").strip()
            respostas = [r.upper() for r in aluno.get("respostas", [])]

            if not nome:
                continue
            if len(respostas) != num_questoes:
                continue
            if any(r not in ("V", "F") for r in respostas):
                continue
            if nome.lower() in nomes_existentes:
                continue

            dados["alunos"].append({"nome": nome, "respostas": respostas})
            nomes_existentes.add(nome.lower())
            adicionados.append(nome)

        if not adicionados:
            return {
                "status": "aviso",
                "mensagem": "Nenhum aluno novo foi adicionado (já existem ou dados inválidos).",
            }

        dados["ultima_atualizacao"] = datetime.datetime.now().isoformat()
        self.salvar(disciplina, dados)

        return {
            "status": "sucesso",
            "disciplina": disciplina,
            "total_alunos": len(dados["alunos"]),
            "alunos_adicionados": adicionados,
            "mensagem": f"{len(adicionados)} aluno(s) adicionado(s) com sucesso.",
        }

    def definir_gabarito(
        self, disciplina: str, gabarito: List[str]
    ) -> dict:
        """Define ou atualiza o gabarito de uma disciplina.

        Args:
            disciplina: Nome da disciplina.
            gabarito: Lista de respostas V/F.

        Returns:
            Dict com status e resultado.
        """
        dados = self.carregar(disciplina)
        if not dados:
            return {
                "status": "erro",
                "mensagem": f"Disciplina '{disciplina}' não encontrada.",
            }

        gabarito_upper = [r.upper() for r in gabarito]
        if len(gabarito_upper) != dados["num_questoes"]:
            return {
                "status": "erro",
                "mensagem": (
                    f"O gabarito deve ter {dados['num_questoes']} respostas "
                    f"(recebido {len(gabarito_upper)})."
                ),
            }

        dados["gabarito"] = gabarito_upper
        dados["ultima_atualizacao"] = datetime.datetime.now().isoformat()
        self.salvar(disciplina, dados)

        return {
            "status": "sucesso",
            "disciplina": disciplina,
            "gabarito": gabarito_upper,
            "mensagem": f"Gabarito definido: {' '.join(gabarito_upper)}",
        }

    def gerar_resultados(self, disciplina: str) -> dict:
        """Calcula notas e gera relatórios para uma disciplina.

        Requer que a disciplina exista, tenha alunos e gabarito definido.

        Args:
            disciplina: Nome da disciplina.

        Returns:
            Dict com resultados, estatísticas e caminhos dos arquivos gerados.
        """
        dados = self.carregar(disciplina)
        if not dados:
            return {"status": "erro", "mensagem": f"Disciplina '{disciplina}' não encontrada."}

        if not dados["alunos"]:
            return {"status": "erro", "mensagem": f"Não há alunos cadastrados em '{disciplina}'."}

        if not dados.get("gabarito"):
            return {
                "status": "erro",
                "mensagem": f"Gabarito não definido para '{disciplina}'. Use 'definir_gabarito' primeiro.",
            }

        gabarito = dados["gabarito"]
        num_questoes = dados["num_questoes"]
        resultados, estatisticas = self._calcular_notas(dados, gabarito)
        info = self._gerar_arquivos_relatorio(
            disciplina, resultados, estatisticas, num_questoes, gabarito
        )

        return {
            "status": "sucesso",
            "disciplina": disciplina,
            "num_questoes": num_questoes,
            "total_alunos": len(resultados),
            "media": info["media"],
            "maior_nota": info["maior"],
            "menor_nota": info["menor"],
            "resultados": resultados,
            "estatisticas_questoes": dict(estatisticas),
            "arquivos": info["arquivos"],
            "mensagem": (
                f"Resultados gerados para '{disciplina}'. "
                f"Média: {info['media']:.2f} | Maior: {info['maior']} | Menor: {info['menor']}"
            ),
        }

    # ── Métodos internos de cálculo ──────────────────────────────

    def _calcular_notas(
        self, dados: dict, gabarito: List[str]
    ) -> Tuple[List[dict], Dict[int, int]]:
        """Calcula notas e estatísticas por questão."""
        num_questoes = dados["num_questoes"]
        resultados = []
        estatisticas_questoes: Dict[int, int] = defaultdict(int)

        for aluno in dados["alunos"]:
            nome = aluno["nome"]
            respostas = aluno["respostas"]

            todas_iguais = len(set(respostas)) == 1

            if todas_iguais:
                pontuacao = 0
                observacao = f"Todas as respostas '{respostas[0]}' — nota zerada"
            else:
                acertos = [
                    i + 1
                    for i, (ra, rg) in enumerate(zip(respostas, gabarito))
                    if ra == rg
                ]
                for q in acertos:
                    estatisticas_questoes[q] += 1
                pontuacao = len(acertos)
                observacao = f"{pontuacao}/{num_questoes} acertos"

            resultados.append({
                "nome": nome,
                "pontuacao": pontuacao,
                "observacao": observacao,
            })

        return resultados, estatisticas_questoes

    def _gerar_arquivos_relatorio(
        self,
        disciplina: str,
        resultados: List[dict],
        estatisticas_questoes: Dict[int, int],
        num_questoes: int,
        gabarito: List[str],
    ) -> dict:
        """Gera arquivos de relatório (alfabético, por nota, cache)."""
        total_alunos = len(resultados)
        pontuacoes = [r["pontuacao"] for r in resultados]
        media = sum(pontuacoes) / total_alunos if total_alunos > 0 else 0
        maior, menor = max(pontuacoes), min(pontuacoes)

        alfabetica = sorted(resultados, key=lambda r: r["nome"].lower())
        por_nota = sorted(resultados, key=lambda r: (-r["pontuacao"], r["nome"].lower()))

        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Arquivo alfabético
        caminho_alf = self._caminho(f"{disciplina}_alfabetico.txt")
        with open(caminho_alf, "w", encoding="utf-8") as f:
            f.write(f"RESULTADOS DE {disciplina.upper()} — ORDEM ALFABÉTICA\n")
            f.write(f"Data/Hora: {data_hora}\n")
            f.write(f"Total de alunos: {total_alunos} | Questões: {num_questoes} | Média: {media:.2f}\n")
            f.write("-" * 70 + "\n")
            for r in alfabetica:
                f.write(f"{r['nome']:<35} {r['pontuacao']:>3} pontos   {r['observacao']}\n")

        # Arquivo por nota
        caminho_notas = self._caminho(f"{disciplina}_notas.txt")
        with open(caminho_notas, "w", encoding="utf-8") as f:
            f.write(f"RESULTADOS DE {disciplina.upper()} — ORDEM DE NOTAS\n")
            f.write(f"Data/Hora: {data_hora}\n")
            f.write(f"Total de alunos: {total_alunos} | Questões: {num_questoes}\n")
            f.write(f"Média: {media:.2f} | Maior nota: {maior} | Menor nota: {menor}\n\n")

            f.write("ESTATÍSTICAS POR QUESTÃO (acertos):\n")
            f.write("-" * 40 + "\n")
            for q in range(1, num_questoes + 1):
                acertos = estatisticas_questoes.get(q, 0)
                pct = (acertos / total_alunos) * 100
                f.write(f"Questão {q}: {acertos}/{total_alunos} ({pct:.1f}%)\n")
            f.write("-" * 40 + "\n\n")

            f.write("RANKING:\n")
            f.write("-" * 70 + "\n")
            posicao, nota_ant = 0, None
            for i, r in enumerate(por_nota, 1):
                if r["pontuacao"] != nota_ant:
                    posicao = i
                    nota_ant = r["pontuacao"]
                f.write(f"{posicao:>3}º  {r['nome']:<35} {r['pontuacao']:>3} pontos   {r['observacao']}\n")
            f.write("-" * 70 + "\n")
            f.write(f"\nMédia da turma: {media:.2f} pontos\n")

        # Cache JSON
        cache = {
            "resultados": resultados,
            "estatisticas_questoes": dict(estatisticas_questoes),
            "media": media,
            "maior": maior,
            "menor": menor,
            "gerado_em": data_hora,
        }
        with open(self._caminho(f"{disciplina}_cache.json"), "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

        return {
            "media": media,
            "maior": maior,
            "menor": menor,
            "arquivos": {
                "alfabetico": caminho_alf,
                "notas": caminho_notas,
                "cache": self._caminho(f"{disciplina}_cache.json"),
            },
        }

    # ── Consulta e visualização ─────────────────────────────────

    def listar_disciplinas(self) -> List[dict]:
        """Lista todas as disciplinas cadastradas com metadados."""
        disciplinas = []
        for arquivo in sorted(os.listdir(self.diretorio_dados)):
            if arquivo.endswith(".json") and not arquivo.endswith("_cache.json"):
                nome = arquivo[:-5]
                dados = self.carregar(nome)
                if dados:
                    disciplinas.append({
                        "nome": nome,
                        "num_questoes": dados["num_questoes"],
                        "total_alunos": len(dados["alunos"]),
                        "tem_gabarito": dados.get("gabarito") is not None,
                        "tem_resultado": os.path.exists(
                            self._caminho(f"{nome}_cache.json")
                        ),
                        "ultima_atualizacao": dados.get("ultima_atualizacao", ""),
                    })
        return disciplinas

    def obter_resultados(self, disciplina: str) -> Optional[dict]:
        """Obtém resultados cacheados de uma disciplina."""
        caminho_cache = self._caminho(f"{disciplina}_cache.json")
        if not os.path.exists(caminho_cache):
            return None
        try:
            with open(caminho_cache, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def obter_dados_completos(self, disciplina: str) -> Optional[dict]:
        """Obtém dados completos de uma disciplina (alunos, gabarito, etc.)."""
        dados = self.carregar(disciplina)
        if not dados:
            return None

        # Adiciona info de resultado se existir
        cache = self.obter_resultados(disciplina)
        if cache:
            dados["resultados"] = cache

        return dados

    def fazer_backup(self) -> dict:
        """Cria um backup zip dos dados."""
        data_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_zip = f"backup_avaliacoes_{data_hora}.zip"
        try:
            with zipfile.ZipFile(nome_zip, "w") as z:
                for arquivo in os.listdir(self.diretorio_dados):
                    z.write(
                        self._caminho(arquivo),
                        arcname=arquivo,
                    )
            return {
                "status": "sucesso",
                "arquivo": nome_zip,
                "mensagem": f"Backup criado: {nome_zip}",
            }
        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro ao criar backup: {e}"}
