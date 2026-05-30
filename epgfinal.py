import requests
import gzip
from lxml import etree
import os

# Configurações
EPG_SOURCES = [
    "https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz"

]

OUTPUT_DIR = "epg"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "epg_final2.xml")
OUTPUT_FILE_GZ = os.path.join(OUTPUT_DIR, "epg_final2.xml.gz")

def fetch_content(url):
    print(f"Baixando: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        
        if url.endswith(".gz") or response.content.startswith(b'\x1f\x8b'):
            return gzip.decompress(response.content)
        return response.content
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return None

def merge_epgs():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    combined_root = etree.Element("tv")
    combined_root.set("generator-info-name", "EPG-Merger-Pro")

    added_channels = set()

    for url in EPG_SOURCES:
        content = fetch_content(url)
        if content:
            try:
                parser = etree.XMLParser(recover=True, remove_blank_text=True)
                tree = etree.fromstring(content, parser=parser)
                
                for channel in tree.xpath("//channel"):
                    channel_id = channel.get("id")
                    if channel_id not in added_channels:
                        combined_root.append(channel)
                        added_channels.add(channel_id)
                
                for programme in tree.xpath("//programme"):
                    combined_root.append(programme)
                
                print(f"Dados integrados com sucesso: {url}")
            except Exception as e:
                print(f"Erro ao processar XML de {url}: {e}")

    # --- SALVAMENTO DOS ARQUIVOS ---

    # 1. Converte a árvore para string XML em memória (formato bytes)
    print("\nGerando dados finais...")
    xml_data = etree.tostring(
        combined_root, 
        encoding="utf-8", 
        xml_declaration=True, 
        pretty_print=True
    )

    # 2. Salva o XML normal
    try:
        with open(OUTPUT_FILE, "wb") as f:
            f.write(xml_data)
        print(f"Arquivo XML salvo em: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Erro ao salvar XML: {e}")

    # 3. Salva o XML Comprimido (.gz)
    try:
        with gzip.open(OUTPUT_FILE_GZ, "wb") as f_gz:
            f_gz.write(xml_data)
        print(f"Arquivo GZ salvo em: {OUTPUT_FILE_GZ}")
    except Exception as e:
        print(f"Erro ao criar arquivo GZ: {e}")

    print(f"\nConcluído! Total de canais únicos: {len(added_channels)}")

if __name__ == "__main__":
    merge_epgs()
