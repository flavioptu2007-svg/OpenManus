"""Tests for AvaliacaoProvas tool — OpenManus tool interface for exam evaluation.

These tests verify:
- Tool initialization and schema
- All command implementations
- Error handling
- ToolResult formatting
"""

import os
import shutil
import tempfile

import pytest

from app.exceptions import ToolError
from app.tool.avaliacao_provas import AvaliacaoProvas
from app.tool.base import ToolResult


@pytest.fixture
def tool():
    """Creates an AvaliacaoProvas tool instance with a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    tool = AvaliacaoProvas()
    tool._sistema.diretorio_dados = temp_dir
    yield tool
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
async def tool_com_disciplina(tool):
    """Creates a tool with a sample discipline already set up."""
    await tool.execute(
        command="criar",
        disciplina="Historia",
        num_questoes=3,
        alunos=[
            {"nome": "Alice", "respostas": ["V", "F", "V"]},
            {"nome": "Bob", "respostas": ["F", "V", "F"]},
        ],
        gabarito=["V", "F", "V"],
    )
    return tool


class TestToolSchema:
    """Tests for tool schema and metadata."""

    def test_tool_name(self, tool):
        """Test tool has correct name."""
        assert tool.name == "avaliacao_provas"

    def test_tool_description(self, tool):
        """Test tool has a description."""
        assert "Avaliação" in tool.description or "avaliação" in tool.description

    def test_tool_parameters(self, tool):
        """Test tool has valid parameters schema."""
        params = tool.parameters
        assert params["type"] == "object"
        assert "command" in params["properties"]
        assert "command" in params["required"]
        assert params["properties"]["command"]["type"] == "string"

    def test_to_param(self, tool):
        """Test to_param returns OpenAI function calling format."""
        param = tool.to_param()
        assert param["type"] == "function"
        assert param["function"]["name"] == "avaliacao_provas"
        assert "parameters" in param["function"]


class TestComandoCriar:
    """Tests for the 'criar' command."""

    @pytest.mark.asyncio
    async def test_criar_disciplina_simples(self, tool):
        """Test creating a simple discipline."""
        result = await tool.execute(
            command="criar",
            disciplina="Matematica",
            num_questoes=5,
        )

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "Matematica" in result.output
        assert "5" in result.output

    @pytest.mark.asyncio
    async def test_criar_disciplina_com_alunos(self, tool):
        """Test creating a discipline with students."""
        result = await tool.execute(
            command="criar",
            disciplina="Ciencias",
            num_questoes=3,
            alunos=[
                {"nome": "Carlos", "respostas": ["V", "F", "V"]},
                {"nome": "Diana", "respostas": ["F", "V", "F"]},
            ],
        )

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "Carlos" in result.output
        assert "Diana" in result.output

    @pytest.mark.asyncio
    async def test_criar_sem_disciplina(self, tool):
        """Test error when disciplina parameter is missing."""
        with pytest.raises(ToolError, match="disciplina.*obrigatório"):
            await tool.execute(command="criar")

    @pytest.mark.asyncio
    async def test_criar_sem_num_questoes(self, tool):
        """Test error when num_questoes parameter is missing."""
        with pytest.raises(ToolError, match="num_questoes"):
            await tool.execute(command="criar", disciplina="Test")

    @pytest.mark.asyncio
    async def test_criar_num_questoes_invalido(self, tool):
        """Test error when num_questoes is not positive."""
        with pytest.raises(ToolError, match="num_questoes.*positivo"):
            await tool.execute(command="criar", disciplina="Test", num_questoes=0)


class TestComandoAdicionarAlunos:
    """Tests for the 'adicionar_alunos' command."""

    @pytest.mark.asyncio
    async def test_adicionar_alunos_sucesso(self, tool_com_disciplina):
        """Test adding students to existing discipline."""
        result = await tool_com_disciplina.execute(
            command="adicionar_alunos",
            disciplina="Historia",
            alunos=[{"nome": "Charlie", "respostas": ["V", "V", "F"]}],
        )

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "Charlie" in result.output
        assert "3" in result.output

    @pytest.mark.asyncio
    async def test_adicionar_alunos_disciplina_nao_encontrada(self, tool):
        """Test error when discipline doesn't exist."""
        result = await tool.execute(
            command="adicionar_alunos",
            disciplina="NaoExiste",
            alunos=[{"nome": "Test", "respostas": ["V"]}],
        )

        assert isinstance(result, ToolResult)
        assert result.error is not None
        assert "não encontrada" in result.error

    @pytest.mark.asyncio
    async def test_adicionar_alunos_sem_disciplina(self, tool):
        """Test error when disciplina parameter is missing."""
        with pytest.raises(ToolError, match="disciplina.*obrigatório"):
            await tool.execute(
                command="adicionar_alunos",
                alunos=[{"nome": "Test", "respostas": ["V"]}],
            )

    @pytest.mark.asyncio
    async def test_adicionar_alunos_sem_alunos(self, tool_com_disciplina):
        """Test error when alunos parameter is missing."""
        with pytest.raises(ToolError, match="alunos.*obrigatório"):
            await tool_com_disciplina.execute(
                command="adicionar_alunos",
                disciplina="Historia",
            )


class TestComandoDefinirGabarito:
    """Tests for the 'definir_gabarito' command."""

    @pytest.mark.asyncio
    async def test_definir_gabarito_sucesso(self, tool_com_disciplina):
        """Test defining an answer key."""
        result = await tool_com_disciplina.execute(
            command="definir_gabarito",
            disciplina="Historia",
            gabarito=["F", "V", "F"],
        )

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "F V F" in result.output

    @pytest.mark.asyncio
    async def test_definir_gabarito_tamanho_errado(self, tool_com_disciplina):
        """Test error when gabarito size doesn't match."""
        result = await tool_com_disciplina.execute(
            command="definir_gabarito",
            disciplina="Historia",
            gabarito=["V", "F"],  # Wrong size
        )

        assert isinstance(result, ToolResult)
        assert result.error is not None
        assert "deve ter 3 respostas" in result.error

    @pytest.mark.asyncio
    async def test_definir_gabarito_sem_disciplina(self, tool):
        """Test error when disciplina parameter is missing."""
        with pytest.raises(ToolError, match="disciplina.*obrigatório"):
            await tool.execute(
                command="definir_gabarito",
                gabarito=["V", "F", "V"],
            )

    @pytest.mark.asyncio
    async def test_definir_gabarito_sem_gabarito(self, tool_com_disciplina):
        """Test error when gabarito parameter is missing."""
        with pytest.raises(ToolError, match="gabarito.*obrigatório"):
            await tool_com_disciplina.execute(
                command="definir_gabarito",
                disciplina="Historia",
            )


class TestComandoGerarResultados:
    """Tests for the 'gerar_resultados' command."""

    @pytest.mark.asyncio
    async def test_gerar_resultados_sucesso(self, tool_com_disciplina):
        """Test generating results."""
        result = await tool_com_disciplina.execute(
            command="gerar_resultados",
            disciplina="Historia",
        )

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "Estatísticas" in result.output
        assert "Ranking" in result.output
        assert "Alice" in result.output
        assert "Bob" in result.output

    @pytest.mark.asyncio
    async def test_gerar_resultados_disciplina_nao_encontrada(self, tool):
        """Test error when discipline doesn't exist."""
        result = await tool.execute(
            command="gerar_resultados",
            disciplina="NaoExiste",
        )

        assert isinstance(result, ToolResult)
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_gerar_resultados_sem_disciplina(self, tool):
        """Test error when disciplina parameter is missing."""
        with pytest.raises(ToolError, match="disciplina.*obrigatório"):
            await tool.execute(command="gerar_resultados")


class TestComandoListar:
    """Tests for the 'listar' command."""

    @pytest.mark.asyncio
    async def test_listar_vazio(self, tool):
        """Test listing when no disciplines exist."""
        result = await tool.execute(command="listar")

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "Nenhuma disciplina" in result.output

    @pytest.mark.asyncio
    async def test_listar_com_disciplinas(self, tool_com_disciplina):
        """Test listing disciplines."""
        result = await tool_com_disciplina.execute(command="listar")

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "Historia" in result.output


class TestComandoVerDisciplina:
    """Tests for the 'ver_disciplina' command."""

    @pytest.mark.asyncio
    async def test_ver_disciplina_sucesso(self, tool_com_disciplina):
        """Test viewing discipline details."""
        result = await tool_com_disciplina.execute(
            command="ver_disciplina",
            disciplina="Historia",
        )

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "HISTORIA" in result.output
        assert "Alice" in result.output
        assert "Bob" in result.output

    @pytest.mark.asyncio
    async def test_ver_disciplina_nao_encontrada(self, tool):
        """Test error when discipline doesn't exist."""
        result = await tool.execute(
            command="ver_disciplina",
            disciplina="NaoExiste",
        )

        assert isinstance(result, ToolResult)
        assert result.error is not None
        assert "não encontrada" in result.error

    @pytest.mark.asyncio
    async def test_ver_disciplina_sem_disciplina(self, tool):
        """Test error when disciplina parameter is missing."""
        with pytest.raises(ToolError, match="disciplina.*obrigatório"):
            await tool.execute(command="ver_disciplina")


class TestComandoVerResultados:
    """Tests for the 'ver_resultados' command."""

    @pytest.mark.asyncio
    async def test_ver_resultados_sucesso(self, tool_com_disciplina):
        """Test viewing results."""
        # First generate results
        await tool_com_disciplina.execute(
            command="gerar_resultados",
            disciplina="Historia",
        )

        result = await tool_com_disciplina.execute(
            command="ver_resultados",
            disciplina="Historia",
        )

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "Resultados" in result.output
        assert "Ranking" in result.output

    @pytest.mark.asyncio
    async def test_ver_resultados_nao_existentes(self, tool_com_disciplina):
        """Test error when results don't exist yet."""
        result = await tool_com_disciplina.execute(
            command="ver_resultados",
            disciplina="Historia",
        )

        assert isinstance(result, ToolResult)
        assert result.error is not None
        assert "gerar_resultados" in result.error

    @pytest.mark.asyncio
    async def test_ver_resultados_sem_disciplina(self, tool):
        """Test error when disciplina parameter is missing."""
        with pytest.raises(ToolError, match="disciplina.*obrigatório"):
            await tool.execute(command="ver_resultados")


class TestComandoBackup:
    """Tests for the 'backup' command."""

    @pytest.mark.asyncio
    async def test_backup_sucesso(self, tool_com_disciplina):
        """Test creating a backup."""
        result = await tool_com_disciplina.execute(command="backup")

        assert isinstance(result, ToolResult)
        assert result.error is None
        assert "Backup criado" in result.output

    @pytest.mark.asyncio
    async def test_backup_limpa(self, tool):
        """Test backup on empty directory."""
        result = await tool.execute(command="backup")

        assert isinstance(result, ToolResult)
        assert result.error is None


class TestComandosInvalidos:
    """Tests for invalid commands."""

    @pytest.mark.asyncio
    async def test_comando_invalido(self, tool):
        """Test error for unrecognized command."""
        with pytest.raises(ToolError, match="não reconhecido"):
            await tool.execute(command="comando_inexistente")

    @pytest.mark.asyncio
    async def test_comando_com_erro_retorna_tool_result(self, tool):
        """Test that runtime errors return ToolResult with error."""
        # This should trigger an error in the underlying system
        result = await tool.execute(
            command="gerar_resultados",
            disciplina="NaoExiste",
        )

        assert isinstance(result, ToolResult)
        assert result.error is not None


class TestIntegracaoCompleta:
    """Integration tests for complete workflows."""

    @pytest.mark.asyncio
    async def test_fluxo_completo(self, tool):
        """Test a complete workflow: create -> add students -> define key -> generate results."""
        # 1. Create discipline
        result1 = await tool.execute(
            command="criar",
            disciplina="FluxoCompleto",
            num_questoes=2,
            alunos=[
                {"nome": "Aluno1", "respostas": ["V", "F"]},
            ],
        )
        assert result1.error is None

        # 2. Add more students
        result2 = await tool.execute(
            command="adicionar_alunos",
            disciplina="FluxoCompleto",
            alunos=[{"nome": "Aluno2", "respostas": ["F", "V"]}],
        )
        assert result2.error is None

        # 3. Define answer key
        result3 = await tool.execute(
            command="definir_gabarito",
            disciplina="FluxoCompleto",
            gabarito=["V", "F"],
        )
        assert result3.error is None

        # 4. Generate results
        result4 = await tool.execute(
            command="gerar_resultados",
            disciplina="FluxoCompleto",
        )
        assert result4.error is None
        assert "Estatísticas" in result4.output

        # 5. View results
        result5 = await tool.execute(
            command="ver_resultados",
            disciplina="FluxoCompleto",
        )
        assert result5.error is None

        # 6. List disciplines
        result6 = await tool.execute(command="listar")
        assert "FluxoCompleto" in result6.output

        # 7. Create backup
        result7 = await tool.execute(command="backup")
        assert result7.error is None
