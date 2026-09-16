import re

import pandas as pd
import streamlit as st

# --- Configuração da Página ---
st.set_page_config(
    page_title="Ferramenta para Modificação de Code",
    page_icon="🚛",
    layout="wide"
)

# ==================================================================
# Regras de extração
# ==================================================================

# Nº da Variante: "QVV" + números + sufixo "C" ou "T" (normalmente "T").
# O tamanho da parte numérica varia, por isso \d+ em vez de \d{N}.
RE_VARIANTE = re.compile(r'\bQVV\d+[CT]\b')

# Rede de segurança: se o sufixo C/T não vier, ainda assim achamos a variante.
RE_VARIANTE_SEM_SUFIXO = re.compile(r'\bQVV\d+\b')

# Baumuster: "C9" + dígitos, com quantidade variável de dígitos.
# O "C" fica FORA do grupo de captura porque a saída pedida é só a parte numérica.
RE_BAUMUSTER = re.compile(r'\bC(9\d{4,})\b')

# "Nº de Registros: 128" — o total que o próprio PDF declara.
# Usado para conferir automaticamente se a extração pegou tudo.
RE_REGISTROS = re.compile(r'N[º°o]?\s*de\s*Registros\s*:?\s*(\d+)', re.IGNORECASE)

# Uma célula da coluna "Code": exatamente "IN" + 3 ou 4 caracteres, nada mais.
# É o fullmatch que descarta descrições que por acaso começam com "IN"
# (ex.: "INTERFACE, FLEET MANAGEMENT SYSTEM FMS" -> "INTERFACE," não casa).
RE_CODE = re.compile(r'IN([A-Z0-9]{3,4})')


def _e_celula_de_code(token):
    """True se o token for uma célula da coluna Code (ex.: 'INA2Z')."""
    return RE_CODE.fullmatch(token) is not None


def _descricao_da_proxima_linha(linhas, i):
    """Busca a descrição na linha seguinte.

    Dependendo do leitor de PDF, o copiar/colar pode separar a coluna 'Code'
    da coluna 'Denominação' em duas linhas. Nesse caso a descrição está na
    próxima linha não-vazia — desde que ela já não seja outro code.
    """
    for proxima in linhas[i + 1:]:
        if not proxima:
            continue
        if _e_celula_de_code(proxima.split()[0]):
            return ""
        return proxima
    return ""


def _unicos(valores):
    """Remove duplicatas preservando a ordem de aparição."""
    vistos = set()
    saida = []
    for v in valores:
        if v not in vistos:
            vistos.add(v)
            saida.append(v)
    return saida


def extrair(texto):
    """Lê o texto colado da composição e devolve tudo que foi encontrado."""
    linhas = [linha.strip() for linha in texto.splitlines()]

    # --- Cabeçalho (repetido em toda página do PDF, por isso o _unicos) ---
    variantes = _unicos(RE_VARIANTE.findall(texto))
    if not variantes:
        variantes = _unicos(RE_VARIANTE_SEM_SUFIXO.findall(texto))

    baumusters = _unicos(RE_BAUMUSTER.findall(texto))
    registros = _unicos(int(n) for n in RE_REGISTROS.findall(texto))

    # --- Coluna "Code" ---
    encontrados = []
    for i, linha in enumerate(linhas):
        if not linha:
            continue

        partes = linha.split(None, 1)
        achou = RE_CODE.fullmatch(partes[0])
        if not achou:
            continue

        code = achou.group(1)
        if len(partes) > 1:
            descricao = partes[1].strip()
        else:
            descricao = _descricao_da_proxima_linha(linhas, i)

        encontrados.append((code, descricao))

    # Codes de verdade começam com letra. Os que começam com número são
    # registros de mercado/país (ex.: "775L - BRASIL") e não entram na saída.
    validos = [(c, d) for c, d in encontrados if c[0].isalpha()]
    descartados = [(c, d) for c, d in encontrados if not c[0].isalpha()]

    # Deduplica a saída preservando a ordem do PDF.
    vistos = set()
    saida = []
    for code, descricao in validos:
        if code not in vistos:
            vistos.add(code)
            saida.append((code, descricao))
    repetidos = len(validos) - len(saida)

    return {
        "variantes": variantes,
        "baumusters": baumusters,
        "registros": registros,
        "saida": saida,
        "descartados": descartados,
        "repetidos": repetidos,
        "total_encontrado": len(encontrados),
    }


# ==================================================================
# Interface
# ==================================================================

st.title("🚛 Ferramenta para Modificação de Code")

with st.expander("Como usar"):
    st.markdown("""
    1. Copie todo o texto da composição da variante extraído do PDF.
    2. Cole o texto na área abaixo.
    3. Clique em **Extrair Códigos** (ou pressione `Ctrl + Enter`).
    4. Confira o painel de validação e copie os codes pelo botão da caixa de resultado.
    """)

if "resultado" not in st.session_state:
    st.session_state.resultado = None

# O formulário permite enviar com Ctrl+Enter, sem precisar mirar no botão.
with st.form("formulario_extracao"):
    texto_colado = st.text_area(
        "Cole a 'Composição da Variante' aqui:",
        height=300,
        placeholder="Cole aqui o texto copiado do PDF da composição da variante...",
    )
    enviado = st.form_submit_button("Extrair Códigos", type="primary")

if enviado:
    if texto_colado.strip():
        # Guardar em session_state faz o resultado sobreviver aos reruns que o
        # Streamlit dispara ao clicar em outros botões (ex.: Baixar .txt).
        st.session_state.resultado = extrair(texto_colado)
    else:
        st.session_state.resultado = None
        st.error("Por favor, cole o texto na área designada antes de extrair.")

resultado = st.session_state.resultado

if resultado:
    saida = resultado["saida"]
    variantes = resultado["variantes"]
    baumusters = resultado["baumusters"]
    registros = resultado["registros"]

    st.divider()

    # --- Cabeçalho: variante, baumuster e contagem ---
    col_variante, col_baumuster, col_total = st.columns(3)

    with col_variante:
        st.caption("Nº da Variante")
        if variantes:
            st.code(variantes[0], language=None)
        else:
            st.warning("Não encontrada.")

    with col_baumuster:
        st.caption("Baumuster (sem o 'C')")
        if baumusters:
            st.code(baumusters[0], language=None)
        else:
            st.warning("Não encontrado.")

    with col_total:
        st.caption("Codes na saída")
        st.code(str(len(saida)), language=None)

    # Mais de um valor distinto = provavelmente duas composições coladas juntas.
    if len(variantes) > 1:
        st.error(
            f"Foram encontradas **{len(variantes)} variantes diferentes** no texto: "
            f"{', '.join(variantes)}. Confira se você não colou mais de um PDF."
        )
    if len(baumusters) > 1:
        st.error(
            f"Foram encontrados **{len(baumusters)} baumusters diferentes** no texto: "
            f"{', '.join(baumusters)}. Confira se você não colou mais de um PDF."
        )

    # --- Validação contra o "Nº de Registros" declarado pelo PDF ---
    if len(registros) == 1:
        declarado = registros[0]
        if declarado == resultado["total_encontrado"]:
            st.success(
                f"Conferência OK: o PDF declara **{declarado} registros** e foram "
                f"encontrados **{resultado['total_encontrado']}**."
            )
        else:
            st.error(
                f"Divergência: o PDF declara **{declarado} registros**, mas foram "
                f"encontrados **{resultado['total_encontrado']}**. "
                "Confira se o texto foi colado por completo."
            )
    else:
        st.info(
            "O texto colado não traz o 'Nº de Registros' — não foi possível "
            "conferir a contagem automaticamente."
        )

    if resultado["repetidos"]:
        st.warning(
            f"{resultado['repetidos']} code(s) repetido(s) foram removidos da saída."
        )

    if resultado["descartados"]:
        nomes = ", ".join(f"{c} ({d})" if d else c for c, d in resultado["descartados"])
        st.info(f"Fora da saída (não é code de componente): {nomes}")

    # --- Resultado pronto para copiar ---
    st.subheader("Resultado (Pronto para Copiar)")

    if saida:
        texto_saida = "\n".join(code for code, _ in saida)
        st.code(texto_saida, language=None)

        nome_arquivo = f"codes_{variantes[0]}.txt" if variantes else "codes.txt"
        st.download_button(
            "Baixar .txt",
            data=texto_saida,
            file_name=nome_arquivo,
            mime="text/plain",
        )

        with st.expander(f"Conferir os {len(saida)} codes e suas descrições"):
            st.dataframe(
                pd.DataFrame(saida, columns=["Code", "Denominação"]),
                hide_index=True,
            )
    else:
        st.warning("Nenhum code válido foi encontrado no texto fornecido.")
