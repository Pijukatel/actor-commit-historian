from datetime import datetime, timedelta, timezone
from tempfile import TemporaryDirectory

from git import Commit, Repo

repo_name = "apify/crawlee-python"


TODAY = datetime.now(tz=timezone.utc)
LAST_WEEK = TODAY - timedelta(days=7)


def get_commits(
    repo_name: str,
    branch: str = None,
    since: datetime = LAST_WEEK,
    until: datetime = TODAY,
) -> list[str]:
    """Get list of commits each summarized into single string."""
    repo_url = f"https://github.com/{repo_name}"

    with TemporaryDirectory() as temp_dir:
        repo = Repo.clone_from(f"{repo_url}.git", temp_dir, branch=branch)
        repo.git.checkout()
        commits = []
        for commit in repo.iter_commits():
            if commit.committed_datetime.astimezone(timezone.utc) < since:
                break
            elif commit.committed_datetime.astimezone(timezone.utc) < until:
                commits.append(commit_to_string(repo_url, commit))
    return commits


def commit_to_string(repo_url: str, commit: Commit) -> str:
    return (
        f"Author: {commit.author.name}\n"
        f"Url: {repo_url}/commit/{commit.hexsha}\n"
        f"Date: {commit.committed_datetime.isoformat()}\n"
        f"Commit message: {commit.message}\n"
    )
