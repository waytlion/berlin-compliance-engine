# Hackathon: "Arbio" - Berlin Compliance AI

**"Making Compliance Simple for Everyone"**

This repository contains the **AI Backend** (Compliance Engine) for our Hackathon solution. The frontend is built with [Lovable.dev](https://lovable.dev) and hosted separately.

## 🏗️ System Architecture

Our solution follows a decoupled, event-driven architecture to handle complex legal analysis without blocking the user interface.

### The Flow
1.  **Frontend (Lovable)**: User submits property details (Address, Usage Type, Registration Status).
2.  **API Trigger**: Lovable calls the **Tower API** (`POST /runs`).
3.  **AI Analysis (This Repo)**:
    - The Tower app (`compliance.py`) starts.
    - It reads rules from `ground_truth.json`.
    - **GPT-4o** infers facts (e.g., "Is this a primary residence?") and applies the specific Berlin laws.
4.  **Webhook Result**:
    - Once analysis is done (~15s), Tower sends a **Webhook** back to Lovable.
    - The payload includes "Smart Labels" (`inferred_facts`) and specific "Action Recommended" buttons.
5.  **User UI**: Lovable displays the report card with "Download PDF" buttons for the exact required forms.

### 🔗 Components
*   **Backend (Tower)**: [This Repository] - Handles logic, law knowledge base (`ground_truth.json`), and OpenAI orchestration.
*   **Frontend (Lovable)**: [Link to Lovable Repo/App] - User interface and report visualization.

### 🧠 Why This Architecture?
*   **Scalability**: We can add support for Munich or Hamburg just by adding a new JSON file in the backend.
*   **Reliability**: Webhooks prevent timeout errors on the frontend during long AI thinking times.
*   **Maintainability**: Legal experts can update `ground_truth.json` without touching code.
