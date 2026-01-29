import streamlit as st

# --- Configuração da Página ---
st.set_page_config(
    page_title="Ferramenta para Modificação de Code",
    page_icon="🚛",
    layout="wide"
)

# --- Título e Descrição ---
st.title("Ferramenta para Modificação de Code")
st.markdown("""
**Instruções:**
1.  Copie todo o texto da composição da variante extraído do PDF da variante.
2.  Cole o texto na área abaixo.
3.  Clique no botão **"Extrair Códigos"**.
4.  O resultado aparecerá em uma caixa abaixo.
""")

# --- Área de Entrada de Texto ---
input_text = st.text_area(
    "Cole a 'Composição da Variante' aqui:",
    height=300
)

# --- Botão e Lógica de Extração ---
if st.button("Extrair Códigos", type="primary"):
    if input_text:
        extracted_codes = []
        lines = input_text.splitlines()

        for line in lines:
            # remove espaços em branco no início e fim da linha
            clean_line = line.strip()

            # verifica se a linha começa com "IN" e tem pelo menos 5 caracteres
            if clean_line.startswith('IN') and len(clean_line) >= 5:
                # pega a primeira palavra (o código) e extrai os 3 caracteres
                code_part = clean_line.split()[0]
                extracted_code = code_part[2:5]
                extracted_codes.append(extracted_code)

        if extracted_codes:
            st.success(f"**{len(extracted_codes)} códigos extraídos com sucesso!**")

            # junta todos os códigos em uma única string, separados por quebra de linha
            codes_with_linebreak = "\n".join(extracted_codes)

            st.subheader("Resultado (Pronto para Copiar)")
            # st.code() exibe o texto e adiciona automaticamente um botão para copiar
            st.code(codes_with_linebreak, language=None)

        else:
            st.warning("Nenhum código válido (iniciando com 'IN') foi encontrado no texto fornecido.")
    else:
        st.error("Por favor, cole o texto na área designada antes de extrair.")