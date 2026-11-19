"""Labels padrão da org ArtemisHubApp e planejamento da sincronização.

Este módulo só descreve o que deve existir (`labels_padrao`), compara com o que já
existe (`planejar`) e monta os argumentos do `gh` (`comando_gh`). Nunca apaga label.
Usa apenas a biblioteca padrão.
"""

from dataclasses import dataclass
from typing import Literal

ORG: str = "ArtemisHubApp"
REPOS: tuple[str, ...] = (
    "artemishub_orchestration",
    "artemishub_docs",
    "artemishub_frontend",
    "artemishub_backend",
    "artemishub_agents",
    "artemishub_rag",
    ".github",
)
SEMANAS: int = 7


@dataclass(frozen=True)
class Label:
    nome: str
    cor: str
    descricao: str


@dataclass(frozen=True)
class Mudanca:
    acao: Literal["criar", "atualizar"]
    label: Label
    nome_atual: str | None = None


_PRIORIDADES_E_TIPOS: tuple[Label, ...] = (
    Label("prioridade: alta", "b60205", "Caminho crítico ou entregável do roadmap"),
    Label("prioridade: média", "fbca04", "Importante, mas não bloqueia outras tarefas"),
    Label("prioridade: baixa", "0e8a16", "Desejável; pode ficar para depois"),
    Label("tipo: feature", "a2eeef", "Funcionalidade nova ou mudança de comportamento"),
    Label("tipo: bug", "d73a4a", "Algo não funciona como deveria"),
    Label("tipo: chore", "c5def5", "Manutenção, configuração ou faxina, sem mudar comportamento"),
    Label("tipo: docs", "0075ca", "Documentação"),
)


def labels_padrao(semanas: int = SEMANAS) -> list[Label]:
    """Labels desejadas: semanas, depois prioridades, depois tipos."""
    return [Label(f"semana-{n}", "bfd4f2", f"Roadmap: semana {n}") for n in range(1, semanas + 1)] + list(
        _PRIORIDADES_E_TIPOS
    )


def planejar(existentes: list[dict[str, str]], desejadas: list[Label]) -> list[Mudanca]:
    """Compara as labels existentes com as desejadas; labels extras são ignoradas."""
    por_nome = {e["name"].casefold(): e for e in existentes}
    mudancas: list[Mudanca] = []
    for label in desejadas:
        atual = por_nome.get(label.nome.casefold())
        if atual is None:
            mudancas.append(Mudanca("criar", label))
        elif (
            atual["name"] != label.nome
            or atual.get("color", "").lower() != label.cor
            or atual.get("description", "") != label.descricao
        ):
            mudancas.append(Mudanca("atualizar", label, nome_atual=atual["name"]))
    return mudancas


def comando_gh(repo: str, mudanca: Mudanca) -> list[str]:
    """Argumentos do `gh` para aplicar a mudança; `repo` é `ArtemisHubApp/<nome>`."""
    label = mudanca.label
    if mudanca.acao == "criar":
        base = ["label", "create", label.nome]
    else:
        base = ["label", "edit", mudanca.nome_atual or label.nome, "--name", label.nome]
    return [*base, "--color", label.cor, "--description", label.descricao, "-R", repo]
