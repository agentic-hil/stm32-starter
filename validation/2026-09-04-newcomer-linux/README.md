# Newcomer path, Linux, 2026-09-04

Evidence for box 14 in [../README.md](../README.md), "The whole path, from the one-line
installer to the first green hardware plan, is walked by somebody who has not seen this
repository before, and it takes under four hours."

Both passes below were walked by an automated agent following the public pages only, and
not by a human newcomer. What is measured here is the span, the commands it takes, and
where the pages fail a first reader. The box itself stays unticked, because the reader it
asks for is a person.

This is the first walk that starts where box 14 starts: at the one-line installer, on a
machine with no Agentic HIL on it, no configuration and no clone. The two earlier bench
walks began after those already existed, which is why both left this box open.

It was walked twice on the same board and the same host, minutes apart. Pass 1 followed the
public pages literally on the current release, 0.21.2, and stopped before the first hardware
action. Pass 2 repeated the identical walk on the development build, 0.21.3.dev0, and
reached the first green hardware plan in 47 seconds and all three plans in 71.

Only commands the public pages tell a reader to run were used: the starter's `README.md`
first, then the main project's `README.md`, `docs/installation.md` and `TROUBLESHOOTING.md`.
The pages were read from github.com and no local checkout was consulted. No debugger, serial
device or CAN adapter was opened outside Agentic HIL, and `AGENTIC_HIL_CONFIG` was never set.
Where a command failed, the fallback the page named was followed at most twice before the
stop was recorded.

## Environment

| Item | Value |
|---|---|
| Date | 2026-09-04, pass 1 started 20:55:11 UTC, pass 2 started 20:59:00 UTC |
| OS | Ubuntu 24.04.4 LTS, kernel 6.8.0 |
| Account | a fresh account with the README's prerequisites installed, no administrator rights and no way to gain them |
| Home | a home directory created for this walk, empty at the start: no earlier clone, no `~/.local/bin`, no Agentic HIL configuration. A second, equally empty one for pass 2 |
| Agentic HIL, pass 1 | 0.21.2, from the one-line installer |
| Agentic HIL, pass 2 | 0.21.3.dev0, from a wheel, installed with `uv tool install` where the pages would have installed the release |
| uv | 0.12.5 in pass 1 (fetched by the installer), 0.12.9 in pass 2 (fetched the way the pages describe) |
| Python | 3.12.3, with no `pip` module, which is the ordinary Ubuntu server shape |
| CMake | 3.28.3 |
| Compiler | `arm-none-eabi-gcc` 13.2.1 |
| Debugger backend | `openocd`, Open On-Chip Debugger 0.12.0, at a system path, SWD through the onboard ST-LINK |
| STM32CubeProgrammer | not installed |
| Clone | `fe695d3a30c6ea575df6663c963934be5cf19f41`, the same commit in both passes |
| Configuration | `~/.config/agentic-hil/projects/<project-id>/config.yaml`, written by `agentic-hil setup` in both passes |
| State root | `~/.local/state/agentic-hil`, `verdict ok` in both passes |

The prerequisites the README lists were installed on this host before the walk began:
OpenOCD, CMake, Ninja and the GNU Arm Embedded Toolchain, and the account was already in
`dialout` and `plugdev` so the probe and the serial port open without an administrator.
Nothing else was there. Installing those is outside box 14's span and was not measured.

## Board identity

As Agentic HIL reported it in `doctor` after pass 2's `setup`:

```
Target
  name        nucleo-f446re-starter
  controller  stm32f446ret6

Debuggers
  dut (openocd, bound)
    probe_id       066AFF303435554157113106
    interface_cfg  interface/stlink.cfg (search_name) resolved by openocd
    target_cfg     target/stm32f4x.cfg (search_name) resolved by openocd
    check           ok              OpenOCD is available.

COM ports
  dut_uart
    device           /dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066AFF303435554157113106-if02
    baudrate         115200
    serial_number    066AFF303435554157113106
    identity_source  serial_number
```

The same board the two Windows walks used, reached here through OpenOCD instead of
STM32CubeProgrammer, and named by its `/dev/serial/by-id/` symlink rather than by
`/dev/ttyACM0`. `doctor` printed no `warnings` block, because the probe carries its
`probe_id` and the port carries both a stable device name and a serial number.

## Firmware

`cmake --preset Debug` and `cmake --build --preset Debug` both exited 0 in both passes, on a
tree with no `build/` in it.

```
Memory region         Used Size  Region Size  %age Used
           FLASH:         936 B       512 KB      0.18%
             RAM:           4 B       128 KB      0.00%
   text	   data	    bss	    dec	    hex	filename
    936	      0	      4	    940	    3ac	build/Debug/stm32-starter.elf
```

`text` 936, the same figure the 2026-09-03 walk recorded on a different compiler on
Windows. The ELF the reactor flashed in pass 2 is
`402bdd4adeda2d2a02e90fb7614735f4dd243d24040ac73ad1c93c90f3688dda`, which every report of
that pass names under `steps[].result.artifact.sha256`.

## Pass 1, the release as a stranger gets it today

### The installer

`curl -LsSf https://agentic-hil.github.io/install.sh | sh` finished in 21 seconds with exit
0 and installed 0.21.2. The host's `python3` carries no `pip` module, which is what most
Ubuntu servers ship, and step 2 handled that by itself:

```
agentic-hil install: step 2/5  package: python3 has no pip module, so pip cannot install with it; falling back to uv
```

That is exactly what TROUBLESHOOTING 1a says it will do, and it did it without being asked.

Step 3 was wrong about the machine:

```
agentic-hil install: step 3/5  PATH: agentic-hil is installed in ~/.local/bin, already on your PATH
```

`~/.local/bin` was not on the shell's `PATH`, and `command -v agentic-hil` in a fresh shell
found nothing. The starter's `README.md` says of its own `export` line that it "is the one
the installer prints itself when `~/.local/bin` is not already on your `PATH`", so a reader
who takes step 3 at its word skips the export and meets `command not found`. TROUBLESHOOTING
1a has a bullet for a step 3 that reports the directory does not resolve, and none for a step
3 that claims it does when it does not. The walk was not stopped by this, because the code
block in that README carries the export unconditionally and a copy-paste reader runs it.
This is stop 1 in the table below, filed as agentic-hil#430.

### The plans with no board attached

```
$ uv sync
$ uv run pytest -q -s
PASS  configuration and test semantics validated in simulator
NEEDS PHYSICAL FIXTURE  electrical behavior not verified
...
3 passed in 1.15s
```

Green in two seconds, on the first try, with nothing to work around. This half of the
starter behaved exactly as documented in both passes.

### Stops 2 and 3: `setup` writes a placeholder while the board is attached, and `doctor` accepts it

```
$ agentic-hil setup --agent codex
Steps
  config  ok  No attached bench was found, so the placeholder Agentic HIL project
              configuration was written, with every permission granted except the two
              that are false so that flashing works.
```

Exit 0, and every one of the five steps says `ok`. The board was attached the whole time.
The configuration this wrote holds `target.name: "example-target"`,
`controller: "unknown-controller"`, `probe_id: null`, `executable: null` and `com_ports: {}`.

The `README.md` this walk read accounted for a placeholder only in the paragraph that began
"With no board attached that command is green anyway". A reader with a board on the desk had
no sentence to hold this against, and nothing in the output suggested stopping. That is #15,
and the commit that files this note rewrites the paragraph.

`agentic-hil doctor` then exited 0 on that configuration. It reported `example-target`,
`unknown-controller`, `probe_id  not set` and `COM ports  None configured`, and it did not
say that no plan can run against it. Following the README's own ordered command list, the
reader builds and runs a plan next.

### Stop 4: the placeholder becomes visible at the first plan

```
$ agentic-hil test-reactor --test-config tests/hil/nominal.testconfig.yaml
Refused: test_config_invalid
  validation_error
    Test step references a COM port that is not in the authoritative config.
    step    2
    field   steps[1].port_id
    route   dut_uart
    action  uart_open
```

The refusal is precise and it carries no next step. Unlike every other refusal in this walk
it prints no remediation block, and `test_config_invalid` appears in no section of
TROUBLESHOOTING.md. Its only occurrence in any page a reader is sent to is the starter
README's own sentence about a missing firmware artifact, which is a different cause. The
reader has to work out for themselves that `route dut_uart` means `com_ports` is empty and
that `setup` is where that happened.

TROUBLESHOOTING 5b is the section that matches, and it matches word for word: "the
configuration holds `probe_id: null`, `executable: null`, `target.controller:
"unknown-controller"` and no `com_ports` entry, and `doctor` skips the debugger check."

### Stop 5: `adopt-hardware` refuses on a host that has OpenOCD and the board

Following 5b's fix, first attempt:

```
$ agentic-hil adopt-hardware --dry-run
Refused: debugger_not_found

  STM32CubeProgrammer CLI was not found. Nothing was read out of the configuration and
  nothing was written.
```

The same output goes on to enumerate the attached board, with its serial number, its USB
ids and its stable device name:

```
      - /dev/ttyACM0
          description    STM32 STLink - ST-Link VCP Ctrl
          hwid           USB VID:PID=0483:374B SER=066AFF303435554157113106
          serial_number  066AFF303435554157113106
          stable_device  /dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066AFF303435554157113106-if02

Next step
  Attach the board this project drives, then call this again. Nothing was written.
```

The board is attached, the tool lists it, and the next step it names is to attach it.
OpenOCD 0.12.0 is installed and on `PATH`, and the configuration the tool itself wrote says
`type: "openocd"`.

TROUBLESHOOTING 4 states the opposite of what happened:

> discovery uses STM32CubeProgrammer's CLI where it is installed, and otherwise enumerates
> the ST-Link out of this host's USB serial inventory and drives it with the `openocd` on
> `PATH`. Installing OpenOCD alone is enough, and is the smaller of the two. The refusal
> carries `tools_searched`, which says which binaries were looked for and where each
> resolved.

OpenOCD alone was not enough on 0.21.2, and there is no `tools_searched` anywhere in the
refusal, in the rendering or beside it.

Second and last attempt, this time following section 4's own fix, "have the operator set
`debuggers.<name>.executable` in the authoritative config to an existing host-owned
executable outside the workspace", which is also what `doctor` printed under
`Debugger check`. One line of the authoritative configuration was changed:

```diff
-    executable: null
+    executable: "/usr/bin/openocd"
```

```
$ agentic-hil doctor
    check           ok              OpenOCD is available.

$ agentic-hil adopt-hardware --dry-run
Refused: debugger_not_found

  STM32CubeProgrammer CLI was not found.
```

`doctor` calls the backend available and `adopt-hardware` still looks for a different one.
Its discovery does not consult the configured backend at all.

`com_ports` was still empty, the plan was refused identically, and no documented command
fills that entry. **Pass 1 ended at 20:58:41 UTC, 3 minutes 29 seconds in, with no hardware
action ever attempted.** The only remaining route would be hand-writing a `com_ports` entry
into the authoritative configuration, which no page instructs and which 5b explicitly warns
against.

## Pass 2, the development build

The identical walk, in a second empty home, with 0.21.3.dev0 where the pages would have
installed the release. `uv` was fetched exactly as the starter's README describes it.

### `setup` finds the board

```
$ agentic-hil setup --agent codex
Steps
  config  ok  Attached hardware was discovered and configured, with every permission
              granted except the two that are false so that flashing works.
```

Same host, same OpenOCD, still no STM32CubeProgrammer. `doctor` afterwards reported
`nucleo-f446re-starter`, `stm32f446ret6`, the probe serial, `check ok  OpenOCD is
available.` and the `dut_uart` port bound to its `/dev/serial/by-id/` name with
`identity_source  serial_number`. Both stops of pass 1 are gone at their root.

### The three plans

| Plan | Verdict | Run |
|---|---|---|
| `tests/hil/nominal.testconfig.yaml` | `Test reactor sequence completed.` | `run-d48fd44bd2dd3629` |
| `tests/hil/diagnostic.testconfig.yaml` | `Refused: comparator_unmet` | `run-11f6c3e9ac414278` |
| `tests/hil/recovery.testconfig.yaml` | `Test reactor sequence completed.` | `run-d99c1dc46b4d4dec` |

Two green, one red, and the red one is the diagnostic plan, which is what the starter's
README says to expect. The nominal plan flashed and verified in 1278 ms on the first
attempt, with `success_confirmed yes`, `verify yes`, `lease_state released` and
`quarantined no`.

The diagnostic plan's step 6 names the claim and quotes the answer:

```
          error_type  comparator_unmet
          port_id                  dut_uart
          timeout_s                5.0
          bytes_received           39
          reads                    2
          comparator
            pattern  "state":"DEGRADED","diagnostic":"E_SELF_TEST"
          received_tail
            hex       7b227374617465223a225245414459222c22646961676e6f73746963223a224e4f4e45227d0d0a
            text      {"state":"READY","diagnostic":"NONE"}
            encoding  utf-8
```

Byte for byte the exchange the 2026-09-03 walk recorded, on a different operating system and
a different debugger backend.

Two things this pass settles for the boxes above it. Every run, refusals included, printed
its `canonical_report_path` under the operator's state root, so the three reports of three
runs survive without copying anything between them. And a read whose comparator matched now
quotes what it matched, which box 9 previously needed the COM log to show:

```
          Expected pattern matched the COM port output.
          bytes_received          45
          reads                   1
          comparator
            pattern  "event":"boot"
          matched_text
            hex       226576656e74223a22626f6f7422
            text      "event":"boot"
            encoding  utf-8
```

The reset step carried one honest warning worth recording, since a reader will meet it:

```
          Target reset with mode 'run'. OpenOCD printed 1 failure-worded line in a run
          its own success marker confirmed; they are carried verbatim in backend_warnings.
          success_confirmed      yes
          backend_warnings       Error: Error setting register pc
```

### What was left standing

```
$ agentic-hil lease-status
OK.
  owner_active         no
  bench_held           no
  snapshot_atomic      yes
  blocked              no
  incident_stands      no
  lifecycle_state      open
```

Nothing held, nothing quarantined. The board carries the shipped firmware with its
deliberate defect, running, not halted. No firmware fix was attempted in either pass:
box 14 is about reaching the first green plan, and the exercise is a separate box.

## Elapsed time

| Span | Pass 1 (0.21.2) | Pass 2 (0.21.3.dev0) |
|---|---|---|
| One-line installer or wheel install | 21 s | 21 s |
| Clone, `uv sync`, `uv run pytest` | 13 s | 12 s |
| `setup` and `doctor` | 14 s | 11 s |
| `cmake --preset` and `cmake --build` | 1 s | under 1 s |
| To the first green hardware plan | never reached | **47 s** |
| All three plans | never reached | 71 s |
| Walk ended | 3 min 29 s, stopped | 1 min 31 s, complete |

Box 14's budget is four hours. Pass 2 walked the whole span, from an empty home to a green
hardware plan on a real board, in 47 seconds. Pass 1 walked the same span on the released
version and did not reach a hardware action at all.

## Stops, in the order a reader meets them

| # | What stopped the reader | Page that failed them | 0.21.3.dev0 | Filed as |
|---|---|---|---|---|
| 1 | The installer's step 3 says `~/.local/bin` is "already on your PATH" when it is not | the starter README's sentence about that `export` line, and TROUBLESHOOTING 1a, which has a bullet only for the opposite case | not exercised | agentic-hil#430 |
| 2 | `setup` reports "No attached bench was found" and writes a placeholder with the board attached, exit 0, every step `ok` | the starter README described a placeholder only for the case where no board is attached | fixed | #15, for the paragraph |
| 3 | `doctor` exits 0 on that placeholder and does not say no plan can run against it | the starter README presents `doctor` as what validates the configuration and reports the devices it bound | did not arise | agentic-hil#433 |
| 4 | `test_config_invalid` refuses the first plan with no remediation and no next step | TROUBLESHOOTING.md has no section for `test_config_invalid` | still undocumented | agentic-hil#431 |
| 5 | `adopt-hardware` refuses with "STM32CubeProgrammer CLI was not found" while listing the attached board, and tells the reader to attach it | TROUBLESHOOTING 4: "Installing OpenOCD alone is enough" and "The refusal carries `tools_searched`" | fixed; `tools_searched` still absent | fixed by agentic-hil#423 |

## Friction points

1. `agentic-hil setup` on the release reports a green placeholder on an attached bench, and
   the two commands after it agree with it. Five commands were run against a configuration
   that could not work before anything said so, and the thing that finally said so was the
   test reactor, at the first plan. On the development build `setup` finds the board, so
   this is a released-version problem and not a design one.
2. `adopt-hardware`, the command TROUBLESHOOTING 5b names as the whole fix for a placeholder
   configuration, is the one command in the walk that cannot recover from it on the release.
   It refuses for a toolchain the configuration does not name and never looks at the one it
   does.
3. A refusal that tells the reader to do the thing they have already done is worse than a
   refusal with no advice. "Attach the board this project drives, then call this again",
   printed above a full description of the attached board, sends a reader to check cables.
4. `test_config_invalid` is the one refusal family in this walk with no remediation block,
   and it is the first refusal a newcomer meets. It is also absent from TROUBLESHOOTING.md.
   The two facts compound: there is nothing in the output to follow and nothing in the
   documentation to look up. Filed as agentic-hil#431.
5. `doctor` exiting 0 is the reader's go signal, and it exits 0 on a configuration with no
   probe, no controller and no COM port. It has no single line that says whether this bench
   can run a plan. Filed as agentic-hil#433.
6. The starter README's "What you need for the hardware run" named STM32CubeProgrammer CLI
   as "what `agentic-hil setup` looks for when it discovers your probe" and put OpenOCD
   after it, "once the configuration names it". On this host `setup` discovered the board
   through OpenOCD with no STM32CubeProgrammer installed, so the sentence understated
   OpenOCD rather than overstating it, and a Linux reader could go install a vendor tool
   they do not need. Filed as #15, and rewritten in the commit that files this note.
7. That same list named no Linux serial-access step. Opening the ST-LINK virtual COM port
   needs membership in `dialout` on Debian and Ubuntu, and TROUBLESHOOTING 11 calls that
   "the one setup step that may genuinely need an administrator once". A newcomer on a plain
   Ubuntu account is not in that group. This walk did not meet it, because the account
   already was, so it is recorded here rather than measured. Filed as #16, and the same
   commit adds the two groups and the `usermod` line to the prerequisites.
8. TROUBLESHOOTING 4 names `agentic-hil debugger-probes` alongside `init` and
   `adopt-hardware` as bootstrap discovery driven by "the `openocd` on `PATH`". On an
   `openocd` bench it refuses with `not_supported`, "OpenOCD cannot enumerate all connected
   probe IDs through a backend-independent command." The refusal is honest and the sentence
   that sent the reader there is not. Filed as agentic-hil#432.

## Box 14 stays open

Box 14 asks for the whole path, from the one-line installer to the first green hardware
plan, by somebody who has not seen this repository before, under four hours. Pass 2 walked
that exact span end to end in 47 seconds on 0.21.3.dev0, so the span itself is measured
rather than estimated. Pass 1 shows that the same span does not complete on 0.21.2 on a host
without STM32CubeProgrammer, which is the ordinary shape of a Linux bench.

Neither pass closes the box. Both were walked by an automated agent reading the public
pages, and the box asks for a person who has not seen this repository before. An agent that
follows a page literally is a good instrument for finding where the page is wrong and a poor
stand-in for a reader who would have guessed what it meant. The box waits for a human
newcomer, on a release that carries the fixes the stops above name.
