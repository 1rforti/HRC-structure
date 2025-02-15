from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import xmltodict

app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gifs')
def gifs():
    return render_template('gifs.html')

@app.route('/gifs2')
def gifs2():
    return render_template('gifs2.html')

@app.route('/gifs3')
def gifs3():
    return render_template('gifs3.html')


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

def read_xml(xml_file):
    data_dict = xmltodict.parse(xml_file.read())
    return data_dict

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
