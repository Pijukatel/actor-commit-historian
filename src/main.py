import os
from apify import Actor


async def main() -> None:
    """Main entry point for the Apify Actor."""
    async with Actor:
        actor_input = await Actor.get_input()
        os.environ.setdefault(
            "OPENAI_API_KEY", actor_input.get("open_ai_key", "missing key")
        )

        from src.ai_utils import repo_commit_analyzer, Deps

        response = (
            await repo_commit_analyzer.run(
                user_prompt=actor_input.get("prompt"),
                deps=Deps(
                    github_token=actor_input.get("github_token"),
                    repo_name=actor_input.get("repo"),
                ),
            )
        ).data
        Actor.log.info(response)
        await (await Actor.open_dataset()).push_data(
            {"Prompt": actor_input.get("prompt"), "Response": response}
        )
