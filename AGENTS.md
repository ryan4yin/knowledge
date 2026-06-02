# Repository Guidelines

## Project Structure & Module Organization

This repository is a personal knowledge base organized by topic. Most content is Markdown under
top-level subject directories such as `pl/`, `telemetry/`, `network/`, `devops/`, `music/`, and
`electrical-engineering/`. Topic directories commonly include a `README.md` index plus article files
near related examples or assets. Store images in nearby `_img/`, `_imgs/`, or `image/` folders, and
keep runnable snippets or manifests beside the article that explains them, for example
`telemetry/metrics/prometheus/dockprom/`.

## Build, Test, and Development Commands

- `nix develop`: enter the development shell with `typos` and `prettier` available.
- `nix flake check`: run the configured pre-commit checks for spelling and formatting.
- `prettier --write "**/*.md"`: format Markdown using `.prettierrc.yaml`.
- `typos`: check spelling with repository exclusions from `.typos.toml`.

Prefer the Nix-provided tools so results match CI/local hook behavior. Do not introduce package
manager lockfiles or toolchains unless the repository already uses them for that area.

## Coding Style & Naming Conventions

Markdown is the primary format. Use clear headings, short paragraphs, fenced code blocks with
language identifiers, and relative links for local references. Prettier uses 100-character line
width, double quotes where relevant, no semicolons, trailing commas for supported syntaxes, and
always wraps prose. Existing filenames are often Chinese and may contain spaces; match the local
topic style rather than renaming unrelated files.

## Testing Guidelines

There is no application test suite. Validate documentation changes with `nix flake check` before
submitting. For YAML, Docker Compose, Kubernetes manifests, Python, Go, or shell examples, run the
smallest relevant validator or command when practical and mention anything not verified.

## Commit & Pull Request Guidelines

Recent history uses short Conventional Commit-style subjects such as `feat: postgresql` and
`feat: korean`. Keep commits focused, use lowercase types like `feat:`, `fix:`, or `docs:`, and name
the changed topic in the subject. Pull requests should summarize changed areas, explain why the
content moved or was added, link related issues when present, and include screenshots only for
visual or rendered documentation changes.

## Security & Configuration Tips

Never commit secrets, tokens, private keys, kubeconfigs, or personal credentials. Use placeholders
in examples and redact sensitive command output. For infrastructure notes, prefer plan/check
commands over apply/delete commands, and clearly label destructive operations as examples rather
than steps to run blindly.
