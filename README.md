# 🚛 Extrator de Códigos para Modificação de Variantes (Mercedes-Benz)

Esta ferramenta foi desenvolvida para agilizar o processo de customização de caminhões conforme as necessidades das concessionárias. Ela elimina a necessidade de comparação manual entre variantes, tornando o processo de alteração muito mais rápido e seguro.

## 🚀 O que esta ferramenta resolve?

Antigamente, era necessário comparar a **Variante Atual** com a **Nova Variante** e modificar apenas os códigos divergentes. Isso tomava tempo e abria margem para erros.

**Com este sistema, o fluxo de trabalho foi simplificado:**
1. Você limpa todos os códigos atuais do veículo no AFAB.
2. Extrai a composição da nova variante pelo Sales.
3. Insere todos os novos códigos de uma vez (resultado do sistema).

Dessa forma, a "variante atual" não importa mais, pois garantimos que a nova configuração será inserida de forma integral e formatada corretamente.

---

## 🛠️ Como usar (Passo a Passo)

O sistema foi desenhado para ser intuitivo, mesmo para quem não tem experiência com tecnologia:

1.  **Acesse a composição da variante:** Baixe o PDF da variante desejada pelo Sales Excellence.
2.  **Copie os dados:** Selecione e copie o texto da lista de composição **(Exceto code BRASIL)**.
3.  **Cole no Extrator:** Cole o texto bruto na área indicada no sistema ("Cole a 'Composição da Variante' aqui").
4.  **Processe os dados:** Clique no botão azul **"Extrair Códigos"**.
5.  **Copie o resultado:** O sistema filtrará a formatação correta dos codes para inserção no AFAB.
6.  **Cole o resultado:** Com o veículo sem nenhum code, cole o resultado do sistema no AFAB.

OBS: Sempre confira, depois de colar os codes, o code correspondente ao **Ano do Modelo** do veículo.

---

## ⚙️ Como o sistema funciona?

* Filtra apenas linhas que começam com o padrão **"IN"**.
* Ignora espaços em branco e textos desnecessários.
* Extrai exatamente os **3 caracteres** de identificação após o prefixo.
* Gera uma lista limpa, com um código por linha, que é o formato aceito pelo software de modificação (AFAB).

---

## 🔐 Requisitos de Acesso

A ferramenta está hospedada na nuvem, dispensando qualquer instalação no seu computador. Para acessar, siga os requisitos abaixo:

* **Link de Acesso:** [https://truckcodes.streamlit.app]
* **Conta no Streamlit:** É necessário possuir uma conta cadastrada no [Streamlit.io](https://streamlit.io/) (você pode usar seu e-mail corporativo).
* **Autorização:** Por questões de segurança, o acesso é restrito. Caso não consiga visualizar o app, entre em contato comigo para que eu possa **liberar o seu e-mail** na lista de usuários permitidos.

---

## 👤 Informações do Desenvolvedor

**Nome:** Leonardo Miranda

**Cargo:** Estagiário VCRP

**Empresa:** Mercedes-Benz

**Desenvolvido em:** Outubro de 2025
