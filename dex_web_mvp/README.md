# Dex Web MVP

Esta versão tem interface web simples com Streamlit.

## O que ela faz

- Chat do aluno com o Dex
- Aba do professor
- Memória por aluno
- Upload/edição simples da base de conhecimento
- Integração com OpenAI
- Banco SQLite local

## Como instalar

```bash
cd dex_web_mvp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Abra o arquivo `.env` e coloque sua chave da OpenAI:

```text
OPENAI_API_KEY=sua_chave_aqui
```

## Como rodar

```bash
streamlit run app.py
```

Depois abra o link que aparecer no terminal.

Normalmente será:

```text
http://localhost:8501
```

## Como testar

1. Abra a aba Student Chat.
2. Coloque o student_id, por exemplo: turco.
3. Escreva uma frase em inglês.
4. O Dex responde e salva a conversa.
5. Vá na aba Teacher Dashboard.
6. Escolha o mesmo student_id.
7. Clique em Generate Student Summary.
