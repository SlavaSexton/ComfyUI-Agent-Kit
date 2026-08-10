# Video models (API / closed)

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 13 entries for this family.


### Kling (2.1/2.5, 2.6, 3.0/V3, O1, O3) - Kuaishou
- **Prompt style:** five-part - Subject (specific) -> Action/Motion (start+end, "first... then... finally...", speed) -> Scene (5-7 details + lighting) -> Camera (move with motivation + lens) -> Audio (tag speakers + tone, on 2.6/V3/O3). `++emphasis++` max 2. O1 edits use plain instructions.
- **Structure:** most-important first; multi-shot (V3/O3): label `Shot 1 (Xs): [framing] - [subject+action]. [camera]. [audio]`; bind recurring subjects with `@ElementName`.
- **Strengths:** motion/physics fidelity, explicit camera direction, native audio (2.6/V3/O3) with lip-sync + multi-character dialogue; up to 15s / 6 shots (O3); O1 unifies generate + edit.
- **Avoid:** open-ended motion (looping), pronouns/synonyms across shots, >2 emphasis. Negatives ARE supported (no negation words).
- **Settings:** 1080p; 5/10s (O1 3-10s; O3 up to 15s); aspect 16:9/9:16/1:1; `cfg_scale` 0-1 (def 0.5); Standard vs Pro; prompt ~2500 chars.
- **Source:** ir.kuaishou.com (Kling O1 / 3.0 releases) ; node templates `kling_*.md`.

### Veo 3 / 3.1 (Google)
- **Prompt style:** natural-language, 100-150 words; one camera move (film terms); audio after the visual ("Audio: ...").
- **Structure:** Subject -> Action -> Context/Setting -> Style (early) -> Camera/Lens -> Lighting -> Motion -> Audio -> Constraints (end).
- **Strengths:** native audio (dialogue + SFX + ambient + music) with lip-sync, real-world physics; 3.1 adds native 9:16, up to 3 refs, first/last-frame, Scene Extension.
- **Avoid:** "don't show X" does NOT work (use descriptive exclusions at the end, 1-3 max); over-constraining; conflicting camera moves.
- **Settings:** T2V + I2V; 5-20s; aspect 16:9/9:16/1:1/21:9; prompt ~1024 tokens; optional structured JSON.
- **Source:** ai.google.dev/gemini-api/docs/video ; node template `veo.md`.

### Gemini Omni Flash (Google)
- **What it is (confirmed, Google DeepMind model card, published 2026-05-19):** an any-to-any generative video model - text-to-video, image-to-video, and conversational video *editing* - with **native audio out**. Inputs are text, images, audio, and video; output is high-resolution video with audio. Google's card claims real-world-physics simulation and faithful instruction following.
- **ComfyUI (confirmed from the official Comfy-Org/workflow_templates, read 2026-06-30):** official partner node **`GeminiVideoOmni`** with three shipped templates - `api_google_gemini_omni_flash_t2v` / `_i2v` / `_video_edit`. It is an API / cloud partner node - runs server-side through Comfy's API, needs a Comfy API key + credits, like Veo / Kling / Sora - and needs a current ComfyUI (the node landed after 0.25.1; if it is missing, update ComfyUI + the frontend / api-nodes package).
  - **Node I/O:** inputs `model.prompt` (STRING), `model.images.image_1..3` (IMAGE, up to 3 reference images, used by I2V), `model.videos.video_1..2` (VIDEO - a source clip plus an optional second for edits); outputs `VIDEO` and a `STRING` (response text). Widgets seen in the templates: `["Omni Flash", "", 1, 0.95, <seed>, "randomize"]` = model variant, an (empty) text field, a count, ~0.95 temperature/guidance, seed, seed-control (exact widget labels inferred - confirm via `get_node_info GeminiVideoOmni` once your build has it).
  - **Three graphs (buildable, from the official templates):** T2V = `GeminiVideoOmni(model.prompt)` -> `SaveVideo` (+ `PreviewAny` on the STRING). I2V = `LoadImage` x1-3 -> `GeminiVideoOmni(image_1..3, prompt)` -> `SaveVideo`. Video-edit = `LoadVideo` -> `GeminiVideoOmni(video_1 [+ optional video_2], prompt)` -> `SaveVideo`.
- **"Replaces Veo entirely" is overstated:** Google's own card lists Veo and Gemini Omni Flash as separate models, and the official templates still ship Veo (`api_veo2_i2v`, `api_veo3`). Treat Omni Flash as an addition, not a Veo removal.
- **Prompt style (inferred from the Gemini / Veo family plus the conversational-edit design; verify against Google Flow / the node once you run it):** natural language, subject -> action -> setting -> camera -> audio; for an edit, give a plain conversational instruction ("make it night, add rain on the window, keep the actor"). Audio renders with the visual, so name dialogue / SFX / ambience in the prompt.
- **Third-party alternative:** the community pack `github.com/Anil-matcha/gemini-omni-comfyui` reaches the same model via the **muapi.ai** API (its own nodes + a video saver, `gemini_omni_nodes.py`) if you prefer that route over Comfy's own API.
- **Source:** deepmind.google/models/model-cards/gemini-omni-flash (2026-05-19) ; Comfy-Org/workflow_templates `api_google_gemini_omni_flash_{t2v,i2v,video_edit}.json` (official node `GeminiVideoOmni`, confirmed 2026-06-30) ; muapi.ai + github.com/Anil-matcha/gemini-omni-comfyui (third-party route).

### Sora 2 / Sora 2 Pro (OpenAI)
- **Prompt style:** storyboard sketch, 50-100 words; write for the lens, not adjectives.
- **Structure:** Subject+environment -> Camera (framing, angle, lens, single move) -> Action (2-3 beats with timing) -> Lighting+color (3-5 anchors) -> Audio (one note/line) -> Constraints; front-load visuals into the first ~500 chars.
- **Strengths:** coherence/continuity, native dialogue + SFX synced to timing, technical lens/film-stock cues; Pro = higher fidelity.
- **Avoid:** abstract descriptors, >2-3 beats, multiple camera moves, past ~100 words. Exclusions structured at end.
- **Settings:** T2V + I2V (image = first frame, match resolution); max ~2000 chars; Storyboard/Loop are web-app only.
- **Source:** platform.openai.com/docs/guides/video-generation ; node template `sora.md`.

### Seedance 1.0, 1.5 Pro, 2.0 and 2.5 (ByteDance)
- **Prompt style:** structured, concise (2.0 under ~60 words + constraints); cinematic camera language is the core strength.
- **Structure:** Subject -> Action (one verb/shot + speed + endpoint) -> Camera (shot size, then one move + angle + lens) -> Style -> Constraints; multi-shot via cut words ("Cut to / Camera switching"); 2.0 refs `@Image1 as the main character`.
- **Strengths:** camera-language response (surround, aerial, zoom, pan, follow, handheld); multi-shot consistency; 2.0 native audio with phoneme-level lip-sync (8+ langs), camera-motion replication, beat-synced editing.
- **Avoid:** stacking motion verbs, vague mood as camera direction; on-screen text and fast hands glitch; set "not fixed camera" when moving. Constraints (3-5 bans) substitute for a negative field.
- **Settings:** 480/720/1080p, **2.0 now up to 4K** (smoother gradients, richer tones, detail that holds through motion and into post; the templates default to 720p, raise the resolution field for 4K), 24fps; 2-12s (1.0) / 4-15s or auto (2.0); 2.0 inputs up to 9 images / 3 videos / 3 audio (`model.reference_images.image_1..9`, `reference_videos.video_*`, `reference_audios.audio_*`).
- **2.0 official ComfyUI templates / modes:** T2V, reference-to-video (R2V), first-last-frame (FLF2V); R2V and FLF2V each also ship a `_real_human` variant tuned for realistic people (T2V does not); `api_seedance2_0_t2v.json` + `api_seedance2_0_{r2v,flf2v}(_real_human).json` (Comfy-Org/workflow_templates), plus community storyboard-to-video / character-swap / LLM-prompt-helper. A faster, cheaper **Seedance 2.0 Mini** is selectable in the same `ByteDance2TextToVideoNode` / `ByteDance2ReferenceNode` (templates `api_seedance2_0_mini_{t2v,r2v}.json`).
- **Seedance 1.5 Pro - the tier the kit used to skip.** `seedance-1-5-pro-251215`, selectable in **`ByteDanceTextToVideoNode`**, **`ByteDanceImageToVideoNode`** and **`ByteDanceFirstLastFrameNode`** (NOT the `ByteDance2*` nodes, which are the 2.0 family). Templates `api_bytedance_seedance1_5_{text_to_video,image_to_video,flf2v}.json`. Confirmed from `comfy_api_nodes/nodes_bytedance.py` on master: `resolution` 480p / 720p / 1080p, `aspect_ratio` 16:9 / 4:3 / 1:1 / 3:4 / 9:16 / 21:9, `duration` slider 3-12s. Three things only the code tells you: (1) **minimum duration is 4 seconds** - the node raises `ValueError` below that even though the slider goes to 3; (2) **`generate_audio` is honoured ONLY for 1.5 Pro** and is ignored on every 1.0 model in the same nodes, and it **doubles the price** (per 10s: 480p $0.12, 720p $0.26, 1080p $0.58-0.59, scaled by `duration / 10`); (3) the node **rejects settings written into the prompt text** via `raise_if_text_params` (`resolution`, `ratio`, `duration`, `seed`, `camerafixed`, `watermark`) - set them on widgets, not in prose. `camera_fixed` only appends an instruction to your prompt and is explicitly not guaranteed.
- **Seedance 2.5 SHIPPED in ComfyUI on 2026-08-08 and this entry said the opposite until 2026-08-09.** The
  earlier line, "Seedance 2.5 exists but has NO ComfyUI nodes", was true when written on 2026-08-01 and went
  stale seven days later with core **v0.31.0** (PR 15395). It is kept here as a correction rather than quietly
  overwritten. **2.5 is now a model option inside the SAME `ByteDance2*` nodes**, confirmed by reading
  `SEEDANCE_MODELS` and the `IO.DynamicCombo` option lists in `comfy_api_nodes/nodes_bytedance.py` on master:
  - `ByteDance2TextToVideoNode` (display "ByteDance Seedance 2.5 Text to Video"), `ByteDance2FirstLastFrameNode`
    ("... First-Last-Frame to Video"), `ByteDance2ReferenceNode` ("... Reference to Video"), category
    `partner/video/ByteDance`. The `model` widget is a DynamicCombo whose options are `Seedance 2.5`,
    `Seedance 2.0`, `Seedance 2.0 Fast`, `Seedance 2.0 Mini`; picking one swaps the sub-widgets underneath it.
    Model id behind 2.5 is `dreamina-seedance-2-5-260628`.
  - **The graph is two nodes.** `ByteDance2TextToVideoNode.VIDEO` -> `SaveVideo.video`. That is the whole shipped
    `api_seedance2_5_t2v.json`. FLF2V adds two `LoadImage` into `first_frame` / `last_frame`; R2V uses
    `ByteDance2ReferenceNode` with `LoadImage` into `reference_images.image_1`. The video-editing template adds
    one more node worth copying: `LoadVideo` -> **`Video Slice`** (core, `comfy_extras/nodes_video.py`; widgets
    `0, 5, false` there) -> the node's `reference_videos.video_1`, so only the first 5 seconds of the source
    clip are sent rather than the whole file.
  - **2.5 sub-widgets:** `prompt` (multiline), `resolution` **480p or 720p ONLY**, `ratio` 16:9 / 4:3 / 1:1 /
    3:4 / 9:16 / 21:9 / adaptive (absent on the first-last-frame node, which takes the ratio from the frames),
    `duration` slider **4 to 30 s** (default 5), `generate_audio` (default true), `output_format` **mp4 only**.
  - **Two limits that contradict the marketing, both read off the code.** 2.5 has **no 1080p and no 4K** in
    ComfyUI: those resolutions exist only on the `Seedance 2.0` option. And the node's own model tooltip
    advertises "mp4/mov output" while the `output_format` combo offers exactly `["mp4"]`. Take the widget, not
    the tooltip.
  - **Reference capacity, now confirmed in code rather than from the announcement:** `ByteDance2ReferenceNode`
    on 2.5 autogrows to **30 reference images, 10 reference videos and 10 reference audios** (`image_1..30`,
    `video_1..10`, `audio_1..10`), plus `auto_downscale` (default on) and `auto_upscale` (advanced, default off)
    for reference videos outside the pixel budget. Its `video_editing` boolean is the edit-in-place switch: with
    it on the output keeps the SOURCE clip's length and aspect ratio and the `duration` / `ratio` widgets are
    ignored entirely.
  - **Prompting rule straight from the node:** "Put spoken lines in double quotes to steer the generated
    dialogue."
  - **Price** (from the node's own `price_badge` expression, approximate and per run): 2.5 bills per frame at
    24 fps times duration plus one frame, at **$0.015301** per unit without a reference video and **$0.009152**
    with one; the per-frame unit is 400 at 480p and 900 at 720p for 16:9, with small deltas for 1:1, 4:3, 3:4
    and 21:9. Evaluating that expression: 720p 5 s 16:9 = **$1.67**, 480p 5 s 16:9 = **$0.74**, 720p 10 s 16:9 =
    **$3.32**. These come from running the badge's own formula, not from a quoted price list.
  - Full prompting mechanics for the family (the three task types, the `@Image 1` label syntax, the
    `（）<>{}【】` symbols, shot sequencing, the asset-count rule and the failure table) live in the dedicated
    sibling **`seedance` skill** (invoke by name; beside the comfyui skill on disk), distilled from the official
    BytePlus prompt guide.
- **Source:** docs.byteplus.com (Seedance 1.0 / 1.5 / 2.0 prompt guide) ; Comfy-Org/workflow_templates `api_seedance2_0_*` and `api_seedance2_5_{t2v,flf2v,r2v,video_editing}.json` ; ComfyUI "Seedance 2.0 4K is live" announce (2026-06) ; seed.bytedance.com Seedance 2.5 announce (2026-07-31) ; blog.comfy.org "Seedance 2.5 is now available via Partner Nodes" (2026-08-08) ; core release v0.31.0 PR 15395 ; `comfy_api_nodes/nodes_bytedance.py` on master, read 2026-08-09.

### FLUX 3 Video (Black Forest Labs, API, new in core v0.31.0)
BFL's first video model in ComfyUI, and it generates **synchronized audio** (ambient, speech, effects) in the
same pass. Everything below is confirmed by reading `comfy_api_nodes/nodes_bfl.py` on master (classes
`Flux3VideoNodeBase`, `Flux3TextToVideoNode`, `Flux3ImageToVideoNode`, `Flux3VideoContinuationNode`, all three
registered in `BFLExtension`), plus the shipped templates `api_bfl_flux3_t2v.json` / `api_bfl_flux3_i2v.json`.

- **Prompt style:** plain language, and the service expands it for you. The node's own tooltip: "What you want,
  in plain language; the prompt is interpreted and expanded before generation." So do NOT tag-dump. The one
  piece of structure that pays: **describe ambient sound, music and speech separately** if you want layered
  audio, because that is what the tooltip asks for. On image to video the prompt tooltip shifts to "How the
  scene should move and sound", so write motion plus audio there, not appearance.
- **The graph is two nodes.** `Flux3TextToVideoNode.VIDEO` -> `SaveVideo.video`; that is the entire shipped T2V
  template. Image to video is `LoadImage` -> the node's `images` autogrow slot -> `SaveVideo`.
- **Three nodes, category `partner/video/BFL`:**
  - `Flux3TextToVideoNode` ("Flux 3 Text to Video"): `prompt` + the common widgets.
  - `Flux3ImageToVideoNode` ("Flux 3 Image to Video"): `prompt`, then an autogrow group **`keyframes`** (slots
    `image_1` to `image_10`, minimum 1, **in playback order**, each at least 256x256 and no more extreme than
    64:1 aspect), then a DynamicCombo **`placement`** with two options: `spread across the clip` (FLUX 3 places
    them; one image opens the clip, two become its start and end) or `at times`, which reveals a `times` string
    taking one increasing, comma-separated second per image, e.g. `0, 2.5, 5`. Graph: `LoadImage.IMAGE` ->
    `keyframes.image_1`, node VIDEO -> `SaveVideo`.
  - `Flux3VideoContinuationNode` ("Flux 3 Video Continuation"): takes a `video` and carries on from its final
    frames. The source clip is uploaded to the Comfy API first.
- **Common widgets on all three:** `aspect_ratio` (auto, 21:9, 2:1, 16:9, 4:3, 1:1, 3:4, 9:16; default auto),
  `duration` (auto or an integer **5 to 20** seconds; default auto), `resolution` (**720p or 1080p**, default
  720p), `generate_audio` (default true; off gives a silent video), `safety_tolerance` (0 strictest to 4,
  advanced, and **any request carrying an image or video is capped at 2** whatever you set), `seed` (BFL picks
  its own seed, so results are nondeterministic regardless).
- **Price, per second, taken from each class's `RATE_HD` / `RATE_FHD`:** text to video and image to video
  **$0.2431/s at 720p** and **$0.4147/s at 1080p**; **continuation is much dearer at $0.5863/s and $0.7579/s**.
  A 10 s 1080p continuation is therefore about $7.58 against $4.15 for generating the same length fresh. Set
  `duration` to a number rather than `auto` if you want the badge to show a total instead of a rate.
- **Gotcha:** a failed task answers the poll with a retryable-looking HTTP 5xx (500 and 503 both observed by the
  node's author, who capped it at 3 retries per poll). If a job dies, expect a server error rather than a clean
  failure message.
- **Source:** `comfy_api_nodes/nodes_bfl.py` on master ; templates `api_bfl_flux3_t2v.json`, `api_bfl_flux3_i2v.json` ; core release **v0.31.0** (2026-08-08) PR 15295 ; blog.comfy.org "FLUX 3 is now available via Partner Nodes" (2026-08-05). Read 2026-08-09.

### Luma Ray 2 / Ray 3 (Dream Machine)
- **Prompt style:** keep camera OUT of the prompt (set via API "Concepts"); content-only.
- **Structure:** Main subject -> Action (direction + endpoint) -> details -> scene/atmosphere -> style -> quality reinforcer at end; pass camera as composable Concepts (20 moves, 14 angles).
- **Strengths:** photorealism, composable multi-motion camera, Loop + Video Extension (~60s); Ray 3 reasoning + 16-bit EXR HDR.
- **Avoid:** camera in the prompt text; multiple primary actions; negative phrasing. No negative field, no CFG, no seed, no native audio.
- **Settings:** 540/720/1080p; 5s or 9s; many aspects; Ray 2 Flash 3x faster; image inputs `frame0`/`frame1`.
- **ComfyUI:** Ray 3.x runs via `LumaRay32TextToVideoNode` (+ `LumaRay32ExtendVideoNode` to extend a clip, chained by the upstream `generation_id`); template `api_luma_ray3_3_t2v.json`.
- **Source:** docs.lumalabs.ai/docs/video-generation ; node template `luma.md`.

### Runway Gen-4 / Gen-4.5
- **Prompt style:** complete natural-language sentences (not keyword lists); precise verbs; one action + one camera move per sentence with a speed modifier.
- **Structure:** Subject action -> Camera motion -> Visual context/style; for I2V don't re-describe the source; references control their domain (Character / Style / Environment, up to 3).
- **Strengths:** reference consistency across shots, clean cinematic motion; Gen-4.5 adds T2V + sequenced camera choreography + higher resolution.
- **Avoid:** "no X"/"avoid Y" NOT supported (may backfire); keyword lists; competing actions. No negatives, no CFG, no native audio.
- **Settings:** 720p (Gen-4 Turbo) / 720-1080p (Gen-4.5); 5/10s; 24fps; max prompt 1000 chars; Gen-4 Turbo is I2V-only.
- **Source:** docs.dev.runwayml.com ; help.runwayml.com Gen-4 prompting guide ; node template `runway.md`.

### MiniMax / Hailuo
- **Prompt style:** Subject + Action (dynamic verbs) + Setting + Time + Style; camera commands in square brackets with NO space before text, e.g. `[Push in]A lamb stands...`.
- **Structure:** bracket at the point the move occurs; combine up to 3 moves - simultaneous `[Pan left,Pedestal up]` (no gap) or sequential `[Push in] then [Pan right]`.
- **Strengths:** physics/motion realism, facial expression, frame-accurate motion; Director-mode camera; keyframe control; multilingual.
- **Avoid:** vague words, natural-language camera descriptions (use brackets), space after `]`, over-long. Default Prompt Optimizer rewrites prompts (set `prompt_optimizer: false` for precise control). No standard negative field.
- **Settings:** T2V + I2V; Standard vs Fast; prompt 2-2000 chars (optimal ~100-300).
- **MiniMax H3 (Hailuo 03), new in core v0.29.2 (PR 15167) - three nodes**, all category `partner/video/MiniMax`, confirmed from `comfy_api_nodes/nodes_minimax.py` on master. Every one of them nests its generation widgets inside a `model` DynamicCombo whose single option is `MiniMax H3`, so the widgets read `model.prompt`, `model.resolution`, `model.duration` and so on.
  - **`MinimaxHailuo03TextToVideoNode`** ("MiniMax H3 Text to Video"): `model` (prompt, `resolution` = `2K` only, `ratio` from `16:9 / 4:3 / 1:1 / 3:4 / 9:16 / 21:9`, `duration` 5 to 15s slider) + `seed` + `watermark` (default off) -> VIDEO out -> `SaveVideo`.
  - **`MinimaxHailuo03FirstLastFrameNode`** ("MiniMax H3 First-Last-Frame to Video"): same widgets minus `ratio` (the aspect follows the images), plus `first_frame` (IMAGE, required) and `last_frame` (IMAGE, optional). Wire one `LoadImage` into each. Frames are validated: aspect between **2:5 and 5:2** and at least **256x256**, else the node errors before spending anything.
  - **`MinimaxHailuo03ReferenceNode`** ("MiniMax H3 Reference to Video"): adds three Autogrow groups - `reference_images` (`image_1`..`image_9`), `reference_videos` (`video_1`..`video_3`, 2 to 15s each, 15s total) and `reference_audios` (`audio_1`..`audio_3`, same limits). **Audio cannot be used without at least one image or video reference.**
  - **Prompting H3, from the node descriptions and the shipped templates:** refer to each reference by its connection order in the prose - "Image 1", "Image 2", "Video 1", "Audio 1". The official `api_minimax_h3_t2v` prompt opens with a technical header ("Single continuous shot, 5 seconds, one take, no cuts. Cinematic oner, third-person chase camera, ... Aspect ratio 16:9."), then the scene, then a **second-by-second beat sheet** ("Second 0-1: ... Second 1-2.5: ..."), then a bracketed `[VFX: ...]` list, then explicit exclusions ("No text, no logos, no dialogue"). The `flf2v` template opens with "Use Image 1 as the first frame and Image 2 as the last frame." This is a different shape from the classic Hailuo `[Push in]` bracket syntax above; H3 takes long directed prose.
  - **Cost:** the price badge computes **duration x $0.1859** for t2v and flf2v (so a 5s clip is about $0.93), and the reference node adds per-reference terms on top. Priced from the node's own `PriceBadge` expression, not from a docs page.
- **Source:** minimax.io/platform/document/video_generation ; node template `minimax.md` ; `comfy_api_nodes/nodes_minimax.py` on master + Comfy-Org/ComfyUI PR 15167 (v0.29.2) ; templates `api_minimax_h3_{t2v,flf2v,r2v}.json`.

#### MiniMax H3 LOCAL (open weights) - a second, entirely separate path from the API nodes above

**READ THE LICENCE BEFORE YOU RUN IT. This one has teeth.** The MiniMax H3 Community License Agreement (2026-08-02,
`MiniMaxAI/MiniMax-H3/LICENSE`) grants rights only inside the "Applicable Territory", defined as worldwide
**excluding the European Union, the United Kingdom, the Republic of Korea and the United States of America**.
Section V.4 is explicit that this covers the outputs too: "You may not use, reproduce, modify, distribute, or
display the MiniMax H3 Works **or any of their Outputs or results** outside the Applicable Territory." Anyone in
those four territories has to contact MiniMax for a separate licence rather than just downloading the weights.
Beyond territory: over **20 million USD** yearly revenue needs prior written authorisation (api@minimax.io), any
product built on it must display **"Powered by MiniMax H3"**, and redistribution must carry the copyright notice.
Open weights, NOT open source. Quoted from the licence file itself, not from a summary.

**What is actually open.** Only **H3-Base** ships, and it generates at **768p**. The official system has three
modules, and two are hosted-only: **H3-Context-IR** (a multi-stage prompt/context refiner that MiniMax calls
"critical to the quality of the final output") and **H3-Regenerate-2K** (the 2K upscale pass). So the local model
is the base engine without the official prompt brain and without the 2K stage. In their place: any local LLM to
expand prompts into the format below, and an ordinary upscaler. Expect the hosted web result to look more
finished than a local run of the same idea; that is the missing IR, not your settings.

**Build the graph (confirmed from `comfy_extras/nodes_minimax_h3.py` and the shipped templates).** Two core nodes:
- **`MiniMaxH3ImageToVideo`** covers T2V, I2V, first-frame, last-frame and first-and-last-frame in one node.
  Inputs `clip` (CLIP), `vae` (VAE), `first_frame` (IMAGE, optional), `last_frame` (IMAGE, optional),
  `prompt` (STRING), `width` / `height` / `length` (INT). Outputs `positive` (CONDITIONING) + `LATENT`.
  **Connect no image and it IS text-to-video** - that is exactly how the `video_minimax_h3_t2v` template works.
- **`MiniMaxH3ReferenceToVideo`** for reference-to-video. Same inputs plus `audio_vae` (VAE),
  `ref_images.ref_image_0..2` (IMAGE), `ref_videos.ref_video_0` (IMAGE), `ref_video_audios.ref_video_audio_0`
  (AUDIO), `ref_audios.ref_audio_0` (AUDIO). Same two outputs.
- **The complete graph, every node the template actually contains.** Drop these and wire exactly this way; the
  list is deliberately exhaustive because a missing `RandomNoise` alone makes `SamplerCustomAdvanced` invalid.
  - **Feeding the H3 node:** `CLIPLoader` (type **`minimax`**) -> `clip` · `VAELoader` (video VAE) -> `vae` ·
    `VAELoader` (audio VAE) -> `audio_vae` · `ResolutionSelector` -> `width` and `height` ·
    `PrimitiveFloat` (duration in seconds) -> `ComfyMathExpression` -> `length` ·
    `PrimitiveStringMultiline` -> `prompt` (the templates keep the prompt in its own node, not typed into the
    H3 widget) · `LoadImage` -> `first_frame` / `last_frame` on the FL2VA node, or -> `ref_image_N` on the
    reference node. For plain text-to-video, connect no image at all.
  - **Sampling:** `UNETLoader` (fl2va or ref2va) -> **both** `BasicGuider` and `BasicScheduler`, not just one.
    The H3 node's `positive` -> `BasicGuider`. Then `RandomNoise` (NOISE), `BasicGuider` (GUIDER),
    `KSamplerSelect` **`res_multistep`** (SAMPLER) and `BasicScheduler` **`simple`, 25 steps** (SIGMAS) all four
    into `SamplerCustomAdvanced`, plus the H3 node's `LATENT`.
  - **Decoding:** `SamplerCustomAdvanced`'s LATENT goes to **both** `VAEDecode` (through the video VAE) and
    `VAEDecodeAudio` (through the audio VAE). Their IMAGE and AUDIO meet in `CreateVideo` at **24 fps** ->
    `SaveVideo`. Skip the audio branch and you throw away the model's headline feature.
  - **Two nodes in the I2V template that are NOT part of the live path.** It also carries
    `ImageScaleToTotalPixels` -> `GetImageSize`, and that pair is **left disconnected**: the scaler has no input
    wired and the size outputs feed nothing, because the generation size comes from `ResolutionSelector`. They
    are there as the alternative route, scale the input image to the target pixel budget and take width and
    height from it, which is worth wiring yourself when the output must follow the source image's aspect exactly
    instead of a preset ratio. Do not copy them expecting them to do something as shipped.
- **The frame grid, straight from the node schema.** `length` is `default 124, min 5, max 3600, step 17`, and the
  tooltip names the rule: frame count at 24 fps **snapped up to the model's "17k+5 grid"**, i.e. it must leave
  **remainder 5 when divided by 17** (124 = ~5 s, 73 = ~3 s). The templates compute it with
  `max(5, round(seconds * 24)) + (5 - (max(5, round(seconds * 24)) % 17)) % 17`; keep that `ComfyMathExpression`
  rather than typing a length by hand. **The trained range is ~124 to 362 frames** (roughly 5 to 15 s) per the
  same tooltip; the widget accepts up to 3600 but the model was not trained there, which is the honest ceiling
  behind the "people ran 25 s clips" reports.
- Template defaults: **1344 x 768**, 16:9, which matches the model's ~1 megapixel training target. Push past it
  and time and VRAM climb while detail does not; the official route to 2K is the Regenerate pass that is not open.

**Files (exact names and sizes, read from the `Comfy-Org/MiniMax-H3` repo tree).** Two task families, four
precisions each, all under `diffusion_models/`:
`minimax_h3_{fl2va,ref2va}_bf16.safetensors` **66.3 GB** · `..._int8_convrot.safetensors` **34.0 GB** ·
`..._pruned_int8_convrot.safetensors` **21.0 GB** · `..._pruned_fp8_scaled.safetensors` **21.0 GB**.
Use **fl2va** for T2V / I2V / first-last-frame and **ref2va** for reference-to-video. Plus
`text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`, `vae/minimax_h3_video_vae_fp16.safetensors` and
`vae/minimax_h3_audio_vae_fp32.safetensors`. Note the **pruned fp8 variant**, same 21 GB as the pruned int8 and
worth trying if int8 misbehaves on your card. These are Comfy-Org's own conversions; the community has since
added GGUF / INT4 / NVFP4 builds under other authors (Abiray, Merserk, DeepBeepMeep, Gluttony10 and more).

**Prompt format: H3-Base eats the IR output, so write in that shape.** From the official
`VIDEO_PROMPT_WRITING_GUIDE_base_en.md`, the prompt is an optional instruction line, a blank line, then **three
named fields**:
```
integrated_multimodal_description: [Shot 1] ... [Shot 2] At 00:04.500, ...
overall_soundscape: ...
non_diegetic_music: ...
```
`integrated_multimodal_description` carries visuals, action, shots, speakers, dialogue and diegetic sound along
the timeline; `overall_soundscape` sums up ambience and physical-action sound; `non_diegetic_music` is score the
characters cannot hear. For I2V the first line is fixed: `For the target video, at 0.00 seconds into the target
video, <Picture 1> (from [Shot 1]) is fully referenced.` First-and-last-frame uses the alignment sentence naming
both pictures and the second mark each lands on, to two decimals.
- **Dialogue has a syntax, and this is why "the speech is gibberish" reports happen.** Speakers get stable IDs
  `(S1)`, `(S2)`, joint `(S1,S2)`. The spoken words go **inside `<d>` tags with a language tag**, everything about
  who says it and how stays outside, and the text is copied verbatim:
  `The young woman with a quiet, breathy voice (S1) says: <d>[English] I get off at the next station.</d>`
  Voiceover needs the exact phrase `says in an off-screen voiceover` plus a statement that the lips stay closed.
  Use `<scenetrans>` when a line crosses a cut and `<cutoff>` when speech is truncated by the end.
- **On-screen text** goes in double quotes, verbatim, untranslated.
- **Camera** is motion type plus amplitude plus speed, from a fixed vocabulary: `Zoom In/Out`, `Push In/Pull Out`,
  `Pan Left/Right`, `Truck Left/Right`, `Tilt Up/Down`, `Pedestal Up/Down`, `Arc Shot`, `Tracking Shot`. Medium
  amplitude and normal speed are the defaults and are simply left out.
- **Reference labels (R2V)**, from `VIDEO_PROMPT_WRITING_GUIDE_ref_en.md`: `<Subject N>` is the key one because it
  binds sources together, e.g. "`<Subject 1>` is the woman whose appearance comes from `<Picture 1>` and whose
  walking motion comes from `<Video 1>`." `<Picture N>` is a frame or composition anchor, `<Video N>` an editing
  or temporal source, `<Audio N>` a copied signal. The guide's full structure is `subject_definitions`, `summary`,
  `retention_analysis` (what is preserved, transferred or reused) and `detailed_description`.

**Reference limits and the sizing switch.** The node's slots are **Autogrow**, so the shipped template showing
three image sockets is just what that graph instantiated, not the ceiling. From the node schema: `ref_images`
**max 9**, `ref_videos` **max 3**, `ref_video_audios` **max 3**, `ref_audios` **max 3** - the same envelope as the
official card, which adds that clips run 2 to 15 s each with 15 s total, at most **12 files** across all types,
and that **audio can never be the only reference** (it must accompany an image or video). `ref_video_audio_N` is
specifically the soundtrack of the same-numbered reference video; `ref_audio_N` is standalone audio.
- **`ref_image_size` is the setting that will surprise you on cost.** `match` (default) scales each reference
  down to the generation's pixel area; `max` uses the reference pipeline's 2048 px short edge for the best
  identity fidelity. The node's own tooltip warns why that is not free: **reference tokens ride through every
  sampling step, so `max` can be several times slower**. Reach for `max` when a face has to hold, stay on
  `match` otherwise. References are only ever downscaled, never upscaled.

**Speed and hardware (field reports, not measured here).** Generation is slow, and the reason is in the official
card: H3 supports sparse attention natively but **the open release ships inference with full attention only**,
with a sparse implementation promised later. Community VRAM ladder as reported by users: 8 GB is a stunt, 12 GB
does 480p short T2V with aggressive offload, 16 GB is a working minimum for 480p 5 to 10 s, **24 GB (3090/4090)
is the realistic home tier for T2V / I2V and short R2V**, 32 GB works comfortably near the native megapixel, and
48 GB is where heavy reference-to-video with long video references stops thrashing. On Windows, ComfyUI has been
reported to use only part of the card (15 to 17 GB of a 24 GB board) while pushing the rest into system RAM, with
Linux behaving better. Treat the whole ladder as community reports; the numbers were not verified here.
- **Duration:** the node itself states the trained range as ~124 to 362 frames, about 5 to 15 s. Nothing blocks a
  longer `length` and people have posted 25 s clips, but that is past training; expect drift and cost, and treat
  15 s as where the evidence stops.
- **Content behaviour:** the safety guardrails described on the model card are part of the **hosted** pipeline
  (automated moderation of submitted material and enhanced prompts). The open weights carry no such filter, and
  anatomical fidelity holds up in the image and reference paths. The licence's acceptable-use terms still apply
  to whatever you generate; MiniMax claims no rights over outputs but places responsibility on you.

**Full prompting and operating brain: the dedicated sibling `minimax-h3` skill** (invoke by name; beside the comfyui skill on disk).
It carries the three-field prompt format, the `<d>` dialogue syntax, the camera vocabulary, the reference
labelling system, the Krea production-job taxonomy, the quant and acceleration ladder (GGUF sizes, the
larryvrh/drbaph Turbo LoRA, Spectrum, the latent upscaler) and a symptom-to-cause table. Read it before writing
an H3 prompt or picking a quant; this entry stays the node-level reference.

**Community tooling for the local path (2026-08-04).** Two custom packs matter enough to build with; both are
read from their node source, not from summaries.

- **Spectrum: forecast some solver steps instead of computing them.** `xmarre/ComfyUI-Spectrum-MiniMax-H3`
  (GPL-3.0). One node, **`SpectrumApplyMiniMaxH3`** ("Spectrum Apply MiniMax H3", category `sampling/spectrum`),
  and it is a **MODEL patcher, not a replacement sampler**: MODEL in, MODEL out, so it sits between `UNETLoader`
  and everything downstream (`BasicGuider` and `BasicScheduler` both take the patched model). The rest of the
  graph is untouched. `enabled=false` passes the model through unchanged, and `require_native_minimax_h3` throws
  if the model is not native H3, so it cannot be misapplied silently.
  - **What it really does, in the author's own numbers:** it predicts feature trajectories with a Chebyshev fit
    instead of running the transformer on some steps. Over 20 steps: **Euler runs 13 actual + 7 forecast**
    (forecasting at steps 5, 7, 9, 11, 13, 15, 17), **RES multistep / CFG++ runs 14 actual + 6 forecast**. Those
    are ~35% and ~30% fewer transformer calls. The README is careful that this is NOT the wall-clock number:
    end-to-end gain also depends on output-head cost, CPU transfers, offload, references, CFG branching, latent
    size and hardware. Treat circulating "1.5x" figures as one machine's result, not a spec.
  - **Supported samplers:** `sample_euler`, `sample_res_multistep`, `sample_res_multistep_cfg_pp`. **Ancestral
    samplers fall back to native H3 on purpose** (injected noise breaks the smooth trajectory the forecaster
    needs), and multi-GPU parallel sampling also stays native. RES additionally **keeps its last three solver
    steps native**, a floor that overrides a smaller `tail_actual_steps`.
  - **Knobs:** `blend_weight` 0.5, `degree` 4 (Chebyshev order), `ridge_lambda` 0.1, `window_size` 2.0,
    `flex_window` 0.75, `warmup_steps` 5, `tail_actual_steps` 1, `max_history` 8, `debug`, plus optional
    `history_storage` = `system_ram` (default) or `vram`. The author measured `vram` history costing **about
    2.2 GiB more peak** for a small and variable timing gain, so it is an option for spare VRAM, not a free win.
  - **Version coupling is tight, and "just update to 0.30.0" is WRONG.** It targets
    `comfy.ldm.minimax.model.MiniMaxH3Model` and needs the H3 plus packed-latent sampler APIs from ComfyUI commit
    **a post-v0.30.0 ComfyUI build, 2026-08-03 20:29 UTC** (the `latent_shapes` argument on `outer_sample`). **v0.30.0 was tagged
    that same day at 03:48 UTC, about 17 hours EARLIER, and does not contain it** (verified with a commit
    comparison: v0.30.0 is two commits behind it). As of 2026-08-06 no tagged release carries the API, so this
    pack needs a master / nightly build newer than that commit. Advice circulating as "update to 0.30.0 or newer"
    will leave you on a build that fails. Older revisions are unsupported, later ones are explicitly unverified,
    and the node checks the contract at apply time so it fails loudly rather than drifting.
  - **Honest quality note from the author:** fast action can follow a different trajectory, and fast-moving or
    briefly visible detail can degrade. Qualitative, varies with prompt, motion, sampler, resolution and refs.

- **Latent upscaler: a real two-pass at higher resolution.** `Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler` (no
  licence file). Node **`MiniMaxH3LatentUpscaleCombined`** ("MiniMax H3 Latent Upscale Combined", category
  `latent/minimax_h3`). It exists because **stock `LatentUpscaleBy` and `AddNoise` break on H3's `NestedTensor`
  AV latent** (video `[B,24,T,H/16,W/16]` packed together with audio `[B,32,2,T_audio]`); this is not a learned
  upscaler, it is spatial interpolation plus correct re-noising of that packed structure.
  - **Inputs:** `samples` (LATENT), `scale_by` (1.5 default, 0.01-8), `method` (`nearest` / `bilinear` default /
    `bicubic`), `model` (MODEL), `noise` (NOISE), `sigmas` (SIGMAS), `audio_denoise`, and optional `positive` /
    `negative` (CONDITIONING). **Outputs:** `latent`, `positive`, `negative`.
  - **Wiring, from the author's own instructions.** Split the schedule first: one `BasicScheduler` feeds a
    **`SplitSigmas`** (documented in `NODE_LIBRARY/samplers.md`), whose HIGH half goes to pass 1 and LOW half to
    both the Combined node and pass 2. Without it there is no "high" and "low" sigma set to talk about.
    `SamplerCustomAdvanced` #1 runs the high half at low resolution -> take its **`denoised_output`** (not the
    plain output) -> the Combined node, fed the same conditioning as pass 1 plus `RandomNoise`, the LOW sigmas
    and the model -> build a **new `BasicGuider` from the returned `positive` / `negative`** ->
    `SamplerCustomAdvanced` #2 with **DisableNoise**, the low sigmas and the Combined latent.
  - **`audio_denoise` is why the first reports of this node looked bad.** It defaults to **1.0**, which fully
    re-noises the audio at `sigmas[0]` so pass 2 can rewrite it. `0` locks pass-1 audio untouched; the author
    recommends **0.25 to 0.5** for light polish. The README's own troubleshooting says that if audio garbles at
    `audio_denoise>0`, **run more of the schedule in pass 1, because audio settles late**, or lower the value. A
    disappointing result at defaults is the expected outcome, not evidence the node is broken. Inferred, not
    tested here: that is the most likely cause of the poor community result, and it is cheap to check.
  - **Why the conditioning outputs matter (ref2va).** `minimax_refs` carries each reference with its own latent
    and `latent_h` / `latent_w`. Grow the target canvas 2x and references sized for the old canvas sit at the
    wrong relative scale and RoPE row layout, which is the classic identity warp. The node upscales the reference
    visual latents and their metadata together, which is why you must rebuild the guider from its outputs rather
    than reusing the pass-1 conditioning.
  - **Constraint:** MiniMax's DiT patch size is `(1, 2, 2)` and the conditioning patchify does not pad, so the
    upscaled **height and width must stay even**. Also avoid forced cache-empty or model-unload nodes between the
    two passes, especially with `--disable-dynamic-vram` plus a quantized H3 and SageAttention.

- **kijai's VRAM patch, and a name collision worth knowing.** `kijai/ComfyUI-KJNodes` ships
  **`MiniMaxH3MemoryEfficientSageAttentionPatch`** ("MiniMax H3 Mem Eff Sage Attention Patch", category
  `KJNodes/minimax`, flagged EXPERIMENTAL). Like Spectrum it is a **MODEL patcher** (MODEL in, MODEL out), so the
  two chain: it swaps a custom SageAttention into H3's self-attention on every transformer block **to cut peak
  VRAM**, where Spectrum cuts step count. It refuses to apply unless sageattention is new enough, the ComfyUI
  build supports H3, and the model really is a `MiniMaxH3Model`. This is the "kijai patch" that appears in
  community reference-to-video test configs alongside SageAttention.
  **Do not confuse it with `MiniMaxRemover`** (`zibojia/minimax-remover`), an unrelated video object-removal
  model that kijai wires in `ComfyUI-WanVideoWrapper`; grepping "minimax" in his repos hits that too.

**Community performance reports (2026-08, unverified here, treat as anecdote).** A 16 GB RTX 4090 Laptop with
32 GB RAM reportedly did 960x540, 5 s, 20 steps on pruned INT8 + NVFP4 in ~182 s; an RTX 4080 run reported
608x352, ~5.2 s at ~157 s with peak VRAM ~9.5 GiB thanks to offload plus pruned INT8. Several users report
dropping 20 steps to 15 with little visible loss. None of this was measured here, and the low VRAM peaks in
particular depend on offload settings that trade speed for memory.

- **Source (local path):** `MiniMaxAI/MiniMax-H3` model card, its `LICENSE`, and `docs/VIDEO_PROMPT_WRITING_GUIDE_{base,ref}_en.md` ;
  `Comfy-Org/MiniMax-H3` repo tree for file names and sizes ; `comfy_extras/nodes_minimax_h3.py` ; templates
  `video_minimax_h3_{t2v,i2v,r2v}.json` ; `xmarre/ComfyUI-Spectrum-MiniMax-H3` and
  `Tr1dae/ComfyUI-MiniMaxH3_LatentUpscaler` node source and READMEs.

### PixVerse
- **Prompt style:** `[Character] [Action] [Scene] with [Visual Style], [Cinematography], and [Mood]`; state camera work explicitly and chain it.
- **Structure:** character/object -> scene -> cinematography (position, movement, angle) -> style/grade -> mood -> negative prompt.
- **Strengths:** customizable camera movement/angle, follows camera + lighting words (V5.6), product multi-clip orbit.
- **Avoid:** generic prompts, visual overload, omitting style, excessive length. Negatives ARE supported (list artifacts/objects/styles to exclude).
- **Settings:** 5/8/10s; up to 1080p (720p for 10s); aspect 16:9/9:16/4:5; T2V + I2V + Effects. (Maker docs gated; verify exact knobs against PixVerse platform docs.)
- **Source:** imagine.art/blogs/pixverse-v5-prompt-guide ; docs.pollo.ai.

### Vidu (Q1 / Q2)
- **Prompt style:** `@`-label syntax to bind subjects, then action + camera in natural language: `@a(short-hair woman in red coat), @b(man in denim)` ... action ... camera.
- **Structure:** reference labels first -> action (sequential) -> camera (intentional moves); Q1 leans on keyframes.
- **Strengths:** multi-subject reference consistency (up to 7, one image each, `@a, @b...`); built-in push/pull, pan, tilt, zoom; motion-amplitude control; video extension.
- **Avoid:** thin official prompt doc; keep references high-res; fixed seed for repeatable motion. Negative support not documented.
- **Settings:** 1080p; refs JPG/PNG/WEBP (<=10MB, up to 7); motion amplitude auto/small/medium/large; aspect 16:9/9:16.
- **Source:** wavespeed.ai/docs (Vidu R2V) ; vidu.com. (Verify knobs against Vidu platform docs.)

### Pika 2.2 / 2.5
- **Prompt style:** shot-plan order - subject + material details -> one motion cue (direction + speed) -> scene/lighting -> one camera move -> style at the end; describe what IS.
- **Structure:** one motion per shot; exactly ONE camera type (zoom OR pan OR rotate OR tilt); "smooth" reduces jitter.
- **Strengths:** quick turnaround; Pikascenes (combine refs, `ingredients_mode`), Pikaframes (up to 5 keyframes) for transitions/loops.
- **Avoid:** complex multi-stage motion, stacking camera types, over-describing. Negatives ARE supported ("ugly, blurry, low quality, watermark, distorted, jittery, morphing"). Pikaffects/Pikaswaps are web-UI only.
- **Settings:** 720/1080p; 5/10s; many aspects; guidance 8-24 (def 12); motion intensity 1-4 (def 1).
- **Source:** pika.art ; docs.pika.art ; node template `pika.md`.

### Sync 3 (sync.so) - lip sync + talking image
- **What it is:** a dedicated LIP-SYNC model, not a general video generator. Two jobs: re-sync the mouth of existing footage to new speech, or bring a single still portrait to life from an audio track. Handles close-ups, profiles and partial obstructions automatically while preserving the speaker's expression. Cost scales with output duration. API / paid (Comfy Cloud or a sync.so key).
- **Prompt style:** only the Talking Image node takes text, and it is OPTIONAL guidance for how the portrait comes to life (framing, mood, small motion), not a scene description. The audio drives everything else. Lip Sync takes no prompt at all.
- **Build the graph (confirmed from `comfy_api_nodes/nodes_sync_so.py` + the official templates):**
  - **Lip sync existing footage** - `LoadVideo` -> **`SyncLipSyncNode`** ("sync.so Lip Sync") `video`, plus `LoadAudio` (or `RecordAudio`) -> its `audio`; `VIDEO` out -> `SaveVideo`. Template `api_sync_so_lip_sync_video`.
  - **Talking portrait** - `LoadImage` -> **`SyncTalkingImageNode`** ("sync.so Talking Image") `image`, plus `LoadAudio` -> its `audio`; `VIDEO` out -> `SaveVideo`. Template `api_sync_so_talking_image`. Output duration MATCHES the audio length.
- **Settings that matter:**
  - `model` = `sync-3` on both. The image input is **exclusive to sync-3**.
  - **`sync_mode`** (Lip Sync only): `bounce` (default) / `cut_off` / `loop` / `silence` / `remap` - how a duration mismatch between video and audio is resolved, and it also SETS the output length. This is the knob to reach for first when the result runs long or short.
  - Face location: `default` / `auto-detect` / `coordinates` (Lip Sync also has `auto-detect`). Pick `coordinates` and give the X / Y pixel position (plus, on Lip Sync, the video frame to locate from) when several faces are in shot and it syncs the wrong one.
  - Talking Image has an auto-downscale toggle (on by default) for images past 4K.
  - `seed` only controls whether the node re-runs; results are non-deterministic regardless of seed (the node's own tooltip says so).
- **Input limits:** video and image up to 4K (4096x2160); a CONSTANT frame rate of 24 / 25 / 30 fps works best for the source footage.
- **Avoid:** treating it as a text-to-video model (there is no scene generation); expecting seed-reproducible output; feeding variable-frame-rate footage.
- **Source:** `comfy_api_nodes/nodes_sync_so.py` (node schemas + tooltips, read on master) ; Comfy-Org/workflow_templates `api_sync_so_{lip_sync_video,talking_image}`.

### HeyGen (avatar video, talking photo, TTS, video translate)
- **What it is:** a PRESENTER / avatar stack, not a scene generator. Four jobs, one per node: drive a stock or custom avatar to speak (Avatar Video), animate any still photo of a person into a lip-synced clip (Talking Photo), synthesize speech alone (Text to Speech), or re-voice an existing spoken video into another language with the original speaker's cloned voice and re-animated mouth (Video Translate). API / paid (Comfy Cloud or a HeyGen key). Priced per second of output.
- **Prompt style:** there is NO scene prompt anywhere. The only free text is the SCRIPT the avatar speaks (or SSML, in the TTS node) and, on Create Avatar, a character DESCRIPTION. Do not write camera or lighting language; it is ignored.
- **Build the graph (confirmed from `comfy_api_nodes/nodes_heygen.py` on master + the four official templates):**
  - **Talking photo** - `LoadImage` -> **`HeyGenTalkingPhotoNode`** ("HeyGen Talking Photo") `image`; `VIDEO` out -> `SaveVideo`. Template `api_heygen_talking_photo`.
  - **Avatar presenter** - **`HeyGenAvatarVideoNode`** ("HeyGen Avatar Video") standalone; `VIDEO` out -> `SaveVideo`. To use your OWN avatar, chain **`HeyGenCreateAvatarNode`** ("HeyGen Create Avatar") first: its `avatar_id` (STRING) output -> the Avatar Video node's `custom_avatar_id`, and its `preview` (IMAGE) output -> `PreviewAny` / `SaveImage`. Template `api_heygen_avatar_video` also wires `SaveText` so the avatar_id is kept on disk, which matters because the ID is the only way to reuse that avatar later. Create Avatar is a FLAT $1.43 per call, so re-creating an avatar you failed to save is a real cost.
  - **Text to speech** - **`HeyGenTextToSpeechNode`** ("HeyGen Text to Speech", category `partner/audio/HeyGen`) standalone; `AUDIO` out -> `SaveAudioAdvanced`. Template `api_heygen_text_to_speech`.
  - **Video translate** - `LoadVideo` -> **`HeyGenVideoTranslateNode`** ("HeyGen Video Translate") `video`; `VIDEO` out -> `SaveVideo`. Template `api_heygen_video_translate`.
- **The `speech` widget is a DynamicCombo, and this is the part that trips people up.** On both Talking Photo and Avatar Video, `speech` ("speech source") switches the visible inputs: pick `script` and you get `text` (multiline, up to 5000 chars), `voice`, `custom_voice_id`, `voice_speed` (0.5-1.5); pick `audio` and you get a single `audio` AUDIO input (up to 10 minutes) and the voice widgets disappear. Feeding your own audio is how you use a voice HeyGen does not offer.
  - On Talking Photo a voice is REQUIRED in `script` mode (the node raises if none resolves). On Avatar Video it is optional, because the avatar carries a default voice; its `voice` list has an extra `(avatar's default voice)` option.
  - `custom_voice_id` overrides the `voice` combo when set. HeyGen's library is 2000+ voices, so the combos are only the curated popular subset.
- **`engine` on Avatar Video is also a DynamicCombo** and it filters the avatar list: `auto` shows every curated avatar and picks the best engine it supports (Avatar IV preferred), while `avatar_iv` / `avatar_iii` / `avatar_v` each show only the looks that support that engine. Fidelity and price go together: `avatar_iii` $0.0239-0.0619/s, `avatar_iv` $0.0715-0.0954/s, `avatar_v` $0.0954/s (flat). **Every price in this entry is read from the node's `price_badge` declaration in the schema, not from a billed run**, so treat them as what ComfyUI displays rather than as a confirmed invoice. Talking Photo is always Avatar IV at $0.0715/s. Choosing a `custom_avatar_id` whose look does not support the engine you forced raises an error naming the supported engines; `auto` avoids that.
- **Settings that matter:** `resolution` `720p` / `1080p` (default `1080p`) and `aspect_ratio` `auto` / `16:9` / `9:16` / `1:1` / `4:5` / `5:4` on both video nodes; `expressiveness` `low` / `medium` / `high` (default `low`) on Talking Photo only; `background_color` on Avatar Video takes a hex string and MUST start with `#` (`#00ff00` for a keyable green) or the node raises. Video Translate has `mode` `speed` (default, $0.0476/s) vs `precision` (better lip sync, $0.0954/s; the node's own tooltip calls it twice the price), `translate_audio_only` (swap the audio track and leave the original mouth alone), and `speaker_count` (0 = auto-detect, up to 10). TTS has `speed` 0.5-2.0 and an `ssml` boolean for pause / emphasis / pronunciation control.
- **Input limits:** images are downscaled automatically past 2000px on the long side (Talking Photo and the photo branch of Create Avatar); script text 1-5000 characters and the resulting speech must be at least 1 second; Create Avatar's prompt is up to 1000 characters with up to 3 optional reference images (`ref_image_1..3`).
- **Avoid:** expecting a scene or camera prompt to do anything; forgetting to save the `avatar_id`; setting a background colour without the leading `#`; assuming `seed` changes the result (the tooltip says outright it is not sent to HeyGen, it only forces a re-run).
- **Source:** `comfy_api_nodes/nodes_heygen.py` (node schemas, tooltips, payloads and price badges, read on master 2026-07-25) ; Comfy-Org/workflow_templates `api_heygen_{avatar_video,talking_photo,text_to_speech,video_translate}`.
