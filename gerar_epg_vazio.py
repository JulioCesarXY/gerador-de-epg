import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

def gerar_xmltv():
    # 1. Configurações básicas do canal
    channel_id = "Canal24.7"
    channel_name = "Canal 24/7"
    program_title = "Programação 24/7"
    program_desc = "Programação Regular do Canal Ao Vivo."

    # 2. Criar a estrutura raiz do XML
    tv = ET.Element("tv", attrib={"generator-info-name": "Gerador EPG Automático"})

    # Adicionar o canal
    channel = ET.SubElement(tv, "channel", attrib={"id": channel_id})
    display_name = ET.SubElement(channel, "display-name")
    display_name.text = channel_name

    # 3. Definir o início (hora atual zerada nos minutos/segundos para ficar organizado)
    agora = datetime.datetime.now()
    hora_inicio = agora.replace(minute=0, second=0, microsecond=0)

    # 4. Gerar 24 blocos de 1 hora
    for i in range(24):
        inicio_bloco = hora_inicio + datetime.timedelta(hours=i)
        fim_bloco = hora_inicio + datetime.timedelta(hours=i + 1)

        # Formato de data exigido pelo XMLTV: YYYYMMDDhhmmss +0000 (ou o fuso local)
        # Usaremos o formato local padrão simples: YYYYMMDDhhmmss +0000
        str_inicio = inicio_bloco.strftime("%Y%m%d%H%M%S +0000")
        str_fim = fim_bloco.strftime("%Y%m%d%H%M%S +0000")

        # Criar elemento do programa
        programme = ET.SubElement(tv, "programme", attrib={
            "start": str_inicio,
            "stop": str_fim,
            "channel": channel_id
        })

        # Título e Descrição
        title = ET.SubElement(programme, "title", attrib={"lang": "pt"})
        title.text = f"{program_title} - {inicio_bloco.strftime('%H:%M')}"
        
        desc = ET.SubElement(programme, "desc", attrib={"lang": "pt"})
        desc.text = program_desc

    # 5. Identar e salvar o arquivo de forma bonita (Pretty Print)
    xml_string = ET.tostring(tv, encoding="utf-8")
    reparsed = minidom.parseString(xml_string)
    xml_bonito = reparsed.toprettyxml(indent="  ")

    # Salvar no arquivo epg.xml
    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(xml_bonito)

    print("Sucesso: O arquivo 'epg.xml' foi gerado com as próximas 24 horas!")

if __name__ == "__main__":
    gerar_xmltv()
