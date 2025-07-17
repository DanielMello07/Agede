# Agede - Agente Inteligente de Combate à Dengue

A Agede é uma inteligência artificial especializada em dengue que coleta dados, analisa informações e explica conceitos de forma simples. Seu objetivo é democratizar o acesso a informações confiáveis sobre dengue para toda a população, especialmente comunidades com menor acesso a serviços de saúde.

## Funcionalidades principais
- Coleta automática de dados de fontes confiáveis como OPAS/OMS, SciELO e COFEN
- Respostas claras em linguagem acessível para qualquer pessoa
- Atualização diária das informações sobre dengue
- Interface simples que funciona em celulares e computadores

## Tecnologias utilizadas
Usamos Python com Flask para criar o sistema principal. Para coletar dados dos sites, usamos BeautifulSoup e PDFPlumber. O frontend foi desenvolvido com Bootstrap para garantir que funcione bem em qualquer dispositivo, usando HTML, CSS e JavaScript.

## Como executar
1. Instale o Python (versão 3.8 ou superior)

2. Abra o terminal na pasta do projeto

3. Instale as bibliotecas necessárias:
pip install flask beautifulsoup4 requests pdfplumber

5. Execute o aplicativo:
python agede.py

5. Acesse no seu navegador:
http://localhost:5000

A Agede estará pronta para responder suas perguntas sobre dengue de forma simples e direta, com informações atualizadas das melhores fontes de saúde.
