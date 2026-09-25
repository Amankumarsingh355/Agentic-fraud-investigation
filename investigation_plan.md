# Investigation UI Refactor Plan

## Goal
Redesign the application into a ChatGPT-style conversational investigation environment while preserving the dark cyber-forensics theme. Ensure all data is fully dynamic and driven by the backend.

## Architectural Changes

1.  **Main Layout (App.jsx)**
    *   **Left Column (Case Explorer)**: Replaces `Sidebar.jsx`. Displays the 20 benchmark cases from the backend (HHG-XXX mapping to CASE-XXX).
    *   **Center Column (Investigation Center)**:
        *   **Header**: Compact Case Summary (Case ID, Risk, Confidence, Status, Active Agent, Evidence Count).
        *   **Middle**: Scrollable `ChatInterface.jsx`.
        *   **Bottom**: ChatGPT-style input box.
    *   **Right Column (Contextual Views)**: Tabs for `Graph`, `Agents`, `Timeline`, `Evidence`, `Actions`.

2.  **Contextual Views (Right Panel)**
    *   `Graph`: `PegaGraphCanvas.jsx` (already has zoom/pan, needs export, focus, collapse).
    *   `Agents`: Live agent activity pipeline (visualize the 11 agents).
    *   `Timeline`: Dynamically generated from backend events.
    *   `Actions`: Next Best Action panel (Approve, Reject, Request).

3.  **Real-Time Data Sync**
    *   `ChatInterface` needs to handle real responses from `/api/chat` (served by Ollama) and persist them via backend or `localStorage`.
    *   Implement polling or SSE in `App.jsx` to fetch live agent states (simulate progress/state changes across the 11 agents when an investigation starts).

4.  **No Fake Data**
    *   Ensure all charts, lists, timelines, and agent statuses fetch from the case JSON or `/api/system/status`.

## Step-by-Step Execution

1.  **Step 1: Refactor Main Layout (App.jsx)**
    *   Remove modal-based navigation (`activeNav` switching the entire screen).
    *   Implement a strict 3-column layout (Sidebar, Center Chat, Right Panel).
2.  **Step 2: Update Sidebar (Case Explorer)**
    *   Display all cases dynamically with risk/status indicators.
3.  **Step 3: Enhance Chat Interface (Center)**
    *   Make it the prominent view. Connect it to `/api/chat`.
4.  **Step 4: Build Contextual Right Panel**
    *   Tab system for Graph, Agents, Timeline, Actions.
    *   Move `PegaGraphCanvas` into the `Graph` tab.
    *   Move `AgentActivity` into the `Agents` tab.
    *   Move `CaseTimeline` into the `Timeline` tab.
5.  **Step 5: Agent Pipeline Visualization**
    *   Ensure the `Agents` tab visualizes the 11 agents with states like QUEUED, RUNNING, COMPLETED.
6.  **Step 6: Refinement & Polish**
    *   Ensure styling is strictly dark charcoal/green cyber-forensics.
