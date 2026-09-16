import re

import pandas as pd
import streamlit as st
from pypdf import PdfReader
from pypdf.errors import PdfReadError

# --- Configuração da Página ---
st.set_page_config(
    page_title="Modificador de Variante",
    page_icon="🚛",
    layout="wide"
)

# --- Cor de destaque (complementa o tema padrão do .streamlit/config.toml) ---
# Best-effort: mira nos seletores mais comuns do Streamlit para botões
# primários e no indicador da aba ativa. Como não há como renderizar CSS de
# navegador neste ambiente, vale conferir visualmente ao rodar o app.
PALETAS = {
    "Azul-aço": "#1B3B6F",
    "Verde": "#1E7145",
    "Vermelho suave": "#B3453A",
}

with st.sidebar:
    st.subheader("🎨 Aparência")
    tema = st.selectbox("Cor de destaque", list(PALETAS.keys()), key="cor_destaque")
    st.caption(
        "Prefere tema claro/escuro? Use o menu **⋮** (canto superior direito) "
        "→ **Settings** → **Choose app theme**."
    )

_cor = PALETAS[tema]
st.markdown(
    f"""
    <style>
    button[kind="primary"], [data-testid="stBaseButton-primary"],
    .stDownloadButton > button[kind="primary"] {{
        background-color: {_cor} !important;
        border-color: {_cor} !important;
    }}
    [data-baseweb="tab-highlight"] {{
        background-color: {_cor} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
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


def texto_do_pdf(arquivo):
    """Extrai o texto de um PDF enviado via st.file_uploader.

    Usa extraction_mode="plain" (o padrão do pypdf) de propósito: ele devolve
    o Code e a Denominação em linhas separadas, formato que a extrair() já
    trata (mesma lógica usada quando o usuário cola o texto manualmente).
    """
    leitor = PdfReader(arquivo)
    return "\n".join(pagina.extract_text() for pagina in leitor.pages)


# ==================================================================
# Interface
# ==================================================================

st.title("🚛 Modificador de Code")

with st.expander("Como usar"):
    st.markdown("""
    **Opção 1 — enviar o PDF (recomendado):** anexe o arquivo `.pdf` da
    composição da variante e clique em **Extrair do PDF**.

    **Opção 2 — colar o texto:** copie o texto do PDF (Ctrl+A, Ctrl+C dentro
    do visualizador) e cole na caixa da aba "Colar texto".
    """)

if "resultado" not in st.session_state:
    st.session_state.resultado = None

aba_pdf, aba_texto = st.tabs(["📄 Enviar PDF", "📋 Colar texto"])

with aba_pdf:
    arquivo_pdf = st.file_uploader("Selecione o PDF da composição da variante:", type="pdf")
    if st.button("Extrair do PDF", type="primary", disabled=arquivo_pdf is None):
        try:
            texto_extraido = texto_do_pdf(arquivo_pdf)
        except PdfReadError:
            st.session_state.resultado = None
            st.error(
                "Não foi possível ler esse arquivo como PDF. Confira se o "
                "arquivo não está corrompido e tente novamente."
            )
        else:
            if texto_extraido.strip():
                st.session_state.resultado = extrair(texto_extraido)
            else:
                st.session_state.resultado = None
                st.error(
                    "O PDF foi lido, mas nenhum texto foi encontrado nele "
                    "(pode ser um PDF escaneado/imagem). Tente colar o texto "
                    "manualmente na outra aba."
                )

with aba_texto:
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
            # Guardar em session_state faz o resultado sobreviver aos reruns
            # que o Streamlit dispara ao clicar em outros botões (ex.: Baixar .txt).
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
    declarado = registros[0] if len(registros) == 1 else None

    st.divider()

    # --- Cartão com o cabeçalho (variante, baumuster, contagens) e ---
    # --- qualquer inconsistência crítica que mereça atenção antes de copiar. ---
    with st.container(border=True):
        col_variante, col_baumuster, col_encontrados, col_saida = st.columns(4)

        with col_variante:
            st.metric("🔢 Nº da Variante", variantes[0] if variantes else "—")

        with col_baumuster:
            st.metric("🏭 Baumuster", baumusters[0] if baumusters else "—")

        with col_encontrados:
            # Delta só aparece quando há divergência com o "Nº de Registros"
            # do PDF — some quando bate, para não poluir o caso normal.
            delta = None
            if declarado is not None and declarado != resultado["total_encontrado"]:
                delta = resultado["total_encontrado"] - declarado
            st.metric(
                "📄 Registros encontrados",
                resultado["total_encontrado"],
                delta=delta,
                delta_color="inverse",
                help="Comparado com o 'Nº de Registros' declarado pelo próprio PDF.",
            )

        with col_saida:
            st.metric("📦 Codes na saída", len(saida))

        if not variantes:
            st.warning("Nº da Variante não encontrado.")
        if not baumusters:
            st.warning("Baumuster não encontrado.")

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

        if declarado is not None:
            if declarado == resultado["total_encontrado"]:
                st.success(f"Conferência OK: o PDF declara **{declarado} registros**.")
            else:
                st.error(
                    f"Divergência: o PDF declara **{declarado} registros**, mas foram "
                    f"encontrados **{resultado['total_encontrado']}**. "
                    "Confira se o texto foi colado por completo."
                )
        else:
            st.info(
                "O texto não traz o 'Nº de Registros' — não foi possível conferir "
                "a contagem automaticamente."
            )

    # --- Resultado pronto para copiar (logo após o cartão, é o que importa) ---
    st.subheader("Resultado (Pronto para Copiar)")

    if saida:
        texto_saida = "\n".join(code for code, _ in saida)
        st.code(texto_saida, language=None)

        sufixo_arquivo = variantes[0] if variantes else "codes"

        col_txt, col_csv = st.columns(2)
        with col_txt:
            st.download_button(
                "⬇️ Baixar .txt",
                data=texto_saida,
                file_name=f"codes_{sufixo_arquivo}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col_csv:
            # utf-8-sig para o Excel abrir os acentos da Denominação corretamente.
            tabela_csv = pd.DataFrame(saida, columns=["Code", "Denominação"]).to_csv(
                index=False
            ).encode("utf-8-sig")
            st.download_button(
                "⬇️ Baixar tabela (.csv)",
                data=tabela_csv,
                file_name=f"codes_{sufixo_arquivo}.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.warning("Nenhum code válido foi encontrado no texto fornecido.")

    # --- Avisos secundários: não impedem o uso do resultado acima, mas ---
    # --- valem uma conferência. ---
    if resultado["repetidos"]:
        st.warning(
            f"{resultado['repetidos']} code(s) repetido(s) foram removidos da saída."
        )

    if resultado["descartados"]:
        nomes = ", ".join(f"{c} ({d})" if d else c for c, d in resultado["descartados"])
        st.info(f"Fora da saída (não é code de componente): {nomes}")

    if saida:
        with st.expander(f"Conferir os {len(saida)} codes e suas descrições"):
            st.dataframe(
                pd.DataFrame(saida, columns=["Code", "Denominação"]),
                hide_index=True,
            )
