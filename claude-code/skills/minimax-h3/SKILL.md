---
name: minimax-h3
description: Use when writing or debugging prompts for MiniMax H3 (Hailuo 3) video-with-audio generation, running the open weights locally in ComfyUI, choosing a quant or an acceleration LoRA for the VRAM you have, wiring reference-to-video with images, video or audio, or when a generated clip produces gibberish speech, drifts off a reference identity, garbles audio after a latent upscale, or refuses to run on a build that looks current.
---

# MiniMax H3 (Hailuo 3)

H3 generates **video and synchronised stereo audio jointly**, from text, images, reference video, reference
audio, or any mix. It is the same model family whether you hit the hosted API or run the open weights, but the
two paths are wired completely differently and only one of them is free.

**Two paths, do not confuse them.**
- **Hosted API**, partner nodes `MinimaxHailuo03TextToVideoNode` / `...FirstLastFrameNode` / `...ReferenceNode`,
  category `partner/video/MiniMax`. 2K output, priced per second, no local weights.
- **Local open weights**, core nodes `MiniMaxH3ImageToVideo` and `MiniMaxH3ReferenceToVideo` from
  `comfy_extras/nodes_minimax_h3.py`. 768p, free, and everything below is about this path.

**Who owns what, so you open one file, not three.** THIS file owns the prompt format and the operating rules.
`reference.md` next to it owns weights, quant sizes, acceleration packs and their wiring. The MiniMax entry in
the kit's `MODELS.md` owns the node-level graph (every node and socket) and the licence. When they disagree,
the node code wins and the discrepancy is a bug worth reporting.

## The prompt format is not free-form prose

H3-Base consumes the output of a hosted prompt refiner (**H3-Context-IR**) that is **not** in the open release.
So locally you write in the refiner's output shape yourself. From MiniMax's own
`VIDEO_PROMPT_WRITING_GUIDE_base_en.md`, that is an optional instruction line, a blank line, then three fields:

```
integrated_multimodal_description: [Shot 1] ... [Shot 2] At 00:04.500, ...

overall_soundscape: ...

non_diegetic_music: ...
```

- `integrated_multimodal_description` carries visuals, action, shots, speakers, dialogue and diegetic sound along
  the timeline. `overall_soundscape` sums ambience and physical-action sound. `non_diegetic_music` is score the
  characters cannot hear.
- **Image modes need a fixed first line.** I2V: `For the target video, at 0.00 seconds into the target video,
  <Picture 1> (from [Shot 1]) is fully referenced.` First-and-last-frame uses the alignment sentence naming both
  pictures and the second each lands on, to two decimals.

### A complete prompt, end to end

Nothing above is usable until you have seen one whole. This is a 5 s text-to-video brief in the official shape:

```
integrated_multimodal_description: [Shot 1] Cinematic medium-wide shot, Push In slowly. A bicycle mechanic in
a navy work coat lowers a metal shutter in a narrow workshop at dusk; warm tungsten light spills across
scattered tools and rain-dark pavement outside. He pauses, looks toward the street. At 00:03.200 he switches
off the bench lamp and the frame drops to ambient blue. The mechanic (weathered voice, mid-fifties, speaks
English only) says quietly: <d>[English] That's enough for today.</d>

overall_soundscape: Steady rain on a metal awning, the rolling clatter of the shutter, one soft click of the
lamp switch, distant tyres on wet asphalt. No music from within the scene.

non_diegetic_music: Sparse solo piano, slow, minor key, entering after the shutter closes and fading to
silence on the lamp click.
```

For **image-to-video** the same block is preceded by the fixed line and one blank line:

```
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] ...
```

Note what is doing the work: one physical action the camera and the sound can both follow, a camera move from
the fixed vocabulary, the spoken line wrapped in `<d>` so the words are exact, and the two audio fields kept
separate so diegetic sound and score do not fight.

## Dialogue: the single most common cause of "the speech is gibberish"

Speakers get stable IDs `(S1)`, `(S2)`, joint `(S1,S2)`. **The words go inside `<d>` with a language tag**, and
everything about who says it and how stays outside. Copy the line verbatim, do not paraphrase or translate:

```
The young woman with a quiet, breathy voice (S1) says: <d>[English] I get off at the next station.</d>
```

Without `<d>` the model is never told the exact words and improvises phonetics. Voiceover needs the exact phrase
`says in an off-screen voiceover` plus a statement that the lips stay closed. Use `<scenetrans>` when a line
crosses a cut, `<cutoff>` when speech is truncated by the end. On-screen text goes in double quotes, verbatim.

## Camera is a controlled vocabulary

Motion type plus amplitude plus speed, and medium amplitude at normal speed is the default you simply omit:
`Zoom In/Out`, `Push In/Pull Out`, `Pan Left/Right`, `Truck Left/Right`, `Tilt Up/Down`, `Pedestal Up/Down`,
`Arc Shot`, `Tracking Shot`.

## Reference-to-video: label every file with a job

`<Subject N>` is the one that does the real work, because it binds sources: "`<Subject 1>` is the woman whose
appearance comes from `<Picture 1>` and whose walking motion comes from `<Video 1>`." Then `<Picture N>` is a
frame or composition anchor, `<Video N>` an editing or temporal source, `<Audio N>` a copied signal.

**Reference-to-video has its OWN output contract, and it is six sections, not the three above.** MiniMax ships
**two** prompt guides, and until 2026-08-09 this skill knew only the first. `VIDEO_PROMPT_WRITING_GUIDE_base_en.md`
governs T2VA / I2VA / FL2VA / L2VA and gives the three fields at the top of this file.
`VIDEO_PROMPT_WRITING_GUIDE_ref_en.md` governs full-reference mode and opens: "A complete rewrite output
consists of six sections in the following order":

```
subject_definitions: <Subject 1> is ... whose appearance comes from <Picture 1> ...
summary: ...
retention_analysis: ...
detailed_description: [Shot 1] ...
overall_soundscape: ...
non_diegetic_music: ...
```

`subject_definitions` declares the references and their labels; `summary` states the task type, the target
video and the main relationships to the references; `retention_analysis` says how each reference is retained,
transferred or reused; `detailed_description` carries visuals, action, shots, sound and dialogue in playback
order; the last two match their base-mode meanings. The order is fixed, and the field is **`retention_analysis`**,
not `retention`. Note this is six named sections of prose in one string, not a JSON array, whatever a
third-party node's docs call it. Confirmed by reading the guide on `MiniMaxAI/MiniMax-H3` (23 553 bytes,
2026-08-09); the core node itself validates none of this, `comfy_extras/nodes_minimax_h3.py` takes a plain
multiline string, so nothing will tell you when you get it wrong except the result.

Limits from the official card: **9 images, 3 video clips, 3 audio clips, 12 files total**, clips 2 to 15 s each
and 15 s total, and **audio can never be the only reference**. The local `MiniMaxH3ReferenceToVideo` node has
**four** Autogrow families reaching those ceilings: `ref_images` (max 9), `ref_videos` (3),
**`ref_video_audios` (3, the soundtrack of the same-numbered reference video)** and `ref_audios` (3, standalone).
A template showing three image sockets is not the limit.

## Ten production jobs to write against

Krea's 2026-08-05 guide frames H3 prompts as production paperwork, one job per clip: director's single-shot
brief · timed three-beat teaser · first-to-last-frame passage · influencer identity-and-voice lock ·
reference-motion performance · native-audio product reveal · brand-title reveal with required text and negatives ·
protected-frame object swap · UI walkthrough · omni-reference director brief. Pick the job first, then decide
which control has to survive: camera, timing, identity, motion source, or the sound event line.

Note their examples use a `[0-3s]` beat style, which is a readable shorthand rather than MiniMax's own
`[Shot N]` plus `At 00:04.500` convention. Both work; the official form is the safer default locally.

## Operating facts that bite

- **Frame count sits on a grid.** `length` must leave **remainder 5 modulo 17** (124 frames = ~5 s, 73 = ~3 s,
  362 = ~15 s). The node calls it the "17k+5 grid" and the trained range is ~124 to 362 frames.
- **Native size is ~1 MP**, template default **1344 x 768** at 24 fps. Higher costs time and VRAM without more
  real detail; the official 2K route is a hosted regenerate pass that is not open.
- **Duration:** trained and tested 5 to 15 s. Longer runs but is untrained territory.
- **Speed:** the open release ships **full attention only**; sparse attention is promised later. This is why it
  is slow, and why the community acceleration below matters.
- **Licence:** open weights, not open source, and the territory clause is unusually strict. See `MODELS.md`.

## When it goes wrong

| Symptom | Most likely cause |
|---|---|
| Speech is fluent-sounding nonsense | The line is not inside `<d>[Language] ... </d>` |
| Face drifts across the clip | No `<Subject N>` binding the identity source, or refs at the wrong scale after an upscale |
| Audio garbles after a latent upscale | `audio_denoise` left at its default 1.0 (inferred cause, not measured); audio settles late, so run more of the schedule in pass 1 |
| Wrong face animated in a crowd | Reference sizing set to `match` when identity needed `max` |
| Acceleration node refuses to load | The build is older than the pack requires; a tagged release is not automatically new enough |
| Output length is not what you asked | `length` fell off the 17k+5 grid |
