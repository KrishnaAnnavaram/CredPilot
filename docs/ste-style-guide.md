# The writing standard: ASD-STE100 Simplified Technical English

Use these rules for every README and for `docs/ste-style-guide.md` in each repository. Copy this file
into the repository as `docs/ste-style-guide.md` and add a **project vocabulary** section (Section 3)
with the technical names and technical verbs of that project.

## 1. The writing rules

### Words

1. Use one word for one meaning, and one meaning for one word. Do not use synonyms for variety.
2. Use a word only as one part of speech. For example, `test` is a noun or a verb, `check` is a verb.
3. Do not use phrasal verbs (`set up`, `carry out`, `find out`, `pick up`, `look up`, `come up with`).
   Use one verb: `prepare`, `do`, `find`, `get`, `make`.
4. Do not use an `-ing` form as a noun or an adjective (`the running job`, `after indexing`).
   Exception: a technical name, a file name, a command or a status value.
5. Do not use contractions (`don't`, `it's`, `can't`). Do not use slang or idioms
   (`out of the box`, `under the hood`, `at a glance`, `gotcha`, `bells and whistles`).
6. Do not use `and/or`. Write `A, B or both`.
7. Do not use `should`, `could`, `would` or `may` for instructions. Use `must` for a rule, the
   imperative for a step and `can` for a possibility.
8. Keep the articles `a`, `an` and `the` in sentences.
9. Do not make a noun cluster of more than three words. A technical name is one word.

### Sentences

1. A procedural sentence (an instruction) has a maximum of **20 words**.
2. A descriptive sentence has a maximum of **25 words**.
3. Write one instruction in one sentence.
4. Use the imperative for an instruction: `Run the tests.` Not `The tests should be run.`
5. Use the active voice. Use the passive voice only when the agent of the action is not important.
6. Use only the simple present, the simple past and the simple future.
7. Put a condition before the instruction: `If the index is stale, build it again.`
8. Do not use semicolons in sentences. Write two sentences.

### Paragraphs, notes and warnings

1. A paragraph has one topic and a maximum of **6 sentences**. Start with the topic sentence.
2. A warning or a caution starts with a clear command. Then it gives the reason.
3. A note gives information. It does not give an instruction.
4. Use a vertical list for a sequence or a set of conditions. Each item of a numbered procedure is one step.

### Tables, headings and diagrams

1. A table cell can be a short phrase. If a cell has a sentence, the sentence obeys the rules.
2. A heading is a noun phrase (`The cost model`) or an imperative (`Run the demo`).
   Do not start a heading with an `-ing` form.
3. A diagram label is a short phrase. Use the same terms as the text.

### What STE does not change

Code, commands, file names, paths, field names, environment variables, status values, enum values,
product names and URLs stay exactly as they are. They are technical names. Put them in backticks.

## 2. General words to replace

| Do not use | Use |
|---|---|
| utilize, leverage | use |
| in order to | to |
| set up | prepare, install, configure |
| carry out, perform | do |
| make sure, ensure | make sure (allowed), or `check that` |
| a lot of, lots of | many, much |
| e.g., i.e. | for example, that is |
| should (instruction) | must (rule) / imperative (step) |
| might, may (possibility) | can |
| very, really, just, simply, easily | (delete) |
| seamless, robust, powerful, blazing | (delete or give a measured fact) |


## 3. Project vocabulary

This section gives the technical names and the technical verbs of CredPilot. The README uses each term with only this meaning.

### 3.1 Technical names (nouns)

| Term | Meaning | Do not use |
|---|---|---|
| **product** | One lending product: `MORTGAGE` or `EDUCATION_LOAN` | line of business, vertical |
| **application** | One loan application file, one JSON packet in `synthetic_data/<product>/applications/` | case (except "golden case"), loan file, request |
| **application packet** | The JSON content of one application, after `build_underwriting_input` adds the input tables | payload, record |
| **policy document** | One Markdown file in `synthetic_data/<product>/policy_corpus/` | policy file, manual |
| **policy version** | One published version of a policy document, for example `POL-DTI-001 v2.0` | revision, edition |
| **rule** | One identified requirement in a policy document, for example `DTI-CONV-001` | clause, criterion |
| **rule family** | The rules that share a prefix, for example `DTI-CONV` | rule group, category |
| **corpus** | All policy documents of one product | knowledge base, library |
| **chunk** | One retrieval unit: a rule with its parameters, a section or a document overview | passage, snippet, fragment |
| **collection** | One Chroma collection. Each product has one collection | index (for Chroma), namespace |
| **evidence** | The chunks that retrieval returns, each with a citation | context, sources |
| **citation** | The text that points to one rule, section or document, for example `POL-DTI-001 v2.0 rule DTI-CONV-001` | reference, source link |
| **as-of date** | The underwriting date that selects the governing policy version | decision date, run date |
| **governing version** | The policy version in force on the as-of date | current version, latest version |
| **domain router** | The graph node that resolves the product from structured facts | classifier, dispatcher |
| **node** | One step of the LangGraph | stage (for the graph), task |
| **figure** | One number that `src/calculations.py` calculates, for example `back_end_dti` | value, metric (for underwriting) |
| **threshold** | A limit that the rule engine reads from a retrieved rule, for example 43 % | cutoff, limit value |
| **rule engine** | `src/rules.py`, which applies thresholds to figures | decision engine, scorer |
| **verdict** | The result of one rule evaluation: `PASS`, `FAIL`, `INDETERMINATE` or `NOT_APPLICABLE` | result (for a rule) |
| **eligibility status** | `ELIGIBLE`, `INELIGIBLE` or `INDETERMINATE` for one application | eligibility outcome |
| **recommendation** | `APPROVE_RECOMMENDATION`, `REFER_RECOMMENDATION` or `DECLINE_RECOMMENDATION` | decision, verdict |
| **review trigger** | A condition of `UWR-HRV-001` or `EDU-GOV-002` that sends an application to a human | alert, flag (for review) |
| **risk flag** | One flag of the risk screen, for example `OFAC_HIT` | alert |
| **rationale** | The text that Gemini writes to explain a recommendation | narrative (except the node name `narrative`), summary |
| **untrusted text** | Text that the applicant supplied, in `untrusted_applicant_text` | user input, free text |
| **golden case** | One expected result in `golden_set/` that the evaluation compares with | label, ground truth |
| **step budget** | The maximum number of node runs in one assessment (24) | quota, limit |

### 3.2 Technical verbs

| Verb | Meaning |
|---|---|
| **assess** | Run one application through the full graph |
| **route** | Select the next node, or send an application to `human_review` |
| **resolve** | Find the product of an application, or find the source of a citation |
| **retrieve** | Get evidence from one collection for one question |
| **index** | Build the Chroma collections and the BM25 indexes from the corpus |
| **fuse** | Join the BM25 ranking and the dense ranking with reciprocal rank fusion |
| **rerank** | Sort the fused candidates again with the cross-encoder |
| **calculate** | Make a figure from the application packet, with no model |
| **evaluate** | Apply a threshold to a figure and give a verdict, or score the system against golden cases |
| **quarantine** | Put untrusted text in its own compartment and record each injection finding |
| **redact** | Replace an identifier with a placeholder before the text is written |
| **verify** | Check each citation and each figure of a rationale against its evidence |
| **trace** | Write OpenTelemetry spans for a run |
