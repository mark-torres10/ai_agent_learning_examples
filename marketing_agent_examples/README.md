# Marketing agent examples

Examples of how to make marketing agents, using various agentic examples and workflows.

These will use the LLM APIs directly to work through how to do so.

Sources:

- https://www.anthropic.com/engineering/building-effective-agents
- https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents

Inside of this folder there will be a series of notebooks that will show different ways to architect this design. The B1 design shows a simple sequential implementation for achieving this agent workflow. The second notebook, the V2 notebook, will show how to modify this to use a supervisor and a retrial loop architecture. In the third version, V3, we will use other tools such as Langraph and Langsmith to make this more robust for putting into production. And in V4 we will put it all together by building just via a Docker container behind a REST API.
