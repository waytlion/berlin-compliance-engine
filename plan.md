# 🚀 Project: Arbio "Compliance Guardian" Autopilot
**Hackathon Strategy Guide | Remaining Time: 16 Hours**

## 🎯 The Winning Concept: "From Chaos to Compliance"
**The Hook:** Start the demo with a "Folder of Doom"—messy PDFs, email screenshots, and handwritten notes.
**The Magic:** Drag and drop this folder. The system doesn't just "check" data; it **constructs** the property profile, cross-references local laws in real-time, and auto-drafts the permit application.
**The Wow Factor:** A "Compliance Confidence Score" that visually scans the uploaded documents and highlights risks (e.g., "This Airbnb is in a zone where rentals are limited to 90 days").

---

## 🛠 Technology Stack Strategy (Efficiency First)
*Use the provided tools to automate the coding process.*

1.  **Frontend & UI (Lovable):**
    * **Role:** Rapid UI generation. We will not write CSS/HTML manually.
    * *Automation Hack:* We will prompt Lovable to generate **three distinct UX flows** (Dashboard view, Map view, Document view). We pick the best one after 30 mins.
    * *Style:* Prompt it to scan `arbio.com` (visuals) to match the color palette (Teal/White/Clean) and typography.
2.  **Orchestration & Data (Tower):**
    * **Role:** The "Brain" pipeline. Use Tower to manage the async flow of data extraction so the UI doesn't freeze.
    * *Why:* Keeps the demo fast. Handling PDF parsing + OpenAI legal analysis takes time. Tower handles this in the background and pushes the result to the UI.
3.  **Intelligence (OpenAI):**
    * **Role:** The "Lawyer" & "Data Entry Clerk."
    * *Model:* `gpt-4o` (essential for multimodal vision analysis of photos/PDFs).

---

## 👥 Team Division (The "2-Person Powerhouse")

### **Member A: The Architect (Backend & Intelligence)**
* **Focus:** Tower Pipelines, OpenAI Prompts, Data Structure.
* **Goal:** Ensure the backend actually returns valid legal data.
* **Key Task:** Build the "Regulation Validator" logic.

### **Member B: The Visionary (Frontend, Experience & Pitch)**
* **Focus:** Lovable UI, User Journey, Mock Data, Video Production.
* **Goal:** Make it look like a finished product.
* **Key Task:** Build the "Human-in-the-loop" interface where the consultant approves the AI's findings.

---

## ⏱️ 16-Hour Sprint Roadmap

### Phase 1: The Blueprint & Setup (Hours 0-2)
* **Action:** Set up the GitHub Repo.
* **Member A (Tower):** Initialize a Tower pipeline. Create a script that takes a "Property Address" and "Uploaded Text," sends it to OpenAI with a prompt to check specific Berlin/London housing regulations.
* **Member B (Lovable):** Login to Lovable. Prompt: *"Create a property management dashboard for Arbio. Use a clean, professional teal and white color scheme. Sidebar: 'New Onboarding', 'Compliance alerts'. Main area: Drag-and-drop zone for property documents."*

### Phase 2: The Logic Core (Hours 2-6)
* **Member A:**
    * Refine the OpenAI System Prompt: *"You are a strict compliance officer for [City]. Analyze this unstructured text/image. Extract: Max Occupancy, Permit Number, Fire Safety Status. Compare against [Local Law Database - mock this with a static text file of rules]. Return JSON."*
    * Integrate this script into Tower.
* **Member B:**
    * Iterate on Lovable. Ask Lovable to add a "Split View": Left side = Original Document, Right side = Extracted Fields.
    * *Automation:* Ask Lovable to "Mock up the success state where all fields are green."

### Phase 3: Integration & "The Magic" (Hours 6-10)
* **Joint Effort:** Connect the Lovable Frontend to the Tower/Python Backend (via simple API or webhook).
* **The "Research" Feature:** Implement the logic where, if data is missing, the AI "browses" (simulated or real) to find the local council website.
* **Refinement:** Ensure the "Human-in-the-Loop" button works. The user must be able to click "Edit" on an AI suggestion.

### Phase 4: The Polish & Demo Prep (Hours 10-14)
* **Mock Data Injection:** Do not rely on live scraping for the demo video. Hardcode a "Perfect Scenario" and a "Compliance Violation Scenario."
* **Visuals:** Add a map component (Mapbox or Google Maps embed) showing the property location.
* **Repo Cleanup:** Ensure `README.md` is written (use ChatGPT to write it based on your code).

### Phase 5: Video & Submission (Hours 14-16)
* **Script:** Write the script (see below).
* **Record:** Use Loom. Record segments. Speed up loading times in editing if necessary.
* **Submit:** Double-check all links.

---

## 🎬 The "Awing" Demo Script (2 Minutes)

1.  **The Problem (0:00-0:20):**
    * *Visual:* Screen split. Left: A messy folder of PDFs/Emails. Right: A stressed property manager.
    * *Voiceover:* "Onboarding a property takes 30 hours of manual compliance checking. One mistake means a lawsuit."

2.  **The Solution - Ingestion (0:20-0:50):**
    * *Visual:* Drag and drop the messy folder into **Arbio Autopilot**.
    * *Visual:* Loading bar says "Scanning Local Regulations for Berlin-Mitte..." (Show the AI working).

3.  **The "Wow" Moment - Compliance Check (0:50-1:20):**
    * *Visual:* The dashboard lights up.
    * *Action:* The AI flags an issue: *"Warning: This property claims 6 guests, but Berlin regulations for this sq/ft limit it to 4."*
    * *Action:* User clicks "Resolve." AI suggests: *"Update listing to 4 guests" or "Apply for special permit."* User clicks "Update."

4.  **The Automation - Checklist & Export (1:20-1:50):**
    * *Visual:* The "Human-in-the-loop" consultant reviews the final summary. Green checks appear everywhere.
    * *Action:* Click "Finalize Onboarding." System generates a "Ready to Rent" PDF summary.

5.  **Outro (1:50-2:00):**
    * *Voiceover:* "Arbio Autopilot. Reducing onboarding from 3 days to 3 minutes. Powered by Tower and OpenAI."

---

## 🤖 AI Automation Prompts (Copy & Paste)

**To generate UI options in Lovable:**
> "I need 3 different variations of a 'Compliance Review' card.
> Option A: A simple checklist style.
> Option B: A conversational chat interface where the AI asks the user for missing info.
> Option C: A legal document style with annotations.
> Implement all 3 in a tabbed view so I can compare them."

**To generate the Compliance Logic (for Cursor/IDE):**
> "Write a Python script using OpenAI API. It needs to accept a PDF text string. It should extract 'Address' and 'Amenities'. Then, act as a Logic Engine: If 'Pool' is present, check against a boolean flag 'requires_fence_permit'. Return a JSON with {extracted_data, compliance_flags, missing_info_questions}."