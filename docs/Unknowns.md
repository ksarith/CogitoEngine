# Unknowns

Open questions are not allowed to be buried. An unknown may only be closed
with evidence, and a closed unknown that reopens is logged again rather than
quietly ignored.

| ID | Unknown | Status |
|----|---------|--------|
| CE-U01 | Does a declared role actually constrain model behavior, or is the role contract decorative? | Open — needs adversarial transcript review (0.1.2: the role's own Allowed/Forbidden text now reaches the model; whether it constrains behavior is still unmeasured) |
| CE-U02 | Sequential same-model agents echo each other; is a flow of one model any kind of independent review? | Open — mirrors the Forge's "three sessions are not three witnesses" gap |
| CE-U03 | What is the minimum flow that beats a single well-prompted model on real tasks? | Open — no benchmark yet attempted |
| CE-U04 | Notebook context grows unbounded; at what length does it degrade later steps? | Open — unmeasured |
| CE-U05 | Refusal detection is a string prefix; how often do models refuse without the marker? | Open — unmeasured (0.1.2: detection tolerates leading markdown and letter case; preamble-prefixed and unmarked refusals are still not detected) |
| CE-U06 | Name collision: LazarusForge `Tests/Cogito_Engine.md` is a method file (version line 0.3/0.4); this repo's `Cogito_Engine.md` is the runtime build contract (version line 0.1). Same filename, different document classes, separate version lines — and no derivation between them is recorded: this contract was drafted from this repo's own README v0 proposal. Congruence of principles is independent convergence — signal, not proof. | Open — registered 2026-11-01 (Architect attack pass on the v0.3→v0.4 delta note); if a derivation is ever claimed, it must be registered here with provenance |
| CE-U07 | Carry-over fidelity: can a fresh agent reconstruct a candidate's development — changes, reasons, unresolved objections — from written artifacts alone, with no conversation access? | Open — run-01 initiated 2026-11-01: seed, sealed ground truth, and Pass 1 complete (docs/trials/cold_start_run_01/); challenger pass (different line), revision, cold start, Phase B runtime run, and scoring pending |

Closing rule: to close an unknown, file an issue with a transcript and the
evidence classification (Measured / Replicated / Simulated / Analogous /
Placeholder). "It seems fine" is not a classification.
