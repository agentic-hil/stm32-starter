# STM32 Agentic HIL Starter

**Clone this repository, say one sentence to your coding agent, and watch it build firmware, flash a real Nucleo-F446RE, talk to it, and prove what the board actually did.**

This is the reference path for [Agentic HIL](https://github.com/agentic-hil/agentic-hil), the local MCP server that lets an AI agent close the firmware loop on hardware you own: build, flash, stimulate, observe, diagnose, fix. Everything here needs a Nucleo-F446RE, a USB cable, and the onboard ST-LINK. No fixture to wire, no adapter to buy.

The firmware ships with one deliberate defect in its diagnostic protocol. Finding it is the exercise.

## Install Agentic HIL

**Linux and macOS**, in any shell:

```bash
curl -LsSf https://agentic-hil.github.io/install.sh | sh
```

**Windows**, in PowerShell:

```powershell
irm https://agentic-hil.github.io/install.ps1 | iex
```

**Windows**, from `cmd.exe` or the Run box:

```cmd
powershell -c "irm https://agentic-hil.github.io/install.ps1|iex"
```

One line installs the package user-local and registers the agent skill and the MCP server for every agent CLI it finds on your `PATH`. No admin rights are required, and it writes nothing inside this repository. Then restart your agent once.

To register a single agent instead of all of them, pass `--agent claude-code` (or `codex`, `opencode`); piped, that reads `| sh -s -- --agent claude-code`.

## Three steps

### 1. Open this repository in your agent

```bash
git clone https://github.com/agentic-hil/stm32-starter.git
cd stm32-starter
```

Start your agent from this directory. It reads [AGENTS.md](AGENTS.md) and finds the `agentic-hil` MCP server already registered by the installer.

### 2. Say one sentence

```text
Set up this project for the attached Nucleo-F446RE and run the three hardware
test plans in tests/hil.
```

The agent runs `agentic-hil setup --agent <agent>`, which discovers your ST-LINK, matches its virtual COM port, and writes this project's authoritative configuration outside the repository, which is where the policy that decides what the bench may do belongs. Then it builds the firmware and runs the plans.

### 3. Watch it prove itself

Two of the three plans go green on a working board. `tests/hil/diagnostic.testconfig.yaml` does not, and its report names the claim that went unmet and quotes what the board answered instead.

Every step is a command you can run yourself, and these are the ones the agent runs:

```bash
agentic-hil setup --agent claude-code    # or: codex / opencode
agentic-hil doctor

cmake --preset Debug
cmake --build --preset Debug

agentic-hil test-reactor --test-config tests/hil/nominal.testconfig.yaml
agentic-hil test-reactor --test-config tests/hil/diagnostic.testconfig.yaml
agentic-hil test-reactor --test-config tests/hil/recovery.testconfig.yaml
```

## The exercise: fix the bug

The firmware in [firmware/src/main.c](firmware/src/main.c) speaks a small JSON diagnostic protocol over the ST-LINK virtual COM port at 115200 baud:

| Command | Expected answer |
|---|---|
| `STATUS` | `{"state":"READY","diagnostic":"NONE"}` |
| `DIAG ON` | `{"state":"DEGRADED","diagnostic":"E_SELF_TEST"}` |
| `DIAG CLEAR` | `{"state":"READY","diagnostic":"NONE"}` |

One of those three commands does not do what this table says. [tests/hil/diagnostic.testconfig.yaml](tests/hil/diagnostic.testconfig.yaml) is the plan that catches it, and it is the only red plan of the three, so the failure points at one command rather than at the firmware in general.

Hand the exercise to your agent:

```text
Run tests/hil/diagnostic.testconfig.yaml on the board, work out why the
diagnostic claim goes unmet, make the smallest firmware fix, rebuild, and rerun
all three plans. Do not change the test plans or the protocol.
```

A finished run is three green plans on one firmware revision, and the reactor's report under `.agentic-hil/reports/` is the evidence.

## What runs where

**On any machine, with no board attached**, the simulator suite validates the three hardware plans with the test reactor's own loader: the closed plan schema, the step vocabulary, the format version gate, the diagnostic protocol the plans state, and the rule that a plan names logical devices and never somebody's serial port. A plan that passes here is one the reactor's loader accepts. The reactor also holds a plan against this bench's configured devices and permissions before the first hardware action, and that half needs a configuration, so it happens on the bench.

It needs Python 3.10 or newer and [uv](https://docs.astral.sh/uv/), which is what the lock file is for:

```bash
uv sync
uv run pytest -q -s
```

The one-line installer above may or may not leave you with `uv`, since it falls back to `pip --user` where `uv` is absent. Install it with `curl -LsSf https://astral.sh/uv/install.sh | sh` on Linux and macOS, or `irm https://astral.sh/uv/install.ps1 | iex` in PowerShell.

Without `uv`, the same suite runs from a plain virtual environment:

```bash
python -m venv .venv
.venv/bin/pip install "agentic-hil>=0.16.0" pytest pyyaml   # .venv\Scripts\pip on Windows
.venv/bin/pytest -q -s
```

Every test states what a green run is worth:

```text
PASS  configuration and test semantics validated in simulator
NEEDS PHYSICAL FIXTURE  electrical behavior not verified
```

**On a bench with a Nucleo-F446RE attached**, the three plans in [tests/hil/](tests/hil/) run through `agentic-hil test-reactor`, which validates every device name, permission and session order before the first hardware action, holds the probe and the serial line for the whole run, closes them even when a step fails, and writes one JSON report saying what ran under which policy. That is where electrical behaviour is established.

## What you need for the hardware run

- A Nucleo-F446RE connected through its ST-LINK USB port
- CMake 3.21 or newer, which is what [CMakePresets.json](CMakePresets.json) needs for its preset version and its `toolchainFile`, plus Ninja and the GNU Arm Embedded Toolchain (`arm-none-eabi-gcc`) on your `PATH`; [STM32CubeCLT](https://www.st.com/en/development-tools/stm32cubeclt.html) carries all three
- STM32CubeProgrammer CLI, which is what `agentic-hil setup` looks for when it discovers your probe; OpenOCD serves the same role once the configuration names it
- Python 3.10 or newer

`agentic-hil doctor` validates this project's configuration and reports the debugger backend and the devices it bound. The build tools above are yours to put on the path, and `cmake --build --preset Debug` is what tells you they are there.

## Register the MCP server in another host

The installer registers the server at user level for Claude Code, Codex and opencode, which is where a hardware gate belongs: outside the repository, so the agent working in the repository cannot rewrite how it is launched. That is why this repository ships no `.mcp.json` and no `.vscode/mcp.json`, and why both are listed in [.gitignore](.gitignore).

For a host the installer does not cover, register it by hand. Every block below carries the same launch contract: the verified absolute path to your persistent `agentic-hil` executable, the argument `mcp-stdio`, and this repository root as the working directory. `agentic-hil doctor` prints the exact executable path to paste.

**Claude Code**, from this repository root:

```bash
claude mcp add --transport stdio --scope user agentic-hil -- "/absolute/path/to/persistent/agentic-hil" mcp-stdio
```

**Codex**, in `~/.codex/config.toml`:

```toml
[mcp_servers.agentic-hil]
command = "/absolute/path/to/persistent/agentic-hil"
args = ["mcp-stdio"]
cwd = "/absolute/path/to/stm32-starter"
enabled = true
```

**opencode**, in `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "agentic-hil": {
      "type": "local",
      "command": [
        "/absolute/path/to/persistent/agentic-hil",
        "mcp-stdio"
      ],
      "cwd": "/absolute/path/to/stm32-starter",
      "enabled": true
    }
  }
}
```

**VS Code and GitHub Copilot**, in the VS Code user-profile MCP configuration (VS Code uses `servers`, not `mcpServers`):

```json
{
  "servers": {
    "agentic-hil": {
      "type": "stdio",
      "command": "/absolute/path/to/persistent/agentic-hil",
      "args": [
        "mcp-stdio"
      ],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

[The MCP host guide](https://github.com/agentic-hil/agentic-hil/blob/master/docs/mcp-hosts.md) has JetBrains, the generic host contract, and how to verify the connection.

## Continuous integration

- [.github/workflows/simulator.yml](.github/workflows/simulator.yml) runs the simulator suite on a GitHub-hosted runner, on every push and pull request, and uploads the JUnit XML report.
- [.github/workflows/hardware-test.yml](.github/workflows/hardware-test.yml) runs the three plans on a self-hosted runner that has a Nucleo-F446RE attached, labelled `agentic-hil` and `nucleo-f446re`. It serialises bench access with a concurrency group and uploads the reactor reports and logs whether the run passed or failed.

[expected/](expected/) holds the reference simulator report, and [expected/README.md](expected/README.md) has the two commands that reproduce it and compare the two byte for byte.

## Where everything lives

| Path | What it is |
|---|---|
| [firmware/src/main.c](firmware/src/main.c) | The whole firmware: USART2 setup, the diagnostic protocol, and the defect |
| [CMakeLists.txt](CMakeLists.txt), [CMakePresets.json](CMakePresets.json) | The `Debug` and `Release` builds, producing `build/Debug/stm32-starter.elf` |
| [tests/hil/](tests/hil/) | Three test reactor plans, one per hardware test |
| [tests/simulator/](tests/simulator/) | The host-side validation of those plans |
| [agentic-hil.config.example.yaml](agentic-hil.config.example.yaml) | What `agentic-hil setup` should discover for this project |
| [AGENTS.md](AGENTS.md) | The instructions your agent reads when it opens this repository |
| [expected/](expected/) | Reference reports to diff against |
| [validation/](validation/) | The evidence gate this starter is held to |

## Licence

[Apache License 2.0](LICENSE), the same licence Agentic HIL itself ships under.
