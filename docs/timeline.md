
# Milestone 2 — Project Timeline and Task Allocation

## Transylvanian Folk & Rap Dual-Mode Creative Agent

**Team:** Platinum Records  
**Period:** Week 6 – Week 14

This document defines the weekly responsibilities and expected deliverables for each of the five team members.

Each member is responsible for completing the tasks assigned to their role. Collaboration is expected whenever tasks depend on another workstream.

---

## 1. Team Members and Roles

| Team Member | Role | Main Responsibility |
|-------------|---|---|
| Taisia      | Data Lead | Dataset collection, cleaning, preprocessing and licensing |
| Roxana      | RAG Lead | Chunking, embeddings, Qdrant and retrieval experiments |
| Răzvan      | Fine-tuning Lead | SLM selection, QLoRA and model evaluation |
| Denis       | MCP / Agent Lead | MCP server, tools, agent workflow and guardrails |
| Luiza       | Evaluation & Documentation Lead | Golden Dataset, evaluation metrics, documentation and presentation |

---

## 2. Weekly Task Allocation

### Week 6 — Architecture and Planning

**Goal:** Finalise the proposed architecture and upload the Milestone 2 documentation to GitHub. Implementation starts in Week 7.

| Role | Assigned Tasks | Expected Deliverable |
|---|---|---|
| Data Lead | Identify candidate folk, rap and dialect sources. Check their availability and initial licensing information. Decide with the team what type of rap data will be used. | Initial dataset source inventory and data collection plan |
| RAG Lead | Finalise the chunking strategy, choose Qdrant and BGE-M3 as primary candidates, and document alternative approaches. | RAG architecture and technical justification |
| Fine-tuning Lead | Identify 2–3 candidate SLMs, investigate GPU availability and define the proposed QLoRA approach. | Model selection plan and training strategy |
| MCP / Agent Lead | Finalise the six proposed MCP tools, define their responsibilities and document the agent decision workflow. | Agent workflow and MCP tool specifications |
| Evaluation & Documentation Lead | Define the Golden Dataset structure, evaluation categories, metrics and weekly timeline. Coordinate the final architecture document and upload. | Architecture documentation, timeline and evaluation plan |

**Team deliverable:**
- `docs/architecture.md`
- `docs/timeline.md`
- Architecture diagrams uploaded to GitHub.

---

### Week 7 — Data Preparation and Initial Infrastructure

**Goal:** Prepare the initial dataset, start the retrieval infrastructure and implement the first MCP tool.

| Role | Assigned Tasks | Expected Deliverable |
|---|---|---|
| Data Lead | Collect an initial sample of 50–100 text fragments. Create `sources.csv`, implement `clean.py`, normalise text and remove duplicates. | `data/raw/`, `data/processed/chunks.jsonl`, `sources.csv` |
| RAG Lead | Set up Qdrant locally, configure BGE-M3 embeddings, prepare the initial collection and implement the first retrieval notebook. | Running Qdrant instance and initial retrieval notebook |
| Fine-tuning Lead | Test access to Colab/GPU, check hardware limitations and run initial inference tests on the selected candidate models. | GPU availability report and model testing notes |
| MCP / Agent Lead | Implement `syllable_counter`, create approximately 12 manually verified test verses and initialise the MCP server skeleton. | Functional `syllable_counter` with pytest tests |
| Evaluation & Documentation Lead | Create the first 30 Golden Dataset examples, including prompts, expected answers or evaluation constraints. Coordinate dialect validation with the Data Lead. | Initial `data/eval/golden_v1_draft.jsonl` |

**Experiment E1:** Compare BGE-M3 and multilingual-e5 embeddings using an initial retrieval test set.

**Dependencies:** Data Lead provides the JSONL data format and sample to RAG Lead. Evaluation Lead coordinates prompt validation with Data Lead.

---

### Week 8 — Baseline RAG and Dataset Finalisation

**Goal:** Build the first RAG baseline and expand the agent's available tools.

| Role | Assigned Tasks | Expected Deliverable |
|---|---|---|
| Data Lead | Expand the initial corpus, complete data cleaning and ensure metadata is consistent across all records. | Updated and validated `chunks.jsonl` |
| RAG Lead | Complete the initial ingestion into Qdrant, implement baseline retrieval and test mode-based filtering. | Working baseline retrieval pipeline |
| Fine-tuning Lead | Compare the selected 2–3 SLM candidates on the same prompts, with and without retrieved context. Record their performance and limitations. | Model comparison notebook and observations |
| MCP / Agent Lead | Implement `rhyme_checker` and `retrieve_context`. Connect the retrieval tool to the RAG implementation. | Three functional tools: `syllable_counter`, `rhyme_checker`, `retrieve_context` |
| Evaluation & Documentation Lead | Expand the Golden Dataset to approximately 100 examples, organise development and locked test splits, and finalise the evaluation criteria. | Frozen `data/eval/golden_v1.jsonl` |

**Experiment E2:** Compare stanza-based chunking with fixed-size chunking.

**Dependencies:** RAG Lead provides the retrieval interface to MCP Lead. Fine-tuning Lead receives the same evaluation prompts from Evaluation Lead.

---

### Week 9 — Progress Check

**Goal:** Demonstrate the first working agent loop with RAG and three MCP tools.

| Role | Assigned Tasks | Expected Deliverable |
|---|---|---|
| Data Lead | Verify corpus quality, fix incorrect or duplicate entries and document data coverage. | Validated initial knowledge base |
| RAG Lead | Evaluate retrieval results, compare mode-filtered and baseline retrieval, and prepare retrieval experiment observations. | Retrieval experiment results |
| Fine-tuning Lead | Run the commercial baseline and untuned SLM on the same evaluation prompts. Record output quality and limitations. | Baseline comparison results for systems A and B |
| MCP / Agent Lead | Integrate the three functional tools into the agent loop. Implement basic generation, checking and revision flow. | Demonstrable agent prototype with RAG and three tools |
| Evaluation & Documentation Lead | Coordinate the progress demonstration, collect results from all members and prepare the progress report. | Week 9 progress report and evaluation summary |

**Experiment E3:** Compare mode filtering, hybrid search and re-ranking.

**Team deliverable:** Progress check demonstration of the agent loop with RAG and three MCP tools.

---

### Week 10 — Fine-tuning and Ingestion

**Goal:** Start task-specific fine-tuning and extend the MCP server.

| Role | Assigned Tasks | Expected Deliverable |
|---|---|---|
| Data Lead | Prepare and validate instruction pairs for folk generation, rap generation and dialect questions. Check source permissions and remove duplicates. | Fine-tuning dataset |
| RAG Lead | Improve retrieval using the results from Week 9. Implement or test hybrid search and document its effect. | Improved RAG pipeline and experiment results |
| Fine-tuning Lead | Configure QLoRA with 4-bit quantisation and rank r=16. Run the first fine-tuning experiment on the prepared instruction pairs. | First QLoRA training run and model checkpoint |
| MCP / Agent Lead | Implement the `ingest_dataset` tool and integrate it with the existing data ingestion pipeline. Add toxicity filter v1. | Functional dataset ingestion tool and initial safety filter |
| Evaluation & Documentation Lead | Evaluate the first fine-tuning run on the development split. Record results against the base model and update the experiment documentation. | QLoRA evaluation report |

**Experiment E4:** Compare the first QLoRA model with the base SLM on the development split.

---

### Week 11 — Full Toolset and Model Comparison

**Goal:** Complete all six MCP tools and integrate the fine-tuned model.

| Role | Assigned Tasks | Expected Deliverable |
|---|---|---|
| Data Lead | Review the training and retrieval datasets, correct remaining quality issues and prepare any additional examples required by the team. | Final cleaned dataset version |
| RAG Lead | Finalise the selected RAG configuration, optimise retrieval parameters and document the comparison of tested strategies. | Selected RAG configuration and results |
| Fine-tuning Lead | Run a second QLoRA experiment if needed, select the best checkpoint and compare the fine-tuned model with the base model. | Fine-tuned SLM v1 and comparison report |
| MCP / Agent Lead | Implement `dialect_lookup` and `meaning_check`. Integrate all six tools and add grounding checks for dialect-related claims. | Complete six-tool MCP server |
| Evaluation & Documentation Lead | Evaluate systems A, B and C on the Golden Dataset. Analyse structural quality, dialect authenticity and meaning preservation. | Three-system evaluation report |

**Experiment E5:** Compare the commercial baseline (A), untuned SLM (B) and fine-tuned SLM (C) on the Golden Dataset.

---

### Week 12 — GitHub Progress Review

**Goal:** Have a reproducible and inspectable implementation committed to GitHub before the Christmas holiday.

| Role | Assigned Tasks | Expected Deliverable |
|---|---|---|
| Data Lead | Ensure data ingestion, cleaning scripts, source documentation and processed dataset samples are committed and reproducible. | Complete data pipeline committed |
| RAG Lead | Ensure Qdrant configuration, retrieval pipeline, chunking and experiment results are committed. | Working RAG implementation committed |
| Fine-tuning Lead | Commit the fine-tuning scripts, model configuration, training results and model v1 or an accessible reference to it. | Fine-tuning implementation and results v1 |
| MCP / Agent Lead | Commit all six MCP tools, agent workflow, integration code and automated tests. | Complete MCP server and agent implementation |
| Evaluation & Documentation Lead | Consolidate evaluation results, update README with setup and execution instructions, and prepare the GitHub progress review documentation. | Updated README, evaluation report and progress review documentation |

**Experiment E6:** Compare the agent with and without the revision loop.

**Team deliverable:** All major components must be visible in GitHub commit history: ingestion, RAG, six tools, tuned model v1 and results v1.

---

### Week 13 — Final Evaluation and Improvements

**Goal:** Improve the system based on evaluation results and prepare the final demonstration.

| Role | Assigned Tasks | Expected Deliverable |
|---|---|---|
| Data Lead | Review the final knowledge base and correct problematic dialect entries or data inconsistencies identified during evaluation. | Final validated dataset |
| RAG Lead | Analyse retrieval failures, fix the most frequent retrieval issues and finalise RAG documentation. | Final retrieval results |
| Fine-tuning Lead | Analyse generation errors, make final model adjustments if feasible and document the final model configuration. | Final selected SLM and training report |
| MCP / Agent Lead | Fix tool integration issues, improve the revision loop and verify toxicity and grounding checks. | Stable integrated agent |
| Evaluation & Documentation Lead | Conduct human evaluation with native speakers, consolidate metrics and prepare the final documentation and presentation. | Final evaluation report and presentation |

**Experiment E7:** Human evaluation of dialect authenticity using a 1–5 rating scale.

**Team deliverable:** Code freeze, final documentation and demo rehearsal.

---

### Week 14 — Final Presentation

**Goal:** Present the completed project and demonstrate the system.

| Role | Assigned Tasks | Expected Deliverable |
|---|---|---|
| Data Lead | Explain the data sources, preprocessing and dataset ingestion functionality during the presentation. | Data pipeline demonstration |
| RAG Lead | Explain the RAG architecture and demonstrate retrieval from Qdrant. | RAG demonstration |
| Fine-tuning Lead | Present the SLM selection, QLoRA approach and model comparison results. | Model evaluation presentation |
| MCP / Agent Lead | Demonstrate the agent workflow, MCP tools and revision process. | Live agent demonstration |
| Evaluation & Documentation Lead | Coordinate the presentation, explain evaluation results and ensure documentation is complete. | Final presentation and documentation |

**Final deliverables:**
- 15-minute project demonstration.
- Complete documentation.
- Source code.
- Final evaluation results.

---

## 3. Experiment Summary

| ID | Experiment | Week | Responsible Roles |
|---|---|---|---|
| E1 | BGE-M3 vs multilingual-e5 embeddings | 7 | RAG Lead, Fine-tuning Lead |
| E2 | Stanza-based vs fixed-size chunking | 8 | RAG Lead, Data Lead |
| E3 | Mode filtering, hybrid search and re-ranking | 9 | RAG Lead, Evaluation Lead |
| E4 | First QLoRA run vs base SLM | 10 | Fine-tuning Lead, Evaluation Lead |
| E5 | Commercial baseline vs untuned SLM vs fine-tuned SLM | 11 | Fine-tuning Lead, Evaluation Lead |
| E6 | Agent with vs without revision loop | 12 | MCP / Agent Lead, Evaluation Lead |
| E7 | Human evaluation of dialect authenticity | 13 | Evaluation Lead, Data Lead |

---

## 4. Dependencies Between Roles

To avoid integration delays, the following dependencies must be respected:

- **Data Lead → RAG Lead:** Provides the JSONL schema, source inventory and cleaned data samples.
- **Evaluation Lead → Fine-tuning Lead:** Provides the evaluation prompts and ensures separation between training and evaluation data.
- **RAG Lead → MCP / Agent Lead:** Provides the retrieval interface required by `retrieve_context`.
- **Fine-tuning Lead → MCP / Agent Lead:** Provides the selected model and inference interface for agent integration.
- **All roles → Evaluation Lead:** Provide implementation results, experiment outputs and documentation for evaluation.

---

## 5. Risk Management

| Risk | Responsible Role | Mitigation |
|---|---|---|
| Dataset licensing restrictions | Data Lead | Verify licenses and prioritise original or permitted content |
| Poor data quality | Data Lead | Validate, clean and deduplicate records |
| Retrieval performance issues | RAG Lead | Compare embedding models and retrieval strategies |
| GPU or memory limitations | Fine-tuning Lead | Test GPU access early and use the planned fallback model |
| Fine-tuning does not improve quality | Fine-tuning Lead | Compare against the base SLM and document results |
| MCP integration delays | MCP / Agent Lead | Implement and test tools incrementally |
| Evaluation data leakage | Evaluation & Documentation Lead | Keep the locked test split separate from training data |
| Delays in project integration | All members | Commit progress weekly and agree on interfaces early |

---

## 6. GitHub Commit Expectations

Each member is expected to commit their work regularly under their assigned workstream.

The repository should show visible progress throughout the project, especially before the Week 12 GitHub review.

Suggested repository structure:

```text
project/
├── docs/
│   ├── RFC.md
│   ├── architecture.md
│   └── timeline.md
├── data/
│   ├── raw/
│   ├── processed/
│   └── eval/
├── notebooks/
├── mcp_server/
├── src/
└── README.md
```

Each weekly milestone should include:
- Implemented functionality or completed documentation.
- Relevant tests or experiment results.
- GitHub commits showing individual contributions.
- Updated documentation when technical decisions change.
