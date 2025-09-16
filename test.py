import sys
import os
from git import Repo, GitCommandError
from pydriller import Repository
from collections import Counter

# Define o diretório onde os repositórios serão clonados
CLONE_DIR = "repositorios_clonados"

def analisar_com_pydriller(repo_path: str, top_n: int = 10):
    """
    Usa o PyDriller para encontrar os arquivos mais modificados.
    Este método é mais alto nível e recomendado para análises complexas.
    """
    print(f"\n--- Análise com PyDriller: Top {top_n} Arquivos Mais Modificados ---")
    
    # Counter é um dicionário especial para contar ocorrências
    contador_arquivos = Counter()

    # Itera sobre todos os commits do repositório
    # PyDriller lida com todos os branches por padrão (order='topo')
    try:
        for commit in Repository(repo_path).traverse_commits():
            for modificacao in commit.modified_files:
                # O new_path representa o caminho do arquivo no commit atual
                if modificacao.new_path:
                    contador_arquivos[modificacao.new_path] += 1

        # Imprime os N arquivos mais comuns
        if not contador_arquivos:
            print("Nenhum arquivo modificado encontrado.")
            return

        print(f"{'Modificações':<15} | {'Caminho do Arquivo'}")
        print("-" * 70)
        for caminho, contagem in contador_arquivos.most_common(top_n):
            print(f"{contagem:<15} | {caminho}")

    except Exception as e:
        print(f"Ocorreu um erro durante a análise com PyDriller: {e}")


def analisar_com_gitpython(repo_path: str, top_n: int = 10):
    """
    Usa o GitPython para encontrar os arquivos mais modificados.
    Este método é mais baixo nível, interagindo diretamente com o Git.
    """
    print(f"\n--- Análise com GitPython: Top {top_n} Arquivos Mais Modificados ---")
    
    contador_arquivos = Counter()
    repo = Repo(repo_path)
    
    try:
        # Itera sobre todos os commits em todos os branches
        for commit in repo.iter_commits('--all'):
            # commit.stats.files é um dicionário com {caminho_arquivo: stats}
            for caminho_arquivo in commit.stats.files.keys():
                contador_arquivos[caminho_arquivo] += 1
        
        # Imprime os N arquivos mais comuns
        if not contador_arquivos:
            print("Nenhum arquivo modificado encontrado.")
            return
            
        print(f"{'Modificações':<15} | {'Caminho do Arquivo'}")
        print("-" * 70)
        for caminho, contagem in contador_arquivos.most_common(top_n):
            print(f"{contagem:<15} | {caminho}")

    except Exception as e:
        print(f"Ocorreu um erro durante a análise com GitPython: {e}")


def main():
    """
    Função principal do script.
    """
    if len(sys.argv) < 2:
        print(f"ERRO: Forneça a URL de um repositório Git.")
        print(f"Uso: python {sys.argv[0]} <URL_DO_REPOSITORIO>")
        sys.exit(1)
        
    repo_url = sys.argv[1]
    repo_nome = repo_url.split('/')[-1].replace('.git', '')
    caminho_local = os.path.join(CLONE_DIR, repo_nome)
    
    try:
        if not os.path.exists(caminho_local):
            print(f"Clonando repositório de '{repo_url}' para '{caminho_local}'...")
            os.makedirs(CLONE_DIR, exist_ok=True)
            Repo.clone_from(repo_url, caminho_local)
        else:
            print(f"Repositório '{repo_nome}' já existe em '{caminho_local}'.")
        
        # Executa as duas análises
        analisar_com_pydriller(caminho_local)
        analisar_com_gitpython(caminho_local)

    except GitCommandError as e:
        print(f"\nERRO DO GIT: Não foi possível acessar o repositório.")
        print(f"Detalhe do erro: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()