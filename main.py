from dotenv import load_dotenv
import requests
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

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
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    res = response.json()
    if 'items' not in res:
        return None
    if len(res['items']) == 0:
        return None
    
    return res['items'][0]['link']

def codeify(q):
    code = ''
    parts = q.split('/')
    code += parts[0] + "_"
    print(parts)
    if parts[2] == 'M':
        code += 's' + parts[4] + '_ms_' + parts[1]
    elif parts[2] == 'O':
        code += 'w' + parts[4] + '_ms_' + parts[1]
    elif parts[2] == 'F':
        code += 'm' + parts[4] + '_ms_' + parts[1]
    return code

@app.route('/search', methods=['GET'])
def main():
    q = request.args.get('q')
    q = codeify(q)
    link = search_query(q)
    if link is None:
        return jsonify({'error': 'No results found'})
    else:
        return link

if __name__ == '__main__':
    app.run(debug=True)