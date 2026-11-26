"""Gera um resumo em Markdown a partir de um relatorio JUnit XML."""

import sys
import xml.etree.ElementTree as ET  # noqa: S405 - arquivo gerado pelo proprio pipeline


def main(caminho: str) -> int:
    raiz = ET.parse(caminho).getroot()  # noqa: S314
    suite = raiz if raiz.tag == "testsuite" else raiz.find("testsuite")
    total = int(suite.get("tests", 0))
    falhas = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
    puladas = int(suite.get("skipped", 0))
    print(
        f"- Total: **{total}** | Aprovados: **{total - falhas - puladas}** | "
        f"Falhas: **{falhas}** | Ignorados: **{puladas}** | Tempo: {suite.get('time')}s"
    )
    for caso in suite.iter("testcase"):
        if caso.find("failure") is not None or caso.find("error") is not None:
            print(f"  - FALHOU: `{caso.get('classname')}::{caso.get('name')}`")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
