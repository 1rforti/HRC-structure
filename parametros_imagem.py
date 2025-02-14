import cv2
import json
import os
import numpy as np

# Diretório onde as imagens estão localizadas
input_dir = "C:\\HRCStructureRENDER\\GGPoker\\imagens"

# Lista os arquivos na pasta
image_files = [f for f in os.listdir(input_dir) if f.endswith(".png")]

if image_files:
    # Pega o primeiro arquivo de imagem
    first_image_file = image_files[0]

    # Constrói o caminho completo para a primeira imagem
    first_image_path = os.path.join(input_dir, first_image_file)

    # Lê a imagem com o OpenCV e a chama de original_image
    original_image = cv2.imread(first_image_path)
    image_np = np.array(original_image)

    image_np = cv2.resize(image_np, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    tesseract_max_width = 1500  # Limite máximo de largura do Tesseract

    # Verifique se a largura da imagem excede o limite
    if image_np.shape[1] > tesseract_max_width:
        # Calcule o fator de escala
        scale_factor = tesseract_max_width / image_np.shape[1]

        # Redimensione a imagem
        new_width = tesseract_max_width
        new_height = int(image_np.shape[0] * scale_factor)
        image_np = cv2.resize(image_np, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

    # Defina os limites inferior e superior para a cor verde em BGR
    lower_green = np.array([35, 70, 35])  # Limite inferior em BGR (pode ajustar)
    upper_green = np.array([85, 255, 85])  # Limite superior em BGR (pode ajustar)

    # Crie uma máscara para a cor verde
    mask2 = cv2.inRange(image_np, lower_green, upper_green)

    # Substitua as áreas verdes por preto na imagem original
    image_np[mask2 > 0] = [0, 0, 0]  # Define os pixels correspondentes a verde como preto (0, 0, 0)

    if original_image is not None:
        # A imagem foi lida com sucesso
        # Agora você pode processar a imagem original ou exibi-la, conforme necessário
        pass
    else:
        print("Erro ao ler a imagem.")
else:
    print("Nenhuma imagem .png encontrada na pasta.")

# Função para salvar os parâmetros em um arquivo JSON
def save_parameters(brightness, column_start, binarization_threshold, contrast, selected_areas):
    # Calcular a largura da coluna baseada na largura da imagem original e no início da última coluna
    column_width = image_np.shape[1] - column_start

    parameters = {
        "brightness": brightness,
        "column_start": column_start,
        "column_width": column_width,
        "binarization_threshold": binarization_threshold,
        "contrast": contrast,
        "selected_areas": selected_areas  # Adicionando as áreas selecionadas
    }

    with open("parameters.json", "w") as param_file:
        json.dump(parameters, param_file)

# Função para processar a imagem e ajustar os parâmetros
def process_image():
    brightness = 100.0
    column_start = 0
    binarization_threshold = 50
    contrast = 100.0
    selected_areas = []

    # Ajuste a imagem com base nos parâmetros
    adjusted_image = cv2.convertScaleAbs(image_np, alpha=contrast / 100.0)
    adjusted_image = cv2.convertScaleAbs(adjusted_image, beta=brightness / 100.0 * 255 - 255)
    adjusted_image = adjusted_image[:, column_start:column_start + (image_np.shape[1] - column_start)]

    for area in selected_areas:
        x1, y1 = area[0]
        x2, y2 = area[1]
        x1 -= column_start  # Ajuste a posição horizontal
        x2 -= column_start  # Ajuste a posição horizontal
        adjusted_image = draw_selection(adjusted_image, (x1, y1), (x2, y2))

    image_np1 = cv2.cvtColor(adjusted_image, cv2.COLOR_BGR2GRAY)
    _, binarized_image = cv2.threshold(adjusted_image, binarization_threshold, 255, cv2.THRESH_BINARY)

    # Exibir a imagem processada
    cv2.imshow("Imagem Processada", binarized_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Salvar os parâmetros
    save_parameters(brightness, column_start, binarization_threshold, contrast, selected_areas)

# Função para desenhar a seleção na imagem
def draw_selection(image, start, end):
    x1, y1 = start
    x2, y2 = end
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), -1)
    return image

# Processar a imagem
process_image()
