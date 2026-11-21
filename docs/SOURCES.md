# Sources and Verification Notes

**Reference date:** 2026-11-21  
**Source policy:** Prefer official project documentation, model cards, papers, and operating-system/API documentation. Recheck mutable pages, model revisions, licenses, and pricing at implementation time.

## 1. Player-1 Project

1. Project website: https://player-1-project.github.io/
   - Project overview and published dataset/model information.
   - Reported dataset and action-space details.

2. Research paper: https://arxiv.org/abs/2610.20584
   - Player-1 model and training/evaluation methodology.
   - SFT, synthetic Player-1-Gym environments, and PPO.
   - Published benchmark results and dataset statistics.

3. Official GitHub repository: https://github.com/TencentARC/Player-1
   - Source code and implementation.
   - `docs/MODELS.md`: model serving and inference instructions.
   - `docs/DATA_PRODUCTION.md`: data-production documentation.
   - `docs/TRAINING.md`: training environment and requirements.
   - `LICENSE`: software license.

4. Player-1-9B model card: https://huggingface.co/yyyang/Player-1-9B
   - Model architecture and parameter count.
   - Documented 200 ms action step.
   - Model license and file sizes.
   - Official inference and vLLM serving guidance.

5. Player-1-35B-A3B model card: https://huggingface.co/yyyang/Player-1-35B-A3B
   - Model architecture, total/active parameter information, license, and file sizes.

6. Player-1-Data: https://huggingface.co/datasets/yyyang/Player-1-Data
   - Dataset card, files, metadata, and source-dependent license.
   - `recordings.jsonl` and source documentation contain provenance identifiers.

7. Player-1-Data source documentation:
   https://huggingface.co/datasets/yyyang/Player-1-Data/blob/main/SOURCES.md
   - Source categories, trajectory counts, and source-session references.

## 2. D2E Source Dataset

8. D2E-Original dataset card:
   https://huggingface.co/datasets/open-world-agents/D2E-Original
   - Dataset structure and source-level terms.
   - Synchronized video, audio, and input-event information.

9. D2E GitHub repository:
   https://github.com/worv-ai/D2E
   - Data structure and reader documentation.

## 3. Capture, Input, and Platform APIs

10. DXcam:
    https://github.com/ra1nty/DXcam
    - Windows Desktop Duplication/DXGI and WinRT capture backends.
    - Frame buffering and timestamping capabilities.
    - Performance must be measured on the actual deployment hardware.

11. Microsoft `SendInput` documentation:
    https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-sendinput
    - Operating-system keyboard and mouse event injection.
    - UIPI and integrity-level restrictions.

12. Windows Graphics Capture:
    https://learn.microsoft.com/windows/uwp/audio-video-camera/screen-capture
    - Windows screen and application-window capture APIs.

13. Windows audio capture documentation:
    https://learn.microsoft.com/windows/win32/coreaudio/loopback-recording
    - WASAPI loopback capture reference for the optional audio adapter.

## 4. Inference Hosting and Pricing

14. vLLM documentation:
    https://docs.vllm.ai/
    - Serving configuration and OpenAI-compatible API.
    - Confirm Player-1-specific support against the official Player-1 model instructions.

15. RunPod pricing:
    https://www.runpod.io/pricing
    - Mutable cloud GPU pricing reference.
    - Recheck current prices, billing rules, regions, and availability before provisioning.

## 5. Source-Quality Rules

- A model weight-file size is not the same as total inference VRAM requirements.
- The documented action step is not a guarantee of end-to-end decision throughput.
- Capture FPS is not the same as model decision frequency.
- Full source-dataset statistics must not be conflated with the subset used by Player-1.
- Dataset viewer counts and publication counts may differ; preserve and explain discrepancies.
- Metadata labels do not establish the visual contents of source videos that are unavailable.
- Licenses for software, model weights, and dataset sources are separate.
- Every unmeasured performance value must be labeled as a target, estimate, or unknown.
- Recheck mutable pages and exact model/dataset revisions before implementation or redistribution.
