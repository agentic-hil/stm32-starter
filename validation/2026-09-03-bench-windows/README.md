# Bench side gate, Windows, 2026-09-03

Evidence for the ten items under "Bench side, board required" in
[../README.md](../README.md), walked on Windows with a Nucleo-F446RE attached,
on Agentic HIL 0.21.1.

The boxes in [../README.md](../README.md) carry stable numbers now, and this
note's numbers predate them: item N of this note is box N minus 9, so its item
15 is box 6.

This is the second bench walk. The first, on 0.21.0
([../2026-09-02-bench-windows/](../2026-09-02-bench-windows/README.md)), stopped
at the first hardware plan with `unsafe_configured_path` and left eight items
open. On 0.21.1 the refusal names the repair for that case, the repair worked,
and nine of the ten items are now closed. Nothing was routed around: no
configuration was edited by hand, `AGENTIC_HIL_CONFIG` was not set, and no
debugger, serial device or CAN adapter was opened outside Agentic HIL. Every
board action ran through `uv run agentic-hil`.

## Environment

| Item | Value |
|---|---|
| Date | 2026-09-03, walk started 22:25:07 +02:00 |
| OS | Microsoft Windows 11 Pro, 10.0.26200, 64 bit |
| Host | a packaged (MSIX) agent host with a redirected profile, `C:\Users\mail\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local` |
| Clone | `C:\Users\mail\work\ahil-starter`, branch `validation/bench-gate-2` off `main`, commit `5d9ed823b3544915b6a7dc4dac9d02f600a87518` |
| Agentic HIL | 0.21.1, from the project environment (`uv run agentic-hil`), package at `.venv\Lib\site-packages\agentic_hil` |
| uv | `uv 0.11.27 (19fc8b03b 2026-07-06 x86_64-pc-windows-msvc)` |
| CMake | `cmake version 4.3.1`, `C:\ST\STM32CubeCLT_1.22.0\CMake\bin\cmake.exe` |
| Compiler | `arm-none-eabi-gcc.exe (GNU Tools for STM32 14.3.rel1.20251027-0700) 14.3.1 20250623` |
| STM32CubeCLT | 1.22.0 |
| Debugger backend | `stlink`, `C:\ST\STM32CubeCLT_1.22.0\STM32CubeProgrammer\bin\STM32_Programmer_CLI.EXE`, version `STM32CubeProgrammer 2.23.0`, interface SWD |
| Configuration | `C:\Users\mail\.agentic-hil\projects\ahil-starter-27c0fc5d4e\config.yaml` |
| State root, after the repair | `C:\Users\mail\.agentic-hil\state` |

The project environment was used for every Agentic HIL command, as in the first
walk, because the bench-wide `agentic-hil` on `PATH` is an older release held by
other sessions on this machine.

## Board identity

As the backend reported it through Agentic HIL, in
[green-2/logs/stlink-20260903T203135859Z-reset_target.log](green-2/logs/stlink-20260903T203135859Z-reset_target.log):

```
ST-LINK SN  : 066AFF303435554157113106
ST-LINK FW  : V2J30M19
Board       : NUCLEO-F446RE
Voltage     : 3.26V
SWD freq    : 4000 KHz
Connect mode: Normal
Reset mode  : Software reset
Device ID   : 0x421
Revision ID : Rev A
Device name : STM32F446xx
NVM size    : 512 KBytes
Device type : MCU
Device CPU  : Cortex-M4
BL Version  : 0x90
```

## Firmware revisions

| Tree | Identity | ELF SHA256 | Bytes | `text` |
|---|---|---|---|---|
| Shipped, with the deliberate defect | commit `5d9ed823b3544915b6a7dc4dac9d02f600a87518`, `firmware/src/main.c` blob `1489f78f278225ea6626221cb9fa8aea7109d818` | `383917046e3aa1608b29d3995184c72bc738a479c9b8d8441e4a59bc3c0e7d32` | 29856 | 936 |
| Fixed, not committed | tree `d39ce5b00890dfa3ad2642943deeb284f78b0a99`, `firmware/src/main.c` blob `6b8ed689f74c80fab7517fe0006ef71b2476218d` | `facb8770d64fc89a188dba202ee4f54120da630cc9448cae79cc199c62acba89` | 29856 | 932 |

The shipped ELF hash is the one the first walk recorded on 2026-09-02, so the
build reproduces byte for byte across the two walks.

## The configuration, and the repair the tool named

`uv run agentic-hil init` found the configuration the first walk wrote and kept
it, which is what it is documented to do:

```
$ uv run agentic-hil init
Agentic HIL project configured.

  config_path  C:\Users\mail\.agentic-hil\projects\ahil-starter-27c0fc5d4e\config.yaml
  agent        none named
  scope        project

Steps
  config                   skipped  Existing authoritative config, unchanged: not a
                                    byte of it was written, and this never replaces
                                    operator policy.
  doctor                   ok       Agentic HIL configuration loaded and 1 debugger(s)
                                    checked.
```

That configuration still named `state_root: C:\Users\mail\AppData\Local\agentic-hil`,
the redirected root, so the first hardware plan was refused exactly as on
2026-09-02, with `audit_unavailable` over `unsafe_configured_path`
(`run-2c3dd95465eb27d9`). What is new in 0.21.1 is remediation item 4, which
names the repair:

```
  4. This refusal is about a path, so it is deterministic: the same
     command with nothing changed is refused again, with a new run id and
     the same two spellings. Repair the setting instead. When `field` is
     `state_root`, the configuration names a root this profile will not
     accept and `agentic-hil init --force` (or `project_config_create`)
     rewrites the file with one it will; anything else here is a path an
     operator set, and it is changed in the file before the command is run
     again.
```

On 0.21.0 that item said instead to re-run the failed command and that nothing
else had to change, which the first walk tried and which was refused
identically.

`uv run agentic-hil init --force` was run, and it changed one line of the
configuration and nothing else:

```
-state_root: C:\Users\mail\AppData\Local\agentic-hil
+state_root: C:\Users\mail\.agentic-hil\state
```

The configuration digest went from
`sha256:95a58f739f9970c3e188c18c8f180ef551bdf5e3e0f427bda7d2293b45e43c21` to
`sha256:eab5dcf5f76d3b2969310e308d621896af104132cf3483f9f6e09ca819a19141`. Every
hardware run below carries the second digest in its `config_in_force`.

## Item 15: doctor reports the bench healthy

```
$ uv run agentic-hil doctor
Agentic HIL configuration loaded and 1 debugger(s) checked.

  config_path      C:\Users\mail\.agentic-hil\projects\ahil-starter-27c0fc5d4e\config.yaml
  state            unchanged
  loaded_digest    sha256:eab5dcf5f76d3b2969310e308d621896af104132cf3483f9f6e09ca819a19141
  reload_required  no
  The authoritative configuration on disk is byte-for-byte the one this server loaded.

Installation
  version       0.21.1
  package_path  C:\Users\mail\work\ahil-starter\.venv\Lib\site-packages\agentic_hil
  editable      no

Target
  name        nucleo-f446re-starter
  controller  stm32f446ret6

Debuggers
  dut (stlink, bound)
    probe_id     066AFF303435554157113106
    permissions  granted: allow_debug_execution, allow_flash, allow_reset; closed:
                 allow_mass_erase, allow_raw_debugger_commands
    check           ok              STM32CubeProgrammer CLI is available.
    target_support  not_applicable  STM32CubeProgrammer identifies the connected part
                                    itself; debuggers.<name>.target_type is not read
                                    by this backend.

COM ports
  dut_uart
    device           COM3
    baudrate         115200
    encoding         utf-8
    serial_number    066AFF303435554157113106
    identity_source  serial_number
    permissions  granted: allow_write

CAN buses
  None configured.
```

Exit status 0. One ST-Link discovered, the probe named `dut`, the serial line
named `dut_uart`, and COM3 matched to that probe by serial number.

`doctor` reports neither `state_root` nor the reports and logs directories, in
its rendering or under `--json`, so the setting the refusal above turns on is
not visible in the command that is supposed to say the bench is healthy.

## The build

```
$ cmake --preset Debug
-- The C compiler identification is GNU 14.3.1
-- The ASM compiler identification is GNU
-- Found assembler: C:/ST/STM32CubeCLT_1.22.0/GNU-tools-for-STM32/bin/arm-none-eabi-gcc.exe
-- Configuring done (2.8s)
-- Generating done (0.0s)
-- Build files have been written to: C:/Users/mail/work/ahil-starter/build/Debug

$ cmake --build --preset Debug
[1/3] Building ASM object CMakeFiles/stm32-starter.dir/firmware/src/startup_stm32f446xx.S.obj
[2/3] Building C object CMakeFiles/stm32-starter.dir/firmware/src/main.c.obj
[3/3] Linking C executable stm32-starter.elf
Memory region         Used Size  Region Size  %age Used
           FLASH:         936 B       512 KB      0.18%
             RAM:           4 B       128 KB      0.00%
   text	   data	    bss	    dec	    hex	filename
    936	      0	      4	    940	    3ac	C:/Users/mail/work/ahil-starter/build/Debug/stm32-starter.elf
```

Both exited 0, on a `build/` deleted first so the image belongs to this commit.

## Item 16: the shipped firmware, two green and one red

Run on commit `5d9ed82`, ELF `383917046e...`. Reports and logs in
[shipped/](shipped/).

| Plan | Verdict | Run | Report |
|---|---|---|---|
| `tests/hil/nominal.testconfig.yaml` | `Test reactor sequence completed.` | `run-f8de7b2f5a29682d` | [shipped/nominal-report.json](shipped/nominal-report.json) |
| `tests/hil/recovery.testconfig.yaml` | `Test reactor sequence completed.` | `run-c06b8ff380e202e5` | [shipped/recovery-report.json](shipped/recovery-report.json) |
| `tests/hil/diagnostic.testconfig.yaml` | `Refused: comparator_unmet` | `run-6945203bd56cbbed` | [shipped/diagnostic-report-red.json](shipped/diagnostic-report-red.json) |

Two green, one red, and the red one is the diagnostic plan. No other plan is
red.

The first attempt at the nominal plan was refused before that, with
`flash_erase_failed` (`run-24d835430d618a6f`,
[shipped/nominal-flash-erase-refusal.json](shipped/nominal-flash-erase-refusal.json)).
The programmer's own transcript is in the report:

```
Connect mode: Hot Plug
...
Erasing memory corresponding to segment 0:
Erasing internal memory sector 0
Error: failed to erase memory
```

The refusal's guidance item 1 says to retry the flash once, that on the bench it
was measured on a core still executing from flash under hot plug defeated the
erase and every immediate retry programmed and verified, and that nothing has to
be recovered first. Its recovery block reported `outcome recovered`,
`incident_resolved yes`, `incident_open no`. The identical command was run once
more and programmed and verified, which is the green nominal run in the table.
The same refusal did not recur in any of the eight plan runs after it.

## Item 17: the failing report quotes what the board answered

From [shipped/diagnostic-report-red.json](shipped/diagnostic-report-red.json),
step 6:

```
    - 6
        route   dut_uart
        action  uart_read
        result
          Expected pattern did not match the COM port output before this step's
          timeout.
          error_type  comparator_unmet
          port_id                  dut_uart
          timeout_s                5.0
          bytes_received           39
          reads                    2
          received_tail_truncated  no
          comparator
            pattern  "state":"DEGRADED","diagnostic":"E_SELF_TEST"
          received_tail
            hex       7b227374617465223a225245414459222c22646961676e6f73746963223a224e4f4e45227d0d0a
            text      {"state":"READY","diagnostic":"NONE"}
            encoding  utf-8
```

The claim that went unmet and the line the board sent instead are both in the
report, in text and in hex. The COM log
[shipped/logs/com-20260903T203006320Z-dut_uart.jsonl](shipped/logs/com-20260903T203006320Z-dut_uart.jsonl)
carries the same exchange framed byte by byte: `DIAG ON\n` out, and
`{"state":"READY","diagnostic":"NONE"}\r\n` back.

## Item 18: the recovery plan's middle read

On the shipped firmware
([shipped/recovery-report.json](shipped/recovery-report.json), `run-c06b8ff380e202e5`)
the plan has three `uart_read` steps and each matched once:

| Step | Pattern | `bytes_received` | `reads` |
|---|---|---|---|
| 4 | `"event":"boot"` | 45 | 1 |
| 6 | `"state":"(READY\|DEGRADED)"` | 39 | 1 |
| 8 | `"state":"READY","diagnostic":"NONE"` | 39 | 1 |

Two status lines, one consumed by the middle read and one by the final read.
The COM log
[shipped/logs/com-20260903T202920762Z-dut_uart.jsonl](shipped/logs/com-20260903T202920762Z-dut_uart.jsonl)
shows which line each read took: the middle read took the answer to `DIAG ON`
and the final read the answer to `DIAG CLEAR`.

On the fixed firmware the two lines differ from each other, which settles it
without relying on byte counts.
[green-2/logs/com-20260903T203133988Z-dut_uart.jsonl](green-2/logs/com-20260903T203133988Z-dut_uart.jsonl):

```
rx  {"event":"boot","firmware":"stm32-starter"}\r\n
rx  {"state":"DEGRADED","diagnostic":"E_SELF_TEST"}\r\n
tx  DIAG ON\n
rx  {"state":"READY","diagnostic":"NONE"}\r\n
tx  DIAG CLEAR\n
```

The middle read consumed the `DEGRADED` line that `DIAG ON` produced, and the
final read the `READY` line that `DIAG CLEAR` produced, so the plan's claim is
about what `DIAG CLEAR` answered.

## Item 19: the defect and the fix

The protocol table in `README.md` says `DIAG ON` answers
`{"state":"DEGRADED","diagnostic":"E_SELF_TEST"}`. The firmware matched the
literal `DIAG ENABLE` instead, so `DIAG ON` fell through the command handler
without setting `diagnostic_active`, and `report_status` answered with the
`READY` branch, which is the line the red report quotes.

```diff
diff --git a/firmware/src/main.c b/firmware/src/main.c
index 1489f78..6b8ed68 100644
--- a/firmware/src/main.c
+++ b/firmware/src/main.c
@@ -99,7 +99,7 @@ static void report_status(void)
 
 static void handle_command(const char *command)
 {
-    if (text_equals(command, "DIAG ENABLE")) {
+    if (text_equals(command, "DIAG ON")) {
         diagnostic_active = true;
     } else if (text_equals(command, "DIAG CLEAR")) {
         diagnostic_active = false;
```

Nothing outside `firmware/` was touched: the plans in `tests/hil/`, the suite in
`tests/simulator/` and the protocol table in `README.md` are as they ship. The
fix is recorded here and not committed, because the starter ships the defect on
purpose; `git checkout -- firmware/` restored it after the second green run.

## Item 20: three green, then three green again

`cmake --build --preset Debug` on the fixed tree produced ELF
`facb8770d64f...`, and both runs below flashed that same image, which each
report names under `steps[].result.artifact.sha256`. Nothing was edited between
the two runs and nothing was rebuilt.

| Plan | Green run 1 | Green run 2 |
|---|---|---|
| nominal | `run-7873d97027383ca6` | `run-ea2499c6d046305a` |
| recovery | `run-b20c329117ab67c7` | `run-60ce556da742fc7d` |
| diagnostic | `run-20c12f4e561ac473` | `run-953e27f7b5a767b9` |

All six exited 0 with `Test reactor sequence completed.`

## Item 21: the retained evidence

- [shipped/](shipped/): three reports from commit `5d9ed82`, the
  `flash_erase_failed` refusal report, and fourteen backend and COM logs.
- [green-1/](green-1/): three reports and nine logs.
- [green-2/](green-2/): three reports and nine logs.

Each log is the file its report names under `log_path`, copied unchanged out of
`.agentic-hil/logs/`.

## Item 22: durations

Wall clock at the shell, one measurement each.

| Command | Wall clock |
|---|---|
| `uv sync` (environment already present) | 0.150 s |
| `uv run agentic-hil --version` | 0.453 s |
| `uv run agentic-hil init` (existing config kept) | 0.960 s |
| `uv run agentic-hil doctor` (before the repair) | 0.512 s |
| `cmake --preset Debug` (on a deleted `build/`) | 2.940 s |
| `cmake --build --preset Debug` (shipped firmware) | 0.419 s |
| `test-reactor nominal` (refused, `audit_unavailable`) | 0.793 s |
| `uv run agentic-hil init --force` | 0.981 s |
| `uv run agentic-hil doctor` (after the repair) | 0.519 s |
| `test-reactor nominal` (refused, `flash_erase_failed`) | 1.408 s |
| `test-reactor nominal` (retry, green) | 1.808 s |
| `test-reactor recovery` (green) | 1.774 s |
| `test-reactor diagnostic` (red, `comparator_unmet`) | 6.952 s |
| `cmake --build --preset Debug` (fixed firmware) | 0.292 s |
| green run 1: `test-reactor nominal` | 1.633 s |
| green run 1: `test-reactor recovery` | 1.737 s |
| green run 1: `test-reactor diagnostic` | 1.612 s |
| green run 2: `test-reactor nominal` | 1.651 s |
| green run 2: `test-reactor recovery` | 1.695 s |
| green run 2: `test-reactor diagnostic` | 1.604 s |

The red diagnostic run takes about five seconds longer than the others because
its failing read waits out the plan's own `timeout_s: 5.0`.

The walk started at 22:25:07 +02:00 and the first green hardware plan completed
at 22:28:45 +02:00: 3 minutes 38 seconds.

## Item 23 stays open

Item 23 asks for the whole path "from the one-line installer to the first green
hardware plan", walked by somebody who has not seen this repository before,
under four hours. The measured span above is 3 minutes 38 seconds, and it starts
later than the item does. What was already on this machine before the walk and
was therefore not measured:

- `uv`, STM32CubeCLT 1.22.0 and the project virtual environment.
- The Agentic HIL project configuration from the 2026-09-02 walk, whose
  `state_root` is what `init --force` repaired. A newcomer on a clean machine
  meets a different first command than this walk did.
- The one-line installer itself was not run, in this walk or the first. On this
  machine `doctor` reports `persistent no` and
  `No trusted persistent executable to register yet`, and rejects both
  workspace executables with `The MCP server command must not come from the
  workspace or a temporary/cache directory`, so the installer half of the item
  is not just unmeasured here, it is unresolved.

The four hour budget is not in question at these durations. The item is left
open because the span it names was not walked, and closing it would be a
judgement rather than a measurement.

## What was left standing

`uv run agentic-hil lease-status` after the last run:

```
  owner_active         no
  bench_held           no
  snapshot_atomic      yes
  blocked              no
  incident_stands      no
  auto_recoverable     no
  lifecycle_state      open

record
  state             released
  config_sha256     eab5dcf5f76d3b2969310e308d621896af104132cf3483f9f6e09ca819a19141
```

Nothing is held and nothing is quarantined. The board carries the fixed image
`facb8770d64f...` that green run 2 flashed and verified, running, not halted:
the last hardware action of that run was the plan's own reset into run mode.
The repository tree carries the shipped defect again.

## Findings for the product

1. `agentic-hil init` with no flag will not repair a configuration whose
   `state_root` the host cannot use. It reports `config skipped` with
   `Existing authoritative config, unchanged`, exits 0, and `doctor` then calls
   that bench healthy, because `doctor` never reads or reports `state_root`. The
   only thing that says something is wrong is the reactor, at the first hardware
   action. Nine commands on this walk were run against a configuration two of
   them had already declared sound.
2. The remediation that names the repair keys it on a field the refusal does not
   emit. Item 4 reads "When `field` is `state_root`", and there is no `field`
   anywhere in the refusal, in the rendering or in the `--json` document, which
   carries `error_type`, `path` and `resolved_parent` and nothing else. The
   reader has to infer that the offending path is the state root by comparing
   `path` against the configuration file, which the refusal also does not print.
3. `agentic-hil init --help` documents `--force` with no help text at all. The
   flag that is the repair for this failure is the one flag in that command with
   no description.
4. The `flash_erase_failed` refusal's guidance is long enough to obscure its own
   answer. Item 1 opens with the fix ("Retry the flash once"), then spends
   twenty lines on incident lifecycle and stand-down semantics before item 2
   starts. The retry worked first time.
5. The recovery block of the `unsafe_configured_path` refusal now says "The
   target confirmed the reset into halt, but the result could not be written to
   the audit record", which matches the reset log, and it carries
   `failed_check audit_ok`. On 0.21.0 the same block claimed the target did not
   confirm the reset while its own log showed `Core halted`, so that finding is
   addressed. The block still reports `outcome failed` and
   `failed_action reset_halt` next to a sentence saying the reset was confirmed.
6. The COM log JSONL is not ordered by its own timestamps. In every log of this
   walk the `tx` entry appears after the `rx` entries it caused, while carrying
   an earlier `time`. Reading a log top to bottom gives the wrong order of
   events unless the reader sorts by `time`.

## Newcomer notes on the starter

1. `README.md` and `AGENTS.md` both open with `agentic-hil setup`. On this
   machine the right first command is `agentic-hil init`, which `AGENTS.md`
   names only as what to do after a refusal. The 2026-09-02 walk reported the
   same thing and it is still true.
2. `validation/README.md` numbers no items, and its two readers have already
   numbered them differently: the 2026-09-02 note calls the `setup` box "Item
   17", while the box this note calls item 19 is the one that box's own reader
   would call 22. Two people saying "item 18" do not mean the same box. Numbering
   the boxes in the file would settle it.
3. A failed run leaves its logs in `.agentic-hil/logs/` inside the repository
   and its reports in `.agentic-hil/reports/`, while the audit state that
   decides whether the run may start at all lives under `state_root` outside it.
   The 2026-09-02 note asked for that to be stated in `AGENTS.md`, and it is
   still not.
4. `.agentic-hil/reports/` holds `last-report.json` and `last-failure.json`, and
   each run overwrites them. Item 21 asks for the reports of three separate runs
   to be retained, which means copying the file after every single run. Nothing
   in `README.md` or `AGENTS.md` warns about that, and a walker who runs all
   three plans first and collects evidence afterwards keeps one report out of
   three.
5. The reactor's report records the comparator pattern, the byte count and the
   number of reads for a read that matched, but not the text it matched. Only a
   failing read quotes what arrived. Item 18 is a claim about what two matching
   reads consumed, so on the shipped firmware it can only be shown from byte
   counts plus the COM log, not from the report alone.
