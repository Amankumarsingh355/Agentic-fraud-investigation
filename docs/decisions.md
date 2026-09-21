# Technical Decisions Record

## 1. Agent Framework
- **Selection**: **LangGraph / Stateful Graph Agent Loop**
- **Justification**: Provides deterministic state-machine orchestration, cycle support for iterative evidence gathering, and native human-in-the-loop checkpoints required for policy-enforced approval routing (`auto`, `L1`, `L2`).

## 2. Large Language Model (LLM)
- **Selection**: **Google Gemini 2.5 Flash / Pro (via `google-genai` SDK)**
- **Justification**: Delivers rapid structured JSON output generation conforming to the strict hackathon schema, superior reasoning over rich graph-derived evidence contexts, and high rate limits for processing multi-hop GraphRAG retrievals.

## 3. Graph Database & Protocol
- **Selection**: **TigerGraph (Savanna / TGCloud) + TigerGraph MCP (`tigergraph-mcp`)**
- **Justification**: Fulfills the hard hackathon requirement for graph traversal and GSQL execution, exposing standardized Model Context Protocol tools to the autonomous agent.
