# Agent Instructions

You are working in the Agentic HIL STM32 starter. The target is an ST Nucleo-F446RE reached through its onboard ST-LINK: a debug probe and a virtual COM port over one USB cable.

The firmware in `firmware/src/main.c` contains one deliberate defect in its diagnostic protocol. Your job is to run the hardware test plans, let the failure name itself, fix the firmware, and rerun everything.

## The hardware is reached through Agentic HIL and nothing else

Every action that touches the board goes through the `agentic-hil` MCP tools. Do not call OpenOCD, STM32CubeProgrammer, `st-flash`, `st-info`, `pyocd`, GDB, `screen`, `minicom` or `picocom`, do not open `COM*` or `/dev/tty*` yourself, and do not run a build target that does any of that for you. Those bypass the policy the operator set and leave nothing they can audit.

A `permission_denied` result is the answer to your request, not an obstacle. Report it, name the permission, and stop. Never edit the authoritative configuration to grant yourself a permission: that file is the operator's.

## 1. Set up the project

```bash
agentic-hil setup --agent <claude-code|codex|opencode>
```

Say what it writes before you run it, and then run it in the same turn. It installs the agent skill and the user-level MCP registration, and it writes this project's authoritative configuration outside the repository. `setup` is the first command when the agent on this machine is yours to register; when only the project half is wanted, on a shared bench or under a runner whose agent registrations are somebody else's, `agentic-hil init` is the first command and not a fallback. If the host refuses the command, run `agentic-hil init` immediately, which writes the project half and needs no agent-level grant, and hand the operator the one line that is left: `agentic-hil agent-install --agent <agent>`.

`agentic-hil.config.example.yaml` in this repository is the bootstrap profile, not the configuration. It asks for the serial line at 115200 baud with writes allowed, because the plans send commands to the board, and for firmware images to be read from `build/`. Discovery supplies the rest: which ST-Link is attached, where STM32CubeProgrammer lives, and which virtual COM port belongs to that probe. A generated configuration names the probe `dut` and the serial line `dut_uart`, which are the two names every plan routes to.

Then confirm the bench:

```bash
agentic-hil doctor
```

The MCP registration lands at the next session start, so if the tools are not there yet, tell the operator to restart the agent rather than waiting for them to appear.

## 2. Build the firmware

```bash
cmake --preset Debug
cmake --build --preset Debug
```

This produces `build/Debug/stm32-starter.elf`, which is the image every plan flashes. Rebuild before every hardware run, so the board is running the source you are reading.

## 3. Run the hardware tests

The hardware tests are three declared plans, not a script you assemble:

- `tests/hil/nominal.testconfig.yaml` claims `STATUS` answers `READY` with no diagnostic raised.
- `tests/hil/diagnostic.testconfig.yaml` claims `DIAG ON` answers `DEGRADED` with `E_SELF_TEST`.
- `tests/hil/recovery.testconfig.yaml` claims that the answer arriving after `DIAG CLEAR` is `READY` with no diagnostic raised. It reads and discards the answer to the `DIAG ON` before it, so the claim is about what `DIAG CLEAR` produced and not about what was already on the line.

Run each one with the `test_reactor_run` tool, passing the plan as `test_config_path`. That is the route for an agent, because it is the one the operator can see and audit, and it needs no `bench_run_start` around it: a plan is already a run. The operator's equivalent at a shell is `agentic-hil test-reactor --test-config <plan>`.

The reactor validates every device name, permission and session order before the first hardware action, holds the probe and the serial line for the whole plan, closes them even when a step fails, and writes one report. Do not rebuild that loop out of `flash_firmware`, `com_session_start`, `reset_target` and `com_read` calls: the plan says the same thing, is checked before it runs, and cleans up after itself. Reach for the individual tools only when a step needs something the plan vocabulary has no word for, and say in your report that you did and why.

Expect two green plans and one red one on a working board. `.github/workflows/hardware-test.yml`, which runs the same three plans on a bench in CI, expects the same thing: its diagnostic step is expected to fail with `comparator_unmet` on the shipped firmware, and the step after it asserts exactly that from the run's own report, so that workflow is green while the firmware behaves as documented and red for any other reason.

## 4. Diagnose and fix

Read the failing plan's report. A claim that goes unmet fails with the tail of what the port did say, so the report tells you what the board answered instead of the expected line. Compare that against the protocol table in `README.md` and against `firmware/src/main.c`.

Make the smallest firmware-only correction, rebuild, and run all three plans again. Three green plans on one firmware revision is the finished state.

## Constraints

- Do not change the test plans in `tests/hil/`, the simulator suite in `tests/simulator/`, or the protocol in `README.md` to make the challenge pass. The firmware is what is wrong.
- Do not emulate the MCU. The claim this repository makes is about a real board.
- Do not say a simulator run verified firmware behaviour. `uv run pytest -q -s` validates the plans on any machine; it establishes nothing electrical, and the suite prints exactly that beside every result, which is what the `-s` is for.
- Do not write `.mcp.json` or `.vscode/mcp.json` into this repository. Both are gitignored on purpose: an MCP registration names the program that answers as the hardware gate, so it belongs in the operator's user-level configuration, not in a file anyone with repository access can change.
- Do not commit build output, reactor reports or logs. `build/` and `.agentic-hil/` are gitignored.

## Reporting

Say what you ran and what came back: the build command, each plan you ran and its verdict, the firmware revision, the board and probe `agentic-hil doctor` reported, and the path of each reactor report. If something was refused, name the permission or the host rule that refused it. A green simulator run on its own is not evidence that the loop closed.

Reports and logs are workspace-relative, `.agentic-hil/reports/` and `.agentic-hil/logs/`, while the audit state that decides whether a run may start at all is under the operator's `state_root` outside the repository. A run refused before its first hardware action still leaves its log in `.agentic-hil/logs/`, and when what was refused is the audit write itself it leaves no report at all, so the log and the refusal you were handed are that run's record.

`.agentic-hil/reports/last-report.json` holds the last run only, because every run overwrites it, so it is never the path to quote when more than one run has to be shown. The copy that survives is the canonical per-run one under the operator's `state_root`, one file per run that nothing later overwrites, and Agentic HIL 0.21.2 tells you where it is: the report carries the path in `canonical_report_path` and the run repeats it in the summary line it prints, a refusal included. Report that path for each run.
