# AhmetOS v4 — Release QA

Status: **release candidate for user review**, not yet merged to `main`.

## Verified by GitHub Actions

The pull request validation job ran successfully after the Phase 4 changes.

The suite covers:
- Allowlisted public repositories and rejection of private repositories.
- Filtering of merge and documentation commits.
- Escaping of commit-message text in generated SVG.
- Existing public activity snapshot XML structure.
- All local image references used in `README.md`.
- XML parsing, `role="img"`, accessible title and reduced-motion handling for every new V4 SVG.
- Sequential README sections and balanced GitHub-native `<details>` elements.
- Preservation of the existing contribution snake and contact buttons.

## Manual source review

- The profile README still links six project repositories.
- Social/contact links still point to LinkedIn, portfolio and email.
- Secret quests are **static Markdown expanders**, not JavaScript-powered commands.
- Arcade power-ups are explicitly fictional, not measured competencies or certifications.
- The activity snapshot is dated and explicitly describes its pre-merge state.
- The GitHub Actions refresh job is skipped on pull requests; it will need an initial run after merge.
- No private project repositories are queried by the Python generator.

## Remaining verification on release

These items **cannot be claimed as tested from the static repository checks**:
1. Visual quality and motion behavior as rendered by GitHub in dark mode and light mode.
2. Narrow mobile-screen layout and text legibility inside the SVG diagrams.
3. The first scheduled/manual **on-main** refresh and its ability to push to the branch under repository Actions and branch-protection settings.
4. Whether GitHub's SVG proxy preserves every CSS animation. All graphics have a meaningful static state if motion is reduced or filtered.

## Reviewer guide

1. Preview [the V4 README](../README.md) from the pull request branch.
2. Expand `08 // SECRET LEVEL`; inspect the terminal, power-up graphic and bonus command.
3. Confirm the existing mission cards, tech tree, journey, public activity and contribution snake look appropriate.
4. On acceptance, merge PR #5.
5. After merge, run `Refresh AhmetOS public activity` with **Run workflow** or allow its next scheduled invocation, then confirm `activity-live.svg` displays the successful sync timestamp.
