# MPLAD-AI: Execution Order & Branch Synchronization Timeline
**Preventing Team Mismatches, Merge Conflicts & Broken Dependencies**  
**Smart India Hackathon 2026 | Problem Statement ID: 26102**

---

## 1. Master Chronological Execution Flowchart

To prevent data mismatches and broken APIs, team members must execute and push their tasks in **4 Sequential Waves**. Nobody should jump to a dependent task before the foundation is verified and merged into `main`.

```mermaid
flowchart TD
    classDef lead fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef data fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef ml fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    classDef ui fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef gate fill:#ffebee,stroke:#d32f2f,stroke-width:3px;

    subgraph W1["Wave 1: Data Contracts & Foundations (Hours 0 - 24)"]
        M1_1["Member 1 (Leader - branch: backend)\n• PostgreSQL / Neon Schema\n• Pydantic Schemas & /health\n• Push to 'backend'"]:::lead
        M2_1["Member 2 (branch: data)\n• Raw Data Ingestion & Cleaning\n• Handle Missing Values & Outliers\n• Push to 'data'"]:::data
        M56_1["Members 5 & 6 (branch: frontend)\n• React 18 + Vite Setup\n• Layout Shell & Route Guards\n• Push to 'frontend'"]:::ui
    end

    G1{{"GATE 1: Verify & Merge M1, M2, M5/6 into main"}}:::gate
    W1 --> G1

    subgraph W2["Wave 2: Features & Core ML Models (Hours 24 - 48)"]
        M2_2["Member 2 (branch: data)\n• Feature Engineering Pipeline\n• Exports processed_data.parquet\n• Push to 'data'"]:::data
        M3_1["Member 3 (branch: ml-model)\n• Trains Cost, Delay, Duplicate & Payment Models\n• Serializes .joblib models\n• Push to 'ml-model'"]:::ml
        M5_1["Member 5 (branch: frontend)\n• Executive KPI Dashboard\n• Multi-Filter Project Table (Mock)\n• Push to 'frontend'"]:::ui
        M6_1["Member 6 (branch: frontend)\n• Leaflet India GIS Map Setup\n• Boundary & Marker Layers\n• Push to 'frontend'"]:::ui
    end

    G1 --> W2
    M2_2 -->|"Feeds processed_data.parquet"| M3_1
    W2 --> G2{{"GATE 2: Verify & Merge M2, M3, M5/6 into main"}}:::gate

    subgraph W3["Wave 3: Risk Engine & API Integration (Hours 48 - 72)"]
        M4_1["Member 4 (branch: risk-engine)\n• 0-100 Hybrid Scoring Engine\n• 4 Tiers: Low/Med/High/Critical\n• Explainable AI (XAI) Reasons\n• Push to 'risk-engine'"]:::ml
        M1_2["Member 1 (Leader - branch: backend)\n• Connects ML & Risk Models to FastAPI\n• /api/v1/projects & /api/v1/ai routes\n• Push to 'backend'"]:::lead
    end

    G2 --> W3
    M3_1 -.->|"Feeds detection outputs"| M4_1
    M4_1 -.->|"Feeds risk formulas"| M1_2
    W3 --> G3{{"GATE 3: Verify & Merge M4 & M1 into main"}}:::gate

    subgraph W4["Wave 4: Full UI Connect & Final Polish (Hours 72 - 96)"]
        M5_2["Member 5 (branch: frontend)\n• Connects Live KPIs & Explorer Table\n• PDF / Excel Export Suite\n• Push to 'frontend'"]:::ui
        M6_2["Member 6 (branch: frontend)\n• Connects 4-Color Map Pins (Green/Yellow/Orange/Red)\n• Builds Detailed Dossier & XAI Evidence Card\n• Push to 'frontend'"]:::ui
    end

    G3 --> W4
    M1_2 -.->|"Live REST API Endpoints"| M5_2
    M1_2 -.->|"Live Geo & Risk Endpoints"| M6_2
    W4 --> G4{{"GATE 4: Final End-to-End Test & Hackathon Pitch Ready"}}:::gate
```

---

## 2. Who Waits for Whom? (Strict Dependency Rules)

To prevent breaking code:

1. **Member 3 (ML Models) MUST WAIT for Member 2 (Feature Engineering):**  
   - Member 3 cannot train cost or delay models until Member 2 produces `processed_dataset.parquet` with normalized cost ratios and delay elapsed flags.
2. **Member 4 (Risk Engine) MUST WAIT for Member 3 (Detection Models):**  
   - Member 4 cannot compute the 0–100 composite risk score until Member 3 provides the individual model outputs (cost anomaly score, delay days, duplicate similarity, payment flags).
3. **Member 1 (Backend API) MUST WAIT for Member 4 (Risk Engine):**  
   - Member 1 cannot expose `/api/v1/ai/risk-assessment` until Member 4 finalizes the Risk Engine class and XAI reason generator.
4. **Members 5 & 6 (Frontend) CAN BUILD UI IN PARALLEL with Mock Data:**  
   - Frontend developers can design components, tables, and maps using mock JSON during Waves 1–2.  
   - They **switch to live APIs** in Wave 4 only after Member 1 merges live backend routes into `main`.

---

## 3. Step-by-Step Push & Pull Instructions for Teammates

### Rule: Always Pull Latest `main` Before Pushing!
Whenever a Gate is merged, all teammates must run:
```bash
# Update local branch with the latest verified main
git checkout <your-branch>
git pull origin main
```

### When Finishing a Task:
```bash
# Example for Member 3 on ml-model
git checkout ml-model
git add ml_engine/detection/
git commit -m "feat(ml): implement delay regressor and duplicate detection"
git push origin ml-model
```

Then tell the Team Leader:
> *"I have pushed my subtask to `ml-model`. Ready for verification."*
