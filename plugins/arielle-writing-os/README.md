# Arielle Writing OS

Private writing plugin for Arielle Shipper.

This adapts the Compound Writing model into a personal Every writing system:

- The plugin supplies reusable skills, review lenses, and workspace templates.
- The agent supplies reasoning, drafting, editing, and file operations.
- The writing project supplies Arielle's actual source material and durable memory.

## What It Is For

- operational Slack updates, emails, briefs, policies, handoffs, and decision memos
- Every-style article development from ops work and internal experiments
- draft review through focused editorial lenses
- visible learning through approved updates to workspace files

## Workspace Model

Use these files in a writing project when they exist:

```text
writing-project/
|-- voice.md
|-- context.md
|-- style-guides/
|   |-- ops.md
|   `-- article.md
`-- strategy/
    `-- contributor-positioning.md
```

Durable files should change only after Arielle approves the wording. `context.md` can hold current work and provisional observations.

## First Version

The first version intentionally starts small:

- `arielle-writing-os`: router and workspace contract
- `ops-writing`: operational writing in Arielle's voice
- `every-article-development`: article shaping for Every
- `every-editor`: Every-style editorial review
- `writing-review-lenses`: focused draft pressure
- `save-writing-learning`: approval-based memory

The plugin is private by design. Do not move internal Slack, Notion, draft, or strategy material into a public repo.
