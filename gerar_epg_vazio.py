import datetime
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
from xml.dom import minidom

def gerar_xmltv():
    channel_id = "Canal24.7"
    channel_name = "Canal 24/7"
    program_desc = "Programação Regular do Canal Ao Vivo."

    tv = ET.Element("tv", attrib={"generator-info-name": "Gerador EPG Automático"})

    channel = ET.SubElement(tv, "channel", attrib={"id": channel_id})
    display_name = ET.SubElement(channel, "display-name")
    display_name.text = channel_name

    # 1. Força o fuso horário do Brasil (Brasília/São Paulo)
    fuso_brasil = ZoneInfo("America/Sao_Paulo")
    agora_brasil = datetime.datetime.now(fuso_brasil)
    
    # 2. Zera minutos e segundos baseado no horário do Brasil
    hora_inicio = agora_brasil.replace(minute=0, second=0, microsecond=0)

    for i in range(24):
        inicio_bloco = hora_inicio + datetime.timedelta(hours=i)
        fim_bloco = hora_inicio + datetime.timedelta(hours=i + 1)

        # 3. Formata a hora incluindo a tag de fuso (ex: -0300) para a TV ler perfeitamente
        str_inicio = inicio_bloco.strftime("%Y%m%d%H%M%S %z")
        str_fim = fim_bloco.strftime("%Y%m%d%H%M%S %z")

        programme = ET.SubElement(tv, "programme", attrib={
            "start": str_inicio,
            "stop": str_fim,
            "channel": channel_id
        })

        # 4. Título dinâmico com o horário correto do Brasil
        exibicao_inicio = inicio_bloco.strftime("%H:%M")
        exibicao_fim = fim_bloco.strftime("%H:%M")
        program_title = f"Programação 24/7 ({exibicao_inicio} - {exibicao_fim})"

        title = ET.SubElement(programme, "title", attrib={"lang": "pt"})
        title.text = program_title
        
        desc = ET.SubElement(programme, "desc", attrib={"lang": "pt"})
        desc.text = program_desc

    xml_string = ET.tostring(tv, encoding="utf-8")
    reparsed = minidom.parseString(xml_string)
    xml_bonito = reparsed.toprettyxml(indent="  ")

    with open("epg_canal_vazio.xml", "w", encoding="utf-8") as f:
        f.write(xml_bonito)

    print("Sucesso: O arquivo 'epg.xml' foi gerado com base no horário do Brasil!")

if __name__ == "__main__":
    gerar_xmltv()
