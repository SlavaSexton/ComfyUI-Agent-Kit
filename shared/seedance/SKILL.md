---
name: seedance
description: Use when writing or debugging prompts for ByteDance Seedance video models (Seedance 2.5, 2.0, 2.0 Mini, 1.5 Pro, 1.0) on Dreamina, Jimeng AI, Doubao, BytePlus ModelArk or ComfyUI, when a generated video drifts off the reference face, grows unwanted subtitles or watermarks, duplicates a character, jumps at an extension seam, or when planning multi-shot or multi-reference video briefs.
---

# Seedance video prompting

ByteDance's Seedance family generates video and audio jointly and takes multimodal references
(images, video clips, audio clips) that a prompt addresses **by label**. Getting the labels and the
task type right matters more than adjectives: the same sentence can be read as "reference this" or
"edit this" depending on one word.

**Load `reference.md`** for the full formulas, the failure table, worked examples and the ComfyUI
parameters. **Load `supplementary.md`** only for non-official leads about 2.5; it never overrides
`reference.md` and carries a conflict ledger. This file is the router and the rules you need before
writing a single line.

## Which model you are talking to

| Model | Where it runs | Refs per pass | Max length | In ComfyUI |
|---|---|---:|---|---|
| Seedance 2.5 | Dreamina, Jimeng AI, Doubao Pro, **and ComfyUI since core v0.31.0** | 30 img + 10 video + 10 audio (audio-only allowed) | 4 to 30s; nest-extend to 60s; **Long Video mode 30 to 180s in one shot** | **Yes**, since 2026-08-08 |
| Seedance 2.0 / 2.0 Mini / 2.0 Fast | BytePlus ModelArk, ComfyUI | 9 img + 3 video + 3 audio | 15s | Yes |
| Seedance 1.5 Pro | BytePlus ModelArk, ComfyUI | n/a (no omni-reference) | 4 to 12s, **min 4s enforced** | Yes, and the only one there with `generate_audio` |
| Seedance 1.0 Lite / Pro / Pro Fast | BytePlus ModelArk, ComfyUI | n/a | n/a | Yes |

**Seedance 2.5 reached ComfyUI on 2026-08-08 (core v0.31.0, PR 15395), and this file said the
opposite until 2026-08-09.** The old line, "Seedance 2.5 has no ComfyUI nodes", was correct on
2026-08-01 and went stale a week later. Kept as a correction rather than silently replaced.

**How to build it now.** 2.5 is a model option inside the SAME `ByteDance2*` nodes, not new nodes:
`ByteDance2TextToVideoNode`, `ByteDance2FirstLastFrameNode`, `ByteDance2ReferenceNode` (category
`partner/video/ByteDance`). Set the `model` DynamicCombo to `Seedance 2.5` and the widgets underneath
change. Minimal graph: the node's `VIDEO` output straight into `SaveVideo.video`.

**What ComfyUI's 2.5 gives you, read from `comfy_api_nodes/nodes_bytedance.py` on master (2026-08-09),
not from the announcement:**
- `resolution` is **480p or 720p only**. There is no 1080p and no 4K on 2.5 in ComfyUI; those live on
  the `Seedance 2.0` option of the same node.
- `duration` 4 to 30 s, `ratio` 16:9 / 4:3 / 1:1 / 3:4 / 9:16 / 21:9 / adaptive (the first-last-frame
  node has no ratio widget), `generate_audio` on by default, `output_format` **mp4 only** even though
  the node's own model tooltip advertises "mp4/mov".
- `ByteDance2ReferenceNode` autogrows to **30 images, 10 videos, 10 audios**, which confirms the
  announcement's 30+10+10 in code. Its `video_editing` toggle makes the output inherit the source
  clip's duration and aspect, and the `duration` / `ratio` widgets are then ignored.
- Node-level prompting rule: **put spoken lines in double quotes** to steer the generated dialogue.
- The **Long Video 30 to 180 s** mode in the table above is a Dreamina / Jimeng feature and is **not**
  reachable through these nodes, whose ceiling is 30 s. Nest-extend instead.

## The three task types, and the word that switches between them

Every Seedance prompt is one of three tasks, and the model decides which from your phrasing:

| Task | Phrasing | Result |
|---|---|---|
| **Multimodal reference** | "Reference `<Subject_N>` in `<Image_N>` to generate..." | brand-new video borrowing an element |
| **Video editing** | "Strictly edit `<Video_N>`, and modify X to Y" | the original video, partially changed |
| **Video extension** | "Extend `<Video_N>` forward/backward to generate..." | the original continued in time |

**The trap:** for edit and extend, name the asset as **`<Video_N>` directly**. Writing
"reference `<Video_N>`" makes the model treat it as a reference task and generate something new
instead of editing what you gave it. (Confirmed, official BytePlus guide.)

## Reference labels

Official ByteDance examples write **`@Image 1`, `@Video 1`, `@Audio 1`** with a space. Dreamina's
consumer guide shows `@Image1` without one. Both appear in the wild; the official form is spaced.
Do not invent other label shapes.

Two ways to name a subject, and you must pick one and keep it:

- **Bind inline:** `<Subject_N>@<Image_N>`, e.g. `Zhang San@Image 1`, repeated every single time the
  subject is mentioned.
- **Define once, then reuse the label:** "define the tall man in Video 1 as **police officer**", then
  say "police officer" consistently forever after.

Define a subject with **2 to 3 stable static features** (clothing, hairstyle, category), never with
mood or action. Every mention must be explicit; an unlabelled mention is where subjects get swapped.

## Four symbols that carry meaning

Officially documented, and nothing else does their job:

| Content | Symbol | Example |
|---|---|---|
| Music | `（）` | `（fast-paced rock music is playing）` |
| Sound effect | `<>` | `<dog barking in the distance>` |
| Dialogue | `{}` | `{Hello, world}` |
| Subtitles | `【】` | `【Chapter One: Departure】` |

Non-Chinese, non-English dialogue must name its language: `says in Japanese {こんにちは}`.

## Shot sequencing beats prose

Write a storyboard, not a paragraph. Label segments `Shot 1`, `Shot 2`, `Shot 3` in the order events
happen, and give each one: camera move or transition, subject action and expression, position or
spatial change, audio.

**Timing depends on the version, and this reversed in 2.5.**
- **2.0:** do not force timings. The official 2.0 guide says support for precise timing such as
  "0 to 3 seconds" is **unstable** and constraining duration can break the generation.
- **2.5:** timestamps are a **headline feature**, built because users asked for exactly this. Write time
  slices as `0s-3s:`, `3s-8s:` and direct each one. See `reference.md` section 2.5-C.

**One camera movement per shot.** Asking for push, pull, pan and track at once destabilises the image.

## Do not fill the reference budget

The single most counterintuitive official rule. 2.5 accepts 50 assets; the guide recommends **4 to 5**:
1-2 character images (headshot plus full body) + 1 scene image + 1 camera-movement video + 1 audio clip.
Too many assets and the model cannot rank features, producing style conflicts and blurred subjects.

Place the assets that need the most faithful reference **earliest in the prompt**.

## When something comes out wrong

| Symptom | First fix |
|---|---|
| Face drifts or swaps mid-video | Add a separate **headshot** reference; never use multi-view character sheets, they read as several people |
| Two identical characters appear | Label every character to its image, plus a global "no duplicate characters" constraint |
| Subtitles you never asked for | Add "avoid generating any text or subtitles"; prefer landscape, portrait is markedly worse |
| A watermark or logo appears | Add "do not generate a watermark", "do not generate a logo" |
| Style drifts to live action | State the style explicitly; better, convert the reference image to the target style first |
| Jump at an extension seam | Post fix: trim 6 frames off the end of the earlier clip and 1 frame off the start of the next |

Full causes, the rest of the table and the ComfyUI-specific limits are in `reference.md`.

## Sources and honesty

Normative content here comes from ByteDance primary sources: the official BytePlus ModelArk prompt
guide for the Seedance 2.0 series, the official Seed blog announcing 2.5 (2026-07-31), Dreamina's
official product guide, and ComfyUI's own node source. Third-party writing is kept out of the
normative layer and lives in `supplementary.md`, subordinate and with its conflicts listed.

**The detailed prompting rules are the official 2.0-series guide.** Seedance 2.5 launched 2026-07-31
and has no public prompting guide of its own yet; it inherits the mechanics visibly, but treat
2.5-specific numbers as the only part confirmed for 2.5. `reference.md` marks every claim.
