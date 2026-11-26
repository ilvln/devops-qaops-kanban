"""API HTTP (Flask) e pagina web do quadro Kanban."""

from flask import Flask, jsonify, request

from app import __version__
from app.domain import NaoEncontradoError, Quadro, RegraError, ValidacaoError


def _corpo_json() -> dict:
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ValueError("corpo JSON invalido")
    return dados


def _registrar_erros(app: Flask) -> None:
    """Converte as excecoes do dominio em respostas HTTP."""

    @app.errorhandler(ValidacaoError)
    def _validacao(exc):
        return jsonify(erro=str(exc)), 422

    @app.errorhandler(RegraError)
    def _regra(exc):
        return jsonify(erro=str(exc)), 409

    @app.errorhandler(NaoEncontradoError)
    def _nao_encontrado(exc):
        return jsonify(erro=str(exc)), 404

    @app.errorhandler(ValueError)
    def _json_invalido(exc):
        return jsonify(erro=str(exc)), 400


def create_app() -> Flask:
    app = Flask(__name__)
    quadro = Quadro()

    _registrar_erros(app)

    @app.get("/")
    def pagina():
        return app.send_static_file("index.html")

    @app.get("/health")
    def health():
        return jsonify(status="ok", versao=__version__)

    @app.get("/api/cards")
    def listar():
        cards = quadro.listar(request.args.get("coluna"))
        return jsonify([c.para_dict() for c in cards])

    @app.post("/api/cards")
    def criar():
        dados = _corpo_json()
        card = quadro.criar(dados.get("titulo"), dados.get("prioridade", "MEDIA"))
        return jsonify(card.para_dict()), 201

    @app.post("/api/cards/<int:card_id>/mover")
    def mover(card_id: int):
        dados = _corpo_json()
        return jsonify(quadro.mover(card_id, dados.get("coluna")).para_dict())

    @app.delete("/api/cards/<int:card_id>")
    def remover(card_id: int):
        quadro.remover(card_id)
        return "", 204

    @app.get("/api/resumo")
    def resumo():
        return jsonify(quadro.resumo())

    return app


if __name__ == "__main__":  # pragma: no cover
    create_app().run(host="127.0.0.1", port=5000)
