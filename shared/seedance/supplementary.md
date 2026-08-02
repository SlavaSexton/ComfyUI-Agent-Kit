# Seedance: supplementary (non-official) observations

**Subordinate layer.** Nothing here overrides `reference.md`. Where the two disagree, the official
source wins and the conflict is listed below. Use this file for leads and for context the official
docs do not cover, never as the basis for a rule.

Why it exists: Seedance 2.5 launched 2026-07-31 with no public prompting guide, so for a while the only
writing about it is third-party. That is worth reading and worth distrusting.

## Conflict ledger (official wins)

| Question | Official says | Third party says | Ruling |
|---|---|---|---|
| Reference label spacing | `@Image 1`, `@Video 1`, `@Audio 1` **with a space**, in the BytePlus guide's own worked example | Dreamina's 2.5 consumer page shows `@Image1` with no space; Pollo shows `@Image 1` with a space | **Use the spaced form.** Both appear in the wild and no parser rule is published, so do not normalise them into an invented universal syntax. If a platform's UI inserts the tag for you, accept whatever it inserts |
| Reference budget | 30 images + 10 video + 10 audio (ByteDance Seed blog) | "50 multimodal inputs" (Dreamina), same 30+10+10 split repeated by Pollo, Sohu, Morphic | Same fact, two phrasings. 30+10+10 = 50. No conflict |
| How many assets to actually use | **4 to 5 total**, explicitly "not recommended to use the full asset limit" | Third-party guides celebrate the 50-reference ceiling as the headline feature | **Official.** The ceiling is capacity, not advice |

## Leads worth knowing, all unverified

Each of these is a single-source claim with no primary confirmation. Treat as a hypothesis to test, and
never write it into a graph or a client-facing spec.

- **Extension rounds.** Pollo states a video can be extended consecutively **up to three times** while
  keeping sharpness, colour and motion continuity. The official blog says only "multi-round extensions"
  without a number.
- ~~**Timestamp instructions.**~~ **RESOLVED 2026-08-02, promoted to `reference.md`.** Pollo's claim
  that time-addressed direction works turned out to be correct and understated. The official Dreamina
  Seedance 2.5 User Guide makes timestamps a headline feature with a documented syntax (`0s-3s:`) and a
  three-module long-video formula built around them. Pollo was right and I was wrong to flag it as
  dangerous: I was generalising the official **2.0** warning about unstable timing to 2.5, which is
  exactly the version where it was fixed. Kept here as a reminder that a third-party lead can beat a
  stale primary source.
- ~~**Native 4K.**~~ **REFUTED.** Claimed by Pollo and Morphic. The official 2.5 guide lists output
  resolution as **480p and 720p** only. 4K appears only as an accepted *input* image resolution.
- **Third-party UI limits.** `seedance2ai.app` exposes 480p and 720p with 4, 8 and 15 second choices.
  That is one reseller's product surface, not the model's capability envelope.

## Pre-launch guidance, useful but dated

`seeddance.io` published a Chinese prompting guide on **2026-07-03, before the 2.5 launch**. Its advice
is sensible workflow hygiene rather than a 2.5 measurement:

- too many scenes or actions in one prompt makes motion unstable
- generated readable text is generally weak
- outputs are probabilistic, not exactly reproducible
- image-to-video prompts should explicitly state which faces, products, poses and composition to preserve
- keep a human review step

Its proposed order (subject, action, camera, setting, lighting, style, duration, constraints) broadly
matches the official advanced formula, which is mild corroboration and nothing more.

## Opinion, recorded as opinion

A UISDC author argued before launch that the 50-reference feature may be a **marketing gimmick**
(营销噱头), reasoning that few productions need that many separately controlled characters, and guessed
native 4K would be expensive. The piece frames its own pricing talk as speculation. Recorded because the
scepticism is reasonable and the official "use 4 to 5 assets" recommendation points the same direction.

## What nobody has

As of 2026-08-01, across every accessible source:

- **No hands-on failure report for 2.5 after launch.** Not one.
- **No MiniMax H3 comparison.** The community Feishu wiki reportedly contains one; it is behind a login.
- **No Blender workflow, no long-video guide.** Same wiki, same wall.

If those arrive, they belong in this file first and only move into `reference.md` if a ByteDance source
confirms them.

## Sources

Opened and read: Dreamina official product guide (official, used in `reference.md`), Pollo AI Chinese
page, Sohu article, UISDC article, Morphic Chinese prompt guide, seeddance.io Chinese guide.

Failed to load: five `mp.weixin.qq.com` articles (Internal Error), and both
`bytedance.larkoffice.com` documents (302 to login). No login was attempted and no account was created.
