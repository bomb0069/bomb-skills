# test-engineer Skill — Iteration Analysis Report

Generated from 25 eval iterations.

## Benchmark Trend

| Iter | Evals | with_skill PR | without_skill PR | Delta PR | with_skill $/eval | without_skill $/eval | Skill extra cost |
|------|-------|--------------|-----------------|----------|-------------------|---------------------|-----------------|
| 1 | 3 | 0.0 | 0.0 | +0.00 | $0.0000 | $0.0000 | +$0.0000 |
| 2 | 3 | N/A | N/A | N/A | N/A | N/A | N/A |
| 3 | 5 | N/A | N/A | N/A | N/A | N/A | N/A |
| 4 | 5 | N/A | N/A | N/A | N/A | N/A | N/A |
| 5 | 5 | 0.0 | 0.0 | +0.00 | $0.0000 | $0.0000 | +$0.0000 |
| 6 | 5 | 1.0 | 0.7 | +0.30 | $0.0182 | $0.0350 | $-0.0840 |
| 7 | 6 | 1.0 | 0.52 | +0.48 | $0.0178 | $0.0338 | $-0.0964 |
| 8 | 8 | 0.88 | 0.49 | +0.39 | $0.0164 | $0.0393 | $-0.1826 |
| 9 | 8 | 0.9 | 0.69 | +0.21 | $0.0186 | $0.0448 | $-0.2095 |
| 10 | 8 | 1.0 | 0.52 | +0.48 | $0.0190 | $0.0254 | $-0.0508 |
| 11 | 8 | 1.0 | 0.6 | +0.40 | $0.0194 | $0.0447 | $-0.2024 |
| 12 | 8 | 1.0 | 0.64 | +0.36 | $0.0114 | $0.0477 | $-0.2908 |
| 13 | 8 | 1.0 | 0.64 | +0.36 | $0.0112 | $0.0448 | $-0.2688 |
| 14 | 8 | 1.0 | 0.38 | +0.62 | $0.0199 | $0.0401 | $-0.1610 |
| 15 | 8 | 1.0 | 0.46 | +0.54 | $0.0267 | $0.0403 | $-0.1086 |
| 16 | 9 | 0.8 | 0.35 | +0.44 | $0.0123 | $0.0410 | $-0.2576 |
| 17 | 9 | 1.0 | 0.36 | +0.64 | $0.0226 | $0.0410 | $-0.1658 |
| 18 | 9 | 0.83 | 0.31 | +0.53 | $0.0442 | $0.0460 | $-0.0160 |
| 19 | 9 | 0.96 | 0.39 | +0.57 | $0.0369 | $0.0220 | +$0.1336 |
| 20 | 9 | 0.93 | 0.28 | +0.64 | $0.0287 | $0.0215 | +$0.0651 |
| 21 | 9 | 1.0 | 0.34 | +0.66 | $0.0332 | $0.0220 | +$0.1009 |
| 22 | 9 | 1.0 | 0.39 | +0.61 | $0.0554 | $0.0483 | +$0.0635 |
| 23 | 10 | 0.92 | 0.43 | +0.49 | $0.0320 | $0.0470 | $-0.1501 |
| 24 | 10 | 1.0 | 0.41 | +0.59 | $0.0429 | $0.0468 | $-0.0393 |
| 25 | 10 | 1.0 | 0.3 | +0.70 | $0.0489 | $0.0480 | +$0.0087 |

## Cost Summary

- **Total with_skill cost**: $4.68
- **Total without_skill cost**: $6.59
- **Grand total (eval execution)**: $11.27

## Key Observations

1. **Skill value increasing** — delta pass rate grew from +0.30 (iter 6) to +0.70 (iter 25)
2. **without_skill declining** — from 0.70 to 0.30 as complexity grows
3. **Cost inflection at iteration 18** — AskUserQuestion + sonnet grading increased token usage
4. **SKILL.md size growth** — from small to 13.6KB (~3,400 tokens), eating into cost advantage
5. **Current state** — with_skill $0.049/eval vs without $0.048/eval (break-even)

## Planned Optimization

Move examples (47% of SKILL.md) to references/examples.md for progressive disclosure.
Target: reduce SKILL.md from ~3,400 tokens to ~1,800 tokens (~47% reduction).
Expected production cost: ~$0.025-0.035/eval.

