# Training nodes: LoRA training and dataset preparation, in core

The nodes that let a graph **make** a model rather than only prompt one. I/O read from
`comfy_extras/nodes_train.py` and `comfy_extras/nodes_dataset.py` on master, **2026-08-06**, not confirmed with
`get_node_info` (the dataset half is not in a tagged release yet). Query `/object_info` on your own build before
wiring, and treat sockets below as CURATED, not LIVE.

**Status split, check before promising anything:**
- `nodes_train.py` (`TrainLoraNode`, `SaveLoRA`, `LossGraphNode`, `LoraModelLoader`) is in **released core**.
- `nodes_dataset.py` (16 nodes) is **master only** as of 2026-08-06. On a tagged build the trainer exists but
  the data-prep layer does not, and you feed it latents some other way.

## The whole chain, end to end

```
LoadImageTextDataSetFromFolder  ->  MakeTrainingDataset  ->  ResolutionBucket  ->  TrainLoraNode
        (images + texts)              (+ vae, + clip)         (regroup by aspect)      |
                                             |                                        +-> SaveLoRA
                                    SaveTrainingDataset / LoadTrainingDataset          +-> LossGraphNode
                                    (persist the prepared pair, skip re-encoding)
```

The pair that flows through the middle is always **`LATENT` + `CONDITIONING`**: images are VAE-encoded and
captions are CLIP-encoded once, up front, so training never re-encodes.

---

## TrainLoraNode  (display: "Train LoRA")
- **category:** `model/training` | **purpose:** train a LoRA in-graph against a prepared dataset.
- **inputs:** `model` (MODEL), `latents` (LATENT, the encoded images), `positive` (CONDITIONING, the encoded
  captions), `batch_size` (INT), `grad_accumulation_steps` (INT), `steps` (INT), `learning_rate` (FLOAT),
  `rank` (INT), `optimizer` (combo).
- **outputs:** the trained `lora`, a `loss_map`, and `steps`.
- **placement:** the end of the dataset chain. Feed its `lora` to `SaveLoRA` and its `loss_map` to
  `LossGraphNode` in the same run, otherwise the run leaves nothing behind.
- **gotchas:** `grad_accumulation_steps` is the lever when `batch_size` will not fit in VRAM: accumulate over
  several small batches instead of raising the batch. `rank` drives both capacity and output file size.

## SaveLoRA  (display: "Save LoRA Weights")
- **category:** `model/merging` | **purpose:** write the trained LoRA to disk.
- **inputs:** the lora, `prefix` (STRING), `steps` (INT), `filename_prefix` (STRING).
- **placement:** directly after `TrainLoraNode`. Without it the training run is discarded when the graph ends.

## LossGraphNode  (display: "Plot Loss Graph")
- **category:** `model/training` | **purpose:** render the `loss_map` as a plot so divergence is visible rather
  than guessed at.
- **inputs:** the loss map, `filename_prefix` (STRING).
- **placement:** a leaf off `TrainLoraNode`. Cheap, and the only feedback the graph gives you about whether the
  run was learning or thrashing.

## LoraModelLoader  (display: "Load LoRA Model")
- **category:** `model/loaders` | **purpose:** load a LoRA back onto a model.
- **inputs:** `model` (MODEL), `strength_model` (FLOAT), `bypass` (BOOLEAN) | **outputs:** MODEL.
- **placement:** the inference side, to test what you just trained in the same session.

---

## MakeTrainingDataset  (display: "Make Training Dataset")
- **category:** `model/training` | **purpose:** turn raw images plus captions into the encoded pair the trainer
  consumes.
- **inputs:** `images` (IMAGE), `vae` (VAE), `clip` (CLIP), `texts` (STRING).
- **outputs:** `LATENT` + `CONDITIONING`.
- **placement:** immediately after a dataset loader. This is the node that makes the VAE and CLIP choice part of
  the dataset: encode with the same VAE and text encoder the target model uses, or you train against a
  representation the model does not share.

## ResolutionBucket  (display: "Resolution Bucket")
- **category:** `model/training` | **purpose:** the classic multi-aspect bucketing step.
- **inputs:** `latents` (LATENT), `conditioning` (CONDITIONING) | **outputs:** the same pair, regrouped.
- **placement:** between `MakeTrainingDataset` and `TrainLoraNode`. Skip it on a mixed-aspect set and everything
  gets squeezed toward one shape, which is a slow way to teach the model your crop rather than your subject.

## SaveTrainingDataset / LoadTrainingDataset
- **category:** `model/training` | **purpose:** persist and reload the prepared `LATENT` + `CONDITIONING` pair.
- **`SaveTrainingDataset` inputs:** `latents`, `conditioning`, `folder_name` (STRING), `shard_size` (INT).
- **`LoadTrainingDataset` inputs:** `folder_name` (combo) | **outputs:** `LATENT` + `CONDITIONING`.
- **placement:** wrap the expensive half. Encode once, save, then iterate on learning rate and rank against the
  saved dataset instead of re-walking and re-encoding a folder every run. `shard_size` matters for large sets.

---

## Dataset loaders and savers
- **`LoadImageDataSetFromFolder`** ("Load Image (from Folder)", category `image`) - images only. PNG, JPG, JPEG,
  WEBP. Input `folder` (combo) -> IMAGE list.
- **`LoadImageTextDataSetFromFolder`** ("Load Image-Text (from Folder)", `image`) - **the one LoRA training
  wants**: image plus caption pairs. Input `folder` (combo) -> IMAGE + STRING.
- **`LoadVideoDataSetFromFolder`** / **`LoadVideoTextDataSetFromFolder`** - the video equivalents. MP4, AVI,
  MOV, WEBM, MKV, FLV.
- **`SaveImageDataSetToFolder`** / **`SaveImageTextDataSetToFolder`** - write a set back out; captions are saved
  as sidecar TXT next to PNG images, which is the layout the loaders expect.

## Shuffling
- **`ShuffleImageTextDataset`**, **`ShuffleVideoDataset`**, **`ShuffleVideoTextDataset`** - randomise order.
  Pair-preserving on the `*Text*` variants, so a caption never separates from its image.

## Video-to-clip preparation
- **`VideoFrameSample`** - sample a fixed number of frames from a video by strategy.
- **`VideoTemporalCrop`** - crop a continuous frame range.
- **`VideoRandomTemporalCrop`** - the same, randomly placed, so repeated epochs see different segments.
- **placement:** between a video dataset loader and `MakeTrainingDataset`, to turn long clips into
  training-length segments rather than feeding whole files.

---

**Anti-patterns**
- Encoding the dataset with a VAE or CLIP that is not the target model's. Silent, and it wastes the whole run.
- Training without `LossGraphNode` wired: you get no signal about divergence until you test the output.
- Raising `batch_size` until it OOMs when `grad_accumulation_steps` gets the same effective batch inside VRAM.
- Re-running `MakeTrainingDataset` every iteration instead of `SaveTrainingDataset` once.

**Relation to the LTX-2 route:** for LTX-2 specifically the official Lightricks trainer is deeper and is
documented in [`LTX2_TRAINING.md`](../LTX2_TRAINING.md). This native path is the general one and the right first
suggestion for a style or subject LoRA that should stay inside ComfyUI.
