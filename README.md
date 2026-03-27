# Hackaton Berlin 2026 - Berlin Compliance Engine (Tower App)

This is the backend for the "Berlin Short-Term Rental Compliance" tool. It runs on the [Tower.dev](https://tower.dev) platform and uses OpenAI (GPT-4o) to analyze property listings against local regulations (`ZwVbG`, `ZwVbV`).

## 🛠️ Setup & Deployment

### 1. Prerequisites
- **Tower CLI**: Install via `npm install -g @tower-dev/cli`
- **OpenAI API Key**: You need a key with GPT-4 access.

### 2. Configuration
The app uses a **Data-Driven Rules Engine** defined in `ground_truth.json`. You do not need to edit Python code to update laws.

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/waytlion/berlin-compliance-engine.git
    cd berlin-compliance-engine
    ```
2.  **Set Environment Variables**:
    Looking at `Towerfile`, ensure your secrets are managed via the Tower Dashboard or CLI.
    ```bash
    tower secrets set OPENAI_API_KEY sk-...
    ```

### 3. Deploy
Deploy the app to your Tower workspace:
```bash
tower deploy
```

### 4. Running Locally (Testing)
You can run the script in standalone mode to verify logic before deploying:
```bash
python compliance.py
```
*(Make sure `OPENAI_API_KEY` is set in your local environment)*.

## 📂 Key Files
- `compliance.py`: Main logic (inference, context checks, webhook).
- `ground_truth.json`: **The Brain.** Contains all compliance categories, legal refs, and logic.
- `LOVABLE_INTEGRATION.md`: API contract for the frontend.
