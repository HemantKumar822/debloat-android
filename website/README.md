# Website

Static HTML, CSS and JavaScript in `dist/`. No framework or build dependency.

Preview from the repository root:

```bash
python -m http.server 4173 --bind 127.0.0.1 --directory website/dist
```

The download is a curated release from `scripts/package_skill.py`, not a copy of the repository. Regenerate after runtime or skill changes using a new output path, then replace the previous release deliberately. Never include real-device reports.

`.openai/hosting.json` identifies the private Sites preview. The Sites publication helper runs from an ignored `.tools/site-publish` copy so its managed Git repository does not become a nested repository in the main project.
