# Hotspot Detector — Mineração de Repositórios de Software

## 1) Membros do grupo
- Lucas Cassio Costa  
- Luís Eduardo Jorge Almeida 
- Nicolas Von Dolinger Moreira Rocha
- Bruna Dias

---

## 2) Explicação do sistema
O **Hotspot Detector** é uma ferramenta de linha de comando que analisa o histórico de commits de um repositório Git e identifica os arquivos mais problemáticos.  

**Entrada:** caminho para o repositório (`repo.git`).  
**Saída:** lista de arquivos mais modificados e com mais commits de correção de bugs.  

A ideia é que quanto mais um arquivo sofre mudanças e correções, maior a chance de ele ser um ponto crítico do sistema (um *hotspot*).  

---

## 3) Tecnologias possíveis
- **Python** para implementação.
- **GitPython** e **PyDriller** para ler histórico de commits.  
- **pandas** para organizar e gerar a lista de arquivos.  
- **argparse** para criar a interface de linha de comando.

## 4) Repositórios Analisados
- https://github.com/huggingface/transformers
- https://github.com/tensorflow/tensorflow
- 
