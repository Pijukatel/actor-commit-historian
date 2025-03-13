## Commit historian

Simple tool to help analyze Github repository commits.  It checkouts the repository and get all relevant commit messages. It uses OpenAI to answer questions asked by the user. This is done through [PydanticAI](https://ai.pydantic.dev/) framework.


## How it works

Enter the repo name and your question and start the actor.
Optionally you can pick specific branch if your question is not related to the default branch of the repository.

If you do not input your own OpenAI API key then the actor will use our own API key, which will cause additional costs for running the actor.
You can pass your own OpenAI API key to significantly reduce the actor run costs.



