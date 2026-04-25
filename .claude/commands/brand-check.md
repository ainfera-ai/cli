Run the full brand-words grep battery from CLAUDE.md. Every query must return zero hits on actual content (meta-references inside CLAUDE.md and docs/BRAND-WORDS.md defining the regex itself are expected and don't count).

Categories to scan: DID method, retired revenue split, non-canonical SDK import, named third parties, stage / timeline / funding language, jurisdictional framing, founder identifiers, forbidden vocabulary.

Report each violation with file, line, and a suggested canonical replacement. Don't auto-fix — propose and wait for approval.

See docs/BRAND-WORDS.md for the canonical reference each query enforces.
