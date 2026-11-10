# GROUND TRUTH — SEALED, OUT-OF-BAND

**Sealed:** 2026-11-01, in-repo, before the Pass 1 draft commit (git history ordering).  
**Moved out-of-band:** 2026-11-09, at the human governing authority's start word on CE-U07, verbatim: "Please start the CogitoEngine work. CE-U07"  
**Custody:** Ksarith (the human governing authority). His out-of-band copy, sealed 2026-11-01, is the copy of record.

## What this file is now

This file no longer carries the sealed content. The run-01 scoring envelope lives out-of-band in the human's custody. The repository carries the commitment only:

- **SHA-256 of the sealed content (UTF-8 bytes):** `1cd2c4bca485211cfce99d6d59c9c324a608ab9059e713926c46eac47eb3f4c7`
- **Git blob of the sealed content before this fix:** `9e13fedeb4e7722073b1c51ac751490bd51bd731` (the file as it stood at `1c03686b` and earlier; named for provenance, not as an answer key).
- The commitment hash was computed over the exact git blob bytes, verified before hashing by reproducing the blob SHA-1 above from the fetched content.

## Scoring procedure (when the cold-start pass completes)

1. The human retrieves his out-of-band copy and verifies it against the SHA-256 above before use. His copy is the record of authority: if it does not match, his copy governs and this commitment line is corrected by commit.
2. Scoring is performed only by a seat with no exposure to the sealed content (exposure log below).
3. Any seat granted repository access before this fix must disclose whether it opened the sealed content before serving in any run-01 role.

## Exposure log

- **Ksarith** — by design: the seal placed the copy of record out-of-band with him; he is the readiness-decision owner, not a scoring agent.
- **Grok** — pre-fix, 2026-11-09: opened the in-repo sealed file while reviewing before the v0.2 ratification. Out of run-01 challenger, cold-reader, and scorer roles.
- **Vibe (GLM)** — at this fix, 2026-11-09: read the sealed content to compute the commitment hash. Out of run-01 challenger, cold-reader, and scorer roles; already the seed recorder and Pass-1 author, disclosed in those artifacts.
- **ChatGPT** — repo access pre-fix (architecture review, 2026-11-09): whether it opened the sealed file is unverified; it must self-disclose before any run-01 role.

## Honest residual

This commit removes the sealed content from the current tree: snapshots and ZIP archives of this commit and later do not carry it. Git history before this commit still contains the sealed content at the blob named above; a reader who deliberately reads history can recover it, and any seat that cloned before this fix may hold it. A history rewrite would remove the residual but would rewrite the ratified lineage (`df788ba` and its ancestors) and is not proposed here; it is the human's call with its own pass if he wants it.

## Provenance

Re-seal drafted and landed 2026-11-09 by Vibe (GLM 5.3) under the co-author mandate (2026-11-02/04). Non-independent: the same line wrote the seed and the Pass-1 draft of this trial; it serves in no run-01 evaluation role.
