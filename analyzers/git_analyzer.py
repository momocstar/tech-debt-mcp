# analyzers/git_analyzer.py (扩展)
import os
import git
from collections import defaultdict

def get_modification_frequency(repo_path: str, since_months: int = 6) -> dict:
    repo = git.Repo(repo_path)
    freq = defaultdict(int)
    import datetime
    cutoff = datetime.datetime.now() - datetime.timedelta(days=since_months*30)
    for commit in repo.iter_commits():
        if commit.committed_datetime < cutoff:
            continue
        for file in commit.stats.files:
            freq[file] += 1
    return freq

def get_changed_files(repo_path: str, since_commit: str) -> list:
    """返回相对于指定 commit 的所有变更文件路径（绝对路径）"""
    repo = git.Repo(repo_path)
    # 解析 since_commit，支持 HEAD~N 或具体哈希
    if since_commit.startswith('HEAD~'):
        # 例如 HEAD~5
        commit = repo.commit(since_commit)
    else:
        # 可能是具体的 commit hash
        commit = repo.commit(since_commit)
    # 获取自该 commit 以来的所有变更文件
    # 使用 git diff --name-only 获得文件列表
    diff = repo.git.diff('--name-only', commit.hexsha, 'HEAD')
    files = diff.split('\n') if diff else []
    # 转换为绝对路径
    abs_files = [os.path.join(repo_path, f) for f in files if f]
    return abs_files