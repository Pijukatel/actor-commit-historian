import os
from apify import Actor


async def main() -> None:
    """Main entry point for the Apify Actor."""
    async with Actor:
        actor_input = await Actor.get_input()
        os.environ["OPENAI_API_KEY"] = (
            actor_input.get("open_ai_key", "") or os.environ["OPENAI_API_KEY"]
        )

        from src.ai_utils import repo_commit_analyzer, Deps

        response = await repo_commit_analyzer.run(
            user_prompt=actor_input.get("prompt"),
            deps=Deps(
                branch=actor_input.get("branch") or None,
                repo_name=actor_input.get("repo"),
                logger=Actor.log,
            ),
        )
        if actor_input.get("open_ai_key", ""):
            await Actor.charge(event_name="with_apify_token", count=1)
        else:
            await Actor.charge(event_name="with_own_token", count=1)

        Actor.log.info(
            f"Commit analysis was finished. Here is the answer:\n{response.data}"
        )
        await (await Actor.open_dataset()).push_data(
            {"Prompt": actor_input.get("prompt"), "Response": response.data}
        )
