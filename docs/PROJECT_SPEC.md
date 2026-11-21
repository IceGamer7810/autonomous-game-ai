# Technical Specification — General Autonomous PC Game Agent Based on Player-1

**Status:** Implementation specification  
**Date:** 2026-11-21  
**Product scope:** A game-agnostic autonomous agent designed to discover, learn, and play unfamiliar PC games through visual observation and keyboard/mouse control.  
**Primary policy:** Tencent ARC Lab Player-1, used as the short-horizon visual-action policy.  
**Core restriction:** The agent must not depend on a game's internal state, process memory, files, APIs, mods, telemetry, or title-specific integrations.

---

## 1. Product Goal and Operating Principles

Build a general autonomous PC game-playing system. At runtime, the system is given a user-selected game window and a user-defined goal. It must be able to:

1. Observe the selected game continuously through its visible output.
2. Discover the game's menus, controls, interface, rules, and mechanics without prior title-specific configuration.
3. Form and update hypotheses through controlled experiments.
4. Learn reusable procedures from observed successes and failures.
5. Decompose long-horizon goals into dependent subtasks.
6. Execute short-horizon actions through keyboard and mouse.
7. Verify outcomes from subsequent visual observations.
8. Recover from errors, blocked progress, timeouts, and unexpected UI states.
9. Preserve useful knowledge between sessions without modifying model weights.
10. Run for extended periods with bounded resource usage and reliable stop behavior.

The system must not require the game title as an input to its reasoning process. A window identifier may be used internally to route capture and input safely, but the title must not select game-specific logic, scripts, prompts, assets, or rules.

The architecture must remain game-agnostic. Game-specific knowledge is discovered at runtime and stored in a session/game profile. No game title is a canonical target or a hard-coded evaluation target. Generalization must be evaluated across multiple previously unfamiliar games, without embedding their identities in the implementation.

### 1.1 Input and observation boundary

Allowed observations:
- Pixels captured from the user-selected game window.
- Optional audio captured from the selected game session through a loopback audio interface.
- Information explicitly entered by the user, such as the high-level goal.

Allowed control:
- Keyboard and mouse events sent to the selected game window through the operating system input layer.

Disallowed access:
- Process memory, DLL injection, hooks, game APIs, mods, console commands, internal telemetry, save-file parsing, installation-file inspection, or other hidden game state.
- Reading the game title to activate title-specific behavior.
- Model-generated shell commands or arbitrary code execution.

The system must not claim that every PC game is controllable through this interface. Compatibility depends on whether the game exposes a capturable window and accepts permitted keyboard/mouse input. Unsupported input methods or platform restrictions must be reported rather than bypassed.

### 1.2 Learning policy

The project does not require manual fine-tuning, offline RL, online RL, or any other model-weight update. Player-1 remains the pretrained tactical policy.

Learning during use means:
- Persisting observations, actions, outcomes, and evidence.
- Building a runtime control map and knowledge base.
- Creating and validating reusable skills.
- Updating task state, confidence, and strategy selection.
- Reusing relevant knowledge in later sessions.

This is memory-based and in-context adaptation, not a claim that the underlying model has been retrained.

---

## 2. System Overview

The system is a coordinated set of components rather than one model:

- **Game Adapter:** Selects and identifies the target window, captures its visible output, checks focus, and provides the input interface.
- **Latest-Frame Buffer:** Holds a bounded number of recent frames in RAM. New frames replace old frames; stale frames are discarded.
- **Perception Engine:** Performs lightweight visual analysis, OCR, UI detection, and change/stuck detection.
- **Player-1 Tactical Policy:** Converts the latest visual observation and current instruction into short-horizon keyboard/mouse action proposals.
- **Explorer:** Discovers controls and mechanics through cautious, evidence-based experiments.
- **Core Planner:** Converts the user's long-term goal into subtasks, dependencies, priorities, and completion criteria.
- **Dynamic Task Graph and Scheduler:** Tracks task dependencies and assigns one control task at a time.
- **Memory System:** Stores session observations, discovered knowledge, outcomes, confidence, and reusable skills.
- **Reflex Engine:** Detects urgent conditions and proposes immediate safe recovery actions without waiting for a large model.
- **Input Arbiter:** The only component permitted to authorize operating-system input.
- **Executor:** Sends validated input events and guarantees release of held keys/buttons.
- **Audio Adapter (optional):** Captures audio and converts it into contextual events or transcription for the Planner. Player-1 must not be represented as natively audio-capable.
- **Telemetry and Dashboard:** Exposes status, metrics, logs, and user controls.

The Planner and Explorer may request actions, but neither may bypass the Input Arbiter.

---

## 3. Player-1 Model and Deployment

### 3.1 Role of Player-1

Player-1 is the tactical visual-action policy. It is responsible for short-horizon visual interpretation and action proposals. It is not, by itself, the complete autonomous agent.

The surrounding system is responsible for:
- Goal selection and task decomposition.
- Preparing current images and relevant history.
- Discovering unknown controls and mechanics.
- Maintaining persistent memory.
- Validating model-produced actions.
- Executing actions safely.
- Verifying visible outcomes.
- Long-horizon planning and recovery.

Use the official Player-1 inference implementation, chat template, and action format. Do not invent a replacement protocol when the official implementation specifies a different one.

### 3.2 Model choice

Initial tactical model: `yyyang/Player-1-9B`.

The official model materials describe:
- A 9B-class checkpoint (approximately 9.6B parameters).
- A 200 ms action step.
- vLLM-based serving and an OpenAI-compatible inference interface.
- A BF16 model file of approximately 18.8 GB.

The 35B-A3B model is an optional future alternative, not a requirement for the first implementation.

### 3.3 Hardware and serving

The local machine has:
- Intel Core i5-9300H.
- NVIDIA GeForce RTX 2060 Laptop GPU, 6 GB VRAM.
- 32 GB DDR4 RAM.
- 2 TB NVMe SSD.

The local GPU cannot host the full BF16 Player-1-9B checkpoint with adequate runtime headroom. The initial deployment therefore keeps capture, perception, memory, orchestration, safety, and input local, while serving Player-1 remotely through an authenticated vLLM endpoint.

Do not assume a quantized build is equivalent to the official checkpoint. Any quantized or local alternative requires separate compatibility, quality, memory, and latency tests.

The inference endpoint, credentials, model name, timeouts, and retry policy must be configurable. Do not hard-code a cloud provider.

---

## 4. Runtime Architecture and Data Flow

1. The user selects a game window and supplies a high-level goal.
2. The Game Adapter records a stable window identifier and verifies that capture is available.
3. Capture continuously samples the selected window at a target of 30 FPS.
4. Each frame is timestamped and placed in a bounded RAM ring buffer. The buffer overwrites or discards old frames; it must not become an unbounded queue.
5. The Perception Engine processes the newest useful frame, skipping stale frames rather than building latency.
6. OCR and visual detectors extract visible text, UI regions, prompts, state changes, and evidence with confidence values.
7. The Session Manager updates working memory and determines whether a tactical action, exploration experiment, or planning event is needed.
8. The Scheduler grants exclusive control ownership to one active task.
9. Player-1 receives the current image, concise task instruction, and only the relevant recent action/observation context.
10. The Player-1 adapter parses the official action/tool-call format into a typed action proposal.
11. The Action Validator checks schema, allowed keys/buttons, coordinates, duration, target window, and expiry.
12. The Input Arbiter checks priority, focus, emergency-stop state, ownership, and policy limits.
13. The Executor dispatches the authorized input and tracks all held keys/buttons.
14. Capture continues during inference and action execution. Subsequent frames are compared with expected visible outcomes.
15. Memory stores the observation, action, result, evidence, and confidence—not an unlimited sequence of full-resolution screenshots.
16. Explorer and Planner update hypotheses, skills, task dependencies, and next steps.
17. The Reflex Engine may interrupt any active action when an urgent safety or recovery condition is detected.

### 4.1 Capture and frame retention

- Target capture rate: 30 FPS, subject to measured machine performance.
- Capture runs continuously while the session is active, including while inference is pending.
- Frames are held in a fixed-capacity RAM ring buffer.
- When the buffer is full, old frames are overwritten or discarded.
- Stale frames are not accumulated in a work queue.
- Full-resolution screenshots are not written to disk as a continuous recording by default.
- Persist frame hashes, timestamps, compact observations, and optional low-resolution evidence thumbnails. Saving screenshot artifacts must be explicit, bounded, and governed by a retention policy.

### 4.2 Decision frequency

The Player-1 model's documented action step is 200 ms, corresponding to a nominal maximum of about five action decisions per second. This is not a throughput guarantee. Actual decision frequency depends on inference latency, network latency, scheduling, and action validation.

The system must not invoke Player-1 once for every captured frame. Capture and lightweight perception operate independently from model inference.

---

## 5. Timing and Concurrency

| Component | Initial target | Requirement |
|---|---:|---|
| Screen capture | Up to 30 FPS | Continuous, bounded RAM buffer |
| Lightweight perception | Up to 10–30 Hz | Process newest frame; skip stale frames |
| Player-1 | Nominal 200 ms action step | Measure actual p50/p95 latency |
| Local input scheduler | 60 Hz tick or event-driven | Timing, cancellation, release, watchdog |
| Planner | Event-driven | No unnecessary continuous polling |
| Explorer | Event-driven | Bounded experiments and cooldowns |
| Memory writes | Event-driven / batched | Bounded queues and controlled transactions |
| Reflex Engine | Continuous / event-driven | Must not depend on model response |

Use monotonic clocks for durations and wall-clock timestamps for human-readable logs. Capture must not block on inference, database writes, or dashboard requests. Workers must have bounded queues, explicit cancellation, and deterministic shutdown behavior.

---

## 6. Planning, Exploration, and Task Management

### 6.1 Core Planner

The Planner converts a user goal into a hierarchy of tasks. Each task must include:
- Description and priority.
- Preconditions and dependencies.
- Expected visible evidence of completion.
- Retry limit and failure policy.
- Current state and confidence.

Start with a deterministic/rule-based Planner so the application remains usable without a paid LLM API key. A provider-neutral LLM adapter may be added for more complex planning. Planner output must be structured and validated. The Planner may create tasks or request a tactical decision, but it may not send input directly.

Replan when meaningful events occur:
- Goal changes.
- A new menu, prompt, or mechanic is discovered.
- A task completes or fails.
- Progress stalls.
- A hypothesis is contradicted.
- A safety or resource limit is reached.

### 6.2 Explorer

Explorer discovers an unfamiliar game's interface and mechanics. It must:
- Inspect visible menus, tutorials, settings, prompts, and control descriptions.
- Build a control map with evidence and confidence.
- Propose short, low-risk, reversible experiments where possible.
- Change one variable at a time when practical.
- Record preconditions, action, expected effect, observed effect, and result.
- Avoid repeating risky actions without new evidence.
- Promote a hypothesis to confirmed knowledge only after sufficient repeatable evidence.

The Explorer must not rely on title-specific scripts, preloaded game walkthroughs, hidden state, or hard-coded game mechanics.

### 6.3 Dynamic Task Graph and Scheduler

Represent long-horizon tasks as a dependency graph. A task may be `PENDING`, `READY`, `RUNNING`, `COMPLETED`, `FAILED`, `BLOCKED`, or `ABANDONED`.

The Scheduler:
- Dispatches only eligible tasks.
- Prevents duplicate active execution.
- Ensures only one task owns game input at a time.
- Returns observed results to the graph.
- Triggers replanning when dependencies or completion evidence change.

---

## 7. Memory, Skills, and Runtime Learning

Use SQLite in WAL mode as the initial persistent store, with FTS5 for text retrieval. Keep the design simple and local.

Logical stores:
- Working/session state.
- Observations and visual evidence.
- Actions and outcomes.
- Game/session profiles.
- Hypotheses and confirmed knowledge.
- Experiments.
- Reusable skills and skill steps.
- Task graph nodes and dependencies.
- Audit and telemetry events.

Every knowledge item must include:
- Claim or procedure.
- Scope (general skill or session/game-specific fact).
- Status (`hypothesis`, `observed`, `confirmed`, `invalidated`).
- Confidence and supporting evidence references.
- Creation and last-validation timestamps.

Separate game-specific control maps from general reusable skills. Never apply a game-specific procedure to another session without checking its preconditions and validating the expected visual result.

A skill becomes reliable only after repeated successful verification. It must be revocable when later evidence contradicts it.

### 7.1 Bounded resource policy

- RAM frame buffers have fixed capacities.
- Inference, perception, memory, and input queues have explicit maximum sizes.
- Old or superseded frame work is dropped rather than accumulated.
- Worker tasks must be cancellable and cleaned up.
- Cache sizes and retention periods must be configurable.
- Database writes must be batched or rate-limited where appropriate.
- No unbounded per-frame history or screenshot list is allowed.
- Resource telemetry must expose process RAM, GPU VRAM where available, queue lengths, buffer occupancy, database size, and worker health.

The system must reach a stable resource-usage range during a long session. A design statement alone is not proof; this requires soak testing.

---

## 8. Reflex Engine, Input Arbiter, and Executor

### 8.1 Reflex Engine

The Reflex Engine handles urgent conditions without waiting for a large model:
- Focus loss.
- Emergency stop.
- Model or capture timeout.
- Repeated identical frames with no progress.
- Repeated action loops.
- Invalid or expired action proposals.
- Unexpected application/window closure.
- Resource exhaustion or critical worker failure.

It may propose cancellation, input release, safe idle, or a bounded recovery action. It must rely on visible evidence and system telemetry, not invented game state.

### 8.2 Input Arbiter

Only the Input Arbiter may authorize actual keyboard/mouse input.

Priority order:
1. Emergency stop.
2. Focus loss, watchdog, or safety block.
3. Reflex recovery.
4. Explicit user-approved control.
5. Player-1 action.
6. Explorer action.

The Arbiter must:
- Validate action schema and duration.
- Verify selected-window identity and current focus.
- Enforce configured input and action bounds.
- Reject expired or stale actions.
- Prevent concurrent control owners.
- Cancel lower-priority actions when required.
- Track held keys and mouse buttons.
- Release every held input on cancellation, timeout, focus loss, exception, and shutdown.
- Log accepted and rejected proposals with reasons.

### 8.3 Executor

The Executor performs only validated input events. It must not interpret arbitrary natural-language commands, launch processes, execute shell commands, or send input to a window other than the selected target.

---

## 9. Audio

Audio is optional and separate from the Player-1 visual-action interface.

The initial Player-1 integration sends image and text context only. If audio is enabled, a local audio adapter may capture loopback audio and provide bounded, timestamped events or speech-to-text output to Perception/Planner. Audio must remain contextual evidence and must not be used to infer hidden internal game state.

---

## 10. Technology Stack

| Layer | Initial choice |
|---|---|
| Runtime | Python 3.12 |
| Tactical model serving | vLLM on a remote Linux GPU host |
| Transport | Authenticated OpenAI-compatible HTTP |
| Windows capture | DXcam / DXGI, with an adapter boundary |
| Input | Win32 `SendInput` adapter |
| Image processing | Pillow + OpenCV |
| OCR | Adapter interface; PaddleOCR or Windows OCR implementation |
| Async orchestration | asyncio plus isolated worker threads/processes where needed |
| Persistent memory | SQLite WAL + FTS5 |
| API/dashboard | FastAPI, localhost-only |
| Configuration/contracts | YAML + Pydantic |
| Tests | pytest, unit/integration/replay/soak |
| Dependency management | uv or pip-tools |

The first implementation targets Windows 10/11 because the current capture/input implementation is Windows-based. Keep capture and input behind interfaces so other PC environments can be supported without changing the game-agnostic agent logic.

---

## 11. Security and Isolation

- Run the game on the host in the first version.
- Run the agent with the least privileges possible.
- Require explicit user selection of the target window.
- Do not read game memory or files.
- Do not inject code or use game APIs, mods, or console commands.
- Do not execute model-generated shell commands or arbitrary code.
- Keep credentials in environment variables or a secure local secret store.
- Never log credentials.
- Bind local control APIs to `127.0.0.1` by default.
- Do not expose unauthenticated remote control.
- The emergency stop must work even while inference is blocked.
- Release all held inputs on application shutdown.
- Send only the selected session's required image/context to the explicitly configured inference endpoint over an encrypted connection.

A VM may be used for isolated development or Planner testing, but real game control must not depend on GPU passthrough.

---

## 12. Hardware and Deployment

### Local client

The current laptop can host:
- Window capture.
- Bounded frame buffering.
- Lightweight visual processing and OCR, subject to measurement.
- Input execution.
- Memory, scheduling, Planner orchestration, Reflex, and telemetry.

It cannot host the official BF16 Player-1-9B checkpoint with adequate VRAM headroom.

### Remote inference

Use a configurable remote GPU service for the official Player-1 model. The initial reference configuration is a GPU with approximately 48 GB VRAM; an 80 GB class accelerator is an alternative. Final hardware selection must be validated against actual vLLM startup, memory use, context length, and measured latency.

The system must separately measure:
- Frame preparation and upload time.
- Network round-trip time.
- Model processing time.
- Total request latency p50/p95.
- Action scheduling drift.

Do not describe the system as real-time unless measured end-to-end performance supports that claim.

---

## 13. Implementation Plan

### Phase 0 — Repository and Contracts
- Package structure, configuration, logging, typed contracts, and tests.
- Player-1 endpoint client interface.
- Health checks and CLI.
- Tests runnable without GPU or model endpoint.

### Phase 1 — Safe Capture and Input MVP
- Explicit window selection.
- Continuous capture and bounded RAM ring buffer.
- Fake capture/model/input backends.
- Action parser and validator.
- Input Arbiter, emergency stop, focus watchdog, and release-all behavior.
- Replay tests using synthetic frames.

### Phase 2 — Player-1 Integration
- Remote vLLM endpoint.
- Official chat template and action format.
- Strict tool/action parsing.
- Configurable timeouts and bounded retries.
- Latency and capture telemetry.

### Phase 3 — Perception, Memory, and Explorer
- OCR and visual change detection.
- SQLite schema and migrations.
- Observation/action/outcome records.
- Control discovery and bounded experiments.
- Skill validation and confidence updates.

### Phase 4 — Planner, Task Graph, and Reflex
- Event-driven planning.
- Task dependencies and completion evidence.
- Stuck/progress detection.
- Recovery policy and priority arbitration.
- Safe session lifecycle.

### Phase 5 — Cross-Game Generalization Evaluation
- Evaluate on multiple previously unfamiliar PC games selected independently of the implementation.
- Do not hard-code their titles, assets, rules, controls, or walkthroughs.
- Include materially different interaction styles and game mechanics.
- Measure discovery success, task completion, recovery rate, action validity, and performance by task family.
- Report failures and unsupported input/platform cases honestly.

### Phase 6 — Long-Run Reliability
- Run an 8–12 hour continuous soak test.
- Measure RAM, VRAM, queue lengths, frame-buffer occupancy, database growth, CPU/GPU load, worker health, and inference latency.
- Verify that resource usage stabilizes rather than growing continuously.
- Verify that capture continues without stale-frame backlog.
- Verify that no key/button remains held after any cancellation or fault.
- Verify pause, resume, emergency stop, and clean shutdown throughout the run.

Every phase has its own tests and acceptance criteria. Do not skip phases or claim unrun tests passed.

---

## 14. Testing and Acceptance Criteria

### Unit tests
- Action schema and every field.
- Malformed tool calls and invalid coordinates.
- Unsupported keys/buttons and out-of-range durations.
- Action expiry and selected-window mismatch.
- Emergency stop and priority arbitration.
- Focus loss, timeout, crash, and shutdown release.
- Duplicate action suppression.
- Task Graph state transitions and dependency handling.
- Skill confidence updates and invalidation.
- Bounded queues, ring-buffer overwrite, and cancellation cleanup.
- Dataset audit completeness and count consistency.

### Integration tests
- Fake capture → fake policy → validator → Arbiter → fake input.
- Real capture with model/input disabled.
- Real inference endpoint with input disabled.
- Full integration with explicit user opt-in.
- Audio adapter tested independently if enabled.
- Repeated session start/stop and recovery cycles.

### MVP safety acceptance
- No action can bypass the Input Arbiter.
- Only the selected window receives input.
- Emergency stop works while inference is pending.
- All inputs are released on timeout, focus loss, cancellation, and shutdown.
- Capture FPS and p50/p95 inference latency are measured and exported.
- No game memory/file/API access exists in code.
- Automated tests pass.

### Long-run acceptance
- An 8–12 hour soak test completes without an uncontrolled memory/VRAM increase.
- RAM and buffer occupancy settle into a bounded operating range.
- Queues do not grow without limit.
- No stuck input remains after fault injection.
- No silent loss of task or observation records occurs.
- All metrics and faults are exported in a session report.

---

## 15. Costs and Evidence Discipline

Cloud GPU prices are deployment estimates, not fixed project requirements. Recheck current prices before provisioning. Include storage, network, taxes, region, and stopped-instance billing in any actual cost estimate.

Never fabricate:
- Model performance or benchmark results.
- Dataset coverage.
- Successful game completion.
- Measured capture or inference rates.
- Long-run memory stability.

Separate documented facts, measured project results, estimates, and hypotheses in all reports.
