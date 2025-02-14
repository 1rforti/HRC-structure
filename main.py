from flask import Flask, render_template, request, jsonify
import os
import json
import xmltodict
import threading
import queue
import subprocess

app = Flask(__name__)

# Declare uma fila global para armazenar as mensagens
prints_queue = queue.Queue()
atualizacao_disponivel = False
usuario_decidiu_evento = threading.Event()

def exibir_prints():
    while True:
        text = prints_queue.get()  # Bloqueia até que uma mensagem esteja disponível
        # Aqui você pode adicionar lógica para exibir as mensagens na interface web
        print(text)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    try:
        message = prints_queue.get_nowait()
    except queue.Empty:
        message = ""
    return jsonify({"message": message})

@app.route('/generate_json', methods=['POST'])
def generate_json():
    xml_file_path = request.form.get('xml_file_path')
    imagens_directory = request.form.get('imagens_directory')
    stack_inicial = request.form.get('stack_inicial')

    if not stack_inicial:
        return jsonify({"error": "Por favor, informe o stack inicial."}), 400

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

        output_file_path = os.path.join("output", "output.json")
        with open(output_file_path, 'w') as file:
            json.dump(output_data, file, indent=2)

        return jsonify({"status": "JSON gerado e salvo com sucesso!", "output_file_path": output_file_path})

    elif imagens_directory and not xml_file_path:
        print(f"Chamando run_main2_with_gif com stack_inicial: {stack_inicial}")
        process = subprocess.Popen(["python", "C:\\HRCStructureRENDER\\parametros_imagem.py"], creationflags=subprocess.CREATE_NO_WINDOW)
        process.wait()
        run_main2_with_gif(stack_inicial)
        return jsonify({"status": "Processo de gera\u00e7\u00e3o de JSON iniciado com imagens."})

    elif not xml_file_path and not imagens_directory:
        return jsonify({"error": "Por favor, selecione um arquivo XML ou um diret\u00f3rio de imagens."}), 400

    else:
        return jsonify({"error": "Por favor, selecione apenas um arquivo XML ou um diret\u00f3rio de imagens, não ambos."}), 400

def read_xml(xml_file_path):
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        data_dict = xmltodict.parse(file.read())
    return data_dict

def run_main2_with_gif(stack_inicial):
    def start_process():
        process = subprocess.Popen(["python", "C:\\HRCStructureRENDER\\main2.py", "--stack", stack_inicial], creationflags=subprocess.CREATE_NO_WINDOW)
        process.wait()
        process_finished[0] = True

    process_finished = [False]

    def atualizar_frame(frame):
        if not process_finished[0]:
            gif_window.after(100, atualizar_frame, (frame + 2) % len(frames))
        else:
            gif_window.destroy()

    gif_window = tk.Toplevel()
    gif_window.title("GIF Window")
    gif_window.overrideredirect(True)
    x, y = root.winfo_x(), root.winfo_y()
    gif_window.geometry(f"+{x}+{y}")

    gif_image = Image.open("HRCStructure_json.gif")
    frames = [ImageTk.PhotoImage(frame) for frame in ImageSequence.Iterator(gif_image)]

    gif_label = tk.Label(gif_window, image=frames[0])
    gif_label.image = frames[0]
    gif_label.pack()

    process_thread = threading.Thread(target=start_process)
    process_thread.start()

    atualizar_frame(0)

if __name__ == "__main__":
    threading.Thread(target=exibir_prints).start()
    app.run(host='0.0.0.0', port=5000)


