# Evidências de cobertura

1. Rode localmente: `pip install -e ../oficina-contracts && pip install -e ".[dev]" && pytest --cov-report=term-missing`
2. No GitHub Actions, baixe o artefato **coverage-report** do workflow CI/CD.
3. Cole um print do terminal ou do relatório HTML em `cobertura-AAAA-MM-DD.png` nesta pasta e referencie no README.

Exemplo de link no README:

`https://github.com/TGuapyassu/oficina-os-service/actions/workflows/ci-cd.yml`
