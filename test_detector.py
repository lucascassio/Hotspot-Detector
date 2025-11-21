import pytest
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime
import pandas as pd

from fetch_repositories import analisar_com_pydriler

@pytest.fixture
def mock_commit_factory():
    def _create_commit(msg="fix bug", date=None, files=None, author="Dev"):
        commit = MagicMock()
        commit.msg = msg
        commit.committer_date = date if date else datetime.now()
        commit.author.name = author
        
        mod_files = []
        if files:
            for f_path in files:
                mod = MagicMock()
                mod.new_path = f_path 
                mod_files.append(mod)
        
        commit.modified_files = mod_files
        return commit
    return _create_commit

@pytest.fixture(autouse=True)
def mock_dependencies():
    m_open = mock_open()
    
    with patch("fetch_repositories.os.makedirs"), \
         patch("fetch_repositories.pd.DataFrame.to_csv"), \
         patch("fetch_repositories.plt.savefig"), \
         patch("fetch_repositories.plt.show"), \
         patch("fetch_repositories.webbrowser.open"), \
         patch("builtins.print"), \
         patch("builtins.open", m_open): 
        yield


@patch("fetch_repositories.Repository")
def test_fluxo_completo_sucesso(mock_repo, mock_commit_factory):
    c1 = mock_commit_factory(files=["main.py"])
    mock_repo.return_value.traverse_commits.return_value = [c1]

    analisar_com_pydriler("repo/path")

    mock_repo.return_value.traverse_commits.assert_called()
    assert pd.DataFrame.to_csv.called

@patch("fetch_repositories.Repository")
def test_sem_arquivos_modificados(mock_repo, mock_commit_factory):
    mock_repo.return_value.traverse_commits.return_value = []

    analisar_com_pydriler("repo/path")

    pd.DataFrame.to_csv.assert_not_called()

@patch("fetch_repositories.Repository")
def test_filtro_tipo_arquivo_positivo(mock_repo, mock_commit_factory):
    c1 = mock_commit_factory(files=["script.py", "readme.md"])
    mock_repo.return_value.traverse_commits.return_value = [c1]

    analisar_com_pydriler("repo/path", tipo_arquivo=".py")

    assert pd.DataFrame.to_csv.called

@patch("fetch_repositories.Repository")
def test_filtro_tipo_arquivo_negativo(mock_repo, mock_commit_factory):
    c1 = mock_commit_factory(files=["leia-me.txt"])
    mock_repo.return_value.traverse_commits.return_value = [c1]

    analisar_com_pydriler("repo/path", tipo_arquivo=".py")

    pd.DataFrame.to_csv.assert_not_called()

@patch("fetch_repositories.Repository")
def test_filtro_mensagem_commit_encontrado(mock_repo, mock_commit_factory):
    c1 = mock_commit_factory(msg="fix: critical bug", files=["bug.py"])
    mock_repo.return_value.traverse_commits.return_value = [c1]

    analisar_com_pydriler("repo/path", commit_msg_list=["fix"])

    assert pd.DataFrame.to_csv.called

@patch("fetch_repositories.Repository")
def test_filtro_mensagem_commit_ignorado(mock_repo, mock_commit_factory):
    c1 = mock_commit_factory(msg="docs: update readme", files=["readme.md"])
    mock_repo.return_value.traverse_commits.return_value = [c1]

    analisar_com_pydriler("repo/path", commit_msg_list=["fix"])

    pd.DataFrame.to_csv.assert_not_called()

@patch("fetch_repositories.Repository")
def test_erro_formato_data_desde(mock_repo):
    analisar_com_pydriler("repo", desde_data="DATA-INVALIDA")
    mock_repo.assert_not_called()

@patch("fetch_repositories.Repository")
def test_erro_formato_data_ate(mock_repo):
    analisar_com_pydriler("repo", ate_data="DATA-INVALIDA")
    mock_repo.assert_not_called()

@patch("fetch_repositories.Repository")
def test_ignora_arquivos_deletados(mock_repo, mock_commit_factory):
    c1 = mock_commit_factory(files=[])
    mod_deleted = MagicMock()
    mod_deleted.new_path = None 
    c1.modified_files = [mod_deleted]

    mock_repo.return_value.traverse_commits.return_value = [c1]

    analisar_com_pydriler("repo/path")

    pd.DataFrame.to_csv.assert_not_called()

@patch("fetch_repositories.Repository")
def test_verifica_parametros_pydriller(mock_repo, mock_commit_factory):
    mock_repo.return_value.traverse_commits.return_value = []
    
    analisar_com_pydriler("repo", desde_data="2023-01-01", ate_data="2023-12-31")
    
    _, kwargs = mock_repo.call_args
    assert kwargs['since'] == datetime(2023, 1, 1)
    assert kwargs['to'] == datetime(2023, 12, 31)