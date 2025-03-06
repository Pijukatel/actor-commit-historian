import asyncio
from dataclasses import dataclass

from github import Commit, Github, Auth
from pydantic_ai import Agent, Tool, RunContext
from datetime import datetime


@dataclass
class Deps:
    github_token: str | None
    repo_name: str | None


time_scope_analyzer = Agent(
    "openai:gpt-4o",
    result_type=list[datetime, datetime],
    system_prompt=(
        f"Based on the prompt suggest time scope of the question and return it in datetime format with start date and"
        f" end date. Today is {datetime.now()}. "
    ),
    deps_type=datetime,
)

is_commit_relevant = Agent(
    "openai:gpt-4o",
    result_type=bool,
    system_prompt="Decide whether a commit is related to prompt.",
)


def commit_to_string(commit: Commit):
    return (
        f"Author: {commit.commit.author.name}\n Url: {commit.html_url}\n Date: {commit.commit.author.date}\n"
        f"Commit message: {commit.raw_data['commit']['message']}\n"
    )


async def prepare_commit_summaries(ctx: RunContext[Deps]) -> str:
    """Aggregate all relevant commits into single string."""

    # Get time scope of the question
    start, end = (await time_scope_analyzer.run(ctx.prompt)).data
    commits = (
        Github(auth=Auth.Token(ctx.deps.github_token))
        .get_repo(ctx.deps.repo_name)
        .get_commits(since=start, until=end)
    )
    commit_summaries: list[str] = []

    async def append_commit_summary_if_relevant(commit: Commit):
        """Append commit if it is relevant for the prompt."""
        commit_summary = commit_to_string(commit)
        if (
            await is_commit_relevant.run(
                f"Is following commit (Commit start) {commit_summary} (Commit end)\n"
                f"related to this prompt: {ctx.prompt}"
            )
        ).data:
            commit_summaries.append(commit_summary)

    tasks = [
        asyncio.create_task(append_commit_summary_if_relevant(commit))
        for commit in commits
    ]
    await asyncio.gather(*tasks)
    return "\n".join(commit_summaries)


repo_commit_analyzer = Agent(
    "openai:gpt-4o",
    result_type=str,
    system_prompt=(
        "Use `prepare_commit_summaries` tool to get batch of timestamped commit messages with url links to each commit "
        "and create summary based on input prompt. Insert relevant commit urls to the summary as link to source "
        "of the summary."
    ),
    deps_type=Deps,
    tools=[Tool(prepare_commit_summaries, takes_ctx=True)],
)
