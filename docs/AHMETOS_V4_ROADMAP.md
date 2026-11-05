# AhmetOS v4 — Pixel Arcade Developer World

This branch is an incremental redesign of the GitHub profile. Keep `main` stable until the v4 release is reviewed.

## Design direction

- Retain the colorful Neon Arcade interface and genuine repository links.
- Introduce **Byte**, a friendly animated pixel-art robot, as the profile mascot.
- Use self-contained SVG and GitHub-compatible Markdown. No JavaScript is executed in GitHub READMEs.
- Respect `prefers-reduced-motion` in any animated SVG.
- Never invent GitHub activity counts, project milestones, skills, or achievements.

## Development phases

- [x] **Phase 1: Identity.** Introduce Byte and retitle the animated terminal as AhmetOS v4.
- [x] **Phase 2: Skill Tree + Developer Journey.** Add a colorful animated skills network and a career checkpoint map, based on actual experience.
- [ ] **Phase 3: Live project signals.** Add a permission-limited GitHub Actions workflow that regenerates a data panel from public GitHub commits. Check the default branch, API rate limits, permissions, missing data and failed jobs; show the date of last successful refresh. Do not include private repositories.
- [ ] **Phase 4: Easter eggs + release polish.** Add GitHub-safe expandable terminal surprises and achievements; validate color contrast, desktop/mobile views, broken links, reduced-motion experience, and readability.

## Current implementation

- `assets/ahmetos-v4/hero.svg`: v4 animated terminal masthead.
- `assets/ahmetos-v4/byte-mascot.svg`: original self-contained pixel-art mascot, with wave, blink, bob, and twinkling background.
- `README.md`: introduces Byte while keeping six project cards, contact buttons, existing neon marquee, architecture, and contribution snake.

- `assets/ahmetos-v4/skill-tree.svg`: original animated four-branch skill tree describing documented technologies, without proficiency claims.
- `assets/ahmetos-v4/developer-journey.svg`: original animated five-checkpoint career quest map with selected real experiences, not a dated chronology.
- `README.md`: now includes both visuals and renumbers the sections to preserve reading order.

## Release checks

1. Render the GitHub README preview and verify all new SVGs load.
2. Open the profile in GitHub light and dark modes; check a narrow mobile viewport.
3. Confirm social links and all project links are correct.
4. Verify motion works where GitHub allows it, but the static state remains understandable.
5. Merge only after reviewing the complete v4 changes.
