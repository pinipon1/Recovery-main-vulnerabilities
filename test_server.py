from flask import Flask, jsonify
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

@app.route('/api/test')
def test():
    return jsonify({
        "status": "ok",
        "message": "Servidor funcionando",
        "google_api_key": "configurada" if os.getenv('GOOGLE_POLLEN_API_KEY') else "não configurada"
    })

@app.route('/api/previsao_tempo')
def previsao_tempo_test():
    return jsonify({
        "regiao": "Teste",
        "tem_polen": False,
        "message": "API de teste - Google Pollen API precisa ser ativada"
    })

if __name__ == '__main__':
    print("Iniciando servidor de teste...")
    app.run(debug=False, port=5003, host='127.0.0.1')