# Physical validation gate

The evidence checklist this starter is held to before it is announced or promoted anywhere. Every item wants an objective result behind it, not a judgement. The first section can be closed on any developer machine. Everything under the two after it needs a Nucleo-F446RE on a desk, and none of it can be closed from a machine that has none.

## Host side, no board required

Walked on Windows 11 build 26200.9168 with uv 0.11.27 and STM32CubeCLT 1.22.0 on
2026-09-02. Evidence: [2026-09-02-host-windows.md](2026-09-02-host-windows.md).

- [ ] A fresh clone plus `uv sync` succeeds on Linux, macOS and Windows. Windows is closed; Linux and macOS are not walked yet, so the item stays open.
- [x] The three simulator tests pass and print the scope statement.
- [x] A fresh report, put through the normalisation in `expected/README.md`, is byte for byte identical to `expected/simulator-junit.xml`.
- [x] The `Debug` and `Release` presets both build with `arm-none-eabi-gcc`, and `build/Debug/stm32-starter.elf` is what the plans name.

## Bench side, board required

Walked on Windows 11 build 26200 with Agentic HIL 0.21.0 and a Nucleo-F446RE
attached on 2026-09-02. The first two items closed. The first hardware plan was
then refused before its first hardware action, so the eight items after them
stay open. The project half was walked with `agentic-hil init`, which is the
half of `setup` that writes this project's configuration, because the agent
registrations on that machine were another session's. Evidence:
[2026-09-02-bench-windows/](2026-09-02-bench-windows/README.md).

- [x] `agentic-hil setup --agent <agent>` on a machine with the board attached discovers one ST-Link, matches its virtual COM port, and writes a configuration naming the probe `dut` and the port `dut_uart`.
- [x] `agentic-hil doctor` reports that bench healthy.
- [ ] The shipped firmware passes `tests/hil/nominal.testconfig.yaml` and `tests/hil/recovery.testconfig.yaml` and fails `tests/hil/diagnostic.testconfig.yaml`, and no other plan is red.
- [ ] The failing report quotes what the board answered, so the failure names the defect rather than describing a silence.
- [ ] The recovery plan's middle read consumes the answer to `DIAG ON` on the bench as it does on paper: its report shows that read matching one status line and the final read matching a second, so the plan's claim is about what `DIAG CLEAR` produced.
- [ ] A coding agent fixes the firmware without changing the test plans, the simulator suite, or the protocol.
- [ ] All three plans pass, then pass again on the same firmware revision with nothing edited in between.
- [ ] The reactor reports and logs from both green runs are retained.
- [ ] The board identity, firmware revision, debugger backend and version, compiler version, and the duration of each run are recorded beside them.
- [ ] The whole path, from the one-line installer to the first green hardware plan, is walked by somebody who has not seen this repository before, and it takes under four hours.

## Remote CI

- [ ] A self-hosted runner labelled `agentic-hil` and `nucleo-f446re` runs `.github/workflows/hardware-test.yml` to three green plans.
- [ ] Two runs queued at once serialise rather than colliding on the bench.
- [ ] The evidence artifact uploads on a failed run as well as a passing one.

Do not close a physical item with a simulator result, and do not close one with a hand-edited report. An open box is a fact about this repository; a closed one that nothing happened behind is a claim it cannot keep.
