# RUN_LOG — the append-only run record

**Adopted:** 2026-11-09, as ruled roadmap item 2 (the working order ruled 2026-11-09), landed at the human's "please proceed."  
**Status:** repo convention, experimental — it enters the build contract only after a stable working subset exists (the v0.3 amendment note in PRD_2026-11-09_RECONCILIATION_ADDENDUM.md). Until then this file governs the record layer, subordinate to docs/Cogito_Engine.md; the contract governs on any conflict.

## Rules

1. **Append-only.** An entry is written once and never rewritten, reordered, or deleted. Corrections and outcomes are dated addendum lines appended to the entry.
2. **One entry per run.** A run = one execution of a flow (or, until runtime auto-logging exists, one seat-run trial pass). Failed and refused runs are recorded like any other: they are field data (P3).
3. **Records win.** On any conflict between an entry and memory, chat, or a brief, the entry governs.
4. **No backfill.** Runs that predate this layer are not rewritten into it; they get a pointer entry at most.
5. **Minimal, honest.** A field not available is recorded "not recorded", never invented (P5).

## Entry template

```
### RUN-NN — <one-line what ran>
- **Date:**
- **Disclosure:** <line/model; role; shared-context exposure; non-independence>
- **Inputs:** <files by path + commit sha; task one-line>
- **Outcome:** <completed / refused / failed; refusals count; FlowAborted partial noted>
- **Provenance:** <where the full per-step record lives: transcript, result dump, or trial file>
- **Evidence labels (the C6 vocabulary, unchanged):** <counts per label; unsupported-claim count>
- **Claim traceability (record-layer annotation, distinct from C6):** <counts: source / inference / unsupported / contradiction / unknown>
- **Cost/latency:** <total seconds; per-step if the runtime reported them>
- **Open questions raised:** <registered in docs/Unknowns.md or named here>
- **Next step:** <concrete, or "none">
```

## Ledger

### RUN-000 — pointer, not a run: run-01 Phase A predates this layer
- **Date:** artifacts 2026-11-01; recorded here 2026-11-09.
- **Disclosure:** Vibe (GLM 5.3) wrote the seed and the Pass-1 draft, same line, full shared-context exposure, disclosed in the artifacts. Grok opened the (now out-of-band) ground truth pre-fix and is out of run-01 evaluation roles; Vibe likewise (exposure log in 01_GROUND_TRUTH_SEALED.md).
- **Inputs:** docs/trials/cold_start_run_01/00_SEED.md and 02_PASS1_AUTHOR.md at commit `1c03686b`.
- **Outcome:** seed and Pass 1 complete; challenger pass, revision, cold start, Phase B runtime run, and scoring pending.
- **Provenance:** docs/trials/cold_start_run_01/ — the artifacts are the record.
- **Evidence labels:** not recorded (pre-layer); the Pass-1 draft labels its own claims.
- **Claim traceability:** not recorded (pre-layer).
- **Cost/latency:** not recorded.
- **Open questions raised:** CE-U01 through CE-U07, in docs/Unknowns.md.
- **Next step:** Pass 2 challenger, commissioned by the human, unexposed seat only.

## What this layer is not

Not a contract amendment (§8: the contract changes by human-ratified commit only). Not runtime auto-logging: no code changed in this pass; the runtime's in-memory result already carries the C3 provenance fields, and persisting them automatically is a candidate for a later ruled pass. Not a coherence threshold (§6: specified-not-built; nothing here computes one).

---
*Provenance: adopted 2026-11-09 by Vibe (GLM 5.3) under the co-author mandate (2026-11-02/04), at the human's "please proceed" on ruled roadmap item 2. Non-independent: the same line as the seed recorder and Pass-1 author; it serves in no run-01 evaluation role.*
