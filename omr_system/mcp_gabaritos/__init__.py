"""Servidor MCP gabaritos_mcp — expõe o Sistema de Gabaritos como tools.

Transporte: stdio. Nunca escrever logs em stdout (o protocolo usa stdout);
usar stderr ou logging para diagnóstico.
"""

from mcp_gabaritos.server import main  # noqa: F401


__version__ = "1.0.0"
