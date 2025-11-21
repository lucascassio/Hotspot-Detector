# Hotspot Detector 

Membros do grupo
- Lucas Cassio Costa  
- Luís Eduardo Jorge Almeida 
- Nicolas Von Dolinger Moreira Rocha
- Bruna Andrade Dias

O **Hotspot Detector** é uma ferramenta de linha de comando (CLI) projetada para analisar o histórico de commits de repositórios Git e identificar arquivos problemáticos, conhecidos como *hotspots*.

A premissa da ferramenta é que arquivos que sofrem muitas alterações frequentes ou muitas correções de bugs têm maior probabilidade de conter dívida técnica e instabilidade.

---

## 🎯 Objetivo

Fornecer uma visão rápida e analítica sobre a saúde do código, permitindo que desenvolvedores identifiquem:
1.  Quais arquivos são modificados com mais frequência.
2.  Onde estão concentradas as correções de bugs.
3.  Como a atividade do repositório se comporta ao longo do tempo.

**Entrada:** URL de um repositório Git (ex: `https://github.com/owner/repo`).  
**Saída:** Relatório HTML contendo dados e gráficos a respeito do repositório.

---

## 🛠️ Tecnologias Utilizadas

A ferramenta foi desenvolvida em **Python** e utiliza as seguintes bibliotecas principais:

* **PyDriller & GitPython:** Para mineração e extração de dados do histórico de commits.
* **Pandas:** Para organização, filtragem e processamento dos dados.
* **Matplotlib & Seaborn:** Para a geração de gráficos estatísticos e visualização de dados.
* **Argparse:** Para a construção da interface de linha de comando.
* **Pytest:** Para a execução de testes automatizados.

---

## 🚀 Como Instalar

Pré-requisitos: Você precisa ter o **Python 3.10+** e o **Git** instalados na sua máquina.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/Hotspot-Detector.git](https://github.com/SEU_USUARIO/Hotspot-Detector.git)
    cd Hotspot-Detector
    ```

2.  **Crie e ative um ambiente virtual:**
    * *Windows:*
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * *Linux/Mac:*
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

---

## 💻 Como Utilizar

A sintaxe básica para rodar a ferramenta é:

```bash
python fetch_repositories.py [URL_DO_REPO] [OPCOES]
```

Argumentos opcionais

    --top : Define quantos arquivos exibir no ranking final. (Padrão: 10)
    -m, --commit : Filtra commits cuja mensagem contenha uma ou mais palavras-chave. 
    --type : Analisa apenas arquivos com uma extensão específica.
    --desde : Data inicial da análise (Formato: AAAA-MM-DD).
    --ate : Data final da análise (Formato: AAAA-MM-DD).
