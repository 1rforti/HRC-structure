from ast import Module
import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import json
import numpy as np
import tkinter.font as tkFont
import re

current_mouse_position = None
cursor_type = "arrow"  # Cursor padrão
selected_areas = []
selection_start = None
selecting_area = False


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


def mouse_move(event):
    global current_mouse_position
    if selecting_area:
        x, y = event.x, event.y
        current_mouse_position = (x, y)
    
        
        

def mouse_press(event):
    global selecting_area, selection_start, current_mouse_position
    if selecting_area:
        x, y = event.x, event.y
        if 0 <= x < image_np.shape[1] and 0 <= y < image_np.shape[0]:
            selection_start = (x, y)
            current_mouse_position = (x, y)

def mouse_release(event):
    global selecting_area, current_mouse_position, cursor_type
    if selecting_area:
        x, y = event.x, event.y
        if 0 <= x < image_np.shape[1] and 0 <= y < image_np.shape[0]:
            selected_areas.append((selection_start, (x, y)))
            current_mouse_position = None
            update_image()
            # Defina selecting_area como False quando você soltar o botão do mouse
            selecting_area = False
            # Defina o cursor para o cursor padrão
            cursor_type = "arrow"
            root.config(cursor=cursor_type)
            # Volte o botão para o estado "Desativado"
            select_area_button.config(text="         Cortar ícone do 'Deal' \n Quando Houver : Desativado", style="Green.TButton")
            
            
current_image_width = image_np.shape[1]  # Largura da imagem original
column_width = image_np.shape[1]

# Função para atualizar a imagem com base nos controles deslizantes
# ...

def update_image():
    brightness = brightness_scale.get() / 100.0
    column_start = int(column_start_scale.get())
    

    binarization_threshold = int(binarization_scale.get() * 2.55)
    contrast = contrast_scale.get() / 100.0

    # Calcular a largura da coluna baseada na largura da imagem original e no início da última coluna
    column_width = image_np.shape[1] - column_start

    adjusted_image = cv2.convertScaleAbs(image_np, alpha=contrast)
    adjusted_image = cv2.convertScaleAbs(adjusted_image, beta=brightness * 255 - 255)
    adjusted_image = adjusted_image[:, column_start:column_start + column_width]

    for area in selected_areas:
        x1, y1 = area[0]
        x2, y2 = area[1]
        x1 -= column_start  # Ajuste a posição horizontal
        x2 -= column_start  # Ajuste a posição horizontal
        adjusted_image = draw_selection(adjusted_image, (x1, y1), (x2, y2))
        
    image_np1 = cv2.cvtColor(adjusted_image, cv2.COLOR_BGR2GRAY)

    _, binarized_image = cv2.threshold(adjusted_image, binarization_threshold, 255, cv2.THRESH_BINARY)
     # Após todas as modificações, obtenha a largura resultante da imagem
    current_image_width = adjusted_image.shape[1]

  

    display_image(binarized_image)    
   

# ...
# Função para desenhar a seleção na imagem
def draw_selection(image, start, end):
    x1, y1 = start
    x2, y2 = end
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), -1)
    return image

def toggle_selection_mode():
    global selecting_area, cursor_type
    if not selecting_area:
        selecting_area = True
        selection_start = None
        cursor_type = "plus"  # Cursor de seleção de área
        select_area_button.config(text="   Corte o Ícone do 'Deal' \n Quando Houver: Ativado", style="Red.TButton")
        root.geometry(f"{image_np.shape[1]}x800")
        
         # Ajuste o valor inicial do controle deslizante para o tamanho original da imagem
        column_start_scale.set(0)
        root.geometry(f"{image_np.shape[1]}x800")
        
        
    else:
        selecting_area = False
        cursor_type = "arrow"  # Cursor padrão
        select_area_button.config(text="      Corte o Ícone do 'Deal' \n Quando Houver: Desativado", style="Green.TButton")
        
        
    root.config(cursor=cursor_type)  # Define o cursor
    



# Função para redefinir os parâmetros
def reset_parameters():
    global column_width
    # Redefina o valor de "column_width" para 280
    column_width = 279.8837209302326
    column_start = image_np.shape[1] - column_width
     
    

    # Atualize os controles deslizantes
    brightness_scale.set(113.95348837209302)
    binarization_scale.set(67.44186046511628)
    contrast_scale.set(134.88372093023256)
    column_start_scale.set(column_start)    
    # Redefina a largura da janela para a largura da imagem
    root.geometry(f"{zoomed_image_np.shape[1]}x800")

    update_image()
    
    
# Função para redefinir os parâmetros
def clean_mask():
  
     
    selected_areas.clear()

 

    update_image()


# Função para salvar os parâmetros em um arquivo JSON
def save_parameters():
    brightness = brightness_scale.get()
    column_start = column_start_scale.get()
    binarization_threshold = binarization_scale.get()
    contrast = contrast_scale.get()
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

# Função para exibir uma imagem na interface gráfica
def display_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image = ImageTk.PhotoImage(image=image)
    label.config(image=image)
    label.image = image 
    
    
def draw_dashed_line(image, start, end, color, thickness, line_length):
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    distance = max(abs(dx), abs(dy)) + 1  # Adicionando 1 para evitar a divisão por zero
    step_x = dx / distance
    step_y = dy / distance
    x, y = x1, y1
    for _ in range(int(distance / line_length)):
        x1 = int(x)
        y1 = int(y)
        x2 = int(x + step_x * line_length)
        y2 = int(y + step_y * line_length)
        cv2.line(image, (x1, y1), (x2, y2), color, thickness)
        x += step_x * line_length * 2
        y += step_y * line_length * 2
    return image

def mouse_click(event):
    global selection_start, current_mouse_position
    if selecting_area:
        x, y = event.x, event.y
        if 0 <= x < image_np.shape[1] and 0 <= y < image_np.shape[0]:
            if selection_start is None:
                selection_start = (x, y)
            else:
                selected_areas.append((selection_start, (x, y)))
                update_image()
                selection_start = None
            current_mouse_position = (x, y)



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
                width = window_width  # Usar a largura da imagem redimensionada
                height = 800
                if x is not None and y is not None and width is not None and height is not None:
                    # Definir a posição e tamanho da janela
                    window.geometry(f"{width}x{height}+{x-400}+{y}")
            else:
                # Obter a posição centralizada da janela para o primeiro uso
                x, y = get_centered_window_position(window, width, height)  # Passar a largura e altura
                window.geometry(f"{width}x{height}+{x}+{y}")

def get_centered_window_position(window, width, height):
    # Obter a resolução do monitor principal
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcular a posição centralizada da janela
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    return x, y


# Redimensione a imagem usando o OpenCV
zoom_factor = 0.5
new_width1 = int(image_np.shape[1] * zoom_factor)
new_height1 = int(image_np.shape[0] * zoom_factor)
zoomed_image_np = cv2.resize(image_np, (new_width1, new_height1), interpolation=cv2.INTER_LINEAR)

# Defina a largura mínima da janela (a largura da imagem inicial)
min_window_width = zoomed_image_np.shape[1]


# Defina a largura da janela com base nas dimensões da imagem redimensionada
window_width = zoomed_image_np.shape[1]




# Carregar o arquivo de ícone e definir o ícone da janela
icon_path = r'favicon.ico'

# Crie uma janela e defina seu título
root = tk.Tk()
root.title("Ajuste de Imagem")
root.iconbitmap(icon_path)
# Carregue a posição da janela principal
load_window_position(root, "root_position")


# Criar um objeto de fonte com tamanho 14 e estilo normal
font = tkFont.Font(family="Arial", size=12, weight="bold")
font2 = tkFont.Font(family="Arial", size=14, weight="bold")
 
# Criar um objeto de estilo para o botão
style = ttk.Style()
style.configure("Red.TButton", font=font, foreground="red")
style.configure("Green.TButton", font=font, foreground="green")
style.configure("Gray.TButton", font=font, foreground="gray")
style.configure("Gray.Label", font=font, foreground="gray")
style.configure("Black.TButton", font=font, foreground="black")
style.configure("Blue.TButton", font=font2, foreground="blue")
style.configure("Blue.Label", font=font, foreground="blue")
style.configure("Red.Label", font=font, foreground="red")





#select_area_label = ttk.Label(root, text="Antes de Ajustar a Coluna PayOuts", style="Gray.Label")
#select_area_label.grid(column=0, row=0)

select_area_button = ttk.Button(root, text="      Corte o Ícone do 'Deal'\n Quando Houver : Desativado", command=toggle_selection_mode, style="Black.TButton")
select_area_button.grid(column=0, row=0)

select_area_label = ttk.Label(root, text=" Antes de Ajustar a Coluna PayOuts\n", style="Gray.Label")
select_area_label.grid(column=0, row=1)

select_area_label = ttk.Label(root, text=" Da esquerda para a direita \n       De cima para baixo", style="Gray.Label")
select_area_label.grid(column=0, row=2)


clean_area_button = ttk.Button(root, text="Limpar Mascara", command=clean_mask, style="Black.TButton")
clean_area_button.grid(column=0, row=3)

# Crie um botão para redefinir os parâmetros
reset_button = ttk.Button(root, text="       Melhores Parametros\n(para a maioria das imagens)", command=reset_parameters, style="Blue.TButton")
reset_button.grid(column=1, row=0)



column_start_label = ttk.Label(root, text="NAO OMITIR A PALAVA 'Result'", style="Red.Label")
column_start_label.grid(column=1, row=1)
column_start_scale = ttk.Scale(root, from_=image_np.shape[1]-1, to=0, orient="horizontal", length=300)
column_start_scale.set(0)  # Valor inicial
column_start_label = ttk.Label(root, text="Ajustar Coluna de PayOuts", style="Gray.Label")
column_start_label.grid(column=1, row=2)
column_start_scale.grid(column=1, row=3)



brightness_label = ttk.Label(root, text=" Nao precisa setar \n       salvo raras \n       excessões", style="Gray.Label")
brightness_label.grid(column=2, row=1)

# Crie controles deslizantes para ajustar os parâmetros da imagem
brightness_label = ttk.Label(root, text="Luminosidade:")
brightness_label.grid(column=2, row=2)
brightness_scale = ttk.Scale(root, from_=0, to=200, orient="horizontal")
brightness_scale.set(100)  # Valor inicial
brightness_scale.grid(column=2, row=3)



binarization_label = ttk.Label(root, text="Binarização:")
binarization_label.grid(column=2, row=4)
binarization_scale = ttk.Scale(root, from_=0, to=100, orient="horizontal")
binarization_scale.set(50)  # Valor inicial
binarization_scale.grid(column=2, row=5)


contrast_label = ttk.Label(root, text="Contraste:")
contrast_label.grid(column=2, row=6)
contrast_scale = ttk.Scale(root, from_=0, to=200, orient="horizontal")
contrast_scale.set(100)  # Valor inicial
contrast_scale.grid(column=2, row=7)



# Crie um botão para salvar os parâmetros
save_button = ttk.Button(root, text="Salvar Parâmetros", command=save_parameters, style="Blue.TButton")
save_button.grid(column=0, row=6, columnspan=2)


# Crie um rótulo para exibir a imagem
label = ttk.Label(root)
label.grid(column=0, row=8, columnspan=2)

# Ligando a função de clique do mouse
label.bind("<Button-1>", mouse_click)
label.bind("<Motion>", update_image)
label.bind("<Motion>", mouse_move)  # Adicione esta linha
label.bind("<ButtonPress-1>", mouse_press)  # Adicione esta linha
label.bind("<ButtonRelease-1>", mouse_release)  # Adicione esta linha
# Vincule o evento ao controle deslizante da coluna
column_start_scale.bind("<Motion>", lambda event: update_image())
binarization_scale.bind("<Motion>", lambda event: update_image())
contrast_scale.bind("<Motion>", lambda event: update_image())
brightness_scale.bind("<Motion>", lambda event: update_image())


display_image(zoomed_image_np)




# Carregar a posição da janela principal
load_window_position(root, "root_position")

# Inicie a interface gráfica
root.mainloop()