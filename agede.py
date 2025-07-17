from flask import Flask, render_template, request, jsonify, session
from meta_ai_api import MetaAI
import json
import os
from datetime import datetime

# IMPORTA o coletor de dados como módulo
from coletar_dados_dengue import coletar_dados

ai = MetaAI()
app = Flask(__name__)
app.secret_key = "segredo-super-seguro"  # Necessário para session

# Rota de verificação de saúde
@app.route('/health')
def health_check():
    return "Bot online com sucesso! 🟶"

@app.route('/')
def index():
    session.clear()

    # Atualiza os dados automaticamente ao iniciar
    atualizar = False
    if not os.path.exists("dados_dengue.json"):
        atualizar = True
    else:
        ultima_mod = datetime.fromtimestamp(os.path.getmtime("dados_dengue.json"))
        hoje = datetime.now()
        if (hoje - ultima_mod).days >= 1:
            atualizar = True

    if atualizar:
        try:
            coletar_dados()
            print(" Dados atualizados ao iniciar Agede.")
        except Exception as e:
            print(f" Erro ao coletar dados no início: {e}")

    return render_template('index.html')


@app.route('/send', methods=['POST'])
def send():
    entrada = request.form.get('userInput', '').strip()

    if not entrada:
        return jsonify({'response': '<p><small>Por favor, envie uma pergunta ou mensagem válida.</small></p>'})

    if entrada.lower() == '/sair':
        return jsonify({'response': '<p>Saindo do programa...</p>'})

    if "resumo coletado" in entrada.lower():
        if os.path.exists("dados_dengue.json"):
            try:
                with open("dados_dengue.json", "r", encoding="utf-8") as f:
                    dados = json.load(f)
                resumo = "<h4>Últimos dados coletados:</h4><br>"
                for fonte, textos in dados.get("conteudos", {}).items():
                    resumo += f"<strong>{fonte.upper()}</strong><br><ul>"
                    for t in textos[:5]:
                        resumo += f"<li>{t}</li>"
                    resumo += "</ul><br>"
                return jsonify({'response': resumo})
            except Exception as e:
                return jsonify({'response': f'<p><small>Erro ao ler dados: {e}</small></p>'})
        else:
            return jsonify({'response': '<p><small>Nenhum dado coletado ainda. Execute o script de coleta primeiro.</small></p>'})

    # Contexto para a IA
    dados_coletados = ""
    if os.path.exists("dados_dengue.json"):
        try:
            with open("dados_dengue.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
                for fonte, textos in dados.get("conteudos", {}).items():
                    dados_coletados += f"\nFonte: {fonte.upper()}\n"
                    for t in textos[:3]:
                        dados_coletados += f"- {t}\n"
                    dados_coletados += "\n"
        except Exception as e:
            dados_coletados = f"\n[Erro ao carregar dados: {e}]\n"

    # Prompt para a IA
    prompt = (
        f"{dados_coletados}\n"
        "Você é Agede, uma inteligência artificial especializada exclusivamente em pesquisas sobre dengue.  Sempre se apresente como Agede. Se apresente somente uma vez, na primeir amensagem. "
        "Use uma linguagem simples, informativa e direta, para facilitar a compreensão de pessoas leigas. "
        "Nunca responda perguntas que não sejam relacionadas à dengue. "
        "Sempre forneça os links das fontes de onde os dados foram coletados, exceto quando não aplicável. "
        "Use HTML para formatar sua resposta com tags como: <h4>, <strong>, <p>, <ul>, <li>, <small>. "
        "NÃO inclua tags <html>, <head> ou <body>. "
        "Separe os blocos com quebras de linha. "
        "Nunca use jargões técnicos. "
        "Nunca responda nada fora do tema dengue. "
        f"Mensagem do usuário: {entrada}"
    )

    resposta = ai.prompt(message=prompt)
    mensagem_final = resposta.get("message", "<p><small>Não foi possível obter resposta da IA.</small></p>")
    
    if not mensagem_final.startswith('<'):
        mensagem_final = f"<p>{mensagem_final}</p>"
    
    return jsonify({'response': mensagem_final})


if __name__ == '__main__':
    # Configuração para funcionar em serviços de hospedagem
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)