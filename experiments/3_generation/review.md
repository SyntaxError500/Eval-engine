# Phase 3: generated question review

5 questions. For each one, tick every item that holds. The gate passes when at least 85% of questions pass every item that applies to them.

Checklist per question:

1. Task type is right for the question
2. Question is self-contained and answerable in a short paragraph
3. Every criterion is binary and observable
4. Criteria ask for nothing the question doesn't need
5. Criteria don't leak a model sentence to copy
6. Granular enough that a partial answer can meet some criteria
7. Each path is a complete alternative answer, not a part the question requires together with the other paths (analytical / explanatory only)
8. The question's premise and the rubric's facts are correct

## 1. factual · science · `512f892a6afa`

**Q:** Name three distinct phases of the cell cycle and give one key event that occurs in each phase. Answer in a short paragraph (3‑8 sentences).

**Path P1:** Provides three distinct cell‑cycle phases each paired with a correct key event.

- `P1.C1` correctness, core, w=1: Names a valid cell‑cycle phase (e.g., G1, S, G2, or M). ← asked by: "Name three distinct phases of the cell cycle"
- `P1.C2` correctness, core, w=1: Provides a correct key event that occurs in the phase named in C1. ← asked by: "give one key event that occurs in each phase"
- `P1.C3` correctness, core, w=1: Names a second valid cell‑cycle phase (e.g., G1, S, G2, or M). ← asked by: "Name three distinct phases of the cell cycle"
- `P1.C4` correctness, core, w=1: Provides a correct key event that occurs in the phase named in C3. ← asked by: "give one key event that occurs in each phase"
- `P1.C5` correctness, core, w=1: Names a third valid cell‑cycle phase (e.g., G1, S, G2, or M). ← asked by: "Name three distinct phases of the cell cycle"
- `P1.C6` correctness, core, w=1: Provides a correct key event that occurs in the phase named in C5. ← asked by: "give one key event that occurs in each phase"
- `P1.C7` completeness, core, w=0.5: The three phases named are all different from each other. ← asked by: "Name three distinct phases of the cell cycle"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 2. factual · technology · `647b3337f666`

**Q:** In a short paragraph (3‑8 sentences), name three major renewable‑energy storage technologies, state the primary physical principle each relies on, and give one real‑world installation that uses each technology.

**Path P1:** Provides the three technologies with their principles and examples.

- `P1.C1` completeness, core, w=1: Names three distinct renewable‑energy storage technologies. ← asked by: "name three major renewable‑energy storage technologies"
- `P1.C2` correctness, core, w=1: States the primary physical principle for the first technology named. ← asked by: "state the primary physical principle each relies on"
- `P1.C3` correctness, non-core, w=0.5: Provides a real‑world installation example for the first technology named. ← asked by: "give one real‑world installation that uses each technology"
- `P1.C4` correctness, core, w=1: States the primary physical principle for the second technology named. ← asked by: "state the primary physical principle each relies on"
- `P1.C5` correctness, non-core, w=0.5: Provides a real‑world installation example for the second technology named. ← asked by: "give one real‑world installation that uses each technology"
- `P1.C6` correctness, core, w=1: States the primary physical principle for the third technology named. ← asked by: "state the primary physical principle each relies on"
- `P1.C7` correctness, non-core, w=0.5: Provides a real‑world installation example for the third technology named. ← asked by: "give one real‑world installation that uses each technology"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 3. factual · ethics · `5a492c637640`

**Q:** In a short paragraph (3‑8 sentences), name the two conditions of the principle of double effect and give one distinct example that illustrates each condition.

**Path P1:** Correct answer lists both conditions and supplies an example for each.

- `P1.C1` completeness, core, w=1: Names both conditions of the principle of double effect ← asked by: "name the two conditions of the principle of double effect"
- `P1.C2` correctness, core, w=1: Provides a valid example that illustrates the first condition ← asked by: "give one distinct example that illustrates each condition"
- `P1.C3` correctness, core, w=1: Provides a valid example that illustrates the second condition ← asked by: "give one distinct example that illustrates each condition"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 4. factual · economics · `886e0fcd1e3d`

**Q:** In a short paragraph of 3–6 sentences, list three distinct types of unemployment and give one concrete example for each type.

**Path P1:** List three distinct types of unemployment and provide an example for each.

- `P1.C1` completeness, core, w=1: Names three distinct types of unemployment ← asked by: "list three distinct types of unemployment"
- `P1.C2` correctness, core, w=1: Provides a correct example for the first type named ← asked by: "give one concrete example for each type"
- `P1.C3` correctness, non-core, w=0.5: Provides a correct example for the second type named ← asked by: "give one concrete example for each type"
- `P1.C4` correctness, non-core, w=0.5: Provides a correct example for the third type named ← asked by: "give one concrete example for each type"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 5. analytical · economics · `e82fb3602421`

**Q:** In a short paragraph of 3-6 sentences, argue whether a government-imposed carbon tax effectively reduces greenhouse gas emissions. State a position (for or against) and support it with at least two distinct arguments.

**Path P1:** Argument in favor of a carbon tax

- `P1.C1` correctness, core, w=1: States a position (for) ← asked by: "State a position (for or against)"
- `P1.C2` completeness, core, w=1: Provides at least two distinct arguments supporting the position ← asked by: "support it with at least two distinct arguments"
- `P1.C3` reasoning, core, w=1: Gives a first distinct argument that supports the position ← asked by: "support it with at least two distinct arguments"
- `P1.C4` reasoning, core, w=1: Gives a second distinct argument that supports the position ← asked by: "support it with at least two distinct arguments"

**Path P2:** Argument against a carbon tax

- `P2.C1` correctness, core, w=1: States a position (against) ← asked by: "State a position (for or against)"
- `P2.C2` completeness, core, w=1: Provides at least two distinct arguments supporting the position ← asked by: "support it with at least two distinct arguments"
- `P2.C3` reasoning, core, w=1: Gives a first distinct argument that supports the position ← asked by: "support it with at least two distinct arguments"
- `P2.C4` reasoning, core, w=1: Gives a second distinct argument that supports the position ← asked by: "support it with at least two distinct arguments"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8
