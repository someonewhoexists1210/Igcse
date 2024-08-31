from dotenv import load_dotenv
import requests
import os, json
from flask import Flask, request, jsonify
from flask_cors import CORS

with open('subjects.json') as f:
    subjects = json.load(f)


app = Flask(__name__)
CORS(app, resources={"*": {"origins": ["http://127.0.0.1:5500", "http://localhost"]}})


load_dotenv()
CX = os.getenv('CX')
API_KEY = os.getenv('KEY')

def search_query(query):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': API_KEY,
        'cx': CX,
        'q': query,
        'fileType': 'pdf',
    }
    print(url, params)
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    res = response.json()
    if 'items' not in res:
        return None
    if len(res['items']) == 0:
        return None
    
    return res['items'][0]['link']

def codeify_ms(data):
    code = ''
    code += data['subject'] + '_'
    parts = [data['paper'], data['variant'], data['series'], data['year'][2:]]
    if parts[2] == 'M':
        code += 's' + parts[3] + '_ms_' + parts[0] + parts[1]
    elif parts[2] == 'O':
        code += 'w' + parts[3] + '_ms_' + parts[0] + parts[1] 
    elif parts[2] == 'F':
        code += 'm' + parts[3] + '_ms_' + parts[0] + parts[1]
    return code

def codeify_qp(q):
    return codeify_ms(q).replace('ms', 'qp')

@app.route('/search', methods=['POST'])
def main():
    data = request.form
    if data['type'] == 'ms':
        query = codeify_ms(data)
    elif data['type'] == 'qp':
        query = codeify_qp(data)

    link = search_query(query)
    if link is None:
        return jsonify({'error': 'Not found'})
    return jsonify({'link': link})

@app.route('/subjects', methods=['GET'])
def get_subjects():
    return jsonify(subjects)


HOST = '127.0.0.1'
PORT = 5000
if __name__ == '__main__':
    app.run(debug=True)