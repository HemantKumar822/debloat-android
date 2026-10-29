# Android Device Care v0.3 — implementation brief

2026-10-28. User direction: start building; premium minimal Firecrawl-inspired
landing page, no green, no phone illustration or report showcase. Markdown audit
reports and installation for Codex, Cursor, Claude Code and Antigravity.

## Design

White canvas, near-black type, fine pale borders, ember orange accents. Large
editorial sans-serif headings with compact monospace utility labels. One original
pixel spark mark; short staggered reveals and a quiet pixel field give it motion.
Preserve keyboard navigation and reduced-motion preferences. No fabricated
testimonials, adoption counts, performance improvements, or certification badges.

Build a static site under `website/dist` with HTML, CSS, and JavaScript. This
keeps deployment portable and allows the page to work without a framework. Native
CSS and Web Animations are sufficient for the restrained motion requested.

Sections: hero, three clear capabilities, short workflow, IDE-specific install
instructions, FAQ, open-source footer. Primary CTA: install the skill. Secondary:
read the docs. GitHub links use a real configured URL only; no remote exists yet.

## Implementation tasks

1. Replace HTML report generation with UTF-8 Markdown. Default outputs end in .md.
   Include summary, device snapshot, evidence, research notes, full inventory,
   unknown backup status, limitations and next steps. Escape untrusted Markdown.
   Keep exclusive writes and optional JSON. Update tests with failure-first checks.
2. Add a standard-library installer for project or user scopes. Use a curated
   portable bundle; exclude reports, website, Git state, caches and local tools.
   Support dry-run. Refuse existing targets and symlinked source/destination
   paths. Test installed invocation from a different current directory.
3. Build the landing page and keep motion independent from content visibility.
   Add accessible IDE tabs and copy feedback; downloads contain the real portable
   package. Documentation accurately labels documentation-checked support versus
   live IDE validation. No device access from the website.
4. Update README, onboarding, skill entrypoint, roadmap, CI and synthetic example.
5. Run Python suite, installed-bundle smoke tests, Markdown checks, website
   desktop/mobile/keyboard/reduced-motion checks, and independent final review.
6. Publish an owner-private Sites preview when supported. GitHub repository
   publication awaits a real owner/repository destination.

## Compatibility sources checked

All checked 2026-10-28. All platforms still require a local execution environment
with Python and ADB for real phones; skill discovery alone does not prove USB access.

| Host | Project directory | Personal directory | Source |
|---|---|---|---|
| Codex | `.agents/skills/android-device-care` | `~/.agents/skills/android-device-care` | [OpenAI](https://learn.chatgpt.com/docs/build-skills) |
| Cursor | `.cursor/skills/android-device-care` | `~/.cursor/skills/android-device-care` | [Cursor](https://cursor.com/docs/skills) |
| Claude Code | `.claude/skills/android-device-care` | `~/.claude/skills/android-device-care` | [Anthropic](https://code.claude.com/docs/en/skills) |
| Antigravity IDE | `.agents/skills/android-device-care` | `~/.gemini/config/skills/android-device-care` | [Google](https://antigravity.google/docs/skills?app=antigravity-ide) |

Antigravity CLI has a different personal directory; it is not included in the
IDE target. Cursor also recognizes `.agents/skills`. Avoid duplicate installations.
Use the common [Agent Skills format](https://agentskills.io/specification), with
one skill source and ordinary relative resource links; no host-specific runtime API.

## Design research

[Firecrawl](https://www.firecrawl.dev/) was inspected visually: sparse typography,
subtle grid structure and warm accents are the reference, not its assets or copy.
[UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) provides
pixel-style and accessibility guidance; the initial generic design-system search
was too documentation-oriented, so only its targeted pixel-style guidance is used.
[Frontend Design](https://github.com/anthropics/skills/tree/main/skills/frontend-design)
guides composition and restraint. No claim that any skill is objectively the best.

## Invariants

Read-only adapter and consent boundary remain. No live-phone scan is authorized
by development work. Name heuristics remain weak evidence. No package mutation,
backup verification, tracker detection, or universal compatibility claim is added.
