import requests
from bs4 import BeautifulSoup
import pdfplumber
import json
from datetime import datetime
from urllib.parse import urljoin
import os
import tempfile

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SITES = {
    "ministerio_da_saude": "https://www.gov.br/saude/pt-br/assuntos/noticias?b_start:int=0",
    "paho_opas": "https://www.paho.org/pt/topicos/dengue",
    "cofen": "http://www.cofen.gov.br/?s=dengue",
    "scielo": "https://search.scielo.org/?q=dengue&lang=pt&count=10"
}

ARQUIVO_SAIDA = "dados_dengue.json"

def baixar_e_extrair_pdf(url_pdf):
    try:
        response = requests.get(url_pdf, headers=HEADERS, timeout=15)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(response.content)
            caminho_pdf = tmp_pdf.name

        texto_extraido = ""
        with pdfplumber.open(caminho_pdf) as pdf:
            for pagina in pdf.pages:
                texto_extraido += pagina.extract_text() or ""

        os.remove(caminho_pdf)
        return texto_extraido.strip()
    except Exception as e:
        return f"Erro ao processar PDF {url_pdf}: {e}"

def extrair_links_com_conteudo(url_base, palavra_chave="dengue", limite=10):
    try:
        response = requests.get(url_base, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a", href=True)

        resultados = []
        links_visitados = set()

        for a in links:
            href = a["href"]
            texto_link = a.get_text(strip=True)

            if palavra_chave.lower() not in texto_link.lower():
                continue

            link_completo = urljoin(url_base, href)
            if link_completo in links_visitados:
                continue
            links_visitados.add(link_completo)

            if link_completo.endswith(".pdf"):
                texto_pdf = baixar_e_extrair_pdf(link_completo)
                resultados.append(f"[PDF] {texto_link}:\n{texto_pdf[:1000]}")
            else:
                try:
                    sub_resp = requests.get(link_completo, headers=HEADERS, timeout=10)
                    sub_soup = BeautifulSoup(sub_resp.content, "html.parser")
                    texto_pagina = " ".join(p.get_text(strip=True) for p in sub_soup.find_all("p"))
                    resultados.append(f"{texto_link}:\n{texto_pagina[:2000]}")
                except Exception as e:
                    resultados.append(f"Erro ao acessar {link_completo}: {e}")

            if len(resultados) >= limite:
                break

        return resultados
    except Exception as e:
        return [f"Erro ao acessar {url_base}: {e}"]

def coletar_dados():
    resultados = {
        "data_coleta": datetime.now().isoformat(),
        "conteudos": {}
    }

    for nome, url in SITES.items():
        print(f"🔎 Coletando de {nome}...")
        resultados["conteudos"][nome] = extrair_links_com_conteudo(url)

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Dados salvos em {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    coletar_dados()
