# CredPilot Hackathon Team

Two people built CredPilot: **Krishna Annavaram** and **Mahesh Rajendra**.

## How to read this document

Every claim below is labelled as one of two kinds, and the two are never merged:

**`REPOSITORY-VERIFIED`**
  Something this repository can prove on its own — a commit, a branch, a merge, a
  file, a test. Anyone can check it with the command given.

**`TEAM-ATTESTED`**
  Something the team states and the repository cannot show. Research, reading,
  design discussion, pair working and review conversations leave no commit
  behind.

**The absence of a commit is not the absence of work.** Most of this project's
research was done by Mahesh and is not recorded in Git, because research does not
produce commits. A contribution table built only from `git shortlog` would
describe who typed, not who contributed, and would be wrong about this team in
particular. That is why both categories appear here, and why neither is presented
as the other.

---

## Repository facts both members share

`REPOSITORY-VERIFIED`

```bash
git shortlog -sne --all
```

```
    12  Krishna Annavaram <annavaramkrishna02@gmail.com>
     2  KrishnaAnnavaram <162373752+KrishnaAnnavaram@users.noreply.github.com>
     1  Mahesh Rajendra <rajendramahesh25@gmail.com>
```

Two distinct contributors, three identities: the `users.noreply.github.com`
address is Krishna's GitHub web identity, used when merging pull requests through
the GitHub UI rather than locally.

**Commit window** — `REPOSITORY-VERIFIED`

| | |
|---|---|
| First commit | `10a2ba4` — 2026-09-20 01:08:46 −0500 |
| Last commit | `76a8a6b` — 2026-09-22 08:44:53 −0500 |
| Elapsed wall-clock | **≈ 55.6 hours** |
| Commits | 15 (13 authored + 2 merge commits) |

Elapsed wall-clock is the window work happened inside. It is **not** a measure of
effort and is not offered as one — see [WORKLOG.md](WORKLOG.md).

---

## Krishna Annavaram

**Role:** Co-developer · Primary implementation and integration contributor ·
Internal reviewer of the education synthetic-data work

### Repository-verified contributions

`REPOSITORY-VERIFIED` — each row is checkable with
`git show <commit> --stat`.

| Component | Work performed | Evidence |
|---|---|---|
| Requirements-validation suite | Independent 112-requirement validator, registry, runners, reports | `10a2ba4`, `2df754f` — `requirements_validation_tests/` |
| Mortgage synthetic data | Mortgage data foundation: applications, policy corpus, documents | `a726e31` (1,331 files) — `synthetic_data/mortgage/` |
| Dataset unification | Both products moved under one product-partitioned root | `362355d` (1,591 files) — `synthetic_data/` |
| Agentic RAG + vector retrieval | Retrieval pipeline, fusion, rerank, applicability, citations | `09dc15b` (113 files) — `src/rag/` |
| Evaluation + governance | Agent evaluation subsystem, governance pack | `7cb2ee7` (66 files) — `eval/`, `docs/` |
| Conversational copilot + MCP | Graph, supervisor, MCP server and host, evidence chain | `52aa9ba` (99 files) — `src/graph.py`, `mcp_server/` |
| Evidence gap closure | Findings from the full validator run worked through | `e6a1ba8`, `b566030` |
| Engineering completion report | `docs/COMPLETION_REPORT.md` | `74ac6fd` |
| LangMem + Guardrails-AI | Cross-session memory and the declarative guard layer | `a6a673c` (48 files) — `src/memory/semantic.py`, `src/guardrails/policy_guard.py` |
| Gemini requirements judge | LLM-as-judge harness over the requirements document | `76a8a6b` — `eval/requirements_judge.py` |

**Integration of Mahesh's education dataset** — `REPOSITORY-VERIFIED`

Krishna merged Mahesh's `syn-data-edu` branch through pull request #2
(merge commit `f5126c7`, 2026-09-20 23:25 −0500) and then unified both datasets
under a shared root in `362355d`. A merge is a recorded integration and review
action; the substance of that review is documented in
[EDUCATION_DATA_REVIEW.md](EDUCATION_DATA_REVIEW.md).

### Team-attested contributions

`TEAM-ATTESTED` — stated by the team, not derivable from this repository.

* Shared design and research work with Mahesh throughout, including problem
  framing and technology choices.
* Ongoing discussion of the agent architecture, retrieval strategy and evidence
  model.

---

## Mahesh Rajendra

**Role:** Co-developer · Internal peer reviewer · Education synthetic-data
contributor · Principal research contributor

### Repository-verified contributions

`REPOSITORY-VERIFIED`

```bash
git show f28a1fd --stat
git log --author="rajendramahesh25@gmail.com"
```

| Component | Work performed | Evidence |
|---|---|---|
| Education synthetic data | Seeded generator, 200 applications, policy corpus, applicant document artifacts, 20-case golden evaluation set. All records fictional. | Commit `f28a1fd` — **260 files, 39,470 insertions** |

Commit `f28a1fd`, *"feat: add synthetic education loan origination dataset"*,
authored 2026-09-21 00:04:38 −0400 on branch `syn-data-edu`, merged to `main`
through pull request #2 (`f5126c7`).

That single commit is one of the largest contributions in the repository by
volume, and it is the entire education product line — the second of CredPilot's
two loan products. Everything the education RAG path retrieves, every education
golden case the evaluation scores, and the education half of the product-isolation
guarantees rest on data Mahesh generated.

The commit also carries `Co-authored-by: Cursor <cursoragent@cursor.com>`. An
assistant was used during development, which this project discloses throughout
rather than hiding.

### Team-attested contributions

`TEAM-ATTESTED` — stated by the team, not derivable from this repository. **These
are not lesser contributions; they are contributions Git cannot record.**

* **The majority of the project's research.** Domain reading on loan origination
  and underwriting, lending-policy structure, agentic architecture patterns and
  evaluation approaches. This is the largest single body of work not represented
  in the commit history.
* **Internal peer review** of project and code work across the build — see
  [PEER_REVIEW.md](PEER_REVIEW.md).
* **Collaborative development** with Krishna: the two worked together on the
  project rather than dividing it into separate, independently committed halves,
  which is why commit counts do not reflect the split of effort.

---

## Education synthetic-data ownership

Recorded here because the two roles are deliberately separated, and because the
reviewer is not the author:

| | |
|---|---|
| **Contributor / developer** | **Mahesh Rajendra** — `REPOSITORY-VERIFIED` (`f28a1fd`) |
| **Internal reviewer** | **Krishna Annavaram** — `REPOSITORY-VERIFIED` merge (`f5126c7`), review substance `TEAM-ATTESTED` |

Detail in [EDUCATION_DATA_REVIEW.md](EDUCATION_DATA_REVIEW.md).

---

## What this document does not claim

* It does not convert any `TEAM-ATTESTED` row into a `REPOSITORY-VERIFIED` one.
* It does not use commit counts or line counts as a measure of contribution.
  Krishna has more commits; the team states Mahesh did most of the research.
  Both statements are true at once, and only the first is visible in Git.
* It does not describe either member as an official Virtusa hackathon evaluator.
  Mahesh's review role is **internal peer review within the delivery team**.
