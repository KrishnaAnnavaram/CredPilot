# Third-party licences

Generated 2026-09-22T15:05:10Z by 
[`scripts/build_dependency_licenses.py`](../scripts/build_dependency_licenses.py) 
from the installed distributions' own metadata. Machine-readable form: 
[`reports/dependency_licenses.json`](../reports/dependency_licenses.json).

```bash
python scripts/build_dependency_licenses.py
```


## Two different questions

This document answers exactly one of them:

| | |
|---|---|
| **A — CredPilot's own licence** | Not addressed here. Whether this repository carries a licence, and which, is a Virtusa policy question. No project `LICENSE` was added or changed to satisfy a requirement. |
| **B — the licence of each dependency** | **This document.** Read from installed package metadata. |

The requirements document's stack row says *"Python 3.11+ · LangGraph (MIT)"*. That is a claim of kind **B**, and it is checkable.


## LangGraph — the one the source names

| Field | Value |
|---|---|
| Package | `langgraph` |
| Version | `1.2.11` |
| **Resolved licence** | **MIT** |
| Evidence source | License-Expression (PEP 639) |
| Trove classifiers | — |

Reproduce it directly:

```python
from importlib import metadata
d = metadata.distribution("langgraph")
print(d.version, d.metadata.get("License-Expression"),
      d.metadata.get_all("Classifier"))
```

The source document's description of LangGraph as MIT is therefore **confirmed against the installed package**, not taken on trust.


## Why this does not close REQ-035

`REQ-035-T03` asks for *"any licence artifact the implementation must carry to evidence LangGraph's MIT licence"*. The source document names the licence in a stack table and **places no obligation on this repository to carry any licence artifact** — so there is no artifact for the check to look for, and it is registered as `UNSPECIFIED_BY_REQUIREMENT`.

Adding this file is the right thing to do on the merits and does not change that. The validator was not modified to accept it, because the check is not wrong: the specification really is silent. See [`requirements_validation_tests/reports/unverifiable_requirements.md`](../requirements_validation_tests/reports/unverifiable_requirements.md).


## Every declared runtime dependency

33 distributions declared in `requirements.txt`, 33 with readable licence metadata.

| Package | Version | Licence | Evidence source |
| --- | --- | --- | --- |
| `arize-phoenix` | 11.38.0 | Elastic-2.0 | License field |
| `arize-phoenix-evals` | 2.13.0 | Elastic-2.0 | License field |
| `arize-phoenix-otel` | 0.17.1 | Apache-2.0 | License field |
| `chromadb` | 1.5.9 | Apache Software License | Trove classifier |
| `deepeval` | 4.2.3 | Apache Software License | Trove classifier |
| `fastapi` | 0.141.1 | MIT | License-Expression (PEP 639) |
| `guardrails-ai` | 0.11.0 | Apache Software License | Trove classifier |
| `langchain-core` | 1.6.2 | MIT License | Trove classifier |
| `langchain-google-genai` | 4.4.0 | MIT | License field |
| `langchain-mcp-adapters` | 0.3.2+subro.sync.1 | MIT | License-Expression (PEP 639) |
| `langgraph` | 1.2.11 | MIT | License-Expression (PEP 639) |
| `langgraph-checkpoint-sqlite` | 3.1.1 | MIT | License-Expression (PEP 639) |
| `langmem` | 0.0.30 | (full licence text embedded in metadata) | License field (full text) |
| `matplotlib` | 3.11.2 | Python Software Foundation License | Trove classifier |
| `mcp` | 1.30.0 | MIT License | Trove classifier |
| `numpy` | 2.4.2 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | License-Expression (PEP 639) |
| `openinference-instrumentation-langchain` | 0.1.76 | Apache-2.0 | License-Expression (PEP 639) |
| `opentelemetry-exporter-otlp-proto-http` | 1.44.0 | Apache-2.0 | License-Expression (PEP 639) |
| `opentelemetry-sdk` | 1.44.0 | Apache-2.0 | License-Expression (PEP 639) |
| `pandas` | 2.3.3 | BSD License | Trove classifier |
| `presidio_analyzer` | 2.2.361 | MIT | License-Expression (PEP 639) |
| `presidio_anonymizer` | 2.2.361 | MIT | License-Expression (PEP 639) |
| `pydantic` | 2.12.5 | MIT | License-Expression (PEP 639) |
| `pytest` | 9.0.2 | MIT | License-Expression (PEP 639) |
| `pytest-asyncio` | 1.3.0 | Apache-2.0 | License-Expression (PEP 639) |
| `python-dotenv` | 1.2.2 | BSD-3-Clause | License field |
| `PyYAML` | 6.0.3 | MIT License | Trove classifier |
| `rank-bm25` | 0.2.2 | Apache2.0 | License field |
| `sentence-transformers` | 6.0.1 | Apache-2.0 | License-Expression (PEP 639) |
| `starlette` | 0.52.1 | BSD-3-Clause | License-Expression (PEP 639) |
| `torch` | 2.14.0 | Apache-2.0 AND Apache-2.0 WITH LLVM-exception AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND MIT | License-Expression (PEP 639) |
| `transformers` | 5.17.0 | Apache 2.0 License | License field |
| `uvicorn` | 0.51.0 | BSD-3-Clause | License-Expression (PEP 639) |

## Scope

Direct dependencies declared in `requirements.txt` only. Transitive dependencies are not enumerated: the list would run to several hundred packages and none of them is named by the requirements document.

