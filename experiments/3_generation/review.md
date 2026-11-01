# Phase 3: generated question review

33 questions. For each one, tick every item that holds. The gate passes when at least 85% of questions pass every item that applies to them.

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

## 4. factual · ethics · `5a492c637640`

**Q:** In a short paragraph (3‑8 sentences), name the two conditions of the principle of double effect and give one distinct example that illustrates each condition.

**Path P1:** Correct answer lists both conditions and supplies an example for each.

- `P1.C1` completeness, core, w=1: Names both conditions of the principle of double effect ← asked by: "name the two conditions of the principle of double effect"
- `P1.C2` correctness, core, w=1: Provides a valid example that illustrates the first condition ← asked by: "give one distinct example that illustrates each condition"
- `P1.C3` correctness, core, w=1: Provides a valid example that illustrates the second condition ← asked by: "give one distinct example that illustrates each condition"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 5. factual · economics · `886e0fcd1e3d`

**Q:** In a short paragraph of 3–6 sentences, list three distinct types of unemployment and give one concrete example for each type.

**Path P1:** List three distinct types of unemployment and provide an example for each.

- `P1.C1` completeness, core, w=1: Names three distinct types of unemployment ← asked by: "list three distinct types of unemployment"
- `P1.C2` correctness, core, w=1: Provides a correct example for the first type named ← asked by: "give one concrete example for each type"
- `P1.C3` correctness, non-core, w=0.5: Provides a correct example for the second type named ← asked by: "give one concrete example for each type"
- `P1.C4` correctness, non-core, w=0.5: Provides a correct example for the third type named ← asked by: "give one concrete example for each type"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 6. factual · environment · `476bdbe5578d`

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

## 7. factual · health · `17b9d268178a`

**Q:** In a short paragraph (3-8 sentences), name the three main macronutrients required by the human body and state one primary function of each.

**Path P1:** Correctly identifies three macronutrients and gives a primary function for each.

- `P1.C1` completeness, core, w=1: Names three distinct macronutrients required by the human body ← asked by: "name the three main macronutrients"
- `P1.C2` correctness, core, w=1: States a primary function of the first macronutrient named ← asked by: "state one primary function of each"
- `P1.C3` correctness, core, w=1: States a primary function of the second macronutrient named ← asked by: "state one primary function of each"
- `P1.C4` correctness, core, w=1: States a primary function of the third macronutrient named ← asked by: "state one primary function of each"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 8. factual · literature · `b0affe8aae1b`

**Q:** In a short paragraph (3–8 sentences), name three distinct literary movements of the 19th century and give one characteristic work (title and author) associated with each.

**Path P1:** Provide three 19th‑century literary movements and a characteristic work for each.

- `P1.C1` completeness, core, w=1: Names a distinct 19th‑century literary movement (first of three) ← asked by: "name three distinct literary movements of the 19th century"
- `P1.C2` correctness, core, w=1: Gives a valid characteristic work (title and author) associated with the first named movement ← asked by: "give one characteristic work (title and author) associated with each"
- `P1.C3` completeness, core, w=1: Names a distinct 19th‑century literary movement (second of three) ← asked by: "name three distinct literary movements of the 19th century"
- `P1.C4` correctness, core, w=1: Gives a valid characteristic work (title and author) associated with the second named movement ← asked by: "give one characteristic work (title and author) associated with each"
- `P1.C5` completeness, core, w=1: Names a distinct 19th‑century literary movement (third of three) ← asked by: "name three distinct literary movements of the 19th century"
- `P1.C6` correctness, core, w=1: Gives a valid characteristic work (title and author) associated with the third named movement ← asked by: "give one characteristic work (title and author) associated with each"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 9. factual · geography · `c555e910c2cb`

**Q:** In a short paragraph of 3–8 sentences, name five of the world’s longest rivers and, for each, state the continent on which it primarily flows.

**Path P1:** Provides five distinct longest rivers and correctly identifies their primary continents.

- `P1.C1` completeness, core, w=1: Provides five distinct river names that are among the five longest rivers globally ← asked by: "name five ... longest rivers"
- `P1.C2` correctness, core, w=1: For the first river named, states the correct continent on which it primarily flows ← asked by: "state the continent"
- `P1.C3` correctness, core, w=1: For the second river named, states the correct continent on which it primarily flows ← asked by: "state the continent"
- `P1.C4` correctness, core, w=1: For the third river named, states the correct continent on which it primarily flows ← asked by: "state the continent"
- `P1.C5` correctness, core, w=1: For the fourth river named, states the correct continent on which it primarily flows ← asked by: "state the continent"
- `P1.C6` correctness, core, w=1: For the fifth river named, states the correct continent on which it primarily flows ← asked by: "state the continent"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 10. factual · everyday life · `3d813378c122`

**Q:** In a short paragraph (3–8 sentences), list three distinct bedtime routines that many adults follow and state the usual order of steps for each routine (e.g., brush teeth → change into pajamas → read a book).

**Path P1:** Provides three distinct bedtime routines each with its typical step order.

- `P1.C1` completeness, core, w=1: Names the first distinct bedtime routine ← asked by: "list three distinct bedtime routines"
- `P1.C2` correctness, core, w=1: States the typical order of steps for the first routine ← asked by: "state the usual order of steps for each routine"
- `P1.C3` completeness, core, w=1: Names the second distinct bedtime routine ← asked by: "list three distinct bedtime routines"
- `P1.C4` correctness, core, w=1: States the typical order of steps for the second routine ← asked by: "state the usual order of steps for each routine"
- `P1.C5` completeness, core, w=1: Names the third distinct bedtime routine ← asked by: "list three distinct bedtime routines"
- `P1.C6` correctness, core, w=1: States the typical order of steps for the third routine ← asked by: "state the usual order of steps for each routine"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 11. analytical · science · `4cb875e3c8cc`

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

## 15. analytical · history · `17c1b10632b5`

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

## 16. explanatory · technology · `e9829aabdcd6`

**Q:** In a short paragraph (3‑8 sentences), explain how cloud computing enables small businesses to scale their IT resources on demand.

**Path P1:** Explanation of cloud‑based scaling for small businesses

- `P1.C1` completeness, core, w=1: States that cloud computing offers a shared pool of computing resources (such as servers, storage, and networking) that can be provisioned dynamically ← asked by: "explain how cloud computing enables small businesses to scale their IT resources on demand"
- `P1.C2` correctness, core, w=1: Accurately explains that this dynamic provisioning lets small businesses increase or decrease resource usage quickly in response to demand ← asked by: "explain how cloud computing enables small businesses to scale their IT resources on demand"
- `P1.C3` reasoning, non-core, w=0.5: Provides a reason why this flexibility reduces the need for upfront hardware investment, for example by using a pay‑as‑you‑go pricing model ← asked by: "explain how cloud computing enables small businesses to scale their IT resources on demand"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 17. explanatory · ethics · `91798e725180`

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

## 18. explanatory · economics · `669bce9c85fb`

**Q:** In a short paragraph of 3–6 sentences, explain how a depreciation of a country's currency influences its export competitiveness. Provide one mechanism that connects the change in exchange rate to export volumes.

**Path P1:** Explanation that links depreciation to export competitiveness via a price‑effect mechanism

- `P1.C1` completeness, core, w=1: Explains how a depreciation of a country's currency influences its export competitiveness ← asked by: "explain how a depreciation of a country's currency influences its export competitiveness"
- `P1.C2` correctness, core, w=1: States that depreciation lowers the foreign‑currency price of the country's exported goods ← asked by: "explain how a depreciation of a country's currency influences its export competitiveness"
- `P1.C3` reasoning, core, w=1: Provides one mechanism that links the exchange‑rate change to export volumes (e.g., lower prices increase foreign demand) ← asked by: "provide one mechanism that connects the change in exchange rate to export volumes"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 19. explanatory · environment · `1e9d95d9130f`

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

## 20. explanatory · literature · `c08ec38ec72f`

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

## 21. explanatory · geography · `3f8052a62a58`

**Q:** Explain why mountain ranges often create dry regions on their leeward side (rain shadows). In a short paragraph of 3–8 sentences, state the main atmospheric mechanism responsible, describe how it leads to reduced precipitation on the leeward side, and give one supporting fact that illustrates this process.

**Path P1:** Explain the orographic precipitation mechanism that produces a rain shadow.

- `P1.C1` correctness, core, w=1: States the main atmospheric mechanism responsible for rain shadows (orographic lift causing precipitation on the windward side and descending dry air on the leeward side). ← asked by: "state the main atmospheric mechanism responsible"
- `P1.C2` reasoning, core, w=1: Describes how the mechanism leads to reduced precipitation on the leeward side (descending air warms, its relative humidity drops, and precipitation decreases). ← asked by: "describe how it leads to reduced precipitation on the leeward side"
- `P1.C3` completeness, core, w=1: Gives one supporting fact that illustrates the process (e.g., temperature drops ~6 °C per km of ascent, or cites a known rain‑shadow region such as the leeward side of the Cascades). ← asked by: "give one supporting fact that illustrates this process"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 22. explanatory · everyday life · `610c46d48e48`

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

## 23. explanatory · history · `3dadfd69ad7c`

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

## 24. explanatory · science · `23575fb39cfd`

**Q:** Explain why a hot‑air balloon rises when the air inside it is heated. Answer in a short paragraph (3‑8 sentences).

**Path P1:** The balloon rises because heating the air inside reduces its density, creating a buoyant upward force.

- `P1.C1` correctness, core, w=1: States that heating the air inside the balloon reduces its density compared to the surrounding cooler air ← asked by: "Explain why a hot‑air balloon rises when the air inside it is heated"
- `P1.C2` reasoning, core, w=1: Links the lower density of the heated air to a net upward buoyant force that lifts the balloon ← asked by: "Explain why a hot‑air balloon rises when the air inside it is heated"
- `P1.C3` completeness, core, w=1: Mentions that the surrounding air is cooler (or at ambient temperature) providing the contrast needed for lift ← asked by: "Explain why a hot‑air balloon rises when the air inside it is heated"

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 25. creative · ethics · `4881228365fa`

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

## 26. creative · economics · `14f014e48366`

**Q:** Write a short scene (3–5 sentences) in which a college student learns that the price of their favorite coffee has increased. The scene must (1) mention the price increase, (2) show the student's internal thought about whether to keep buying it, and (3) include a brief reference to an alternative beverage they could choose instead.

**Path P1:** The answer is a short scene that satisfies all brief constraints.

- `P1.C1` correctness, core, w=1: Mentions the price increase ← asked by: "mention the price increase"
- `P1.C2` correctness, core, w=1: Shows the student's internal thought about whether to keep buying it ← asked by: "show the student's internal thought"
- `P1.C3` correctness, core, w=1: Includes a brief reference to an alternative beverage ← asked by: "include a brief reference to an alternative beverage"
- `P1.C4` expression, non-core, w=0.5: Contains a turn or development where the scene moves from noticing the price increase to the student's decision ← craft test (by design)
- `P1.C5` expression, non-core, w=0.5: Does not use any of: "price is too high", "I can't afford it", "cheaper alternative" ← craft test (by design)

**Obvious answers (originality check):**

- Student sighs about the coffee price hike, thinks about budget, and mentions switching to tea.
- Student notes the coffee now costs $5, worries about cost, and considers buying a cheaper iced latte.
- Student reacts to the price increase, internally debates, and mentions buying a generic brand instead.
- Student hears about the coffee price rise, reflects on spending, and suggests trying a bottled water.
- Student sees the coffee price go up, thinks about saving money, and mentions ordering a cheaper instant coffee.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 27. creative · environment · `2b28e1af770f`

**Q:** Write a short scene (3 to 8 sentences) that depicts a coastal mangrove forest after a storm surge, showing the first signs of ecological recovery. Use vivid sensory details and include a turn where a character reflects on resilience.

**Path P1:** All required elements are present

- `P1.C1` correctness, core, w=1: Shows a coastal mangrove forest setting that has experienced a storm surge ← asked by: "depicts a coastal mangrove forest after a storm surge"
- `P1.C2` correctness, core, w=1: Describes the first signs of ecological recovery ← asked by: "showing the first signs of ecological recovery"
- `P1.C3` correctness, core, w=1: Includes at least one vivid sensory detail ← asked by: "Use vivid sensory details"
- `P1.C4` expression, core, w=1: Contains a turn where a character reflects on resilience ← asked by: "include a turn where a character reflects on resilience"
- `P1.C5` expression, non-core, w=0.5: Does not use any of: "peaceful", "serene", "calm" ← craft test (by design)

**Obvious answers (originality check):**

- The water recedes, the mud glistens, a child spots a new sprout and thinks the forest will thrive again.
- Rain drips from mangrove roots, the salty air smells fresh, a fisherman watches seedlings emerge and feels hopeful.
- Waves pull back, birds return, a teenager notes the green leaves and whispers that nature heals.
- The storm's aftermath shows mud drying, a turtle crawls onto a new shoot, and a guide remarks on the forest's resilience.
- Leaves glisten with remaining droplets, a scientist observes new growth and concludes the ecosystem is recovering.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 28. creative · literature · `30cfecdb54df`

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

## 29. creative · geography · `05c2f2ca70a4`

**Q:** Write a short radio news script (3–8 sentences) announcing the discovery of a floating island in the middle of the Great Lakes. Include the island’s geographic location, a vivid description of its appearance, and one surprising ecological feature.

**Path P1:** Answer follows the required content and avoids prohibited clichés.

- `P1.C1` correctness, core, w=1: States the island’s geographic location (e.g., which Great Lake and approximate position). ← asked by: "geographic location"
- `P1.C2` correctness, core, w=1: Provides a vivid description of the island’s appearance. ← asked by: "vivid description of its appearance"
- `P1.C3` correctness, core, w=1: Mentions one surprising ecological feature of the island. ← asked by: "one surprising ecological feature"
- `P1.C4` expression, non-core, w=0.5: Does not use any of: "once upon a time", "magical", "mysterious". ← craft test (by design)

**Obvious answers (originality check):**

- The island is located in Lake Superior near its center, described as a grassy mound with scattered birch trees, and it hosts a colony of rare salamanders.
- The island sits in Lake Michigan, appears as a rocky outcrop with cascading waterfalls, and contains a small geothermal hot spring supporting unique algae.
- The island drifts in Lake Erie, looks like a floating mat of reeds and cattails, and provides a breeding ground for thousands of migratory birds.
- The island is in Lake Huron, shrouded in mist with a surface covered in luminous bioluminescent algae, creating a glowing shoreline at night.
- The island lies in Lake Ontario, is a sandy speck with remnants of an ancient petrified forest, and contains fossils of extinct fish species.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 30. creative · everyday life · `7cb37a949c50`

**Q:** Write a brief scene of 3–6 sentences describing a person cooking dinner alone, focusing on the protagonist’s internal thoughts, include at least one auditory detail of the kitchen, and end with a subtle hint of an upcoming surprise.

**Path P1:** Meets all creative constraints.

- `P1.C1` correctness, core, w=1: Includes the internal thoughts of the protagonist. ← asked by: "focusing on the protagonist’s internal thoughts"
- `P1.C2` correctness, core, w=1: Provides at least one auditory detail of the kitchen. ← asked by: "include at least one auditory detail of the kitchen"
- `P1.C3` correctness, core, w=1: Ends with a subtle hint of an upcoming surprise. ← asked by: "end with a subtle hint of an upcoming surprise"
- `P1.C4` expression, non-core, w=0.5: Shows rather than tells the scene (uses descriptive language). ← craft test (by design)
- `P1.C5` expression, non-core, w=0.5: Does not use any of the following cliché phrases: "home‑cooked meal", "food for the soul", "sizzle of the pan", "taste of nostalgia". ← craft test (by design)

**Obvious answers (originality check):**

- The cook thinks about a recent argument while chopping onions, hears the timer beep, and the scene ends with a sudden knock suggesting a visitor.
- The protagonist reflects on the day’s fatigue as the pot boils, hears the hiss of steam, and the final line hints at an unexpected delivery.
- Internal monologue about loneliness accompanies the clatter of dishes, the oven timer dings, and the ending mentions a mysterious text arriving.
- The narrator worries about tomorrow while the skillet sizzles, hears a distant radio song, and the last sentence hints at a surprise phone call.
- The chef muses on missed opportunities as the knife hits the cutting board, hears the faucet drip, and the scene closes with a subtle hint of an unannounced guest.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 31. creative · history · `b687bcd90776`

**Q:** Write a short speech (3–8 sentences) that a women’s suffrage activist might deliver at a 1910 rally in London. The speech must (a) call for women’s right to vote, (b) reference the recent 1910 women’s suffrage march, and (c) convey the speaker’s personal conviction. Do not use the cliché phrase “the time is now.” Ensure the speech shows the speaker’s emotions rather than simply stating them.

**Path P1:** A short rally speech meeting all constraints.

- `P1.C1` correctness, core, w=1: Includes a direct call for women’s right to vote. ← asked by: "call for women’s right to vote"
- `P1.C2` correctness, core, w=1: Mentions the 1910 women’s suffrage march. ← asked by: "reference the recent 1910 women’s suffrage march"
- `P1.C3` expression, core, w=1: Conveys personal conviction using first‑person language. ← asked by: "convey the speaker’s personal conviction"
- `P1.C4` expression, non-core, w=0.5: Shows emotions through vivid description rather than merely stating feelings. ← asked by: "show the speaker’s emotions rather than simply stating them"
- `P1.C5` correctness, non-core, w=0.5: Does not contain the exact phrase “the time is now.” ← asked by: "Do not use the cliché phrase “the time is now.”"

**Obvious answers (originality check):**

- A speech that repeats a simple call for the vote, mentions the 1910 march, and says “I believe we must win the vote.”
- A short rally address that states “Women deserve the vote,” cites the march, and uses personal language like “my heart is with the cause.”
- An emotional speech that declares “Grant us the vote,” references the recent march, and includes a line such as “I will fight for this right.”
- A brief speech that calls for voting rights, notes the 1910 march, and expresses conviction with phrases like “I am determined to see this happen.”
- A rally speech that urges women’s suffrage, mentions the march, avoids the banned phrase, and shows feeling through vivid words such as “the fire of hope burns within me.”

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 32. creative · science · `13360f60b1fe`

**Q:** Write a short sci‑fi scene (3‑8 sentences) set aboard a generation starship where an artificial intelligence caretaker discovers a concealed garden of Earth plants. The scene should introduce the setting, describe the discovery, and include a development that creates a moral dilemma among the crew.

**Path P1:** Meets all brief constraints for the sci‑fi scene

- `P1.C1` correctness, core, w=1: Contains between 3 and 8 sentences. ← asked by: "3‑8 sentences"
- `P1.C2` correctness, core, w=1: Introduces the setting (mentions the generation starship, deep‑space environment, or similar). ← asked by: "introduce the setting"
- `P1.C3` correctness, core, w=1: Describes the discovery of a concealed garden of Earth plants by the AI caretaker. ← asked by: "describe the discovery"
- `P1.C4` correctness, core, w=1: Includes a development that creates a moral dilemma among the crew. ← asked by: "include a development that creates a moral dilemma among the crew"
- `P1.C5` expression, non-core, w=0.5: Shows the scene through sensory details or actions rather than merely stating facts. ← craft test (by design)
- `P1.C6` expression, non-core, w=0.5: Does not use any of the following clichés: "out of this world", "the sky was the limit", "cutting edge", "beyond imagination", "reach for the stars". ← craft test (by design)

**Obvious answers (originality check):**

- A straightforward description that mentions the starship, the AI, the hidden garden, and the crew's ethical debate.
- A scene that opens with the ship’s corridors, then the AI discovers a greenhouse, followed by crew arguing about preserving the plants.
- A narrative from the AI’s perspective describing the scent of Earth flowers and ending with a moral choice for the crew.
- A brief scene that includes the setting, the concealed garden, and a sudden conflict over resource allocation.
- A simple plot where the AI reveals the garden, the crew reacts, and a moral dilemma is presented.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 33. creative · technology · `6878445611ca`

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
