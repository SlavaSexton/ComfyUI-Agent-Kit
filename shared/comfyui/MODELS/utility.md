# Enhancement and utility (NOT prompt-driven)

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 2 entries for this family.


These are not text-prompted generators. They take an existing image/video, or run inside a graph, and improve or
analyze it. They need the right SETTINGS and inputs, not a prompt recipe. Use them as pipeline steps (e.g. a final
upscale on a hero, frame interpolation on a clip, a depth map to drive ControlNet).

### Upscale, restore, interpolation

- **Real-ESRGAN / ESRGAN family** (upscale): GAN super-resolution, deterministic and fast; one pass that enlarges
  (2x/4x) and removes compression/blur. Use for a final 2x/4x on a good image or per-frame on video (detail
  preserved, not hallucinated). ComfyUI: `UpscaleModelLoader` -> `ImageUpscaleWithModel`; scale is baked into the
  model file (RealESRGAN_x2/x4plus, 4x-UltraSharp = 4x); add an ImageScale downsample for non-native targets.
  Source: github.com/xinntao/Real-ESRGAN, OpenModelDB.
- **SUPIR** (diffusion restore/upscale): SDXL-based, regenerates plausible high-frequency detail, optional caption.
  Use on heavily degraded/low-res photos where ESRGAN stays soft; heavier/slower, a quality pass not a bulk step.
  Settings: scale_by, ~30-45 steps, cfg, denoise, s_churn/s_noise; v0Q (quality) vs v0F (light degradation,
  faithful); ~10GB (512->1024) to 24GB (~3072px), FP8 + VAE tiling cuts VRAM. LICENSE: the SUPIR weights are
  NON-COMMERCIAL (XPixel Group); do not use in a commercial pipeline. Source: github.com/kijai/ComfyUI-SUPIR.
- **SeedVR2** (video/image upscale+restore): one-step diffusion with temporal consistency (frames denoised
  together). Target the short edge (default 1080); 3B (fast) vs 7B (quality); FP16/FP8/GGUF; batch follows the
  4n+1 rule (1,5,9,13,17,21...); ~8GB to 24GB+. Source: github.com/numz/ComfyUI-SeedVR2_VideoUpscaler.
- **FlashVSR** (video super-res): one-step streaming diffusion, ~17 FPS at 768x1408 on an A100; designed for 4x SR
  (use 4x for best stability); V1.1 recommended. CAVEAT: needs the Block-Sparse Attention (LCSA) module
  (`mit-han-lab/Block-Sparse-Attention`, a compile-and-install dependency, memory-intensive at build time); without it
  ComfyUI and other third-party implementations fall back to DENSE attention with noticeable quality degradation at
  higher resolutions (the card calls out early ComfyUI versions as affected). GPU compatibility confirmed on A100/A800;
  H200 (Hopper) also runs per the card (limited acceleration); RTX 40/50 and H800 currently unknown. Source: huggingface.co/JunhaoZhuang/FlashVSR. **ComfyUI build:** runs through kijai `ComfyUI-WanVideoWrapper` (FlashVSR is a supported family there) - see KIJAI.md for the WanVideoWrapper loader / sampler nodes. (`OHLIA/flashvsr_mix_gui` is a standalone GUI, not a node pack.)
- **Z-Image-Turbo Fun-ControlNet-Tile** (diffusion tile SR): ControlNet-Tile super-res for the Z-Image-Turbo stack,
  trained to 2048x2048, 8-step distilled; tiled so structure holds while enlarging. Reuses the Z-Image loader
  (8 steps, low CFG), so no separate SR model stack. This is the IDENTITY-FAITHFUL path: unlike the Union
  controlnet-locked img2img refine (which regenerates a real subject's face at denoise 0.4+), the Tile model
  enlarges without reinterpreting. See the Z-Image-Turbo entry above. Source:
  huggingface.co/alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1.
- **Topaz** (external API): commercial upscale/denoise/sharpen + frame interpolation via Topaz's API (built-in
  `TopazVideoEnhance` node). Upscale models Starlight (Astra) Fast/Creative + Starlight Precise 2.5; interpolation 15-240 fps, slow-mo 1-16x; needs a license.
  Source: docs.comfy.org/built-in-nodes/TopazVideoEnhance.
- **Magnific** (external API): cloud creative upscaler/enhancer (Freepik) up to 16K with prompt + creativity
  controls; no first-party ComfyUI node (HTTP/SDK or community wrapper). Scale 2x/4x/8x/16x. Source: docs.magnific.com.
- **FILM** (frame interpolation): Google, handles large motion; accepts as few as 2 frames, arbitrary multipliers.
  Use for slow-mo / fps boost with large motion. ComfyUI: FILM VFI node (multiplier, clear_cache_after_n_frames).
  Source: github.com/google-research/frame-interpolation.
- **RIFE** (frame interpolation): fast optical-flow interpolation, the default speed-first choice (e.g. 16->32/60
  fps over many frames). ComfyUI: RIFE VFI node (ckpt rife47/rife49, multiplier, ensemble). Source: github.com/hzwer/Practical-RIFE.

**Picking an upscaler + ordering a restore chain** (general practice, not tool-specific). Choose by content, not
only by scale: a GAN (Real-ESRGAN) is fast and faithful for photoreal footage, but x4 can look plastic on skin and
fine fabric, so x2 is the safer pore-preserving pass; a diffusion upscaler (FlashVSR / SeedVR2 / SUPIR) handles
stylized, anime, line-art, and AI-generated frames better and regenerates detail instead of only sharpening. Rough
rule: source under ~540p or big jumps -> 4x GAN; 720p+ cleanup -> 2x GAN; animated / AI-gen -> diffusion. ORDER
matters in a restore chain: denoise FIRST (4x grain becomes 4x larger grain, and noise turns into per-frame
flicker), then deinterlace (QTGMC / yadif) and deblock if the source is heavily compressed, THEN upscale, and
color-grade AFTER (more headroom). Stabilize on the original, not at 4x. Do not run x2 twice to fake x4 (it stacks
artifacts), and do not expect an upscaler to deblur, it reconstructs detail, not motion. Cheap generation path:
make it small, then upscale the keeper (e.g. LTX-2.3 at 512 -> Real-ESRGAN x4 -> ~2048).

### Segmentation, depth, pose, conditioning

- **SAM3** (segmentation): detects/segments/tracks every instance matching a text noun phrase or visual prompt,
  across images and video. Use to isolate subjects -> mask for inpaint/background-swap/compositing, or track an
  object through a clip. Outputs masks, boxes, scores, per-object IDs. Source: github.com/facebookresearch/sam3.
- **BiRefNet** (matting): high-res foreground mask with hair-level edges. Use for clean cutouts/background
  replacement when you need sharper edges than a coarse segmenter. Variants general/portrait/matting/HR (up to
  2048x2048). Source: github.com/ZhengPeng7/BiRefNet.
- **High-detail matting (hair / fur / semi-transparent / motion blur)** is a multi-stage VFX task, not one node:
  coarse select (SAM3 / BiRefNet) -> trimap -> alpha matte (ViTMatte / SDMatte / Matte-Anything) -> edge refine
  (LayerStyle `MaskEdgeUltraDetailV2`); for video use a temporal model (MatAnyone2, needs a SAM2/SAM3/SeC keyframe
  mask; or RVM for clean humans). Full recipe, tool table, ready-template pointer, and license flags in
  [`ADVANCED.md`](../../docs/ADVANCED.md).
- **Depth Anything V2 / V3** (depth/geometry): per-pixel relative depth from one image (V2); V3 adds consistent
  depth + geometry + camera pose across multi-view/video and can export point clouds. Use to make a depth map to
  drive a depth ControlNet, parallax, or masking. Source: github.com/DepthAnything/Depth-Anything-V2 ;
  github.com/ByteDance-Seed/Depth-Anything-3.
- **DWPose** (pose): whole-body 2D keypoints (18 body, 21/hand, 68 face) as a skeleton; a more accurate OpenPose
  replacement to drive a pose ControlNet. Source: github.com/IDEA-Research/DWPose.
- **MoGe** (geometry): monocular point map + depth + normals in one pass from a single photo, for 3D-aware
  conditioning/reconstruction beyond a flat depth map. MoGe-2 adds metric scale. Source: github.com/microsoft/MoGe.
- **IP-Adapter** (conditioning): ~22M adapter that lets a diffusion model take an IMAGE as a prompt (decoupled
  cross-attention). Use to transfer style/subject/face from a reference without text; stack with ControlNet.
  Variants base / Plus / Face / FaceID; main knob is conditioning weight. Source: github.com/tencent-ailab/IP-Adapter.
- **LivePortrait** (portrait animation): drives a still portrait with a driving video's motion/expression (stitching
  + eye/lip retargeting). Use to animate one portrait without per-subject training. Source: github.com/KlingAIResearch/LivePortrait.
- **Mediapipe** (landmarks): fast on-device face (478) / hand (21) / pose (33) landmarks (Holistic combines all).
  Use for lightweight keypoints for conditioning/masking/alignment. Source: ai.google.dev/edge/mediapipe.
- **VOID** (video inpainting / object removal): Netflix open-source; removes a subject plus its shadows, reflections,
  and the motion it caused. Control is a 4-value greyscale "quadmask" (remove / overlap / physically-affected / keep),
  NOT a binary mask or text prompt. Two passes: Pass 1 base, Pass 2 optical-flow refinement for longer/textured clips.
  Source: docs.comfy.org/tutorials/utility/void-video-inpainting. **ComfyUI build:** the linked tutorial IS the official Comfy-Org template - open it for the quadmask input node and the two-pass (generate + optical-flow refine) graph.
- **Qwen3-VL TextGenerate** (in-graph local VLM, NOT an image/video model): a `TextGenerate` node fed by `CLIPLoader(qwen3vl_4b_fp8_scaled.safetensors)` runs Qwen3-VL locally to generate text from a prompt + optional `image` / `video` / `audio` input. Use it in-graph for captioning, VQA, or prompt generation / rewriting with no API call. Params: `max_tokens` (def 512), `temperature` 0.7, `top_k` 64, `top_p` 0.95. Template `llm_qwen3vl_text_gen.json`; weights `Comfy-Org/Qwen3-VL` (Apache-2.0). The local, no-cost counterpart to the in-graph Claude / API prompt nodes.
