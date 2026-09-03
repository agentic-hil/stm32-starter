# Physical validation gate

The evidence checklist this starter is held to before it is announced or promoted anywhere. Every item wants an objective result behind it, not a judgement. The first section can be closed on any developer machine. Everything under the two after it needs a Nucleo-F446RE on a desk, and none of it can be closed from a machine that has none.

The number in front of a box is its name. It does not move: a new box takes the next unused number wherever it belongs, and no box is renumbered, so a note that cites a box by number stays right.

## Host side, no board required

Walked on Windows 11 build 26200.9168 with uv 0.11.27 and STM32CubeCLT 1.22.0 on
2026-09-02. Evidence: [2026-09-02-host-windows.md](2026-09-02-host-windows.md).

- [ ] **1.** A fresh clone plus `uv sync` succeeds on Linux, macOS and Windows. Windows is closed; Linux and macOS are not walked yet, so the item stays open.
- [x] **2.** The three simulator tests pass and print the scope statement.
- [x] **3.** A fresh report, put through the normalisation in `expected/README.md`, is byte for byte identical to `expected/simulator-junit.xml`.
- [x] **4.** The `Debug` and `Release` presets both build with `arm-none-eabi-gcc`, and `build/Debug/stm32-starter.elf` is what the plans name.

## Bench side, board required

Walked twice on Windows 11 build 26200 with a Nucleo-F446RE attached. The
project half was walked with `agentic-hil init` both times, which is the half of
`setup` that writes this project's configuration, because the agent
registrations on that machine were another session's.

On 2026-09-02, with Agentic HIL 0.21.0, boxes 5 and 6 closed and the first
hardware plan was then refused before its first hardware action, so the eight
boxes after them stayed open. Evidence:
[2026-09-02-bench-windows/](2026-09-02-bench-windows/README.md).

On 2026-09-03, with Agentic HIL 0.21.1, that refusal named its own repair, the
repair held, and the three plans ran. Boxes 7 to 13 closed. Box 14 stays open:
the span it names, from the one-line installer, was not the span this walk
measured. Evidence:
[2026-09-03-bench-windows/](2026-09-03-bench-windows/README.md).

- [x] **5.** `agentic-hil setup --agent <agent>` on a machine with the board attached discovers one ST-Link, matches its virtual COM port, and writes a configuration naming the probe `dut` and the port `dut_uart`.
- [x] **6.** `agentic-hil doctor` reports that bench healthy.
- [x] **7.** The shipped firmware passes `tests/hil/nominal.testconfig.yaml` and `tests/hil/recovery.testconfig.yaml` and fails `tests/hil/diagnostic.testconfig.yaml`, and no other plan is red.
- [x] **8.** The failing report quotes what the board answered, so the failure names the defect rather than describing a silence.
- [x] **9.** The recovery plan's middle read consumes the answer to `DIAG ON` on the bench as it does on paper: its report shows that read matching one status line and the final read matching a second, so the plan's claim is about what `DIAG CLEAR` produced.
- [x] **10.** A coding agent fixes the firmware without changing the test plans, the simulator suite, or the protocol.
- [x] **11.** All three plans pass, then pass again on the same firmware revision with nothing edited in between.
- [x] **12.** The reactor reports and logs from both green runs are retained.
- [x] **13.** The board identity, firmware revision, debugger backend and version, compiler version, and the duration of each run are recorded beside them.
- [ ] **14.** The whole path, from the one-line installer to the first green hardware plan, is walked by somebody who has not seen this repository before, and it takes under four hours.

`.agentic-hil/reports/last-report.json` is overwritten by every run, so a run's report is copied out right after the run that wrote it and not after the last of them: whoever runs the three plans first and collects afterwards keeps one report of three. A canonical per-run copy is kept under the operator's `state_root`, and a coming Agentic HIL release will print its path; until it does, the workspace copy is the one to collect.

A read whose comparator matched records the pattern, the byte count and the number of reads, and not the text it matched, which only a failing read quotes. Box 9 is a claim about what two matching reads consumed, so it is shown from the COM log beside the report until the report carries the matched text itself.

## Remote CI

- [ ] **15.** A self-hosted runner labelled `agentic-hil` and `nucleo-f446re` runs `.github/workflows/hardware-test.yml` to three green plans.
- [ ] **16.** Two runs queued at once serialise rather than colliding on the bench.
- [ ] **17.** The evidence artifact uploads on a failed run as well as a passing one.

Do not close a physical item with a simulator result, and do not close one with a hand-edited report. An open box is a fact about this repository; a closed one that nothing happened behind is a claim it cannot keep.
