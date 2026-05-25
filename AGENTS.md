# AGENTS.md - Diretrizes de Desenvolvimento SOTA

## Regras de Segurança e Contexto (Obrigatório)
Qualquer comando que leia ficheiros de dados, logs ou outputs de execução DEVE limitar a saída para evitar o colapso do contexto do LLM:

- **Padrão Obrigatório:** `COMMAND 2>&1 | head -c 4000`
- **Proibição:** Nunca usar `cat`, `head -n` ou `grep` diretamente em ficheiros grandes sem o pipe para `head -c 4000`.
- **Justificação:** Esta medida protege o buffer de contexto contra ficheiros binários ou grandes datasets.

## Padrões de Código
- Código modular, seguindo o padrão já estabelecido em `src/`.
- Documentação em docstrings seguindo estilo Google.
- Validação de erros em cada etapa da pipeline.