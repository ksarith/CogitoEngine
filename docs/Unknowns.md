# Unknowns

Open questions are not allowed to be buried. An unknown may only be closed
with evidence, and a closed unknown that reopens is logged again rather than
quietly ignored.

| ID | Unknown | Status |
|----|---------|--------|
| CE-U01 | Does a declared role actually constrain model behavior, or is the role contract decorative? | Open — needs adversarial transcript review |
| CE-U02 | Sequential same-model agents echo each other; is a flow of one model any kind of independent review? | Open — mirrors the Forge's "three sessions are not three witnesses" gap |
| CE-U03 | What is the minimum flow that beats a single well-prompted model on real tasks? | Open — no benchmark yet attempted |
| CE-U04 | Notebook context grows unbounded; at what length does it degrade later steps? | Open — unmeasured |
| CE-U05 | Refusal detection is a string prefix; how often do models refuse without the marker? | Open — unmeasured |

Closing rule: to close an unknown, file an issue with a transcript and the
evidence classification (Measured / Replicated / Simulated / Analogous /
Placeholder). "It seems fine" is not a classification.
