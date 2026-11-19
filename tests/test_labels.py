import re

from labels import Label, Mudanca, comando_gh, labels_padrao, planejar

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
