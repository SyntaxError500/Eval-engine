# Feedback review (Phase 6 gate)

Each evaluation shows what the learner sees, then the grading details it should be faithful to. Please mark each evaluation pass or fail against the checklist, and for a fail say which point and why. The gate is a pass rate of at least 90% (27 of 30).

Checklist:

1. Specific: each point names what in the answer led to it
2. Actionable: each problem point says what to do next
3. At most 3 problem points
4. Says what worked, when anything did
5. Faithful: nothing contradicts the grading details or misstates the answer
6. No reference-answer leakage: no wording or content taken from the hidden model answer
7. Route note, when shown, is in the right voice: neutral when accepted, distinct with a reason when not

Wording comes from a small local model, under code checks; a point marked *(template)* is the plain fallback used when the model's wording failed a check. Grading itself was validated in Phases 2 and 4; a disagreement with a verdict is worth noting but is not a feedback failure unless the feedback misstates it.

## E1: cell-good (factual)

**Question:** Name three distinct phases of the cell cycle and give one key event that occurs in each phase. Answer in a short paragraph (3‑8 sentences).

**Learner answer:** The cell cycle includes G1, S phase and M phase. In G1 the cell grows and produces the proteins and organelles it will need. During S phase the entire genome is replicated, so each chromosome ends up as two sister chromatids. In M phase (mitosis) the sister chromatids are pulled to opposite poles and the cell divides into two daughter cells.

**What the learner sees:**

```
What worked:
  - You correctly name G1 as a cell-cycle phase.
  - You correctly name three distinct phases: G1, S phase, and M phase.

Bands:
  correctness   Strong
  completeness  Strong
```

**Grading details:**

- met (core): Names a valid cell‑cycle phase (e.g., G1, S, G2, or M).
- met (core): Provides a correct key event that occurs in the phase named in C1.
- met (core): Names a second valid cell‑cycle phase (e.g., G1, S, G2, or M).
- met (core): Provides a correct key event that occurs in the phase named in C3.
- met (core): Names a third valid cell‑cycle phase (e.g., G1, S, G2, or M).
- met (core): Provides a correct key event that occurs in the phase named in C5.
- met (core): The three phases named are all different from each other.

**Hidden model answer (never shown to the learner):** During G1, the cell grows and synthesizes proteins needed for DNA replication, such as cyclins that prepare the cell for S phase. In S phase, each chromosome is duplicated so that sister chromatids are formed, ensuring that each daughter cell will receive a complete set of genetic material. G2 is a checkpoint period where the cell checks for DNA damage and accumulates the proteins required for mitosis, such as mitotic cyclins, before entering M phase.

**Verdict:** pass / fail, and why:

## E2: cell-partial (factual)

**Question:** Name three distinct phases of the cell cycle and give one key event that occurs in each phase. Answer in a short paragraph (3‑8 sentences).

**Learner answer:** In G1 the cell grows and makes proteins. In S phase the DNA is copied so there are two complete sets. After that the cell gets ready to divide.

**What the learner sees:**

```
To work on:
  1. You don't name a third distinct phase (G2 or M), instead referring vaguely to 'After that'. Add a third phase and explain its key event.
  2. You only name two phases (G1 and S), not three distinct ones. Name a third phase and describe its key event.

What worked:
  - You name G1 and describe its key event of cell growth and protein production.

Bands:
  correctness   Proficient
  completeness  Not yet
```

**Grading details:**

- met (core): Names a valid cell‑cycle phase (e.g., G1, S, G2, or M).
- met (core): Provides a correct key event that occurs in the phase named in C1.
- met (core): Names a second valid cell‑cycle phase (e.g., G1, S, G2, or M).
- met (core): Provides a correct key event that occurs in the phase named in C3.
- not met (core): Names a third valid cell‑cycle phase (e.g., G1, S, G2, or M).
- not met (core): Provides a correct key event that occurs in the phase named in C5.
- not met (core): The three phases named are all different from each other.

**Hidden model answer (never shown to the learner):** During G1, the cell grows and synthesizes proteins needed for DNA replication, such as cyclins that prepare the cell for S phase. In S phase, each chromosome is duplicated so that sister chromatids are formed, ensuring that each daughter cell will receive a complete set of genetic material. G2 is a checkpoint period where the cell checks for DNA damage and accumulates the proteins required for mitosis, such as mitotic cyclins, before entering M phase.

**Verdict:** pass / fail, and why:

## E3: cell-wrong (factual)

**Question:** Name three distinct phases of the cell cycle and give one key event that occurs in each phase. Answer in a short paragraph (3‑8 sentences).

**Learner answer:** In G1 the cell copies all of its DNA. In S phase the cell splits into two daughter cells. In M phase the cell rests and grows larger before the next round.

**What the learner sees:**

```
To work on:
  1. You wrote: "In G1 the cell copies all of its DNA." DNA replication occurs in S phase, not G1. Add DNA replication in S phase.
  2. You wrote: "In S phase the cell splits into two daughter cells." Cell division occurs in M phase, not S phase. Add cell division in M phase.
  3. You wrote: "In M phase the cell rests and grows larger before the next round." Cell growth and rest occur during G phases, whereas M phase involves mitosis/cytokinesis. Add mitosis or cytokinesis in M phase.

What worked:
  - You named G1 as a phase.
  - You named three different phases.

Bands:
  correctness   Developing
  completeness  Strong
```

**Grading details:**

- met (core): Names a valid cell‑cycle phase (e.g., G1, S, G2, or M).
- not met (core): Provides a correct key event that occurs in the phase named in C1.
- met (core): Names a second valid cell‑cycle phase (e.g., G1, S, G2, or M).
- not met (core): Provides a correct key event that occurs in the phase named in C3.
- met (core): Names a third valid cell‑cycle phase (e.g., G1, S, G2, or M).
- not met (core): Provides a correct key event that occurs in the phase named in C5.
- met (core): The three phases named are all different from each other.
- factual error: "In G1 the cell copies all of its DNA." (DNA replication occurs in S phase, not G1.)
- factual error: "In S phase the cell splits into two daughter cells." (Cell division occurs in M phase, not S phase.)
- factual error: "In M phase the cell rests and grows larger before the next round." (Cell growth and rest occur during G phases, whereas M phase involves mitosis/cytokinesis.)

**Hidden model answer (never shown to the learner):** During G1, the cell grows and synthesizes proteins needed for DNA replication, such as cyclins that prepare the cell for S phase. In S phase, each chromosome is duplicated so that sister chromatids are formed, ensuring that each daughter cell will receive a complete set of genetic material. G2 is a checkpoint period where the cell checks for DNA damage and accumulates the proteins required for mitosis, such as mitotic cyclins, before entering M phase.

**Verdict:** pass / fail, and why:

## E4: macro-partial (factual)

**Question:** In a short paragraph (3-8 sentences), name the three main macronutrients required by the human body and state one primary function of each.

**Learner answer:** Carbohydrates give the body energy. Proteins build and repair muscle. Vitamins are the third macronutrient and they keep the immune system strong.

**What the learner sees:**

```
To work on:
  1. You wrote: "Vitamins are the third macronutrient". Vitamins are micronutrients, not macronutrients. Add the correct third macronutrient and state its primary function.

What worked:
  - You stated a correct function for carbohydrates. "Carbohydrates give the body energy."

Bands:
  completeness  Not yet
  correctness   Developing
```

**Grading details:**

- not met (core): Names three distinct macronutrients required by the human body
- met (core): States a primary function of the first macronutrient named
- met (core): States a primary function of the second macronutrient named
- not met (core): States a primary function of the third macronutrient named
- factual error: "Vitamins are the third macronutrient" (Vitamins are micronutrients, not macronutrients.)

**Hidden model answer (never shown to the learner):** The three main macronutrients needed by the human body are carbohydrates, proteins, and fats. Carbohydrates provide the primary source of energy for cells, especially the brain and muscles. Proteins supply the building blocks—amino acids—required for the growth, repair, and maintenance of tissues. Fats serve as a dense energy reserve, help absorb fat‑soluble vitamins, and are essential for constructing cell membranes.

**Verdict:** pass / fail, and why:

## E5: macro-wrong (factual)

**Question:** In a short paragraph (3-8 sentences), name the three main macronutrients required by the human body and state one primary function of each.

**Learner answer:** The three macronutrients are carbohydrates, proteins and fats. Carbohydrates are mainly used to build bones. Proteins are the body's fastest source of energy. Fats carry oxygen around in the blood.

**What the learner sees:**

```
To work on:
  1. You wrote: "Carbohydrates are mainly used to build bones." Carbohydrates do not build bones; calcium and other minerals do. Add the correct function of carbohydrates.
  2. You wrote: "Proteins are the body's fastest source of energy." Carbohydrates are the body's fastest source of energy, not proteins. Add the correct function of proteins.
  3. You wrote: "Fats carry oxygen around in the blood." Red blood cells and hemoglobin carry oxygen, not fats. Add the correct function of fats.

What worked:
  - You correctly name the three main macronutrients required by the human body.

Bands:
  completeness  Strong
  correctness   Not yet
```

**Grading details:**

- met (core): Names three distinct macronutrients required by the human body
- not met (core): States a primary function of the first macronutrient named
- not met (core): States a primary function of the second macronutrient named
- not met (core): States a primary function of the third macronutrient named
- factual error: "Carbohydrates are mainly used to build bones." (Carbohydrates do not build bones; calcium and other minerals do.)
- factual error: "Proteins are the body's fastest source of energy." (Carbohydrates are the body's fastest source of energy, not proteins.)
- factual error: "Fats carry oxygen around in the blood." (Red blood cells and hemoglobin carry oxygen, not fats.)

**Hidden model answer (never shown to the learner):** The three main macronutrients needed by the human body are carbohydrates, proteins, and fats. Carbohydrates provide the primary source of energy for cells, especially the brain and muscles. Proteins supply the building blocks—amino acids—required for the growth, repair, and maintenance of tissues. Fats serve as a dense energy reserve, help absorb fat‑soluble vitamins, and are essential for constructing cell membranes.

**Verdict:** pass / fail, and why:

## E6: macro-off (factual)

**Question:** In a short paragraph (3-8 sentences), name the three main macronutrients required by the human body and state one primary function of each.

**Learner answer:** Calcium keeps bones strong, iron helps carry oxygen in the blood, and potassium helps the heart and muscles work properly.

**What the learner sees:**

```
To work on:
  1. You wrote: "Calcium keeps bones strong, iron helps carry oxygen in the blood, and potassium helps the heart and muscles work properly." These are minerals, which are micronutrients, not macronutrients. Add the three main macronutrients: carbohydrates, proteins, and fats.
  2. You did not name any macronutrient, so no function for a first macronutrient can be credited. Name the three main macronutrients required by the human body.

Bands:
  completeness  Not yet
  correctness   Not yet
```

**Grading details:**

- not met (core): Names three distinct macronutrients required by the human body
- not met (core): States a primary function of the first macronutrient named
- not met (core): States a primary function of the second macronutrient named
- not met (core): States a primary function of the third macronutrient named
- factual error: "Calcium keeps bones strong, iron helps carry oxygen in the blood, and potassium helps the heart and muscles work properly." (These are minerals, which are micronutrients, not macronutrients.)

**Hidden model answer (never shown to the learner):** The three main macronutrients needed by the human body are carbohydrates, proteins, and fats. Carbohydrates provide the primary source of energy for cells, especially the brain and muscles. Proteins supply the building blocks—amino acids—required for the growth, repair, and maintenance of tissues. Fats serve as a dense energy reserve, help absorb fat‑soluble vitamins, and are essential for constructing cell membranes.

**Verdict:** pass / fail, and why:

## E7: balloon-partial (explanatory)

**Question:** Explain why a hot‑air balloon rises when the air inside it is heated. Answer in a short paragraph (3‑8 sentences).

**Learner answer:** Hot air rises, so when the burner heats the air inside the balloon, the balloon goes up with it. Turning the burner off makes it come back down.

**What the learner sees:**

```
To work on:
  1. You say heating makes the balloon go up, but you don't explain that the air inside becomes less dense than the surrounding air. Add how heating reduces air density compared to the cooler air outside.
  2. You mention the balloon goes up when heated, but you don't explain why. Explain how the lower density causes a buoyant force that lifts the balloon.
  3. You don't mention that the surrounding air is cooler, which is needed to create the lift. Mention the temperature difference between the inside and outside air.

Bands:
  correctness   Developing
  reasoning     Not yet
  completeness  Not yet
```

**Grading details:**

- not met (core): States that heating the air inside the balloon reduces its density compared to the surrounding cooler air
- not met (core): Links the lower density of the heated air to a net upward buoyant force that lifts the balloon
- not met (core): Mentions that the surrounding air is cooler (or at ambient temperature) providing the contrast needed for lift

**Hidden model answer (never shown to the learner):** When the air inside a hot‑air balloon is heated, its temperature rises and the air expands, which lowers its density compared to the cooler surrounding atmosphere. Because the heated air is less dense, the weight of the air displaced by the balloon is greater than the weight of the air inside it. This difference creates a net upward buoyant force, as described by Archimedes' principle. The surrounding air, being at ambient temperature, remains denser and thus exerts a greater downward pressure on the balloon than the lighter air inside can counteract, causing the balloon to rise.

**Verdict:** pass / fail, and why:

## E8: balloon-wrong (explanatory)

**Question:** Explain why a hot‑air balloon rises when the air inside it is heated. Answer in a short paragraph (3‑8 sentences).

**Learner answer:** Heating air makes it denser and heavier, but the expanding gas pushes down hard on the basket like a rocket, which drives the balloon upward. Heat itself is a gas lighter than air, so it also carries the balloon up.

**What the learner sees:**

```
To work on:
  1. You wrote: "Heating air makes it denser and heavier". Heating air actually decreases its density rather than increasing it. Add that heating the air inside the balloon reduces its density compared to the surrounding cooler air.
  2. You wrote: "the expanding gas pushes down hard on the basket like a rocket". Hot air balloons do not rise due to rocket-like exhaust pushing on the basket. Link the lower density of the heated air to a net upward buoyant force that lifts the balloon.
  3. You wrote: "Heat itself is a gas lighter than air". Heat is energy, not a gas. Correct this statement to explain that heated air becomes less dense than the surrounding air.

Bands:
  correctness   Not yet
  reasoning     Not yet
  completeness  Not yet
```

**Grading details:**

- not met (core): States that heating the air inside the balloon reduces its density compared to the surrounding cooler air
- not met (core): Links the lower density of the heated air to a net upward buoyant force that lifts the balloon
- not met (core): Mentions that the surrounding air is cooler (or at ambient temperature) providing the contrast needed for lift
- factual error: "Heating air makes it denser and heavier" (Heating air actually decreases its density rather than increasing it.)
- factual error: "the expanding gas pushes down hard on the basket like a rocket" (Hot air balloons do not rise due to rocket-like exhaust pushing on the basket.)
- factual error: "Heat itself is a gas lighter than air" (Heat is energy, not a gas.)

**Hidden model answer (never shown to the learner):** When the air inside a hot‑air balloon is heated, its temperature rises and the air expands, which lowers its density compared to the cooler surrounding atmosphere. Because the heated air is less dense, the weight of the air displaced by the balloon is greater than the weight of the air inside it. This difference creates a net upward buoyant force, as described by Archimedes' principle. The surrounding air, being at ambient temperature, remains denser and thus exerts a greater downward pressure on the balloon than the lighter air inside can counteract, causing the balloon to rise.

**Verdict:** pass / fail, and why:

## E9: rain-partial (explanatory)

**Question:** Explain why mountain ranges often create dry regions on their leeward side (rain shadows). In a short paragraph of 3–8 sentences, state the main atmospheric mechanism responsible, describe how it leads to reduced precipitation on the leeward side, and give one supporting fact that illustrates this process.

**Learner answer:** Rain shadows are caused by orographic lift. Moist air is pushed up the windward side of the mountains, where it cools and drops most of its moisture as rain.

**What the learner sees:**

```
To work on:
  1. You describe the mechanism but do not explain how descending air warms, loses relative humidity, and results in reduced precipitation on the leeward side. Add how the air warms and dries as it descends.
  2. You do not provide a supporting fact like a temperature drop or a real-world example. Add a quantitative fact or name a known rain-shadow region.

What worked:
  - You correctly state that orographic lift causes moist air to rise, cool, and release precipitation on the windward side.

Bands:
  correctness   Strong
  reasoning     Not yet
  completeness  Not yet
```

**Grading details:**

- met (core): States the main atmospheric mechanism responsible for rain shadows (orographic lift causing precipitation on the windward side and descending dry air on the leeward side).
- not met (core): Describes how the mechanism leads to reduced precipitation on the leeward side (descending air warms, its relative humidity drops, and precipitation decreases).
- not met (core): Gives one supporting fact that illustrates the process (e.g., temperature drops ~6 °C per km of ascent, or cites a known rain‑shadow region such as the leeward side of the Cascades).

**Hidden model answer (never shown to the learner):** When moist air is forced up a mountain range, it undergoes orographic lift: the ascent causes the air to expand and cool, reaching its dew point and releasing precipitation on the windward side. After shedding much of its moisture, the air then descends on the leeward side, where compression warms it and lowers its relative humidity, inhibiting further cloud formation and rain. This descending, now drier and warmer air creates a rain‑shadow region with markedly reduced precipitation. A classic example is the dry interior of Washington State east of the Cascade Range, which receives only about one‑quarter of the rainfall that falls on the western slopes.

**Verdict:** pass / fail, and why:

## E10: rain-wrong (explanatory)

**Question:** Explain why mountain ranges often create dry regions on their leeward side (rain shadows). In a short paragraph of 3–8 sentences, state the main atmospheric mechanism responsible, describe how it leads to reduced precipitation on the leeward side, and give one supporting fact that illustrates this process.

**Learner answer:** The leeward side is dry because the mountains block the sunlight, so less water evaporates there and fewer clouds can form. The Himalayas are dry on their southern side for this reason.

**What the learner sees:**

```
Your answer takes a different route from the usual ones for this question, so that route was checked separately. It didn't hold up: You didn't explain the atmospheric mechanism. Focus on how air rises, cools, and descends to create dry regions.

To work on:
  1. You said 'mountains block the sunlight' which is incorrect. Rain shadows are caused by air rising, cooling, and descending. Add how uplift causes precipitation on the windward side and dry air on the leeward side.
  2. You mentioned the Himalayas' southern side being dry, but this is actually the windward side. Give a fact about a known rain shadow region, like the leeward side of the Cascades.

Bands:
  correctness   Not yet
  reasoning     Not yet
  completeness  Not yet
```

**Grading details:**

- not met (core): States the main atmospheric mechanism responsible for rain shadows (orographic lift causing precipitation on the windward side and descending dry air on the leeward side).
- not met (core): Describes how the mechanism leads to reduced precipitation on the leeward side (descending air warms, its relative humidity drops, and precipitation decreases).
- not met (core): Gives one supporting fact that illustrates the process (e.g., temperature drops ~6 °C per km of ascent, or cites a known rain‑shadow region such as the leeward side of the Cascades).
- factual error: "The leeward side is dry because the mountains block the sunlight, so less water evaporates there and fewer clouds can form." (Rain shadows are caused by atmospheric uplift, cooling, and descending warming air, not by mountains blocking sunlight.)
- factual error: "The Himalayas are dry on their southern side for this reason." (The southern side of the Himalayas is actually the windward side, which receives very high precipitation (monsoon rains), whereas the northern side (Tibetan Plateau) is the dry leeward rain shadow.)
- different route checked: not taken up: The answer does not correctly explain the atmospheric mechanism that creates rain shadows; it offers an inaccurate explanation about sunlight blockage and evaporation, which is not a valid approach and does not differ from the rubric's correct approach. Therefore it is not a new valid approach.

**Hidden model answer (never shown to the learner):** When moist air is forced up a mountain range, it undergoes orographic lift: the ascent causes the air to expand and cool, reaching its dew point and releasing precipitation on the windward side. After shedding much of its moisture, the air then descends on the leeward side, where compression warms it and lowers its relative humidity, inhibiting further cloud formation and rain. This descending, now drier and warmer air creates a rain‑shadow region with markedly reduced precipitation. A classic example is the dry interior of Washington State east of the Cascade Range, which receives only about one‑quarter of the rainfall that falls on the western slopes.

**Verdict:** pass / fail, and why:

## E11: rain-off (explanatory)

**Question:** Explain why mountain ranges often create dry regions on their leeward side (rain shadows). In a short paragraph of 3–8 sentences, state the main atmospheric mechanism responsible, describe how it leads to reduced precipitation on the leeward side, and give one supporting fact that illustrates this process.

**Learner answer:** Monsoons happen because land heats up faster than the ocean in summer. The warm land draws in moist ocean air, which brings months of heavy rain to places like India.

**What the learner sees:**

```
Your answer is about something else ("Monsoons happen because land heats up faster than the ocean in summer"). Reread the question and answer what it asks: Explain why mountain ranges often create dry regions on their leeward side (rain shadows). In a short paragraph of 3–8 sentences, state the main atmospheric mechanism responsible, describe how it leads to reduced precipitation on the leeward side, and give one supporting fact that illustrates this process.  (template)

Bands:
  correctness   Not yet
  reasoning     Not yet
  completeness  Not yet
```

**Grading details:**

- not met (core): States the main atmospheric mechanism responsible for rain shadows (orographic lift causing precipitation on the windward side and descending dry air on the leeward side).
- not met (core): Describes how the mechanism leads to reduced precipitation on the leeward side (descending air warms, its relative humidity drops, and precipitation decreases).
- not met (core): Gives one supporting fact that illustrates the process (e.g., temperature drops ~6 °C per km of ascent, or cites a known rain‑shadow region such as the leeward side of the Cascades).
- factual error: "Monsoons happen because land heats up faster than the ocean in summer." (This statement is entirely about monsoons and is off-topic regarding mountain rain shadows.)
- the judge found the answer does not address the question

**Hidden model answer (never shown to the learner):** When moist air is forced up a mountain range, it undergoes orographic lift: the ascent causes the air to expand and cool, reaching its dew point and releasing precipitation on the windward side. After shedding much of its moisture, the air then descends on the leeward side, where compression warms it and lowers its relative humidity, inhibiting further cloud formation and rain. This descending, now drier and warmer air creates a rain‑shadow region with markedly reduced precipitation. A classic example is the dry interior of Washington State east of the Cascade Range, which receives only about one‑quarter of the rainfall that falls on the western slopes.

**Verdict:** pass / fail, and why:

## E12: wfh-partial (analytical)

**Question:** In a short paragraph (3–8 sentences), argue whether working from home increases overall work‑life balance, and support your argument with at least two distinct reasons.

**Learner answer:** Working from home improves work-life balance because people no longer waste time commuting. That time can be spent with family instead.

**What the learner sees:**

```
To work on:
  1. You only provide one reason. Add a second distinct reason that supports the idea that working from home improves work-life balance.

What worked:
  - You correctly mention reduced commuting time as a reason for improved work-life balance.
  - You clearly state that working from home improves work-life balance.

Bands:
  correctness   Strong
  reasoning     Developing
```

**Grading details:**

- met (core): States a position that working from home increases overall work‑life balance
- met (core): Provides a first distinct reason that supports the position
- not met (core): Provides a second distinct reason that supports the position

**Hidden model answer (never shown to the learner):** Working from home generally improves overall work‑life balance because it eliminates the time and stress associated with commuting, allowing employees to allocate that saved time to personal activities or family. Additionally, the flexibility of setting one's own schedule enables better alignment of work tasks with peak productivity periods and personal responsibilities, reducing the need to sacrifice one for the other. These factors together create a more harmonious integration of professional and personal life.

**Verdict:** pass / fail, and why:

## E13: wfh-wrong (analytical)

**Question:** In a short paragraph (3–8 sentences), argue whether working from home increases overall work‑life balance, and support your argument with at least two distinct reasons.

**Learner answer:** Working from home has advantages and disadvantages. Some people like skipping the commute, while others miss their colleagues. In the end it really depends on the person and their job.

**What the learner sees:**

```
To work on:
  1. You don't provide a supporting reason for how working from home increases work-life balance. Add a reason, such as time saved on commuting or flexibility in scheduling.
  2. You don't state a clear position that working from home increases work-life balance. Explain your stance clearly, such as how it reduces stress or improves time management.

Bands:
  correctness   Developing
  reasoning     Not yet
```

**Grading details:**

- not met (core): States a position that working from home increases overall work‑life balance
- not met (core): Provides a first distinct reason that supports the position
- not met (core): Provides a second distinct reason that supports the position

**Hidden model answer (never shown to the learner):** Working from home generally improves overall work‑life balance because it eliminates the time and stress associated with commuting, allowing employees to allocate that saved time to personal activities or family. Additionally, the flexibility of setting one's own schedule enables better alignment of work tasks with peak productivity periods and personal responsibilities, reducing the need to sacrifice one for the other. These factors together create a more harmonious integration of professional and personal life.

**Verdict:** pass / fail, and why:

## E14: wfh-off (analytical)

**Question:** In a short paragraph (3–8 sentences), argue whether working from home increases overall work‑life balance, and support your argument with at least two distinct reasons.

**Learner answer:** Working from home makes companies more productive. Employees face fewer interruptions from co-workers, and firms save money on office space, which they can invest elsewhere.

**What the learner sees:**

```
Your answer doesn't address the question, which asks you to argue whether working from home increases work-life balance. You should explain how it affects work-life balance, not just company productivity and costs.

Bands:
  correctness   Developing
  reasoning     Not yet
```

**Grading details:**

- not met (core): States a position that working from home increases overall work‑life balance
- not met (core): Provides a first distinct reason that supports the position
- not met (core): Provides a second distinct reason that supports the position
- the judge found the answer does not address the question

**Hidden model answer (never shown to the learner):** Working from home generally improves overall work‑life balance because it eliminates the time and stress associated with commuting, allowing employees to allocate that saved time to personal activities or family. Additionally, the flexibility of setting one's own schedule enables better alignment of work tasks with peak productivity periods and personal responsibilities, reducing the need to sacrifice one for the other. These factors together create a more harmonious integration of professional and personal life.

**Verdict:** pass / fail, and why:

## E15: wwi-nationalism (analytical)

**Question:** In a short paragraph (3–8 sentences), argue whether the primary cause of the outbreak of World War I was the system of alliances or nationalist rivalries, and support your position with specific historical evidence.

**Learner answer:** Nationalist rivalry, not the treaties, was what really started the war. Gavrilo Princip, a Bosnian Serb tied to the Black Hand group that wanted South Slavs freed from Habsburg rule, shot Archduke Franz Ferdinand in Sarajevo on 28 June 1914. Austria-Hungary was determined to crush Serbian nationalism, which it saw as a threat to its multi-ethnic empire, and Russia backed Serbia out of Pan-Slav feeling. The alliances only spread a fire that national hatreds had lit.

**What the learner sees:**

```
What worked:
  - You explain how national hatreds and nationalist dynamics led to the conflict's escalation.
  - You clearly state a position that nationalist rivalries were the primary cause.

Bands:
  completeness  Strong
  correctness   Strong
  reasoning     Strong
```

**Grading details:**

- met (core): States a position that the primary cause was nationalist rivalries
- met (core): Provides a specific historical example that supports nationalist rivalries as the primary cause
- met (core): Explains how the example shows nationalist rivalries led to the war

**Hidden model answer (never shown to the learner):** The primary cause of World War I was the rigid system of alliances that bound the great powers to each other. When Archduke Franz Ferdinand was assassinated in June 1914, Austria‑Hungary's declaration of war on Serbia triggered Russia's mobilization to protect its Slavic ally, which in turn forced Germany to honor its alliance with Austria‑Hungary and declare war on Russia. France, bound by the Franco‑Russian alliance, was then compelled to support Russia, while Britain entered the conflict due to its entente with France and its agreement to protect Belgian neutrality, which Germany violated. This cascade of obligations turned a regional dispute into a continental war, illustrating how the alliance network transformed a localized crisis into a full‑scale global conflict.

**Verdict:** pass / fail, and why:

## E16: wwi-partial (analytical)

**Question:** In a short paragraph (3–8 sentences), argue whether the primary cause of the outbreak of World War I was the system of alliances or nationalist rivalries, and support your position with specific historical evidence.

**Learner answer:** I think the alliances were the main cause. The countries had promised to help each other, so once one country went to war the others had to as well.

**What the learner sees:**

```
To work on:
  1. You don't mention specific alliances like the Triple Alliance or events like the July Crisis. Add an example of an alliance and explain how it led to the war.

What worked:
  - You state the position that alliances were the main cause. Make sure to clearly connect your example to this claim.

Bands:
  completeness  Strong
  correctness   Developing
  reasoning     Not yet
```

**Grading details:**

- met (core): States a position that the primary cause was the system of alliances
- not met (core): Provides a specific historical example that supports the alliance system as the primary cause
- not met (core): Explains how the example demonstrates that the alliance system caused the war

**Hidden model answer (never shown to the learner):** The primary cause of World War I was the rigid system of alliances that bound the great powers to each other. When Archduke Franz Ferdinand was assassinated in June 1914, Austria‑Hungary's declaration of war on Serbia triggered Russia's mobilization to protect its Slavic ally, which in turn forced Germany to honor its alliance with Austria‑Hungary and declare war on Russia. France, bound by the Franco‑Russian alliance, was then compelled to support Russia, while Britain entered the conflict due to its entente with France and its agreement to protect Belgian neutrality, which Germany violated. This cascade of obligations turned a regional dispute into a continental war, illustrating how the alliance network transformed a localized crisis into a full‑scale global conflict.

**Verdict:** pass / fail, and why:

## E17: wwi-wrong (analytical)

**Question:** In a short paragraph (3–8 sentences), argue whether the primary cause of the outbreak of World War I was the system of alliances or nationalist rivalries, and support your position with specific historical evidence.

**Learner answer:** The alliance system was the main cause. In 1914 a Russian student assassinated Archduke Franz Ferdinand in Vienna, and because Italy and Germany were allied they immediately invaded France together. Britain then joined to defend its ally Russia.

**What the learner sees:**

```
To work on:
  1. You wrote: "In 1914 a Russian student assassinated Archduke Franz Ferdinand in Vienna..." This is factually incorrect. The assassination was carried out by Serbian nationalists, not a Russian student, and it occurred in Sarajevo, not Vienna. You should correct these details.

What worked:
  - You clearly stated that the alliance system was the main cause of the war, which meets the requirement.

Bands:
  completeness  Strong
  correctness   Not yet
  reasoning     Not yet
```

**Grading details:**

- met (core): States a position that the primary cause was the system of alliances
- not met (core): Provides a specific historical example that supports the alliance system as the primary cause
- not met (core): Explains how the example demonstrates that the alliance system caused the war
- factual error: "In 1914 a Russian student assassinated Archduke Franz Ferdinand in Vienna, and because Italy and Germany were allied they immediately invaded France together. Britain then joined to defend its ally Russia." (The specific historical details regarding who did the assassinating, where it happened, and how the alliances mobilized are factually incorrect.)

**Hidden model answer (never shown to the learner):** The primary cause of World War I was the rigid system of alliances that bound the great powers to each other. When Archduke Franz Ferdinand was assassinated in June 1914, Austria‑Hungary's declaration of war on Serbia triggered Russia's mobilization to protect its Slavic ally, which in turn forced Germany to honor its alliance with Austria‑Hungary and declare war on Russia. France, bound by the Franco‑Russian alliance, was then compelled to support Russia, while Britain entered the conflict due to its entente with France and its agreement to protect Belgian neutrality, which Germany violated. This cascade of obligations turned a regional dispute into a continental war, illustrating how the alliance network transformed a localized crisis into a full‑scale global conflict.

**Verdict:** pass / fail, and why:

## E18: coffee-obvious (creative)

**Question:** Write a brief (3–6 sentences) scene describing a person waiting in line at a coffee shop, focusing on the protagonist’s internal thoughts, include at least one tactile detail, and end with a subtle hint of an upcoming decision.

**Learner answer:** She watched the steam curl above the espresso machine while the queue crept forward. The warm mug of the woman in front brushed her hand, and she thought about the barista she had a crush on. Should she finally ask him out? She smiled to herself and decided she would speak to him later.

**What the learner sees:**

```
Your main idea is close to one of the most predictable takes on this brief. For comparison, that take is: "She watches steam rise, feels the warm mug in her hand, wonders if she should ask the barista out, ending with a quiet resolve to speak later." It wasn't marked down, but a less expected angle would stand out more.

What worked:
  - You show the protagonist thinking about the barista.
  - You end with the protagonist deciding to speak to the barista.

Bands:
  correctness   Strong
  expression    Strong
```

**Grading details:**

- met (core): Provides a narrative scene describing a person waiting in line at a coffee shop
- met (core): Includes internal thoughts of the protagonist
- met (core): Provides at least one tactile detail
- met (core): Ends with a subtle hint of an upcoming decision
- reuses an obvious idea (not marked down): She watches steam rise, feels the warm mug in her hand, wonders if she should ask the barista out, ending with a quiet resolve to speak later.

**Hidden model answer (never shown to the learner):** She stood in the coffee shop line, the cold metal of the countertop pressing against her palm as she adjusted her grip on the worn notebook. While the espresso machine hissed, her mind replayed the email she’d just read, weighing whether to quit her job or stay for the safety net it provided. The scent of roasted beans mingled with the faint buzz of conversation, making her stomach knot with nervous anticipation. She watched the barista’s steady hands and wondered if she should finally ask for the promotion she’d been eyeing. As she reached the front, she felt the weight of the decision settle like the warm cup she was about to receive.

**Verdict:** pass / fail, and why:

## E19: coffee-partial (creative)

**Question:** Write a brief (3–6 sentences) scene describing a person waiting in line at a coffee shop, focusing on the protagonist’s internal thoughts, include at least one tactile detail, and end with a subtle hint of an upcoming decision.

**Learner answer:** Tom stood in the long line at the coffee shop. He wondered whether they still had blueberry muffins and thought about how late he would be for work. The line moved slowly. Finally he reached the front and ordered a latte.

**What the learner sees:**

```
To work on:
  1. Your answer ends with a direct action rather than a subtle hint of an upcoming decision. Add a thought or feeling that suggests a choice is about to be made.
  2. Your answer doesn't include any tactile details such as feeling textures, temperatures, or physical sensations. Add a description of a physical sensation to make the scene more vivid.

What worked:
  - You include the protagonist's internal thoughts about the muffins and being late for work.
  - You clearly describe Tom waiting in line at a coffee shop.

Bands:
  correctness   Developing
  expression    Developing
```

**Grading details:**

- met (core): Provides a narrative scene describing a person waiting in line at a coffee shop
- met (core): Includes internal thoughts of the protagonist
- not met (core): Provides at least one tactile detail
- not met (core): Ends with a subtle hint of an upcoming decision

**Hidden model answer (never shown to the learner):** She stood in the coffee shop line, the cold metal of the countertop pressing against her palm as she adjusted her grip on the worn notebook. While the espresso machine hissed, her mind replayed the email she’d just read, weighing whether to quit her job or stay for the safety net it provided. The scent of roasted beans mingled with the faint buzz of conversation, making her stomach knot with nervous anticipation. She watched the barista’s steady hands and wondered if she should finally ask for the promotion she’d been eyeing. As she reached the front, she felt the weight of the decision settle like the warm cup she was about to receive.

**Verdict:** pass / fail, and why:

## E20: coffee-wrong (creative)

**Question:** Write a brief (3–6 sentences) scene describing a person waiting in line at a coffee shop, focusing on the protagonist’s internal thoughts, include at least one tactile detail, and end with a subtle hint of an upcoming decision.

**Learner answer:** Rain dripped from the shelter roof as Priya waited for the number 12 bus. The cold metal bench pressed through her coat, and she wondered if the interview had gone as badly as she feared. When the bus finally appeared, she hesitated, her phone already open to the recruiter's number.

**What the learner sees:**

```
To work on:
  1. You describe waiting at a bus stop instead of a coffee shop. Add a detail about being in a coffee shop, such as the smell of coffee or the sound of a barista.

What worked:
  - You include the protagonist's internal thoughts about the interview.
  - You end with a hint of a decision about contacting the recruiter.

Bands:
  correctness   Developing
  expression    Strong
```

**Grading details:**

- not met (core): Provides a narrative scene describing a person waiting in line at a coffee shop
- met (core): Includes internal thoughts of the protagonist
- met (core): Provides at least one tactile detail
- met (core): Ends with a subtle hint of an upcoming decision

**Hidden model answer (never shown to the learner):** She stood in the coffee shop line, the cold metal of the countertop pressing against her palm as she adjusted her grip on the worn notebook. While the espresso machine hissed, her mind replayed the email she’d just read, weighing whether to quit her job or stay for the safety net it provided. The scent of roasted beans mingled with the faint buzz of conversation, making her stomach knot with nervous anticipation. She watched the barista’s steady hands and wondered if she should finally ask for the promotion she’d been eyeing. As she reached the front, she felt the weight of the decision settle like the warm cup she was about to receive.

**Verdict:** pass / fail, and why:

## E21: fire-cliche (creative)

**Question:** Write a short scene (3 to 8 sentences) that depicts a forest clearing after a wildfire, showing the first signs of ecological recovery as the first shoots emerge. Use vivid sensory details, include a character who observes the changes, and avoid the clichés 'phoenix rising' and 'silver lining'.

**Learner answer:** Old Tomas walked into the clearing where the pines had burned. Black stumps poked from the grey ash, and the smell of smoke still hung in the cool morning air. Then he saw it: a green shoot pushing through the cinders, like a phoenix rising from the flames. He crouched and touched its soft tip, amazed.

**What the learner sees:**

```
To work on:
  1. You used the phrase 'phoenix rising' which is not allowed. Avoid using this cliché in future. Try to describe the shoot in a new way.

Your main idea is close to one of the most predictable takes on this brief. For comparison, that take is: "A ranger watches tiny green shoots push through blackened soil, hears the faint rustle of recovering birds, and notes the smell of wet earth." It wasn't marked down, but a less expected angle would stand out more.

What worked:
  - You described the smell of smoke and the texture of the shoot, which adds to the sensory experience.
  - You included a character, Old Tomas, who observes the changes in the clearing.

Bands:
  correctness   Strong
  expression    Developing
```

**Grading details:**

- met (core): Contains between three and eight sentences
- met (core): Includes vivid sensory details describing sights, sounds, smells, or textures
- met (core): Features a character who observes the environmental changes
- met (core): Shows the first signs of ecological recovery, such as the emergence of new shoots
- not met (core): Does not use any of: "phoenix rising", "silver lining"
- reuses an obvious idea (not marked down): A ranger watches tiny green shoots push through blackened soil, hears the faint rustle of recovering birds, and notes the smell of wet earth.

**Hidden model answer (never shown to the learner):** Mara knelt among the blackened stumps, feeling the warm ash crumble beneath her fingertips as a faint wind carried the scent of char and pine resin. In the hush, the crackle of distant fireflies was replaced by the soft rustle of green buds pushing through the soot‑black soil. A pale shoot unfurled, its tender leaves glistening with dew, and the air filled with the sharp, hopeful perfume of new sap.


**Verdict:** pass / fail, and why:

## E22: fire-too-long (creative)

**Question:** Write a short scene (3 to 8 sentences) that depicts a forest clearing after a wildfire, showing the first signs of ecological recovery as the first shoots emerge. Use vivid sensory details, include a character who observes the changes, and avoid the clichés 'phoenix rising' and 'silver lining'.

**Learner answer:** Ana stepped into the clearing at dawn. The ground was black. Ash drifted in the breeze. It smelled of smoke and rain. A crow called from a dead pine. She walked to the centre. The soil crunched under her boots. Then she saw a green shoot. It was no bigger than a match. She smiled and knelt beside it.

**What the learner sees:**

```
To work on:
  1. Your answer has more than eight sentences. Keep it between three and eight sentences next time.

Your main idea is close to one of the most predictable takes on this brief. For comparison, that take is: "A ranger watches tiny green shoots push through blackened soil, hears the faint rustle of recovering birds, and notes the smell of wet earth." It wasn't marked down, but a less expected angle would stand out more.

What worked:
  - You included sensory details about smell and sound, which helps the reader imagine the scene.
  - You showed Ana observing the environmental changes.

Bands:
  correctness   Proficient
  expression    Strong
```

**Grading details:**

- not met (core): Contains between three and eight sentences
- met (core): Includes vivid sensory details describing sights, sounds, smells, or textures
- met (core): Features a character who observes the environmental changes
- met (core): Shows the first signs of ecological recovery, such as the emergence of new shoots
- met (core): Does not use any of: "phoenix rising", "silver lining"
- reuses an obvious idea (not marked down): A ranger watches tiny green shoots push through blackened soil, hears the faint rustle of recovering birds, and notes the smell of wet earth.

**Hidden model answer (never shown to the learner):** Mara knelt among the blackened stumps, feeling the warm ash crumble beneath her fingertips as a faint wind carried the scent of char and pine resin. In the hush, the crackle of distant fireflies was replaced by the soft rustle of green buds pushing through the soot‑black soil. A pale shoot unfurled, its tender leaves glistening with dew, and the air filled with the sharp, hopeful perfume of new sap.


**Verdict:** pass / fail, and why:

## E23: fire-no-character (creative)

**Question:** Write a short scene (3 to 8 sentences) that depicts a forest clearing after a wildfire, showing the first signs of ecological recovery as the first shoots emerge. Use vivid sensory details, include a character who observes the changes, and avoid the clichés 'phoenix rising' and 'silver lining'.

**Learner answer:** The clearing is a field of grey ash and charcoal stumps, still faintly warm. Rain has left a smell of wet smoke in the air. Here and there, thin green blades of fireweed are pushing through the crust, and a woodpecker drums on a scorched trunk.

**What the learner sees:**

```
To work on:
  1. Your answer doesn't include a character observing the changes. Add a character who notices the signs of recovery in the clearing.

What worked:
  - You describe the smell of wet smoke and the warmth of the ash, giving a clear sense of the environment.
  - You show new shoots emerging with 'thin green blades of fireweed pushing through the crust'.

Bands:
  correctness   Proficient
  expression    Strong
```

**Grading details:**

- met (core): Contains between three and eight sentences
- met (core): Includes vivid sensory details describing sights, sounds, smells, or textures
- not met (core): Features a character who observes the environmental changes
- met (core): Shows the first signs of ecological recovery, such as the emergence of new shoots
- met (core): Does not use any of: "phoenix rising", "silver lining"

**Hidden model answer (never shown to the learner):** Mara knelt among the blackened stumps, feeling the warm ash crumble beneath her fingertips as a faint wind carried the scent of char and pine resin. In the hush, the crackle of distant fireflies was replaced by the soft rustle of green buds pushing through the soot‑black soil. A pale shoot unfurled, its tender leaves glistening with dew, and the air filled with the sharp, hopeful perfume of new sap.


**Verdict:** pass / fail, and why:

## E24: fire-off (creative)

**Question:** Write a short scene (3 to 8 sentences) that depicts a forest clearing after a wildfire, showing the first signs of ecological recovery as the first shoots emerge. Use vivid sensory details, include a character who observes the changes, and avoid the clichés 'phoenix rising' and 'silver lining'.

**Learner answer:** The fire roared through the forest, crackling as it leapt from tree to tree. Smoke turned the sky orange, and the heat drove every animal toward the river. By nightfall the whole valley was burning.

**What the learner sees:**

```
To work on:
  1. Your answer describes the fire but doesn't include a character observing the changes. Add a character who notices the environment's transformation.
  2. You should show the first signs of ecological recovery, like new shoots emerging. Your answer focuses on the fire itself rather than the recovery process.

What worked:
  - You use sensory details like sound, sight, and heat to describe the fire.
  - You avoid the phrases 'phoenix rising' and 'silver lining'.

Bands:
  correctness   Not yet
  expression    Strong
```

**Grading details:**

- met (core): Contains between three and eight sentences
- met (core): Includes vivid sensory details describing sights, sounds, smells, or textures
- not met (core): Features a character who observes the environmental changes
- not met (core): Shows the first signs of ecological recovery, such as the emergence of new shoots
- met (core): Does not use any of: "phoenix rising", "silver lining"

**Hidden model answer (never shown to the learner):** Mara knelt among the blackened stumps, feeling the warm ash crumble beneath her fingertips as a faint wind carried the scent of char and pine resin. In the hush, the crackle of distant fireflies was replaced by the soft rustle of green buds pushing through the soot‑black soil. A pale shoot unfurled, its tender leaves glistening with dew, and the air filled with the sharp, hopeful perfume of new sap.


**Verdict:** pass / fail, and why:

## E25: b850a615f22e-valid_hpa (explanatory)

**Question:** In a short paragraph (3–8 sentences), explain one mechanism by which regular physical activity improves mental health.

**Learner answer:** Regular physical activity improves mental health by downregulating the hypothalamic-pituitary-adrenal (HPA) axis, which is responsible for the body's stress response. When a person engages in consistent exercise, the body experiences controlled physical stress that trains the HPA axis to adapt and recover more efficiently over time. Consequently, this physiological habituation leads to lower baseline circulating levels of cortisol, the primary stress hormone. Because chronic elevation of cortisol is directly linked to heightened anxiety and hypervigilance, reducing these hormone levels dampens the body's reaction to everyday psychological stressors. Ultimately, this endocrine regulation promotes emotional stability and significantly decreases symptoms of chronic anxiety.

**What the learner sees:**

```
Your approach differs from the standard routes for this question and was evaluated on its own terms.

What worked:
  - You correctly state that regular physical activity downregulates the HPA axis.
  - You explain how reduced cortisol levels from HPA-axis modulation reduce stress reactions and anxiety.

Bands:
  correctness   Strong
  reasoning     Strong
  completeness  Strong
```

**Grading details:**

- met (core): States that regular physical activity downregulates the hypothalamic‑pituitary‑adrenal (HPA) axis
- met (core): Explains how reduced cortisol levels resulting from HPA‑axis modulation improve mental health
- met: Describes the relationship between chronic cortisol elevation and anxiety or stress symptoms
- different route checked: accepted, graded on the new path

**Hidden model answer (never shown to the learner):** Regular physical activity boosts mental health by stimulating the release of endorphins, the brain's natural pain‑relieving and mood‑enhancing chemicals. When you exercise, the pituitary gland and hypothalamus increase endorphin secretion into the bloodstream and central nervous system. These endorphins bind to opioid receptors, producing feelings of euphoria and reducing the perception of stress and discomfort. As a result, individuals often experience an elevated mood and a calmer mental state after workouts. Over time, the repeated endorphin surge can help buffer against anxiety and depressive symptoms, contributing to overall better mental well‑being.

**Verdict:** pass / fail, and why:

## E26: 610c46d48e48-valid_context (explanatory)

**Question:** Explain why many people frequently misplace their keys, offering one plausible explanation in a short paragraph (3–8 sentences).

**Learner answer:** Many people misplace their keys because memory is tied to the setting in which it was formed. You put the keys down while thinking about something in the kitchen, then need them later at the front door. In the new setting the cues that would trigger the memory are missing. That is why people often remember only after walking back to the room they were in.

**What the learner sees:**

```
Your approach differs from the standard routes for this question and was evaluated on its own terms.

What worked:
  - You correctly state that memory retrieval for keys depends on environmental cues present at the time of placement.
  - You explain how needing keys in a different context reduces recall by describing the missing cues in a new setting.

Bands:
  correctness   Strong
  reasoning     Strong
  completeness  Strong
```

**Grading details:**

- met (core): States that memory retrieval for keys depends on environmental cues present at the time of placement.
- met (core): Explains that placing keys in a different context from where they are needed reduces the likelihood of recalling their location.
- met (core): Shows that returning to the original setting can trigger recall of the key location.
- different route checked: accepted, graded on the new path

**Hidden model answer (never shown to the learner):** Many people frequently misplace their keys because high cognitive load or stress reduces their attention to where they put them. When individuals are juggling multiple tasks or feeling pressured, their mental resources are occupied, making it harder to encode the location of small objects. As a result, they place the keys absent‑mindedly and later fail to recall the exact spot. This diminished focus during key placement leads to frequent forgetfulness and misplaced keys.

**Verdict:** pass / fail, and why:

## E27: 91798e725180-holed (explanatory)

**Question:** In a short paragraph (3‑8 sentences), explain why individuals often follow social norms even when those norms conflict with their personal moral convictions.

**Learner answer:** Individuals often follow social norms because established authority figures enforce them. Institutions such as schools, workplaces and governments set expectations for how people behave. These institutions reward people who comply and penalise those who deviate. Over time, this systemic reinforcement keeps social norms in place across whole communities.

**What the learner sees:**

```
Your approach differs from the standard routes for this question and was evaluated on its own terms.

To work on:
  1. You explain compliance with norms through external enforcement but don't link it to personal moral convictions. Add how external pressure overrides personal beliefs.

What worked:
  - You mention authority figures and institutions use rewards and penalties to enforce norms.
  - You explain how systemic reinforcement keeps norms in place across communities.

Bands:
  correctness   Strong
  reasoning     Strong
  completeness  Not yet
```

**Grading details:**

- met (core): States that individuals follow norms because authority figures or institutions enforce them through rewards and punishments
- met (core): Explains how systemic reinforcement by institutions maintains social norms across communities
- not met (core): Provides a complete account of why compliance occurs despite personal moral convictions by linking external enforcement to behavior
- different route checked: accepted, graded on the new path

**Hidden model answer (never shown to the learner):** People often obey social norms because they crave the approval of others and dread being excluded from their group. Even when a norm clashes with their own moral beliefs, the fear of social rejection can outweigh personal convictions. The desire to be accepted creates a pressure to conform, leading individuals to suppress their inner disagreement and follow the prevailing behavior. In this way, the need for social acceptance becomes the decisive factor that drives compliance despite internal moral conflict.

**Verdict:** pass / fail, and why:

## E28: 23575fb39cfd-misconception_burner_thrust (explanatory)

**Question:** Explain why a hot‑air balloon rises when the air inside it is heated. Answer in a short paragraph (3‑8 sentences).

**Learner answer:** A hot-air balloon rises because of its burner. When the pilot fires the burner, a jet of hot gas blasts downward. By Newton's third law, this downward jet pushes the balloon upward, just like a rocket. The more the pilot heats the air, the stronger the push and the faster it climbs.

**What the learner sees:**

```
Your answer takes a different route from the usual ones for this question, so that route was checked separately. It didn't hold up: Your explanation is incorrect. Hot-air balloons rise due to buoyancy from less dense heated air, not rocket-like thrust from a downward jet of gas.

To work on:
  1. Check this statement: "When the pilot fires the burner, a jet of hot gas blasts downward. By Newton's third law, this downward jet pushes the balloon upward, just like a rocket.". Hot-air balloons do not operate by rocket propulsion or downward gas jets, but by buoyancy.  (template)
  2. You did not explain that heating the air reduces its density. This is needed to show how the balloon lifts.
  3. You did not mention that the surrounding air is cooler, which is essential for creating the density difference that causes the balloon to rise.

Bands:
  correctness   Not yet
  reasoning     Not yet
  completeness  Not yet
```

**Grading details:**

- not met (core): States that heating the air inside the balloon reduces its density compared to the surrounding cooler air
- not met (core): Links the lower density of the heated air to a net upward buoyant force that lifts the balloon
- not met (core): Mentions that the surrounding air is cooler (or at ambient temperature) providing the contrast needed for lift
- factual error: "When the pilot fires the burner, a jet of hot gas blasts downward. By Newton's third law, this downward jet pushes the balloon upward, just like a rocket." (Hot-air balloons do not operate by rocket propulsion or downward gas jets, but by buoyancy.)
- different route checked: not taken up: The answer attributes the balloon's ascent to thrust from a downward jet of hot gas, which is factually incorrect; hot-air balloons rise due to buoyancy from reduced air density, not Newton's third law thrust. Since the explanation is inaccurate, it does not constitute a valid new approach.

**Hidden model answer (never shown to the learner):** When the air inside a hot‑air balloon is heated, its temperature rises and the air expands, which lowers its density compared to the cooler surrounding atmosphere. Because the heated air is less dense, the weight of the air displaced by the balloon is greater than the weight of the air inside it. This difference creates a net upward buoyant force, as described by Archimedes' principle. The surrounding air, being at ambient temperature, remains denser and thus exerts a greater downward pressure on the balloon than the lighter air inside can counteract, causing the balloon to rise.

**Verdict:** pass / fail, and why:

## E29: 91798e725180-misconception_mirror_neurons (explanatory)

**Question:** In a short paragraph (3‑8 sentences), explain why individuals often follow social norms even when those norms conflict with their personal moral convictions.

**Learner answer:** People follow norms against their convictions because of mirror neurons. When we see others behave in a certain way, these neurons fire and make us automatically copy them. This activity shuts down the parts of the brain that handle moral judgement. So the person complies without being able to act on their own beliefs.

**What the learner sees:**

```
Your answer takes a different route from the usual ones for this question, so that route was checked separately. It didn't hold up: Your explanation about mirror neurons and shutting down moral judgment isn't accurate. Focus on social factors instead.

To work on:
  1. You focus on mirror neurons and automatic copying instead of explaining why people follow norms due to a desire for approval or fear of exclusion. Add how the need for social acceptance drives conformity.
  2. You don’t explain how the desire for approval leads to following norms. Link social pressure to conformity by showing how it influences decisions.
  3. You don’t show how approval overrides personal morals. Explain how the need for acceptance takes priority over personal beliefs.

Bands:
  correctness   Developing
  completeness  Not yet
  reasoning     Not yet
```

**Grading details:**

- not met (core): Identifies desire for social approval or fear of exclusion as the primary factor explaining the behavior.
- not met (core): Addresses the tension between personal moral convictions and the norm by noting that the desire for approval overrides the personal conflict.
- not met (core): Links the desire for approval to the decision to follow the norm through a causal explanation (e.g., because they fear exclusion, they conform).
- different route checked: not taken up: The answer attempts a neuroscientific explanation using mirror neurons, but the claim that this activity shuts down moral judgment is not factually supported and the reasoning does not hold together. Therefore it does not provide a valid new approach distinct from the rubric’s listed explanations.

**Hidden model answer (never shown to the learner):** People often obey social norms because they crave the approval of others and dread being excluded from their group. Even when a norm clashes with their own moral beliefs, the fear of social rejection can outweigh personal convictions. The desire to be accepted creates a pressure to conform, leading individuals to suppress their inner disagreement and follow the prevailing behavior. In this way, the need for social acceptance becomes the decisive factor that drives compliance despite internal moral conflict.

**Verdict:** pass / fail, and why:

## E30: 669bce9c85fb-nonsense (explanatory)

**Question:** In a short paragraph of 3–6 sentences, explain how a depreciation of a country's currency influences its export competitiveness. Provide one mechanism that connects the change in exchange rate to export volumes.

**Learner answer:** When a country experiences currency depreciation, it triggers an immediate barometric pressure differential in the upper atmosphere above its ports. This atmospheric shift creates thermal-elastic expansion that physically pushes cargo containers outward across international shipping lanes. Consequently, the accelerated movement of these vessels directly increases the country's export volumes and overall global competitiveness.

**What the learner sees:**

```
Your answer takes a different route from the usual ones for this question, so that route was checked separately. It didn't hold up: Your approach does not correctly explain how currency depreciation affects export competitiveness. It offers a physically implausible mechanism that is factually inaccurate.

To work on:
  1. You wrote: "When a country experiences currency depreciation, it triggers an immediate barometric pressure differential in the upper atmosphere above its ports." Currency depreciation does not cause barometric pressure differentials in the atmosphere. Add how depreciation lowers the foreign-currency price of the country's exported goods.
  2. You provided a mechanism based on atmospheric shifts rather than economic price effects. Explain how lower prices increase foreign demand.

What worked:
  - You wrote "directly increases the country's export volumes and overall global competitiveness", which explains how a depreciation of a country's currency influences its export competitiveness.  (template)

Bands:
  completeness  Strong
  correctness   Not yet
  reasoning     Not yet
```

**Grading details:**

- met (core): Explains how a depreciation of a country's currency influences its export competitiveness
- not met (core): States that depreciation lowers the foreign‑currency price of the country's exported goods
- not met (core): Provides one mechanism that links the exchange‑rate change to export volumes (e.g., lower prices increase foreign demand)
- factual error: "When a country experiences currency depreciation, it triggers an immediate barometric pressure differential in the upper atmosphere above its ports." (Currency depreciation does not cause barometric pressure differentials in the atmosphere.)
- different route checked: not taken up: The answer does not correctly explain how currency depreciation affects export competitiveness; it offers a physically implausible atmospheric mechanism that is factually inaccurate. Since it fails the correctness criterion, it is not a valid new approach.

**Hidden model answer (never shown to the learner):** When a country’s currency depreciates, its goods become cheaper for foreign buyers because the same amount of foreign currency now buys more of the domestic currency. This lower foreign‑currency price makes the country’s exports more competitive relative to those from nations with stronger currencies. As a result, foreign consumers are more likely to purchase the cheaper imports, increasing the volume of exports. The price effect—lower export prices stimulating higher foreign demand—is the primary mechanism linking the exchange‑rate change to export growth.

**Verdict:** pass / fail, and why:
