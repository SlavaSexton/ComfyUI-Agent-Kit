# Contributing

Read this before opening a pull request. It exists because PR #2 was 951 lines of good code that could not
be merged, and the author had no way to know that in advance. That was the repo's fault, not his.

## What this kit is

A knowledge layer for AI coding agents driving a local ComfyUI. The value is curated, verified, current
knowledge about models and nodes, plus a thin client and the wiring that registers a third-party MCP driver.

It is deliberately **not** a collection of tools. `shared/tools/` holds four scripts that maintain the kit
itself: sync the official template library, build the quick index, inventory node types, fetch a shared
workflow. That drawer is infrastructure, not general utilities.

**Everything under `shared/` is copied into the installed skill by `tools/build_plugin.py`.** Whatever you add
there installs on every user of the kit. That raises the bar: it has to be worth its weight to people who will
never use your specific workflow.

## What is welcome

- **A model or technique entry**, written to the Teaching standard (below). This is the most valuable thing
  you can send.
- **A correction.** If the kit states something false, say so with the source that proves it. Corrections are
  merged fast and the entry records that it was wrong, rather than quietly swapping the text.
- **A `docs/KNOWN_ISSUES.md` row** for a real, sourced ComfyUI bug, with a workaround and a URL.
- **A fix to the client, the installers or the gates**, with the failing case it addresses.

## What will not be merged, and why

- **Tooling for one specific pipeline.** Editing bridges, render farm glue, project scaffolders. Not because
  the code is bad, but because it ships to every user and serves few of them. Publish it as its own
  repository and open an issue asking for a pointer from `docs/TASKS.md`. That link is granted freely.
- **Anything unsourced.** A claim without a primary source cannot be verified, and the kit's whole premise is
  that its claims can be.
- **Vendored third-party code.** The installer fetches components from their own sources at install time and
  this repository stays licence-clear. Keep it that way.
- **Prose polish with no factual change.** The kit's voice is deliberate.

## The Teaching standard

The bar for any knowledge entry: **reading only your new entry plus `SKILL.md`, an agent must be able to build
a working ComfyUI graph and get a result.** A trigger word and a repo link is a failure.

That means, concretely:

- Real node class names, their inputs and outputs with types, and how they wire (output A into input B).
- The settings that matter, with the values the official template actually ships, not values you assume.
- The gotcha that breaks a hand-built copy. Every entry that has one must name it.
- **Every claim marked confirmed or inferred.** A confirmed claim names the file, template or command it came
  from. An inferred claim says so and says what would confirm it. Never invent a node, a filename or a setting.
- Read the primary source completely: the node code on master, the official template JSON including any
  MarkdownNote inside it, the full model card. Not a blog summary.

## House rules

- **No em dashes or en dashes anywhere.** Use a comma, a full stop, or a plain hyphen. This is checked.
- **Counts are gated.** If you change the number of recipe entries, run `python tools/check_counts.py`. It
  recomputes every headline number from the files and tells you which copies drifted.
- **Run `python tools/build_plugin.py`** so the bundle under `claude-code/` matches your source change. Its
  own gate checks that links and script paths resolve.
- **No `Co-Authored-By` or AI-assistant trailers** in commit messages.
- **No private paths.** Examples use invented placeholders (`E:\path\to\ComfyUI`, `D:/comfy/projects/my-short`),
  never a real path from your machine. A placeholder that looks like a placeholder is correct, not a defect.

## Licence

This repository is **Apache-2.0** as of v3.2.0. Releases up to and including v3.1.0 were MIT and that grant
stands for anyone who took them.

By opening a pull request you agree that your contribution is licensed under Apache-2.0. If you opened a PR
before the relicence, a comment saying you are fine with Apache-2.0 is enough.

## Before you open a PR

1. Say what problem it solves in the first two lines.
2. State what you actually ran. "It should work" is not a test result.
3. If you are adding an entry, name the primary source you read.

An issue first is welcome and usually faster, especially for anything large. It costs you nothing and it can
save you 951 lines.
