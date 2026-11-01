# Pass 1 — Author Draft + Delta Note — Ice-Harvest Bench v0.1

**Author:** Vibe (GLM 5.3)  
**Date:** 2026-11-01  
**Disclosure (method v0.4 P5):** same line as the seed recorder, same session, full shared-context exposure. Non-independent, disclosed.  
**Draft identity:** Ice-Harvest Bench design doc, v0.1 draft (this file, section below).

---

## First draft — Ice-Harvest Bench v0.1

### Concept

A batch-mode **carousel bake-out bench**: an insulated carousel of six sample cells holds ice-doped granular analog; each cell rotates into a heated bake-out position, drives off water vapor, which is condensed on a cold finger and collected in a sealed vial per batch. One cell bakes while the next charges; excavation of the analog into cells is by hand auger. All control is by thermostat and multimeter — no software required.

### Mass/energy budget table (first-pass figures)

| Subsystem | Power (W) | Mass (kg, est.) | Salvage source | Evidence label |
|---|---|---|---|---|
| Excavation (hand auger, powered feed) | 80 | 2 | Salvaged hand drill | Placeholder |
| Bake-out heaters (cartridge elements, 6 cells) | 300 | 1.5 | Salvaged toaster-oven / cartridge heaters | Placeholder |
| Condenser (mini-fridge compressor loop, cold finger) | 100 | 8 | Salvaged dorm mini-fridge | Placeholder |
| Carousel drive (gearmotor) | 20 | 3 | Salvaged washing-machine motor | Placeholder |
| **Total** | **500** | **14.5** | — | — |

### Salvage gate map

| Component | Function preserved? | Gate reached |
|---|---|---|
| Hand drill | Yes — rotary drive reused as-is | Function |
| Toaster-oven elements | Yes — resistive heating reused | Component |
| Mini-fridge | Partially — compressor loop reused, cabinet cut for the cold finger | Assembly |
| Gearmotor | Yes — geared rotary drive reused | Component |

### Top three failure modes

1. **Thermal leak at the condenser stage** — the cold finger fights the same cold the heaters just paid to move; if the loop loses, the water re-vents.
2. **Fines migration** — analog dust into bearings, seals, and heater contacts.
3. **Ledger drift** — the hand ledger is abandoned once the experiment gets interesting; budgets silently rot.

### Evidence labels

All budget figures are **Placeholder** (nothing has been measured). The overall bench concept is **Analogous** (to documented ISRU bench extraction generally). No Measured or Replicated claims are made.

### Open unknowns

- Transfer validity: what ambient-pressure, terrestrial-mineralogy results say about real cold traps.
- Whether 500 W closes thermally with the dorm-fridge loop at the required cold-finger temperature.
- Real excavation energy of the chosen analog.

---

## Delta note (seed -> v0.1 draft) — method v0.4 P2 minimum delta record

**(a) Draft identity reviewed:** Seed Note — Ice-Harvest Bench (00_SEED.md), 2026-11-01.

**(b) What changed, and the trigger:**
- Added a concrete architecture (carousel bake-out) — trigger: the seed bounded the problem but named no mechanism.
- Added a concrete 500 W power split across four subsystems — trigger: seed constraint 1 requires the budget to be visible.
- Added a salvage gate map — trigger: seed constraint 2.
- Named three failure modes — trigger: seed constraint 5.

**(c) Kept / changed / dropped / unresolved:**
- Kept: the 100 g/day-equivalent target, the 500 W cap, hand-ledger requirement, evidence-label requirement, all seed constraints.
- Changed: "design problem, not a build commitment" developed into a specific batch architecture.
- Dropped: nothing.
- Unresolved: all seed unknowns remain; none were closed by drafting.

**(d) Claim classes of each material claim (method vocabulary):**
- Carousel concept, power split, masses, salvage sources: **assumed**.
- Failure-mode set (thermal leak, fines, ledger drift): **inferred** from general bench practice.
- Nothing is **observed** — no measurement has occurred. No claim is **unknown**-class here; the unobserved status is recorded in (c) as unresolved.

**(e) Next review step:** Pass 2 — challenger agent, different line, attack pass on this draft, disposition recorded per v0.4 P5. Readiness decision remains owned by the human.
