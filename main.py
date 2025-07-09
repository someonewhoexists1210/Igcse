from dotenv import load_dotenv
import requests
import os, json
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import logging, io
from datetime import datetime
from paper import get_paper_pdf

logging.basicConfig(filename='app.log', level=logging.DEBUG)
app = Flask(__name__)
CORS(app, resources={"*": {"origins": ["http://igcse.someonewhoexists.hackclub.app", "http://127.0.0.1"]}})

cached_links = {}
CACHE_TIMEOUT = 60 * 60 * 24 * 30
last_updated = int(datetime.now().timestamp())

load_dotenv()
CX = os.getenv('CX')
API_KEY = os.getenv('KEY')

def search_query(query):
    if query in cached_links.keys():
        print('Cache hit for query:', query)
        return cached_links[query]

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
        cached_links[query] = None
        return None
    if len(res['items']) == 0:
        cached_links[query] = None
        return None
    
    cached_links[query] = res['items'][0]['link']
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
    global last_updated
    if int(datetime.now().timestamp()) - last_updated > CACHE_TIMEOUT:
        cached_links.clear()
        last_updated = int(datetime.now().timestamp())
    print('Request IP:', request.remote_addr)
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
    with open('subjects.json', 'r') as f:
        subjects = json.load(f)
        f.close()
    return jsonify(subjects)

@app.route('/papersdownload', methods=['POST'])
def get_papers():
    data = request.form
    code = data['code']
    papers = data['papers'].split(',')
    variants = data['variants'].split(',')
    papers = [paper.strip() for paper in papers]
    variants = [variant.strip() for variant in variants]
    pdf = get_paper_pdf(code, papers, variants)

    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=code + "_papers.pdf",
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/paper', methods=['GET'])
def paper():
    return render_template('paper.html')


HOST = '0.0.0.0'
PORT = 5379
if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)
