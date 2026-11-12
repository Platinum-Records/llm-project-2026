# Week 7 — Fine-Tuning Lead Report

**Prepared by:** Răzvan Nojea
**Status:** I completed controlled smoke tests for Qwen and Gemma. RoLlama remains blocked by pending Hugging Face access to its base model.
**GPU check:** 2026-11-10
**Controlled inference run:** 2026-11-12

## What I Checked

I checked Google Colab GPU availability and ran the same three draft evaluation prompts against Qwen and Gemma. These were inference-only smoke tests; I did not train a model.

| Item                                        | Observed value                                                     |
| ------------------------------------------- | ------------------------------------------------------------------ |
| GPU                                         | NVIDIA Tesla T4                                                    |
| GPU memory                                  | 15,360 MiB reported by `nvidia-smi`; 14.56 GiB reported by PyTorch |
| Driver                                      | 580.82.07                                                          |
| CUDA                                        | 13.0                                                               |
| Memory in use during the initial idle check | 0 MiB                                                              |

The T4 confirms that I can use a Colab GPU. This check does not establish that the T4 can complete the planned training run; model fit and training time still need to be tested with the approved data and final settings.

## Candidate Models

| Model                                                                               | Role                                       | My test status                                                                                                                                                    |
| ----------------------------------------------------------------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`Qwen/Qwen3-4B-Instruct-2507`](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | Primary 4B instruction-tuned candidate     | Tested on all three prompts                                                                                                                                       |
| [`google/gemma-3-4b-it`](https://huggingface.co/google/gemma-3-4b-it)               | Alternative 4B instruction-tuned candidate | Tested on all three prompts in BF16                                                                                                                               |
| [`OpenLLM-Ro/RoLlama-3.2-1B`](https://huggingface.co/OpenLLM-Ro/RoLlama-3.2-1B)     | Optional Romanian-language reference       | Not tested: access to required `meta-llama/Llama-3.2-1B` base model is pending. It is a 1B base model, so it is not a like-for-like instruction-model comparison. |

I recommend Qwen3-4B-Instruct-2507 as the first QLoRA candidate, subject to a training memory check and team review. My local `Qwen3.5-9B` Q4_K_M GGUF is an additional inference reference only; I did not test it in this Colab run, and it is not the planned Transformers training checkpoint.

## Prompts and Data Handling

I used three prompts from the Evaluation Lead's [`golden_v1_draft.jsonl`](https://github.com/Platinum-Records/llm-project-2026/blob/main/data/eval/golden_v1_draft.jsonl):

| ID      | Task            | Prompt and constraints                                                                                                                   |
| ------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `g-003` | Folk generation | `Scrie o poezie populară despre mama care coace pâine.` Four lines, 7–8 syllables per line, ABAB rhyme, at least 2 regional terms.       |
| `g-004` | Rap generation  | `Scrie o strofă de rap despre întoarcerea acasă, în Ardeal.` Four lines, 12–16 syllables per line, AABB rhyme, at least 1 regional term. |
| `g-001` | Dialect QA      | `Ce înseamnă cuvântul ardelenesc „bade”?` The draft marks this answer as validated.                                                      |

These three draft examples have now been exposed in my smoke tests. I will tell the Evaluation Lead so they can be assigned to development or replaced before the locked-test split is set. I will not use evaluation examples for training or retrieval-corpus construction. The draft dataset is still provisional; I will wait for approved instruction pairs from the Data Lead before any fine-tuning.

## Controlled Inference Run

I repeated all six model/prompt combinations with the same generation settings:

- **Dtype:** BF16
- **Maximum new tokens:** 220
- **Sampling:** disabled (`do_sample=False`)
- **GPU:** Tesla T4, 14.56 GiB available to PyTorch
- **Software:** CUDA 13.0, PyTorch 2.14.1+cu130, Transformers 5.22.2

My setup time includes tokenizer or processor loading and model loading from the active Colab cache. Generation times and memory peaks are per prompt. The allocated/reserved figures below are PyTorch allocator measurements during generation, not whole-process `nvidia-smi` measurements.

| Model                  | Prompt     |    Generated tokens | Generation time | Peak allocated | Peak reserved |
| ---------------------- | ---------- | ------------------: | --------------: | -------------: | ------------: |
| Qwen3-4B-Instruct-2507 | Folk       |                 134 |          9.30 s |       7.54 GiB |      7.55 GiB |
| Qwen3-4B-Instruct-2507 | Rap        |                 139 |          9.06 s |       7.54 GiB |      7.56 GiB |
| Qwen3-4B-Instruct-2507 | Dialect QA | 220 (limit reached) |         14.66 s |       7.55 GiB |      7.56 GiB |
| Gemma 3 4B IT          | Folk       |                  92 |          7.00 s |       8.04 GiB |      8.06 GiB |
| Gemma 3 4B IT          | Rap        |                 126 |          9.96 s |       8.05 GiB |      8.07 GiB |
| Gemma 3 4B IT          | Dialect QA | 220 (limit reached) |         16.88 s |       8.06 GiB |      8.08 GiB |

Setup time was 25.18 seconds for Qwen and 38.10 seconds for Gemma. Both dialect QA generations reached the 220-token limit before finishing.

## Results and Limitations

| Model                  | Folk result                                                                                | Rap result                                                                                                | Dialect QA result                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Qwen3-4B-Instruct-2507 | Four lines, but it missed the constraints and invented meanings for “pădure” and “păsăre.” | Four lines, but it missed the constraints and invented “pădurel” as a regional term.                      | Incorrect clothing-related explanation; generation hit the token limit.            |
| Gemma 3 4B IT          | Four lines, but it missed the meter, rhyme, and regional-vocabulary requirements.          | Four lines, but it missed the syllable/rhyme constraints and supplied an unsupported regional expression. | Incorrect fabricated historical/political meaning; generation hit the token limit. |

I initially loaded Gemma in FP16 and observed NaN logits and pad-token output. I reloaded it in BF16; the logits were finite and it generated readable text. In the controlled run, both Qwen and Gemma used BF16. These six outputs are preliminary smoke-test results, not a full evaluation or evidence of fine-tuning performance.

### Qwen outputs from the controlled run

**Folk (`g-003`):**

```text
Mama coacă pâine cu foc de pădure,
Pâine de măsline, cu zahăr de pădure.
În bucătărie, zâmbete de păsăre,
Când pâinea e fierbinte, e ca un război de pădure.

*(Termeni regionali: „pădure” – folosit ca metaforă pentru foc, „păsăre” – simbol al zâmbetului și bunătății într-un context rural)*
```

**Rap (`g-004`):**

```text
În vârful dealului, pădurea zâmbește,
Călătorii răsfoiesc vechiul pădurel.
Păsări de la vârf, zboară pe deal,
Acasă, în Ardeal, suntem de tot.

*(Termen regional: "pădurel" – expresie locală din Ardeal, folosită pentru o pădure sau loc de pădure, adesea în contexte de tradiție sau vechiă viață rurală.)*
```

**Dialect QA (`g-001`, excerpt; generation reached the token limit):**

```text
Cuvântul **„bade”** din limba **„ardelenescă”** (o variantă a limbii românești din regiunea Ardealului, în special în zona Ardealului de Sud, în apropierea graniței cu România) are un sens **specific local** și **cultural**.

În contextul ardealenc, **„bade”** înseamnă **o formă de a se îmbrăca sau a se îmbrăca într-un mod specific**, adesea în legătură cu **tradiția de a se îmbrăca în timpul unei activități sau a unui eveniment**. Mai precis, **„bade”** poate fi folosit ca **formă de a se îmbrăca într-un mod simplu, deschis, fără prea multă eleganță**, adesea într-un context rural sau tradi
```

### Gemma outputs from the controlled run

**Folk (`g-003`):**

```text
Sigur, iată o poezie populară despre mama care coace pâine, respectând cerințele tale:

În cuptor, focul-i aprins și-ncing,
Cu făină de grâu, un miros divin,
Mama-i la cuptor, cu-a ei rostogolind,
"Pâine-n casă, binecuvântată, fin!"
```

**Rap (`g-004`):**

```text
Sigur, iată o strofă de rap despre întoarcerea acasă în Ardeal, respectând constrângerile tale:

Am plecat departe, prin lume-ntregă am zburat,
Dar sufletul meu-a dorit mereu să mă-ntorc, să-mi găsesc drumul.
Acum văd dealurile, sub soare-n zori,
Și-un "să nu te-nfurți, drace!"-un strigăt bun, de la-n sat, cu pace.
```

**Dialect QA (`g-001`, excerpt; generation reached the token limit):**

```text
Cuvântul ardelenesc "bade" este un cuvânt complex cu o semnificație bogată și nuanțată, care depășește o simplă traducere directă în română. În esență, "bade" se referă la **o stare de spirit, o atitudine, o mentalitate specifică a poporului român din Țara Românească și Transilvania, în special în perioada Războaielor României**.

Iată o descompunere a semnificațiilor și a nuanțelor cuvântului:

* **Rezistență și curaj:** "Bade" implică o rezistență feroce față de dominația străină, în special a Imperiului Otoman. Era o atitudine de a nu se lăsa subjugat, de a lupta pentru libertate și independență.
* **Onor și demnitate:** "Bade" era legat de un puternic sentiment de onoare și dem
```

I have not tested RoLlama because access to its required base model is pending. If access is approved, I can run it as a Romanian-language reference, but I will label it separately because it is a 1B base model rather than an instruction-tuned 4B model.

My Week 7 tests and notes are complete for Qwen and Gemma. My next comparison—testing candidates with and without retrieved context—belongs to Week 8, after the Evaluation Lead publishes the development and locked-test splits.
