import datetime
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

    # Pega o horário atual e zera os minutos/segundos para alinhar na hora cheia
    agora = datetime.datetime.now()
    hora_inicio = agora.replace(minute=0, second=0, microsecond=0)

    for i in range(24):
        inicio_bloco = hora_inicio + datetime.timedelta(hours=i)
        fim_bloco = hora_inicio + datetime.timedelta(hours=i + 1)

        # Usando a formatação sem fuso fixo para o player gerenciar o fuso local da TV
        str_inicio = inicio_bloco.strftime("%Y%m%d%H%M%S")
        str_fim = fim_bloco.strftime("%Y%m%d%H%M%S")

        programme = ET.SubElement(tv, "programme", attrib={
            "start": str_inicio,
            "stop": str_fim,
            "channel": channel_id
        })

        # Título dinâmico mostrando o intervalo correto do bloco
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

    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(xml_bonito)

    print("Sucesso: O arquivo 'epg.xml' foi atualizado com títulos corrigidos!")

if __name__ == "__main__":
    gerar_xmltv()
