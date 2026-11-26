"""Regras de negocio do quadro Kanban.

Regras:
- Colunas, em ordem: A_FAZER -> FAZENDO -> FEITO.
- Todo card nasce em A_FAZER.
- Titulo obrigatorio, de 1 a 100 caracteres (espacos nas pontas sao ignorados).
- Prioridade: BAIXA, MEDIA (padrao) ou ALTA.
- Um card so anda uma coluna por vez (para frente ou para tras).
- Limite de WIP (trabalho em andamento): no maximo 3 cards em FAZENDO.
"""

from dataclasses import asdict, dataclass

COLUNAS = ("A_FAZER", "FAZENDO", "FEITO")
COLUNA_WIP = "FAZENDO"
LIMITE_WIP = 4
TITULO_MAX = 100
PRIORIDADES = ("BAIXA", "MEDIA", "ALTA")


class ValidacaoError(ValueError):
    """Dado de entrada invalido (HTTP 422)."""


class RegraError(ValueError):
    """Operacao valida, mas proibida pelas regras do quadro (HTTP 409)."""


class NaoEncontradoError(LookupError):
    """Card inexistente (HTTP 404)."""


@dataclass
class Card:
    id: int
    titulo: str
    prioridade: str
    coluna: str

    def para_dict(self) -> dict:
        return asdict(self)


def validar_titulo(titulo) -> str:
    if not isinstance(titulo, str):
        raise ValidacaoError("titulo deve ser texto")
    titulo = titulo.strip()
    if not 1 <= len(titulo) <= TITULO_MAX:
        raise ValidacaoError(f"titulo deve ter de 1 a {TITULO_MAX} caracteres")
    return titulo


def validar_prioridade(prioridade) -> str:
    if prioridade not in PRIORIDADES:
        raise ValidacaoError(f"prioridade deve ser uma de {', '.join(PRIORIDADES)}")
    return prioridade


class Quadro:
    """Quadro Kanban em memoria."""

    def __init__(self) -> None:
        self._cards: dict[int, Card] = {}
        self._proximo_id = 1

    def criar(self, titulo, prioridade="MEDIA") -> Card:
        card = Card(
            id=self._proximo_id,
            titulo=validar_titulo(titulo),
            prioridade=validar_prioridade(prioridade),
            coluna=COLUNAS[0],
        )
        self._cards[card.id] = card
        self._proximo_id += 1
        return card

    def obter(self, card_id: int) -> Card:
        if card_id not in self._cards:
            raise NaoEncontradoError(f"card {card_id} nao encontrado")
        return self._cards[card_id]

    def listar(self, coluna=None) -> list[Card]:
        if coluna is not None and coluna not in COLUNAS:
            raise ValidacaoError(f"coluna deve ser uma de {', '.join(COLUNAS)}")
        cards = [c for c in self._cards.values() if coluna is None or c.coluna == coluna]
        # ALTA primeiro; empate pela ordem de criacao
        return sorted(cards, key=lambda c: (-PRIORIDADES.index(c.prioridade), c.id))

    def contar(self, coluna: str) -> int:
        return sum(1 for c in self._cards.values() if c.coluna == coluna)

    def mover(self, card_id: int, destino) -> Card:
        card = self.obter(card_id)
        if destino not in COLUNAS:
            raise ValidacaoError(f"coluna deve ser uma de {', '.join(COLUNAS)}")
        distancia = COLUNAS.index(destino) - COLUNAS.index(card.coluna)
        if distancia == 0:
            raise RegraError("o card ja esta nessa coluna")
        if abs(distancia) > 1:
            raise RegraError("o card so pode andar uma coluna por vez")
        if destino == COLUNA_WIP and self.contar(COLUNA_WIP) >= LIMITE_WIP:
            raise RegraError(
                f"limite de WIP atingido: no maximo {LIMITE_WIP} cards em {COLUNA_WIP}"
            )
        card.coluna = destino
        return card

    def remover(self, card_id: int) -> None:
        self.obter(card_id)
        del self._cards[card_id]

    def resumo(self) -> dict:
        contagem = {coluna: self.contar(coluna) for coluna in COLUNAS}
        return {"colunas": contagem, "wip_livre": LIMITE_WIP - contagem[COLUNA_WIP]}
