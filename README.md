## Commit Historian Agent

Simple tool to help analyze Github repository commits.  It checkouts the repository and gets all relevant commit messages. It uses [OpenAI](https://openai.com/) to answer questions asked by the user. This is done through [PydanticAI](https://ai.pydantic.dev/) framework.

## How to run it

You can pick this actor from [Apify store](https://apify.com/josef.prochazka/commit-historian-agent) and run it on the Apify platform.

Enter repository name and your question and start the Actor.
Optionally you can choose a specific branch if your question is not related to the default branch of the repository.

If you do not input your own OpenAI API key then the actor will use our own API key, which will cause additional costs for running the actor.
You can pass your own OpenAI API key to significantly reduce the actor run costs.

## Example

**Inputs**:
> prompt: Show the most complicated changes done last month.

> repository: apify/crawlee-python

**Result**:
>Here are some of the most complicated changes from last month in the `apify/crawlee-python` repository:
>
>1. **Status Code Handling Update**: This refactor involved removing parameters and methods related to HTTP error status codes in HTTP clients, moving logic to a different class, and updating tests to ensure proper handling of session blocking status codes and error codes that require retries or retires. This was a significant change due to the impact on multiple components such as `Session`, `SessionPool`, `PlaywrightCrawler`, and `HttpCrawler` [details here](https://github.com/apify/crawlee-python/commit/6b5947125e63abdfff481b0669398fc9a7293e55).
>
>2. **Session Cookie Management**: The approach to handling cookies in a session was changed from using a plain dictionary to a more sophisticated `SessionCookies` class incorporating `CookieJar`. This supports basic cookie parameters and multiple domains, requiring extensive updates to tests and support for multi-domain scenarios [details here](https://github.com/apify/crawlee-python/commit/6523b3ade0eed53b0363ddce250c557024339b5e).
>
>3. **Fingerprint Integration**: Integration of the `browserforge` package to enable fingerprint and header generation in `PlaywrightCrawler` was implemented. This added significant functionality to enhance the crawling process by using generated fingerprints [details here](https://github.com/apify/crawlee-python/commit/2b156b4ba688f9111195422e6058dff30eb1f782).
>
>These complex changes involved substantial modifications to multiple parts of the codebase, including handling complex data structures, refactoring logic spread across different modules, and careful testing to ensure stability.


## How does it work

This Actor defines one main [AI agent](https://ai.pydantic.dev/api/agent/) that is responsible for processing the prompt and return desired output. It uses one [tool](https://ai.pydantic.dev/api/tools/#pydantic_ai.tools.AgentDepsT) that gets the commit summaries for the main agent.

The tool for getting the commit summaries is responsible for suggesting the relevant time scope of the prompt, getting the raw commit messages in the relevant time scope and prefilter the commits based on whether they seem relevant for the main prompt or not. It is using two different AI agents through what is described in PydanticAI documentation as [programatic agent hand-off](https://ai.pydantic.dev/multi-agent-applications/#programmatic-agent-hand-off):
* Agent responsible for suggesting time scope of the prompt.
* Agent responsible for deciding whether individual commit is relevant for the prompt.



