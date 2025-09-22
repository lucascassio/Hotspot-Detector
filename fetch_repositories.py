import os
import requests
import re
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import argparse

load_dotenv() 

def parse_github_url(repo_url):
    match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    if match:
        owner, repo_name = match.groups()
        return owner, repo_name
    return None, None

def detect_hotspots_from_github_api(owner, repo_name):
    token = os.getenv("API_KEY") 

    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
    archives = {}
    page = 1
    
    while True:
        response = requests.get(api_url, params={"page": page, "per_page": 100}, headers=headers)
        
        if response.status_code != 200:
            print(f"Erro ao acessar a API: {response.status_code}")
            return None
        
        commits = response.json()
        if not commits:
            break
            
        for commit_data in commits:
            commit_msg = commit_data['commit']['message'].lower()
            is_bugfix = any(word in commit_msg for word in ["fix", "bug", "error", "correction", "bug-fix", "bugfix"])

            commit_detail_url = commit_data['url']
            
            detail_response = requests.get(commit_detail_url, headers=headers)
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                for file_info in detail_data.get('files', []):
                    file_path = file_info['filename']
                    
                    if file_path not in archives:
                        archives[file_path] = {"modifications": 0, "bugfixes": 0}
                    
                    archives[file_path]["modifications"] += 1
                    if is_bugfix:
                        archives[file_path]["bugfixes"] += 1
        
        page += 1

    df = pd.DataFrame.from_dict(archives, orient="index")
    df.index.name = "archives"
    
    if not df.empty:
        df = df.sort_values(by=["bugfixes", "modifications"], ascending=False)
    
    return df

def main():
    parser = argparse.ArgumentParser(description="Hotspot Detector")
    parser.add_argument("repo", help="Caminho para o repositório Git (local ou URL)")
    args = parser.parse_args()

    repo_path = args.repo
    
    owner, repo_name = parse_github_url(repo_path)
    if owner and repo_name:
        df = detect_hotspots_from_github_api(owner, repo_name)
    else:
        print("URL do GitHub inválida.")
        return

    if df is not None and not df.empty:
        df = df.head()
        plt.scatter(df["modifications"], df["bugfixes"])
        plt.xlabel("Modificações")
        plt.ylabel("Correções de Bugs")
        plt.title("Hotspots do Repositório (Top 5)")
        plt.show()
    else:
        print("Nenhum dado encontrado para gerar o gráfico.")

if __name__ == "__main__":
    main()