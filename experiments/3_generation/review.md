# Phase 3: generated question review

29 questions. For each one, tick every item that holds. The gate passes when at least 85% of questions pass every item that applies to them.

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

## 7. factual · literature · `2e67ba664d8f`

**Q:** In a short paragraph (3–8 sentences), name three distinct poems by Emily Dickinson and give the year each was first published (or first appeared in a collection).

**Path P1:** Provides three poems by Emily Dickinson and the year each was first published or first appeared in a collection.

- `P1.C1` completeness, core, w=1: Names three distinct poems by Emily Dickinson ← asked by: "name three distinct poems by Emily Dickinson"
- `P1.C2` correctness, core, w=1: Provides the year each poem was first published or first appeared in a collection ← asked by: "give the year each was first published (or first appeared in a collection)"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 8. factual · geography · `c555e910c2cb`

**Q:** In a short paragraph of 3–8 sentences, name five of the world’s longest rivers and, for each, state the continent on which it primarily flows.

**Path P1:** Provides five distinct longest rivers and correctly identifies their primary continents.

- `P1.C1` completeness, core, w=1: Provides five distinct river names that are among the five longest rivers globally ← asked by: "name five ... longest rivers"
- `P1.C2` correctness, core, w=1: For the first river named, states the correct continent on which it primarily flows ← asked by: "state the continent"
- `P1.C3` correctness, core, w=1: For the second river named, states the correct continent on which it primarily flows ← asked by: "state the continent"
- `P1.C4` correctness, core, w=1: For the third river named, states the correct continent on which it primarily flows ← asked by: "state the continent"
- `P1.C5` correctness, core, w=1: For the fourth river named, states the correct continent on which it primarily flows ← asked by: "state the continent"
- `P1.C6` correctness, core, w=1: For the fifth river named, states the correct continent on which it primarily flows ← asked by: "state the continent"

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

## 10. analytical · technology · `46b076f456cf`

**Q:** Argue whether the tech industry should prioritize developing quantum computing over advancing artificial intelligence. In a short paragraph (3‑8 sentences), present one position and support it with at least two distinct reasons.

**Path P1:** Position: quantum computing should be prioritized over AI

- `P1.C1` completeness, core, w=1: States the position that quantum computing should be prioritized over AI ← asked by: "present one position"
- `P1.C2` reasoning, core, w=1: Provides a first distinct reason that supports the position ← asked by: "support it with at least two distinct reasons"
- `P1.C3` reasoning, non-core, w=0.5: Provides a second distinct reason that supports the position ← asked by: "support it with at least two distinct reasons"
- `P1.C4` correctness, core, w=1: Each reason given is factually accurate ← asked by: "support it with at least two distinct reasons"

**Path P2:** Position: AI should be prioritized over quantum computing

- `P2.C1` completeness, core, w=1: States the position that artificial intelligence should be prioritized over quantum computing ← asked by: "present one position"
- `P2.C2` reasoning, core, w=1: Provides a first distinct reason that supports the position ← asked by: "support it with at least two distinct reasons"
- `P2.C3` reasoning, non-core, w=0.5: Provides a second distinct reason that supports the position ← asked by: "support it with at least two distinct reasons"
- `P2.C4` correctness, core, w=1: Each reason given is factually accurate ← asked by: "support it with at least two distinct reasons"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 11. analytical · ethics · `082591e7ec4e`

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

## 12. analytical · economics · `e82fb3602421`

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

## 13. analytical · environment · `5d564b58c11c`

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

## 14. analytical · health · `80b5228e62c0`

**Q:** In a short paragraph (3–8 sentences), argue whether implementing a tax on sugar‑sweetened beverages is an effective public‑health strategy to reduce obesity. Choose one side, present at least two supporting points, and acknowledge a counterargument from the opposite side.

**Path P1:** Path supporting the implementation of a sugar‑sweetened beverage tax

- `P1.C1` completeness, core, w=1: States the position that a tax on sugar‑sweetened beverages should be implemented ← asked by: "argue whether implementing a tax on sugar‑sweetened beverages is an effective public‑health strategy to reduce obesity. Choose one side"
- `P1.C2` reasoning, core, w=0.5: Provides a first distinct supporting point that includes a reason linking it to the claim ← asked by: "present at least two supporting points"
- `P1.C3` correctness, core, w=0.5: Provides a second distinct supporting point that includes a reason linking it to the claim ← asked by: "present at least two supporting points"
- `P1.C4` completeness, core, w=0.5: Acknowledges a counterargument from the opposite side ← asked by: "acknowledge a counterargument from the opposite side"

**Path P2:** Path opposing the implementation of a sugar‑sweetened beverage tax

- `P2.C1` completeness, core, w=1: States the position that a tax on sugar‑sweetened beverages should not be implemented ← asked by: "argue whether implementing a tax on sugar‑sweetened beverages is an effective public‑health strategy to reduce obesity. Choose one side"
- `P2.C2` reasoning, core, w=0.5: Provides a first distinct supporting point that includes a reason linking it to the claim ← asked by: "present at least two supporting points"
- `P2.C3` correctness, core, w=0.5: Provides a second distinct supporting point that includes a reason linking it to the claim ← asked by: "present at least two supporting points"
- `P2.C4` completeness, core, w=0.5: Acknowledges a counterargument from the opposite side ← asked by: "acknowledge a counterargument from the opposite side"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 15. analytical · literature · `595e6e0cc0b2`

**Q:** In a short paragraph (3–8 sentences), argue whether James Joyce’s *Ulysses* should be understood primarily as a modernist experiment in narrative technique or as a commentary on Irish nationalism, and support your view with at least two distinct pieces of textual or historical evidence.

**Path P1:** Position: *Ulysses* is primarily a modernist experiment in narrative technique

- `P1.C1` correctness, core, w=1: States the position that *Ulysses* should be understood primarily as a modernist experiment in narrative technique ← asked by: "should be understood primarily as a modernist experiment in narrative technique"
- `P1.C2` completeness, core, w=0.5: Provides at least two distinct pieces of textual or historical evidence that support the modernist experiment position ← asked by: "support your view with at least two distinct pieces of textual or historical evidence"
- `P1.C3` reasoning, core, w=1: Explains how the provided evidence demonstrates that *Ulysses* functions primarily as a modernist experiment in narrative technique ← asked by: "support your view with at least two distinct pieces of textual or historical evidence"

**Path P2:** Position: *Ulysses* is primarily a commentary on Irish nationalism

- `P2.C1` correctness, core, w=1: States the position that *Ulysses* should be understood primarily as a commentary on Irish nationalism ← asked by: "should be understood primarily as a commentary on Irish nationalism"
- `P2.C2` completeness, core, w=0.5: Provides at least two distinct pieces of textual or historical evidence that support the Irish nationalism commentary position ← asked by: "support your view with at least two distinct pieces of textual or historical evidence"
- `P2.C3` reasoning, core, w=1: Explains how the provided evidence shows that *Ulysses* functions primarily as a commentary on Irish nationalism ← asked by: "support your view with at least two distinct pieces of textual or historical evidence"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 16. analytical · geography · `e4a2b3b2341d`

**Q:** In a short paragraph of 3–8 sentences, argue whether plate tectonics or climate change is the primary driver of the recent increase in coastal erosion along the Pacific Northwest coast. Choose one factor, state the claim, and provide at least one piece of supporting evidence linking that factor to the erosion.

**Path P1:** Plate tectonics is the primary driver of recent coastal erosion in the Pacific Northwest

- `P1.C1` completeness, core, w=1: States the claim that plate tectonics is the primary driver of recent coastal erosion in the Pacific Northwest ← asked by: "state the claim"
- `P1.C2` correctness, non-core, w=0.5: Provides at least one piece of supporting evidence linking plate tectonics to the increased coastal erosion ← asked by: "provide at least one piece of supporting evidence"
- `P1.C3` reasoning, core, w=1: Explains how the provided evidence supports the claim that plate tectonics is the primary driver ← asked by: "provide at least one piece of supporting evidence"

**Path P2:** Climate change is the primary driver of recent coastal erosion in the Pacific Northwest

- `P2.C1` completeness, core, w=1: States the claim that climate change is the primary driver of recent coastal erosion in the Pacific Northwest ← asked by: "state the claim"
- `P2.C2` correctness, non-core, w=0.5: Provides at least one piece of supporting evidence linking climate change to the increased coastal erosion ← asked by: "provide at least one piece of supporting evidence"
- `P2.C3` reasoning, core, w=1: Explains how the provided evidence supports the claim that climate change is the primary driver ← asked by: "provide at least one piece of supporting evidence"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 17. analytical · everyday life · `bb2a1833528d`

**Q:** In a short paragraph (3–8 sentences), argue whether checking social media before bedtime improves or harms sleep quality, and support your argument with at least two distinct reasons.

**Path P1:** Position that checking social media before bedtime harms sleep quality

- `P1.C1` correctness, core, w=1: States the position that checking social media before bedtime harms sleep quality ← asked by: "argue whether checking social media before bedtime improves or harms sleep quality"
- `P1.C2` completeness, core, w=1: Provides at least two distinct reasons supporting the claim ← asked by: "support your argument with at least two distinct reasons"
- `P1.C3` reasoning, core, w=1: Explains how each reason leads to the claimed effect on sleep quality ← asked by: "support your argument with at least two distinct reasons"

**Path P2:** Position that checking social media before bedtime improves sleep quality

- `P2.C1` correctness, core, w=1: States the position that checking social media before bedtime improves sleep quality ← asked by: "argue whether checking social media before bedtime improves or harms sleep quality"
- `P2.C2` completeness, core, w=1: Provides at least two distinct reasons supporting the claim ← asked by: "support your argument with at least two distinct reasons"
- `P2.C3` reasoning, core, w=1: Explains how each reason leads to the claimed effect on sleep quality ← asked by: "support your argument with at least two distinct reasons"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 18. analytical · history · `17c1b10632b5`

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

## 19. explanatory · technology · `e9829aabdcd6`

**Q:** In a short paragraph (3‑8 sentences), explain how cloud computing enables small businesses to scale their IT resources on demand.

**Path P1:** Explanation of cloud‑based scaling for small businesses

- `P1.C1` completeness, core, w=1: States that cloud computing offers a shared pool of computing resources (such as servers, storage, and networking) that can be provisioned dynamically ← asked by: "explain how cloud computing enables small businesses to scale their IT resources on demand"
- `P1.C2` correctness, core, w=1: Accurately explains that this dynamic provisioning lets small businesses increase or decrease resource usage quickly in response to demand ← asked by: "explain how cloud computing enables small businesses to scale their IT resources on demand"
- `P1.C3` reasoning, non-core, w=0.5: Provides a reason why this flexibility reduces the need for upfront hardware investment, for example by using a pay‑as‑you‑go pricing model ← asked by: "explain how cloud computing enables small businesses to scale their IT resources on demand"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 20. explanatory · ethics · `91798e725180`

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

## 21. explanatory · economics · `669bce9c85fb`

**Q:** In a short paragraph of 3–6 sentences, explain how a depreciation of a country's currency influences its export competitiveness. Provide one mechanism that connects the change in exchange rate to export volumes.

**Path P1:** Explanation that links depreciation to export competitiveness via a price‑effect mechanism

- `P1.C1` completeness, core, w=1: Explains how a depreciation of a country's currency influences its export competitiveness ← asked by: "explain how a depreciation of a country's currency influences its export competitiveness"
- `P1.C2` correctness, core, w=1: States that depreciation lowers the foreign‑currency price of the country's exported goods ← asked by: "explain how a depreciation of a country's currency influences its export competitiveness"
- `P1.C3` reasoning, core, w=1: Provides one mechanism that links the exchange‑rate change to export volumes (e.g., lower prices increase foreign demand) ← asked by: "provide one mechanism that connects the change in exchange rate to export volumes"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 22. explanatory · environment · `1e9d95d9130f`

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

## 23. explanatory · health · `f3c88f16262f`

**Q:** In a short paragraph (3–8 sentences), explain how the body initiates the blood clotting cascade after a vascular injury.

**Path P1:** Explanation of the physiological sequence that starts the clotting cascade following injury to a blood vessel.

- `P1.C1` completeness, core, w=1: Identifies that vascular injury exposes tissue factor (TF) to blood, triggering the cascade ← asked by: "explain how the body initiates the blood clotting cascade after a vascular injury"
- `P1.C2` correctness, core, w=1: Describes activation of the extrinsic pathway leading to generation of thrombin ← asked by: "explain how the body initiates the blood clotting cascade after a vascular injury"
- `P1.C3` reasoning, core, w=1: Explains that thrombin converts fibrinogen to fibrin, forming a stable clot ← asked by: "explain how the body initiates the blood clotting cascade after a vascular injury"
- `P1.C4` completeness, core, w=1: Mentions that platelets adhere to the injury site and aggregate to form a primary plug ← asked by: "explain how the body initiates the blood clotting cascade after a vascular injury"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 24. explanatory · literature · `c08ec38ec72f`

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

## 25. explanatory · geography · `3f8052a62a58`

**Q:** Explain why mountain ranges often create dry regions on their leeward side (rain shadows). In a short paragraph of 3–8 sentences, state the main atmospheric mechanism responsible, describe how it leads to reduced precipitation on the leeward side, and give one supporting fact that illustrates this process.

**Path P1:** Explain the orographic precipitation mechanism that produces a rain shadow.

- `P1.C1` correctness, core, w=1: States the main atmospheric mechanism responsible for rain shadows (orographic lift causing precipitation on the windward side and descending dry air on the leeward side). ← asked by: "state the main atmospheric mechanism responsible"
- `P1.C2` reasoning, core, w=1: Describes how the mechanism leads to reduced precipitation on the leeward side (descending air warms, its relative humidity drops, and precipitation decreases). ← asked by: "describe how it leads to reduced precipitation on the leeward side"
- `P1.C3` completeness, core, w=1: Gives one supporting fact that illustrates the process (e.g., temperature drops ~6 °C per km of ascent, or cites a known rain‑shadow region such as the leeward side of the Cascades). ← asked by: "give one supporting fact that illustrates this process"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 26. explanatory · everyday life · `610c46d48e48`

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

## 27. explanatory · history · `3dadfd69ad7c`

**Q:** In a short paragraph (3–8 sentences), explain how the Haitian Revolution resulted in the abolition of slavery in Haiti. Identify one key factor that contributed to this outcome.

**Path P1:** Explanation that the revolution’s military victory of formerly enslaved people forced abolition.

- `P1.C1` completeness, core, w=1: Provides an explanation that the Haitian Revolution directly caused the abolition of slavery by overthrowing colonial rule and establishing a government that outlawed slavery. ← asked by: "explain how the Haitian Revolution resulted in the abolition of slavery"
- `P1.C2` correctness, core, w=1: Identifies the military success of the formerly enslaved rebels as the key factor. ← asked by: "Identify one key factor"
- `P1.C3` reasoning, non-core, w=0.5: Shows reasoning that the rebels' control of territory made abolition possible. ← asked by: "Identify one key factor"

**Path P2:** Explanation that Enlightenment and French revolutionary ideas inspired abolition.

- `P2.C1` completeness, core, w=1: Provides an explanation that the Haitian Revolution led to abolition because revolutionary Enlightenment ideas inspired leaders to declare freedom for all. ← asked by: "explain how the Haitian Revolution resulted in the abolition of slavery"
- `P2.C2` correctness, core, w=1: Identifies the influence of Enlightenment and French revolutionary ideals as the key factor. ← asked by: "Identify one key factor"
- `P2.C3` reasoning, non-core, w=0.5: Shows reasoning that these ideas motivated the revolutionary assembly to pass abolition laws. ← asked by: "Identify one key factor"

**Path P3:** Explanation that external French policy changes forced Haitian abolition.

- `P3.C1` completeness, core, w=1: Provides an explanation that the Haitian Revolution resulted in abolition because the French Republic’s 1794 decree abolishing slavery was adopted and reinforced by Haitian leaders. ← asked by: "explain how the Haitian Revolution resulted in the abolition of slavery"
- `P3.C2` correctness, core, w=1: Identifies the French revolutionary decree of 1794 abolishing slavery as the key factor. ← asked by: "Identify one key factor"
- `P3.C3` reasoning, non-core, w=0.5: Shows reasoning that the decree provided legal legitimacy for Haitian leaders to end slavery. ← asked by: "Identify one key factor"

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
- `P1.C6` expression, core, w=1: Shows the conflict through dialogue or action rather than stating it directly ← craft test (by design)

**Obvious answers (originality check):**

- The journalist hesitates, says "If I publish, they could sue us," then decides to release the story after a colleague warns of public harm.
- The journalist whispers "I can't betray my source," but after seeing the damage caused, declares "The truth must come out" and publishes.
- The journalist looks at the file, mutters "Keeping this secret protects lives," then, after a phone call, says "No, the world deserves to know" and sends it out.
- The journalist debates internally, says "I could ruin careers," then a whistleblower arrives, prompting the line "Enough hiding," and the journalist posts the report.
- The journalist paces, says "If I hide it, the victims suffer," then a news alert flashes, leading to the decisive "It's time to tell everyone" and the story goes live.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8
