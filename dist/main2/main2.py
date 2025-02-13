# -*- coding: utf-8 -*-

import os
import re
import json
import sys
import cv2
import pytesseract
from PIL import Image
import numpy as np
from tkinter import Tk, filedialog, Toplevel, Label, Button
import webbrowser

caminho =  r"C:\Program Files\Tesseract-OCR"
pytesseract.pytesseract.tesseract_cmd = caminho + r"\tesseract.exe"



# Diretório onde as imagens divididas estão localizadas
input_dir = "C:\\HRCStructureHHHHeadsUp\\GGPoker\\imagens"

# Lista para armazenar as imagens
images = []

# Percorre todas as imagens no diretório e as adiciona à lista
for filename in os.listdir(input_dir):
    if filename.endswith(".png"):
        img = cv2.imread(os.path.join(input_dir, filename))
        images.append(img)

# Define o número máximo de imagens a serem combinadas em uma única imagem
max_images_per_combined = 1

# Divide as imagens em grupos menores de acordo com o número máximo
image_groups = [images[i:i + max_images_per_combined] for i in range(0, len(images), max_images_per_combined)]

# Lista para armazenar os textos extraídos de cada grupo de imagens
group_texts = []

# Lista para armazenar os textos da 5 e 3 coluna de todas as imagens
column_5_texts = []
column_3_texts = []
column_1_texts = []


# Carregue os parâmetros do arquivo JSON
with open("C:\\HRCStructureHHHHeadsUp\\parameters.json", "r") as param_file:
    parameters = json.load(param_file)


# Recupere os valores do JSON e atribua às variáveis
brightness = float(parameters.get("brightness", 100.0))
binarization_threshold = int(parameters.get("binarization_threshold", 50))  # Removemos a escala * 2.55
contrast = float(parameters.get("contrast", 100.0))

# Agora, vamos aplicar as escalas
brightness_scale = brightness / 100.0
binarization_scale = binarization_threshold / 2.55  # Escala inversa para o binarization_threshold
contrast_scale = contrast / 100.0

# Processa cada grupo de imagens
# Processa cada grupo de imagens
# Processa cada grupo de imagens
for i, group in enumerate(image_groups):
        
    # Combina as imagens verticalmente
    combined_image = cv2.vconcat(group)

    # Salva a imagem combinada em um arquivo
    output_filename = f"imagem_combinada_{i}.png"
    cv2.imwrite(output_filename, combined_image)

    # Carrega a imagem combinada
    image = Image.open(output_filename)
  

    # Converte a imagem PIL para um array NumPy
    image_np = np.array(image)
    

    
    image_np = cv2.resize(image_np, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    
        # Defina os limites inferior e superior para a cor verde em BGR
    lower_green = np.array([35, 70, 35])  # Limite inferior em BGR (pode ajustar)
    upper_green = np.array([85, 255, 85])  # Limite superior em BGR (pode ajustar)

    # Crie uma máscara para a cor verde
    mask2 = cv2.inRange(image_np, lower_green, upper_green)

    # Substitua as áreas verdes por preto na imagem original
    image_np[mask2 > 0] = [0, 0, 0]  # Define os pixels correspondentes a verde como preto (0, 0, 0)


    tesseract_max_width = 1500  # Limite máximo de largura do Tesseract

    # Verifique se a largura da imagem excede o limite
    if image_np.shape[1] > tesseract_max_width:
        # Calcule o fator de escala
        scale_factor = tesseract_max_width / image_np.shape[1]
    
        # Redimensione a imagem
        new_width = tesseract_max_width
        new_height = int(image_np.shape[0] * scale_factor)
        image_np = cv2.resize(image_np, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

    mask = parameters.get("selected_areas", [])
    print(mask)

    # Suponha que 'image' seja a imagem que você deseja processar com o Tesseract
    for area in mask:
        # Pinte a área correspondente em branco
        x1, y1 = area[0]
        x2, y2 = area[1]
        image_np[y1:y2, x1:x2] = [0, 0, 0]  # Pinte a área de branco (255)
    
    adjusted_image = cv2.convertScaleAbs(image_np, alpha=brightness_scale)
    adjusted_image = cv2.convertScaleAbs(adjusted_image, beta=brightness_scale * 255 - 255)
    _, binarized_image = cv2.threshold(adjusted_image, binarization_scale, 255, cv2.THRESH_BINARY)
    
    adjusted_image = cv2.cvtColor(adjusted_image, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    adjusted_image = cv2.dilate(adjusted_image, kernel, iterations=3)
    adjusted_image = cv2.erode(adjusted_image, kernel, iterations=3)    
    cv2.adaptiveThreshold(cv2.bilateralFilter(adjusted_image, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
   

    # Agora, a lista processed_images contém todas as imagens processadas deste grupo

    # Continuar com o restante do processamento ou salvamento, se necessário
    
    
    
    

    caminho =  r"C:\Program Files\Tesseract-OCR"
    pytesseract.pytesseract.tesseract_cmd = caminho + r"\tesseract.exe"

    custom_config = r'--oem 3 --psm 6'
    extracted_text = pytesseract.image_to_string(adjusted_image, config=custom_config)
    
    # Adicione o texto extraído deste grupo à lista
    group_texts.append(extracted_text)

    # Carregue o JSON gerado por parametros_imagem.py
    with open("C:\\HRCStructureHHHHeadsUp\\parameters.json", "r") as param_file:
        parameters = json.load(param_file)
        column_widths = [65, 335, 150, 65, 180]  # ou outros valores padrão

        # Extraia os valores relevantes
        column_width = int(parameters["column_width"])
        column_start = int(parameters["column_start"])
        print("column_start", column_start)
        # Calcule a diferença para a coluna 5
        column5 = column_width
        column5 = max(50, min(column5, 350))

        print("column5", column5)
        # Calcule a diferença para a coluna 2
        column2 = column_start - (65+450+100)
        print("column2", column2)
        # Atualize a lista column_widths
        column_widths = [65, column2, 450, 100, column5]


        # Soma das larguras das colunas
        total_width = sum(column_widths)

        print("Soma das larguras das colunas:", total_width)



    # Lista para armazenar os textos de cada coluna
    column_texts = []

    # Dividir a imagem em colunas
    x1 = 0
    for width in column_widths:
        x2 = x1 + width
        x1 = int(x1)  # Convertendo x1 em inteiro
        x2 = int(x2)  # Convertendo x2 em inteiro
        column_image = adjusted_image[:, x1:x2]

                
        caminho =  r"C:\Program Files\Tesseract-OCR"
        pytesseract.pytesseract.tesseract_cmd = caminho + r"\tesseract.exe"

        column_text = pytesseract.image_to_string(column_image, config=custom_config)
        column_texts.append(column_text)

        x1 = x2


    # Agora, a quinta coluna estará em column_texts[-1] da imagem atual
    # Adicione-o à lista de textos da quinta coluna de todas as imagens
    column_5_texts.append(column_texts[-1])
    column_3_texts.append(column_texts[2])
    column_1_texts.append(column_texts[0])
    

# Combine todos os textos da quinta coluna de todas as imagens
column_5_text = "\n".join(column_5_texts)
column_3_text = "\n".join(column_3_texts)
column_1_text = "\n".join(column_1_texts)

# Combine todos os textos extraídos em um único texto
extracted_text = "\n".join(group_texts)
print(column_5_text)


   
# Agora, para a Coluna 5, encontre a palavra 'Result'
result_index = column_5_text.find("Result")



if result_index != -1:
    # Encontrou a palavra 'Result', pegue o texto após ela
    column_5_text = column_5_text[result_index + len("Result"):]
    column_5_text = column_5_text.replace("i", "1")
    column_5_text = column_5_text.replace("® ", "i")
    column_5_text = re.sub(r'[Ss]', '$', column_5_text)
    column_5_text = re.sub(r'[Finished]', '', column_5_text)
    column_5_text = re.sub(r'[a-zA-Z]', 'i', column_5_text)
    column_5_text = re.sub(r'[]°&!(_=§°/?><|\¢)|=-®]', 'i', column_5_text)
        
    print(column_5_text)
   
    # Dividir o texto em linhas
    lines = column_5_text.split('\n')

    # Percorrer as linhas e extrair apenas os primeiros números
    first_numbers = []

    for line in lines:
        line = line.strip()  # Remover espaços em branco no início e no fim
        if line.startswith('$') or line.startswith('i'):
            parts = line.split('+')
            if len(parts) > 0:
                first_number = parts[0].replace('$', '').replace('i', '').strip()
                first_numbers.append(first_number)

    # Imprima os primeiros números de cada linha
    for number in first_numbers:
        print(number)


###################
 # Agora, verifique se o último prêmio é diferente dos três prêmios anteriores e exclua-o, se necessário
if len(first_numbers) >= 4:
    last_prize_str = first_numbers[-1]
    if last_prize_str:
        last_prize = float(last_prize_str)
        previous_prizes = [float(num) for num in first_numbers[-4:-1]]

        if last_prize != previous_prizes[0] or last_prize != previous_prizes[1] or last_prize != previous_prizes[2]:
            # O último prêmio é diferente dos três anteriores, remova-o
            first_numbers.pop(-1)

    # Atualize a variável column_5_text com os números atualizados
    column_5_text = '\n'.join([f"${number}" for number in first_numbers])
    # Imprima os números atualizados
    print("Números atualizados na coluna 5:")
    print(column_5_text)
############################

else:
    print("Palavra 'Result' nao encontrada na Coluna 5.")

# Use expressões regulares para encontrar os valores de "total_entrants" no texto
match = re.search(r"of (\d+,\d+)", extracted_text)
if match:
    total_entrants_str = match.group(1)
    total_entrants = int(total_entrants_str.replace(",", ""))
else:
    total_entrants = None

# Divide o texto extraído em linhas
extracted_lines = extracted_text.split('\n')

# Define o número máximo de linhas a serem verificadas (por exemplo, 3)
max_lines_to_check = 3

# Inicializa as variáveis de bounty_type e progressive_factor como None
bounty_type = None
progressive_factor = None


# Defina o nome do torneio como uma variável
tournament_name = ""

## Extrair o nome do torneio da coluna 3

tournament_name_lines = column_3_text.strip().split('\n')
if tournament_name_lines:
    tournament_name = tournament_name_lines[0]

# Recupere o valor do stack inicial dos argumentos de linha de comando
stack_inicial = None
for i, arg in enumerate(sys.argv):
    if arg == "--stack" and i + 1 < len(sys.argv):
        stack_inicial = sys.argv[i + 1]

if stack_inicial is None:
    print("Erro: Informe o valor do stack inicial usando '--stack'.")
    sys.exit(1)

# Use o valor do stack inicial em seu código
print(f"Valor do stack inicial: {stack_inicial}")

# Converta o valor do stack inicial em um número inteiro
stack_inicial = int(stack_inicial)

# Use expressões regulares para encontrar os valores dos "prizes" no texto
prize_matches = re.findall(r'(\d+)\s+([^$]+)\s+\$([\d,]+\.\d{2})', column_5_text)

# Inicialize o dicionário de "prizes"
prizes_dict = {}
placement_mapping = {str(i + 1): number for i, number in enumerate(first_numbers)}

# Inicialize uma variável para controlar a ordem das colocações
current_placement = 1

# Preencha o dicionário de "prizes" com os valores encontrados
for match in prize_matches:
    position = match[0]
    prize_value_str = match[2].replace(',', '')  # Remova vírgulas
    prize_value_str = prize_value_str.replace('.', '', prize_value_str.count('.') - 1)  # Remova pontos extras
    prize_value = float(prize_value_str.replace(',', '.'))  # Substitua vírgulas por ponto decimal

    # Verifique se a posição atual corresponde à próxima colocação na ordem
    if position in placement_mapping and current_placement <= len(placement_mapping):
        current_placement_str = str(current_placement)
        current_placement += 1
        prizes_dict[current_placement_str] = prize_value
        
# Ordenar os resultados da coluna 5 em ordem decrescente
sorted_first_numbers = []

for value in first_numbers:
    # Verifique se o valor não está vazio e é um número válido antes de convertê-lo
    if value.strip() and value.replace(',', '').replace('.', '').isdigit():
        sorted_first_numbers.append(float(value.replace(',', '')))

sorted_first_numbers.sort(reverse=True)




# Crie o dicionário de prêmios usando os valores da coluna 5
prizes_dict = {placement: value for placement, value in zip(placement_mapping.keys(), sorted_first_numbers)}

# Crie o dicionário de saída
output_data = {
    "name": "/",
    "folders": [],
    "structures": [
        {
            "name": tournament_name,
            "chips": total_entrants * stack_inicial,
            "prizes": prizes_dict,
            
        }
    ]
}
for line in extracted_lines[:max_lines_to_check]:
    if "bounty" in line.lower():
        output_data['structures'][0]['bountyType'] = "PKO"
        output_data['structures'][0]['progressiveFactor'] = 0.5


gif_path = r'1.gif'
gif_path2 = r'2.gif'
gif_path3 = r'3.gif'
gif_path4 = r'4.gif'


def get_centered_window_position(window):
    # Calcule a posição x, y centralizada para a janela
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    return x, y

# Caminho para o arquivo de configuração
config_file_path = "config.json"

def load_window_position(window, config_key):
    if os.path.isfile(config_file_path):
        # Carregar a posição e tamanho do arquivo de configuração
        with open(config_file_path, "r") as file:
            data = json.load(file)
            window_position = data.get(config_key)
            if window_position:
                x = window_position.get("x")
                y = window_position.get("y")
                width = window_position.get("width")
                height = window_position.get("height")
                if x is not None and y is not None and width is not None and height is not None:
                    # Definir a posição e tamanho da janela
                    window.geometry(f"{width}x{height}+{x}+{y}")
            else:
                # Obter a posição centralizada da janela para o primeiro uso
                x, y = get_centered_window_position(window)
                window.geometry(f"{width}x{height}+{x}+{y}")

# Função para fechar a janela principal
def close_main_window():
    root.destroy()


# Inicialize a janela raiz
root = Tk()
root.withdraw()  # Oculta a janela raiz

 #Configurar um evento para fechar a janela principal
root.protocol("WM_DELETE_WINDOW", close_main_window)


# Carregar o arquivo de ícone e definir o ícone da janela
icon_path = r'favicon.ico'

# Solicite ao usuário o caminho de saída do arquivo JSON
output_file_path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=(('JSON Files', '*.json'), ('All Files', '*.*')))

if output_file_path:
    with open(output_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

    popup_window = Toplevel(root)
    popup_window.title('FEITO')
    popup_window.iconbitmap(icon_path)

    # Carregar a posição da janela do popup
    load_window_position(popup_window, "popup_window_position")

    def close_popup():
        popup_window.destroy()
        root.destroy()  # Fecha a janela principal quando a pop-up é fechada

    json_saved_label = Label(popup_window, text='JSON gerado e salvo com sucesso!', font=('Arial', 12, 'bold'))
    json_saved_label.pack()

    def open_instruction_gif():
        webbrowser.open(gif_path2)

    instruction_button = Button(popup_window, text='Instrução GIF Importar JSON HRC', command=open_instruction_gif)
    instruction_button.pack()

    json_saved_label = Label(popup_window, text='', font=('Arial', 12, 'bold'))
    json_saved_label.pack()

    json_saved_label = Label(popup_window, text='Como opção adicional', font=('Arial', 10))
    json_saved_label.pack()

    def open_instruction_gif():
        webbrowser.open(gif_path4)

    instruction_button = Button(popup_window, text='Instrução GIF Salvar Estrutura JSON HRC', command=open_instruction_gif)
    instruction_button.pack()

    # Adicione um loop para manter a janela de popup aberta
    popup_window.protocol("WM_DELETE_WINDOW", close_popup)

    # Inicie o loop principal da janela raiz
    root.mainloop()