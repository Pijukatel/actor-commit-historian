## Commit Historian Agent

Simple tool to help analyze Github repository commits.  It checkouts the repository and get all relevant commit messages. It uses OpenAI to answer questions asked by the user. This is done through [PydanticAI](https://ai.pydantic.dev/) framework.

## How to run it

You can pick this actor from [Apify store](https://apify.com/josef.prochazka/commit-historian-agent) and run it on the Apify platform.


## How it works

Enter repository name and your question and start the Actor.
Optionally you can choose a specific branch if your question is not related to the default branch of the repository.

If you do not input your own OpenAI API key then the actor will use our own API key, which will cause additional costs for running the actor.
You can pass your own OpenAI API key to significantly reduce the actor run costs.



