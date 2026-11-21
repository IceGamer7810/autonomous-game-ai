# autonomous-game-ai

Game-agnostic autonomous PC game agent foundation based on a remote
Player-1-compatible endpoint. The implementation uses only selected-window
pixels and permitted keyboard/mouse input at runtime; it does not inspect game
processes, files, APIs, or hidden state.

## Setup

Requires Python 3.12+ (the current validation environment is Linux; Windows
capture/input must be validated on Windows 10/11).

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m game_agent --config config/default.yaml health
```

Copy `.env.example` to `.env` only for local configuration. Keep endpoint
credentials in environment variables; never commit them.

## Local agent and Player-1 endpoint

The foundation health command is:

```bash
python -m game_agent --config config/default.yaml health
```

The Player-1 client uses the configured OpenAI-compatible `/chat/completions`
endpoint and defaults to `yyyang/Player-1-9B`. A vLLM server command must be
taken from the official Player-1 model/repository instructions and has not
been run in this repository. The local 6 GB GPU is not claimed to host the
official BF16 checkpoint.

## Dataset audit

After downloading a complete, permitted Player-1-Data revision:

```bash
python tools/audit_player1_dataset.py ./data/Player-1-Data \
  --out ./reports/dataset-audit
```

The utility fails closed when trajectory metadata, `recordings.jsonl`, parsing,
or the expected 6,044-record consistency check fails. It reports metadata
facts and 200 ms/turn estimates; it does not infer unavailable video content.

## Reliability harness

The synthetic bounded harness is not evidence of game or Windows reliability:

```bash
python tools/run_soak_test.py --duration-seconds 60 --out reports/soak.json
```

An actual 8–12 hour Windows/game soak, endpoint latency measurement, and
cross-game evaluation remain pending and must be run before claiming those
acceptance criteria.

## Current validation

The latest automated run passed 33 tests (with deprecation warnings from the
installed test/dashboard stack). Measured capture FPS, real Player-1 latency,
Windows compatibility, cross-game results, and long-run resource stability
are not claimed because those environments and inputs were not available.

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) and the authoritative
specifications in [docs/](docs/) for phase status and constraints.
