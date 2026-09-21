# CredPilot Synthetic Data

Every synthetic lending dataset in CredPilot lives under this folder, one
subfolder per lending product.

| Product | Folder | Applications | Policy documents | Applicant documents | Golden cases |
|---------|--------|--------------|------------------|---------------------|--------------|
| U.S. residential mortgage | [`mortgage/`](mortgage/README.md) | 75 | 42 | 1,140 | 75 |
| Private education loan | [`education/`](education/README.md) | 200 | 12 | 18 | 20 |

Each product folder is self-contained: its own generator, schemas, policy
corpus, applicant documents and golden set, plus its own README and data
dictionary. Start with the product README, not this file.

---

## Why one root with a folder per product

The two datasets model different lending products, and their application
schemas are not compatible. A mortgage packet carries a `borrowers` array and a
`subject_property`; an education packet carries a single `borrower` and a
`school`. Their policy corpora use different identifier taxonomies
(`POL-AST-001` against `POL-001`), and each has its own generator and seed.

Interleaving them in shared `applications/` and `policy_corpus/` folders would
put two incompatible schemas in one directory and force every consumer to
discriminate by filename. Keeping a folder per product means a consumer picks a
product and gets a coherent, internally consistent dataset, while everything
still sits under one root that a retriever or a reviewer can point at.

Adding a third product is a new sibling folder. Nothing existing has to move.

---

## Regenerating

Each product regenerates from committed code and a fixed seed.

Mortgage regeneration is byte-identical: two runs leave `git status` clean.
Education regeneration reproduces every record identically, but
`education/scenarios/scenario_catalog.json` carries a wall-clock `generated_at`
stamp, so that one file differs between runs. That is pre-existing behaviour of
the education generator, not a property of this layout.

```bash
# mortgage
python synthetic_data/mortgage/generator/generate_synthetic_data.py
python synthetic_data/mortgage/generator/validate_synthetic_data.py

# education
python synthetic_data/education/generator/generate_synthetic_data.py
python synthetic_data/education/generator/validate_synthetic_data.py
```

Paths recorded inside the data — `relative_path`, `input_packet`,
`document_folder` — are relative to the repository root and include the product
folder, so `synthetic_data/mortgage/applications/APP-000001.json` resolves from
a clean checkout without any product-specific base path.

---

## Line endings

[`.gitattributes`](.gitattributes) at this root pins every text artifact under
`synthetic_data/` to LF, in the repository and in the working tree, on every
platform. It covers both products, and a new product folder inherits it
automatically.

This matters because the reproducibility guarantee is the headline property
here. Without it, a fresh clone on Windows would check out CRLF, the first
regeneration would rewrite every file back to LF, and `git status` would report
the whole dataset as modified by someone who had done nothing but run the
documented command.

---

## No real data

**No record in either dataset is real, and no policy in them is any real
lender's policy.** Every name, identifier, employer, school and account number
is invented, and taxpayer identifiers are masked. Each product README states
the fictional institution its corpus is attributed to.
