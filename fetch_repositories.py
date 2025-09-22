import sys
import os
import argparse
from pydriller import Repository
from collections import Counter
from git import Repo
from datetime import datetime

CLONE_DIR = "repositorios_clonados"

def analisar_com_pydriler(
    repo_path: str,
    top_n: int = 10,
    desde_data: str = None,
    ate_data: str = None,
    tipo_arquivo: str = None,
    commit_msg_list: list[str] = None
):
    """
    Analisa um repositório e lista os arquivos mais modificados com base nos filtros fornecidos.
    """
    
    pydriller_args = {'path_to_repo': repo_path}
    filtros_aplicados = []
        
    if top_n:
        filtros_aplicados.append(f"Listando os {top_n} principais arquivos")
        
    if desde_data:
        try:
            pydriller_args['since'] = datetime.strptime(desde_data, '%Y-%m-%d')
            filtros_aplicados.append(f"Desde: {desde_data}")
        except ValueError:
            print(f"Erro: Formato de data inválido para '--desde'. Use AAAA-MM-DD.")
            return

    if ate_data:
        try:
            pydriller_args['to'] = datetime.strptime(ate_data, '%Y-%m-%d')
            filtros_aplicados.append(f"Até: {ate_data}")
        except ValueError:
            print(f"Erro: Formato de data inválido para '--ate'. Use AAAA-MM-DD.")
            return
            
    if tipo_arquivo:
        if not tipo_arquivo.startswith('.'):
            tipo_arquivo = '.' + tipo_arquivo
        filtros_aplicados.append(f"Tipo de Arquivo: {tipo_arquivo}")
    
    if commit_msg_list:
        termos_busca = ", ".join([f"'{termo}'" for termo in commit_msg_list])
        filtros_aplicados.append(f"Mensagem do Commit contém: {termos_busca}")


    print("\n--- Análise de Modificações de Arquivos ---")
    if filtros_aplicados:
        print("Filtros Aplicados: " + ", ".join(filtros_aplicados))
    else:
        print("Filtros Aplicados: Nenhum (analisando todo o histórico)")

    print(f"\n--- Resultado da Análise ---")
    
    contador_arquivos = Counter()

    try:
        repo_iterator = Repository(**pydriller_args).traverse_commits()

        for commit in repo_iterator:
            if commit_msg_list:
                commit_message_lower = commit.msg.lower()
                if not any(keyword.lower() in commit_message_lower for keyword in commit_msg_list):
                    continue

            for mod in commit.modified_files:
                if not mod.new_path:
                    continue
                
                if tipo_arquivo and not mod.new_path.endswith(tipo_arquivo):
                    continue

                contador_arquivos[mod.new_path] += 1

        if not contador_arquivos:
            print("Nenhum arquivo modificado encontrado com os filtros aplicados.")
            return

        print(f"{'Modificações':<15} | {'Caminho do Arquivo'}")
        print("-" * 70)
        for caminho, contagem in contador_arquivos.most_common(top_n):
            print(f"{contagem:<15} | {caminho}")

    except Exception as e:
        print(f"Erro durante a análise com PyDriller: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Analisa um repositório Git para encontrar os arquivos mais modificados.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("repo_url", help="A URL do repositório Git a ser clonado e analisado.")

    parser.add_argument(
        "--top",
        dest="top_n",
        help="Número de arquivos a serem exibidos no ranking (padrão: 10).",
        type=int,
        default=10
    )

    parser.add_argument(
        "-m", "--commit",
        dest="commit_msg_list",
        nargs='+',
        help="Analisa commits cuja mensagem contenha QUALQUER um dos textos especificados.\n"
             "Exemplo: -m \"fix\" \"refactor\" \"issue-123\"",
        default=None
    )

    parser.add_argument(
        "--desde", 
        dest="desde_data",
        help="Data de início para a análise (formato: AAAA-MM-DD).",
        type=str,
        default=None
    )
    
    parser.add_argument(
        "--ate", 
        dest="ate_data",
        help="Data final para a análise (formato: AAAA-MM-DD).",
        type=str,
        default=None
    )
    
    parser.add_argument(
        "--type", 
        dest="tipo_arquivo",
        help="Filtra a análise por tipo de arquivo (ex: 'py', 'java', 'md').",
        type=str,
        default=None
    )

    args = parser.parse_args()
    
    repo_nome = args.repo_url.split('/')[-1].replace('.git', '')
    caminho_local = os.path.join(CLONE_DIR, repo_nome)
    
    try:
        if not os.path.exists(caminho_local):
            os.makedirs(CLONE_DIR, exist_ok=True)
            print(f"Clonando {args.repo_url} para {caminho_local}...")
            Repo.clone_from(args.repo_url, caminho_local)
        else:
            print(f"Repositório já existe em {caminho_local}.")
            
        analisar_com_pydriler(
            caminho_local,
            top_n=args.top_n,
            desde_data=args.desde_data,
            ate_data=args.ate_data,
            tipo_arquivo=args.tipo_arquivo,
            commit_msg_list=args.commit_msg_list
        )

    except Exception as e:
        print(f"Erro inesperado no processo principal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()