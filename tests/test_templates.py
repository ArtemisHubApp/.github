from pathlib import Path

import pytest
import yaml
from labels import REPOS, SEMANAS, labels_padrao

ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / ".github/ISSUE_TEMPLATE"

TIPOS = {
    "feature": ("feat: ", "tipo: feature"),
    "bug": ("fix: ", "tipo: bug"),
    "chore": ("chore: ", "tipo: chore"),
    "docs": ("docs: ", "tipo: docs"),
}


def _form(tipo):
    return yaml.safe_load((FORMS / f"{tipo}.yml").read_text(encoding="utf-8"))


def _campos(tipo):
    return {item["id"]: item for item in _form(tipo)["body"] if "id" in item}


@pytest.mark.parametrize("tipo", TIPOS)
def test_formulario_tem_titulo_e_label_do_tipo(tipo):
    form = _form(tipo)
    assert form["name"] and form["description"]
    assert (form["title"], form["labels"]) == (TIPOS[tipo][0], [TIPOS[tipo][1]])


@pytest.mark.parametrize("tipo", TIPOS)
def test_formulario_tem_semana_criterios_e_repo_obrigatorios(tipo):
    campos = _campos(tipo)
    assert campos["semana"]["type"] == "dropdown"
    assert campos["criterios"]["type"] == "textarea"
    assert campos["repo"]["type"] == "dropdown"
    assert campos["repo"]["attributes"]["multiple"] is True
    obrigatorios = ("semana", "criterios", "repo")
    assert all(campos[i]["validations"]["required"] is True for i in obrigatorios)


@pytest.mark.parametrize("tipo", TIPOS)
def test_opcoes_de_semana_batem_com_as_labels(tipo):
    opcoes = _campos(tipo)["semana"]["attributes"]["options"]
    esperado = [f"Semana {n}" for n in range(1, SEMANAS + 1)] + ["Backlog (sem semana)"]
    assert opcoes == esperado


@pytest.mark.parametrize("tipo", TIPOS)
def test_repo_afetado_lista_os_repos_da_org(tipo):
    assert _campos(tipo)["repo"]["attributes"]["options"] == list(REPOS)


@pytest.mark.parametrize("tipo", TIPOS)
def test_ids_unicos(tipo):
    ids = [i["id"] for i in _form(tipo)["body"] if "id" in i]
    assert len(ids) == len(set(ids))


def test_labels_dos_formularios_estao_no_padrao():
    padrao = {lb.nome for lb in labels_padrao()}
    assert all(set(_form(t)["labels"]) <= padrao for t in TIPOS)


def test_issue_em_branco_desligada():
    cfg = yaml.safe_load((FORMS / "config.yml").read_text(encoding="utf-8"))
    assert cfg["blank_issues_enabled"] is False and cfg["contact_links"]
