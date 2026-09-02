# Bench side gate, Windows, 2026-09-02

Evidence for the ten items under "Bench side, board required" in
[../README.md](../README.md), walked on Windows with a Nucleo-F446RE attached.

Two items closed. The walk then stopped at the first hardware plan, which was
refused before its first hardware action, and the eight items after it stay
open. The refusal is quoted verbatim below. Nothing was routed around it: the
authoritative configuration was not edited, `init --force` was not run,
`AGENTIC_HIL_CONFIG` was not set, and no debugger, serial device or CAN adapter
was opened outside Agentic HIL.

## Environment

| Item | Value |
|---|---|
| Date | 2026-09-02, walk started 10:03:00 +02:00 |
| OS | Microsoft Windows 11 Pro, 10.0.26200, 64 bit |
| Shell | Windows PowerShell 5.1, inside a packaged (MSIX) host |
| Clone | `C:\Users\mail\work\ahil-starter`, branch `validation/bench-gate` off `main`, commit `ddb35bd` |
| Agentic HIL | 0.21.0, from the project environment (`uv run agentic-hil`), package at `.venv\Lib\site-packages\agentic_hil` |
| uv | `uv 0.11.27 (19fc8b03b 2026-07-06 x86_64-pc-windows-msvc)` |
| CMake | `cmake version 4.3.1`, `C:\ST\STM32CubeCLT_1.22.0\CMake\bin\cmake.exe` |
| arm-none-eabi-gcc | `arm-none-eabi-gcc.exe (GNU Tools for STM32 14.3.rel1.20251027-0700) 14.3.1 20250623` |
| STM32CubeCLT | 1.22.0 |
| Debugger backend | `stlink`, `C:\ST\STM32CubeCLT_1.22.0\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe`, version `STM32CubeProgrammer 2.23.0`, interface SWD |
| Configuration | `C:\Users\mail\.agentic-hil\projects\ahil-starter-27c0fc5d4e\config.yaml` |
| Firmware revision built and attempted | `ddb35bdf4587653ef7ebd82946d7aca48807bd6f`, the shipped tree, unmodified |

The project environment was used for every Agentic HIL command because the
bench-wide `agentic-hil` on `PATH` is an older release held by other sessions on
this machine.

## Board identity

Reported by the backend through Agentic HIL, in the reset log both refused runs
left behind
([stlink-20260902T080556482Z-reset_target.log](stlink-20260902T080556482Z-reset_target.log)):

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

The backend command exited 0 and printed `Core halted`, so the probe and the
board were reachable throughout.

## Item 17: the configuration

Walked with `uv run agentic-hil init`, which is the project half of
`agentic-hil setup` and the route `AGENTS.md` names when the agent half is not
the agent's to write. `setup --agent` also rewrites the operator's agent
registrations on this machine, which is why it was not run. Discovery, COM port
matching and the generated names are the same code either way.

```
$ uv run agentic-hil init
Agentic HIL project configured.

  config_path  C:\Users\mail\.agentic-hil\projects\ahil-starter-27c0fc5d4e\config.yaml
  agent        none named
  scope        project

Steps
  config                   ok       Attached hardware was discovered and configured,
                                    with every permission granted except the two that
                                    are false so that flashing works.
  doctor                   ok       Agentic HIL configuration loaded and 1 debugger(s)
                                    checked.
  agent write restriction  skipped  No agent was named, so no agent write restriction
                                    was applied. Pass --agent to have that agent
                                    refuse its own write tools on the policy files.
```

Exit status 0. One ST-Link discovered, the probe named `dut`, the serial line
named `dut_uart`, and the COM port matched to that probe by serial number.

## Item 18: doctor reports the bench healthy

```
$ uv run agentic-hil doctor
Agentic HIL configuration loaded and 1 debugger(s) checked.

  config_path      C:\Users\mail\.agentic-hil\projects\ahil-starter-27c0fc5d4e\config.yaml
  state            unchanged
  loaded_digest    sha256:95a58f739f9970c3e188c18c8f180ef551bdf5e3e0f427bda7d2293b45e43c21
  reload_required  no
  The authoritative configuration on disk is byte-for-byte the one this server loaded.

Installation
  version       0.21.0
  package_path  C:\Users\mail\work\ahil-starter\.venv\Lib\site-packages\agentic_hil
  editable      no

Target
  name        nucleo-f446re-starter
  controller  stm32f446ret6

Debuggers
  dut (stlink, bound)
    probe_id     066AFF303435554157113106
    permissions  granted: allow_debug_execution, allow_flash, allow_reset; closed:
                 allow_mass_erase, allow_probe, allow_raw_debugger_commands
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
    permissions  granted: allow_write; closed: allow_read

CAN buses
  None configured.
```

Exit status 0. `--json` on the same command names the backend version:
`"version": "STM32CubeProgrammer 2.23.0"`.

The MCP registration section reported no persistent executable to register,
because the only Agentic HIL executables on this machine that resolve the
current release sit in the workspace virtual environment, and an MCP server
command may not come from the workspace. That blocks nothing in this walk: every
command below was run from the command line, which is the operator's own route.

## The build

```
$ cmake --preset Debug
-- The C compiler identification is GNU 14.3.1
-- Found assembler: C:/ST/STM32CubeCLT_1.22.0/GNU-tools-for-STM32/bin/arm-none-eabi-gcc.exe
-- Configuring done (0.6s)
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

Both exited 0, on a `build/Debug` deleted first so the image belongs to this
commit.

| Artifact | Bytes | SHA256 |
|---|---|---|
| `build/Debug/stm32-starter.elf` | 29856 | `383917046E3AA1608B29D3995184C72BC738A479C9B8D8441E4A59BC3C0E7D32` |

## The stop: the first hardware plan is refused

```
$ uv run agentic-hil test-reactor --test-config tests/hil/nominal.testconfig.yaml
Refused: audit_unavailable

  Test reactor sequence failed.

Details
  name              nucleo-f446re-nominal-status
  test_config_path  C:\Users\mail\work\ahil-starter\tests\hil\nominal.testconfig.yaml
  cleanup_ok        yes
  audit_ok          no
  retry_safe        no
  failed_step       1
  step_error_type   audit_unavailable
  run               run-dbd213e9ff0508f9
  steps
    - 1
        route   dut
        action  flash
        result
          Hardware action was not started because audit output is unavailable.
          error_type  audit_unavailable
          side_effect_committed  no
          audit_ok               no
          audit_error
            Configured file's parent directory resolves to a different location than
            it names.
            error_type  unsafe_configured_path
            path             C:\Users\mail\AppData\Local\agentic-hil\projects\32bea74e27467b193691a238\reports\report-state.json
            resolved_parent  C:\Users\mail\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\agentic-hil\projects\32bea74e27467b193691a238\reports
              1. Read `resolved_parent` first when the refusal carries one: the parent
                 of `path` resolves to that other spelling, and the resolved spelling
                 is the one that works. Point the setting at it, or at a location
                 outside the redirected tree. Do not go looking for a symlink; on this
                 profile there is none to find.
              2. Read `component` when the refusal carries one: that is the part of
                 the chain that stopped the walk, and there the object really is a
                 symlink or a file where a directory was needed. Replace it with a
                 real directory, or point the setting at a path that does not go
                 through it.
              3. C:\Users\mail\.agentic-hil is a location this tool creates for itself
                 and is a safe answer when the discovered default cannot be used.
                 `agentic-hil init` and `project_config_create` fall back to it on
                 their own for both the configuration and the state_root, so
                 re-running either is usually the whole fix.
              4. Re-run the command that failed. Nothing else has to change.
              5. Where each file may live: MCP resource
                 agentic-hil://reference/platform-paths.
              - do not: Do not delete or overwrite whatever stands at the named
                component. It is something the operator or another program put there,
                and the refusal is a report about the path, not a request to clear it.
              - do not: Do not move the authoritative configuration or state_root
                inside workspace_root to get past this. Both are refused there for a
                reason that has nothing to do with this failure: repository content
                would then be able to rewrite the policy that governs the hardware.
  audit_error
    Configured file's parent directory resolves to a different location than it names.
    error_type  unsafe_configured_path
    path             C:\Users\mail\AppData\Local\agentic-hil\projects\32bea74e27467b193691a238\reports\report-state.json
    resolved_parent  C:\Users\mail\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\agentic-hil\projects\32bea74e27467b193691a238\reports
      1. Read `resolved_parent` first when the refusal carries one: the parent of
         `path` resolves to that other spelling, and the resolved spelling is the one
         that works. Point the setting at it, or at a location outside the redirected
         tree. Do not go looking for a symlink; on this profile there is none to find.
      2. Read `component` when the refusal carries one: that is the part of the chain
         that stopped the walk, and there the object really is a symlink or a file
         where a directory was needed. Replace it with a real directory, or point the
         setting at a path that does not go through it.
      3. C:\Users\mail\.agentic-hil is a location this tool creates for itself and is
         a safe answer when the discovered default cannot be used. `agentic-hil init`
         and `project_config_create` fall back to it on their own for both the
         configuration and the state_root, so re-running either is usually the whole
         fix.
      4. Re-run the command that failed. Nothing else has to change.
      5. Where each file may live: MCP resource
         agentic-hil://reference/platform-paths.
      - do not: Do not delete or overwrite whatever stands at the named component. It
        is something the operator or another program put there, and the refusal is a
        report about the path, not a request to clear it.
      - do not: Do not move the authoritative configuration or state_root inside
        workspace_root to get past this. Both are refused there for a reason that has
        nothing to do with this failure: repository content would then be able to
        rewrite the policy that governs the hardware.
  audit_errors
    - no
        error_type       unsafe_configured_path
        summary          Configured file's parent directory resolves to a different
                         location than it names.
        path             C:\Users\mail\AppData\Local\agentic-hil\projects\32bea74e27467b193691a238\reports\report-state.json
        resolved_parent  C:\Users\mail\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\agentic-hil\projects\32bea74e27467b193691a238\reports
        remediation      Read `resolved_parent` first when the refusal carries one:
                         the parent of `path` resolves to that other spelling, and the
                         resolved spelling is the one that works. Point the setting at
                         it, or at a location outside the redirected tree. Do not go
                         looking for a symlink; on this profile there is none to
                         find., Read `component` when the refusal carries one: that is
                         the part of the chain that stopped the walk, and there the
                         object really is a symlink or a file where a directory was
                         needed. Replace it with a real directory, or point the
                         setting at a path that does not go through it.,
                         C:\Users\mail\.agentic-hil is a location this tool creates
                         for itself and is a safe answer when the discovered default
                         cannot be used. `agentic-hil init` and
                         `project_config_create` fall back to it on their own for both
                         the configuration and the state_root, so re-running either is
                         usually the whole fix., Re-run the command that failed.
                         Nothing else has to change., Where each file may live: MCP
                         resource agentic-hil://reference/platform-paths.
        do_not           Do not delete or overwrite whatever stands at the named
                         component. It is something the operator or another program
                         put there, and the refusal is a report about the path, not a
                         request to clear it., Do not move the authoritative
                         configuration or state_root inside workspace_root to get past
                         this. Both are refused there for a reason that has nothing to
                         do with this failure: repository content would then be able
                         to rewrite the policy that governs the hardware.
    - unsafe_configured_path
        summary        Configured file's parent directory resolves to a different
                       location than it names.
        backend_error  Configured file's parent directory resolves to a different
                       location than it names.
  recovery
    The target did not confirm a reset into halt, so the bench stays as the failed run
    left it.
    attempted                   yes
    actions                     reap_processes, reset_halt
    outcome                     failed
    devices                     dut
    auto_recover_policy         reset_halt
    auto_recover_policy_source  config
    failed_action               reset_halt
  config_in_force
    path                C:\Users\mail\.agentic-hil\projects\ahil-starter-27c0fc5d4e\config.yaml
    digest_algorithm    sha256
    digest              sha256:95a58f739f9970c3e188c18c8f180ef551bdf5e3e0f427bda7d2293b45e43c21
    description_source  startup
    file_state          unchanged
    file_digest         sha256:95a58f739f9970c3e188c18c8f180ef551bdf5e3e0f427bda7d2293b45e43c21
    diverged_from_file  no
    checked_at          2026-09-02T08:05:18Z
```

Exit status 1, quoted whole. The same error is stated three times in the one
result: under the failed step, again on its own, and a third time as the two
entries of `audit_errors`, whose first entry is rendered with `- no` where a
name is expected.

Remediation item 4 of that refusal says to re-run the command that failed and
that nothing else has to change, so the identical command was run once more,
with nothing changed. It came back with the same refusal, the same
`error_type`, the same two paths, and a new run id `run-3b3c29ae5d3087c3`. The
refusal is deterministic.

No plan ran, so no reactor report exists, on either side of the redirection. The
only hardware evidence either attempt produced is the pair of reset logs
retained beside this note.

### What the refusal is about

The configuration `init` wrote names two roots, and only one of them avoids the
redirected profile tree:

```
workspace_root: C:\Users\mail\work\ahil-starter
state_root: C:\Users\mail\AppData\Local\agentic-hil
```

The configuration file itself landed at
`C:\Users\mail\.agentic-hil\projects\ahil-starter-27c0fc5d4e\config.yaml`, which
is the fallback root the refusal's own item 3 names. The `state_root` beside it
was left pointing at `%LOCALAPPDATA%\agentic-hil`, which under this packaged
host resolves to
`C:\Users\mail\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Local\agentic-hil`.
The reactor writes its audit state under `state_root`, the safety check compares
the configured spelling with the resolved one, they differ, and the flash step
is refused before it starts.

So the fallback that item 3 describes was applied to the configuration and not
to the `state_root`, inside the one `init` run, and item 4 cannot hold while the
file still names the redirected root. Two other project configurations on this
machine, written earlier by other routes, name `state_root:
"C:/Users/mail/.agentic-hil/state"` and run on this same bench.

### What was left standing

`uv run agentic-hil lease-status` after the second refusal:

```
  owner_active         no
  bench_held           no
  snapshot_atomic      yes
  blocked              no
  incident_stands      no
  lifecycle_state      open
```

The bench is not quarantined and nothing is held. The board carries the firmware
a previous session flashed, with its core halted by the recovery reset, and no
image from this walk: both attempts were refused before the flash step ran.
`side_effect_committed  no` in the result above says the same. The core was left
halted because the command line has no reset subcommand and the MCP server was
not reachable in this session, and a raw debugger command was not an option.

## Durations

| Command | Wall clock |
|---|---|
| `uv sync` (environment already present) | 0.059 s |
| `uv run agentic-hil init` | 1.049 s |
| `uv run agentic-hil doctor` | 0.437 s |
| `cmake --preset Debug` | 0.657 s |
| `cmake --build --preset Debug` | 0.239 s |
| `uv run agentic-hil test-reactor --test-config tests/hil/nominal.testconfig.yaml` (refused) | 0.608 s |
| the same command again, unchanged (refused) | 0.634 s |

From the start of the walk to the stop: 5 minutes 17 seconds. There is no time
to the first green hardware plan, because there was none.

## What stayed open

- The three plans did not run, so nothing is known here about what the board
  answers, which plan is red, or what the red report quotes. The firmware was
  not diagnosed and not changed: the exercise starts from the failing report,
  and there is no failing report.
- No reactor report or run log exists to retain, and item 25 asks for the run
  facts to be recorded beside reports that were never written. The board
  identity, firmware revision, backend version, compiler version and durations
  are recorded above regardless.
- The four hour item stays open. It is about reaching a first green hardware
  plan, and this walk did not reach one.
- Everything under "Remote CI" stays open. Nothing in this walk touched a
  runner.

## Findings for the product

1. `agentic-hil init` 0.21.0, run inside a packaged host with a redirected
   profile, applies its fallback root to the configuration file and not to
   `state_root`, and the configuration it writes is then refused by the reactor
   at the first hardware action with `unsafe_configured_path`. The refusal is
   deterministic and reproduced twice.
2. The remediation the refusal prints does not resolve that state. Item 3 states
   that `init` falls back for both paths, which is what did not happen here, and
   item 4 says re-running the failed command is enough, which was tried once,
   unchanged, and refused identically. Plain `init` keeps a configuration that
   is already there, so re-running it changes nothing either.
3. The recovery block reported `outcome failed` and
   `The target did not confirm a reset into halt`, while the reset log that same
   recovery wrote shows the backend exiting 0 with `Core halted` on the
   configured probe. The two statements are about the same action.

## Newcomer notes on the starter

Written from the first walk of this repository, as issue material.

1. `agentic-hil.config.example.yaml` says the authoritative configuration lands
   at `%APPDATA%\agentic-hil\projects\<project-id>\config.yaml` on Windows. On
   this machine it landed at
   `C:\Users\mail\.agentic-hil\projects\ahil-starter-27c0fc5d4e\config.yaml`,
   which is neither `%APPDATA%` nor the `%LOCALAPPDATA%` the state root uses. A
   newcomer looking where the file says to look does not find it. The command
   prints the real path, which is what to trust.
2. `doctor` renders `closed: allow_probe` for the debugger and
   `closed: allow_read` for the COM port, on a configuration that `init` itself
   describes as having "every permission granted except the two that are false
   so that flashing works". Reading needs no grant in this configuration
   version, and both plans do read the port, so nothing is actually withheld,
   but the two renderings disagree and the reader has to know that to tell.
3. The configuration names `reports.directory` and `logs.directory` relative to
   the workspace, while the reactor's audit state lives under `state_root`
   outside it. A failed run therefore leaves logs in the repository tree and
   nothing where the reports are expected. Worth stating in `AGENTS.md`, since
   the first place a newcomer looks after a failure is `.agentic-hil/reports/`.
4. `README.md` and `AGENTS.md` both open with `agentic-hil setup`, which writes
   the operator's agent registrations as well as the project configuration.
   `AGENTS.md` names `init` only as what to do after a refusal. On a machine
   where the agent registrations belong to somebody else, `init` is the right
   first command and not the fallback, and neither document says so.
