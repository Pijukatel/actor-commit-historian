import asyncio
import logging
from dataclasses import dataclass

from pydantic_ai import Agent, Tool, RunContext
from datetime import datetime, timezone

from src.git_utils import get_commits


@dataclass
class Deps:
    branch: str | None
    repo_name: str | None
    logger: logging.Logger


@dataclass
class TimeScope:
    start: datetime
    end: datetime


async def get_relevant_dates(prompt: str) -> TimeScope:
    """Return estimated TimeScope based on the prompt."""
    time_scope_analyzer = Agent(
        "openai:gpt-4o",
        result_type=TimeScope,
        system_prompt=(
            f"Based on the prompt suggest time scope of the question and return only two dates in datetime format."
            f" First is start date and second is end date. For the reference, today is {datetime.now(tz=timezone.utc)}."
        ),
    )
    return (await time_scope_analyzer.run(prompt)).data


async def is_commit_relevant_to_prompt(commit_summary: str, prompt: str) -> bool:
    """Return True if commit summary is relevant for the prompt."""
    commit_relevancy_agent = Agent(
        "openai:gpt-4o",
        result_type=bool,
        system_prompt="Decide whether a commit is related to the prompt. Do not involve time in the decision."
        "If you are not sure, then it is related.",
    )
    return (
        await commit_relevancy_agent.run(
            f"Is following commit (Commit start) {commit_summary} (Commit end)\n"
            f"related to this prompt: {prompt}"
        )
    ).data


async def prepare_commit_summaries(ctx: RunContext[Deps]) -> str:
    """Aggregate all relevant commits into single string."""

    # Get time scope of the question
    time_scope: TimeScope = await get_relevant_dates(prompt=ctx.prompt)
    ctx.deps.logger.info(f"Suggested time scope of the question: {time_scope}.")
    ctx.deps.logger.info(f"Checkout git repository.")
    all_commit_summaries = get_commits(
        repo_name=ctx.deps.repo_name,
        branch=ctx.deps.branch,
        since=time_scope.start.astimezone(timezone.utc),
        until=time_scope.end.astimezone(timezone.utc),
    )
    ctx.deps.logger.info(
        f"Checkout finished. There are {len(all_commit_summaries)} commits in the question time scope."
    )

    async def keep_relevant_commit_summary(commit_summary: str) -> str | None:
        """Keep only commit relevant for the prompt. Filtering to reduce context size of the final prompt"""
        return (
            commit_summary
            if await is_commit_relevant_to_prompt(
                commit_summary=commit_summary, prompt=ctx.prompt
            )
            else None
        )

    tasks = [
        asyncio.create_task(keep_relevant_commit_summary(commit_summary))
        for commit_summary in all_commit_summaries
    ]
    # gather retains order of tasks (time ordered commits remain ordered)
    filtered_commit_summaries = await asyncio.gather(*tasks)
    relevant_commit_summaries = [
        result for result in filtered_commit_summaries if result
    ]
    ctx.deps.logger.info(
        f"Analyze relevant commits. {len(relevant_commit_summaries)} commits seems related to the question."
    )
    return "\n".join(relevant_commit_summaries)


def get_repo_commit_analyzer():
    return Agent(
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
