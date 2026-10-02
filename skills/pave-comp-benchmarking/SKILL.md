---
name: pave-comp-benchmarking
description: Use Pave Market Data to research compensation benchmarks for a role, location, company profile, level, percentile, and pay component. Apply when a user asks to benchmark a hire or compensation range in Pave.
---

# Pave Comp Benchmarking

Prefer Pave's MCP when it is available in the current agent environment and the user has authorized access. As of September 8, 2026, Pave's official MCP announcement describes an initial Claude integration and says support for additional MCP clients is coming; no Pave MCP is installed in Every's Codex environment. Until that changes, use Computer Use in Google Chrome because Pave's benchmark explorer is a visual, authenticated web application.

Pave also publishes a REST API, but its documented endpoints cover merit cycles, exchange rates, and merit-cycle employees rather than Market Data benchmarking. Do not substitute that API for this workflow unless Pave adds a supported benchmarking endpoint. No official Pave CLI has been identified.

## Inputs

Establish the decision the benchmark will support and collect only inputs that materially affect it:

- target role or a short description of the work;
- location or geographic tier;
- company-stage basis and range, such as capital raised or revenue;
- industry and ownership type;
- individual-contributor or manager track and target level, if known;
- requested percentile and pay components, such as base salary, target variable pay, total cash, or equity;
- desired output, such as a concise recommendation, a benchmark table, or values for a hiring document.

Treat demonstrated values as examples, not defaults. In the recording, the user explored Office Management in the New York City metro for a private software company with $10M-$20M raised. Ask a concise question when a missing input would materially change the benchmark. If the target level is unknown, return the relevant nearby levels and explain the distinction instead of silently choosing one.

## Workflow

1. Open `https://app.pave.com/benchmarkingsurvey/data-explorer` in Google Chrome. If authentication or access is required, ask the user to complete it; do not handle credentials.
2. In **Market Data**, search Pave's job catalog using the role title and, when useful, adjacent terms. Select the result whose job-family description best matches the actual responsibilities. Do not rely on title similarity alone.
3. Verify the selected job family, discipline, and track shown on the result page. If the match is ambiguous, present the best candidates and ask the user to choose.
4. Apply the requested comparison cohort using stable labeled controls rather than coordinates:
   - location selector;
   - **All Company Stages** and its stage basis/range;
   - industry selector;
   - **Private & Public companies** ownership selector;
   - any requested peer group, currency, employee-population, or cash/equity setting.
5. After each material filter change, wait for the benchmark table to refresh. Verify the visible filter labels or chips before reading values.
6. Use **Table view** and read the requested rows and percentile columns. Preserve Pave's level label, consistency indicator, currency, pay-component label, and data-refresh date when visible. Check additional sections such as **Annual bonus percent**, **Target variable pay**, **Target total cash**, or equity only when requested.
7. Report the exact observed benchmark values with the complete cohort definition. Clearly separate Pave observations from any recommendation or interpretation.

## Output Standard

Include:

- matched Pave job family and why it fits;
- location, stage/range, industry, ownership, currency, and other active filters;
- level, consistency indicator, requested percentile values, and pay component;
- the data-refresh date when visible;
- any ambiguity, sparse-data warning, or assumption that could change the result.

For a range recommendation, state the chosen anchor percentile and rationale. Do not imply that benchmark data alone determines an offer; flag internal leveling, budget, equity philosophy, and pay-transparency requirements as separate considerations when relevant.

Do not expose unrelated account, employee, candidate, or browser information visible during navigation. Treat Pave benchmark data as authorized workspace information and share only the values needed for the user's stated purpose.
