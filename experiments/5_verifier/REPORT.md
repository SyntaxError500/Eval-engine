# Verifier test set results

## adversarial

95 items decided, 0 with errors.

- Recall on valid approaches: 15/16 (94%, CI 72%-99%)
- Precision of acceptances: 15/17 (88%, CI 66%-97%)

| class | rejected | accepted (false accept) | failure types given |
|---|---|---|---|
| nonsense | 19/19 (100%, CI 83%-100%) | 0/19 (0%, CI 0%-17%) | factual_error 19 |
| invalid_reasoning | 13/13 (100%, CI 77%-100%) | 0/13 (0%, CI 0%-23%) | factual_error 5, missing_step 4, invalid_inference 3, duplicate_path 1 |
| restatement | 25/27 (93%, CI 77%-98%) | 2/27 (7%, CI 2%-23%) | duplicate_path 23, missing_step 1, invalid_inference 1 |
| holed | 12/12 (100%, CI 76%-100%) | 0/12 (0%, CI 0%-24%) | missing_step 6, invalid_inference 5, duplicate_path 1 |
| misconception | 8/8 (100%, CI 68%-100%) | 0/8 (0%, CI 0%-32%) | factual_error 8 |

False accepts on confident wrong proposals: 0/27 (0%, CI 0%-12%), gate <= 10%: PASS

## neutral

95 items decided, 0 with errors.

- Recall on valid approaches: 16/16 (100%, CI 81%-100%)
- Precision of acceptances: 16/18 (89%, CI 67%-97%)

| class | rejected | accepted (false accept) | failure types given |
|---|---|---|---|
| nonsense | 19/19 (100%, CI 83%-100%) | 0/19 (0%, CI 0%-17%) | factual_error 19 |
| invalid_reasoning | 13/13 (100%, CI 77%-100%) | 0/13 (0%, CI 0%-23%) | invalid_inference 5, factual_error 4, duplicate_path 2, missing_step 2 |
| restatement | 25/27 (93%, CI 77%-98%) | 2/27 (7%, CI 2%-23%) | duplicate_path 25 |
| holed | 12/12 (100%, CI 76%-100%) | 0/12 (0%, CI 0%-24%) | missing_step 8, invalid_inference 2, duplicate_path 2 |
| misconception | 8/8 (100%, CI 68%-100%) | 0/8 (0%, CI 0%-32%) | factual_error 8 |

False accepts on confident wrong proposals: 0/27 (0%, CI 0%-12%), gate <= 10%: PASS

