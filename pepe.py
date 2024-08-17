import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def get_character_info(character_name):
    base_url = 'https://arknights.wiki.gg'
    url = f'{base_url}/wiki/{character_name}'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trova l'immagine del personaggio
        img_tag = soup.find('img', {'class': 'pi-image-thumbnail'})
        img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
        
        # Converti l'URL relativo in un URL assoluto
        if img_url and img_url.startswith('/'):
            img_url = base_url + img_url
        
        # Trova altre informazioni del personaggio (esempio: nome, classe, rarità)
        name_tag = soup.find('h1', {'id': 'firstHeading'})
        name = name_tag.text.strip() if name_tag else 'Unknown'
        
        class_tag = soup.find('div', {'data-source': 'class'})
        char_class = class_tag.find('div', {'class': 'pi-data-value'}).text.strip() if class_tag else 'Unknown'
        
        rarity_tag = soup.find('div', {'data-source': 'rarity'})
        rarity = rarity_tag.find('div', {'class': 'pi-data-value'}).text.strip() if rarity_tag else 'Unknown'
        
        # Trova la tabella delle informazioni del personaggio
        info_table = soup.find('table', {'class': 'mrfz-btable'})
        info_text = ''
        if info_table:
            rows = info_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                for col in cols:
                    info_text += col.get_text(separator=' ').strip() + '\n'
        
        return {
            'name': name,
            'class': char_class,
            'rarity': rarity,
            'img_url': img_url,
            'info_text': info_text.strip()
        }
    else:
        return None

def create_character_image(character_info):
    # Scarica l'immagine del personaggio
    response = requests.get(character_info['img_url'])
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    
    # Dimensioni dell'immagine finale
    final_width = 1400
    final_height = 1200  # Aumenta l'altezza dell'immagine finale
    
    # Crea una nuova immagine con sfondo nero
    new_img = Image.new('RGBA', (final_width, final_height), 'black')
    
    # Ridimensiona l'immagine del personaggio
    img = img.resize((600, 600), Image.BILINEAR)
    
    # Incolla l'immagine del personaggio sulla sinistra
    new_img.paste(img, (50, 50), img)
    
    # Aggiungi un bordo attorno all'immagine del personaggio
    draw = ImageDraw.Draw(new_img)
    draw.rectangle([50, 50, 650, 650], outline='white', width=2)
    
    # Aggiungi testo con le informazioni del personaggio
    font = ImageFont.truetype("arial.ttf", 30)
    text = f"Name:\n{character_info['name']}\nClass:\n{character_info['class']}\nRarity:\n{character_info['rarity']}\n\n{character_info['info_text']}"
    
    # Wrapping del testo
    text_x = 700
    text_y = 50
    text_box_width = final_width - text_x - 50
    
    # Calcola l'altezza del testo
    lines = text.split('\n')
    line_height = font.getbbox('A')[3] - font.getbbox('A')[1]
    text_box_height = 600  # Imposta l'altezza del box di testo a 600 pixel
    
    # Calcola la posizione verticale per centrare il testo
    total_text_height = line_height * len(lines)
    vertical_padding = (text_box_height - total_text_height) // 2
    
    # Disegna il box per il testo
    draw.rectangle([text_x - 10, text_y - 10, text_x + text_box_width + 10, text_y + text_box_height + 10], outline='white', width=2)
    
    # Disegna il testo riga per riga, centrato verticalmente
    for i, line in enumerate(lines):
        draw.text((text_x, text_y + vertical_padding + i * line_height), line, fill='white', font=font)
    
    # Salva l'immagine
    new_img = new_img.convert("RGB")  # Converti in RGB prima di salvare
    new_img.save(f"{character_info['name']}.png")

# Esempio di utilizzo
character_name = 'Pepe'
character_info = get_character_info(character_name)

if character_info:
    create_character_image(character_info)
    print(f"Immagine del personaggio {character_info['name']} creata con successo.")
else:
    print("Impossibile ottenere le informazioni del personaggio.")