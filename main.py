
import sys
import io
import os
import json
import xmltodict
import webbrowser
import zipfile
import requests
import certifi
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import tkinter as tk
from tkinter import PhotoImage
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import shutil
import subprocess
import psutil
import threading
from screeninfo import get_monitors
import queue
from queue import Queue, Empty
import time




# Declare uma fila global para armazenar as imagens do GIF
gif_frames = []
atualizar_frame_id = None  # Variável global para armazenar o ID da chamada periódica
atualizacao_disponivel = False
# Declare um evento global para sinalizar quando o usuário tomou uma decisão
usuario_decidiu_evento = threading.Event()





def exibir_prints(prints_queue):
    while True:
        text = prints_queue.get()  # Bloqueia até que uma mensagem esteja disponível
        prints_label.config(text=text)
        janela.update_idletasks()

def atualizar_frame(frame):
    global atualizar_frame_id  # Remova a linha 'global' se ela ainda estiver presente no início da função
    if not encerrar_threads and gif_frames:
        frame_imagem = gif_frames[frame]
        gif_label.configure(image=frame_imagem)
        gif_label.image = frame_imagem
        atualizar_frame_id = janela.after(100, atualizar_frame, (frame + 2) % len(gif_frames))

def fechar_janela():
    global encerrar_threads, atualizar_frame_id
    encerrar_threads = True
    if atualizar_frame_id is not None:
        janela.after_cancel(atualizar_frame_id)  # Cancela a chamada periódica do atualizar_frame
    janela.quit()
    janela.update()
    janela.destroy()
    


def realizar_atualizacao(prints_queue):
    prints_queue.put("Verificando atualizações... ")
    url = "https://api.github.com/repos/1rforti/HRC-structure/commits/master"
    response = requests.get(url)

    if response.status_code == 200:
        commit_info = json.loads(response.text or response.content)
        latest_commit_sha = commit_info["sha"]

        current_commit_sha = ""
        if os.path.exists("C:\\HRCStructureHHHHeadsUp\\commit_sha.txt"):
            with open("C:\\HRCStructureHHHHeadsUp\\commit_sha.txt", "r") as file:
                current_commit_sha = file.read().strip()

        if latest_commit_sha != current_commit_sha:
            prints_queue.put("Comparando atualizações")
            url_updater = "https://github.com/1rforti/HRC-structure/blob/master/main.exe"
            response_updater = requests.get(url_updater)

            if response_updater.status_code == 200:
                with open("C:\\HRCStructureHHHHeadsUp\\main2.exe", "wb") as file:
                    file.write(response_updater.content)

                # Salvar o SHA do commit mais recente para o próximo teste de atualização
                with open("C:\\HRCStructureHHHHeadsUp\\commit_sha.txt", "w") as file:
                    file.write(latest_commit_sha)

                # Mostrar a janela pop-up de confirmação
                prints_queue.put("Nova Versão Disponível...")
                janela.after(0, show_confirmation_popup_async)

                # Aguardar até que o usuário tome uma decisão
                usuario_decidiu_evento.wait()

                if usuario_decidiu_evento.is_set():
                    # Usuário escolheu "Sim"
                    import UpdaterHrcStructure

                    prints_queue.put("Aguarde, atualização em andamento...")

                    # Chame UpdaterHrcStructure.main passando a fila de prints
                    UpdaterHrcStructure.main(prints_queue)
                                                


                else:
                    # Usuário escolheu "Não"
                    prints_queue.put("Continuando a execução do programa...")

            else:
                prints_queue.put("Erro ao baixar o Updater.")
        else:
            prints_queue.put("Nenhuma atualização disponível.")
            time.sleep(3)
            prints_queue.put("Seu software será iniciado em breve.")
    else:
        prints_queue.put("Erro ao verificar atualizações.")
        

def agendar_fechamento():
    global atualizacao_disponivel, prints_queue

    # Verifica se há uma atualização disponível
    if atualizacao_disponivel:
        # Aguarda a decisão do usuário antes de fechar a janela
        prints_queue.put("Aguardando decisão do usuário...")
        user_input = show_confirmation_popup()
        if user_input.lower() == "yes":
            # Se o usuário deseja encerrar o programa, chame a função para encerrar
            close_main_program()
        else:
            # Continue com a execução normal do programa
            prints_queue.put("Continuando a execução do programa...")
            # Agende o fechamento da janela após 20 segundos
            janela.after_idle(agendar_fechamento)
            

    else:
        # Se não houver atualização, agende o fechamento da janela após 20 segundos
        janela.after(10000, fechar_janela)
        
def janela_com_gif_e_prints():
    global janela, gif_label, prints_label, encerrar_threads, gif_frames
    

    janela = tk.Tk()
    janela.title("GIF com Prints")
    janela.overrideredirect(True)

    gif_image = Image.open("HRCStructure.gif")
    gif_frames = [ImageTk.PhotoImage(frame) for frame in ImageSequence.Iterator(gif_image)]

    gif_label = tk.Label(janela, image=gif_frames[0])
    gif_label.pack()

    largura_gif, altura_gif = gif_image.size

    tela_principal = janela.winfo_screenwidth(), janela.winfo_screenheight()
    x = (tela_principal[0] - largura_gif) // 2
    y = (tela_principal[1] - altura_gif) // 2
    janela.geometry(f"{largura_gif}x{altura_gif}+{x}+{y}")

    prints_label = tk.Label(janela, bg="black", fg="white", justify="left")
    prints_label.place(relx=0.5, rely=0.05, anchor=tk.N)
    fonte_personalizada = ("Arial", 11)
    prints_label["font"] = fonte_personalizada

    encerrar_threads = False


    frame_thread = threading.Thread(target=atualizar_frame, args=(0,))
    frame_thread.start()


    prints_queue = queue.Queue()
    prints_thread = threading.Thread(target=exibir_prints, args=(prints_queue,))
    prints_thread.start()

    # Inicie o processo de instalação em uma thread separada
    install_thread = threading.Thread(target=realizar_atualizacao, args=(prints_queue,))
    install_thread.start()

    # Agende o fechamento da janela após 20 segundos
    janela.after(10000, agendar_fechamento)

    janela.mainloop()




def close_main_program():
    try:
        os.kill(os.getpid(), 9)  # Encerre o processo principal de forma mais agressiva
   
    except OSError:
        pass
    
def show_confirmation_popup_async():
    user_input = show_confirmation_popup()
    # Sinalizar o evento com base na decisão do usuário
    if user_input.lower() == "yes":
        usuario_decidiu_evento.set()
    else:
        usuario_decidiu_evento.clear()


    # Força a atualização da interface gráfica
    janela.update_idletasks()
    # Aguarda um curto período para garantir que a interface gráfica tenha tempo de responder
    janela.after(100)

def show_confirmation_popup():
    # Crie uma janela pop-up de confirmação
    root = tk.Tk()
    root.withdraw()  # Esconda a janela principal
    user_input = messagebox.askquestion("Confirmação", "Deseja encerrar o programa e realizar a instalação/atualização?")
    return user_input

if __name__ == "__main__":
    janela_com_gif_e_prints()
    

def load_translations(lang):
    # Verifique se o idioma solicitado é inglês
    if lang == 'en':
        # Carregue as traduções em inglês do arquivo translations_en.json
        with open('translations_en.json', 'r') as file:
            translations = json.load(file)
        return translations

    # Se o idioma solicitado não for suportado, retorne as traduções padrão
    return default_translations  # substitua default_translations pelas traduções padrão do seu aplicativo


# Caminho para o arquivo de configuração
config_file_path = "config.json"

def save_window_position(window, config_key):
    # Obter a posição e tamanho atual da janela
    x = window.winfo_x()
    y = window.winfo_y()
    width = window.winfo_width()
    height = window.winfo_height()

    # Salvar a posição e tamanho no arquivo de configuração
    data = {}
    if os.path.isfile(config_file_path):
        with open(config_file_path, "r") as file:
            data = json.load(file)
    data[config_key] = {"x": x, "y": y, "width": width, "height": height}
    with open(config_file_path, "w") as file:
        json.dump(data, file)

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

def get_centered_window_position(window):
    # Obter a resolução do monitor principal
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcular a posição centralizada da janela
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    return x, y


def open_link_livepix():
    webbrowser.open('https://livepix.gg/hhhheadsup')

def open_link_twitch():
    webbrowser.open('https://twitch.tv/hhhheadsup')

def open_link(event):
    webbrowser.open('https://pt.sharkscope.com/#Find-Tournament')
    
def open_link_YT(event):
    webbrowser.open('https://youtu.be/OKlsuLPB4gs')

def read_xml(xml_file_path):
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        data_dict = xmltodict.parse(file.read())
    return data_dict

gif_path = r'1.gif'
gif_path2 = r'2.gif'
gif_path3 = r'3.gif'
gif_path4 = r'4.gif'



def save_json_and_show_popup(output_file_path, output_data):
    popup_window = Toplevel(root)
    popup_window.title('FEITO')
    popup_window.iconbitmap(icon_path)

    # Carregar a posição da janela do popup
    load_window_position(popup_window, "popup_window_position")

    def close_popup():
        # Salvar a posição da janela do popup
        save_window_position(popup_window, "popup_window_position")
        popup_window.destroy()

    if output_file_path:
        with open(output_file_path, 'w') as file:
            json.dump(output_data, file, indent=2)

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

        popup_window.protocol("WM_DELETE_WINDOW", close_popup)

    else:
        messagebox.showerror('Erro', 'Arquivo de saída não selecionado.')

def browse_xml():
    xml_file_path = filedialog.askopenfilename(filetypes=(('XML Files', '*.xml'), ('All Files', '*.*')))
    if xml_file_path:
        xml_entry.delete(0, END)
        xml_entry.insert(END, xml_file_path)

def generate_json():
    xml_file_path = xml_entry.get()
    imagens_directory = imagens_entry.get()
    stack_inicial = stack_entry.get()

    if not stack_inicial:
        messagebox.showerror('Erro', 'Por favor, informe o stack inicial.')
        return
    
    if xml_file_path and not imagens_directory:
        data_dict = read_xml(xml_file_path)
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

        output_file_path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=(('JSON Files', '*.json'), ('All Files', '*.*')))

        if output_file_path:
            save_json_and_show_popup(output_file_path, output_data)

    elif imagens_directory and not xml_file_path:
         print(f"Chamando run_main2_with_gif com stack_inicial: {stack_inicial}") 
         # Inicie o subprocesso sem exibir a janela de console
         process = subprocess.Popen(["C:\\HRCStructureHHHHeadsUp\\parametros_imagem.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
         # Aguarde a conclusão do processo
         process.wait()
         run_main2_with_gif(stack_inicial)
    elif not xml_file_path and not imagens_directory:
        # Ambos estão vazios, exiba uma mensagem de erro
        messagebox.showerror('Erro', 'Por favor, selecione um arquivo XML ou um diretório de imagens.')
    else:
        # Ambos estão preenchidos, exiba uma mensagem de erro
        messagebox.showerror('Erro', 'Por favor, selecione apenas um arquivo XML ou um diretório de imagens, não ambos.')


    

def on_closing():
    save_window_position(root, "root_position")
    final_window = Toplevel()
    final_window.title('HHHHeadsUp')
    final_window.iconbitmap(icon_path)

    # Carregar a posição da janela final
    load_window_position(final_window, "final_window_position")

    def close_final_window():
        save_window_position(final_window, "final_window_position")
        final_window.destroy()
        root.destroy()

        # Encerre os processos relacionados ao main.exe
        main_exe_name = "main.exe"
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if main_exe_name.lower() in proc.info['name'].lower():
                    process = psutil.Process(proc.info['pid'])
                    process.terminate()
                    print(f"Processo com PID {proc.info['pid']} relacionado ao {main_exe_name} encerrado com sucesso.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    segue_label = Label(final_window, text='SEGUE LÁ!', font=('Arial', 12))
    segue_label.configure(font=('Arial', 12, 'bold'), fg='red')
    segue_label.pack()

    twitch_button = Button(final_window, text='twitch.tv/hhhheadsup', command=open_link_twitch)
    twitch_button.configure(font=('Arial', 11), fg='blue')
    twitch_button.pack()

    similar_label = Label(final_window, text='Programas similares cobram U$20/ano para 5 estruturas/dia', font=('Arial', 12))
    similar_label.pack()

    gera_label = Label(final_window, text='Aqui você gera quantas quiser o tempo todo!!!', font=('Arial', 12))
    gera_label.pack()

    paga_label = Label(final_window, text='E aqui só paga se puder, ou quiser...', font=('Arial', 12))
    paga_label.pack()

    capilha_button = Button(final_window, text='ENTAO CAPRICHA NO CAPILÉ! GLGLGL!!!', command=open_link_livepix)
    capilha_button.configure(font=('Arial', 10, 'bold'), fg='blue')
    capilha_button.pack()

    # Salvar a posição da janela final
    save_window_position(final_window, "final_window_position")

    final_window.protocol("WM_DELETE_WINDOW", close_final_window)



# Função para selecionar e copiar imagens
def browse_images():
    # Abra a janela de seleção de arquivo e permita que o usuário selecione várias imagens
    file_paths = filedialog.askopenfilenames(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")])

    # Diretório de destino onde as imagens serão copiadas
    destination_directory = "C:\\HRCStructureHHHHeadsUp\\GGPoker\\imagens"

    # Limpe o diretório de destino antes de copiar as imagens
    for file_name in os.listdir(destination_directory):
        file_path = os.path.join(destination_directory, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Copie as imagens selecionadas para o diretório de destino
    for source_path in file_paths:
        file_name = os.path.basename(source_path)
        destination_path = os.path.join(destination_directory, file_name)
        shutil.copy2(source_path, destination_path)

    # Atualize o campo de entrada com o diretório de destino
    imagens_entry.delete(0, END)  # Limpe o campo de entrada

    # Insira os nomes das imagens selecionadas no campo de entrada
    imagens_entry.insert(0, ", ".join(os.path.basename(file) for file in file_paths))


# Função para executar parametros_imagem.py
#def run_parametros_imagem():
    #try:
        #subprocess.run(["python", "parametros_imagem.py"])
    #except Exception as e:
        #print(f"Erro ao executar parametros_imagem.py: {str(e)}")
        

root = Tk()
root.title('HRCStructure - HHHHeadsUp')

# Carregar o arquivo de ícone e definir o ícone da janela
icon_path = 'C:\\HRCStructureHHHHeadsUp\\favicon.ico'
icon = Image.open(icon_path)
root.iconbitmap(icon_path)

root.protocol("WM_DELETE_WINDOW", on_closing)


instruction_button = Button(root, text='Instrução GIF Exportar XML SharkScope', command=lambda: webbrowser.open(gif_path))
instruction_button.pack(side='top', anchor='center')

xml_frame = Frame(root)
xml_frame.pack(side='top', anchor='center')

xml_label = Label(xml_frame, text='XML do torneio gerado pelo SharkScope:', font=('Arial', 12), bg='lightblue', fg='black', cursor='hand2')
xml_label.pack()

xml_entry = Entry(xml_frame, width=60)
xml_entry.pack()

browse_xml_button = Button(xml_frame, text='Procurar XML', font=('Arial', 10, 'bold'), command=browse_xml, width=30)
browse_xml_button.pack(side='top', anchor='center')
xml_label.bind('<Button-1>', open_link)


#GG
# Crie um frame para conter os elementos
frame = Frame(root)
frame.pack(padx=20, pady=20)

# Crie um rótulo e um campo de entrada para exibir e inserir o diretório selecionado
imagem_label = Label(frame, text='Estrutura em Imagens GGPOKER (PokerCraft):', font=('Arial', 12), bg='lightblue', fg='black' , cursor='hand2')
imagem_label.pack()

imagens_entry = Entry(frame, width=60)
imagens_entry.pack()

# Crie um botão que executa a função run_parametros_imagem quando clicado
#parametros_imagem_button = Button(root, text='Ajustar Parâmetros de Imagem', font=('Arial', 10, 'bold'), width=30, command=run_parametros_imagem, bg='lightblue', fg='black')
#parametros_imagem_button.pack(side='top', anchor='center')

# Crie um botão para abrir a janela de seleção de diretório
browse_imagens_button = Button(frame, text='Procurar IMAGENS', font=('Arial', 10, 'bold'), command=browse_images, width=30)
browse_imagens_button.pack(side='top', anchor='center')
imagem_label.bind('<Button-1>', open_link_YT)

#GG

stack_frame = Frame(root)
stack_frame.pack(side='top', anchor='center')

espacamento_label = Label(stack_frame, text='', font=('Arial', 9))
espacamento_label.pack()

stack_label = Label(stack_frame, text='Informe o stack inicial:', font=('Arial', 9, 'bold'))
stack_label.pack(side='top')

stack_entry = Entry(stack_frame, width=20)
stack_entry.pack(side='left')

generate_button = Button(stack_frame, text='Gerar JSON', font=('Arial', 10, 'bold'), command=generate_json, width=15)
generate_button.pack(side='left')

instruction_button = Button(root, text='Instrução GIF GerarJSON', command=lambda: webbrowser.open(gif_path3))
instruction_button.pack(side='top', anchor='center')

capile_label = Label(root, text='CURTIU!? MANDA UM CAPILÉ!', font=('Arial', 12, 'bold'), fg='blue', cursor='hand2')
capile_label.pack(side='top', anchor='center')
capile_label.bind('<Button-1>', lambda event: open_link_livepix())






def run_main2_with_gif(stack_inicial):
    def start_process():
        # Inicie o subprocesso sem exibir a janela de console
        # Substitua "Phyton" por "python"
        process = subprocess.Popen(["C:\\HRCStreuctureBackup\\dist\\main2\\main2.exe", "--stack", stack_inicial], creationflags=subprocess.CREATE_NO_WINDOW)
        # Aguarde a conclusão do processo
        process.wait()
        # Quando o processo terminar, marque a variável como True
        process_finished[0] = True

    # Declare uma variável para rastrear o status do processo
    process_finished = [False]

    # Crie uma janela para exibir o GIF
    gif_window = tk.Toplevel()
    gif_window.title("GIF Window")
    gif_window.overrideredirect(True)
    
   # Carregue a posição da janela principal
    load_window_position(root, "root_position")

    # Defina a posição da janela secundária com base na posição da janela principal
    x, y = root.winfo_x(), root.winfo_y()
    gif_window.geometry(f"+{x}+{y}")

    

    # Carregue o GIF com Pillow e converta em uma lista de frames
    gif_image = Image.open("HRCStructure_json.gif")
    frames = [ImageTk.PhotoImage(frame) for frame in ImageSequence.Iterator(gif_image)]

    # Exiba o GIF em um widget Label
    gif_label = tk.Label(gif_window, image=frames[0])
    gif_label.image = frames[0]  # Garante que a imagem não seja coletada pelo garbage collector
    gif_label.pack()

    # Inicie o processo em segundo plano em uma thread separada
    process_thread = threading.Thread(target=start_process)
    process_thread.start()

    # Função para atualizar o frame do GIF
    def atualizar_frame(frame):
        if not process_finished[0]:
            frame_imagem = frames[frame]
            gif_label.configure(image=frame_imagem)
            gif_label.image = frame_imagem
            gif_window.after(100, atualizar_frame, (frame + 2) % len(frames))
        else:
            # Quando o processo terminar, feche a janela do GIF
            gif_window.destroy()

    # Inicie a atualização do frame do GIF
    atualizar_frame(0)



# Carregar a posição da janela principal
load_window_position(root, "root_position")

root.mainloop()




