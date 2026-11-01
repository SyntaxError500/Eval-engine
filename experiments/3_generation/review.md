# Phase 3: generated question review

37 questions. For each one, tick every item that holds. The gate passes when at least 85% of questions pass every item that applies to them.

Checklist per question:

1. Task type is right for the question
2. Question is self-contained and answerable in a short paragraph
3. Every criterion is binary and observable
4. Criteria ask for nothing the question doesn't need
5. Criteria don't leak a model sentence to copy
6. Granular enough that a partial answer can meet some criteria
7. Each path is a complete alternative answer, not a part the question requires together with the other paths (analytical / explanatory only)
8. The question's premise and the rubric's facts are correct

## 1. factual · history · `83e77d761714`

**Q:** In a short paragraph (3–8 sentences), name three distinct outcomes of the Congress of Vienna (1814‑1815) and give one specific example that illustrates each outcome.

**Path P1:** A correct answer lists three distinct outcomes of the Congress of Vienna and provides a specific illustrative example for each outcome.

- `P1.C1` completeness, core, w=1: Names a distinct outcome of the Congress of Vienna (e.g., restoration of monarchies) ← asked by: "name three distinct outcomes of the Congress of Vienna (1814‑1815)"
- `P1.C2` correctness, core, w=1: Provides a specific example that illustrates the first outcome named (e.g., restoration of the Bourbon monarchy in France) ← asked by: "give one specific example that illustrates each outcome"
- `P1.C3` completeness, core, w=1: Names a second distinct outcome of the Congress of Vienna (e.g., creation of a balance of power) ← asked by: "name three distinct outcomes of the Congress of Vienna (1814‑1815)"
- `P1.C4` correctness, core, w=1: Provides a specific example that illustrates the second outcome named (e.g., formation of the German Confederation) ← asked by: "give one specific example that illustrates each outcome"
- `P1.C5` completeness, core, w=1: Names a third distinct outcome of the Congress of Vienna (e.g., territorial adjustments to contain France) ← asked by: "name three distinct outcomes of the Congress of Vienna (1814‑1815)"
- `P1.C6` correctness, core, w=1: Provides a specific example that illustrates the third outcome named (e.g., the annexation of the Rhineland to Prussia) ← asked by: "give one specific example that illustrates each outcome"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 2. factual · science · `512f892a6afa`

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

## 3. factual · technology · `647b3337f666`

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

## 4. factual · economics · `886e0fcd1e3d`

**Q:** In a short paragraph of 3–6 sentences, list three distinct types of unemployment and give one concrete example for each type.

**Path P1:** List three distinct types of unemployment and provide an example for each.

- `P1.C1` completeness, core, w=1: Names three distinct types of unemployment ← asked by: "list three distinct types of unemployment"
- `P1.C2` correctness, core, w=1: Provides a correct example for the first type named ← asked by: "give one concrete example for each type"
- `P1.C3` correctness, non-core, w=0.5: Provides a correct example for the second type named ← asked by: "give one concrete example for each type"
- `P1.C4` correctness, non-core, w=0.5: Provides a correct example for the third type named ← asked by: "give one concrete example for each type"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 5. factual · environment · `476bdbe5578d`

**Q:** In a short paragraph (3 to 8 sentences), list three major sources of water pollution, give one pollutant each source typically releases, and name one ecological impact of that pollutant.

**Path P1:** Correct factual answer covering all three sources, their pollutants, and impacts.

- `P1.C1` completeness, core, w=1: Provides the first listed source of water pollution ← asked by: "list three major sources of water pollution"
- `P1.C2` correctness, core, w=1: Names a pollutant that is typically released by the first source ← asked by: "give one pollutant each source typically releases"
- `P1.C3` correctness, core, w=1: Names an ecological impact caused by that pollutant from the first source ← asked by: "name one ecological impact of that pollutant"
- `P1.C4` completeness, core, w=1: Provides the second listed source of water pollution ← asked by: "list three major sources of water pollution"
- `P1.C5` correctness, core, w=1: Names a pollutant that is typically released by the second source ← asked by: "give one pollutant each source typically releases"
- `P1.C6` correctness, core, w=1: Names an ecological impact caused by that pollutant from the second source ← asked by: "name one ecological impact of that pollutant"
- `P1.C7` completeness, core, w=1: Provides the third listed source of water pollution ← asked by: "list three major sources of water pollution"
- `P1.C8` correctness, core, w=1: Names a pollutant that is typically released by the third source ← asked by: "give one pollutant each source typically releases"
- `P1.C9` correctness, core, w=1: Names an ecological impact caused by that pollutant from the third source ← asked by: "name one ecological impact of that pollutant"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 6. factual · health · `17b9d268178a`

**Q:** In a short paragraph (3-8 sentences), name the three main macronutrients required by the human body and state one primary function of each.

**Path P1:** Correctly identifies three macronutrients and gives a primary function for each.

- `P1.C1` completeness, core, w=1: Names three distinct macronutrients required by the human body ← asked by: "name the three main macronutrients"
- `P1.C2` correctness, core, w=1: States a primary function of the first macronutrient named ← asked by: "state one primary function of each"
- `P1.C3` correctness, core, w=1: States a primary function of the second macronutrient named ← asked by: "state one primary function of each"
- `P1.C4` correctness, core, w=1: States a primary function of the third macronutrient named ← asked by: "state one primary function of each"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 7. factual · literature · `b0affe8aae1b`

**Q:** In a short paragraph (3–8 sentences), name three distinct literary movements of the 19th century and give one characteristic work (title and author) associated with each.

**Path P1:** Provide three 19th‑century literary movements and a characteristic work for each.

- `P1.C1` completeness, core, w=1: Names a distinct 19th‑century literary movement (first of three) ← asked by: "name three distinct literary movements of the 19th century"
- `P1.C2` correctness, core, w=1: Gives a valid characteristic work (title and author) associated with the first named movement ← asked by: "give one characteristic work (title and author) associated with each"
- `P1.C3` completeness, core, w=1: Names a distinct 19th‑century literary movement (second of three) ← asked by: "name three distinct literary movements of the 19th century"
- `P1.C4` correctness, core, w=1: Gives a valid characteristic work (title and author) associated with the second named movement ← asked by: "give one characteristic work (title and author) associated with each"
- `P1.C5` completeness, core, w=1: Names a distinct 19th‑century literary movement (third of three) ← asked by: "name three distinct literary movements of the 19th century"
- `P1.C6` correctness, core, w=1: Gives a valid characteristic work (title and author) associated with the third named movement ← asked by: "give one characteristic work (title and author) associated with each"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 8. factual · geography · `dae71517a495`

**Q:** List the three primary types of plate boundaries—divergent, convergent, and transform—and state one key geological feature or process associated with each. Answer in a short paragraph of 3–8 sentences.

**Path P1:** All three plate‑boundary types are identified and each is linked to a correct geological feature or process.

- `P1.C1` completeness, core, w=1: Names all three primary types of plate boundaries (divergent, convergent, transform). ← asked by: "List the three primary types of plate boundaries"
- `P1.C2` correctness, core, w=1: Provides a valid key geological feature or process for divergent boundaries (e.g., mid‑ocean ridge formation, seafloor spreading). ← asked by: "state one key geological feature or process associated with each"
- `P1.C3` correctness, core, w=1: Provides a valid key geological feature or process for convergent boundaries (e.g., subduction zones, mountain building). ← asked by: "state one key geological feature or process associated with each"
- `P1.C4` correctness, core, w=1: Provides a valid key geological feature or process for transform boundaries (e.g., strike‑slip faulting, earthquakes along a transform fault). ← asked by: "state one key geological feature or process associated with each"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 9. factual · everyday life · `3d813378c122`

**Q:** In a short paragraph (3–8 sentences), list three distinct bedtime routines that many adults follow and state the usual order of steps for each routine (e.g., brush teeth → change into pajamas → read a book).

**Path P1:** Provides three distinct bedtime routines each with its typical step order.

- `P1.C1` completeness, core, w=1: Names the first distinct bedtime routine ← asked by: "list three distinct bedtime routines"
- `P1.C2` correctness, core, w=1: States the typical order of steps for the first routine ← asked by: "state the usual order of steps for each routine"
- `P1.C3` completeness, core, w=1: Names the second distinct bedtime routine ← asked by: "list three distinct bedtime routines"
- `P1.C4` correctness, core, w=1: States the typical order of steps for the second routine ← asked by: "state the usual order of steps for each routine"
- `P1.C5` completeness, core, w=1: Names the third distinct bedtime routine ← asked by: "list three distinct bedtime routines"
- `P1.C6` correctness, core, w=1: States the typical order of steps for the third routine ← asked by: "state the usual order of steps for each routine"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 10. analytical · science · `4cb875e3c8cc`

**Q:** Two main hypotheses explain why some planets possess prominent ring systems while others do not: (1) the remnants of a destroyed moon that was torn apart by tidal forces within the planet's Roche limit, and (2) the accumulation of leftover material from the planet's formation that never coalesced into a moon. In a short paragraph (3‑8 sentences), evaluate these two hypotheses and argue which one you find more convincing, providing supporting evidence for each.

**Path P1:** Argue that the destroyed‑moon hypothesis is more convincing.

- `P1.C1` completeness, core, w=1: States that the destroyed‑moon hypothesis is more convincing. ← asked by: "argue which one you find more convincing"
- `P1.C2` correctness, core, w=1: Provides at least one distinct piece of evidence supporting the destroyed‑moon hypothesis (e.g., observations of ring particles matching moon composition or calculations showing tidal disruption within the Roche limit). ← asked by: "providing supporting evidence for each"
- `P1.C3` correctness, core, w=1: Provides at least one distinct piece of evidence supporting the leftover‑material hypothesis (e.g., models of planet formation that leave a residual disk of dust and ice). ← asked by: "providing supporting evidence for each"
- `P1.C4` reasoning, core, w=1: Explains why the evidence makes the destroyed‑moon hypothesis more convincing than the leftover‑material hypothesis. ← asked by: "argue which one you find more convincing"

**Path P2:** Argue that the leftover‑material hypothesis is more convincing.

- `P2.C1` completeness, core, w=1: States that the leftover‑material hypothesis is more convincing. ← asked by: "argue which one you find more convincing"
- `P2.C2` correctness, core, w=1: Provides at least one distinct piece of evidence supporting the destroyed‑moon hypothesis (e.g., observations of ring particles matching moon composition or calculations showing tidal disruption within the Roche limit). ← asked by: "providing supporting evidence for each"
- `P2.C3` correctness, core, w=1: Provides at least one distinct piece of evidence supporting the leftover‑material hypothesis (e.g., models of planet formation that leave a residual disk of dust and ice). ← asked by: "providing supporting evidence for each"
- `P2.C4` reasoning, core, w=1: Explains why the evidence makes the leftover‑material hypothesis more convincing than the destroyed‑moon hypothesis. ← asked by: "argue which one you find more convincing"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 11. analytical · technology · `d757eca4528c`

**Q:** In a short paragraph (3‑8 sentences), present one position on whether governments should require mandatory data‑privacy standards for consumer Internet‑of‑Things (IoT) devices, and support it with at least one specific reason or piece of evidence.

**Path P1:** Supports the position that governments should require mandatory data‑privacy standards for consumer IoT devices.

- `P1.C1` completeness, core, w=1: States the position that governments should require mandatory data‑privacy standards for consumer IoT devices. ← asked by: "present one position"
- `P1.C2` reasoning, core, w=1: Provides at least one specific reason or piece of evidence supporting the stated position. ← asked by: "support it with at least one specific reason or piece of evidence"
- `P1.C3` correctness, core, w=1: The answer does not contradict the stated position elsewhere in the paragraph. ← asked by: "present one position"

**Path P2:** Supports the position that governments should not require mandatory data‑privacy standards for consumer IoT devices.

- `P2.C1` completeness, core, w=1: States the position that governments should not require mandatory data‑privacy standards for consumer IoT devices. ← asked by: "present one position"
- `P2.C2` reasoning, core, w=1: Provides at least one specific reason or piece of evidence supporting the stated position. ← asked by: "support it with at least one specific reason or piece of evidence"
- `P2.C3` correctness, core, w=1: The answer does not contradict the stated position elsewhere in the paragraph. ← asked by: "present one position"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 12. analytical · ethics · `082591e7ec4e`

**Q:** In a short paragraph (3‑8 sentences), argue whether utilitarianism provides a better foundation for public policy than deontological ethics. State your position, give one concrete policy area where your chosen approach offers an advantage, and explain how it supports your claim.

**Path P1:** Argument that utilitarianism provides the better foundation for public policy

- `P1.C1` completeness, core, w=1: States the position that utilitarianism provides a better foundation for public policy than deontological ethics. ← asked by: "State your position"
- `P1.C2` correctness, core, w=1: Provides one concrete policy area where utilitarianism offers an advantage. ← asked by: "give one concrete policy area"
- `P1.C3` reasoning, core, w=1: Explains how the policy area supports the claim that utilitarianism is the better foundation. ← asked by: "explain how it supports your claim"

**Path P2:** Argument that deontological ethics provides the better foundation for public policy

- `P2.C1` completeness, core, w=1: States the position that deontological ethics provides a better foundation for public policy than utilitarianism. ← asked by: "State your position"
- `P2.C2` correctness, core, w=1: Provides one concrete policy area where deontological ethics offers an advantage. ← asked by: "give one concrete policy area"
- `P2.C3` reasoning, core, w=1: Explains how the policy area supports the claim that deontological ethics is the better foundation. ← asked by: "explain how it supports your claim"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 13. analytical · economics · `d92e0ad73cb8`

**Q:** In a short paragraph of 3–6 sentences, argue whether implementing a progressive wealth tax on the richest households would reduce economic inequality in a market economy. State a position (for or against) and support it with at least two distinct arguments.

**Path P1:** Argument in favor of a wealth tax

- `P1.C1` correctness, core, w=1: States a position (for) as required ← asked by: "State a position (for or against)"
- `P1.C2` reasoning, core, w=1: Provides a first distinct argument that supports the stated position ← asked by: "support it with at least two distinct arguments"
- `P1.C3` reasoning, core, w=1: Provides a second distinct argument that supports the stated position ← asked by: "support it with at least two distinct arguments"
- `P1.C4` completeness, non-core, w=0.5: Mentions economic inequality and links it to the wealth tax ← asked by: "reduce economic inequality"

**Path P2:** Argument against a wealth tax

- `P2.C1` correctness, core, w=1: States a position (against) as required ← asked by: "State a position (for or against)"
- `P2.C2` reasoning, core, w=1: Provides a first distinct argument that supports the stated position ← asked by: "support it with at least two distinct arguments"
- `P2.C3` reasoning, core, w=1: Provides a second distinct argument that supports the stated position ← asked by: "support it with at least two distinct arguments"
- `P2.C4` completeness, non-core, w=0.5: Mentions economic inequality and links it to the wealth tax ← asked by: "reduce economic inequality"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 14. analytical · environment · `5d564b58c11c`

**Q:** In a short paragraph (3 to 8 sentences), argue for either (a) implementing a nationwide ban on the use of chemical pesticides in agriculture, or (b) promoting integrated pest management (IPM) as a sustainable alternative. Choose one position, state at least two distinct supporting reasons, and provide a specific factual example, statistic, or case study for each reason.

**Path P1:** Implement a nationwide ban on chemical pesticides in agriculture

- `P1.C1` completeness, core, w=1: States the chosen position that a ban on chemical pesticides should be implemented ← asked by: "Choose one position"
- `P1.C2` reasoning, core, w=1: Gives a first distinct reason that supports the ban ← asked by: "state at least two distinct supporting reasons"
- `P1.C3` correctness, core, w=1: Provides a specific factual example, statistic, or case study that supports the first reason ← asked by: "provide a specific factual example, statistic, or case study for each reason"
- `P1.C4` reasoning, core, w=1: Gives a second distinct reason that supports the ban ← asked by: "state at least two distinct supporting reasons"
- `P1.C5` correctness, core, w=1: Provides a specific factual example, statistic, or case study that supports the second reason ← asked by: "provide a specific factual example, statistic, or case study for each reason"

**Path P2:** Promote integrated pest management (IPM) as a sustainable alternative to chemical pesticides

- `P2.C1` completeness, core, w=1: States the chosen position that integrated pest management should be promoted ← asked by: "Choose one position"
- `P2.C2` reasoning, core, w=1: Gives a first distinct reason that supports IPM ← asked by: "state at least two distinct supporting reasons"
- `P2.C3` correctness, core, w=1: Provides a specific factual example, statistic, or case study that supports the first reason ← asked by: "provide a specific factual example, statistic, or case study for each reason"
- `P2.C4` reasoning, core, w=1: Gives a second distinct reason that supports IPM ← asked by: "state at least two distinct supporting reasons"
- `P2.C5` correctness, core, w=1: Provides a specific factual example, statistic, or case study that supports the second reason ← asked by: "provide a specific factual example, statistic, or case study for each reason"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 15. analytical · health · `632df277470d`

**Q:** In a short paragraph (3–8 sentences), argue whether mandatory fortification of staple foods with vitamin D should be implemented as a public‑health measure. Choose one side, present at least two supporting points, and acknowledge a counterargument from the opposite side.

**Path P1:** Argument in favor of mandatory vitamin D fortification

- `P1.C1` correctness, core, w=1: States a position that mandatory fortification of staple foods with vitamin D should be implemented ← asked by: "Choose one side"
- `P1.C2` reasoning, core, w=1: Provides a first supporting point that backs the pro‑fortification position ← asked by: "present at least two supporting points"
- `P1.C3` reasoning, core, w=1: Provides a second supporting point that backs the pro‑fortification position ← asked by: "present at least two supporting points"
- `P1.C4` completeness, core, w=1: Acknowledges a counterargument from the opposite side ← asked by: "acknowledge a counterargument from the opposite side"

**Path P2:** Argument against mandatory vitamin D fortification

- `P2.C1` correctness, core, w=1: States a position that mandatory fortification of staple foods with vitamin D should not be implemented ← asked by: "Choose one side"
- `P2.C2` reasoning, core, w=1: Provides a first supporting point that backs the anti‑fortification position ← asked by: "present at least two supporting points"
- `P2.C3` reasoning, core, w=1: Provides a second supporting point that backs the anti‑fortification position ← asked by: "present at least two supporting points"
- `P2.C4` completeness, core, w=1: Acknowledges a counterargument from the opposite side ← asked by: "acknowledge a counterargument from the opposite side"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 16. analytical · literature · `7ef66d20c834`

**Q:** In a short paragraph (3–8 sentences), argue whether Nathaniel Hawthorne’s *The Scarlet Letter* should be read primarily as a critique of Puritan moral hypocrisy or as an exploration of individual psychological trauma, and support your view with at least two distinct pieces of textual evidence.

**Path P1:** Argument that the novel critiques Puritan moral hypocrisy

- `P1.C1` completeness, core, w=1: States that the novel should be read primarily as a critique of Puritan moral hypocrisy ← asked by: "should be read primarily as a critique of Puritan moral hypocrisy"
- `P1.C2` correctness, core, w=1: Provides a first distinct piece of textual evidence that supports the critique ← asked by: "at least two distinct pieces of textual evidence"
- `P1.C3` correctness, non-core, w=0.5: Provides a second distinct piece of textual evidence that supports the critique ← asked by: "at least two distinct pieces of textual evidence"
- `P1.C4` reasoning, core, w=1: Explains how the provided evidence demonstrates the critique of Puritan moral hypocrisy ← asked by: "support your view"

**Path P2:** Argument that the novel explores individual psychological trauma

- `P2.C1` completeness, core, w=1: States that the novel should be read primarily as an exploration of individual psychological trauma ← asked by: "as an exploration of individual psychological trauma"
- `P2.C2` correctness, core, w=1: Provides a first distinct piece of textual evidence that supports the trauma interpretation ← asked by: "at least two distinct pieces of textual evidence"
- `P2.C3` correctness, non-core, w=0.5: Provides a second distinct piece of textual evidence that supports the trauma interpretation ← asked by: "at least two distinct pieces of textual evidence"
- `P2.C4` reasoning, core, w=1: Explains how the provided evidence demonstrates the exploration of individual psychological trauma ← asked by: "support your view"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 17. analytical · geography · `7d174cce75df`

**Q:** In a short paragraph of 3–8 sentences, argue whether the primary cause of the recent intensification of urban heat islands in megacities is (1) reduced vegetation cover or (2) increased anthropogenic heat emissions. Choose one factor, state the claim, and provide at least one piece of supporting evidence that links the chosen factor to stronger urban heat islands.

**Path P1:** Argument that reduced vegetation cover is the primary cause of recent urban heat‑island intensification.

- `P1.C1` correctness, core, w=1: States the claim that reduced vegetation cover is the primary cause of recent intensification of urban heat islands in megacities. ← asked by: "state the claim"
- `P1.C2` reasoning, core, w=1: Provides at least one piece of supporting evidence that links reduced vegetation cover to stronger urban heat islands. ← asked by: "provide at least one piece of supporting evidence"

**Path P2:** Argument that increased anthropogenic heat emissions are the primary cause of recent urban heat‑island intensification.

- `P2.C1` correctness, core, w=1: States the claim that increased anthropogenic heat emissions are the primary cause of recent intensification of urban heat islands in megacities. ← asked by: "state the claim"
- `P2.C2` reasoning, core, w=1: Provides at least one piece of supporting evidence that links increased anthropogenic heat emissions to stronger urban heat islands. ← asked by: "provide at least one piece of supporting evidence"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 18. analytical · everyday life · `78d7767e5351`

**Q:** In a short paragraph (3–8 sentences), argue whether working from home increases overall work‑life balance, and support your argument with at least two distinct reasons.

**Path P1:** Argument that working from home increases overall work‑life balance

- `P1.C1` correctness, core, w=1: States a position that working from home increases overall work‑life balance ← asked by: "argue whether working from home increases overall work‑life balance"
- `P1.C2` reasoning, core, w=1: Provides a first distinct reason that supports the position ← asked by: "support your argument with at least two distinct reasons"
- `P1.C3` reasoning, core, w=1: Provides a second distinct reason that supports the position ← asked by: "support your argument with at least two distinct reasons"

**Path P2:** Argument that working from home does not increase overall work‑life balance

- `P2.C1` correctness, core, w=1: States a position that working from home does not increase overall work‑life balance ← asked by: "argue whether working from home increases overall work‑life balance"
- `P2.C2` reasoning, core, w=1: Provides a first distinct reason that supports the position ← asked by: "support your argument with at least two distinct reasons"
- `P2.C3` reasoning, core, w=1: Provides a second distinct reason that supports the position ← asked by: "support your argument with at least two distinct reasons"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 19. analytical · history · `17c1b10632b5`

**Q:** In a short paragraph (3–8 sentences), argue whether the primary cause of the outbreak of World War I was the system of alliances or nationalist rivalries, and support your position with specific historical evidence.

**Path P1:** Argument that the system of alliances was the primary cause

- `P1.C1` completeness, core, w=1: States a position that the primary cause was the system of alliances ← asked by: "argue whether the primary cause of the outbreak of World War I was the system of alliances or nationalist rivalries"
- `P1.C2` correctness, core, w=1: Provides a specific historical example that supports the alliance system as the primary cause ← asked by: "support your position with specific historical evidence"
- `P1.C3` reasoning, core, w=1: Explains how the example demonstrates that the alliance system caused the war ← asked by: "support your position with specific historical evidence"

**Path P2:** Argument that nationalist rivalries were the primary cause

- `P2.C1` completeness, core, w=1: States a position that the primary cause was nationalist rivalries ← asked by: "argue whether the primary cause of the outbreak of World War I was the system of alliances or nationalist rivalries"
- `P2.C2` correctness, core, w=1: Provides a specific historical example that supports nationalist rivalries as the primary cause ← asked by: "support your position with specific historical evidence"
- `P2.C3` reasoning, core, w=1: Explains how the example shows nationalist rivalries led to the war ← asked by: "support your position with specific historical evidence"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 20. explanatory · technology · `a5cd0a155f64`

**Q:** Explain how 5G wireless networks achieve lower latency than previous 4G LTE networks. In a short paragraph (3‑8 sentences), describe one primary technical mechanism that enables this reduction.

**Path P1:** Provides a correct explanation of a single technical mechanism that lowers latency in 5G compared to 4G and links it to the latency improvement.

- `P1.C1` completeness, core, w=1: Identifies a primary technical mechanism that reduces latency in 5G compared to 4G. ← asked by: "describe one primary technical mechanism that enables this reduction"
- `P1.C2` correctness, core, w=1: The identified mechanism is described accurately and is indeed a factor that lowers latency in 5G. ← asked by: "describe one primary technical mechanism that enables this reduction"
- `P1.C3` reasoning, core, w=1: Explains how the mechanism leads to lower latency in 5G compared to 4G. ← asked by: "Explain how 5G wireless networks achieve lower latency than previous 4G LTE networks"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 21. explanatory · ethics · `91798e725180`

**Q:** In a short paragraph (3‑8 sentences), explain why individuals often follow social norms even when those norms conflict with their personal moral convictions.

**Path P1:** Explanation based on social conformity: individuals follow norms to gain social approval or avoid exclusion.

- `P1.C1` correctness, core, w=1: Identifies desire for social approval or fear of exclusion as the primary factor explaining the behavior. ← asked by: "explain why individuals often follow social norms even when those norms conflict with their personal moral convictions"
- `P1.C2` completeness, core, w=1: Addresses the tension between personal moral convictions and the norm by noting that the desire for approval overrides the personal conflict. ← asked by: "explain why individuals often follow social norms even when those norms conflict with their personal moral convictions"
- `P1.C3` reasoning, core, w=1: Links the desire for approval to the decision to follow the norm through a causal explanation (e.g., because they fear exclusion, they conform). ← asked by: "explain why individuals often follow social norms even when those norms conflict with their personal moral convictions"

**Path P2:** Explanation based on internalized moral identity: norms have become part of the individual's self‑concept through upbringing or habit.

- `P2.C1` correctness, core, w=1: Identifies internalized moral identity or habit formed by upbringing as the primary factor explaining the behavior. ← asked by: "explain why individuals often follow social norms even when those norms conflict with their personal moral convictions"
- `P2.C2` completeness, core, w=1: Notes that the internalized norm persists even when it clashes with current personal convictions. ← asked by: "explain why individuals often follow social norms even when those norms conflict with their personal moral convictions"
- `P2.C3` reasoning, core, w=1: Explains how internalization leads to automatic compliance, overriding conflicting personal judgments. ← asked by: "explain why individuals often follow social norms even when those norms conflict with their personal moral convictions"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 22. explanatory · economics · `669bce9c85fb`

**Q:** In a short paragraph of 3–6 sentences, explain how a depreciation of a country's currency influences its export competitiveness. Provide one mechanism that connects the change in exchange rate to export volumes.

**Path P1:** Explanation that links depreciation to export competitiveness via a price‑effect mechanism

- `P1.C1` completeness, core, w=1: Explains how a depreciation of a country's currency influences its export competitiveness ← asked by: "explain how a depreciation of a country's currency influences its export competitiveness"
- `P1.C2` correctness, core, w=1: States that depreciation lowers the foreign‑currency price of the country's exported goods ← asked by: "explain how a depreciation of a country's currency influences its export competitiveness"
- `P1.C3` reasoning, core, w=1: Provides one mechanism that links the exchange‑rate change to export volumes (e.g., lower prices increase foreign demand) ← asked by: "provide one mechanism that connects the change in exchange rate to export volumes"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 23. explanatory · environment · `1e9d95d9130f`

**Q:** In a short paragraph (3 to 8 sentences), explain one mechanism by which adding biochar to agricultural soil enhances carbon sequestration, and give a concrete example of a farm or region where this mechanism has been applied.

**Path P1:** Mechanism: biochar physically protects organic carbon from decomposition (adsorption, increased recalcitrance).

- `P1.C1` correctness, core, w=1: States that biochar physically protects organic carbon from decomposition by adsorbing it and increasing its recalcitrance ← asked by: "explain one mechanism"
- `P1.C2` completeness, core, w=1: Gives a concrete example of a farm or region where biochar has been applied to achieve this physical‑protection mechanism ← asked by: "give a concrete example of a farm or region where this mechanism has been applied"
- `P1.C3` reasoning, non-core, w=0.5: Explains how the example demonstrates the physical‑protection mechanism (e.g., reports a measured increase in stable carbon due to reduced decomposition) ← asked by: "example where this mechanism has been applied"

**Path P2:** Mechanism: biochar improves soil microbial activity, leading to formation of stable soil organic matter that sequesters carbon.

- `P2.C1` correctness, core, w=1: States that biochar enhances carbon sequestration by stimulating soil microbial activity that creates stable organic matter ← asked by: "explain one mechanism"
- `P2.C2` completeness, core, w=1: Gives a concrete example of a farm or region where biochar has been applied to achieve this microbial‑activity mechanism ← asked by: "give a concrete example of a farm or region where this mechanism has been applied"
- `P2.C3` reasoning, non-core, w=0.5: Explains how the example illustrates the microbial‑activity mechanism (e.g., cites increased microbial biomass or soil organic carbon measurements after biochar addition) ← asked by: "example where this mechanism has been applied"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 24. explanatory · health · `b850a615f22e`

**Q:** In a short paragraph (3–8 sentences), explain one mechanism by which regular physical activity improves mental health.

**Path P1:** Neurochemical explanation via endorphin release

- `P1.C1` completeness, core, w=1: Names a valid mechanism by which regular physical activity improves mental health (e.g., increased endorphin release, enhanced neurogenesis, improved self‑efficacy) ← asked by: "one mechanism"
- `P1.C2` correctness, core, w=1: Describes the mechanism accurately (e.g., states that exercise triggers endorphin release from the pituitary) ← asked by: "explain"
- `P1.C3` reasoning, core, w=1: Explains how this mechanism leads to improved mental health (e.g., endorphins reduce perceived stress or elevate mood) ← asked by: "improves mental health"

**Path P2:** Neurobiological explanation via increased BDNF and neurogenesis

- `P2.C1` completeness, core, w=1: Names a valid mechanism by which regular physical activity improves mental health (e.g., increased endorphin release, enhanced neurogenesis, improved self‑efficacy) ← asked by: "one mechanism"
- `P2.C2` correctness, core, w=1: Describes the mechanism accurately (e.g., explains that exercise raises brain‑derived neurotrophic factor, promoting neurogenesis in the hippocampus) ← asked by: "explain"
- `P2.C3` reasoning, core, w=1: Explains how this mechanism leads to improved mental health (e.g., neurogenesis improves mood regulation and reduces depressive symptoms) ← asked by: "improves mental health"

**Path P3:** Psychosocial explanation via enhanced self‑efficacy and social interaction

- `P3.C1` completeness, core, w=1: Names a valid mechanism by which regular physical activity improves mental health (e.g., increased endorphin release, enhanced neurogenesis, improved self‑efficacy) ← asked by: "one mechanism"
- `P3.C2` correctness, core, w=1: Describes the mechanism accurately (e.g., notes that regular exercise builds confidence and provides opportunities for social engagement) ← asked by: "explain"
- `P3.C3` reasoning, core, w=1: Explains how this mechanism leads to improved mental health (e.g., higher self‑efficacy reduces anxiety and social interaction alleviates loneliness) ← asked by: "improves mental health"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 25. explanatory · literature · `c08ec38ec72f`

**Q:** In a short paragraph (3–8 sentences), explain how the use of an unreliable narrator in F. Scott Fitzgerald’s *The Great Gatsby* influences the reader’s understanding of the American Dream.

**Path P1:** Explanation that the narrator’s unreliability creates ambiguity about the attainability of the American Dream.

- `P1.C1` correctness, core, w=1: Identifies the narrator as unreliable. ← asked by: "unreliable narrator"
- `P1.C2` completeness, core, w=1: States that the narrator’s unreliability influences the reader’s understanding of the American Dream. ← asked by: "influences the reader’s understanding of the American Dream"
- `P1.C3` reasoning, core, w=1: Explains that this influence creates ambiguity about whether the American Dream can be attained. ← asked by: "influences the reader’s understanding of the American Dream"

**Path P2:** Explanation that the narrator’s unreliability reveals the American Dream as a mythic illusion rather than a realistic goal.

- `P2.C1` correctness, core, w=1: Identifies the narrator as unreliable. ← asked by: "unreliable narrator"
- `P2.C2` completeness, core, w=1: States that the narrator’s unreliability influences the reader’s understanding of the American Dream. ← asked by: "influences the reader’s understanding of the American Dream"
- `P2.C3` reasoning, core, w=1: Explains that this influence reveals the American Dream as a mythic illusion rather than a realistic goal. ← asked by: "influences the reader’s understanding of the American Dream"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 26. explanatory · geography · `3f8052a62a58`

**Q:** Explain why mountain ranges often create dry regions on their leeward side (rain shadows). In a short paragraph of 3–8 sentences, state the main atmospheric mechanism responsible, describe how it leads to reduced precipitation on the leeward side, and give one supporting fact that illustrates this process.

**Path P1:** Explain the orographic precipitation mechanism that produces a rain shadow.

- `P1.C1` correctness, core, w=1: States the main atmospheric mechanism responsible for rain shadows (orographic lift causing precipitation on the windward side and descending dry air on the leeward side). ← asked by: "state the main atmospheric mechanism responsible"
- `P1.C2` reasoning, core, w=1: Describes how the mechanism leads to reduced precipitation on the leeward side (descending air warms, its relative humidity drops, and precipitation decreases). ← asked by: "describe how it leads to reduced precipitation on the leeward side"
- `P1.C3` completeness, core, w=1: Gives one supporting fact that illustrates the process (e.g., temperature drops ~6 °C per km of ascent, or cites a known rain‑shadow region such as the leeward side of the Cascades). ← asked by: "give one supporting fact that illustrates this process"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 27. explanatory · everyday life · `610c46d48e48`

**Q:** Explain why many people frequently misplace their keys, offering one plausible explanation in a short paragraph (3–8 sentences).

**Path P1:** Explanation: lack of a designated spot for keys

- `P1.C1` completeness, core, w=1: Provides an explanation that directly addresses why many people frequently misplace their keys. ← asked by: "Explain why many people frequently misplace their keys"
- `P1.C2` correctness, core, w=1: States that the explanation involves not having a designated spot for keys. ← asked by: "offering one plausible explanation"
- `P1.C3` reasoning, non-core, w=0.5: Explains that without a consistent spot, keys are left in various locations, leading to misplacement. ← asked by: "offering one plausible explanation"

**Path P2:** Explanation: cognitive load or stress reduces attention to key placement

- `P2.C1` completeness, core, w=1: Provides an explanation that directly addresses why many people frequently misplace their keys. ← asked by: "Explain why many people frequently misplace their keys"
- `P2.C2` correctness, core, w=1: States that the explanation involves high cognitive load or stress impairing memory for key location. ← asked by: "offering one plausible explanation"
- `P2.C3` reasoning, non-core, w=0.5: Explains that when people are stressed or multitasking they pay less attention to where they place keys, so they forget the location. ← asked by: "offering one plausible explanation"

**Path P3:** Explanation: small size and environmental clutter make keys easy to overlook

- `P3.C1` completeness, core, w=1: Provides an explanation that directly addresses why many people frequently misplace their keys. ← asked by: "Explain why many people frequently misplace their keys"
- `P3.C2` correctness, core, w=1: States that the explanation involves the small size of keys and cluttered surroundings causing them to blend in. ← asked by: "offering one plausible explanation"
- `P3.C3` reasoning, non-core, w=0.5: Explains that because keys are small and blend into clutter, they are easily overlooked and later misplaced. ← asked by: "offering one plausible explanation"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 28. explanatory · science · `23575fb39cfd`

**Q:** Explain why a hot‑air balloon rises when the air inside it is heated. Answer in a short paragraph (3‑8 sentences).

**Path P1:** The balloon rises because heating the air inside reduces its density, creating a buoyant upward force.

- `P1.C1` correctness, core, w=1: States that heating the air inside the balloon reduces its density compared to the surrounding cooler air ← asked by: "Explain why a hot‑air balloon rises when the air inside it is heated"
- `P1.C2` reasoning, core, w=1: Links the lower density of the heated air to a net upward buoyant force that lifts the balloon ← asked by: "Explain why a hot‑air balloon rises when the air inside it is heated"
- `P1.C3` completeness, core, w=1: Mentions that the surrounding air is cooler (or at ambient temperature) providing the contrast needed for lift ← asked by: "Explain why a hot‑air balloon rises when the air inside it is heated"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 29. creative · ethics · `4881228365fa`

**Q:** Write a brief scene of 3‑8 sentences in which a journalist must choose whether to publish a leaked report about a corporation's harmful practices or keep it hidden to protect sources. The scene must include at least one line of dialogue that reveals the journalist's internal conflict, a turning point where the decision is made, must not contain the phrase “ethical dilemma”, and must avoid the clichés “the world will never be the same”, “the stakes are high”, and “moral crossroads”.

**Path P1:** A scene satisfying all listed constraints

- `P1.C1` correctness, core, w=1: Contains between 3 and 8 sentences ← asked by: "3‑8 sentences"
- `P1.C2` correctness, core, w=1: Includes at least one line of dialogue that reveals the journalist's internal conflict ← asked by: "at least one line of dialogue that reveals the journalist's internal conflict"
- `P1.C3` correctness, core, w=1: Contains a turning point where the decision is made ← asked by: "a turning point where the decision is made"
- `P1.C4` correctness, core, w=1: Does not contain the phrase "ethical dilemma" ← asked by: "must not contain the phrase “ethical dilemma”"
- `P1.C5` correctness, core, w=1: Does not use any of the banned clichés: "the world will never be the same", "the stakes are high", "moral crossroads" ← asked by: "must avoid the clichés “the world will never be the same”, “the stakes are high”, and “moral crossroads”"
- `P1.C6` expression, core, w=1: Shows the conflict through dialogue or action rather than stating it directly ← (no quote)

**Obvious answers (originality check):**

- The journalist hesitates, says "If I publish, they could sue us," then decides to release the story after a colleague warns of public harm.
- The journalist whispers "I can't betray my source," but after seeing the damage caused, declares "The truth must come out" and publishes.
- The journalist looks at the file, mutters "Keeping this secret protects lives," then, after a phone call, says "No, the world deserves to know" and sends it out.
- The journalist debates internally, says "I could ruin careers," then a whistleblower arrives, prompting the line "Enough hiding," and the journalist posts the report.
- The journalist paces, says "If I hide it, the victims suffer," then a news alert flashes, leading to the decisive "It's time to tell everyone" and the story goes live.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 30. creative · economics · `33f285706f47`

**Q:** Write a short scene (3–5 sentences) in which a recent college graduate, Alex, discovers that the monthly rent for their first apartment has increased. The scene must (1) mention the new rent amount, (2) show Alex's internal thought about whether to stay or move, and (3) include a brief reference to a roommate offering to share a cheaper place. Write the scene using present‑tense narration and do not use any of the clichés: "money talks", "price is what you pay", "cost of living".

**Path P1:** All required constraints satisfied.

- `P1.C1` correctness, core, w=1: Mentions the new rent amount ← asked by: "mention the new rent amount"
- `P1.C2` correctness, core, w=1: Shows Alex's internal thought about whether to stay or move ← asked by: "show Alex's internal thought about whether to stay or move"
- `P1.C3` correctness, core, w=1: Includes a brief reference to a roommate offering to share a cheaper place ← asked by: "include a brief reference to a roommate offering to share a cheaper place"
- `P1.C4` expression, core, w=1: Uses present‑tense narration ← asked by: "Write the scene using present‑tense narration"
- `P1.C5` expression, core, w=1: Does not use any of the clichés: "money talks", "price is what you pay", "cost of living" ← asked by: "do not use any of the clichés: "money talks", "price is what you pay", "cost of living""

**Obvious answers (originality check):**

- Alex reads a notice that the rent is now $1,200, thinks about the budget squeeze, and the roommate suggests a cheaper $900 apartment they could share.
- Alex gets an email saying the rent jumps to $1,500, worries about affording it, and the roommate offers to split a smaller place nearby.
- Alex sees a text: "Rent is $1,100 now," feels anxious about staying, and the roommate mentions a sublet at a lower price.
- Alex discovers the landlord raised rent to $1,300, debates moving out, and the roommate proposes moving in together to cut costs.
- Alex learns the new rent is $1,250, considers looking for a new place, and the roommate suggests sharing a studio for $800.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 31. creative · environment · `b687c2df5103`

**Q:** Write a short scene (3 to 8 sentences) that depicts a forest clearing after a wildfire, showing the first signs of ecological recovery as the first shoots emerge. Use vivid sensory details, include a character who observes the changes, and avoid the clichés 'phoenix rising' and 'silver lining'.

**Path P1:** Scene meets all brief constraints

- `P1.C1` correctness, core, w=1: Contains between three and eight sentences ← asked by: "3 to 8 sentences"
- `P1.C2` expression, core, w=1: Includes vivid sensory details describing sights, sounds, smells, or textures ← asked by: "vivid sensory details"
- `P1.C3` correctness, core, w=1: Features a character who observes the environmental changes ← asked by: "include a character who observes the changes"
- `P1.C4` correctness, core, w=1: Shows the first signs of ecological recovery, such as the emergence of new shoots ← asked by: "first signs of ecological recovery"
- `P1.C5` expression, core, w=1: Does not use any of: "phoenix rising", "silver lining" ← asked by: "avoid the clichés 'phoenix rising' and 'silver lining'"

**Obvious answers (originality check):**

- A ranger watches tiny green shoots push through blackened soil, hears the faint rustle of recovering birds, and notes the smell of wet earth.
- A local resident steps into the clearing, feels the cool dampness on their boots, sees the first saplings, and reflects on the forest’s resilience.
- A firefighter surveys the charred ground, describes the crackling of cooling ash, spots a lone fern unfurling, and comments on nature’s slow return.
- A scientist records the emergence of moss on burnt rocks, notes the scent of pine resin after rain, and observes a child pointing out the new growth.
- An artist sketches the scarred landscape, captures the glint of sunlight on fresh leaves, hears distant wildlife, and mentions the first sprouts breaking through.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 32. creative · health · `a93e1782531b`

**Q:** Write a short scene (3–8 sentences) in which a pharmacist explains to an elderly customer how to use a new inhaler for asthma. The scene must (1) describe the inhaler's key mechanism of delivering medication, (2) show the customer's reaction using a physical cue instead of naming the feeling, and (3) end with the pharmacist providing a follow‑up instruction.

**Path P1:** Scene that meets all three constraints

- `P1.C1` correctness, core, w=1: Describes the inhaler's key mechanism of delivering medication. ← asked by: "describe the inhaler's key mechanism of delivering medication"
- `P1.C2` expression, core, w=1: Shows the customer's reaction using a physical cue instead of naming the feeling. ← asked by: "show the customer's reaction using a physical cue instead of naming the feeling"
- `P1.C3` correctness, core, w=1: Ends with the pharmacist providing a follow‑up instruction. ← asked by: "end with the pharmacist providing a follow‑up instruction"

**Obvious answers (originality check):**

- The pharmacist says the inhaler sprays a mist of medicine when pressed, the elderly customer tightens his grip on the counter, and the pharmacist tells him to use it twice daily and schedule a follow‑up.
- The pharmacist explains the device releases medication via a propellant, the customer nods slowly and leans forward, and the pharmacist advises a check‑up in a month.
- The pharmacist notes the inhaler delivers a fine aerosol when the trigger is pulled, the customer sighs and rubs his temples, and the pharmacist instructs to rinse his mouth after each dose and return for a refill.
- The pharmacist describes the inhaler’s mechanism as a breath‑activated mist, the customer frowns and taps his foot, and the pharmacist ends by saying to keep a usage log and come back in two weeks.
- The pharmacist points out the inhaler uses a spring‑loaded cartridge to aerosolize the drug, the customer raises his eyebrows and clutches his chest, and the pharmacist finishes with a reminder to clean the mouthpiece and schedule a follow‑up appointment.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 33. creative · literature · `30cfecdb54df`

**Q:** In a short scene of three to eight sentences, write a narrative where a character discovers a forgotten poetry anthology in a rooftop garden. The scene must include vivid sensory description, a twist at the end, show rather than tell, and must avoid the clichés: “the wind whispered”, “the pages fluttered”, “a secret message”.

**Path P1:** Meets all creative constraints

- `P1.C1` correctness, core, w=1: Includes at least one vivid sensory description (e.g., mentions sight, sound, smell, touch, or taste) ← asked by: "vivid sensory description"
- `P1.C2` correctness, core, w=1: Ends with a twist that changes the situation or reveals new information ← asked by: "twist at the end"
- `P1.C3` expression, core, w=1: Conveys information through description of actions or senses rather than directly stating facts ← asked by: "show rather than tell"
- `P1.C4` correctness, core, w=1: Does not use any of the listed cliché phrases: “the wind whispered”, “the pages fluttered”, “a secret message” ← asked by: "avoid the clichés"

**Obvious answers (originality check):**

- A character finds the anthology, smells rain on the garden, and the twist is that the poems are written by the character themselves.
- A character discovers the anthology, hears distant city noises, and the twist reveals the anthology is blank except for a single line predicting the future.
- A character uncovers the anthology, feels dust on the cover, and the twist shows the rooftop garden is actually the roof of a hidden library.
- A character spots the anthology glowing in the sunset, tastes the metallic railing, and the twist is that the poems begin reciting aloud on their own.
- A character lifts the anthology, sees a flock of birds scatter, and the twist is that the book opens a portal to another world.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 34. creative · everyday life · `b54dae9759d1`

**Q:** Write a brief (3–6 sentences) scene describing a person waiting in line at a coffee shop, focusing on the protagonist’s internal thoughts, include at least one tactile detail, and end with a subtle hint of an upcoming decision.

**Path P1:** The answer meets all constraints of the brief.

- `P1.C1` correctness, core, w=1: Provides a narrative scene describing a person waiting in line at a coffee shop ← asked by: "scene describing a person waiting in line at a coffee shop"
- `P1.C2` expression, core, w=1: Includes internal thoughts of the protagonist ← asked by: "protagonist’s internal thoughts"
- `P1.C3` correctness, core, w=1: Provides at least one tactile detail ← asked by: "include at least one tactile detail"
- `P1.C4` expression, core, w=1: Ends with a subtle hint of an upcoming decision ← asked by: "end with a subtle hint of an upcoming decision"

**Obvious answers (originality check):**

- The protagonist taps their foot, feels the cold metal rail, thinks about the overdue project, and the last line hints they might quit their job.
- She watches steam rise, feels the warm mug in her hand, wonders if she should ask the barista out, ending with a quiet resolve to speak later.
- He feels the sticky sugar on his fingers, worries about the meeting later, and the final sentence hints at deciding to change careers.
- She notices the gritty texture of the napkin, worries about a text she received, and ends with a hint that she may finally call her estranged sister.
- He feels the vibration of his phone, contemplates whether to order a pastry, and the closing line subtly suggests he will take a different route home.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 35. creative · history · `1a636015a193`

**Q:** Write a short diary entry (3–8 sentences) from the perspective of a merchant in Constantinople during the fall of the city in 1453. The entry should (a) describe the atmosphere of the siege, (b) mention one specific item the merchant hoped to protect, and (c) convey a personal feeling of loss without using the phrase “I feel sad.”

**Path P1:** Diary entry satisfying all three constraints

- `P1.C1` correctness, core, w=1: Describes the atmosphere of the siege ← asked by: "describe the atmosphere of the siege"
- `P1.C2` correctness, core, w=1: Mentions a specific item the merchant hoped to protect ← asked by: "mention one specific item the merchant hoped to protect"
- `P1.C3` expression, core, w=1: Conveys a personal feeling of loss without using the phrase “I feel sad.” ← asked by: "convey a personal feeling of loss without using the phrase “I feel sad.”"

**Obvious answers (originality check):**

- Describes smoky, noisy siege; mentions a chest of spices; expresses grief with phrases like “my heart aches.”
- Notes darkness and cannon fire; mentions a silk rug; conveys loss using “a hollow emptiness settles over me.”
- Writes about panic and fire; mentions a ledger of trade; shows heartbreak without saying “I feel sad.”
- Talks about the roar of cannons and smoke; mentions a family heirloom; expresses emptiness and sorrow indirectly.
- Describes flames and chaos; mentions gold coins in a chest; conveys sorrow with “the city feels empty” and avoids the banned phrase.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 36. creative · science · `9e4b003116e1`

**Q:** Write a short sci‑fi scene (3‑8 sentences) set on a basaltic moon orbiting a gas giant. The scene must (1) introduce the moon’s harsh, low‑gravity landscape, (2) describe the moment a lone astronaut discovers a glowing crystal that emits a low hum, and (3) include a development that forces the astronaut to reconsider the mission’s objective. Do not use any of the words: "dark", "silent", "mysterious", "unexpected".

**Path P1:** Creative sci‑fi scene meeting all constraints

- `P1.C1` correctness, core, w=1: Introduces the moon’s harsh, low‑gravity landscape ← asked by: "introduce the moon’s harsh, low‑gravity landscape"
- `P1.C2` correctness, core, w=1: Describes the moment a lone astronaut discovers a glowing crystal that emits a low hum ← asked by: "describe the moment a lone astronaut discovers a glowing crystal that emits a low hum"
- `P1.C3` correctness, core, w=1: Includes a development that forces the astronaut to reconsider the mission’s objective ← asked by: "include a development that forces the astronaut to reconsider the mission’s objective"
- `P1.C4` expression, core, w=1: Does not use any of the prohibited words ← asked by: "Do not use any of the words: "dark", "silent", "mysterious", "unexpected""

**Obvious answers (originality check):**

- The astronaut steps onto the cratered, low‑gravity surface, notes the thin air, then finds a crystal glowing in a fissure, and later realizes its energy could power the colony, changing the mission.
- The scene opens with a description of jagged rocks and low gravity, the astronaut spots a humming crystal, and then discovers it contradicts the mission to collect only geological samples.
- The writer describes the moon’s barren plains, the astronaut uncovers a crystal that sings, and then must decide whether to abandon the original survey to study the crystal.
- The narrative sets the moon’s harsh environment, the astronaut finds a crystal emitting a low hum, and then the mission is jeopardized because the crystal signals an unknown phenomenon.
- The scene paints the low‑gravity landscape, the astronaut discovers a glowing crystal, and then faces a choice between reporting it or continuing the planned scientific objectives.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 37. creative · technology · `6878445611ca`

**Q:** In a short scene of 3‑8 sentences, imagine a product launch at a future technology conference where a new AI‑powered personal assistant called "EchoMate" is unveiled. Write the scene using present‑tense narration. The scene must (1) name the product, (2) describe one unique capability of the assistant, (3) include a reaction from an audience member, and (4) end with a tagline of exactly six words.

**Path P1:** All required elements of the scene are present and follow the brief.

- `P1.C1` correctness, core, w=1: Names the product EchoMate ← asked by: "name the product"
- `P1.C2` correctness, core, w=1: Describes a unique capability of EchoMate ← asked by: "describe one unique capability of the assistant"
- `P1.C3` correctness, core, w=1: Includes a reaction from an audience member ← asked by: "include a reaction from an audience member"
- `P1.C4` correctness, core, w=1: Ends with a tagline consisting of exactly six words ← asked by: "end with a tagline of exactly six words"
- `P1.C5` expression, core, w=1: Uses present‑tense narration throughout ← asked by: "using present‑tense narration"

**Obvious answers (originality check):**

- The presenter unveils EchoMate, which can translate any language instantly; a journalist gasps; tagline: "Speak any language, instantly understood."
- At the conference, EchoMate demonstrates real‑time emotional tone adjustment; an engineer claps; tagline: "Feel understood, every word matters."
- The demo shows EchoMate predicting user needs before they speak; an audience member laughs; tagline: "Your thoughts, answered before you ask."
- EchoMate displays holographic reminders on demand; a designer nods approvingly; tagline: "Your day, organized in light."
- The launch highlights EchoMate’s ability to compose music on the fly; a musician cheers; tagline: "Create sound, instantly, without effort."

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8
