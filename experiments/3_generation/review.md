# Phase 3: generated question review

39 questions. For each one, tick every item that holds. The gate passes when at least 85% of questions pass every item that applies to them.

Checklist per question:

1. Task type is right for the question
2. Question is self-contained and answerable in a short paragraph
3. Every criterion is binary and observable
4. Criteria ask for nothing the question doesn't need
5. Criteria don't leak a model sentence to copy
6. Granular enough that a partial answer can meet some criteria
7. Each path is a complete alternative answer, not a part the question requires together with the other paths (analytical / explanatory only)
8. The question's premise and the rubric's facts are correct

## 1. factual · history · `1dadecc3b4e0`

**Q:** In a short paragraph (3–8 sentences), name three distinct inventions that originated during the Industrial Revolution and state the year each was introduced.

**Path P1:** Provides three distinct Industrial Revolution inventions with correct introduction years.

- `P1.C1` completeness, core, w=1: Provides three distinct inventions of the Industrial Revolution (e.g., steam engine, power loom, telegraph).
- `P1.C2` correctness, core, w=1: For the first invention listed, gives the correct year it was introduced (e.g., 1769 for Watt's steam engine).
- `P1.C3` correctness, core, w=1: For the second invention listed, gives the correct year it was introduced.
- `P1.C4` correctness, core, w=1: For the third invention listed, gives the correct year it was introduced.

**Reference answer** (path P1):

> The Industrial Revolution produced many transformative technologies, including James Watt’s improved steam engine, which was introduced in 1769. Another key invention was the power loom, developed by Edmund Cartwright and first put into use in 1785. Finally, Samuel Morse’s electric telegraph, which revolutionized long‑distance communication, was demonstrated in 1837.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 2. factual · science · `e35f2e5583c8`

**Q:** Name three distinct categories of renewable energy sources and give one example of a technology that uses each. Answer in a short paragraph (3‑8 sentences).

**Path P1:** Provides three distinct renewable energy categories with a valid technology example for each.

- `P1.C1` completeness, core, w=1: Names three distinct renewable energy categories.
- `P1.C2` correctness, core, w=1: For the first category named, provides a valid example of a technology that uses it (e.g., solar – photovoltaic panels).
- `P1.C3` correctness, core, w=1: For the second category named, provides a valid example of a technology that uses it (e.g., hydro – hydroelectric dam).
- `P1.C4` correctness, core, w=1: For the third category named, provides a valid example of a technology that uses it (e.g., biomass – biofuel plant).

**Reference answer** (path P1):

> Solar energy, hydroelectric power, and biomass are three distinct categories of renewable energy. Photovoltaic panels convert sunlight directly into electricity, representing a solar technology. Hydroelectric dams harness the kinetic energy of flowing water to generate power, exemplifying a hydro technology. Biomass can be processed into biofuels, such as ethanol, which are used in specialized biofuel plants, illustrating a biomass technology.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 3. factual · technology · `6a51026e61ee`

**Q:** Identify three distinct components of a modern computer's central processing unit (CPU). For each component, state its primary function and give one real‑world technology or product that implements that component. Answer in a short paragraph (3‑8 sentences).

**Path P1:** Lists three CPU components, their functions, and implementation examples.

- `P1.C1` correctness, core, w=1: Names a valid CPU component as the first component (e.g., arithmetic logic unit, control unit, cache).
- `P1.C2` correctness, core, w=1: States the primary function of the first component correctly.
- `P1.C3` completeness, non-core, w=0.5: Provides a correct example of a technology or product that implements the first component.
- `P1.C4` correctness, core, w=1: Names a valid CPU component as the second component, distinct from the first.
- `P1.C5` correctness, core, w=1: States the primary function of the second component correctly.
- `P1.C6` completeness, non-core, w=0.5: Provides a correct example of a technology or product that implements the second component.
- `P1.C7` correctness, core, w=1: Names a valid CPU component as the third component, distinct from the first two.
- `P1.C8` correctness, core, w=1: States the primary function of the third component correctly.
- `P1.C9` completeness, non-core, w=0.5: Provides a correct example of a technology or product that implements the third component.

**Reference answer** (path P1):

> The arithmetic logic unit (ALU) performs the CPU's mathematical and logical operations, such as addition, subtraction, and bitwise comparisons; it is implemented in the Intel Core i9 processor family. The control unit orchestrates the sequencing of instructions, directing data flow between the ALU, registers, and memory, and is realized in AMD's Zen 3 microarchitecture. Finally, the cache provides a small, fast memory hierarchy that stores frequently accessed data and instructions to reduce latency, exemplified by the 8 MB L3 cache in the ARM Cortex‑A78 CPU.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 4. factual · ethics · `741aaa7901e4`

**Q:** In a short paragraph (3‑8 sentences), identify three distinct ethical approaches to animal rights and state one key argument each uses to support its position on animal rights.

**Path P1:** Provides the required factual information about three animal‑rights approaches and their arguments.

- `P1.C1` completeness, core, w=1: Names three distinct ethical approaches to animal rights (e.g., utilitarianism, rights‑based, relational/care ethics).
- `P1.C2` correctness, non-core, w=0.5: Provides a key argument that the first named approach uses to support its position on animal rights.
- `P1.C3` correctness, non-core, w=0.5: Provides a key argument that the second named approach uses to support its position on animal rights.
- `P1.C4` correctness, non-core, w=0.5: Provides a key argument that the third named approach uses to support its position on animal rights.

**Reference answer** (path P1):

> One major approach is utilitarianism, which argues that animals’ capacity to experience pleasure and pain gives them moral consideration, so their suffering should be minimized. A rights‑based perspective, championed by philosophers like Tom Regan, holds that animals are subjects-of-a-life with inherent rights, meaning they should not be used as mere means to human ends. Relational or care ethics emphasizes the moral significance of our relationships with animals, asserting that empathy and responsibility toward them create obligations to protect their well‑being.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 5. factual · economics · `01b534762e93`

**Q:** In a short paragraph of 3–8 sentences, list three distinct ways a government can intervene in a market economy and give one concrete policy example for each way.

**Path P1:** Correct factual answer

- `P1.C1` completeness, core, w=1: Names three distinct types of government intervention in a market economy (e.g., price control, tax/subsidy, regulation).
- `P1.C2` correctness, non-core, w=0.5: Provides a specific, real‑world policy example that illustrates the first type named.
- `P1.C3` correctness, non-core, w=0.5: Provides a specific, real‑world policy example that illustrates the second type named.
- `P1.C4` correctness, non-core, w=0.5: Provides a specific, real‑world policy example that illustrates the third type named.

**Reference answer** (path P1):

> A government can intervene in a market economy through price controls, taxes or subsidies, and regulatory standards. For price controls, the U.S. government imposed rent caps in New York City during the 1970s to limit housing costs. Through taxation, the U.K. introduced a carbon tax on fossil‑fuel producers to discourage emissions. Finally, regulatory standards are used when the European Union enacted the REACH chemical safety regulation, requiring firms to register and test substances before they can be sold.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 6. factual · environment · `290925ed94ab`

**Q:** In a short paragraph (3 to 8 sentences), name three distinct air pollutants that contribute to urban smog, give a primary human activity that emits each pollutant, and mention one health effect associated with each pollutant.

**Path P1:** Correct factual answer

- `P1.C1` completeness, core, w=1: Names three distinct pollutants that contribute to urban smog (e.g., ground‑level ozone, nitrogen oxides, volatile organic compounds)
- `P1.C2` correctness, non-core, w=0.5: Provides a primary anthropogenic source for the first pollutant named
- `P1.C3` correctness, non-core, w=0.5: Provides a primary anthropogenic source for the second pollutant named
- `P1.C4` correctness, non-core, w=0.5: Provides a primary anthropogenic source for the third pollutant named
- `P1.C5` correctness, non-core, w=0.5: States one health effect associated with the first pollutant named
- `P1.C6` correctness, non-core, w=0.5: States one health effect associated with the second pollutant named
- `P1.C7` correctness, non-core, w=0.5: States one health effect associated with the third pollutant named

**Reference answer** (path P1):

> Ground‑level ozone, nitrogen oxides (NOx), and volatile organic compounds (VOCs) are three key pollutants that drive urban smog. Ozone forms when sunlight triggers reactions between NOx and VOCs, which are largely emitted by motor vehicle exhaust. Nitrogen oxides are released primarily from the combustion of fossil fuels in cars and power plants. VOCs come mainly from industrial solvents, gasoline evaporation, and the use of paints and coatings. Exposure to ozone can irritate the respiratory tract and worsen asthma, while NOx can cause inflammation of the lungs and increase susceptibility to infections. VOCs are linked to headaches, dizziness, and can contribute to long‑term damage of the central nervous system.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 7. factual · health · `a4fd29244a3c`

**Q:** In a short paragraph (3–8 sentences), list the three layers of human skin and state one primary function of each layer.

**Path P1:** Correct answer includes all three skin layers and one function for each layer.

- `P1.C1` correctness, core, w=1: Names the epidermis as the outermost layer of the skin
- `P1.C2` completeness, core, w=1: Provides a primary function of the epidermis (e.g., barrier protection, prevention of water loss)
- `P1.C3` correctness, core, w=1: Names the dermis as the middle layer of the skin
- `P1.C4` completeness, core, w=1: Provides a primary function of the dermis (e.g., contains blood vessels, provides strength and elasticity)
- `P1.C5` correctness, core, w=1: Names the hypodermis (subcutaneous tissue) as the deepest layer of the skin
- `P1.C6` completeness, core, w=1: Provides a primary function of the hypodermis (e.g., insulation, energy storage, anchors skin to underlying structures)

**Reference answer** (path P1):

> The outermost layer of human skin is the epidermis, which serves as a protective barrier that prevents pathogens from entering and reduces water loss. Beneath it lies the dermis, the middle layer that contains blood vessels, nerves, and collagen fibers, providing strength, elasticity, and nourishment to the skin. The deepest layer is the hypodermis, or subcutaneous tissue, which insulates the body, stores energy as fat, and anchors the skin to underlying muscles and bones.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 8. factual · literature · `4567a84d2516`

**Q:** In a short paragraph (3–8 sentences), name three distinct novels by Jane Austen and give the year each was first published.

**Path P1:** Answer provides the required three novel‑year pairs.

- `P1.C1` completeness, core, w=1: Provides three distinct novels by Jane Austen, each accompanied by its correct first publication year.
- `P1.C2` correctness, core, w=1: Each novel‑year pair stated is historically accurate (the year matches the novel's first publication).

**Reference answer** (path P1):

> Jane Austen’s novel *Sense and Sensibility* was first published in 1811. Two years later, in 1813, she released *Pride and Prejudice*. Her later work *Emma* appeared in 1815.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 9. factual · geography · `f6fbe2ae1f26`

**Q:** Identify five major terrestrial biomes and, for each, state one key climate characteristic (e.g., temperature range, precipitation pattern). Answer in a short paragraph of 3–8 sentences.

**Path P1:** Provides five major terrestrial biomes with a correct climate characteristic for each.

- `P1.C1` completeness, core, w=1: Lists exactly five distinct major terrestrial biomes (e.g., tropical rainforest, desert, temperate grassland, tundra, Mediterranean).
- `P1.C2` correctness, core, w=1: Gives a correct climate characteristic for the first biome listed.
- `P1.C3` correctness, core, w=1: Gives a correct climate characteristic for the second biome listed.
- `P1.C4` correctness, core, w=1: Gives a correct climate characteristic for the third biome listed.
- `P1.C5` correctness, core, w=1: Gives a correct climate characteristic for the fourth biome listed.
- `P1.C6` correctness, core, w=1: Gives a correct climate characteristic for the fifth biome listed.

**Reference answer** (path P1):

> The tropical rainforest biome experiences high, year‑round temperatures (generally 20‑30 °C) and abundant rainfall exceeding 2000 mm annually. Deserts are characterized by extreme aridity, receiving less than 250 mm of precipitation per year and having large diurnal temperature swings. Temperate grasslands have moderate temperatures with hot summers and cold winters, and they receive moderate precipitation (about 500‑900 mm) that is concentrated in the growing season. Tundra regions are defined by very low temperatures, often below freezing for most of the year, and low precipitation, typically less than 250 mm, mostly as snow. Mediterranean biomes experience mild, wet winters and hot, dry summers, with annual precipitation ranging from 300‑900 mm.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 10. factual · everyday life · `e78b792f3c20`

**Q:** In a short paragraph (3–8 sentences), list four typical items that people purchase during a weekly grocery shop and state the usual store section where each item is found (e.g., apples in produce).

**Path P1:** Lists four common grocery items and their typical store sections.

- `P1.C1` completeness, core, w=1: Names the first grocery item (any common weekly purchase).
- `P1.C2` correctness, core, w=1: Specifies the correct store section for the first item.
- `P1.C3` completeness, non-core, w=0.5: Names a second grocery item distinct from the first.
- `P1.C4` correctness, non-core, w=0.5: Specifies the correct store section for the second item.
- `P1.C5` completeness, non-core, w=0.5: Names a third grocery item distinct from the first two.
- `P1.C6` correctness, non-core, w=0.5: Specifies the correct store section for the third item.
- `P1.C7` completeness, non-core, w=0.5: Names a fourth grocery item distinct from the first three.
- `P1.C8` correctness, non-core, w=0.5: Specifies the correct store section for the fourth item.

**Reference answer** (path P1):

> A typical weekly grocery shop might include apples, which are found in the produce section; milk, located in the dairy aisle; chicken breasts, stocked in the meat department; and canned beans, which are placed in the canned goods aisle.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 11. analytical · science · `845c66360021`

**Q:** Bioluminescence in marine organisms can be explained by two main hypotheses: (1) a defensive hypothesis, which proposes that organisms emit light to startle, distract, or deter predators; and (2) a communication hypothesis, which suggests that light is used to attract mates or coordinate group behaviors. In a short paragraph (3‑8 sentences), evaluate these two hypotheses and argue which one you find more convincing, providing supporting scientific evidence for each.

**Path P1:** Argues that the defensive hypothesis is more convincing.

- `P1.C1` completeness, core, w=1: Claims the defensive hypothesis is the more convincing explanation.
- `P1.C2` correctness, core, w=1: Provides at least one accurate scientific example or study supporting the defensive hypothesis (e.g., observed flash responses when threatened, predator startle reactions).
- `P1.C3` reasoning, core, w=1: Explains why the defensive evidence makes this hypothesis more convincing than the communication hypothesis.

**Path P2:** Argues that the communication hypothesis is more convincing.

- `P2.C1` completeness, core, w=1: Claims the communication hypothesis is the more convincing explanation.
- `P2.C2` correctness, core, w=1: Provides at least one accurate scientific example or study supporting the communication hypothesis (e.g., documented mating displays using light, coordinated schooling behavior mediated by bioluminescence).
- `P2.C3` reasoning, core, w=1: Explains why the communication evidence makes this hypothesis more convincing than the defensive hypothesis.

**Reference answer** (path P2):

> The communication hypothesis provides the more convincing explanation for marine bioluminescence because many species use light in clearly reproductive or social contexts. For example, the firefly squid (Watasenia scintillans) produces patterned flashes that synchronize during courtship, a behavior documented in field observations showing that males and females coordinate their displays to attract mates (Herring 2007). Similarly, the lantern shark (Etmopterus spinax) emits rhythmic glows that facilitate group cohesion during deep‑sea migrations, as demonstrated by video recordings of coordinated swimming linked to synchronized bioluminescent pulses. These examples show that light directly mediates mating success and group organization, functions that cannot be explained by predator deterrence alone. In contrast, defensive flashing is limited to occasional startle responses and does not account for the elaborate, species‑specific signaling patterns observed across diverse taxa, making the communication hypothesis the stronger overall account.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 12. analytical · technology · `98c16d5d0dc4`

**Q:** Argue whether autonomous vehicles should be required to have a human driver ready to take control at all times. In a short paragraph (3‑8 sentences), present one position and support it with at least one specific reason or piece of evidence.

**Path P1:** Position that a human driver must be present and ready to take control of autonomous vehicles at all times.

- `P1.C1` completeness, core, w=1: States that a human driver must be present and ready to take control of autonomous vehicles at all times.
- `P1.C2` correctness, non-core, w=0.5: Provides a factually accurate reason or piece of evidence supporting the need for a human driver (e.g., cites current safety statistics, mentions known sensor failures, or references existing regulations).
- `P1.C3` reasoning, core, w=1: Links the provided reason/evidence to the claim by explaining how it demonstrates the necessity of a human driver.

**Path P2:** Position that autonomous vehicles should be allowed to operate without a human driver ready to take control.

- `P2.C1` completeness, core, w=1: States that autonomous vehicles should be allowed to operate without a human driver ready to take control.
- `P2.C2` correctness, non-core, w=0.5: Provides a factually accurate reason or piece of evidence supporting fully driverless operation (e.g., mentions reduced reaction times, proven safety records in testing, or efficiency gains).
- `P2.C3` reasoning, core, w=1: Explains how the reason/evidence supports the claim that a human driver is unnecessary.

**Reference answer** (path P1):

> Autonomous vehicles should be required to have a human driver ready to take control at all times. Current sensor suites, while advanced, still experience failures; for example, a 2022 study found that lidar units malfunctioned in 4.3% of real‑world drives, leading to temporary loss of object detection. When a sensor outage occurs, the vehicle can no longer reliably interpret its surroundings, creating an immediate safety risk. A vigilant human driver can recognize these gaps and intervene before an accident occurs, bridging the reliability gap that technology has not yet closed. Therefore, the presence of a human fallback is essential to ensure safety until autonomous systems become truly fault‑tolerant.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 13. analytical · ethics · `edc42079d733`

**Q:** In a short paragraph (3‑8 sentences), argue whether moral relativism offers a satisfactory explanation for moral disagreements between cultures. State your position, give one concrete cross‑cultural example of a moral disagreement, and explain how the example supports your claim.

**Path P1:** Argues that moral relativism provides a satisfactory explanation for cross‑cultural moral disagreements.

- `P1.C1` correctness, core, w=1: The answer states that moral relativism provides a satisfactory explanation for cross‑cultural moral disagreements.
- `P1.C2` completeness, core, w=1: The answer gives a specific cross‑cultural moral disagreement (e.g., differing views on animal consumption between Culture A and Culture B).
- `P1.C3` reasoning, core, w=1: The answer explains how the example shows that moral norms are relative to cultural contexts, thereby supporting the claim.

**Path P2:** Argues that moral relativism does NOT provide a satisfactory explanation for cross‑cultural moral disagreements.

- `P2.C1` correctness, core, w=1: The answer states that moral relativism does not provide a satisfactory explanation for cross‑cultural moral disagreements.
- `P2.C2` completeness, core, w=1: The answer gives a specific cross‑cultural moral disagreement (e.g., differing views on gender roles between Culture X and Culture Y).
- `P2.C3` reasoning, core, w=1: The answer explains why the example shows that moral relativism is insufficient, citing a need for universal moral principles or moral progress.

**Reference answer** (path P2):

> Moral relativism does not offer a satisfactory explanation for cross‑cultural moral disagreements because it cannot account for the possibility of moral progress or universal standards. A clear example is the contrasting views on gender roles in Sweden, where gender equality is legally mandated and socially expected, versus Saudi Arabia, where strict gender segregation and male guardianship remain entrenched. This disagreement reveals that both societies claim moral authority for their practices, yet the Swedish model demonstrates improvements in human rights that many consider objectively better, suggesting that some moral judgments transcend cultural boundaries. Therefore, the example shows that a purely relativist account fails to explain why certain moral reforms are widely regarded as genuine advances rather than merely cultural preferences.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 14. analytical · economics · `77d217aac87c`

**Q:** In a short paragraph of 3–6 sentences, argue whether a government‑imposed price floor on agricultural products improves farmers' welfare. State a position (for or against) and support it with at least two distinct arguments.

**Path P1:** Argument in favor of the price floor

- `P1.C1` correctness, core, w=1: States a position supporting the price floor
- `P1.C2` completeness, core, w=1: Provides a first argument that the price floor raises farm income
- `P1.C3` reasoning, core, w=1: Provides a second argument that the price floor reduces price volatility for producers

**Path P2:** Argument against the price floor

- `P2.C1` correctness, core, w=1: States a position opposing the price floor
- `P2.C2` completeness, core, w=1: Provides a first argument that the price floor creates a surplus of unsold produce
- `P2.C3` reasoning, core, w=1: Provides a second argument that the price floor raises consumer prices and reduces overall welfare

**Reference answer** (path P2):

> A government‑imposed price floor on agricultural products harms farmers' welfare. First, by setting a minimum price above the market equilibrium, it creates a surplus of unsold produce, forcing farmers to either store costly excess or discard it, which erodes their net earnings. Second, the higher mandated price is passed on to consumers, raising food costs and reducing overall economic welfare, which can lead to lower demand and further depress farmers' revenues.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 15. analytical · health · `2b6545d8938b`

**Q:** In a short paragraph (3–8 sentences), argue whether vaccination mandates or individual choice should be given priority in public‑health policy. Choose one side, present at least two supporting points, and acknowledge a counterargument from the opposite side.

**Path P1:** Prioritize vaccination mandates over individual choice

- `P1.C1` completeness, core, w=1: States the position that vaccination mandates should be given priority in public‑health policy.
- `P1.C2` reasoning, core, w=1: Provides at least two distinct supporting points that link the priority of mandates to improved public‑health outcomes.
- `P1.C3` completeness, non-core, w=0.5: Mentions a counterargument favoring individual choice and offers a response that addresses it.
- `P1.C4` correctness, non-core, w=0.5: All factual claims about public‑health outcomes are accurate.

**Path P2:** Prioritize individual choice over vaccination mandates

- `P2.C1` completeness, core, w=1: States the position that individual choice should be given priority over vaccination mandates in public‑health policy.
- `P2.C2` reasoning, core, w=1: Provides at least two distinct supporting points that link the priority of personal choice to ethical or practical benefits.
- `P2.C3` completeness, non-core, w=0.5: Mentions a counterargument favoring vaccination mandates and offers a response that addresses it.
- `P2.C4` correctness, non-core, w=0.5: All factual claims about ethical or practical considerations are accurate.

**Reference answer** (path P1):

> Vaccination mandates should be given priority in public‑health policy because they protect the community by achieving herd immunity and reducing the burden on healthcare systems. First, compulsory immunization raises overall vaccination rates, which limits the spread of contagious diseases and prevents outbreaks that can overwhelm hospitals. Second, mandates ensure equitable protection for vulnerable populations who cannot be vaccinated themselves, thereby upholding the principle of collective responsibility. Critics argue that mandates infringe on personal liberty and the right to make medical decisions. While respecting autonomy is important, the societal cost of uncontrolled disease transmission outweighs individual preferences, and exemptions can be narrowly tailored to balance freedom with public safety.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 16. analytical · literature · `e41a8cc6154f`

**Q:** In a short paragraph (3–8 sentences), argue whether George Orwell’s *1984* should be understood primarily as a warning about political totalitarianism or as a critique of language manipulation that undermines truth, and support your view with specific textual evidence.

**Path P1:** Argue that *1984* is primarily a warning about political totalitarianism.

- `P1.C1` completeness, core, w=1: States the claim that the novel’s main purpose is to warn about political totalitarianism
- `P1.C2` correctness, core, w=1: Provides a correct textual example of political oppression from the novel (e.g., Big Brother, Thought Police, or the Party’s surveillance)
- `P1.C3` reasoning, core, w=1: Explains how the example demonstrates the novel’s warning about totalitarianism

**Path P2:** Argue that *1984* is primarily a critique of language manipulation that undermines truth.

- `P2.C1` completeness, core, w=1: States the claim that the novel’s main purpose is to critique language manipulation that undermines truth
- `P2.C2` correctness, core, w=1: Provides a correct textual example of language manipulation (e.g., Newspeak, doublethink, or the Party’s rewriting of history)
- `P2.C3` reasoning, core, w=1: Explains how the example shows the novel’s critique of language’s role in eroding truth

**Reference answer** (path P2):

> George Orwell’s *1984* should be understood primarily as a critique of language manipulation that undermines truth. The novel’s most striking illustration of this is Newspeak, the Party’s engineered language that eliminates words like "free" and "thought" to make dissent literally unthinkable. By constantly rewriting history and promoting doublethink—holding two contradictory beliefs at once—the Party shows how control of language can reshape reality itself. These mechanisms reveal Orwell’s warning that when language is stripped of nuance and honesty, truth collapses and totalitarian power becomes unstoppable.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 17. analytical · geography · `c6f36e0e94db`

**Q:** In a short paragraph of 3–8 sentences, argue which factor is the primary driver of the recent rapid retreat of the Greenland Ice Sheet: (1) atmospheric warming or (2) oceanic melting. Choose one factor, state the claim, and provide at least one piece of supporting evidence that links that factor to the ice sheet’s retreat.

**Path P1:** Argument that atmospheric warming is the primary driver

- `P1.C1` completeness, core, w=1: States that atmospheric warming is the primary driver of the Greenland Ice Sheet retreat
- `P1.C2` correctness, core, w=1: Provides at least one accurate piece of evidence linking rising surface air temperatures to increased ice melt
- `P1.C3` reasoning, core, w=1: Explains how the presented evidence supports the claim that atmospheric warming drives the retreat

**Path P2:** Argument that oceanic melting is the primary driver

- `P2.C1` completeness, core, w=1: States that oceanic melting (warmer ocean waters eroding glacier fronts) is the primary driver of the Greenland Ice Sheet retreat
- `P2.C2` correctness, core, w=1: Provides at least one accurate piece of evidence linking warmer ocean temperatures to basal or submarine melting of Greenland’s outlet glaciers
- `P2.C3` reasoning, core, w=1: Explains how the presented evidence supports the claim that oceanic melting drives the retreat

**Reference answer** (path P1):

> The primary driver of the recent rapid retreat of the Greenland Ice Sheet is atmospheric warming. Satellite observations and weather station data show that average summer surface air temperatures over Greenland have risen by about 2 °C since the 1990s, leading to enhanced surface melt rates and the formation of extensive meltwater lakes. Warmer air directly increases the energy balance at the ice surface, causing more snow to melt and accelerating the conversion of ice to runoff. This heightened surface melt not only thins the ice sheet but also lubricates the bed, promoting faster glacier flow toward the ocean. Consequently, the observed temperature rise provides a clear mechanistic link between atmospheric warming and the accelerated retreat of Greenland’s ice.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 18. analytical · everyday life · `e6459e7e28e7`

**Q:** In a short paragraph (3–8 sentences), argue whether commuting by bicycle improves personal health, and support your argument with at least two distinct reasons.

**Path P1:** Argument that commuting by bicycle improves personal health

- `P1.C1` completeness, core, w=1: States the claim that commuting by bicycle improves personal health.
- `P1.C2` reasoning, core, w=1: Provides a reason that regular cycling gives cardiovascular exercise, linking it to better heart health.
- `P1.C3` reasoning, non-core, w=0.5: Provides a second reason that cycling increases daily physical activity, helping weight management.
- `P1.C4` correctness, non-core, w=0.5: All reasons given are factually accurate (e.g., research shows cardio exercise improves heart health).

**Path P2:** Argument that commuting by bicycle does not improve personal health (or may reduce it)

- `P2.C1` completeness, core, w=1: States the claim that commuting by bicycle does not improve personal health or may reduce it.
- `P2.C2` reasoning, core, w=1: Provides a reason that exposure to traffic pollution increases inhaled pollutants, harming respiratory health.
- `P2.C3` reasoning, non-core, w=0.5: Provides a second reason that risk of accidents and injuries can offset health benefits.
- `P2.C4` correctness, non-core, w=0.5: All reasons given are factually accurate (e.g., studies show higher pollutant exposure for cyclists in traffic).

**Reference answer** (path P1):

> Commuting by bicycle significantly improves personal health. First, regular cycling provides sustained cardiovascular exercise, which strengthens the heart, lowers blood pressure, and reduces the risk of heart disease, as numerous studies have shown. Second, cycling adds moderate physical activity to a daily routine, helping to burn calories and maintain a healthy weight, thereby lowering the likelihood of obesity and related metabolic disorders. Together, these benefits make bicycle commuting a powerful, low‑cost strategy for enhancing overall health.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 19. analytical · history · `5f18b45daf59`

**Q:** In a short paragraph (3–8 sentences), argue whether the unification of Germany in 1871 was driven mainly by Otto von Bismarck’s diplomatic realpolitik or by rising nationalist sentiment among the German states, and support your position with specific historical evidence.

**Path P1:** Argument that Bismarck’s diplomatic realpolitik was the primary factor

- `P1.C1` completeness, core, w=1: States that the primary factor behind German unification was Otto von Bismarck’s diplomatic realpolitik.
- `P1.C2` reasoning, core, w=1: Provides at least one specific historical example of Bismarck’s diplomatic action (e.g., the manipulation of the Austro‑Prussian War, the Ems Dispatch, or the alliance with Italy) and explains how it advanced unification.
- `P1.C3` correctness, non-core, w=0.5: Accurately describes the impact of that diplomatic action on a concrete outcome (e.g., the creation of the North German Confederation after 1866) showing cause‑effect.

**Path P2:** Argument that rising nationalist sentiment was the primary factor

- `P2.C1` completeness, core, w=1: States that the primary factor behind German unification was rising nationalist sentiment among the German states.
- `P2.C2` reasoning, core, w=1: Provides at least one specific historical example of nationalist sentiment (e.g., the 1848 Frankfurt Parliament, popular support for a German nation, cultural movements like the Brothers Grimm) and explains how it contributed to unification.
- `P2.C3` correctness, non-core, w=0.5: Accurately describes the impact of that nationalist sentiment on a concrete event (e.g., mass support for Bismarck’s wars or the formation of the North German Confederation) showing cause‑effect.

**Reference answer** (path P1):

> The unification of Germany in 1871 was driven primarily by Otto von Bismarck’s diplomatic realpolitik. By engineering the Austro‑Prussian War of 1866, Bismarck isolated Austria and secured Prussian dominance over the northern German states, leading directly to the creation of the North German Confederation. He then skillfully manipulated the Ems Dispatch in 1870, provoking French outrage and precipitating the Franco‑Prussian War, which rallied the southern German kingdoms to the Prussian cause. The decisive Prussian victory and the subsequent proclamation of the German Empire in the Hall of Mirrors demonstrated how Bismarck’s calculated diplomatic maneuvers, rather than popular nationalist fervor, produced the political structures necessary for unification.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 20. explanatory · technology · `ce296f896745`

**Q:** Explain how blockchain technology ensures the integrity of its stored data. In a short paragraph (3‑8 sentences), provide one explanation.

**Path P1:** Explanation based on cryptographic hash chaining of blocks

- `P1.C1` correctness, core, w=1: States that each block includes a cryptographic hash of the previous block
- `P1.C2` reasoning, non-core, w=0.5: Explains that changing any transaction alters its hash, which breaks the chain
- `P1.C3` completeness, non-core, w=0.5: Notes that this chaining makes tampering detectable without a central authority

**Path P2:** Explanation based on decentralized consensus among network nodes

- `P2.C1` correctness, core, w=1: States that the network reaches agreement through a consensus mechanism (e.g., proof‑of‑work or proof‑of‑stake)
- `P2.C2` reasoning, non-core, w=0.5: Explains that consensus requires a majority of nodes to validate a new block, preventing a single malicious actor from altering data
- `P2.C3` completeness, non-core, w=0.5: Mentions that this distributed validation ensures data integrity even if some nodes are compromised

**Reference answer** (path P1):

> Each block in a blockchain contains a cryptographic hash of the previous block, linking them together in a chain. If any transaction within a block is altered, its hash changes, which in turn changes the hash stored in the next block, breaking the chain’s continuity. Because every subsequent block depends on the hash of its predecessor, tampering with any part of the ledger instantly becomes evident. This hash‑chaining mechanism allows anyone to verify the integrity of the data without needing a central authority, as any discrepancy signals that the data has been compromised.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 21. explanatory · ethics · `35283af8f248`

**Q:** In a short paragraph (3‑8 sentences), explain why individuals often obey moral rules even when breaking them would bring personal advantage.

**Path P1:** Explanation that internalized moral norms cause compliance

- `P1.C1` completeness, core, w=1: Identifies internalized moral norms as the primary reason for obeying the rule
- `P1.C2` reasoning, core, w=1: Explains how internalization leads to compliance (e.g., desire to act consistently with self‑concept or avoid guilt)
- `P1.C3` correctness, non-core, w=0.5: References a recognized psychological theory or researcher that links internalization to moral behavior (e.g., Kohlberg, Haidt)

**Path P2:** Explanation that fear of social sanctions or reputation concerns cause compliance

- `P2.C1` completeness, core, w=1: Identifies fear of social sanctions or reputation concerns as the primary reason for obeying the rule
- `P2.C2` reasoning, core, w=1: Explains how anticipated punishment or loss of reputation motivates compliance (e.g., avoidance of disapproval, desire for social approval)
- `P2.C3` correctness, non-core, w=0.5: Mentions a sociological or evolutionary concept that supports the sanction explanation (e.g., social contract, reciprocal altruism)

**Reference answer** (path P1):

> People often follow moral rules because those rules have become part of their internalized value system. When a norm is internalized, individuals see acting in accordance with it as consistent with their self‑concept and fear the guilt that would follow a violation. This internal motivation drives compliance even when personal gain is at stake. Lawrence Kohlberg’s stage theory of moral development highlights that higher stages involve adherence to principles that are adopted voluntarily, not merely to avoid external punishment. Thus, the desire to stay true to one’s own moral standards explains why many people obey rules despite tempting alternatives.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 22. explanatory · economics · `35a750dadfc7`

**Q:** Explain why inflation can erode the real value of savings. In a short paragraph of 3–6 sentences, describe one mechanism by which inflation reduces the purchasing power of saved money.

**Path P1:** Explanation that focuses on the impact of inflation on real interest rates (negative real return).

- `P1.C1` completeness, core, w=1: Identifies exactly one mechanism by which inflation erodes the real value of savings.
- `P1.C2` correctness, core, w=1: Accurately describes how a nominal interest rate lower than the inflation rate yields a negative real interest rate, reducing the real value of savings.
- `P1.C3` reasoning, core, w=1: Provides reasoning that links the negative real interest rate to a loss of purchasing power for saved money.
- `P1.C4` completeness, non-core, w=0.5: Gives a concrete numeric example illustrating the mechanism.

**Path P2:** Explanation that focuses on the direct effect of rising price levels on the purchasing power of a fixed nominal amount.

- `P2.C1` completeness, core, w=1: Identifies exactly one mechanism by which inflation erodes the real value of savings.
- `P2.C2` correctness, core, w=1: Accurately describes how a general increase in the price level means each dollar saved buys fewer goods over time.
- `P2.C3` reasoning, core, w=1: Provides reasoning that links the higher price level to a reduction in the real value of savings.
- `P2.C4` completeness, non-core, w=0.5: Gives a concrete numeric example illustrating the mechanism.

**Reference answer** (path P2):

> One way inflation erodes savings is by raising the overall price level so that a fixed amount of money buys fewer goods over time. As prices rise, the purchasing power of each dollar saved declines, meaning the same nominal balance can purchase less than it could before. For example, if you saved $1,000 and the inflation rate is 5% per year, the basket of goods that cost $1,000 today would cost $1,050 a year later, so your savings would be short by $50 in real terms. This loss of purchasing power directly reduces the real value of the saved money.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 23. explanatory · environment · `a14f56512e37`

**Q:** In a short paragraph (3 to 8 sentences), explain one way that green roofs mitigate the urban heat island effect, and illustrate the mechanism with a specific example of a city that has implemented this approach.

**Path P1:** Explanation based on evapotranspiration cooling

- `P1.C1` correctness, core, w=1: Identifies evapotranspiration from vegetation on green roofs as the primary mechanism reducing ambient air temperature.
- `P1.C2` completeness, non-core, w=0.5: Provides a specific city example where widespread green‑roof installation led to measurable temperature reductions.
- `P1.C3` reasoning, non-core, w=0.5: Explains how evapotranspiration translates into lower surface and air temperatures.

**Path P2:** Explanation based on increased albedo and insulation

- `P2.C1` correctness, core, w=1: Identifies increased surface albedo and building insulation from green roofs as the primary mechanism lowering urban temperatures.
- `P2.C2` completeness, non-core, w=0.5: Provides a specific city example where green roofs with high‑albedo vegetation reduced heat‑island intensity.
- `P2.C3` reasoning, non-core, w=0.5: Explains how higher albedo and insulation reduce heat flux into buildings and surrounding air.

**Reference answer** (path P1):

> Green roofs cool cities primarily through evapotranspiration, where water absorbed by the planted vegetation is released as water vapor, carrying away latent heat and lowering the surrounding air temperature. In Chicago, the city’s “Green Roofs for Healthy Cities” program has installed thousands of vegetated roofs that collectively reduce summer ambient temperatures by up to 2 °C in nearby neighborhoods, as measured by the Chicago Climate Center. The process works because the evaporating water absorbs heat from the roof surface, decreasing surface temperature, and the resulting moist air mixes with the urban atmosphere, further reducing the overall heat island intensity.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 24. explanatory · health · `e19a2d15a2c7`

**Q:** In a short paragraph (3–8 sentences), explain how the body regulates blood glucose levels after eating.

**Path P1:** Explanation that emphasizes insulin secretion and its direct actions on peripheral tissues and the liver.

- `P1.C1` correctness, core, w=1: States that the rise in blood glucose after a meal triggers pancreatic β‑cells to release insulin.
- `P1.C2` reasoning, core, w=1: Explains that insulin promotes glucose uptake in muscle and adipose tissue by causing GLUT4 transporters to move to the cell surface.
- `P1.C3` completeness, non-core, w=0.5: Notes that insulin suppresses hepatic glucose production, helping lower blood glucose.

**Path P2:** Explanation that emphasizes incretin hormones and the suppression of glucagon alongside direct hepatic uptake.

- `P2.C1` correctness, core, w=1: States that intestinal L‑cells release GLP‑1 and GIP in response to nutrients, and these incretins enhance insulin secretion.
- `P2.C2` reasoning, core, w=1: Explains that elevated glucose and incretins suppress glucagon secretion from α‑cells, reducing hepatic glucose output.
- `P2.C3` completeness, non-core, w=0.5: Mentions that the liver takes up glucose directly via GLUT2 transporters, contributing to post‑meal glucose clearance.

**Reference answer** (path P1):

> After a meal, the increase in blood glucose stimulates the pancreatic β‑cells to secrete insulin. Insulin then acts on muscle and adipose tissue, causing GLUT4 transporters to translocate to the cell membrane and rapidly take up glucose from the bloodstream. At the same time, insulin signals the liver to suppress its own glucose production by inhibiting glycogenolysis and gluconeogenesis. These combined actions lower circulating glucose levels and help restore normal homeostasis.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 25. explanatory · literature · `262d87e0feea`

**Q:** In a short paragraph (3–8 sentences), explain how the non‑linear narrative structure in Toni Morrison’s *Beloved* contributes to the novel’s exploration of memory and trauma.

**Path P1:** Explanation emphasizing the psychological impact of fragmented chronology on readers' understanding of trauma.

- `P1.C1` completeness, core, w=1: Identifies the non‑linear narrative structure (e.g., flashbacks, time jumps) used in *Beloved*.
- `P1.C2` reasoning, core, w=1: Explains how this fragmented structure mirrors the characters’ fragmented memories of trauma.
- `P1.C3` correctness, non-core, w=0.5: Provides at least one specific example from the novel that illustrates the non‑linear technique.

**Path P2:** Explanation emphasizing the thematic function of the non‑linear structure to connect past and present, showing the lingering impact of slavery.

- `P2.C1` completeness, core, w=1: Identifies the non‑linear narrative structure used in *Beloved*.
- `P2.C2` reasoning, core, w=1: Explains how the structure links past events of slavery to present experiences of the characters.
- `P2.C3` correctness, non-core, w=0.5: Cites a specific passage where a past event is juxtaposed with a present moment to illustrate this link.

**Reference answer** (path P1):

> Morrison structures *Beloved* with frequent flashbacks and abrupt time jumps, creating a non‑linear narrative that never settles into a single chronological order. This fragmented chronology mirrors the way the characters experience memory after trauma, as their recollections surface in disjointed, often involuntary bursts rather than a smooth, linear story. For instance, the novel repeatedly intercuts Sethe’s present life at 124 with vivid, sudden returns to her time at Sweet Home and the night she killed her baby, forcing readers to piece together the trauma as Sethe herself does. The effect is that the reader, like the characters, must navigate a shattered timeline, feeling the lingering pain and confusion that trauma leaves behind.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 26. explanatory · geography · `99dceeec35ba`

**Q:** In a short paragraph of 3–8 sentences, explain why the equatorial region receives more solar energy per unit surface area than regions at higher latitudes. Provide one primary reason and support it with a relevant fact or example.

**Path P1:** Explanation based on the geometry of solar incidence (near‑vertical angle at the equator).

- `P1.C1` completeness, core, w=1: States that the equator receives more solar energy because the Sun's rays strike the surface at a near‑vertical angle year‑round.
- `P1.C2` correctness, core, w=1: Accurately describes that a near‑vertical angle reduces the spreading of solar energy per unit area, increasing intensity.
- `P1.C3` reasoning, non-core, w=0.5: Provides a supporting fact, such as typical solar irradiance at the equator (~1,000 W/m²) being higher than at mid‑latitudes.

**Path P2:** Explanation based on total daylight duration (longer day length at the equator).

- `P2.C1` completeness, core, w=1: States that the equator receives more solar energy because it experiences roughly equal day and night lengths year‑round, giving more total daylight hours than higher latitudes in winter.
- `P2.C2` correctness, core, w=1: Accurately notes that higher latitudes have shorter daylight periods in winter, reducing the total solar input they receive.
- `P2.C3` reasoning, non-core, w=0.5: Provides an example, such as 60° latitude receiving only about 4 hours of daylight in winter compared with ~12 hours at the equator.

**Reference answer** (path P1):

> The equatorial region receives more solar energy per unit surface area because the Sun’s rays strike the surface at a near‑vertical angle throughout the year. When sunlight arrives almost straight down, the energy is concentrated over a smaller area, whereas at higher latitudes the same amount of energy is spread over a larger slanted surface, reducing the intensity. This geometric effect means that the solar irradiance at the equator is typically around 1,000 W/m², noticeably higher than the roughly 800 W/m² measured at mid‑latitudes.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 27. explanatory · everyday life · `9bd22f1114b3`

**Q:** In a short paragraph (3–8 sentences), explain why people often forget where they parked their car in a large shopping‑mall parking garage.

**Path P1:** Explanation based on cognitive overload and memory interference.

- `P1.C1` completeness, core, w=1: Identifies the explanation as memory interference caused by high cognitive load and many similar parking spots.
- `P1.C2` correctness, core, w=1: Provides at least one specific factor that creates cognitive load (e.g., distractions while shopping, a large number of similar spots).
- `P1.C3` reasoning, core, w=1: Links the factor to the memory‑interference explanation (shows how the factor leads to forgetting).
- `P1.C4` completeness, non-core, w=0.5: Mentions at least one possible way people try to mitigate the problem (optional).

**Path P2:** Explanation based on lack of distinctive environmental cues.

- `P2.C1` completeness, core, w=1: Identifies the explanation as forgetting due to insufficient distinctive landmarks or cues in the garage.
- `P2.C2` correctness, core, w=1: Provides at least one specific cue that is missing or uniform (e.g., identical lighting, repetitive column design).
- `P2.C3` reasoning, core, w=1: Explains how the lack of cues leads to difficulty recalling the parking spot.
- `P2.C4` completeness, non-core, w=0.5: Notes a possible additional factor that could also contribute (optional).

**Reference answer** (path P1):

> People often forget where they parked in a large mall garage because the situation creates high cognitive load and memory interference. While shopping they are distracted by sales, crowds, and the need to carry bags, which taxes their attention and reduces the resources available for encoding the parking location. The garage itself contains dozens of nearly identical rows and spots, so the weak, overloaded memory trace is easily confused with other similar spots, leading to interference and forgetting. To combat this, many drivers try to use a distinctive cue—such as noting the nearest column number or taking a photo of the surrounding signage—so they have an external reminder that can anchor the memory later.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 28. explanatory · history · `c4d9f13d146f`

**Q:** In a short paragraph (3–8 sentences), explain why the Black Death spread rapidly across Europe in the 14th century. Provide one plausible mechanism that accounts for its swift transmission.

**Path P1:** Explanation that attributes the rapid spread to trade routes and human movement

- `P1.C1` completeness, core, w=1: Identifies trade routes (e.g., Silk Road, Mediterranean ports) as the primary mechanism for the spread
- `P1.C2` correctness, non-core, w=0.5: Provides at least one specific historical fact linking trade movement to disease transmission (e.g., ships from the Black Sea arriving in Italian ports in 1347)
- `P1.C3` reasoning, core, w=1: Explains how the identified trade mechanism facilitated rapid transmission across Europe (e.g., movement of infected rats and fleas on merchant ships)

**Path P2:** Explanation that attributes the rapid spread to ecological changes and flea vectors

- `P2.C1` completeness, core, w=1: Identifies ecological changes (e.g., climate warming leading to a rodent population boom) as the primary mechanism for the spread
- `P2.C2` correctness, non-core, w=0.5: Provides at least one specific historical or scientific fact supporting the ecological mechanism (e.g., increase in rat populations in 14th‑century Europe)
- `P2.C3` reasoning, core, w=1: Explains how the ecological mechanism led to rapid transmission (e.g., fleas moving from rats to humans across settlements)

**Reference answer** (path P1):

> The Black Death spread swiftly across Europe because it rode the continent's extensive trade networks. In 1347, fleets of Genoese ships arrived in the Italian port of Messina carrying grain and, unknowingly, plague‑infected rats and their fleas from the Black Sea region. These merchant vessels continued to dock at major Mediterranean hubs such as Venice, Marseille, and Barcelona, where the rodents disembarked and mingled with local rodent populations. As traders, soldiers, and pilgrims moved inland along established overland routes, they carried the disease further into the interior. The constant flow of people and goods along these trade arteries allowed the pathogen to jump quickly from one densely populated city to the next, producing the rapid, continent‑wide pandemic.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 29. explanatory · science · `4f27da923721`

**Q:** Explain why a candle flame appears yellow when it burns. Answer in a short paragraph (3‑8 sentences).

**Path P1:** Explanation that the yellow color is due to soot particles produced by incomplete combustion, which incandesce.

- `P1.C1` correctness, core, w=1: Identifies incomplete combustion producing soot particles as the cause of the flame's yellow color
- `P1.C2` reasoning, core, w=1: Explains that heated soot particles emit light primarily in the yellow part of the spectrum
- `P1.C3` completeness, non-core, w=0.5: Provides at least one supporting detail about flame color indicating combustion completeness

**Path P2:** Explanation that the yellow color results from blackbody radiation of hot gases at a temperature that peaks in the yellow wavelength range.

- `P2.C1` correctness, core, w=1: Identifies blackbody radiation of hot gases as the cause of the flame's yellow color
- `P2.C2` reasoning, core, w=1: Explains that the flame temperature corresponds to an emission peak in the yellow region of the spectrum (e.g., using Wien's law)
- `P2.C3` completeness, non-core, w=0.5: Provides at least one supporting detail about how the flame’s temperature compares to that of a hotter (white) flame

**Reference answer** (path P1):

> A candle flame looks yellow because the wax does not burn completely, producing tiny soot particles in the flame. These soot particles are heated to high temperatures and begin to incandesce, emitting light that is strongest in the yellow part of the visible spectrum. The presence of this glowing soot indicates incomplete combustion, whereas a blue or nearly invisible flame would suggest a more complete, hotter burn. Thus the yellow hue is essentially the glow of hot carbon particles suspended in the flame.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 30. creative · ethics · `a96665be80bf`

**Q:** In a brief scene of 3‑8 sentences, dramatize an ethical dilemma where a character must choose between telling a harmful truth or lying to protect someone they care about. The scene should reveal the conflict through dialogue or action, include a turning point, and avoid using the phrase “moral dilemma”.

**Path P1:** Write a short scene that meets the brief's constraints and demonstrates craft.

- `P1.C1` correctness, core, w=1: Contains exactly 3 to 8 sentences.
- `P1.C2` correctness, core, w=1: Presents a recognizable ethical conflict between two moral principles (e.g., truth‑telling vs protecting a loved one).
- `P1.C3` expression, non-core, w=0.5: Shows characters' emotions or stakes through actions or dialogue rather than stating them directly.
- `P1.C4` expression, non-core, w=0.5: Includes a narrative turn or development (e.g., a decision made, a revelation, or a change in the situation).
- `P1.C5` expression, non-core, w=0.5: Avoids common cliché phrasing such as “moral dilemma”, “torn between”, or “right vs wrong”.

**Obvious answers (originality check):**

- A doctor deciding whether to reveal a terminal diagnosis to a patient.
- A whistleblower choosing to expose corporate wrongdoing or stay silent.
- A friend debating whether to tell a secret that could hurt another friend.
- A soldier weighing obedience to orders against personal conscience.
- A journalist deciding whether to publish a story that could endanger lives.

**Reference answer** (path P1):

> Mara stared at the trembling boy, his eyes fixed on the sealed envelope that held the doctor's grim prognosis. "If you tell his mother the truth, she'll lose the will to fight," she whispered, hand hovering over the paper. "But if we hide it, she'll never know how much time he has left." She slipped the letter into her coat, feeling the weight of the secret settle like a stone. At that moment, the boy's mother entered, humming a lullaby, oblivious to the storm brewing behind Mara's smile. "I think it's best we keep this to ourselves for now," Mara said, her voice steady, sealing the choice with a gentle nod.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 31. creative · economics · `8480128da972`

**Q:** Write a short pitch (3–5 sentences) for a new digital currency aimed at college students. The pitch must name one unique feature of the currency, describe one specific benefit for students, and point out one plausible risk or downside.

**Path P1:** Pitch for a student‑focused digital currency

- `P1.C1` correctness, core, w=1: The answer contains exactly three to five sentences.
- `P1.C2` correctness, core, w=1: The answer mentions a unique feature of the currency (e.g., instant peer‑to‑peer transfers, no fees, campus‑ID integration).
- `P1.C3` correctness, core, w=1: The answer states a concrete benefit for college students (e.g., helps budgeting, earns rewards, simplifies campus purchases).
- `P1.C4` correctness, core, w=1: The answer identifies one plausible risk or downside (e.g., security vulnerability, volatility, regulatory uncertainty).
- `P1.C5` expression, non-core, w=0.5: The answer includes a turn or development, moving from description of the feature to either the benefit or the risk.
- `P1.C6` expression, non-core, w=0.5: The answer shows rather than tells by using a concrete example or vivid language (e.g., "students can split a pizza bill in seconds").
- `P1.C7` expression, non-core, w=0.5: The answer avoids cliché phrasing such as "revolutionary" or "game‑changing."

**Obvious answers (originality check):**

- Feature: zero transaction fees; Benefit: saves money on purchases; Risk: security hacks could steal funds.
- Feature: instant peer‑to‑peer transfers via phone; Benefit: makes splitting bills with roommates effortless; Risk: privacy concerns over transaction data.
- Feature: integration with campus ID cards; Benefit: simplifies buying meals and books on campus; Risk: limited acceptance outside the university.
- Feature: rewards for academic achievements; Benefit: earns points redeemable for discounts; Risk: creates inequality between high‑ and low‑performing students.
- Feature: stablecoin pegged to the US dollar; Benefit: protects savings from inflation; Risk: regulatory uncertainty could limit usage.

**Reference answer** (path P1):

> CampusCoin links directly to a student’s university ID, letting them send instant, fee‑free transfers with a single tap. Because the app syncs with class schedules, a sophomore can instantly split a late‑night pizza bill with three roommates after the last lecture, keeping everyone on budget without juggling cash. The same integration also earns points toward campus dining credits, turning everyday purchases into savings. However, tying financial activity to a university account means a data breach could expose both personal and academic information, so users must stay vigilant about security.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 32. creative · environment · `c063fe7120b3`

**Q:** Write a short scene (3 to 8 sentences) that portrays a city park just after a heavy rainstorm, focusing on how the environment begins to recover. Use vivid sensory details and include a clear development from the immediate aftermath toward a sign of renewal.

**Path P1:** Evaluates whether the scene meets the brief’s constraints and demonstrates effective creative craft.

- `P1.C1` correctness, core, w=1: Mentions a city park that has just experienced a heavy rainstorm.
- `P1.C2` correctness, core, w=1: Describes at least two sensory details related to the environment’s recovery (e.g., sound, smell, sight, touch).
- `P1.C3` expression, non-core, w=0.5: Includes a turn or development that moves the scene from immediate aftermath toward a sign of renewal or hope.
- `P1.C4` expression, non-core, w=0.5: Shows rather than tells at least one element (uses vivid description instead of stating the park is recovering).
- `P1.C5` expression, non-core, w=0.5: Avoids common clichés such as "the rain washed away all sins," "the park sprang back to life," or "the sun broke through the clouds."

**Obvious answers (originality check):**

- Describe puddles reflecting streetlights or neon signs
- Mention the earthy smell of wet soil and fresh leaves
- Show children or dogs splashing in the rain‑filled park
- Describe birds or insects returning as the water recedes
- Focus on the sound of dripping leaves and distant thunder fading

**Reference answer** (path P1):

> The city park glistens under the lingering drizzle, puddles reflecting the dim streetlights like scattered mirrors. The air is thick with the fresh, loamy scent of wet soil and the faint perfume of crushed lilacs, while a distant rustle announces the tentative return of sparrows to the sodden benches. Droplets bead on the newly sprouted grass, trembling as a gentle wind nudges them into a rhythmic patter that sounds like soft applause. A lone jogger's shoes splash through the shallow water, sending ripples that catch the first shy shafts of amber light slipping through the thinning clouds. As the sky clears, a tiny green shoot pushes through a puddle, its bright tip a quiet promise that the park is already beginning to heal.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 33. creative · health · `ad7accec3945`

**Q:** Write a short pitch (3–8 sentences) for a new public‑health campaign that encourages regular physical activity, aimed at adults aged 30‑45. Your pitch must include a hook that grabs attention, mention at least one specific health benefit, and finish with a clear call to action.

**Path P1:** Standard pitch meeting constraints and craft expectations

- `P1.C1` correctness, core, w=1: Mentions the target audience of adults aged 30‑45
- `P1.C2` correctness, core, w=1: Contains a hook that aims to grab attention (e.g., startling fact, rhetorical question, vivid image)
- `P1.C3` correctness, core, w=1: States at least one specific health benefit of regular physical activity
- `P1.C4` correctness, core, w=1: Ends with a call to action urging the reader to act (e.g., "Sign up now", "Visit our website", "Join the movement")
- `P1.C5` expression, non-core, w=0.5: Uses vivid, sensory language that shows rather than tells
- `P1.C6` expression, non-core, w=0.5: Includes a turn or development, moving from a problem description to a solution proposal
- `P1.C7` expression, non-core, w=0.5: Avoids overused cliché phrases such as "stay fit" or "healthy lifestyle"

**Obvious answers (originality check):**

- Start with a startling statistic about inactivity, list a benefit like lower heart‑risk, end with "Visit our website to join today!"
- Open with a rhetorical question about energy levels, mention weight‑control benefit, finish with "Sign up now!"
- Begin with a vivid image of a busy office, propose a walking‑break program, close with "Take the first step today!"
- Use a short anecdote of someone feeling sluggish, highlight mood‑boosting benefit, end with "Join the movement!"
- State a problem of sedentary work, offer a 10‑minute‑daily routine, conclude with "Register at our site!"

**Reference answer** (path P1):

> Did you know that a 20‑minute brisk walk can melt away the stress that builds up after a long workday? For adults aged 30‑45, whose bodies are quietly trading muscle for fatigue, moving daily boosts heart health and sharpens mental clarity, leaving you feeling energized and focused. Imagine swapping the hum of traffic for the rhythmic thump of your own heartbeat as you stride through a sun‑lit park. This campaign turns that vision into reality by offering free, neighborhood‑based workout challenges that fit into even the busiest schedules. Join the momentum today—sign up at MoveForward.org and claim your first week of guided sessions for free.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 34. creative · literature · `1680e241cc2e`

**Q:** In a short scene of three to eight sentences, write a brief narrative where a character discovers a hidden library in a modern city. The scene must include vivid sensory description, a clear twist at the end, and should show rather than tell while avoiding common clichés about secret libraries.

**Path P1:** Meets brief constraints and demonstrates craft in the creative scene

- `P1.C1` correctness, core, w=1: Contains exactly three to eight sentences
- `P1.C2` correctness, core, w=1: Includes vivid sensory description of the hidden library (e.g., mentions sights, sounds, textures, smells)
- `P1.C3` correctness, core, w=1: Introduces a twist at the end of the scene (e.g., an unexpected revelation about the library or the character)
- `P1.C4` expression, non-core, w=0.5: Shows rather than tells (uses concrete actions, dialogue, or sensory details instead of abstract statements)
- `P1.C5` expression, non-core, w=0.5: Does not use any of the listed common clichés (e.g., "dusty old books", "secret door", "mysterious librarian")

**Obvious answers (originality check):**

- A character pulls a hidden bookshelf aside and finds a dusty old library filled with ancient tomes, then learns the books write themselves.
- A protagonist discovers a secret underground library behind a graffiti wall, only to realize the library is a virtual reality simulation.
- The narrator finds a concealed library in a subway station, and the twist reveals the library is actually a mind‑reading device.
- A city dweller uncovers a hidden library in an abandoned warehouse, and the twist shows the librarian is a sentient AI.
- A student stumbles upon a secret library in a rooftop garden, and the ending reveals the books contain predictions of the future.

**Reference answer** (path P1):

> Mara slipped through the cracked brick of an abandoned subway tunnel, the air tasting of rust and wet concrete, when a faint hum of turning pages brushed against the echo of distant traffic. The wall ahead pulsed with a soft amber glow, and as she brushed aside a graffiti‑splattered panel, the scent of fresh ink and citrus oil flooded her nostrils, mingling with the metallic tang of the city outside. Inside, rows of sleek, glass‑bound volumes floated inches above polished steel shelves, their spines humming with a low, rhythmic vibration that made the floor thrum beneath her feet. She reached for a hovering tome, its cover warm like sun‑warmed stone, and the moment her fingers made contact, the whole chamber flickered, projecting a holographic map of the entire metropolis onto the ceiling. The map resolved into a single blinking point—her own apartment, indicating that the library had been cataloguing her life as its most prized, unread story.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 35. creative · geography · `f96f805a4666`

**Q:** Write a short travel‑brochure paragraph (3–8 sentences) that introduces a fictional city situated at the edge of the Amazon rainforest. In your paragraph, describe the city’s geographic setting, its local climate, and one unique natural feature that distinguishes it. Aim for vivid description and avoid common clichés.

**Path P1:** Answer meets brief constraints and demonstrates creative craft

- `P1.C1` correctness, core, w=1: The answer contains between 3 and 8 sentences.
- `P1.C2` correctness, core, w=1: The answer states that the city is located at the edge of the Amazon rainforest.
- `P1.C3` correctness, core, w=1: The answer describes at least one geographic characteristic of the surrounding area (e.g., nearby river, forest type, terrain).
- `P1.C4` correctness, core, w=1: The answer mentions a climate characteristic of the location (e.g., high humidity, tropical temperature range, seasonal rainfall).
- `P1.C5` correctness, core, w=1: The answer includes a unique natural feature of the city (e.g., a waterfall, bioluminescent bay, rare orchid grove).
- `P1.C6` expression, non-core, w=0.5: The answer contains a narrative turn or development that introduces a new element or changes focus.
- `P1.C7` expression, non-core, w=0.5: The answer uses descriptive language that shows the setting rather than merely stating facts.
- `P1.C8` expression, non-core, w=0.5: The answer avoids common travel‑brochure clichés such as "hidden gem", "off the beaten path", or "paradise".

**Obvious answers (originality check):**

- A straightforward factual paragraph that lists location, climate, and a natural feature without any narrative turn.
- A promotional‑style paragraph filled with clichés like "hidden gem" or "off the beaten path."
- A paragraph that mentions the Amazon edge and climate but omits any unique natural feature.
- A paragraph that meets the sentence count but relies on generic adjectives such as "beautiful" and "exotic" without vivid description.
- A paragraph that focuses only on tourism amenities (hotels, tours) and ignores geography, climate, or natural feature.

**Reference answer** (path P1):

> Perched where the emerald canopy of the Amazon thins into a winding tributary of the Rio Negro, the city of Luminara greets visitors with the scent of damp earth and distant thunder. Towering basalt cliffs rise on its western fringe, their faces etched with ancient river scars that channel mist into the streets below. The climate clings to a perpetual humidity, with warm, amber‑colored mornings that give way to sudden, torrential rain showers that cleanse the air. What truly sets Luminara apart is the luminous orchid grove that blooms only at dusk, its petals glowing faintly blue as fireflies weave through the foliage. As the sun dips, the city’s market transforms, swapping daytime chatter for the soft hum of nocturnal insects and the glow of lanterns reflecting off the river’s black mirror.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 36. creative · everyday life · `9260f788d0be`

**Q:** Write a brief (3–6 sentences) scene describing a person’s first day at a new job, focusing on the protagonist’s internal thoughts and the atmosphere of the office. Include at least one sensory detail (sight, sound, or smell) and end with a subtle hint of future conflict.

**Path P1:** The answer meets the brief’s constraints and demonstrates effective creative writing.

- `P1.C1` correctness, core, w=1: Contains exactly 3 to 6 sentences.
- `P1.C2` completeness, core, w=1: Includes at least one internal thought of the protagonist.
- `P1.C3` correctness, core, w=1: Provides a sensory detail (sight, sound, or smell) describing the office.
- `P1.C4` reasoning, core, w=1: Ends with a subtle hint of future conflict.
- `P1.C5` expression, non-core, w=0.5: Shows the protagonist’s feelings through description, metaphor, or action rather than stating them directly.
- `P1.C6` expression, non-core, w=0.5: Avoids common clichés such as "first day jitters" or "the office was a maze".

**Obvious answers (originality check):**

- The protagonist sits at a desk, feels nervous, hears the hum of computers, thinks about making a good impression, and ends with a vague feeling that something will go wrong.
- A description of the office’s bright lighting, the protagonist’s racing thoughts, a coffee smell, and a hint that a demanding boss will appear later.
- Narration of the protagonist’s internal monologue about fitting in, the sound of keyboards, and a closing line about an upcoming meeting that seems ominous.
- Scene where the protagonist observes the open‑plan office, feels anxious, smells fresh paint, and ends with a subtle mention of a missing file that could cause trouble.
- A brief where the protagonist thinks about the commute, hears distant chatter, notes the scent of coffee, and ends with a hint that a coworker will challenge them.

**Reference answer** (path P1):

> She steps into the open-plan floor, the hum of the copier a low tide that pulls at the edges of her concentration. A quick glance at the glass-walled conference room reveals a sunrise reflected in the polished surface, and she thinks, *If I can keep up with their pace, maybe I’ll belong here.* The scent of fresh coffee drifts from the break area, mingling with the faint ozone of the air conditioner, grounding her nervous energy. She watches a colleague glance at her screen, then back to his own, and feels a quiet ripple of competition building beneath the polite smiles. As the clock ticks toward lunch, she catches the manager’s sharp intake of breath when she mentions a new client idea, a subtle warning that the day’s optimism may soon be tested.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 37. creative · history · `744452debae8`

**Q:** In a short paragraph (3–8 sentences), write a diary entry from the perspective of a soldier who fought in the Battle of Gettysburg. The entry should convey personal observations and reflect on how the battle has affected you or the war effort.

**Path P1:** Diary entry perspective

- `P1.C1` correctness, core, w=1: Contains between 3 and 8 sentences.
- `P1.C2` correctness, core, w=1: Written in first‑person voice from the perspective of a soldier who fought at Gettysburg.
- `P1.C3` correctness, core, w=1: Mentions the Battle of Gettysburg by name.
- `P1.C4` completeness, core, w=1: Includes a reflection on the battle's impact, either personal or broader.
- `P1.C5` expression, non-core, w=0.5: Uses sensory or emotional details that show rather than tell the experience.
- `P1.C6` expression, non-core, w=0.5: Avoids overused clichés such as "the turning point of the war" without nuance.

**Obvious answers (originality check):**

- A soldier describing the roar of cannon fire and the smell of smoke
- A soldier lamenting the loss of comrades and the wounds he sees around him
- A soldier noting the strategic importance of Little Round Top or Cemetery Ridge
- A soldier expressing fear during the charge and hope for victory afterwards
- A soldier writing about the aftermath, the wounded, and the impact on morale

**Reference answer** (path P1):

> July 3, 1863 – The smoke over Cemetery Ridge still clings to my throat as I write by the flickering lantern in the camp. The roar of artillery and the scream of wounded men are etched into my memory, and the iron taste of blood lingers on my tongue. I watched the Union line hold as Confederate colors fell, and the thunder of the 3rd Minnesota's charge still rattles in my bones. Tonight, the quiet is broken only by distant sobs, and I feel a hollow pride that our stand may have saved countless towns from burning.


Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 38. creative · science · `9894231ecaff`

**Q:** Write a short sci‑fi scene (3‑8 sentences) in which a scientist on an alien planet discovers a new element. The scene should introduce the setting, describe the discovery, and include a development that changes the situation after the discovery.

**Path P1:** Sci‑fi discovery scene

- `P1.C1` correctness, core, w=1: Contains between three and eight sentences.
- `P1.C2` completeness, core, w=1: Introduces a scientist character who discovers a new element on an alien planet.
- `P1.C3` expression, non-core, w=0.5: Uses sensory or concrete details to depict the discovery rather than abstract statements.
- `P1.C4` expression, core, w=1: Includes a narrative turn or development that changes the situation after the discovery.
- `P1.C5` correctness, non-core, w=0.5: Does not contain the phrases "mad scientist", "evil corporation", or "chosen one".
- `P1.C6` expression, non-core, w=0.5: Shows the scientist’s reaction through action or dialogue rather than stating the scientist felt a specific emotion.

**Obvious answers (originality check):**

- A straightforward description of the scientist holding up a glowing rock and announcing the discovery to a crew.
- A dialogue‑heavy scene where the scientist explains the element to a skeptical colleague.
- A comedic scene where the scientist clumsily drops the sample and it creates a harmless spark.
- A dramatic monologue where the scientist narrates the element’s properties while standing alone on the alien landscape.
- A minimalistic scene that only describes the alien environment and mentions the element without any character interaction.

**Reference answer** (path P1):

> Dr. Lira crouched beside the violet‑sanded dunes of Kepler‑9, her instruments humming as the twin suns set behind jagged basalt spires. She brushed a crystal shard from the ground, and a faint blue glow pulsed from its core, scattering iridescent particles into the thin, ozone‑laden air. "This isn't any known isotope," she whispered, tapping the scanner and watching the readout flicker to a symbol she had never seen. Suddenly, the ground trembled and a fissure split open, spewing a torrent of luminous vapor that coalesced into floating, metallic ribbons.
Lira snapped her gloves shut, shouting, "Contain it!" as the ribbons began to rearrange the surrounding magnetic field, pulling her equipment toward the glowing fissure.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8

## 39. creative · technology · `6db333efcd45`

**Q:** Write a short pitch (3‑8 sentences) for a futuristic home‑automation gadget that helps reduce household energy waste. Your pitch should identify the target user, describe one innovative feature, and end with a memorable tagline of five words or fewer.

**Path P1:** Creative brief for an energy‑saving home‑automation gadget

- `P1.C1` correctness, core, w=1: Identifies a specific target user group for the gadget.
- `P1.C2` correctness, core, w=1: Describes exactly one innovative feature of the gadget.
- `P1.C3` correctness, non-core, w=0.5: Ends with a tagline that is a single memorable phrase of five words or fewer.
- `P1.C4` expression, non-core, w=0.5: Uses at least one vivid sensory adjective to describe the gadget.
- `P1.C5` expression, non-core, w=0.5: Does not contain any of the following cliché phrases: "revolutionary", "cutting‑edge", "game‑changer", "next generation".

**Obvious answers (originality check):**

- A pitch for a smart thermostat that learns daily routines and lowers heating when rooms are empty.
- A pitch for solar‑powered window sensors that close blinds automatically to reduce glare and cooling costs.
- A pitch for an AI‑driven lighting system that dims lights based on natural daylight levels.
- A pitch for a water‑usage monitor that alerts users to leaks and excessive flow.
- A pitch for a smart plug that shuts off standby power for idle appliances.

**Reference answer** (path P1):

> Eco‑savvy homeowners who juggle work‑from‑home schedules will love the new AuraPulse hub. Its sleek, whisper‑quiet sensor array learns each appliance’s energy rhythm and automatically throttles power the moment it detects wasteful standby. By visualizing real‑time consumption on a luminous, glass‑like display, users can instantly spot and curb hidden leaks. Smart, silent savings.

Review: [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5 [ ] 6 [ ] 7 [ ] 8
