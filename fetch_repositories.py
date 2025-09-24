import sys
import os
import argparse
from pydriller import Repository
from collections import Counter
from git import Repo
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import webbrowser

CLONE_DIR = "repositories"
OUTPUT_DIR = "data"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")

def analisar_com_pydriler(
    repo_path: str,
    top_n: int = 10,
    desde_data: str = None,
    ate_data: str = None,
    tipo_arquivo: str = None,
    commit_msg_list: list[str] = None
):
    """
    Analisa um repositório, salva os dados e gráficos, e gera um relatório HTML.
    """
    # --- 1. Criação dos diretórios de saída ---
    os.makedirs(IMAGES_DIR, exist_ok=True)

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

    contador_arquivos = Counter()
    data_modificacoes = []

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
                data_modificacoes.append({'arquivo': mod.new_path, 'data': commit.committer_date, 'autor': commit.author.name})

        if not contador_arquivos:
            print("Nenhum arquivo modificado encontrado com os filtros aplicados.")
            return

        # --- 2. Criação e Salvamento dos DataFrames ---
        df = pd.DataFrame.from_records(data_modificacoes)
        df['data'] = pd.to_datetime(df['data'], utc=True)

        # Dados agregados dos top arquivos
        df_agg = df.groupby('arquivo').size().reset_index(name='modificacoes')
        df_agg = df_agg.sort_values(by='modificacoes', ascending=False).head(top_n)

        # Dados de modificações ao longo do tempo (por mês)
        # REMOVIDO WARNING: .dt.tz_localize(None) remove a informação de timezone antes de agrupar
        df_time = df.groupby(df['data'].dt.tz_localize(None).dt.to_period('M')).size().reset_index(name='modificacoes')
        df_time['data'] = df_time['data'].dt.to_timestamp()

        print(f"Salvando arquivos de dados em '{OUTPUT_DIR}'...")
        df.to_csv(os.path.join(OUTPUT_DIR, "modificacoes_completas.csv"), index=False)
        df_agg.to_csv(os.path.join(OUTPUT_DIR, "top_arquivos.csv"), index=False)
        df_time.to_csv(os.path.join(OUTPUT_DIR, "modificacoes_por_mes.csv"), index=False)
        print("Dados salvos com sucesso.")


        # --- 3. Geração e Salvamento dos Gráficos ---
        print(f"Gerando e salvando gráficos em '{IMAGES_DIR}'...")

        # Gráfico 1: Barras dos top arquivos
        plt.figure(figsize=(10, 6))
        # REMOVIDO WARNING: Adicionado hue='arquivo' e legend=False
        sns.barplot(data=df_agg, x='modificacoes', y='arquivo', palette='viridis', hue='arquivo', legend=False)
        plt.title('Top Arquivos Mais Modificados')
        plt.xlabel('Número de Modificações')
        plt.ylabel('Arquivo')
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "top_arquivos.png"))
        plt.close()

        # Gráfico 2: Linha da distribuição de modificações ao longo do tempo
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=df_time, x='data', y='modificacoes', marker='o')
        plt.title('Distribuição de Modificações ao Longo do Tempo')
        plt.xlabel('Data')
        plt.ylabel('Número de Modificações')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "modificacoes_tempo.png"))
        plt.close()

        # Gráfico 3 (NOVO): Pizza da distribuição por tipo de arquivo
        df['extensao'] = df['arquivo'].apply(lambda x: os.path.splitext(x)[1] if os.path.splitext(x)[1] else 'Sem Extensão')
        ext_counts = df['extensao'].value_counts().head(10)
        plt.figure(figsize=(12, 8)) # Figura mais larga para a legenda
        # AJUSTE: Plota o gráfico de pizza sem texto
        wedges, _ = plt.pie(ext_counts, startangle=140, colors=sns.color_palette('pastel'))
        
        # AJUSTE: Cria rótulos para a legenda com os percentuais
        total = float(sum(ext_counts))
        legend_labels = [f'{l} ({s/total*100:0.1f}%)' for l, s in zip(ext_counts.index, ext_counts)]
        
        # AJUSTE: Adiciona a legenda ao lado do gráfico
        plt.legend(wedges, legend_labels,
                   title="Tipos de Arquivo",
                   loc="center left",
                   bbox_to_anchor=(0.9, 0.5))

        plt.title('Distribuição de Modificações por Tipo de Arquivo (Top 10)')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "distribuicao_tipos.png"))
        plt.close()

        # Gráfico 4 (NOVO): Barras da atividade por dia da semana
        df['dia_semana'] = df['data'].dt.day_name()
        dias_ordem = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        plt.figure(figsize=(10, 6))
        # REMOVIDO WARNING: Adicionado hue='dia_semana' e legend=False
        sns.countplot(data=df, y='dia_semana', order=dias_ordem, palette='crest', hue='dia_semana', legend=False)
        plt.title('Atividade de Commit por Dia da Semana')
        plt.xlabel('Número de Commits')
        plt.ylabel('Dia da Semana')
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "atividade_semanal.png"))
        plt.close()
        
        print("Gráficos gerados com sucesso.")

        # --- 4. Geração e Abertura do Relatório HTML ---
        print("Gerando relatório HTML...")
        gerar_e_abrir_html(repo_path, filtros_aplicados, df_agg)


    except Exception as e:
        print(f"Erro durante a análise com PyDriller: {e}")

def gerar_e_abrir_html(repo_nome, filtros, df_agg):
    # Converte a tabela do DataFrame para HTML
    tabela_html = df_agg.to_html(index=False, justify='left', classes='table table-striped')

    html_string = f"""
    <html>
    <head>
        <title>Relatório de Análise do Repositório: {repo_nome}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }}
            h1, h2 {{ color: #333; }}
            .container {{ max-width: 1200px; margin: auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            .filtro {{ background-color: #e7f3fe; border-left: 6px solid #2196F3; padding: 10px 20px; margin-bottom: 20px; }}
            .chart-container {{ text-align: center; margin-bottom: 30px; }}
            img {{ max-width: 100%; height: auto; border-radius: 5px; margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:hover {{ background-color: #f5f5f5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relatório de Análise do Repositório</h1>
            <h2>{repo_nome}</h2>
            <div class="filtro">
                <h3>Filtros Aplicados:</h3>
                <p>{', '.join(filtros) if filtros else 'Nenhum (analisando todo o histórico)'}</p>
            </div>

            <h2>Top Arquivos Mais Modificados</h2>
            {tabela_html}

            <div class="chart-container">
                <h2>Distribuição de Modificações ao Longo do Tempo</h2>
                <img src="{os.path.join(IMAGES_DIR, "modificacoes_tempo.png")}">
            </div>

            <div class="chart-container">
                <h2>Atividade de Commit por Dia da Semana</h2>
                <img src="{os.path.join(IMAGES_DIR, "atividade_semanal.png")}">
            </div>

            <div class="chart-container">
                <h2>Distribuição por Tipo de Arquivo (Top 10)</h2>
                <img src="{os.path.join(IMAGES_DIR, "distribuicao_tipos.png")}">
            </div>
        </div>
    </body>
    </html>
    """
    
    report_path = 'relatorio.html'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_string)
    
    print(f"Relatório salvo em '{report_path}'. Abrindo no navegador...")
    webbrowser.open('file://' + os.path.realpath(report_path))


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