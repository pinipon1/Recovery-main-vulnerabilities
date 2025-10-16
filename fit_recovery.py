# Requisitos: fitparse
# Instale com: pip install fitparse

import os
from fitparse import FitFile

def get_recovery_time_from_fit(fit_path):
    fitfile = FitFile(fit_path)
    for record in fitfile.get_messages('session'):
        for record_data in record:
            if record_data.name == 'total_recovery_time':
                return record_data.value
    return None

def main():
    dados_dir = os.path.join(os.path.dirname(__file__), 'dados')
    fit_files = [f for f in os.listdir(dados_dir) if f.endswith('.fit')]
    if not fit_files:
        print('Nenhum arquivo .fit encontrado na pasta dados.')
        return
    fit_path = os.path.join(dados_dir, fit_files[0])
    recovery_time = get_recovery_time_from_fit(fit_path)
    if recovery_time is not None:
        print(f'Recovery time: {recovery_time} minutos')
    else:
        print('Recovery time não encontrado no arquivo.')

if __name__ == '__main__':
    main()
