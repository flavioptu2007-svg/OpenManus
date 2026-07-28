"""Tests for SistemaAvaliacao — core evaluation system.

These tests verify:
- Creating disciplines with students
- Adding students to existing disciplines
- Defining answer keys
- Calculating grades and generating reports
- Listing and viewing discipline data
- Backup functionality
"""

import json
import os
import shutil
import tempfile

import pytest

from app.avaliacao.core import SistemaAvaliacao


@pytest.fixture
def sistema():
    """Creates a SistemaAvaliacao instance with a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    sistema = SistemaAvaliacao(diretorio_dados=temp_dir)
    yield sistema
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def disciplina_exemplo(sistema):
    """Creates a sample discipline with students for testing."""
    sistema.criar_disciplina(
        nome="Historia",
        num_questoes=3,
        alunos=[
            {"nome": "Alice", "respostas": ["V", "F", "V"]},
            {"nome": "Bob", "respostas": ["F", "V", "F"]},
        ],
        gabarito=["V", "F", "V"],
    )
    return "Historia"


class TestCriarDisciplina:
    """Tests for creating disciplines."""

    def test_criar_disciplina_simples(self, sistema):
        """Test creating a simple discipline without students."""
        resultado = sistema.criar_disciplina(
            nome="Matematica",
            num_questoes=5,
        )

        assert resultado["status"] == "sucesso"
        assert resultado["disciplina"] == "Matematica"
        assert resultado["num_questoes"] == 5
        assert resultado["total_alunos"] == 0

    def test_criar_disciplina_com_alunos(self, sistema):
        """Test creating a discipline with students."""
        alunos = [
            {"nome": "Carlos", "respostas": ["V", "F", "V", "F"]},
            {"nome": "Diana", "respostas": ["F", "V", "F", "V"]},
        ]
        resultado = sistema.criar_disciplina(
            nome="Ciencias",
            num_questoes=4,
            alunos=alunos,
            gabarito=["V", "F", "V", "F"],
        )

        assert resultado["status"] == "sucesso"
        assert resultado["total_alunos"] == 2
        assert "Carlos" in resultado["alunos_adicionados"]
        assert "Diana" in resultado["alunos_adicionados"]

    def test_criar_disciplina_com_gabarito(self, sistema):
        """Test creating a discipline with an answer key."""
        gabarito = ["V", "F", "V", "F", "V"]
        resultado = sistema.criar_disciplina(
            nome="Portugues",
            num_questoes=5,
            gabarito=gabarito,
        )

        assert resultado["status"] == "sucesso"

        # Verify gabarito was saved
        dados = sistema.carregar("Portugues")
        assert dados["gabarito"] == gabarito

    def test_criar_disciplina_sobrescrever(self, sistema):
        """Test overwriting an existing discipline."""
        # Create initial
        sistema.criar_disciplina(nome="Fisica", num_questoes=3)
        
        # Overwrite with different number of questions
        resultado = sistema.criar_disciplina(
            nome="Fisica",
            num_questoes=6,
            sobrescrever=True,
        )

        assert resultado["status"] == "sucesso"
        assert resultado["num_questoes"] == 6

    def test_criar_disciplina_mesclar_alunos(self, sistema):
        """Test merging new students with existing ones."""
        # Create with initial students
        sistema.criar_disciplina(
            nome="Quimica",
            num_questoes=2,
            alunos=[{"nome": "Eve", "respostas": ["V", "F"]}],
        )
        
        # Add more students
        resultado = sistema.criar_disciplina(
            nome="Quimica",
            num_questoes=2,
            alunos=[
                {"nome": "Frank", "respostas": ["F", "V"]},
                {"nome": "Eve", "respostas": ["V", "V"]},  # Duplicate
            ],
        )

        assert resultado["status"] == "sucesso"
        assert resultado["total_alunos"] == 2  # Eve not duplicated
        assert "Frank" in resultado["alunos_adicionados"]
        assert "Eve" not in resultado["alunos_adicionados"]

    def test_criar_disciplina_erro_num_questoes_diferente(self, sistema):
        """Test error when trying to change number of questions on existing discipline."""
        sistema.criar_disciplina(nome="Biologia", num_questoes=3)
        
        resultado = sistema.criar_disciplina(
            nome="Biologia",
            num_questoes=5,
        )

        assert resultado["status"] == "erro"
        assert "já existe" in resultado["mensagem"]

    def test_sanitizar_nome(self, sistema):
        """Test that discipline names are sanitized."""
        resultado = sistema.criar_disciplina(
            nome="História/Brasil:Colonial",
            num_questoes=2,
        )

        assert resultado["status"] == "sucesso"
        # Verify file was created with sanitized name
        assert os.path.exists(sistema._caminho_json("História_Brasil_Colonial"))


class TestAdicionarAlunos:
    """Tests for adding students to existing disciplines."""

    def test_adicionar_alunos_sucesso(self, sistema, disciplina_exemplo):
        """Test adding students to an existing discipline."""
        alunos = [
            {"nome": "Charlie", "respostas": ["V", "V", "F"]},
        ]
        resultado = sistema.adicionar_alunos("Historia", alunos)

        assert resultado["status"] == "sucesso"
        assert "Charlie" in resultado["alunos_adicionados"]
        assert resultado["total_alunos"] == 3

    def test_adicionar_alunos_duplicado(self, sistema, disciplina_exemplo):
        """Test that duplicate students are not added."""
        alunos = [
            {"nome": "Alice", "respostas": ["F", "V", "F"]},  # Already exists
        ]
        resultado = sistema.adicionar_alunos("Historia", alunos)

        assert resultado["status"] == "aviso"
        assert "Nenhum aluno novo" in resultado["mensagem"]

    def test_adicionar_alunos_disciplina_nao_encontrada(self, sistema):
        """Test error when discipline doesn't exist."""
        resultado = sistema.adicionar_alunos(
            "NaoExiste",
            [{"nome": "Test", "respostas": ["V"]}],
        )

        assert resultado["status"] == "erro"
        assert "não encontrada" in resultado["mensagem"]

    def test_adicionar_alunos_respostas_invalidas(self, sistema, disciplina_exemplo):
        """Test that students with invalid answers are rejected."""
        alunos = [
            {"nome": "Invalid", "respostas": ["V", "X", "V"]},  # 'X' is invalid
        ]
        resultado = sistema.adicionar_alunos("Historia", alunos)

        assert resultado["status"] == "aviso"


class TestDefinirGabarito:
    """Tests for defining answer keys."""

    def test_definir_gabarito_sucesso(self, sistema, disciplina_exemplo):
        """Test defining an answer key."""
        novo_gabarito = ["F", "V", "F"]
        resultado = sistema.definir_gabarito("Historia", novo_gabarito)

        assert resultado["status"] == "sucesso"
        assert resultado["gabarito"] == novo_gabarito

    def test_definir_gabarito_tamanho_errado(self, sistema, disciplina_exemplo):
        """Test error when gabarito size doesn't match questions."""
        gabarito_errado = ["V", "F"]  # Wrong size (should be 3)
        resultado = sistema.definir_gabarito("Historia", gabarito_errado)

        assert resultado["status"] == "erro"
        assert "deve ter 3 respostas" in resultado["mensagem"]

    def test_definir_gabarito_disciplina_nao_encontrada(self, sistema):
        """Test error when discipline doesn't exist."""
        resultado = sistema.definir_gabarito("NaoExiste", ["V", "F"])

        assert resultado["status"] == "erro"


class TestGerarResultados:
    """Tests for generating results and reports."""

    def test_gerar_resultados_sucesso(self, sistema, disciplina_exemplo):
        """Test generating results for a discipline."""
        resultado = sistema.gerar_resultados("Historia")

        assert resultado["status"] == "sucesso"
        assert resultado["total_alunos"] == 2
        assert resultado["num_questoes"] == 3
        assert "media" in resultado
        assert "resultados" in resultado
        assert "arquivos" in resultado

        # Verify files were created
        assert os.path.exists(resultado["arquivos"]["alfabetico"])
        assert os.path.exists(resultado["arquivos"]["notas"])
        assert os.path.exists(resultado["arquivos"]["cache"])

    def test_gerar_resultados_calculo_notas(self, sistema):
        """Test that grades are calculated correctly."""
        sistema.criar_disciplina(
            nome="Teste",
            num_questoes=3,
            alunos=[
                {"nome": "Perfeito", "respostas": ["V", "F", "V"]},  # 3/3
                {"nome": "Zero", "respostas": ["F", "V", "F"]},  # 0/3
                {"nome": "Metade", "respostas": ["V", "V", "F"]},  # 1/3
            ],
            gabarito=["V", "F", "V"],
        )

        resultado = sistema.gerar_resultados("Teste")

        assert resultado["status"] == "sucesso"
        assert resultado["media"] == pytest.approx(4 / 3, rel=1e-2)
        assert resultado["maior_nota"] == 3
        assert resultado["menor_nota"] == 0

    def test_gerar_resultados_nota_zerada_todas_iguais(self, sistema):
        """Test that students with all same answers get zero."""
        sistema.criar_disciplina(
            nome="Zerados",
            num_questoes=3,
            alunos=[
                {"nome": "TodasV", "respostas": ["V", "V", "V"]},
                {"nome": "TodasF", "respostas": ["F", "F", "F"]},
            ],
            gabarito=["V", "F", "V"],
        )

        resultado = sistema.gerar_resultados("Zerados")

        assert resultado["status"] == "sucesso"
        for r in resultado["resultados"]:
            assert r["pontuacao"] == 0
            assert "nota zerada" in r["observacao"]

    def test_gerar_resultados_estatisticas_questoes(self, sistema):
        """Test that per-question statistics are calculated correctly."""
        sistema.criar_disciplina(
            nome="Stats",
            num_questoes=2,
            alunos=[
                {"nome": "A", "respostas": ["V", "F"]},  # 2/2
                {"nome": "B", "respostas": ["V", "V"]},  # all V → 0
                {"nome": "C", "respostas": ["F", "V"]},  # 0/2 (F≠V on Q1, V≠F on Q2)
            ],
            gabarito=["V", "F"],
        )

        resultado = sistema.gerar_resultados("Stats")

        assert resultado["status"] == "sucesso"
        # Q1: only A got it right (1/3 — B zeroed, C wrong)
        assert resultado["estatisticas_questoes"][1] == 1
        # Q2: only A got it right (1/3 — B zeroed, C wrong)
        assert resultado["estatisticas_questoes"][2] == 1

    def test_gerar_resultados_disciplina_nao_encontrada(self, sistema):
        """Test error when discipline doesn't exist."""
        resultado = sistema.gerar_resultados("NaoExiste")

        assert resultado["status"] == "erro"

    def test_gerar_resultados_sem_alunos(self, sistema):
        """Test error when no students exist."""
        sistema.criar_disciplina(nome="Vazio", num_questoes=3)
        resultado = sistema.gerar_resultados("Vazio")

        assert resultado["status"] == "erro"
        assert "Não há alunos" in resultado["mensagem"]

    def test_gerar_resultados_sem_gabarito(self, sistema):
        """Test error when gabarito is not defined."""
        sistema.criar_disciplina(
            nome="SemGab",
            num_questoes=3,
            alunos=[{"nome": "X", "respostas": ["V", "F", "V"]}],
        )
        resultado = sistema.gerar_resultados("SemGab")

        assert resultado["status"] == "erro"
        assert "Gabarito não definido" in resultado["mensagem"]


class TestListarDisciplinas:
    """Tests for listing disciplines."""

    def test_listar_vazio(self, sistema):
        """Test listing when no disciplines exist."""
        disciplinas = sistema.listar_disciplinas()
        assert disciplinas == []

    def test_listar_com_disciplinas(self, sistema):
        """Test listing disciplines with data."""
        sistema.criar_disciplina(nome="Historia", num_questoes=3)
        sistema.criar_disciplina(nome="Geografia", num_questoes=5)

        disciplinas = sistema.listar_disciplinas()

        assert len(disciplinas) == 2
        nomes = [d["nome"] for d in disciplinas]
        assert "Historia" in nomes
        assert "Geografia" in nomes

    def test_listar_com_resultados(self, sistema):
        """Test that listing shows if results exist."""
        sistema.criar_disciplina(
            nome="ComResultado",
            num_questoes=2,
            alunos=[{"nome": "A", "respostas": ["V", "F"]}],
            gabarito=["V", "F"],
        )
        sistema.gerar_resultados("ComResultado")

        disciplinas = sistema.listar_disciplinas()
        assert len(disciplinas) == 1
        assert disciplinas[0]["tem_resultado"] is True


class TestObterDados:
    """Tests for obtaining discipline data."""

    def test_obter_dados_completos(self, sistema, disciplina_exemplo):
        """Test obtaining complete discipline data."""
        dados = sistema.obter_dados_completos("Historia")

        assert dados is not None
        assert dados["disciplina"] == "Historia"
        assert len(dados["alunos"]) == 2
        assert dados["gabarito"] == ["V", "F", "V"]

    def test_obter_dados_nao_encontrado(self, sistema):
        """Test obtaining data for non-existent discipline."""
        dados = sistema.obter_dados_completos("NaoExiste")
        assert dados is None

    def test_obter_resultados_cacheados(self, sistema, disciplina_exemplo):
        """Test obtaining cached results."""
        sistema.gerar_resultados("Historia")
        cache = sistema.obter_resultados("Historia")

        assert cache is not None
        assert "resultados" in cache
        assert "media" in cache


class TestBackup:
    """Tests for backup functionality."""

    def test_backup_sucesso(self, sistema, disciplina_exemplo):
        """Test creating a backup."""
        resultado = sistema.fazer_backup()

        assert resultado["status"] == "sucesso"
        assert "arquivo" in resultado
        assert resultado["arquivo"].endswith(".zip")

        # Cleanup
        if os.path.exists(resultado["arquivo"]):
            os.remove(resultado["arquivo"])


class TestUtilitarios:
    """Tests for utility methods."""

    def test_sanitizar_nome(self, sistema):
        """Test name sanitization."""
        assert sistema._sanitizar_nome("Normal") == "Normal"
        assert sistema._sanitizar_nome("Com/Espaco") == "Com_Espaco"
        assert sistema._sanitizar_nome("Com:DoisPontos") == "Com_DoisPontos"
        assert sistema._sanitizar_nome("  ComEspaco  ") == "ComEspaco"

    def test_caminho_json(self, sistema):
        """Test JSON file path generation."""
        caminho = sistema._caminho_json("Teste")
        assert caminho.endswith("Teste.json")
        assert sistema.diretorio_dados in caminho

    def test_init_cria_diretorio(self):
        """Test that __init__ creates the directory if it doesn't exist."""
        temp_dir = tempfile.mkdtemp()
        new_dir = os.path.join(temp_dir, "novo_diretorio")
        sistema = SistemaAvaliacao(diretorio_dados=new_dir)
        assert os.path.exists(new_dir)
        shutil.rmtree(temp_dir)

    def test_carregar_json_corrompido(self, sistema):
        """Test loading corrupted JSON file."""
        # Create a corrupted JSON file
        caminho = sistema._caminho_json("Corrompido")
        with open(caminho, "w") as f:
            f.write("{invalid json}")
        
        resultado = sistema.carregar("Corrompido")
        assert resultado is None

    def test_criar_disciplina_alunos_none(self, sistema):
        """Test creating discipline with alunos=None explicitly."""
        resultado = sistema.criar_disciplina(
            nome="SemAlunos",
            num_questoes=2,
            alunos=None,
        )
        assert resultado["status"] == "sucesso"
        assert resultado["total_alunos"] == 0

    def test_gerar_resultados_calculo_notas_vazio(self, sistema):
        """Test grade calculation with empty alunos list."""
        sistema.criar_disciplina(nome="VazioCalc", num_questoes=3)
        resultado = sistema.gerar_resultados("VazioCalc")
        assert resultado["status"] == "erro"
        assert "Não há alunos" in resultado["mensagem"]
