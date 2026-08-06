# 3D models

Part of the kit's per-model prompting reference. The routing table and the auto-pull rule live in
[`MODELS.md`](../MODELS.md); this file holds the 4 entries for this family.


### Hunyuan3D (Tencent)
- **Prompt style:** subject supplied mainly as a clean input image (single or multi-view, background removed); text is secondary.
- **Structure:** two stages - Hunyuan3D-DiT geometry, then Hunyuan3D-Paint textures/PBR; use `Hunyuan3Dv2Conditioning` (single) or `...MultiView`.
- **Strengths:** strong geometry from images, multi-view input, high-res PBR textures.
- **Avoid:** cluttered/un-preprocessed input images; native ComfyUI gives geometry only on `2mv`.
- **Settings:** output `.glb` to ComfyUI/output/mesh; turbo workflow CFG/Flux-Guidance ~1.0; VRAM Mini 5GB / Standard 6GB geometry / 12GB with texture.
- **Source:** docs.comfy.org/tutorials/3d/hunyuan3D-2.

### Tripo
- **Prompt style:** "Subject + Detail Description + Style Definition" ("A futuristic cybernetic helmet, matte black finish, glowing blue neon strips, high detail, sci-fi style"); concrete geometry/materials/finishes.
- **Structure:** main subject + features clearly; prioritize materials over lighting.
- **Strengths:** material/texture fidelity, multi-view fusion, smart retopology; texture on/off, face-limit budget.
- **Avoid:** abstract adjectives, over-long prompts, cluttered/off-center input images.
- **Settings:** texture on/off; `face_limit`; image input JPG/PNG/WEBP <5MB, solid background, centered.
- **ComfyUI node:** `VAST-AI-Research/ComfyUI-Tripo` (Comfy Registry: `comfyui-tripo`); key nodes `TripoAPIDraft` (text/image -> draft mesh), `TripoTextureModel`, `TripoRefineModel`; needs a Tripo API key.
- **Source:** tripo3d.ai/blog/text-to-3d-prompt-engineering.

### Rodin (Hyper3D)
- **Prompt style:** specific detailed object description; name materials/textures, include lighting, state style, give context; image upload switches to Image-to-3D.
- **Strengths:** geometry quality (Gen-2), quad meshes, HD/4K textures, PBR/Shaded/All material modes, broad export.
- **Avoid:** vague prompts; cluttered backgrounds / low-res inputs (>=512x512, <=16MB); download links expire ~10 min.
- **Settings:** topology Raw or Quad (def Quad); materials PBR/Shaded/All; quality tiers; formats GLB/USDZ/FBX/OBJ/STL; up to 5 images.
- **ComfyUI node:** `DeemosTech/ComfyUI-Rodin`; key nodes `mLoadRodinAPIKEY` + `mRodin3D_Gen2` (text/image -> 3D mesh, GLB); needs a Hyper3D API key.
- **Source:** github.com/DeemosTech/rodin3d-skills ; developer.hyper3d.ai.

### Meshy
- **Prompt style:** Subject + Modifiers (materials, colors, details) + Style; 3-6 concrete physical details; reference anchors; style keywords (low-poly, photorealistic, cartoon, cyberpunk neon, anime cell shading).
- **Structure:** one object, not a scene; add "T-Pose" to characters you plan to rig.
- **Strengths:** style range, character/rigging support, iterative refine; prompts up to 800 chars, any language.
- **Avoid:** describing whole scenes; evaluative adjectives. Negatives ARE supported (`negative_prompt`). Iterate (Generate -> Refine -> Adjust).
- **ComfyUI node:** community `Kazama-Suichiku/ComfyUI-Meshy` (needs a Meshy API key); or call the Meshy REST API via a Python node.
- **Source:** help.meshy.ai (best practices) ; docs.meshy.ai/en/api/text-to-3d.

---
