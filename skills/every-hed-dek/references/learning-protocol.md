# Selection learning protocol

Use this only after the writer identifies the pair they chose or supplies final edited copy.

## Goal

Turn a concrete editorial decision into useful future context without mistaking one context-bound choice for a permanent preference.

The learning must change future decisions. “The user chose option 3” is a history record, not yet a useful rule.

## Evidence hierarchy

From strongest to weakest:

1. **Explicit general preference:** The user states a reusable rule or explains why they chose or edited something.
2. **Repeated revealed preference:** The same meaningful choice recurs across distinct articles and competing option families.
3. **Substantive edit:** The writer changes wording, specificity, framing, punctuation, point of view, or the division of labor between hed and dek.
4. **Single selection:** The writer selects one unedited option from a slate.
5. **Non-selection:** An option was not chosen. This is weak evidence because only one option can win.

Never infer a dislike merely because another option lost. Never invent a reason from a bare option number.

## Extracting learnings

Compare the final pair with the alternatives along dimensions that were actually different:

- directness versus conceptual intrigue;
- claim versus question;
- personal versus impersonal framing;
- specific nouns/numbers versus broad framing;
- utility versus narrative;
- boldness versus qualification;
- brevity versus explanatory detail;
- coined phrase versus familiar language;
- where the hed stops and the dek begins;
- punctuation and cadence;
- topical/product name frontloading;
- emphasis on outcome, method, stakes, or reader benefit.

A valid learning names the observed decision, relevant contrast, and scope. Example: “For first-person reported experiments, Arielle selected the version that put the surprising failure in the hed and reserved explanation for the dek; provisional until repeated.”

An invalid learning removes context or invents causality. Example: “Arielle always prefers negative headlines.”

Separate accuracy-driven edits from style preferences. Record format-specific signals first and generalize across formats only when the evidence crosses formats.

## Confidence and activation

- **Active:** An explicit general preference, or a pattern supported by at least three consistent decisions across independent articles with no meaningful contradiction.
- **Strong provisional:** Two consistent decisions across independent articles, or one decision plus a diagnostic substantive edit.
- **Provisional:** One choice or edit with a plausible contrast.
- **Retired/contradicted:** Later evidence shows the signal was contextual, inconsistent, or wrong.

Do not turn a provisional signal into a hard generation rule. Use it as a tiebreaker or ensure the next slate contains an option that tests it.

Revisions for the same article are one decision lineage, not independent votes. If a user chooses an edited hybrid, store the final pasted pair. Distinguish the chooser as user, editor, team, or unknown when that information is available; a team choice is not automatically the user's personal taste.

## Storage

- `selection-history.jsonl` is the canonical evidence log. Each line holds one decision lineage with all of its revisions. The recording script appends a revision under the same decision ID rather than double-counting it as an independent choice.
- `learned-preferences.json` is the compact, always-read interpretation of that evidence. Its three buckets are `active`, `provisional`, and `retired`.
- Store the packaging brief and decision metadata, not the full article text.

When reconciling `learned-preferences.json`:

1. Add or update only relevant signals.
2. Promote a signal to active only at the threshold above.
3. Preserve counterevidence and narrow, downgrade, or retire a signal when warranted.
4. Consolidate duplicate signals instead of accumulating paraphrases.
5. Keep the file compact and decision-relevant.

Routine selections update learning files, not `SKILL.md` or the house-style reference. Stable workflow or house-style changes should be rare and based on an explicit user correction or broader evidence.

### Recording mechanics

Create a uniquely named temporary JSON payload with `apply_patch`; do not interpolate user text into a shell command. Run `python3 scripts/record_selection.py --record-file /absolute/path/to/payload.json`, then delete only that temporary payload after the record succeeds. Required fields are:

- `decision_id`: stable identifier for this article decision lineage;
- `article_identifier`: title, slug, or concise identifier;
- `format`: column or article type;
- `thesis`: one-sentence packaging brief, not the full article;
- `chosen_hed` and `chosen_dek`;
- `chooser`: `user`, `editor`, `team`, or `unknown`;
- `observable_contrasts`: list of factual differences from the slate;
- `learning_evidence`: a list of objects, each containing:
  - `preference_id`: stable lowercase hyphenated identifier reused when the same signal recurs;
  - `signal`: carefully scoped inference;
  - `scope`: article format or the narrowest justified scope;
  - `basis`: `choice`, `edit`, or `explicit`;
  - `kind`: `style`, `accuracy`, or `format`.

Optional string fields are `source_option`, `material_edits`, and `user_reason`. Use an empty string when unknown. The script validates fields and atomically adds a new decision lineage or a revision to an existing lineage.

Each entry in `learned-preferences.json` must contain `id`, `signal`, `scope`, `basis`, `evidence_decision_ids`, `counterevidence_decision_ids`, and `last_updated`. The ID must match `preference_id` in the **latest revision** of each cited decision; superseded revisions do not support promotion. The validator rejects unknown decision IDs, missing evidence links, duplicate IDs, and inferred active preferences supported by fewer than three distinct articles. The recorder also rejects a second decision ID for the same normalized format and article identifier.

## User-facing acknowledgement

State the final pair recorded, one to three supported learnings, each learning's status, and that the skill's learning files were updated. Do not require the user to explain the choice before saving it.
