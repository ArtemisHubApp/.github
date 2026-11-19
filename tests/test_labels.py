import json
import re
import shutil
import subprocess

import pytest
from labels import REPOS, Label, Mudanca, comando_gh, labels_padrao, main, planejar, rodar_gh

SEM1 = Label("semana-1", "bfd4f2", "Roadmap: semana 1")


def test_padrao_tem_semanas_prioridades_e_tipos():
    nomes = [lb.nome for lb in labels_padrao()]
    assert nomes[:7] == [f"semana-{n}" for n in range(1, 8)]
    assert nomes[7:] == [
        "prioridade: alta",
        "prioridade: média",
        "prioridade: baixa",
        "tipo: feature",
        "tipo: bug",
        "tipo: chore",
        "tipo: docs",
    ]


def test_padrao_respeita_limites_do_github():
    for lb in labels_padrao():
        assert re.fullmatch(r"[0-9a-f]{6}", lb.cor) and len(lb.descricao) <= 100


def test_semana_tem_cor_e_descricao_fixas():
    assert labels_padrao(semanas=2)[1] == Label("semana-2", "bfd4f2", "Roadmap: semana 2")


def test_planejar_cria_o_que_falta():
    assert planejar([], [SEM1]) == [Mudanca("criar", SEM1)]


def test_planejar_ignora_label_igual():  # cor em maiúsculas conta como igual
    assert planejar([{"name": "semana-1", "color": "BFD4F2", "description": "Roadmap: semana 1"}], [SEM1]) == []


def test_planejar_atualiza_cor_ou_descricao_diferente():
    existentes = [{"name": "semana-1", "color": "0E8A16", "description": ""}]
    assert planejar(existentes, [SEM1]) == [Mudanca("atualizar", SEM1, nome_atual="semana-1")]


def test_planejar_casa_nome_sem_diferenciar_maiusculas():
    existentes = [{"name": "Semana-1", "color": "bfd4f2", "description": "Roadmap: semana 1"}]
    assert planejar(existentes, [SEM1]) == [Mudanca("atualizar", SEM1, nome_atual="Semana-1")]


def test_planejar_nunca_apaga():
    assert planejar([{"name": "wontfix", "color": "ffffff", "description": ""}], []) == []


def test_comando_criar():
    assert comando_gh("ArtemisHubApp/artemishub_rag", Mudanca("criar", SEM1)) == [
        "label",
        "create",
        "semana-1",
        "--color",
        "bfd4f2",
        "--description",
        "Roadmap: semana 1",
        "-R",
        "ArtemisHubApp/artemishub_rag",
    ]


def test_comando_atualizar_renomeia_pelo_nome_atual():
    assert comando_gh("ArtemisHubApp/artemishub_rag", Mudanca("atualizar", SEM1, nome_atual="Semana-1")) == [
        "label",
        "edit",
        "Semana-1",
        "--name",
        "semana-1",
        "--color",
        "bfd4f2",
        "--description",
        "Roadmap: semana 1",
        "-R",
        "ArtemisHubApp/artemishub_rag",
    ]


class FakeGh:
    def __init__(self, existentes, negados=()):
        self.existentes = existentes
        self.negados = set(negados)
        self.chamadas = []

    def __call__(self, args):
        self.chamadas.append(args)
        if self.negados & set(args):
            raise RuntimeError("HTTP 403")
        if args[:2] == ["label", "list"]:
            repo = args[args.index("-R") + 1]
            return json.dumps(self.existentes.get(repo, []))
        return ""


def test_main_sem_apply_so_lista(capsys):
    gh = FakeGh({})
    assert main(["--repo", "artemishub_rag"], gh=gh) == 0
    assert all(c[:2] == ["label", "list"] for c in gh.chamadas)
    assert "Ensaio: nada foi alterado" in capsys.readouterr().out


def test_main_com_apply_cria_e_atualiza():
    gh = FakeGh({"ArtemisHubApp/artemishub_rag": [{"name": "Semana-4", "color": "0E8A16", "description": ""}]})
    assert main(["--apply", "--repo", "artemishub_rag"], gh=gh) == 0
    escritas = [c for c in gh.chamadas if c[1] in ("create", "edit")]
    assert ["label", "edit", "Semana-4"] == escritas[3][:3] and len(escritas) == 14  # 7 semanas + 3 + 4


def test_main_continua_quando_um_repo_falha(capsys):
    gh = FakeGh({}, negados={"ArtemisHubApp/artemishub_docs"})
    assert main(["--apply", "--repo", "artemishub_docs", "--repo", "artemishub_rag"], gh=gh) == 1
    assert any(c[-1] == "ArtemisHubApp/artemishub_rag" and c[1] == "create" for c in gh.chamadas)
    assert "ERRO ArtemisHubApp/artemishub_docs: HTTP 403" in capsys.readouterr().err


def test_main_sem_repo_usa_os_sete():
    gh = FakeGh({})
    main([], gh=gh)
    assert [c[3] for c in gh.chamadas] == [f"ArtemisHubApp/{r}" for r in REPOS]


def test_repo_desconhecido_e_recusado():
    with pytest.raises(SystemExit):
        main(["--repo", "kyte"], gh=FakeGh({}))


def test_sem_gh_no_path_avisa(monkeypatch, capsys):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    assert main([]) == 1
    assert "gh não foi encontrado" in capsys.readouterr().err


def test_rodar_gh_transforma_falha_em_runtimeerror(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 1, "", "HTTP 403"))
    with pytest.raises(RuntimeError, match="HTTP 403"):
        rodar_gh(["label", "list"])
