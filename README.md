# STM32 Agentic HIL Starter

**Take your own copy of this repository, say one sentence to your coding agent, and watch it build firmware, flash a real Nucleo-F446RE, talk to it, and prove what the board actually did.**

Click **Use this template** above to get your own copy, or clone this one. The hardware run needs a Nucleo-F446RE, a USB cable, and the onboard ST-LINK, and nothing more: no fixture to wire, no adapter to buy. The three test plans and the suite that validates them need no board at all, so [that half runs on any machine](#run-the-plans-with-no-board-attached) and is the first thing to run whether or not a Nucleo is on your desk. This is the reference path for [Agentic HIL](https://github.com/agentic-hil/agentic-hil), the local MCP server that lets an AI agent close the firmware loop on hardware you own: build, flash, stimulate, observe, diagnose, fix.

The firmware ships with one deliberate defect in its diagnostic protocol. Finding it is the exercise.

## Install Agentic HIL

**Linux and macOS**, in any shell:

```bash
curl -LsSf https://agentic-hil.github.io/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
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

The `export` line in the first block is the one the installer prints itself when `~/.local/bin` is not already on your `PATH`, and it is the line that puts `uv` within reach as well, because both land in that directory.

To register a single agent instead of all of them, pass `--agent claude-code` (or `codex`, `opencode`); piped, that reads `| sh -s -- --agent claude-code`.

## Run the plans with no board attached

The simulator suite validates the three hardware test plans on any machine, with nothing plugged in. It needs Python 3.10 or newer and [uv](https://docs.astral.sh/uv/), which is what the lock file is for. The one-line installer above may or may not have left you with `uv`, since it falls back to `pip --user` where `uv` is absent; install it with `curl -LsSf https://astral.sh/uv/install.sh | sh` on Linux and macOS, or `irm https://astral.sh/uv/install.ps1 | iex` in PowerShell.

```bash
uv sync
uv run pytest -q -s
```

Every test states what a green run is worth:

```text
PASS  configuration and test semantics validated in simulator
NEEDS PHYSICAL FIXTURE  electrical behavior not verified
```

Without `uv`, the same suite runs from a plain virtual environment:

```bash
python -m venv .venv
.venv/bin/pip install "agentic-hil>=0.21.0" pytest pyyaml   # .venv\Scripts\pip on Windows
.venv/bin/pytest -q -s   # .venv\Scripts\pytest on Windows
```

[What runs where](#what-runs-where) is the account of what a green suite establishes and what it leaves to the bench.

## What you need for the hardware run

- A Nucleo-F446RE connected through its ST-LINK USB port
- CMake 3.21 or newer, which is what [CMakePresets.json](CMakePresets.json) needs for its preset version and its `toolchainFile`, plus Ninja and the GNU Arm Embedded Toolchain (`arm-none-eabi-gcc`) on your `PATH`; [STM32CubeCLT](https://www.st.com/en/development-tools/stm32cubeclt.html) carries all three
- STM32CubeProgrammer CLI, which is what `agentic-hil setup` looks for when it discovers your probe; OpenOCD serves the same role once the configuration names it
- Python 3.10 or newer

The build tools above are yours to put on the path, and `cmake --build --preset Debug` is what tells you they are there. Build before you run a plan: the test reactor, the part of Agentic HIL that takes one declared test plan and runs it end to end against the bench, flashes `build/Debug/stm32-starter.elf`, and on a tree nobody has built it refuses the plan before its first hardware action with `test_config_invalid: Firmware artifact does not exist`.

`agentic-hil doctor` validates this project's configuration and reports the debugger backend and the devices it bound, so it comes after the command that writes that configuration and not before it: run first, it has nothing to validate and refuses with `config_file_not_found`. `agentic-hil setup` or `agentic-hil init` is what writes the file it wants.

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

With no board attached that command is green anyway: discovery finds no probe, writes a placeholder where the probe's identity goes, and says so in that step of its own output. What you have afterwards is a configuration to finish on the day the board arrives, not a failure to work around.

`setup` is the first command when the agent on this machine is yours to register; when the agent registrations belong to somebody else, on a shared bench or under a CI runner's user, `agentic-hil init` is the first command instead and writes this project's half without touching them.

### 3. Watch it prove itself

Two of the three plans go green on a working board. `tests/hil/diagnostic.testconfig.yaml` does not, and its report names the claim that went unmet and quotes what the board answered instead.

Every step is a command you can run yourself, and these are the ones the agent runs. The order is not decorative: `doctor` has a configuration to check only once `setup` has written one, and a plan has an image to flash only once the build has produced one.

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

**On any machine, with no board attached**, the simulator suite validates the three hardware plans with the test reactor's own loader: the closed plan schema, the step vocabulary, the format version gate, the diagnostic protocol the plans state, and the rule that a plan names logical devices, the configuration's own names for the probe and the serial line, `dut` and `dut_uart` here, and never somebody's serial port. A plan that passes here is one the reactor's loader accepts. The reactor also holds a plan against this bench's configured devices and permissions before the first hardware action, and that half needs a configuration, so it happens on the bench.

**On a bench with a Nucleo-F446RE attached**, the three plans in [tests/hil/](tests/hil/) run through `agentic-hil test-reactor`, which validates every device name, permission and session order before the first hardware action, holds the probe and the serial line for the whole run under one lease, the machine-wide claim on a device that keeps a second run off it until this one gives it back, closes them even when a step fails, and writes one JSON report saying what ran under which policy. That is where electrical behaviour is established.

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
| [validation/](validation/) | The evidence gate: the checklist of results this starter has to have behind it before it is announced anywhere, and how far it has been walked |

## Licence

[Apache License 2.0](LICENSE), the same licence Agentic HIL itself ships under.
