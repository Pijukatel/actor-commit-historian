import asyncio
import logging
from dataclasses import dataclass

from pydantic_ai import Agent, Tool, RunContext
from datetime import datetime

from src.git_utils import get_commits


@dataclass
class Deps:
    branch: str | None
    repo_name: str | None
    logger: logging.Logger


time_scope_analyzer = Agent(
    "openai:gpt-4o-mini",
    result_type=list[datetime, datetime],
    system_prompt=(
        f"Based on the prompt suggest time scope of the question and return it in datetime format with start date and"
        f" end date. Datetime should be offset-aware, use timezone UTC +2. Today is {datetime.now()}. "
    ),
    deps_type=datetime,
)

is_commit_relevant = Agent(
    "openai:gpt-4o-mini",
    result_type=bool,
    system_prompt="Decide whether a commit is related to prompt.",
)


async def prepare_commit_summaries(ctx: RunContext[Deps]) -> str:
    """Aggregate all relevant commits into single string."""

    # Get time scope of the question
    start, end = (await time_scope_analyzer.run(ctx.prompt)).data
    ctx.deps.logger.info(f"Checkout git repository.")
    all_commit_summaries = get_commits(
        repo_name=ctx.deps.repo_name, branch=ctx.deps.branch, since=start, until=end
    )
    ctx.deps.logger.info(f"Checkout finished.")

    async def keep_relevant_commit_summary(commit_summary: str) -> str | None:
        """Keep only commit relevant for the prompt. Filtering to reduce context size of the final prompt"""
        if (
            await is_commit_relevant.run(
                f"Is following commit (Commit start) {commit_summary} (Commit end)\n"
                f"related to this prompt: {ctx.prompt}"
            )
        ).data:
            return commit_summary
        return None

    tasks = [
        asyncio.create_task(keep_relevant_commit_summary(commit_summary))
        for commit_summary in all_commit_summaries
    ]
    # gather retains order of tasks (time ordered commits remain ordered)
    filtered_commit_summaries = await asyncio.gather(*tasks)
    ctx.deps.logger.info(f"Analyze relevant commits.")
    return "\n".join([result for result in filtered_commit_summaries if result])


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
