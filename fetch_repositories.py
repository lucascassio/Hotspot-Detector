import argparse
import pandas as pd
from pydriller import Repository
import os
import tempfile
import git  # GitPython


def detect_hotspots(repo_path):
    archives = {}

    for commit in Repository(repo_path).traverse_commits():
        is_bugfix = any(word in commit.msg.lower()
                        for word in ["fix", "bug", "error", "correction", "bug-fix", "bugfix"])

        for mod in commit.modified_files:
            if mod.new_path:
                if mod.new_path not in archives:
                    archives[mod.new_path] = {"modifications": 0, "bugfixes": 0}

                archives[mod.new_path]["modifications"] += 1
                if is_bugfix:
                    archives[mod.new_path]["bugfixes"] += 1

    df = pd.DataFrame.from_dict(archives, orient="index")
    df.index.name = "archives"
    df = df.sort_values(by=["bugfixes", "modifications"], ascending=False)

    return df


def main():
    parser = argparse.ArgumentParser(description="Hotspot Detector")
    parser.add_argument("repo", help="Caminho para o repositório Git (local ou URL)")
    args = parser.parse_args()

    repo_path = args.repo

    # Se for URL remota, clona para um diretório temporário
    if repo_path.startswith("http"):
        tmpdir = tempfile.mkdtemp()
        print(f"Clonando repositório em {tmpdir} ...")
        git.Repo.clone_from(repo_path, tmpdir)
        repo_path = tmpdir

    df = detect_hotspots(repo_path)

    print("\n=== Hotspots Detectados ===")
    print(df.head(20))  # mostra os 20 principais


if __name__ == "__main__":
    main()