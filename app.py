# Endpoint para listar atividades do Strava (JSON)
# Endpoint para listar atividades do Strava (JSON)
## ...existing code...


## ...existing code...


from flask import Flask, jsonify, request, send_from_directory
import requests
import os
from pymongo import MongoClient
import datetime
# Carregar variáveis do .env automaticamente

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("DEBUG MONGODB_URI:", os.environ.get("MONGODB_URI"))
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production')

# --- STRAVA INTEGRAÇÃO ---
from flask import redirect, request, session, url_for

# Configurar variáveis de ambiente (com limpeza de caracteres especiais)
STRAVA_CLIENT_ID = os.getenv('STRAVA_CLIENT_ID', '').strip() if os.getenv('STRAVA_CLIENT_ID') else None
STRAVA_CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET', '').strip() if os.getenv('STRAVA_CLIENT_SECRET') else None
STRAVA_REDIRECT_URI = os.getenv('STRAVA_REDIRECT_URI', 'https://your-app.vercel.app/strava/callback').strip()

# Log para debug
print(f"[DEBUG] STRAVA_CLIENT_ID configurado: {'Sim' if STRAVA_CLIENT_ID else 'Não'}")
print(f"[DEBUG] STRAVA_CLIENT_SECRET configurado: {'Sim' if STRAVA_CLIENT_SECRET else 'Não'}")
print(f"[DEBUG] STRAVA_REDIRECT_URI: '{STRAVA_REDIRECT_URI}'")


# --- ENDPOINTS STRAVA ---
from flask import redirect, request, session, url_for

# Inicia login OAuth2
@app.route('/strava/auth')
def strava_auth():
    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
        return "Erro de configuração: Variáveis de ambiente STRAVA_CLIENT_ID e STRAVA_CLIENT_SECRET não estão definidas. Verifique a configuração no Vercel.", 500
    
    try:
        # Limpar e validar parâmetros (remover quebras de linha e espaços)
        client_id = STRAVA_CLIENT_ID.strip().replace('\n', '').replace('\r', '')
        redirect_uri = STRAVA_REDIRECT_URI.strip().replace('\n', '').replace('\r', '')
        
        # Validar se são válidos
        if not client_id or not redirect_uri:
            return "Erro: Parâmetros OAuth inválidos", 500
        
        url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&approval_prompt=auto&scope=activity:read_all"
        print(f"[DEBUG] Redirecionando para Strava OAuth: {url}")
        return redirect(url)
    except Exception as e:
        print(f"[ERRO] Falha ao iniciar OAuth: {e}")
        return f"Erro interno: {str(e)}", 500

# Recebe o token
@app.route('/strava/callback')
def strava_callback():
    print('[DEBUG] Entrou na rota /strava/callback')
    code = request.args.get('code')
    if not code:
        return 'Erro: código não recebido', 400
    
    try:
        # Limpar credenciais antes de usar
        client_id = STRAVA_CLIENT_ID.strip().replace('\n', '').replace('\r', '')
        client_secret = STRAVA_CLIENT_SECRET.strip().replace('\n', '').replace('\r', '')
        
        resp = requests.post('https://www.strava.com/oauth/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        })
    except Exception as e:
        print(f"[ERRO] Falha na requisição OAuth: {e}")
        return f"Erro interno: {str(e)}", 500
    data = resp.json()
    if 'access_token' in data:
        session['strava_token'] = data['access_token']
        print(f"[DEBUG] Strava access_token: {data['access_token']}")
        # Importa atividades automaticamente após login
        try:
            token = data['access_token']
            resp = requests.get('https://www.strava.com/api/v3/athlete/activities', headers={
                'Authorization': f'Bearer {token}'
            }, params={'per_page': 10})
            print(f"[DEBUG] Strava API status: {resp.status_code}")
            atividades = resp.json()
            print(f"[DEBUG] Atividades recebidas: {len(atividades)}")
            strava_collection = db['strava_atividades']
            for atividade in atividades:
                atividade_id = atividade.get('id')
                print(f"[DEBUG] Processando atividade id: {atividade_id}")
                # Buscar detalhes completos
                detalhes_resp = requests.get(f'https://www.strava.com/api/v3/activities/{atividade_id}', headers={
                    'Authorization': f'Bearer {token}'
                })
                detalhes = detalhes_resp.json() if detalhes_resp.status_code == 200 else {}
                # Buscar streams (GPS, altitude, FC, etc.)
                streams_resp = requests.get(f'https://www.strava.com/api/v3/activities/{atividade_id}/streams', headers={
                    'Authorization': f'Bearer {token}'
                }, params={'keys': 'latlng,altitude,heartrate,time', 'key_by_type': 'true'})
                streams = streams_resp.json() if streams_resp.status_code == 200 else {}
                atividade_completa = dict(atividade)
                atividade_completa['detalhes'] = detalhes
                atividade_completa['streams'] = streams
                # Build coordenadas for frontend
                latlng = streams.get('latlng', {}).get('data', [])
                altitude = streams.get('altitude', {}).get('data', [])
                heartrate = streams.get('heartrate', {}).get('data', [])
                tempo_total = detalhes.get('elapsed_time') or atividade.get('elapsed_time') or 0
                coordenadas = []
                for i in range(len(latlng)):
                    try:
                        c = {'lat': latlng[i][0], 'lon': latlng[i][1]}
                        if i < len(altitude): c['altitude'] = altitude[i]
                        if i < len(heartrate): c['heart_rate'] = heartrate[i]
                        # Estimate speed if possible with filtering
                        if i > 0 and tempo_total > 0 and len(latlng) > 1:
                            dx = ((latlng[i][0] - latlng[i-1][0])**2 + (latlng[i][1] - latlng[i-1][1])**2)**0.5 * 111.32
                            dt = tempo_total / len(latlng)
                            speed = (dx / (dt/3600)) if dt > 0 else 0
                            # Filter out unrealistic speeds (> 80 km/h for cycling, > 25 km/h for running)
                            max_speed = 80 if atividade.get('type', '').lower() in ['ride', 'cycling'] else 25
                            if speed > max_speed:
                                speed = 0
                            c['speed'] = round(speed, 2)
                        else:
                            c['speed'] = 0
                        coordenadas.append(c)
                    except Exception:
                        continue
                atividade_completa['coordenadas'] = coordenadas
                if strava_collection.count_documents({'id': atividade_id}) == 0:
                    strava_collection.insert_one(atividade_completa)
                    print(f"[DEBUG] Atividade {atividade_id} inserida no MongoDB com detalhes e streams")
                else:
                    print(f"[DEBUG] Atividade {atividade_id} já existe no MongoDB")
        except Exception as e:
            print(f'[ERRO] Falha ao importar atividades Strava: {e}')
        return redirect('/')
    print(f"[ERRO] Callback Strava: {data}")
    return f"Erro: {data}", 400

# Busca últimas atividades
@app.route('/strava/atividades')
def strava_atividades():
    token = session.get('strava_token')
    if not token:
        return redirect(url_for('strava_auth'))
    resp = requests.get('https://www.strava.com/api/v3/athlete/activities', headers={
        'Authorization': f'Bearer {token}'
    }, params={'per_page': 10})
    atividades = resp.json()
    return {'atividades': atividades}


# Baixa e guarda as 10 últimas atividades do Strava no MongoDB, evitando duplicados

# Novo endpoint: salva atividades Strava como JSON no MongoDB
@app.route('/strava/salvar_json')
def strava_salvar_json():
    token = session.get('strava_token')
    if not token:
        return redirect(url_for('strava_auth'))
    resp = requests.get('https://www.strava.com/api/v3/athlete/activities', headers={
        'Authorization': f'Bearer {token}'
    }, params={'per_page': 10})
    atividades = resp.json()
    strava_collection = db['strava_atividades']
    resultados = []
    for atividade in atividades:
        atividade_id = atividade['id']
        # Fetch details and streams for enrichment
        detalhes_resp = requests.get(f'https://www.strava.com/api/v3/activities/{atividade_id}', headers={
            'Authorization': f'Bearer {token}'
        })
        detalhes = detalhes_resp.json() if detalhes_resp.status_code == 200 else {}
        streams_resp = requests.get(f'https://www.strava.com/api/v3/activities/{atividade_id}/streams', headers={
            'Authorization': f'Bearer {token}'
        }, params={'keys': 'latlng,altitude,heartrate,time', 'key_by_type': 'true'})
        streams = streams_resp.json() if streams_resp.status_code == 200 else {}
        atividade_completa = dict(atividade)
        atividade_completa['detalhes'] = detalhes
        atividade_completa['streams'] = streams
        # Build coordenadas for frontend
        latlng = streams.get('latlng', {}).get('data', [])
        altitude = streams.get('altitude', {}).get('data', [])
        heartrate = streams.get('heartrate', {}).get('data', [])
        tempo_total = detalhes.get('elapsed_time') or atividade.get('elapsed_time') or 0
        coordenadas = []
        for i in range(len(latlng)):
            c = {'lat': latlng[i][0], 'lon': latlng[i][1]}
            if i < len(altitude): c['altitude'] = altitude[i]
            if i < len(heartrate): c['heart_rate'] = heartrate[i]
            # Estimate speed if possible with filtering
            if i > 0 and tempo_total > 0 and len(latlng) > 1:
                dx = ((latlng[i][0] - latlng[i-1][0])**2 + (latlng[i][1] - latlng[i-1][1])**2)**0.5 * 111.32
                dt = tempo_total / len(latlng)
                speed = (dx / (dt/3600)) if dt > 0 else 0
                # Filter out unrealistic speeds (> 80 km/h for cycling, > 25 km/h for running)
                tipo_atividade = atividade.get('type', '').lower()
                max_speed = 80 if tipo_atividade in ['ride', 'cycling'] else 25
                if speed > max_speed:
                    speed = 0
                c['speed'] = round(speed, 2)
            else:
                c['speed'] = 0
            coordenadas.append(c)
        atividade_completa['coordenadas'] = coordenadas
        # Deduplication: only insert if not present
        if strava_collection.count_documents({'id': atividade_id}) == 0:
            strava_collection.insert_one(atividade_completa)
            resultados.append({'atividade_id': atividade_id, 'status': 'salvo'})
        else:
            resultados.append({'atividade_id': atividade_id, 'status': 'duplicado'})
    return jsonify({'resultados': resultados})


# Conexão segura via variável de ambiente
@app.route('/api/atividades_unificadas')
def atividades_unificadas():
    atividades_strava = []
    
    # Verificar se MongoDB está conectado
    if db is None:
        return jsonify({'atividades': atividades_strava})
    
    try:
        # Strava JSON
        strava_collection = db['strava_atividades']
        for doc in strava_collection.find():
            doc = dict(doc)
            doc.pop('_id', None)
            # Processar streams para indicadores e coordenadas
            streams = doc.get('streams', {})
            detalhes = doc.get('detalhes', {})
            latlng = streams.get('latlng', {}).get('data', [])
            altitude = streams.get('altitude', {}).get('data', [])
            heartrate = streams.get('heartrate', {}).get('data', [])
            tempo = detalhes.get('elapsed_time') or doc.get('elapsed_time') or 0
            distancia = detalhes.get('distance') or doc.get('distance') or 0
            altitude_maxima = detalhes.get('max_altitude') or (max(altitude) if altitude else 0)
            altitude_minima = detalhes.get('min_altitude') or (min(altitude) if altitude else 0)
            tipo_atividade = detalhes.get('type') or doc.get('type', '')
            calorias = detalhes.get('calories') or 0
            # Coordenadas para o mapa
            coordenadas = []
            for i in range(len(latlng)):
                try:
                    c = {'lat': latlng[i][0], 'lon': latlng[i][1]}
                    if i < len(altitude): c['altitude'] = altitude[i]
                    if i < len(heartrate): c['heart_rate'] = heartrate[i]
                    # Estimar velocidade se possível
                    if i > 0 and tempo > 0 and len(latlng) > 1:
                        dx = ((latlng[i][0] - latlng[i-1][0])**2 + (latlng[i][1] - latlng[i-1][1])**2)**0.5 * 111.32
                        dt = tempo / len(latlng)
                        c['speed'] = round(dx / (dt/3600), 2) if dt > 0 else 0
                    else:
                        c['speed'] = 0
                    coordenadas.append(c)
                except Exception:
                    continue
            # Indicadores
            velocidade_media = None
            vo2max_estimado = None
            if tempo > 0 and distancia > 0:
                velocidade_media = round((distancia / tempo) * 3.6, 2)
                vo2max_estimado = round(velocidade_media * 2 + 3.5, 1)
            desnível_acumulado = 0
            if altitude and len(altitude) > 1:
                for i in range(1, len(altitude)):
                    diff = altitude[i] - altitude[i-1]
                    if diff > 0:
                        desnível_acumulado += diff
            fc_media = int(sum(heartrate)/len(heartrate)) if heartrate and len(heartrate) > 0 else detalhes.get('average_heartrate') or 0
            
            # Calcular TRIMP (Training Impulse)
            trimp_valor = 0.0
            if coordenadas and fc_media > 0:
                # Usar valores padrão ou estimar baseado na idade (se disponível)
                hr_repouso = 60  # Valor padrão - pode ser configurado pelo usuário futuramente
                hr_max = 185     # Valor padrão - pode ser estimado pela idade futuramente
                trimp_valor = calcular_trimp(coordenadas, hr_repouso, hr_max)
            
            nome_atividade = doc.get('name', 'Strava Activity')
            if nome_atividade:
                # Adiciona polyline e start_latlng se existirem
                polyline = None
                start_latlng = None
                if 'map' in doc and isinstance(doc['map'], dict):
                    polyline = doc['map'].get('summary_polyline')
                if 'start_latlng' in doc and isinstance(doc['start_latlng'], list) and len(doc['start_latlng']) == 2:
                    start_latlng = doc['start_latlng']
                atividades_strava.append({
                    'id': str(doc.get('id', '')),
                    'nome': nome_atividade,
                    'origem': 'strava',
                    'tipo': tipo_atividade,
                    'distancia_total': float(round(distancia/1000, 2)) if distancia else 0.0,
                    'tempo_total': int(tempo/60) if tempo else 0,
                    'velocidade_media': float(velocidade_media) if velocidade_media is not None else 0.0,
                    'vo2max_estimado': float(vo2max_estimado) if vo2max_estimado is not None else 0.0,
                    'desnivel_acumulado': int(desnível_acumulado) if desnível_acumulado else 0,
                    'frequencia_cardiaca_media': int(fc_media) if fc_media is not None else 0,
                    'trimp': float(trimp_valor),
                    'altitude_maxima': float(altitude_maxima) if altitude_maxima else 0.0,
                    'altitude_minima': float(altitude_minima) if altitude_minima else 0.0,
                    'calorias': int(calorias),
                    'coordenadas': coordenadas if coordenadas else [],
                    'data_atividade': str(doc.get('start_date', '') or doc.get('data_atividade', '') or '-'),
                    'start_date': str(doc.get('start_date', '') or '-'),  # Para compatibilidade
                    'json': doc,
                    'summary_polyline': polyline,
                    'start_latlng': start_latlng
                })
    except Exception as e:
        print(f"[ERRO] Falha ao carregar atividades unificadas: {e}")
    
    print(f"[DEBUG] atividades_unificadas retornando {len(atividades_strava)} atividades")
    if atividades_strava:
        print(f"[DEBUG] Primeira atividade - ID: {atividades_strava[0].get('id')}, Data: {atividades_strava[0].get('data_atividade')}")
    
    return jsonify({'atividades': atividades_strava})
# Configuração MongoDB com tratamento de erro
MONGODB_URI = os.environ.get("MONGODB_URI")
print(f"[DEBUG] MONGODB_URI configurado: {'Sim' if MONGODB_URI else 'Não'}")

def get_mongodb_client():
    """Função para obter cliente MongoDB com retry logic"""
    if not MONGODB_URI or MONGODB_URI.strip() == "":
        print("[ERRO] MONGODB_URI não definida!")
        return None, None
    
    # Debug da URI (mascarando senha)
    masked_uri = MONGODB_URI[:20] + "***" + MONGODB_URI[-20:] if len(MONGODB_URI) > 40 else "URI muito curta"
    print(f"[DEBUG] Tentando conectar com URI: {masked_uri}")
    
    # Verificar e ajustar parâmetros SSL na URI
    has_ssl_params = any(param in MONGODB_URI.lower() for param in ['ssl=true', 'tls=true', 'retrywrites=true'])
    print(f"[DEBUG] URI contém parâmetros SSL: {has_ssl_params}")
    
    # Se não tiver parâmetros SSL, adicionar os básicos
    modified_uri = MONGODB_URI
    if not has_ssl_params:
        separator = "&" if "?" in MONGODB_URI else "?"
        modified_uri = f"{MONGODB_URI}{separator}retryWrites=true&w=majority&ssl=true"
        print("[DEBUG] Parâmetros SSL adicionados à URI")
    
    try:
        # Tentar múltiplas configurações SSL para compatibilidade Vercel
        ssl_configs = [
            # Configuração 1: SSL com certificados relaxados
            {
                'serverSelectionTimeoutMS': 10000,
                'connectTimeoutMS': 10000,
                'socketTimeoutMS': 10000,
                'maxPoolSize': 1,
                'retryWrites': True,
                'w': 'majority',
                'authSource': 'admin',
                'tls': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True
            },
            # Configuração 2: SSL básico
            {
                'serverSelectionTimeoutMS': 15000,
                'connectTimeoutMS': 15000,
                'socketTimeoutMS': 15000,
                'maxPoolSize': 1,
                'retryWrites': True,
                'authSource': 'admin'
            },
            # Configuração 3: Mínima
            {
                'serverSelectionTimeoutMS': 20000,
                'maxPoolSize': 1
            }
        ]
        
        client = None
        for i, config in enumerate(ssl_configs):
            test_client = None
            try:
                print(f"[DEBUG] Tentando configuração SSL {i+1}/3")
                test_client = MongoClient(modified_uri, **config)
                test_db = test_client["fitdb"]
                
                # Teste de conectividade
                test_client.admin.command('ping')
                print(f"[DEBUG] Configuração SSL {i+1} funcionou!")
                client = test_client
                db = test_db
                break
                
            except Exception as config_error:
                print(f"[DEBUG] Configuração SSL {i+1} falhou: {config_error}")
                if test_client:
                    try:
                        test_client.close()
                    except:
                        pass
                continue
        
        if client is None:
            raise Exception("Todas as configurações SSL falharam")
            
        print("[DEBUG] MongoDB conectado com sucesso")
        return client, db
        
    except Exception as e:
        print(f"[ERRO] Falha ao conectar MongoDB: {e}")
        return None, None

# Inicializar conexão
client, db = get_mongodb_client()

from datetime import datetime

# Rota de debug para verificar configurações
@app.route('/api/debug_config')
def debug_config():
    return {
        'strava_client_id_set': bool(STRAVA_CLIENT_ID),
        'strava_client_id_clean': STRAVA_CLIENT_ID.strip().replace('\n', '').replace('\r', '') if STRAVA_CLIENT_ID else None,
        'strava_client_secret_set': bool(STRAVA_CLIENT_SECRET),
        'strava_redirect_uri': STRAVA_REDIRECT_URI,
        'strava_redirect_uri_clean': STRAVA_REDIRECT_URI.strip().replace('\n', '').replace('\r', ''),
        'mongodb_connected': db is not None,
        'mongodb_uri_set': bool(MONGODB_URI),
        'mongodb_uri_length': len(MONGODB_URI) if MONGODB_URI else 0,
        'mongodb_uri_preview': MONGODB_URI[:60] + "..." if MONGODB_URI and len(MONGODB_URI) > 60 else MONGODB_URI,
        'secret_key_set': bool(app.secret_key != 'change-this-in-production'),
        'has_newlines_in_redirect': '\n' in STRAVA_REDIRECT_URI or '\r' in STRAVA_REDIRECT_URI,
        'has_newlines_in_client_id': '\n' in (STRAVA_CLIENT_ID or '') or '\r' in (STRAVA_CLIENT_ID or '')
    }

@app.route('/api/debug_mongodb')
def debug_mongodb():
    """Endpoint específico para debug da conexão MongoDB"""
    debug_info = {
        'mongodb_uri_set': bool(MONGODB_URI),
        'mongodb_uri_length': len(MONGODB_URI) if MONGODB_URI else 0,
        'initial_connection': db is not None,
        'retry_test': None,
        'error': None
    }
    
    # Testar reconexão
    try:
        test_client, test_db = get_mongodb_client()
        debug_info['retry_test'] = test_db is not None
        if test_db:
            # Tentar uma operação simples
            test_db.list_collection_names()
            debug_info['collections_accessible'] = True
        else:
            debug_info['collections_accessible'] = False
    except Exception as e:
        debug_info['error'] = str(e)
        debug_info['retry_test'] = False
        debug_info['collections_accessible'] = False
    
    return debug_info

@app.route('/api/debug_compare_apis')
def debug_compare_apis():
    """Debug endpoint para comparar resumo_geral vs atividades_unificadas"""
    if db is None:
        return {'error': 'MongoDB não conectado'}, 500
    
    try:
        # Buscar resumo
        resumo_resp = resumo_geral()
        resumo_data = resumo_resp.get_json()
        resumo_atividades = resumo_data.get('atividades', [])
        
        # Buscar unificadas
        unificadas_resp = atividades_unificadas()
        unificadas_data = unificadas_resp.get_json()
        unificadas_atividades = unificadas_data.get('atividades', [])
        
        comparison = {
            'resumo_count': len(resumo_atividades),
            'unificadas_count': len(unificadas_atividades),
            'resumo_dates': [a.get('data_atividade') for a in resumo_atividades[:3]],
            'unificadas_dates': [a.get('data_atividade') for a in unificadas_atividades[:3]],
            'resumo_ids': [a.get('id') for a in resumo_atividades[:3]],
            'unificadas_ids': [a.get('id') for a in unificadas_atividades[:3]]
        }
        
        return comparison
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/debug_raw_data')
def debug_raw_data():
    """Inspecionar a estrutura real dos dados no MongoDB Atlas"""
    if db is None:
        return {'error': 'MongoDB não conectado'}, 500
    
    try:
        strava_collection = db['strava_atividades']
        
        # Buscar um documento de exemplo
        sample_doc = strava_collection.find_one()
        if not sample_doc:
            return {'error': 'Nenhuma atividade encontrada na coleção'}
        
        # Remover _id para JSON serialization
        sample_doc.pop('_id', None)
        
        # Analisar estrutura
        analysis = {
            'total_docs': strava_collection.count_documents({}),
            'sample_keys': list(sample_doc.keys()),
            'has_start_date': 'start_date' in sample_doc,
            'has_data_atividade': 'data_atividade' in sample_doc,
            'start_date_value': sample_doc.get('start_date'),
            'data_atividade_value': sample_doc.get('data_atividade'),
            'name_value': sample_doc.get('name'),
            'id_value': sample_doc.get('id'),
            'detalhes_keys': list(sample_doc.get('detalhes', {}).keys()) if 'detalhes' in sample_doc else [],
            'streams_keys': list(sample_doc.get('streams', {}).keys()) if 'streams' in sample_doc else []
        }
        
        return analysis
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/debug_frontend_logic')
def debug_frontend_logic():
    """Simular exatamente o que o frontend está fazendo"""
    if db is None:
        return {'error': 'MongoDB não conectado'}, 500
    
    try:
        # Simular o que o frontend faz:
        # 1. Buscar resumo_geral
        resumo_resp = resumo_geral()
        resumo_data = resumo_resp.get_json()
        resumo_atividades = resumo_data.get('atividades', [])
        
        # 2. Buscar atividades_unificadas  
        unificadas_resp = atividades_unificadas()
        unificadas_data = unificadas_resp.get_json()
        unificadas_atividades = unificadas_data.get('atividades', [])
        
        if not resumo_atividades or not unificadas_atividades:
            return {
                'error': 'Dados insuficientes',
                'resumo_count': len(resumo_atividades),
                'unificadas_count': len(unificadas_atividades)
            }
        
        # 3. Tentar fazer o matching como o frontend faz
        primeira_resumo = resumo_atividades[0]
        data_resumo = primeira_resumo.get('data_atividade')
        
        # Procurar na lista unificadas
        encontrada = None
        for ativ_unif in unificadas_atividades:
            data_unif = ativ_unif.get('data_atividade')
            if data_resumo == data_unif:
                encontrada = ativ_unif
                break
        
        # Tentar diferentes formatos de comparação
        from datetime import datetime
        matches_found = []
        
        for ativ_unif in unificadas_atividades:
            data_unif = ativ_unif.get('data_atividade')
            
            # Comparação direta (string)
            if data_resumo == data_unif:
                matches_found.append(('direct_string', data_unif))
                continue
                
            # Tentar comparação por datetime (ignorando timezone)
            try:
                dt_resumo = datetime.fromisoformat(data_resumo.replace('Z', '+00:00')) if data_resumo else None
                dt_unif = datetime.fromisoformat(data_unif.replace('Z', '+00:00')) if data_unif else None
                
                if dt_resumo and dt_unif and dt_resumo.date() == dt_unif.date():
                    matches_found.append(('date_only', data_unif))
                    continue
                    
                if dt_resumo and dt_unif and abs((dt_resumo - dt_unif).total_seconds()) < 60:
                    matches_found.append(('datetime_close', data_unif))
                    
            except:
                pass
        
        return {
            'resumo_primeira_data': data_resumo,
            'resumo_primeira_nome': primeira_resumo.get('nome_atividade'),
            'unificadas_datas': [a.get('data_atividade') for a in unificadas_atividades[:5]],
            'matches_found': matches_found,
            'total_matches': len(matches_found),
            'problema': 'Nenhum match encontrado' if not matches_found else f'{len(matches_found)} matches encontrados'
        }
        
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/debug_strava_activity')
def debug_strava_activity():
    if db is None:
        return {'error': 'MongoDB não conectado. Verifique MONGODB_URI.'}, 500
    
    strava_collection = db['strava_atividades']
    doc = strava_collection.find_one()
    if not doc:
        return {'error': 'No Strava activities found'}
    doc.pop('_id', None)
    streams = doc.get('streams', {})
    latlng = streams.get('latlng', {}).get('data', [])
    altitude = streams.get('altitude', {}).get('data', [])
    heartrate = streams.get('heartrate', {}).get('data', [])
    sample = {
        'latlng': latlng[:5],
        'altitude': altitude[:5],
        'heartrate': heartrate[:5],
        'doc_keys': list(doc.keys()),
        'streams_keys': list(streams.keys()),
        'has_coordenadas': 'coordenadas' in doc,
        'coordenadas_sample': doc.get('coordenadas', [])[:5]
    }
    return sample

@app.route('/api/limpar_strava')
def limpar_strava():
    strava_collection = db['strava_atividades']
    result = strava_collection.delete_many({})
    return {'deleted_count': result.deleted_count}

@app.route('/strava/logout')
def strava_logout():
    session.pop('strava_token', None)
    return redirect('/')
@app.route('/api/resumo_geral')
def resumo_geral():
    print("[DEBUG] Iniciando resumo_geral")
    atividades = []

    # Verificar conexão MongoDB com retry
    current_client, current_db = get_mongodb_client() if db is None else (client, db)
    
    if current_db is None:
        print("[DEBUG] MongoDB não conectado após retry, retornando lista vazia")
        return jsonify({'atividades': atividades, 'error': 'Falha na conexão com MongoDB'})
    
    try:
        print("[DEBUG] Conectando à coleção strava_atividades")
        strava_collection = current_db['strava_atividades']
        count = strava_collection.count_documents({})
        print(f"[DEBUG] Encontradas {count} atividades na coleção")
        
        for i, doc in enumerate(strava_collection.find()):
            try:
                print(f"[DEBUG] Processando atividade {i+1}")
                detalhes = doc.get('detalhes', {})
                tempo = detalhes.get('elapsed_time') or doc.get('elapsed_time') or 0
                distancia = detalhes.get('distance') or doc.get('distance') or 0
                velocidade_media = None
                vo2max_estimado = None
                if tempo > 0 and distancia > 0:
                    velocidade_media = round((distancia / tempo) * 3.6, 2)
                    vo2max_estimado = round(velocidade_media * 2 + 3.5, 1)
                fc_media = detalhes.get('average_heartrate') or doc.get('average_heartrate') or 0
                
                # Calcular TRIMP se houver dados de streams
                trimp_valor = 0.0
                streams = doc.get('streams', {})
                if streams and fc_media > 0:
                    heartrate = streams.get('heartrate', {}).get('data', [])
                    latlng = streams.get('latlng', {}).get('data', [])
                    
                    if heartrate and latlng:
                        # Criar coordenadas básicas para cálculo de TRIMP
                        coordenadas = []
                        for i in range(len(heartrate)):
                            if i < len(latlng):
                                coordenadas.append({
                                    'heart_rate': heartrate[i],
                                    'lat': latlng[i][0],
                                    'lon': latlng[i][1]
                                })
                        
                        if coordenadas:
                            hr_repouso = 60
                            hr_max = 185
                            trimp_valor = calcular_trimp(coordenadas, hr_repouso, hr_max)
                
                nome_atividade = doc.get('name', 'Strava Activity')
                data_atividade = doc.get('start_date', '')
                altitude_maxima = detalhes.get('max_altitude') or doc.get('elev_high') or 0
                altitude_minima = detalhes.get('min_altitude') or doc.get('elev_low') or 0
                desnível_acumulado = detalhes.get('total_elevation_gain') or doc.get('total_elevation_gain') or 0
                
                atividade_data = {
                    'id': str(doc.get('id', '')),  # Adicionar ID para debug
                    'nome_atividade': nome_atividade,
                    'data_atividade': str(data_atividade),
                    'start_date': str(data_atividade),  # Para compatibilidade
                    'velocidade_media': float(velocidade_media) if velocidade_media is not None else 0.0,
                    'vo2max_estimado': float(vo2max_estimado) if vo2max_estimado is not None else 0.0,
                    'distancia_total': float(round(distancia/1000, 2)) if distancia else 0.0,
                    'desnivel_acumulado': int(desnível_acumulado) if desnível_acumulado else 0,
                    'frequencia_cardiaca_media': int(fc_media) if fc_media is not None else 0,
                    'trimp': float(trimp_valor),
                    'altitude_maxima': float(altitude_maxima) if altitude_maxima else 0.0,
                    'altitude_minima': float(altitude_minima) if altitude_minima else 0.0,
                    'tempo_total': int(tempo/60) if tempo else 0
                }
                atividades.append(atividade_data)
                print(f"[DEBUG] Atividade {i+1} processada com sucesso: {nome_atividade}")
            except Exception as doc_error:
                print(f"[ERRO] Falha ao processar atividade {i+1}: {doc_error}")
                continue
    except Exception as e:
        print(f"[ERRO] Falha ao carregar atividades Strava: {e}")
        # Em caso de erro, retornar pelo menos uma estrutura válida
        return jsonify({'atividades': [], 'error': str(e)})
    
    print(f"[DEBUG] Total de atividades processadas: {len(atividades)}")
    
    try:
        print("[DEBUG] Ordenando atividades por data...")
        atividades.sort(key=lambda x: x.get('data_atividade', '') or '', reverse=True)
        print("[DEBUG] Ordenação concluída com sucesso")
    except Exception as e:
        print(f"[ERRO] Falha ao ordenar atividades: {e}")
    
    # Calcular estatísticas gerais
    try:
        print("[DEBUG] Calculando estatísticas gerais...")
        total_distancia = sum(ativ['distancia_total'] for ativ in atividades)
        total_desnivel = sum(ativ['desnivel_acumulado'] for ativ in atividades)
        tempo_total = sum(ativ['tempo_total'] for ativ in atividades)
        
        # Calcular tempo de repouso recomendado (baseado na atividade mais recente)
        tempo_repouso_recomendado = None
        if atividades:
            atividade_recente = atividades[0]  # Já ordenado por data decrescente
            duracao_min = atividade_recente.get('tempo_total', 0)  # Já em minutos
            # Estimar intensidade baseada na velocidade (simplificado)
            vel_media = atividade_recente.get('velocidade_media', 15)
            intensidade = min(1.0, vel_media / 25)  # Normalizar para 0-1
            
            # Valores padrão para demo (em produção viria das definições do utilizador)
            idade_padrao = 35
            peso_padrao = 75
            rpe_padrao = 6  # Perceived Exertion Scale 1-10
            
            if duracao_min > 0:
                horas, minutos, total_min = tempo_descanso(duracao_min, intensidade, idade_padrao, peso_padrao, rpe_padrao)
                tempo_repouso_recomendado = {
                    'horas': horas,
                    'minutos': minutos,
                    'total_minutos': total_min,
                    'texto': f"{horas}h {minutos}min" if horas > 0 else f"{minutos}min"
                }

        resumo = {
            'total_atividades': len(atividades),
            'total_distancia': round(total_distancia, 2),
            'total_desnivel': total_desnivel,
            'tempo_total': tempo_total,
            'tempo_repouso': tempo_repouso_recomendado,
            'atividades': atividades
        }
        
        print(f"[DEBUG] Resumo final: {len(atividades)} atividades, {total_distancia}km")
        if atividades:
            print(f"[DEBUG] Primeira atividade resumo - ID: {atividades[0].get('id')}, Data: {atividades[0].get('data_atividade')}")
        print("[DEBUG] Retornando resposta JSON")
        return jsonify(resumo)
    except Exception as e:
        print(f"[ERRO] Falha ao calcular estatísticas: {e}")
        # Fallback: retornar apenas as atividades
        return jsonify({'atividades': atividades, 'error': 'Falha ao calcular estatísticas'})




@app.route('/api/atividades', methods=['GET'])
def listar_atividades():
    # Sistema agora é 100% Strava - não há mais arquivos .fit
    atividades_mongo = []
    
    # Verifica autenticação Strava
    strava_status = "ok" if session.get('strava_token') else "not-authenticated"
    return jsonify({"atividades": atividades_mongo, "strava_status": strava_status})


def fator_recuperacao(idade, peso, rpe):
    base = 2.5
    ajuste_idade = 0.05 * ((idade - 30) // 10)
    ajuste_peso = 0.02 * ((peso - 75) // 5)
    ajuste_rpe = 10 / rpe
    fator = base + ajuste_idade + ajuste_peso
    fator = min(fator, ajuste_rpe)
    return fator

def tempo_descanso(duracao_min, intensidade, idade, peso, rpe):
    fator = fator_recuperacao(idade, peso, rpe)
    descanso_min = (duracao_min * intensidade) / fator
    horas = int(descanso_min // 60)
    minutos = int(descanso_min % 60)
    return horas, minutos, round(descanso_min, 1)










# Rota para servir o index.html
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Rota para servir arquivos estáticos (caso precise de CSS/JS)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# Mover a rota para fora do if __name__ == '__main__'
@app.route('/api/atividades_strava')
def atividades_strava():
    token = session.get('strava_token')
    if not token:
        return jsonify({'atividades': [], 'error': 'Usuário não autenticado no Strava.'}), 401
    resp = requests.get('https://www.strava.com/api/v3/athlete/activities', headers={
        'Authorization': f'Bearer {token}'
    }, params={'per_page': 10})
    atividades = resp.json()
    return jsonify({'atividades': atividades})

# --- PREVISÃO DO TEMPO ---
import datetime

@app.route('/api/previsao_tempo')
def previsao_tempo():
    """
    Endpoint para obter previsão do tempo de 7 dias com índice de ciclismo
    Usa WeatherAPI como alternativa mais confiável
    """
    regiao = request.args.get('regiao', 'Viseu,PT')
    alergico_polen = request.args.get('alergico_polen', 'false').lower() == 'true'
    
    # Tentar diferentes APIs de tempo gratuitas
    
    # 1. Tentar WeatherAPI (mais confiável)
    weather_api_key = os.getenv('WEATHER_API_KEY')
    if weather_api_key:
        try:
            return usar_weather_api(regiao, weather_api_key, alergico_polen)
        except Exception as e:
            print(f"[DEBUG] WeatherAPI falhou: {e}")
    
    # 2. Tentar OpenWeatherMap como fallback
    openweather_key = os.getenv('OPENWEATHER_API_KEY')
    if openweather_key:
        try:
            return usar_openweather_api(regiao, openweather_key, alergico_polen)
        except Exception as e:
            print(f"[DEBUG] OpenWeatherMap falhou: {e}")
    
    # 3. Usar API gratuita sem chave (Open-Meteo)
    try:
        return usar_open_meteo_api(regiao, alergico_polen)
    except Exception as e:
        print(f"[DEBUG] Open-Meteo falhou: {e}")
    
    # 4. Fallback para dados mockados
    print("[DEBUG] Todas as APIs falharam, usando dados mockados")
    return jsonify({
        'regiao': regiao,
        'previsao': gerar_dados_mockados(),
        'debug': 'Usando dados simulados - APIs não disponíveis'
    })
    
    try:
        print(f"[DEBUG] Buscando previsão para: {regiao}")
        print(f"[DEBUG] API Key presente: {'Sim' if api_key else 'Não'}")
        
        # Primeiro, obter coordenadas da cidade
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {
            'q': regiao,
            'limit': 1,
            'appid': api_key
        }
        
        print(f"[DEBUG] Fazendo geocoding para: {geocoding_url}")
        geo_response = requests.get(geocoding_url, params=geo_params)
        print(f"[DEBUG] Geocoding status: {geo_response.status_code}")
        
        if geo_response.status_code != 200:
            print(f"[DEBUG] Geocoding erro: {geo_response.text}")
            return jsonify({
                'error': f'Erro na geocodificação: {geo_response.status_code}',
                'message': geo_response.text
            }), geo_response.status_code
        
        geo_data = geo_response.json()
        print(f"[DEBUG] Geocoding resposta: {geo_data}")
        
        if not geo_data:
            return jsonify({'error': f'Localização "{regiao}" não encontrada'}), 404
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        print(f"[DEBUG] Coordenadas: lat={lat}, lon={lon}")
        
        # Obter previsão de 7 dias
        weather_url = "https://api.openweathermap.org/data/2.5/forecast"
        weather_params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric',
            'lang': 'pt'
        }
        
        print(f"[DEBUG] Fazendo previsão para: {weather_url}")
        weather_response = requests.get(weather_url, params=weather_params)
        print(f"[DEBUG] Previsão status: {weather_response.status_code}")
        
        if weather_response.status_code != 200:
            print(f"[DEBUG] Previsão erro: {weather_response.text}")
            return jsonify({
                'error': f'Erro na API do tempo: {weather_response.status_code}',
                'message': weather_response.text
            }), weather_response.status_code
        
        weather_data = weather_response.json()
        print(f"[DEBUG] Previsão recebida com {len(weather_data.get('list', []))} itens")
        
        # Verificar se há erro na resposta da API
        if 'cod' in weather_data and weather_data['cod'] != '200':
            return jsonify({
                'error': f'Erro da API OpenWeatherMap: {weather_data.get("message", "Erro desconhecido")}',
                'cod': weather_data['cod']
            }), 400
        
        # Processar dados para 7 dias
        previsao_7_dias = processar_previsao_7_dias(weather_data, alergico_polen)
        
        return jsonify({
            'regiao': f"{geo_data[0]['name']}, {geo_data[0]['country']}",
            'previsao': previsao_7_dias
        })
        
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Erro de requisição: {str(e)}")
        return jsonify({'error': f'Erro de conexão: {str(e)}'}), 500
    except KeyError as e:
        print(f"[DEBUG] Erro de chave: {str(e)}")
        return jsonify({'error': f'Dados incompletos da API: {str(e)}'}), 500
    except Exception as e:
        print(f"[DEBUG] Erro geral: {str(e)}")
        return jsonify({'error': f'Erro ao obter previsão: {str(e)}'}), 500

def processar_previsao_7_dias(weather_data, alergico_polen=False):
    """
    Processa dados da API e calcula índice de ciclismo para 7 dias
    """
    dias = {}
    
    for item in weather_data['list'][:35]:  # ~7 dias (5 dias * 8 previsões por dia)
        dt = datetime.datetime.fromtimestamp(item['dt'])
        data_str = dt.strftime('%Y-%m-%d')
        
        if data_str not in dias:
            dias[data_str] = {
                'data': dt.strftime('%d/%m'),
                'dia_semana': dt.strftime('%a'),
                'temperaturas': [],
                'ventos': [],
                'chuvas': [],
                'descricoes': []
            }
        
        dias[data_str]['temperaturas'].append(item['main']['temp'])
        dias[data_str]['ventos'].append(item['wind']['speed'])
        dias[data_str]['chuvas'].append(item.get('rain', {}).get('3h', 0))
        dias[data_str]['descricoes'].append(item['weather'][0]['description'])
    
    # Calcular médias e índices
    previsao_final = []
    for data, info in list(dias.items())[:7]:  # Garantir apenas 7 dias
        temp_media = sum(info['temperaturas']) / len(info['temperaturas'])
        temp_max = max(info['temperaturas'])
        temp_min = min(info['temperaturas'])
        vento_medio = sum(info['ventos']) / len(info['ventos'])
        prob_chuva = (sum(1 for c in info['chuvas'] if c > 0) / len(info['chuvas'])) * 100
        
        # Calcular índice de ciclismo (pólen será adicionado nos outros endpoints)
        indice = calcular_indice_ciclismo(temp_media, vento_medio, prob_chuva, None, alergico_polen)
        
        previsao_final.append({
            'data': info['data'],
            'dia_semana': info['dia_semana'],
            'temp_min': round(temp_min, 1),
            'temp_max': round(temp_max, 1),
            'temp_media': round(temp_media, 1),
            'vento': round(vento_medio * 3.6, 1),  # Converter m/s para km/h
            'prob_chuva': round(prob_chuva),
            'indice': indice,
            'descricao': info['descricoes'][0]  # Primeira descrição do dia
        })
    
    return previsao_final

def usar_open_meteo_api(regiao, alergico_polen=False):
    """
    Usa Open-Meteo API (gratuita, sem chave necessária)
    """
    print(f"[DEBUG] Usando Open-Meteo API para: {regiao}")
    
    # Obter coordenadas usando Nominatim (OpenStreetMap)
    geo_url = f"https://nominatim.openstreetmap.org/search?q={regiao}&format=json&limit=1"
    geo_response = requests.get(geo_url, headers={'User-Agent': 'CyclingPortal-App/1.0'})
    geo_data = geo_response.json()
    
    if not geo_data:
        raise Exception(f'Localização "{regiao}" não encontrada')
    
    lat = float(geo_data[0]['lat'])
    lon = float(geo_data[0]['lon'])
    display_name = geo_data[0]['display_name']
    
    print(f"[DEBUG] Coordenadas: lat={lat}, lon={lon}")
    
    # Obter previsão usando Open-Meteo
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max,weather_code',
        'forecast_days': 7,
        'timezone': 'Europe/Lisbon'
    }
    
    weather_response = requests.get(weather_url, params=params)
    weather_data = weather_response.json()
    
    if 'daily' not in weather_data:
        raise Exception('Dados de previsão não disponíveis')
    
    # Processar dados
    daily = weather_data['daily']
    previsao = []
    
    for i in range(7):
        data = datetime.datetime.fromisoformat(daily['time'][i])
        temp_max = daily['temperature_2m_max'][i]
        temp_min = daily['temperature_2m_min'][i]
        temp_media = (temp_max + temp_min) / 2
        vento = daily['wind_speed_10m_max'][i]
        prob_chuva = daily['precipitation_probability_max'][i]
        weather_code = daily['weather_code'][i]
        
        # Converter código do tempo para descrição
        descricao = obter_descricao_tempo(weather_code)
        
        # Calcular índice de ciclismo (inicialmente sem pólen)
        indice = calcular_indice_ciclismo(temp_media, vento, prob_chuva, None, alergico_polen)
        
        previsao.append({
            'data': data.strftime('%d/%m'),
            'dia_semana': data.strftime('%a'),
            'temp_min': round(temp_min, 1),
            'temp_max': round(temp_max, 1),
            'temp_media': round(temp_media, 1),
            'vento': round(vento, 1),
            'prob_chuva': round(prob_chuva),
            'indice': indice,
            'descricao': descricao
        })
    
    # Obter dados de pólen e qualidade do ar
    dados_polen = obter_dados_polen_e_qualidade_ar(lat, lon)
    
    # Integrar dados de pólen na previsão (se disponíveis) e recalcular índice
    if dados_polen:
        for i, dia in enumerate(previsao):
            if i < len(dados_polen):
                dia['polen'] = dados_polen[i]
                # Recalcular índice com dados de pólen
                if alergico_polen and 'indice_geral' in dados_polen[i]:
                    nivel_polen = dados_polen[i]['indice_geral']
                    # Recalcular o índice de ciclismo incluindo o pólen
                    dia['indice'] = calcular_indice_ciclismo(
                        dia['temp_media'], 
                        dia['vento'], 
                        dia['prob_chuva'], 
                        nivel_polen, 
                        alergico_polen
                    )
    
    return jsonify({
        'regiao': display_name.split(',')[0] + ', ' + display_name.split(',')[-1],
        'previsao': previsao,
        'fonte': 'Open-Meteo API (gratuita)',
        'tem_polen': bool(dados_polen)
    })

def usar_weather_api(regiao, api_key, alergico_polen=False):
    """
    Usa WeatherAPI.com (1000 chamadas gratuitas/dia)
    """
    print(f"[DEBUG] Usando WeatherAPI para: {regiao}")
    
    weather_url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        'key': api_key,
        'q': regiao,
        'days': 7,
        'aqi': 'no',
        'alerts': 'no'
    }
    
    response = requests.get(weather_url, params=params)
    data = response.json()
    
    if response.status_code != 200:
        raise Exception(f"WeatherAPI erro: {data.get('error', {}).get('message', 'Erro desconhecido')}")
    
    # Processar dados
    previsao = []
    for day_data in data['forecast']['forecastday']:
        day = day_data['day']
        date_obj = datetime.datetime.strptime(day_data['date'], '%Y-%m-%d')
        
        temp_max = day['maxtemp_c']
        temp_min = day['mintemp_c']
        temp_media = day['avgtemp_c']
        vento = day['maxwind_kph']
        prob_chuva = day['daily_chance_of_rain']
        descricao = day['condition']['text']
        
        # Calcular índice de ciclismo (inicialmente sem pólen)
        indice = calcular_indice_ciclismo(temp_media, vento, prob_chuva, None, alergico_polen)
        
        previsao.append({
            'data': date_obj.strftime('%d/%m'),
            'dia_semana': date_obj.strftime('%a'),
            'temp_min': round(temp_min, 1),
            'temp_max': round(temp_max, 1),
            'temp_media': round(temp_media, 1),
            'vento': round(vento, 1),
            'prob_chuva': round(prob_chuva),
            'indice': indice,
            'descricao': descricao
        })
    
    # Obter coordenadas para pólen
    lat = data['location']['lat']
    lon = data['location']['lon']
    
    # Obter dados de pólen e qualidade do ar
    dados_polen = obter_dados_polen_e_qualidade_ar(lat, lon)
    
    # Integrar dados de pólen na previsão (se disponíveis) e recalcular índice
    if dados_polen:
        for i, dia in enumerate(previsao):
            if i < len(dados_polen):
                dia['polen'] = dados_polen[i]
                # Recalcular índice com dados de pólen
                if alergico_polen and 'indice_geral' in dados_polen[i]:
                    nivel_polen = dados_polen[i]['indice_geral']
                    dia['indice'] = calcular_indice_ciclismo(
                        dia['temp_media'], 
                        dia['vento'], 
                        dia['prob_chuva'], 
                        nivel_polen, 
                        alergico_polen
                    )
    
    return jsonify({
        'regiao': f"{data['location']['name']}, {data['location']['country']}",
        'previsao': previsao,
        'fonte': 'WeatherAPI.com',
        'tem_polen': bool(dados_polen)
    })

def usar_openweather_api(regiao, api_key, alergico_polen=False):
    """
    Usa OpenWeatherMap (versão melhorada)
    """
    print(f"[DEBUG] Usando OpenWeatherMap para: {regiao}")
    
    # Primeiro, obter coordenadas da cidade
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct"
    geo_params = {
        'q': regiao,
        'limit': 1,
        'appid': api_key
    }
    
    geo_response = requests.get(geocoding_url, params=geo_params)
    if geo_response.status_code != 200:
        raise Exception(f'Geocoding erro: {geo_response.status_code}')
    
    geo_data = geo_response.json()
    if not geo_data:
        raise Exception(f'Localização "{regiao}" não encontrada')
    
    lat = geo_data[0]['lat']
    lon = geo_data[0]['lon']
    
    # Obter previsão de 7 dias
    weather_url = "https://api.openweathermap.org/data/2.5/forecast"
    weather_params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric',
        'lang': 'pt'
    }
    
    weather_response = requests.get(weather_url, params=weather_params)
    if weather_response.status_code != 200:
        raise Exception(f'API erro: {weather_response.status_code}')
    
    weather_data = weather_response.json()
    if 'cod' in weather_data and weather_data['cod'] != '200':
        raise Exception(f'OpenWeather erro: {weather_data.get("message", "Erro desconhecido")}')
    
    # Processar dados para 7 dias
    previsao_7_dias = processar_previsao_7_dias(weather_data)
    
    # Obter dados de pólen e qualidade do ar
    dados_polen = obter_dados_polen_e_qualidade_ar(lat, lon)
    
    # Integrar dados de pólen na previsão (se disponíveis)
    if dados_polen:
        for i, dia in enumerate(previsao_7_dias):
            if i < len(dados_polen):
                dia['polen'] = dados_polen[i]
    
    return jsonify({
        'regiao': f"{geo_data[0]['name']}, {geo_data[0]['country']}",
        'previsao': previsao_7_dias,
        'fonte': 'OpenWeatherMap',
        'tem_polen': bool(dados_polen)
    })

def obter_descricao_tempo(weather_code):
    """
    Converte código do tempo Open-Meteo para descrição em português
    """
    codigos = {
        0: 'Céu limpo',
        1: 'Principalmente limpo',
        2: 'Parcialmente nublado',
        3: 'Nublado',
        45: 'Nevoeiro',
        48: 'Nevoeiro gelado',
        51: 'Chuvisco fraco',
        53: 'Chuvisco moderado',
        55: 'Chuvisco intenso',
        61: 'Chuva fraca',
        63: 'Chuva moderada',
        65: 'Chuva forte',
        80: 'Pancadas de chuva fracas',
        81: 'Pancadas de chuva moderadas',
        82: 'Pancadas de chuva fortes',
        95: 'Trovoada',
        96: 'Trovoada com granizo fraco',
        99: 'Trovoada com granizo forte'
    }
    return codigos.get(weather_code, 'Tempo variável')

def gerar_dados_mockados():
    """
    Gera dados mockados para demonstração quando a API não está disponível
    """
    dados_mock = []
    
    # Simular 7 dias de previsão
    for i in range(7):
        data = datetime.datetime.now() + datetime.timedelta(days=i)
        # Simular dados variados mas realistas para Viseu
        temp_base = 18 + (i * 2) % 8  # Temperaturas entre 18-25
        
        dados_mock.append({
            'data': data.strftime('%d/%m'),
            'dia_semana': data.strftime('%a'),
            'temp_min': temp_base - 3,
            'temp_max': temp_base + 5,
            'temp_media': temp_base + 1,
            'vento': 12 + (i * 3) % 10,  # Vento entre 12-22 km/h
            'prob_chuva': 20 + (i * 15) % 60,  # Chuva entre 20-80%
            'indice': calcular_indice_ciclismo(temp_base + 1, (12 + (i * 3) % 10) / 3.6, 20 + (i * 15) % 60),
            'descricao': ['Céu limpo', 'Parcialmente nublado', 'Nublado', 'Chuva fraca'][i % 4]
        })
    
    return dados_mock

def calcular_trimp(coordenadas, hr_repouso=60, hr_max=185):
    """
    Calcula o TRIMP (Training Impulse) de uma atividade baseado nos dados de frequência cardíaca.
    
    Args:
        coordenadas: Lista de coordenadas com dados de heart_rate e timestamps
        hr_repouso: Frequência cardíaca de repouso (default: 60 bpm)
        hr_max: Frequência cardíaca máxima (default: 185 bpm)
    
    Returns:
        float: Valor TRIMP da sessão
    """
    if not coordenadas or len(coordenadas) < 2:
        return 0.0
    
    trimp = 0.0
    tempo_anterior = 0
    
    try:
        for i, coord in enumerate(coordenadas):
            if i == 0:
                continue
                
            # Verificar se existe dados de heart_rate
            hr = coord.get('heart_rate')
            if hr is None or hr <= 0:
                continue
            
            # Calcular intervalo de tempo (assumindo 1 segundo entre pontos se não houver timestamp)
            if 'time' in coord and 'time' in coordenadas[i-1]:
                dt = (coord['time'] - coordenadas[i-1]['time']) / 60.0  # em minutos
            else:
                dt = 1.0 / 60.0  # 1 segundo em minutos
            
            # Calcular intensidade relativa
            if hr_max > hr_repouso and hr >= hr_repouso:
                intensity = (hr - hr_repouso) / (hr_max - hr_repouso)
                # Aplicar fator exponencial de Banister (para TRIMP mais preciso)
                if intensity > 0:
                    trimp += intensity * dt * (intensity * 1.92)  # Fator de Banister
                    
    except Exception as e:
        print(f"[ERRO] Cálculo TRIMP: {e}")
        return 0.0
    
    return round(trimp, 2)

def estimar_hr_max_por_idade(idade):
    """
    Estima HR máxima baseada na idade usando fórmula de Tanaka.
    
    Args:
        idade: Idade em anos
    
    Returns:
        int: HR máxima estimada
    """
    return int(208 - (0.7 * idade))

def calcular_indice_ciclismo(temp, vento_kmh, prob_chuva, nivel_polen=None, alergico_polen=False):
    """
    Calcula índice de qualidade para ciclismo com análise mais detalhada
    Baseado em: temperatura ideal (18-24°C), vento moderado (<15km/h), baixa chuva (<20%), pólen (se alérgico)
    """
    pontuacao = 100
    
    # Análise detalhada da temperatura (ideal: 18-24°C)
    if temp < 0:
        pontuacao -= 50  # Congelamento - perigoso
    elif temp < 5:
        pontuacao -= 35  # Muito frio
    elif temp < 10:
        pontuacao -= 20  # Frio
    elif temp < 15:
        pontuacao -= 10  # Fresco
    elif temp < 18:
        pontuacao -= 5   # Ligeiramente fresco
    elif temp <= 24:
        pontuacao += 0   # Temperatura ideal
    elif temp <= 28:
        pontuacao -= 5   # Ligeiramente quente
    elif temp <= 32:
        pontuacao -= 15  # Quente
    elif temp <= 36:
        pontuacao -= 30  # Muito quente
    else:
        pontuacao -= 45  # Extremamente quente
    
    # Análise detalhada do vento
    vento_kmh = vento_kmh * 3.6 if vento_kmh < 50 else vento_kmh  # Garantir que está em km/h
    if vento_kmh <= 10:
        pontuacao += 5   # Vento calmo - bom
    elif vento_kmh <= 15:
        pontuacao += 0   # Vento leve - ideal
    elif vento_kmh <= 20:
        pontuacao -= 8   # Vento moderado
    elif vento_kmh <= 25:
        pontuacao -= 15  # Vento forte
    elif vento_kmh <= 30:
        pontuacao -= 25  # Vento muito forte
    else:
        pontuacao -= 40  # Vento extremo - perigoso
    
    # Análise detalhada da chuva
    if prob_chuva <= 10:
        pontuacao += 0   # Sem chuva - ideal
    elif prob_chuva <= 20:
        pontuacao -= 5   # Chuva leve possível
    elif prob_chuva <= 40:
        pontuacao -= 15  # Chuva moderada possível
    elif prob_chuva <= 60:
        pontuacao -= 25  # Chuva provável
    elif prob_chuva <= 80:
        pontuacao -= 35  # Chuva muito provável
    else:
        pontuacao -= 50  # Chuva quase certa
    
    # Análise de pólen (apenas se usuário for alérgico)
    if alergico_polen and nivel_polen is not None:
        # Deduzir pontos baseado no nível de pólen
        if nivel_polen <= 1:
            pontuacao -= 0   # Muito baixo - sem impacto
        elif nivel_polen <= 2:
            pontuacao -= 5   # Baixo - leve impacto
        elif nivel_polen <= 3:
            pontuacao -= 15  # Moderado - impacto significativo
        elif nivel_polen <= 4:
            pontuacao -= 25  # Alto - grande impacto
        else:
            pontuacao -= 35  # Muito alto - impacto severo
    
    # Garantir que pontuação está entre 0-100
    pontuacao = max(0, min(100, pontuacao))
    
    # Classificar com mais intervalos (escala tipo semáforo)
    if pontuacao >= 85:
        return {'nivel': 'excelente', 'texto': 'Excelente', 'cor': '#059669', 'pontuacao': pontuacao}
    elif pontuacao >= 70:
        return {'nivel': 'muito_bom', 'texto': 'Muito Bom', 'cor': '#16a34a', 'pontuacao': pontuacao}
    elif pontuacao >= 55:
        return {'nivel': 'bom', 'texto': 'Bom', 'cor': '#65a30d', 'pontuacao': pontuacao}
    elif pontuacao >= 40:
        return {'nivel': 'razoavel', 'texto': 'Razoável', 'cor': '#d97706', 'pontuacao': pontuacao}
    elif pontuacao >= 25:
        return {'nivel': 'mau', 'texto': 'Mau', 'cor': '#dc2626', 'pontuacao': pontuacao}
    else:
        return {'nivel': 'pessimo', 'texto': 'Péssimo', 'cor': '#991b1b', 'pontuacao': pontuacao}

def obter_dados_polen_e_qualidade_ar(lat, lon):
    """
    Obter dados de qualidade do ar da OpenWeatherMap + dados sazonais de pólen
    """
    try:
        print(f"[DEBUG] Buscando dados de qualidade do ar e pólen para lat={lat}, lon={lon}")
        
        # 1. Obter dados de qualidade do ar da OpenWeatherMap
        openweather_key = os.getenv('OPENWEATHER_API_KEY')
        qualidade_ar = None
        
        if openweather_key:
            try:
                url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={openweather_key}"
                response = requests.get(url)
                if response.status_code == 200:
                    qualidade_ar = response.json()
                    print(f"[DEBUG] Dados de qualidade do ar obtidos: {len(qualidade_ar.get('list', []))} registros")
            except Exception as e:
                print(f"[DEBUG] Erro ao obter qualidade do ar: {e}")
        
        # 2. Gerar dados sazonais de pólen baseados na época do ano e localização
        previsao_polen = gerar_dados_polen_sazonais(lat, lon)
        
        # 3. Combinar qualidade do ar com dados de pólen
        if qualidade_ar and previsao_polen:
            # Adicionar dados de qualidade do ar aos dados de pólen
            air_data = qualidade_ar.get('list', [])
            for i, dia_polen in enumerate(previsao_polen):
                if i < len(air_data):
                    components = air_data[i].get('components', {})
                    dia_polen['qualidade_ar'] = {
                        'aqi': air_data[i].get('main', {}).get('aqi', 1),
                        'pm2_5': components.get('pm2_5', 0),
                        'pm10': components.get('pm10', 0),
                        'o3': components.get('o3', 0),
                        'no2': components.get('no2', 0)
                    }
        
        return previsao_polen
        
    except Exception as e:
        print(f"[DEBUG] Erro ao obter dados de pólen e qualidade do ar: {e}")
        return []

def gerar_dados_polen_sazonais(lat, lon):
    """
    Gera dados mock de pólen baseados na época do ano e localização geográfica
    """
    try:
        hoje = datetime.datetime.now()
        previsao_polen = []
        
        # Determinar região climática baseada na latitude
        if lat > 45:  # Norte da Europa
            regiao = 'norte'
        elif lat > 35:  # Europa Central/Sul
            regiao = 'central'
        else:  # Mediterrâneo/Subtropical
            regiao = 'sul'
        
        # Padrões sazonais por região
        padroes_sazonais = {
            'norte': {
                'inverno': {'arvores': 1, 'ervas': 0, 'plantas': 0},
                'primavera': {'arvores': 4, 'ervas': 2, 'plantas': 1},
                'verao': {'arvores': 2, 'ervas': 4, 'plantas': 3},
                'outono': {'arvores': 1, 'ervas': 2, 'plantas': 1}
            },
            'central': {
                'inverno': {'arvores': 1, 'ervas': 1, 'plantas': 0},
                'primavera': {'arvores': 5, 'ervas': 3, 'plantas': 2},
                'verao': {'arvores': 3, 'ervas': 5, 'plantas': 4},
                'outono': {'arvores': 2, 'ervas': 3, 'plantas': 2}
            },
            'sul': {
                'inverno': {'arvores': 2, 'ervas': 1, 'plantas': 1},
                'primavera': {'arvores': 4, 'ervas': 3, 'plantas': 3},
                'verao': {'arvores': 3, 'ervas': 4, 'plantas': 4},
                'outono': {'arvores': 3, 'ervas': 2, 'plantas': 2}
            }
        }
        
        # Determinar estação
        mes = hoje.month
        if mes in [12, 1, 2]:
            estacao = 'inverno'
        elif mes in [3, 4, 5]:
            estacao = 'primavera'
        elif mes in [6, 7, 8]:
            estacao = 'verao'
        else:
            estacao = 'outono'
        
        padrao_base = padroes_sazonais.get(regiao, padroes_sazonais['central'])[estacao]
        
        # Gerar previsão para 5 dias
        import random
        for i in range(5):
            data_atual = hoje + datetime.timedelta(days=i)
            
            # Usar seed baseada na data para valores consistentes
            # Combinar ano, mês, dia e índice do dia para criar seed única
            seed = int(f"{data_atual.year}{data_atual.month:02d}{data_atual.day:02d}{i}")
            random.seed(seed)
            
            # Simular condições meteorológicas que afetam o pólen
            # Chuva reduz pólen, vento aumenta dispersão
            condicao_meteorologica = random.choice(['sol', 'sol', 'vento', 'chuva_leve'])
            
            if condicao_meteorologica == 'chuva_leve':
                # Chuva reduz significativamente o pólen
                modificador = -2
            elif condicao_meteorologica == 'vento':
                # Vento aumenta dispersão 
                modificador = random.randint(0, 1)
            else:  # sol
                # Condições normais
                modificador = random.randint(-1, 1)
            
            # Aplicar modificador com variação individual por tipo
            variacao_arvores = modificador + random.randint(-1, 0)
            variacao_ervas = modificador + random.randint(0, 1)  
            variacao_plantas = modificador + random.randint(-1, 1)
            
            arvores = max(0, min(5, padrao_base['arvores'] + variacao_arvores))
            ervas = max(0, min(5, padrao_base['ervas'] + variacao_ervas))
            plantas = max(0, min(5, padrao_base['plantas'] + variacao_plantas))
            
            indice_geral = max(arvores, ervas, plantas)
            
            previsao_polen.append({
                'data': data_atual.strftime('%d/%m'),
                'arvores': arvores,
                'ervas': ervas,
                'plantas': plantas,
                'indice_geral': indice_geral,
                'nivel': obter_nivel_polen(indice_geral)
            })
        
        # Reset da seed para não afetar outros códigos
        import time
        random.seed(time.time())
        
        print(f"[DEBUG] Gerados dados sazonais de pólen para região {regiao}, estação {estacao}")
        print(f"[DEBUG] Dados de pólen gerados de forma consistente baseada na data")
        return previsao_polen
        
    except Exception as e:
        print(f"[DEBUG] Erro ao gerar dados sazonais de pólen: {e}")
        return []

def obter_nivel_polen(indice):
    """
    Converte índice numérico em nível descritivo
    """
    if indice <= 1:
        return {'texto': 'Muito Baixo', 'cor': '#16a34a', 'emoji': '🟢'}
    elif indice <= 2:
        return {'texto': 'Baixo', 'cor': '#65a30d', 'emoji': '🟡'}
    elif indice <= 3:
        return {'texto': 'Moderado', 'cor': '#d97706', 'emoji': '🟠'}
    elif indice <= 4:
        return {'texto': 'Alto', 'cor': '#dc2626', 'emoji': '🔴'}
    else:
        return {'texto': 'Muito Alto', 'cor': '#991b1b', 'emoji': '🟣'}

@app.route('/api/heatmap_rotas')
def heatmap_rotas():
    """Endpoint para obter dados de GPS das últimas 10 atividades para heatmap"""
    try:
        # Usar conexão global do MongoDB
        if db is None:
            return jsonify({
                'success': False,
                'error': 'MongoDB não conectado',
                'rotas': []
            }), 500
            
        strava_collection = db['strava_atividades']
        
        # Buscar últimas 10 atividades no MongoDB, ordenadas por data
        atividades = list(strava_collection.find({}, {
            'id': 1, 
            'name': 1, 
            'start_date': 1, 
            'coordenadas': 1,
            'type': 1
        }).sort('start_date', -1).limit(10))
        
        rotas = []
        for atividade in atividades:
            coordenadas = atividade.get('coordenadas', [])
            if coordenadas:  # Só incluir se tiver coordenadas
                rota = {
                    'id': atividade.get('id'),
                    'name': atividade.get('name', 'Atividade sem nome'),
                    'type': atividade.get('type', 'Ride'),
                    'coordinates': [
                        [coord['lat'], coord['lon']] 
                        for coord in coordenadas 
                        if 'lat' in coord and 'lon' in coord
                    ]
                }
                if rota['coordinates']:  # Só adicionar se tiver coordenadas válidas
                    rotas.append(rota)
        
        print(f"[DEBUG] Encontradas {len(rotas)} rotas com coordenadas para heatmap")
        return jsonify({
            'success': True,
            'rotas': rotas,
            'total': len(rotas)
        })
        
    except Exception as e:
        print(f"[ERRO] Falha ao gerar dados de heatmap: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'rotas': []
        }), 500

# Para compatibilidade com Vercel - exportar a aplicação
application = app

if __name__ == '__main__':
    app.run(debug=True, port=5001)
