# Week 7 — Running the RAG Notebook on Windows

## Requirements
- Python 3.12
- Docker Desktop running with Linux containers
- VS Code with Python and Jupyter extensions
- Internet connection for the first model download

Run terminal commands from the repository root.

## 1. Create the Python environment
Only needed if .venv does not already exist:

```powershell
py -m venv .venv
```

Activate it and install dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install ipykernel
```

## 2. Start Qdrant
For the first run:

```powershell
docker run -d --name llm-qdrant -p 127.0.0.1:6333:6333 -v llm-qdrant-storage:/qdrant/storage qdrant/qdrant
```

If the container already exists:

```powershell
docker start llm-qdrant
```

Dashboard: http://localhost:6333/dashboard

The Docker volume preserves Qdrant data.

## 3. Open the notebook
Open notebooks/week7_rag_retrieval.ipynb in VS Code.
Select the kernel belonging to .venv\Scripts\python.exe.

Make sure data/processed/chunks.jsonl exists.
If missing, generate the provisional sample:

```powershell
python src/ingestion/clean.py
```

## 4. Run the notebook
Run the cells in order.

Set HF_HUB_DISABLE_XET=1 before importing sentence_transformers
or huggingface_hub. Restart the kernel first if either library
has already been imported.

First model downloads require internet and may take time.
E5 is downloaded with snapshot_download and loaded locally.
The notebook already contains the successful download and local-loading sequence.
Model revisions are fixed; completed downloads are reused from the Hugging Face cache.
Do not delete cached models between runs.

Expected checks (`chunks.jsonl` now has 61 records; the notebook keeps the original 60 used for E1):
- 60 input fragments
- BGE-M3 embeddings: (60, 1024)
- E5-base embeddings: (60, 768)
- 60 points in each Qdrant collection
- Top 5 results for each of the 5 queries
- Evaluation JSON files saved under eval/week7/

## 5. Outputs
- bge_m3_results.json
- e5_base_results.json
- relevance_review.json
- metrics.json

The evaluation is exploratory and requires team review.
The dataset is provisional and intended for local prototyping.
## Troubleshooting
- Connection refused: start Docker Desktop, then `docker start llm-qdrant`.
- Wrong Python: select the project .venv kernel.
- Missing ipykernel: install it in .venv using the command above.
- Download timeout: inspect byte progress; do not leave a stalled download overnight.
- Collection dimension/count assertion: inspect the named collection. This notebook
  does not delete existing data automatically.

## Reproducibility
The model revisions are specified in the notebook.
`eval/week7/environment.json` records package versions used for local verification.
The root requirements.txt is not version-locked; other versions may behave differently.
See week7-rag-report.md for evaluation scope and limitations.
