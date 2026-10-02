---
name: every-hed-dek
description: Draft, compare, and refine Every-style headline and dek pairs for an article, then process the writer's subsequent selection and update the skill's learned preferences. Use when a user asks for heds, headlines, subheads, or deks for an article, or replies with the pair they chose from a prior slate. Do not use for section headings or title brainstorming unrelated to editorial packaging.
---

# Every Hed + Dek

Create a small, varied slate of headline/dek pairs that accurately package the article, then learn from the pair the writer ultimately uses.

## Route the request

- **Draft mode:** The user wants options, evaluation, or refinement. Follow “Draft pairs.”
- **Learn mode:** The user identifies a chosen pair or supplies final edited copy from a prior slate. Follow “Learn from the choice.”
- If both apply, learn from the prior choice first, then use the updated preferences for the new slate.

## Required context

Work from the article draft when available. An outline, detailed pitch, or substantive notes can work, but do not invent a claim, result, framework, test, or degree of certainty that the source does not support. If there is not enough material to identify the central idea and payoff, ask for the draft or outline before generating options.

## Draft pairs

1. Read [references/every-house-style.md](references/every-house-style.md).
2. Read [references/learned-preferences.json](references/learned-preferences.json). Apply active preferences and use provisional signals only as hypotheses or tiebreakers.
3. Extract a compact packaging brief:
   - article type and intended reader;
   - one-sentence thesis;
   - distinctive concept, result, or transformation;
   - evidence or method that earns the thesis;
   - stakes and reader payoff;
   - required names, products, numbers, and terms;
   - tempting claims the article does not support.
4. Choose several interest engines that genuinely fit the article. Useful families include a direct claim, reversal, coined concept, confession or personal result, specific outcome, utility promise, verdict with qualification, and narrative frame.
5. Draft broadly, then present the strongest **five** pairs unless the user asks for a different number. The five must represent meaningfully different editorial strategies, not cosmetic rewrites.

For each numbered option, show:

- **Hed:** the headline
- **Dek:** the dek
- one short sentence naming its editorial strategy or tradeoff

Recommend one option with a concise reason. Do not imply that the recommendation is objectively correct.

End with this request, adapted only when necessary:

> Which hed/dek pair did you choose? Reply with the option number, or paste the final pair if you edited it. I’ll use your choice to improve the skill.

This request is part of the completion contract. Do not replace it with “let me know what you think.” Draft mode is not complete until the options are paired, varied, grounded in the article, and the question is asked.

## Learn from the choice

The user's request to build this feedback loop supplies standing authorization to update this skill's own learning files after an unambiguous selection. It does not authorize changes to unrelated files or skills.

1. Resolve the exact final hed and dek from the conversation. Prefer pasted final copy over a numbered option. If the pair or article is genuinely ambiguous, ask one concise clarification before writing. Store uncertain chooser metadata as `unknown`; do not interrupt solely to identify the chooser.
2. Read [references/learning-protocol.md](references/learning-protocol.md) and [references/learned-preferences.json](references/learned-preferences.json).
3. Compare the final pair with the article's packaging brief, the other options, any user edits, existing signals, and contrary evidence.
4. Extract only observable contrasts and appropriately scoped inferences. Do not invent the user's reason from a bare option number.
5. Record the decision with `scripts/record_selection.py` using the file-based procedure in the learning protocol. Revisions for the same article use the same decision ID so the history preserves them as one decision lineage.
6. Reconcile [references/learned-preferences.json](references/learned-preferences.json): add or update relevant provisional signals, active preferences, and counterevidence. Use `apply_patch`; keep it compact and valid JSON.
7. Run `python3 scripts/validate_learning_store.py`. If it fails because of the update, repair the store before finishing. Run the host skill validator too when it is available.
8. Tell the user briefly what pair was recorded, what was learned, and whether each learning is provisional or active.

Learn mode is not complete until the exact final pair is recorded, preferences are reconciled, validation passes, and the user is told what changed.

## Mutable state ownership

The directory containing this `SKILL.md` is the canonical copy of the skill and its learning state. Do not maintain a second writable copy. If this skill is installed from another location, use a symlink to this canonical directory or explicitly make the installed directory canonical before collecting choices. Do not overwrite `selection-history.jsonl` or `learned-preferences.json` during upgrades.

## Editorial invariants

- Judge the hed and dek as a pair. The hed creates the central charge; the dek adds mechanism, evidence, scope, stakes, or qualification.
- The dek must not restate the hed.
- The pair must stand on its own before the article has taught the reader its concepts. Do not rely on unexplained internal frameworks, scales, levels, coined terms, or shorthand; translate them into plain-language meaning or create curiosity without requiring prior knowledge.
- The opening and article body must begin paying off the pair promptly.
- Prefer bounded curiosity over mystery-box clickbait: reveal the compelling answer while withholding the reasoning or implications.
- Reject any option that is more certain, sweeping, or sensational than the article.
- Keep first person only when the writer's experience is material evidence.
- Preserve official capitalization of people, companies, products, and models.
- Apply the case and punctuation conventions in the house-style reference.
- Favor concrete nouns, verbs, outcomes, and tradeoffs over generic AI futurism or corporate language.

## Google Doc presentation

When placing a selected pair into an article's Google Doc, put the hed in bold on its own paragraph and the dek in italics on the next paragraph. Follow the dek with one blank paragraph before the article body. Preserve the article body and any unrelated formatting.

## Output quality

Internally score candidates for fidelity, one-big-idea strength, specificity, interest, hed/dek complementarity, voice, freshness, and format fit. Fidelity is a gate: discard an attractive option if the article does not earn it.

Do not expose a large scoring table unless the user asks. The normal output should feel like an editor's considered slate, not a model evaluation report.
