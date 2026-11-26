"""Testes unitarios das regras do quadro Kanban (positivos, negativos e limites)."""

import pytest

from app.domain import (
    LIMITE_WIP,
    NaoEncontradoError,
    Quadro,
    RegraError,
    ValidacaoError,
)


@pytest.fixture
def quadro():
    return Quadro()


def _em_fazendo(quadro, quantidade):
    for i in range(quantidade):
        card = quadro.criar(f"tarefa {i}")
        quadro.mover(card.id, "FAZENDO")


class TestCriar:
    def test_card_nasce_em_a_fazer_com_prioridade_media(self, quadro):
        card = quadro.criar("Escrever relatorio")
        assert (card.id, card.coluna, card.prioridade) == (1, "A_FAZER", "MEDIA")

    def test_ids_sao_sequenciais(self, quadro):
        assert [quadro.criar("a").id, quadro.criar("b").id] == [1, 2]

    def test_titulo_sem_espacos_nas_pontas(self, quadro):
        assert quadro.criar("  Revisar  ").titulo == "Revisar"

    @pytest.mark.parametrize("tamanho", [1, 100])
    def test_limites_validos_do_titulo(self, quadro, tamanho):
        assert len(quadro.criar("x" * tamanho).titulo) == tamanho

    @pytest.mark.parametrize("titulo", ["", "   ", "x" * 101, None, 123])
    def test_titulo_invalido(self, quadro, titulo):
        with pytest.raises(ValidacaoError):
            quadro.criar(titulo)

    @pytest.mark.parametrize("prioridade", ["BAIXA", "MEDIA", "ALTA"])
    def test_prioridades_validas(self, quadro, prioridade):
        assert quadro.criar("t", prioridade).prioridade == prioridade

    @pytest.mark.parametrize("prioridade", ["URGENTE", "alta", None, 1])
    def test_prioridade_invalida(self, quadro, prioridade):
        with pytest.raises(ValidacaoError):
            quadro.criar("t", prioridade)


class TestMover:
    def test_fluxo_completo(self, quadro):
        card = quadro.criar("t")
        quadro.mover(card.id, "FAZENDO")
        assert quadro.mover(card.id, "FEITO").coluna == "FEITO"

    def test_pode_voltar_uma_coluna(self, quadro):
        card = quadro.criar("t")
        quadro.mover(card.id, "FAZENDO")
        assert quadro.mover(card.id, "A_FAZER").coluna == "A_FAZER"

    def test_nao_pula_coluna(self, quadro):
        card = quadro.criar("t")
        with pytest.raises(RegraError):
            quadro.mover(card.id, "FEITO")

    def test_nao_move_para_mesma_coluna(self, quadro):
        card = quadro.criar("t")
        with pytest.raises(RegraError):
            quadro.mover(card.id, "A_FAZER")

    @pytest.mark.parametrize("coluna", ["BACKLOG", "fazendo", None])
    def test_coluna_invalida(self, quadro, coluna):
        card = quadro.criar("t")
        with pytest.raises(ValidacaoError):
            quadro.mover(card.id, coluna)

    def test_card_inexistente(self, quadro):
        with pytest.raises(NaoEncontradoError):
            quadro.mover(99, "FAZENDO")


class TestLimiteWip:
    def test_aceita_ate_o_limite(self, quadro):
        _em_fazendo(quadro, 3)  # limite exato: o 3o card ainda entra
        assert quadro.contar("FAZENDO") == LIMITE_WIP

    def test_bloqueia_o_quarto_card(self, quadro):
        _em_fazendo(quadro, 3)
        quarto = quadro.criar("quarto")
        with pytest.raises(RegraError):
            quadro.mover(quarto.id, "FAZENDO")

    def test_libera_vaga_quando_card_sai(self, quadro):
        _em_fazendo(quadro, 3)
        quadro.mover(1, "FEITO")
        quarto = quadro.criar("quarto")
        assert quadro.mover(quarto.id, "FAZENDO").coluna == "FAZENDO"


class TestListarRemoverResumo:
    def test_ordena_por_prioridade_e_criacao(self, quadro):
        quadro.criar("b", "BAIXA")
        quadro.criar("a1", "ALTA")
        quadro.criar("m", "MEDIA")
        quadro.criar("a2", "ALTA")
        assert [c.titulo for c in quadro.listar()] == ["a1", "a2", "m", "b"]

    def test_filtra_por_coluna(self, quadro):
        quadro.criar("a")
        card = quadro.criar("b")
        quadro.mover(card.id, "FAZENDO")
        assert [c.titulo for c in quadro.listar("FAZENDO")] == ["b"]

    def test_filtro_invalido(self, quadro):
        with pytest.raises(ValidacaoError):
            quadro.listar("XYZ")

    def test_remover(self, quadro):
        card = quadro.criar("t")
        quadro.remover(card.id)
        assert quadro.listar() == []

    def test_remover_inexistente(self, quadro):
        with pytest.raises(NaoEncontradoError):
            quadro.remover(1)

    def test_resumo(self, quadro):
        _em_fazendo(quadro, 2)
        quadro.criar("parado")
        assert quadro.resumo() == {
            "colunas": {"A_FAZER": 1, "FAZENDO": 2, "FEITO": 0},
            "wip_livre": 1,
        }
