import datetime
import html  # Garante que caracteres especiais não quebrem o XML
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import pytz
import requests


def obter_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Erro ao acessar a página: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None


def extrair_programas(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    programas_extraidos = []

    # Encontra todos os blocos com a classe fornecida
    blocos = soup.find_all("div", class_="program-info")

    for bloco in blocos:
        title_div = bloco.find("div", class_="title")
        details_div = bloco.find("div", class_="details")

        if title_div and details_div:
            # Escapa caracteres especiais para manter o XML válido
            titulo = html.escape(title_div.text.strip())
            detalhes_texto = details_div.text.strip()

            # Captura os horários no formato 00h00 usando Expressão Regular
            horas_encontradas = re.findall(r"(\d{2})h(\d{2})", detalhes_texto)

            if horas_encontradas:
                hora_inicio = (
                    f"{horas_encontradas[0][0]}:{horas_encontradas[0][1]}"
                )
                hora_fim = (
                    f"{horas_encontradas[1][0]}:{horas_encontradas[1][1]}"
                    if len(horas_encontradas) > 1
                    else None
                )

                programas_extraidos.append(
                    {
                        "titulo": titulo,
                        "hora_inicio": hora_inicio,
                        "hora_fim": hora_fim,
                    }
                )

    return programas_extraidos


def formatar_data_xmltv(data_base, string_horario):
    try:
        hora, minuto = map(int, string_horario.split(":"))
        dt = data_base.replace(
            hour=hora, minute=minuto, second=0, microsecond=0
        )

        fuso_local = pytz.timezone("America/Sao_Paulo")
        dt_local = fuso_local.localize(dt)
        return dt_local.strftime("%Y%m%d%H%M%S %z")
    except Exception:
        return None


def criar_xmltv(programas, nome_arquivo="epg.xml"):
    tv_root = ET.Element("tv")
    tv_root.set("generator-info-name", "Gerador EPG TVPlus Preciso")

    # ID DO CANAL ATUALIZADO PARA: YeeaahTV
    channel_id = "YeeaahTV"
    channel_el = ET.SubElement(tv_root, "channel", id=channel_id)
    display_name = ET.SubElement(channel_el, "display-name")
    display_name.text = "Yeeaah TV2"

    data_hoje = datetime.datetime.now()

    for i, prog in enumerate(programas):
        inicio_formatado = formatar_data_xmltv(data_hoje, prog["hora_inicio"])
        if not inicio_formatado:
            continue

        # Define o horário de fim do programa
        if prog["hora_fim"]:
            fim_formatado = formatar_data_xmltv(data_hoje, prog["hora_fim"])
        elif i < len(programas) - 1:
            fim_formatado = formatar_data_xmltv(
                data_hoje, programas[i + 1]["hora_inicio"]
            )
        else:
            # Fallback caso seja o último item (adiciona 30 minutos)
            hora, minuto = map(int, prog["hora_inicio"].split(":"))
            dt_fim = data_hoje.replace(
                hour=hora, minute=minuto
            ) + datetime.timedelta(minutes=30)
            fim_formatado = (
                pytz.timezone("America/Sao_Paulo")
                .localize(dt_fim)
                .strftime("%Y%m%d%H%M%S %z")
            )

        prog_el = ET.SubElement(
            tv_root,
            "programme",
            start=inicio_formatado,
            stop=fim_formatado,
            channel=channel_id,
        )

        title_el = ET.SubElement(prog_el, "title", lang="pt")
        title_el.text = prog["titulo"]

        desc_el = ET.SubElement(prog_el, "desc", lang="pt")
        desc_el.text = "Programação regular transmitida pela Yeeaah TV."

    tree = ET.ElementTree(tv_root)
    ET.indent(tree, space="  ", level=0)
    tree.write(nome_arquivo, encoding="utf-8", xml_declaration=True)
    print(f"\nSucesso! Arquivo EPG gravado em: {nome_arquivo}")


if __name__ == "__main__":
    url_alvo = "https://tvplus.com.br/programacao/yeeaah"

    print("Buscando dados da página...")
    html_content = obter_html(url_alvo)

    if html_content:
        print("Processando HTML com base na classe 'program-info'...")
        lista_programas = extrair_programas(html_content)

        if lista_programas:
            print(f"Encontrados {len(lista_programas)} programas na grade.")
            criar_xmltv(lista_programas)
        else:
            print(
                "Nenhum programa encontrado. Verifique se a estrutura mudou."
            )
