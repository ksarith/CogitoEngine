# PROPOSAL 2026-11-14 — Peer mode (CE-U09 / CE-U08) and a two-way bridge to Idea Generator 2

**Deposited:** 2026-11-14, `docs/proposals/`.  
**Routing act:** the human governing authority's 2026-11-14 instruction, verbatim: "Let's go with the two-way bridge. But can we chase the role reduction and treating agents more openly and as peers for CogitoEngine if we could."  
**Status:** PROPOSED, experimental. Drafted by Claude, Class A, unratified. The build contract (`docs/Cogito_Engine.md` v0.2) is unchanged; `cogito/__init__.py`, `Flow`, `Agent` and the YAML flow key set are untouched; the conformance declaration stands. Both additions are experimental and **unconformant** under contract §8. No unknown is closed or reworded by this deposit.

## 1. What is added (new files only)

- `cogito/peer.py` — a separate flow type: peer seats, typed side-notes, dispositions, certifier seats. Own strict YAML format (`examples/flows/peer_cluster.yaml`); not loadable by `cogito run`.
- `cogito/ideagen_bridge.py` — stdlib HTTP bridge to a running Idea Generator 2 (loopback API). The bridge itself changes nothing in the idea generator; the optional patch in §7 does. Includes `vet-one` (§7).
- `tests/test_peer_and_bridge.py` — offline mechanics tests (fake LLM, fake idea-generator server).

## 2. Peer mode: which limits are open, which are enforced

CE-U09 separates *capability* limits (who may say what) from *independence* limits (who may judge what). Peer mode opens the first and enforces the second **in code, not in prompt**:

| Open (any seat) | Enforced by the runtime |
|---|---|
| object, counter-propose, add evidence, ask, as typed notes with provenance | a seat's disposition on its own note is ignored (`accepted: false`, flagged) |
| disagree with or improve on any earlier seat | evidence labels (C6 vocabulary, unchanged) count only from `certifies: true` seats, never for the certifier's own contributions |
| refuse with `[REFUSAL]` (still first-class; `stop_on_refusal` per seat) | a note nobody dispositioned stays `open` and is flagged `undisposed:<id>` on the seat that owed it; nothing blocks, nothing is hidden |

Rejected markers, bad labels and malformed notes stay in the record. Raw seat output is kept verbatim (P4). `family` per seat is **declared by the human and not verified**; the result carries a non-independence warning when every seat is one family or any is undisclosed (CE-U02). The cluster is sequential (parallel fan-out is specified, not built, §5).

## 3. The bridge, and the rules that answer its risks

- **Forward (`vet`):** judged ideas at or above a medal threshold (default silver; thresholds mirror the idea generator's `score.js`) are run through a Cogito arm (`peer`, `strict`, or `both`); full JSON and Markdown records are written, optionally into the project folder (`COGITO_VETTING.md`, never overwriting).
- **Back (`feed`):** `counter-proposal` notes from a *peer* run are posted to a board as new seeds. The board's own jury judges them like any other idea.
- **Cogito never writes fitness.** The idea generator's medal is computed in code from its own jury; the bridge only adds material to the pool. A Skeptic verdict does not enter breeding, so evolution cannot learn the Skeptic's wording (Goodhart). Verdicts stay in the run record.
- **Jury withheld by default.** Showing the jury's scores to seats anchors them (CE-U02). `--show-jury` is opt-in and recorded in the run.
- **Bounded:** no daemon; `--max-ideas`; a depth guard (`--max-depth`, default 2) stops Cogito-seeded ideas from being re-vetted and re-seeded indefinitely; `--dry-run` prints the selection and an LLM-call estimate first.
- **Refusal is a valid result:** a refused run is recorded in full and feeds nothing back unless `--feed-refused`. An aborted run is recorded but not marked vetted, so it retries.
- **Untrusted text:** idea text can come from visitors (exhibition mode) or models; it is passed to seats as quoted data. The bridge refuses a non-loopback idea-generator URL without `--allow-remote`.

## 4. How CE-U09 could actually be measured (not done)

Same seeds, two arms: `--arm strict` (the default cognitive flow, contract roles) versus `--arm peer`, via `--arm both`. Counting what arm (a) lost and arm (b) added needs a **scoring rule against ground truth sealed before the run**; the bridge supplies neither. The idea generator's calibration set (`tools/calibrate-judge.ts`: bare-topic weak ideas such as "fire", concrete strong ones) is a candidate seed set with a known weak/strong split, but it grades the *jury*, and a flow record has no numeric score. Any code-computed readout (for example unresolved-note and Placeholder-label counts per record) is itself an unvalidated metric and would have to be registered as such. CE-U09 also depends on CE-U01: if roles do not measurably constrain behavior, the limits cost nothing and this experiment is moot.

## 5. Not demonstrated

- 38 offline tests pass (the 9 existing plus 29 new). They cover mechanics only: parsing, the code-enforced limits, ledger, selection, feed rules, HTTP error paths.
- No live model has run a peer flow. The bridge has been exercised only against a fake idea-generator server, not a live instance. Whether models emit the note/disposition/label markers reliably is unmeasured; the runtime records every miss as a flag rather than assuming compliance.
- Seeds longer than 160 characters are rewritten by the receiving board's distill step, so seeded wording is the board's, not the seat's; the seat's original note stays in the run record and the ledger links note to seeded idea.

## 6. Rulings owed

1. Keep peer mode experimental and out of the contract until CE-U09 has evidence (recommended), or open an amendment draft now.
2. Whether `family` and the non-independence warning should be proposed for the contract's disclosure language (currently the experimental `disclosure` key carries free-form text).
3. Which sealed ground truth and scoring rule a CE-U09 trial uses (CE-U07 run-01 or a fresh seed).

## 7. Addendum (same day): `vet-one` and an optional idea-generator patch

On the governing authority's "Yes please" to adding a way for the idea generator to call Cogito, two things were added.

- **`vet-one --stdin` (this repo):** reads one idea as JSON on stdin, runs the chosen arm(s), prints run records as JSON on stdout. Pure: no HTTP, no ledger, no files; errors go to stderr. A provider failure is an `aborted` run record, not a crash.
- **A separate patch to Idea Generator 2** (shipped as its own zip; a fork of an MIT project, new files plus small edits): a "Vet with Cogito" button on the idea card, run via `server/cogito.ts` (spawns `vet-one`, keys passed in the child's environment only) and `server/vetting.ts` (a `vettings` table, SSE updates, a dialog showing refusals, open notes and counter-proposals). Off unless `COGITO_DIR` is set.

Rules carried over and made structural: Cogito never writes fitness (the patch touches no score, medal, jury or autopilot code); counter-proposals become seeds only when a person picks one; no pass/fail badge, only flags and open questions; jury score hidden from seats unless opted in; Cogito's cost is invisible to the idea generator's dollar budget, so a per-day run cap (`COGITO_MAX_RUNS_PER_DAY`, default 10, counted per arm, failed runs included) is the only brake.

Verification: 15 new Node tests with a faked Cogito and fake command-line children, plus a manual end-to-end pass (real Node server and runner, real `vet-one`, fake OpenAI-compatible provider on localhost). Not verified: any live model, and the browser UI (checked for syntax and string keys only; no DOM test exists in that repo).
