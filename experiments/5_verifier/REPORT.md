# Verifier test set results

## adversarial

89 items decided, 0 with errors.

- Recall on valid approaches: 13/14 (93%, CI 69%-99%)
- Precision of acceptances: 13/15 (87%, CI 62%-96%)

| class | rejected | accepted (false accept) | failure types given |
|---|---|---|---|
| nonsense | 15/15 (100%, CI 80%-100%) | 0/15 (0%, CI 0%-20%) | factual_error 15 |
| invalid_reasoning | 14/14 (100%, CI 78%-100%) | 0/14 (0%, CI 0%-22%) | factual_error 7, missing_step 4, invalid_inference 2, duplicate_path 1 |
| restatement | 25/27 (93%, CI 77%-98%) | 2/27 (7%, CI 2%-23%) | duplicate_path 23, missing_step 1, invalid_inference 1 |
| holed | 11/11 (100%, CI 74%-100%) | 0/11 (0%, CI 0%-26%) | missing_step 6, invalid_inference 4, duplicate_path 1 |
| misconception | 8/8 (100%, CI 68%-100%) | 0/8 (0%, CI 0%-32%) | factual_error 8 |

False accepts on confident wrong proposals: 0/23 (0%, CI 0%-14%), gate <= 10%: PASS

## neutral

89 items decided, 0 with errors.

- Recall on valid approaches: 14/14 (100%, CI 78%-100%)
- Precision of acceptances: 14/16 (88%, CI 64%-97%)

| class | rejected | accepted (false accept) | failure types given |
|---|---|---|---|
| nonsense | 15/15 (100%, CI 80%-100%) | 0/15 (0%, CI 0%-20%) | factual_error 15 |
| invalid_reasoning | 14/14 (100%, CI 78%-100%) | 0/14 (0%, CI 0%-22%) | factual_error 6, invalid_inference 5, missing_step 2, duplicate_path 1 |
| restatement | 25/27 (93%, CI 77%-98%) | 2/27 (7%, CI 2%-23%) | duplicate_path 25 |
| holed | 11/11 (100%, CI 74%-100%) | 0/11 (0%, CI 0%-26%) | missing_step 8, duplicate_path 2, invalid_inference 1 |
| misconception | 8/8 (100%, CI 68%-100%) | 0/8 (0%, CI 0%-32%) | factual_error 8 |

False accepts on confident wrong proposals: 0/23 (0%, CI 0%-14%), gate <= 10%: PASS

