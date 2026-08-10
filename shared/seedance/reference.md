# Seedance reference: official prompting mechanics

Normative layer. Everything here is from a ByteDance primary source or read directly from ComfyUI's
node code. Third-party observations live in `supplementary.md` and never override this file.

**Two official guides, two versions.** Sections 1 to 12 are the official **Seedance 2.0 series**
guide (BytePlus ModelArk). The **Seedance 2.5 specifics** part further down is the official Dreamina
Seedance 2.5 User Guide. Where they differ, 2.5 wins for 2.5 and the difference is called out. Read the
2.5 part first if the task names 2.5.

---

## 1. Basic formulas by task type

Pick the formula from the task, because the phrasing is what tells the model which task it is.

**Multimodal reference** (extract an element, generate something new):
- Image: `Reference <Subject_N> in <Image_N> to generate...`
- Video: `Reference <Action/Camera_movement/Style/Sound_effect> in <Video_N> to generate...`
- Audio: `Reference the timbre in <Audio_N> to generate...`

**Video editing** (modify the original; anything unmentioned stays unchanged by default):
- Add: describe `<Element_Features>` + `<Timing>` + `<Location>`
- Modify: `Strictly edit <Video_N>, and modify <Original_Characteristic> in it to <New_Characteristic>`
- Delete: name what to remove, and explicitly name what must stay unchanged

**Video extension** (continue in time, keeping style, subject and narrative):
- `Extend <Video_N> forward/backward to generate...`
- Track completion: `<Video_1> + <Transition> + followed by <Video_2> + <Transition> + followed by <Video_3>`

**Combined:** `Reference [dimension] of <Image/Video_N>, strictly edit <Video_X>, [specific edits]`

> **The one-word trap.** For edit and extend, refer to the asset as `<Video_N>` directly. Writing
> "reference `<Video_N>`" gets it misidentified as a reference task.

## 2. The advanced formula

```
precise subject + action details + scene/environment + lighting & colour tone
+ camera movement + visual style + image quality + constraints
```

The model decomposes input into a **spatial layer** (what is in frame) and a **temporal layer** (how it
changes). A good prompt is an engineering instruction, not copywriting: who, in what scene, doing what,
how the camera moves, in what order events occur.

## 3. Defining subjects

`Define [Core_Subject_Features] in <Image/Video_N> as <Subject_N>`

- Use **2 to 3 clear, stable, static** features: clothing, hairstyle, appearance, category. Not mood.
- Examples: `Define the woman wearing a red dress and a straw hat in Image 1 as Subject 1`, or
  `... as Zhang Hong`.
- **Every mention must be explicit.** Two supported styles, pick one and never mix:
  - undefined subjects: repeat the binding each time, `Zhang San@Image 1`
  - predefined subjects: define once, then always use the same label ("police officer", "thief")
- Using an **Asset ID** from the asset library does not remove this: you still refer to
  `<Image/Video_N>` in the prompt, because the model cannot associate an Asset ID with content.
- Prefer expressing spatial relationships through reference images rather than long text.

## 4. Shot sequencing

Break the video into `Shot 1`, `Shot 2`, `Shot 3` in the order events occur, primary before secondary.

Each shot, in this order:
1. camera movement or transition ("slowly push in from a wide shot", "fixed camera", "cut to...")
2. subject actions and expressions
3. position or spatial change
4. audio for that shot

Official negative example: *"A man runs nervously down the street, and the scene feels very cinematic."*
Official positive example:
- Shot 1: Side shot of a street alley; the man slowly starts running, with a sense of rapid breathing.
- Shot 2: The man knocks over a fruit stand; the camera shakes quickly and gives a close-up of his frightened face.
- Shot 3: The man climbs over a low wall and disappears; the camera slowly pulls back and freezes on the empty street.

**Timing is unstable in 2.0.** The 2.0 guide states support for precise timing such as "0 to 3
seconds" is unstable and forcing durations may produce abnormal results, so do not impose per-shot
seconds on 2.0. **This reversed in 2.5**, where timestamps are a headline feature: see 2.5-C.

## 5. Action description

- **Refine to body parts** (hands, legs, head, shoulders, back) and quantify range, speed and force:
  "slowly raise a hand", "quickly turn the head", "slightly lower the head".
- **Prefer slow, gentle, continuous small movements.** Avoid sprints, big jumps, violent rolls.
- **Supply the transition between actions:** "use the inertia of turning around to naturally raise a hand".
- **Externalise emotion into physical detail** rather than naming it:

| Abstract emotion | Write instead |
|---|---|
| Sadness | lowering the head, shoulders trembling slightly, eyes reddening, fingers clutching the corner of clothing |
| Joy | corners of the mouth rising, brows relaxing, steps becoming light, unconsciously humming |
| Nervousness | checking the watch, fingers tapping the tabletop, rapid breathing, eyes darting away |
| Anger | fists clenched, jawline tense, chest heaving, squeezing words out through gritted teeth |
| Relief | letting out a long breath, shoulders relaxing, a faint smile, looking up toward the distance |

## 6. Camera

Standard terminology is understood directly: medium shot, close-up, wide shot, slow push-in, smooth
lateral tracking, fixed shot.

**One camera movement per shot.** Requesting push, pull, pan and move together increases instability.

## 7. Quality, style, constraints

- **Quality:** HD, rich details, cinematic texture, natural colours, soft lighting
- **Style:** name it, e.g. cyberpunk cool blue-purple tone, retro film, fresh Japanese style
- **Constraints** matter and are not optional garnish:
  - subtitles: "keep it subtitle-free", "avoid generating any text or subtitles"
  - logo: "do not generate a logo"
  - watermark: "do not generate a watermark"

## 8. Symbols

| Content | Symbol | Example |
|---|---|---|
| Music | `（）` | `（fast-paced rock music is playing in the background）` |
| Sound effect | `<>` | `<dog barking can be heard in the distance>` |
| Dialogue | `{}` | `{Hello, world}` |
| Subtitles | `【】` | `【Chapter One: Departure】` |

Dialogue language must be consistent; avoid mixing Chinese and English except proper nouns. A less
common language must be named: `says in Japanese {こんにちは}`.

## 9. Asset configuration

Four functional roles: **character anchoring**, **scene tone-setting**, **camera-movement reference**,
**rhythmic atmosphere** (audio).

Official recommendation: **4 to 5 assets total** = 1-2 character images (facial close-up plus full body)
+ 1 scene image + 1 camera-movement video + 1 audio clip.

> **Do not use the full asset limit.** Too many assets make feature priority ambiguous, causing style
> conflicts, blurry subject identification and results that drift from intent.

Place assets needing the most precise reference **earliest in the prompt**.

## 10. Failure modes and fixes

| Symptom | Root cause | Fix |
|---|---|---|
| Face drifts / swaps mid-video, may resemble a celebrity and get blocked in review | Face reference diluted: mixed reference image, or face occupies too small a share of the frame | Add a dedicated **headshot** (head only, neutral expression, minimal background). In the prompt: `<Subject 1> facial features reference image 1 (headshot), makeup and styling reference image 2 (full-body photo)`. Put it first. **Never use multi-view / three-view character sheets** - the model reads the angles as different people and drift gets worse |
| Duplicated characters ("twins") in one frame | Subjects not clearly bound to images; multi-view sheets | Mark each character to its image consistently: `Zhang San (corresponding to image 1) throws ... toward Li Si (corresponding to image 2)`. Add a global tail constraint forbidding identical appearance and duplicate avatars. **Cannot be eliminated 100%**, only made less likely |
| Subtitles appear unasked | - | Add explicit "keep it subtitle-free". Remove text from reference assets first. Prefer **landscape**: subtitle probability is significantly lower than portrait. **Cannot be eliminated 100%** |
| Foreign logo or watermark | - | Explicit "do not generate watermarks" / "do not generate Logos" |
| Style drifts to live action | Reference image is realistic and the prompt does not state style | State style explicitly ("2D Japanese anime style", "3D Chinese-style comic"). Better: restyle the reference image first |
| Jump or rollback at an extension seam | Model limitation, to be fixed in future iterations | Post-production: trim **6 frames off the end** of the earlier clip and **1 frame off the start** of the next, at every join. Even then slight jumps remain, so prefer ending a generated segment on a transition cut and starting the next from the new scene |

## 11. Extension versus stitching

- **Continuous long take (extension):** single-scene dialogue, emotional progression, movement along one
  path. Immersive, coherent.
- **Segmented stitching:** plot turns, fast action, chases, fights, montages. Generate independently, cut together.
- Production practice combines both: extend for the conversation, stitch empty shots and transitions around it.

## 12. Text generation

Supported for common text: ad slogans, subtitles, speech bubbles. Colour, style, appearance method,
timing and position can be specified. Prefer common characters; avoid rare characters and special symbols.

---

# Seedance 2.5 specifics (official Dreamina User Guide, read 2026-08-02)

Source: 【Dreamina】Seedance 2.5 User Guide, ByteDance, last modified 2026-07-31, read in full. This section
supersedes the 2.0-series guidance above wherever they differ.

## 2.5-A. Hard limits

| | 2.0 | **2.5** |
|---|---|---|
| Images per request | 0 to 9 | **30** (jpeg, png, webp, bmp, tiff, gif, heic, heif; ratio 0.4 to 2.5; 300 to 6000 px; under 30 MB each) |
| Videos | up to 3, single 2 to 15s, total 15s | **up to 10, single 2 to 30s, total 30s** (mp4/mov, 480p to 4k, under 200 MB, fps 24 to 60) |
| Audio | up to 3, single 2 to 15s, total 15s | **up to 10, single 2 to 30s, total 30s** (wav, mp3, under 15 MB) |
| Audio-only input | **not allowed**, needed at least one image or video | **allowed** |
| Generation duration | -1 and [4, 15], 97 to 361 frames | **-1 and [4, 30], 97 to 721 frames** |
| Output resolution | 480p, 720p | **480p, 720p** |

**Output is 480p or 720p.** Third-party claims of native 4K are wrong; 4K appears only as an accepted
*input* image resolution.

**Official stability guidance, which is about subject COUNT and contradicts "more references is better":**

| Question | Official answer |
|---|---|
| Subjects in audio and video refs | 1-5 works well; 6-10 possible but stability drops |
| Subjects in a subject image | 1-8 works well; 9-12 possible but stability drops |
| Single-view or multi-view refs | 1-5 subjects: either works. Above 5: single view is more stable. If you need several views, **split them into separate images** rather than one image containing multiple views. Stated ranking: multiple images multi-view beats single image multi-view |
| Length of a main audio or video ref | 5-10s works best; longer drops stability |
| Video length for editing | best under 20s |
| Reference images for video editing | 1-5 best; 6-8 possible, less stable |

## 2.5-B. The 2.5 prompt formula

```
Complete prompt = [creatives description] + [one-sentence summary]
                + [specific plot description] + [overall supplement (ending)]
```

- **Creatives description:** creative number **in upload order** + what each one is for
  (character / timbre / action / scene). Skip if you uploaded nothing.
- **One-sentence summary:** Subject + Location + Event + Theme/Style + Special camera movement.
- **Specific plot description:** a timeline or storyline. Each storyboard or time slice carries a
  **positive** part (picture content + camera movement + action + dialogue + sound effects) and a
  **reverse** part (unwanted elements, for example "no subtitles", "no bgm").
- **Overall supplement (ending):** repeat what must hold for the whole video, such as camera position +
  environment + overall sound and atmosphere + lighting. Global prohibitions go here too.

**Label forms seen in the official 2.5 examples:** `@image1`, `@image2` (lowercase, no space) and
`@Figure 1`. Combined with the 2.0 guide's `@Image 1`, there is **no single canonical spelling**. Do not
build a parser around one form. The guide does say: **you may @ the same asset several times through the
prompt, and doing so is more accurate.**

## 2.5-C. Timestamps, the feature that reversed the 2.0 advice

2.0 said precise timing was unstable. 2.5 shipped timestamp control **because users asked for exactly
that**, quoting the guide: "making the character turn in the third second". It is a headline feature.

Syntax from the official worked example:

```
0s-3s: A red-crowned crane stands quietly in the shallow water ... The morning breeze blows, and
       sunlight slants in from the horizon, creating a Tyndall effect.
3s-8s: The crane leaps lightly on the water, its feet alternately tapping the surface ...
```

Time-slice formula: `[start seconds - end seconds] + [core phase or theme]`, then physical instructions
(scene + composition + character detail action), then the emotional or camera-scheduling explanation of why.

## 2.5-D. The 30-second long-video formula, three modules

1. **Multimodal reference layer.** `Based on the uploaded [type], strictly keep [...] consistent,
   strictly lock [...]`. Official example: keep the character's face consistent per `@Figure 1`, keep the
   composition and spatial relationship per `@Figure 2`, and lock the character's position.
2. **Global settings (worldview plus anti-collapse):** `[basic environment and texture] + [visual style]
   + [shot language] + [character modelling] + [performance core] + [prohibited]`. The prohibited slot is
   where sound, subtitle, behaviour and known-fragile items go, for example "prohibit large body
   movements, prohibit extra lines or BGM, prohibit subtitles".
3. **Timestamp script storyboard:** cut the video into slices per 2.5-C.

**Super-long video (30 to 180s)** uses the same shape plus a **global parameters** block at the front:
restate the target duration and the aspect ratio in the prompt itself, because the run is long.

## 2.5-E. Modes, and which to use

- **Omni Reference** is the default multimodal mode.
- **Long Video** generates **30 to 180 seconds in one shot**, no segmenting or extending needed. Set
  duration with the clock icon.
- **Extend Video** accepts only videos **under 30s**. One operation adds **4 to 30s**. It nests: keep
  extending while the result stays under 30s. **Extreme case: a 30s original extended by 30s gives 60s,
  and that is the ceiling for this path.** The prompt applies only to the newly added tail, the original
  footage is retained untouched.
- **Smart Edit / Edit with marks / Video Editing** are text-described edits; after uploading a local
  video you also get marquee, arrow and anchor-point marking, plus a timestamp selector.
- **First and Last Frames**.

## 2.5-F. Extension prompt vocabulary

Required words: **forward extension**, **backward extension**, **continuation**.

- **Seamless continuation:** add "require natural extension, smooth movement connection, natural movement
  connection, prohibit rigid cutting of the shot, prohibit objects appearing out of thin air".
- **Cut or transition:** `cut setting = [transition type guide] + [basic constraint requirements] +
  [cut logic requirements]`. You may also list candidate transitions and let the model choose, for
  example "choose the most suitable from natural shot switching, mask transition, ink transition,
  similar object transition".

## 2.5-G. Real-person character formula

```
Character = [Age/Race] + [Skin colour/texture] + [Facial details] + [Eyes/Soul]
          + [Hairstyle/Hair colour] + [Clothing/texture] + [Body type/emotion/temperament] + [other]
```

Sub-formulas that matter:
- **Age/Race:** `[specific age] + [nationality or race] + [style adjective] + [face-shape noun]`
- **Skin:** `[cool or warm tone] + [skin-tone noun] + [texture adjective] + a forced-fidelity suffix`,
  literally "retaining the true micro pores and skin texture". This is the official anti-plastic trick,
  and freckles or blemishes can be added to push it further.
- **Facial details:** at least 3 to 4 of eye shape, brow bone, nose bridge, lip shape, jawline.
- **Eyes/Soul:** `[eye adjective] + [what the gaze conveys] + [underlying emotion]`.
- **Hair:** colour + condition/texture + hairstyle noun + environmental interaction (wind, mess).
- **Clothing:** pattern/cut + colour + garment noun + fabric and wear state + how it is worn.
- **Body/temperament:** skeleton and shoulders + composition and shot + action and gaze + atmosphere.
  Drop the composition and action parts if the plot section already covers them.

## 2.5-H. What 2.5 fixed, so the 2.0 failure table is partly stale

Officially claimed fixed or greatly improved in 2.5:
- **random subtitles and irrelevant BGM** - the 2.0 workarounds still help but the base is much better
- **"twins" and face-swap dislocation** in multi-person scenes, via the multi-person reference upgrade
- **AI-look and distortion on complex shots**, plus cut-to-cut consistency
- **extension continuity**

New abilities: BGM separation and removal by prompt, creativity transfer rather than only motion
transfer, partial object removal and re-editing, spatial perspective modification, timbre reference,
seamless green-screen editing, **Clay Renderer (white model) control**, seamless transition between two
supplied videos, and multi-grid storyboard input (simple line drawings or stick figures recommended).

**Clay Renderer is the Blender path.** There is an official **Maya / Blender Dreamina plugin**: set the
camera route in your DCC, export the white-model video, upload it through the plugin, and Seedance
references the white-model action and camera movement for the final render. ByteDance publishes a
separate Clay Renderer Plugin User Guide.

## 2.5-I. Language support

Priority-optimised: Chinese, English, Spanish, Indonesian, Malay. Fully covered: Thai, Arabic,
Portuguese, Vietnamese, Japanese, Korean. Translating into Chinese or English first is no longer needed.

---

## Seedance in ComfyUI (read from node source, re-read 2026-08-09)

`comfy_api_nodes/nodes_bytedance.py` on master.

**Seedance 2.5 shipped on 2026-08-08** (core v0.31.0, PR 15395). The 2026-08-01 reading of this file
said "Seedance 2.5 has no node", which was true then and is wrong now; it is corrected here rather
than deleted. 2.5 is an option on the existing `ByteDance2*` nodes, model id
`dreamina-seedance-2-5-260628`.

| Node | Display name | 2.5 specifics |
|---|---|---|
| `ByteDance2TextToVideoNode` | ByteDance Seedance 2.5 Text to Video | prompt, resolution, ratio, duration, generate_audio, output_format |
| `ByteDance2FirstLastFrameNode` | ByteDance Seedance 2.5 First-Last-Frame to Video | same minus `ratio`; adds `first_frame` / `last_frame` IMAGE and `first_frame_asset_id` / `last_frame_asset_id` STRING (mutually exclusive with the image inputs) |
| `ByteDance2ReferenceNode` | ByteDance Seedance 2.5 Reference to Video | adds `video_editing`, autogrow `reference_images` (image_1..30), `reference_videos` (video_1..10), `reference_audios` (audio_1..10), `auto_downscale` (on), `auto_upscale` (off) |

| 2.5 parameter | Values |
|---|---|
| `resolution` | **480p, 720p only** (1080p and 4k are 2.0-only) |
| `ratio` | 16:9, 4:3, 1:1, 3:4, 9:16, 21:9, adaptive (default 16:9) |
| `duration` | 4 to 30 s slider, default 5 |
| `generate_audio` | default true |
| `output_format` | **mp4 only**, despite a model tooltip that says "mp4/mov" |

Node-level prompting rule, verbatim from the `prompt` tooltip: put spoken lines in double quotes to
steer the generated dialogue.

**Seedance 1.5 Pro** (`seedance-1-5-pro-251215`) appears in `ByteDanceTextToVideoNode`,
`ByteDanceImageToVideoNode` and `ByteDanceFirstLastFrameNode`.

| Parameter | Values |
|---|---|
| `resolution` | `480p`, `720p`, `1080p` |
| `aspect_ratio` | `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9` |
| `duration` | slider 3 to 12s, default 5 |
| `generate_audio` | **honoured only for 1.5 Pro**; ignored on every other model in these nodes |
| `camera_fixed` | the platform appends a fix-camera instruction to your prompt and **does not guarantee the effect** |
| `watermark` | adds an "AI generated" watermark |

Three hard facts you will not find in any prompt guide:

1. **Minimum duration for 1.5 Pro is 4 seconds.** The node raises
   `ValueError("Minimum supported duration for Seedance 1.5 Pro is 4 seconds.")` below that, even though
   the slider allows 3.
2. **`generate_audio` doubles the price.** The price badge applies a 2x multiplier for 1.5 Pro with audio.
   Cost per 10s: 480p $0.12, 720p $0.26, 1080p $0.58 to $0.59, scaled linearly by `duration / 10`.
3. **The node rejects parameters written into the prompt text.** `raise_if_text_params` blocks
   `resolution`, `ratio`, `duration`, `seed`, `camerafixed`, `watermark` appearing as text. Set them on
   the widgets, not in the prose.

**Seedance 2.0 family** uses different nodes: `ByteDance2TextToVideoNode`, `ByteDance2FirstLastFrameNode`,
`ByteDance2ReferenceNode`, with `Seedance 2.0`, `Seedance 2.0 Mini` and `Seedance 2.0 Fast` selectable.
Asset helpers: `ByteDanceCreateImageAsset`, `ByteDanceCreateVideoAsset`.

---

## Confirmed versus inferred

**Confirmed, primary:**
- Every formula, symbol, failure mode and asset rule in sections 1 to 12: official BytePlus ModelArk
  "Dreamina Seedance 2.0 series prompt guide", read in full 2026-08-01.
- **[2.5]** Launch 2026-07-31 on Jimeng AI and Doubao Pro, API "coming" on BytePlus ModelArk; up to
  **30 images, 10 video clips, 10 audio clips** in a single pass; up to **30 seconds** per generation
  with multi-round extensions, extended from 15s: official ByteDance Seed blog.
- **[2.5]** Omni reference mode, `@` tags to link assets, standard render up to 30s, extended beta mode
  5 to 180s, interpolation 24 to 30/60 fps as a **post-production tool** (not native fps), multiframes up
  to 10 reference frames: Dreamina official product guide.
- All ComfyUI parameters, guards and prices above: read from node source.

**Not confirmed, do not state as fact:**
- That the 2.0 prompting mechanics apply unchanged to 2.5. Likely, visibly inherited, but no public 2.5
  prompting guide exists yet.
- `@Audio` and `@Video` label syntax **for 2.5 specifically**. The spaced `@Image 1` / `@Video 1` /
  `@Audio 1` forms are confirmed in the official 2.0 guide's examples; Dreamina's 2.5 page shows only
  `@Image` style without a space.
- Native resolution, fps, aspect-ratio list, tiers or pricing for 2.5. Not published.
- Any "timestamp-level editing" mechanic beyond the phrase itself.
- Any post-launch hands-on failure report for 2.5. None found in accessible sources.

**Known gaps, blocked by login:** the official Lark wiki and prompt doc
(`bytedance.larkoffice.com/wiki/NjnWwvf4BiFYFLk2RzrcEgaunGf`,
`bytedance.larkoffice.com/docx/A88jd0B47oAd8zxWp5ycZFMfnxh`) both 302 to a login page. The community
Feishu wiki reportedly holds a MiniMax H3 comparison, a Blender workflow and a long-video guide. Five
`mp.weixin.qq.com` articles returned Internal Error. None of this is in the skill.
