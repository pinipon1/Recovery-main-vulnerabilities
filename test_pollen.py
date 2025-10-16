#!/usr/bin/env python3
"""
Teste simples para verificar se a Google Air Quality API está funcionando
"""
import os
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def testar_google_pollen_api():
    """Testa a Google Air Quality API"""
    
    api_key = os.getenv('GOOGLE_POLLEN_API_KEY')
    if not api_key:
        print("❌ GOOGLE_POLLEN_API_KEY não encontrada no .env")
        return False
    
    print(f"🔑 Using API Key: {api_key[:20]}...")
    
    # Coordenadas de Viseu
    latitude = 40.66
    longitude = -7.91
    
    url = f"https://airquality.googleapis.com/v1/forecast:lookup"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "location": {
            "longitude": longitude,
            "latitude": latitude
        },
        "includePollenInfo": True
    }
    
    params = {
        'key': api_key
    }
    
    print(f"🌍 Testando coordenadas: {latitude}, {longitude}")
    print(f"🔗 URL: {url}")
    
    try:
        response = requests.post(url, json=data, headers=headers, params=params, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API FUNCIONANDO!")
            print("📋 Dados recebidos:")
            
            # Verificar se tem informações de pólen
            if 'pollenInfo' in data:
                print("🌸 Dados de pólen encontrados!")
                for day in data.get('pollenInfo', {}).get('dailyInfo', []):
                    print(f"  📅 Data: {day.get('date', 'N/A')}")
                    for pollen in day.get('pollenTypeInfo', []):
                        pollen_type = pollen.get('code', 'UNKNOWN')
                        index_info = pollen.get('indexInfo', {})
                        value = index_info.get('value', 'N/A')
                        category = index_info.get('category', 'N/A')
                        print(f"    🌿 {pollen_type}: {value} ({category})")
            else:
                print("⚠️ Nenhum dado de pólen encontrado na resposta")
            
            return True
            
        elif response.status_code == 403:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Erro desconhecido')
            print("❌ API ainda não está ATIVA")
            print(f"📝 Erro: {error_msg}")
            
            # Verificar se é SERVICE_DISABLED
            if 'SERVICE_DISABLED' in str(error_data):
                print("🔧 Ação necessária:")
                print("   1. Ir ao Google Cloud Console")
                print("   2. Ativar a 'Air Quality API'")
                print("   3. Aguardar alguns minutos para propagação")
                
            return False
            
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testando Google Air Quality API...")
    print("=" * 50)
    
    sucesso = testar_google_pollen_api()
    
    print("=" * 50)
    if sucesso:
        print("🎉 Teste CONCLUÍDO com SUCESSO!")
        print("💡 A API está pronta para uso no sistema principal")
    else:
        print("⏳ Teste PENDENTE - API ainda não ativa")
        print("💡 Execute novamente após ativar a API no Google Cloud Console")