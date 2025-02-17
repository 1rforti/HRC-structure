# -*- coding: utf-8 -*-

import cv2
import pytesseract
from PIL import Image
import os
import numpy as np
import re
import json
import sys
from flask import Flask, request, jsonify, send_file, render_template

app = Flask(__name__)  # Definição da instância do Flask

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_json', methods=['POST'])
def generate_json():
    xml_file = request.files.get('xml_file')
    stack_inicial = request.form.get('stack_inicial')

    if not stack_inicial:
        return jsonify({"error": "Por favor, informe o stack inicial."}), 400

    if not xml_file:
        return jsonify({"error": "Por favor, selecione um arquivo XML."}), 400

    data_dict = read_xml(xml_file)
    tournament_info = data_dict['CompletedTournament']
    tournament_name = tournament_info['@name']
    total_entrants = int(tournament_info['@totalEntrants']) + int(tournament_info['@reEntries'])
    flags = tournament_info['@flags']

    chips = total_entrants * int(stack_inicial)

    output_data = {
        "name": "/",
        "folders": [],
        "structures": [
            {
                "name": tournament_name,
                "chips": chips,
                "prizes": {}
            }
        ]
    }

    if 'B' in flags:
        output_data['structures'][0]['bountyType'] = "PKO"
        output_data['structures'][0]['progressiveFactor'] = 0.5

    tournament_entries = data_dict['CompletedTournament'].get('TournamentEntry', [])
    prize_dict = {}

    for entry in tournament_entries:
        position = entry['@position']
        prize = float(entry.get('@prize', 0))
        prize_bounty_component = float(entry.get('@prizeBountyComponent', 0))
        calculated_prize = prize - prize_bounty_component
        calculated_prize = round(calculated_prize, 2)

        if calculated_prize > 0:
            prize_dict[position] = calculated_prize

    output_data['structures'][0]['prizes'] = prize_dict

    output_file_path = os.path.join("output", "output.json")
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, 'w') as file:
        json.dump(output_data, file, indent=2)

    return send_file(output_file_path, as_attachment=True, download_name='output.json')

@app.route('/process_images', methods=['GET'])
def process_images_form():
    return render_template('process_images.html')

@app.route('/process_images', methods=['POST'])
def process_images():
    # Diretório temporário para armazenar as imagens enviadas
    input_dir = "temp_images"
    os.makedirs(input_dir, exist_ok=True)

    # Salva as imagens enviadas no diretório temporário
    images = []
    for file in request.files.getlist('images'):
        filename = os.path.join(input_dir, file.filename)
        file.save(filename)
        img = cv2.imread(filename)
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
    with open("parameters.json", "r") as param_file:
        parameters = json.load(param_file)

    # Recupere os valores do JSON e atribua às variáveis
    brightness = float(parameters.get("brightness", 100.0))
    binarization_threshold = int(parameters.get("binarization_threshold", 50))
    contrast = float(parameters.get("contrast", 100.0))

    # Agora, vamos aplicar as escalas
    brightness_scale = brightness / 100.0
    binarization_scale = binarization_threshold / 2.55
    contrast_scale = contrast / 100.0

    # Processa cada grupo de imagens
    for i, group in enumerate(image_groups):
        # Combina as imagens verticalmente
        combined_image = cv2.vconcat(group)

        # Salva a imagem combinada em um arquivo
        output_filename = os.path.join(input_dir, f"imagem_combinada_{i}.png")
        cv2.imwrite(output_filename, combined_image)

        # Carrega a imagem combinada
        image = Image.open(output_filename)

        # Converte a imagem PIL para um array NumPy
        image_np = np.array(image)

        image_np = cv2.resize(image_np, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

        # Defina os limites inferior e superior para a cor verde em BGR
        lower_green = np.array([35, 70, 35])
        upper_green = np.array([85, 255, 85])

        # Crie uma máscara para a cor verde
        mask2 = cv2.inRange(image_np, lower_green, upper_green)

        # Substitua as áreas verdes por preto na imagem original
        image_np[mask2 > 0] = [0, 0, 0]

        tesseract_max_width = 1500

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
            image_np[y1:y2, x1:x2] = [0, 0, 0]

        adjusted_image = cv2.convertScaleAbs(image_np, alpha=brightness_scale)
        adjusted_image = cv2.convertScaleAbs(adjusted_image, beta=brightness_scale * 255 - 255)
        _, binarized_image = cv2.threshold(adjusted_image, binarization_scale, 255, cv2.THRESH_BINARY)

        adjusted_image = cv2.cvtColor(adjusted_image, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((1, 1), np.uint8)
        adjusted_image = cv2.dilate(adjusted_image, kernel, iterations=3)
        adjusted_image = cv2.erode(adjusted_image, kernel, iterations=3)
        cv2.adaptiveThreshold(cv2.bilateralFilter(adjusted_image, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

        # Execute o Tesseract com configurações específicas para tabelas
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(adjusted_image, config=custom_config)

        # Adicione o texto extraído deste grupo à lista
        group_texts.append(extracted_text)

        # Carregue o JSON gerado por parametros_imagem.py
        with open("parameters.json", "r") as param_file:
            parameters = json.load(param_file)
            column_widths = [65, 335, 150, 65, 180]

            # Extraia os valores relevantes
            column_width = int(parameters["column_width"])
            column_start = int(parameters["column_start"])
            print("column_start", column_start)
            # Calcule a diferença para a coluna 5
            column5 = column_width
            column5 = max(50, min(column5, 350))

            print("column5", column5)
            # Calcule a diferença para a coluna 2
            column2 = column_start - (65 + 450 + 100)
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
            x1 = int(x1)
            x2 = int(x2)
            column_image = adjusted_image[:, x1:x2]

            # Execute o Tesseract em cada coluna
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
            line = line.strip()
            if line.startswith('$') or line.startswith('i'):
                parts = line.split('+')
                if len(parts) > 0:
                    first_number = parts[0].replace('$', '').replace('i', '').strip()
                    first_numbers.append(first_number)

        # Imprima os primeiros números de cada linha
        for number in first_numbers:
            print(number)

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

    # Extrair o nome do torneio da coluna 3
    tournament_name_lines = column_3_text.strip().split('\n')
    if tournament_name_lines:
        tournament_name = tournament_name_lines[0]

    # Recupere o valor do stack inicial do formulário
    stack_inicial = request.form.get('stack_inicial_images')
    if stack_inicial is None:
        return jsonify({"error": "Por favor, informe o valor do stack inicial."}), 400

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
        prize_value_str = match[2].replace(',', '')
        prize_value_str = prize_value_str.replace('.', '', prize_value_str.count('.') - 1)
        prize_value = float(prize_value_str.replace(',', '.'))

        # Verifique se a posição atual corresponde à próxima colocação na ordem
        if position in placement_mapping and current_placement <= len(placement_mapping):
            current_placement_str = str(current_placement)
            current_placement += 1
            prizes_dict[current_placement_str] = prize_value

    # Ordenar os resultados da coluna 5 em ordem decrescente
    sorted_first_numbers = []

    for value in first_numbers:
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

    # Solicite ao usuário o caminho de saída do arquivo JSON
    output_file_path = "output.json"

    if output_file_path:
        with open(output_file_path, 'w') as json_file:
            json.dump(output_data, json_file, indent=4)

        print('JSON gerado e salvo com sucesso!')

    return send_file(output_file_path, as_attachment=True, download_name='output.json')

def read_xml(xml_file):
    data_dict = xmltodict.parse(xml_file.read())
    return data_dict

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port)
