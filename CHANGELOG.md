# Changelog

Todas as mudanças relevantes da ferramenta de modificação de Code são registradas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).

## [v2] — codes_pdf_v2.py

### Corrigido
- **Falso positivo em descrições que começam com "IN".** A v1 aceitava qualquer
  linha iniciada em "IN" com 5+ caracteres como se fosse um code. Descrições como
  `INTERFACE, FLEET MANAGEMENT SYSTEM FMS` ou `INTERRUP.DESCONEXAO BATERIA...`
  podiam gerar codes falsos (ex.: `TER`) dependendo de como o PDF é colado
  (colunas Code/Denominação em linhas separadas). A v2 exige que o token inteiro
  seja `IN` + 3 ou 4 caracteres (`fullmatch`), não apenas o início da linha.
- **Codes de 3 letras (sem dígito no meio) não eram truncados corretamente.**
  A v1 sempre fatiava `[2:5]`, assumindo o formato fixo letra-número-letra.
  Existem codes reais só com letras (ex.: `ZZU`, `UPI`, `IYZ`) que a v1 devolvia
  incorretos. A v2 captura o code inteiro via regex, sem assumir tamanho fixo.
- **Baumuster com quantidade variável de dígitos não era sempre encontrado.**
  A v1 buscava exatamente `C` + 10 dígitos. Na prática o Baumuster começa com
  `C9` e pode ter 8, 9, 10 ou 11+ dígitos. A v2 aceita `C9` seguido de 4+ dígitos.
- **Resultado sumia ao clicar em outro botão.** Na v1 o resultado só existia
  dentro do `if st.button(...)`; qualquer rerender do Streamlit (ex.: clicar em
  "Baixar") apagava a tela. A v2 guarda o resultado em `st.session_state`.

### Adicionado
- **Extração do Nº da Variante** (`QVV` + dígitos + `C`/`T`), exibida em campo
  próprio com botão de copiar — mantida fora da caixa de codes.
- **Baumuster retornado sem o `C`** (só a parte numérica), conforme pedido.
- **Conferência automática de contagem**: compara os codes encontrados com o
  `Nº de Registros` que o próprio PDF declara, e avisa se houver divergência.
- **Detecção de múltiplas variantes/baumusters no mesmo texto** — alerta se o
  usuário colar mais de um PDF junto sem perceber.
- **Deduplicação de codes**, com aviso de quantos foram removidos.
- **Tabela de conferência** (code + denominação) num expander, para auditoria
  visual antes de colar no sistema de destino.
- **Botão de download em `.txt`** do resultado.
- Envio do formulário com `Ctrl + Enter`.

### Removido
- **Code `775L` (formato "país/mercado", não é code de componente) excluído
  da saída por decisão explícita** — nunca deve aparecer, nem completo nem
  truncado. Qualquer code descartado por esse motivo aparece listado na tela
  para conferência, sem ser silenciosamente omitido.

### Não alterado
- `codes_pdf.py` (v1) permanece intocado e funcional, para rollback imediato
  se necessário.
