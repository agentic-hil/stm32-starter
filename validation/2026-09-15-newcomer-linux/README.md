# Newcomer path, Linux, 2026-09-15

Evidence for box 14 in [../README.md](../README.md), "The whole path, from the one-line
installer to the first green hardware plan, is walked by somebody who has not seen this
repository before, and it takes under four hours." It closes the Linux half of box 1 as a
by-product: a fresh clone plus `uv sync` succeeded on the way.

This walk was made by an automated agent following the public pages only, and not by a
human newcomer, exactly like [the walk of 2026-09-04](../2026-09-04-newcomer-linux/README.md).
What is measured is the span, the commands it takes, and where the pages fail a first
reader. The box itself stays unticked, because the reader it asks for is a person.

What this walk adds: the 2026-09-04 walk stopped at five points on the release of that
day, 0.21.2, and reached the first green plan only on the development build. This one ran
the release as the installer delivers it today, 0.21.5, met no stop, and reached the first
green hardware plan 2 minutes 54 seconds after the installer line, all three plans in
3 minutes 42 seconds, and, after the exercise, three green plans on one fixed firmware
revision 5 minutes 8 seconds after it. The twelve friction points below are all
non-blocking; one of them cost a retry.

Only commands the public pages tell a reader to run were used: the starter's `README.md`,
read from github.com, and nothing else. No local checkout was consulted, no debugger,
serial device or CAN adapter was opened outside Agentic HIL, `AGENTIC_HIL_CONFIG` was
never set, and no administrator right was used. Where the README says to say a sentence
to your agent, the commands the README lists as the ones the agent runs (the block under
"3. Watch it prove itself") were run by hand: no agent CLI drove anything. A `codex`
binary existed on the machine and the installer registered it, but it was never started.
So this walk tests the documented command path and the product, not the agent
integration.

## Environment

| Item | Value |
|---|---|
| Date | 2026-09-15, installer line at 21:35:59 UTC |
| OS | Ubuntu 24.04, x86_64 |
| Account | a fresh home directory with the default system `PATH`, every command run through a login shell in it: no earlier clone, no `~/.local/bin`, no Agentic HIL, no `uv`, no configuration. Verified before the installer: `command -v agentic-hil uv` found nothing |
| Agentic HIL | 0.21.5, from the one-line installer |
| uv | 0.12.10, fetched by the installer |
| Python | 3.12.3, with no `pip` module, the ordinary Ubuntu server shape |
| CMake | 3.28.3, with Ninja 1.11.1 |
| Compiler | `arm-none-eabi-gcc` 13.2.1 |
| Debugger backend | `openocd`, Open On-Chip Debugger 0.12.0, at a system path, SWD through the onboard ST-LINK |
| STM32CubeProgrammer | not installed |
| Clone | `ff2cc5c`, `Merge pull request #20 from agentic-hil/check-plan-wording` |
| Configuration | `~/.config/agentic-hil/projects/stm32-starter-da1f6d6135/config.yaml`, written by `agentic-hil setup`; [config.yaml](config.yaml) is a copy |
| State root | `~/.local/state/agentic-hil`, `verdict ok` |

The prerequisites the README lists were installed on this host before the walk began:
OpenOCD, CMake, Ninja, the GNU Arm Embedded Toolchain, git and curl, and the account was
already in `dialout` and `plugdev`, so the probe and the serial port open without an
administrator. Installing those, the re-login the group change forces and the replug the
README warns about are outside box 14's span, were not walked, and are the steps most
likely to cost a new Linux user time. The 2 minutes 54 seconds is the documented Agentic
HIL path on a machine that already meets the documented prerequisites, not the time from
a blank install.

## Board identity

As `agentic-hil doctor` reported it after `setup`, [doctor.txt](doctor.txt) in full:

```
Bench binding
  verdict  ok
  Every device this configuration declares names the hardware behind it.

Target
  name        nucleo-f446re-starter
  controller  stm32f446ret6

Debuggers
  dut (openocd, bound)
    probe_id       066BFF505050505050505050
    interface_cfg  interface/stlink.cfg (search_name) resolved by openocd
    target_cfg     target/stm32f4x.cfg (search_name) resolved by openocd
    permissions    granted: allow_debug_execution, allow_flash, allow_reset; closed:
                   allow_mass_erase, allow_raw_debugger_commands
    check           ok              OpenOCD is available.

COM ports
  dut_uart
    device           /dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066BFF505050505050505050-if02
    baudrate         115200
    encoding         utf-8
    serial_number    066BFF505050505050505050
    identity_source  serial_number
    permissions  granted: allow_write
```

The same board the earlier walks used, discovered with no vendor tool present: `setup`
looked for `STM32_Programmer_CLI`, found none, found `openocd` at `/usr/bin/openocd`,
and took the probe out of the host's USB serial inventory, which is the path the README
describes for a Linux bench with OpenOCD. It bound the port by its `/dev/serial/by-id/`
symlink and by serial number, and the nominal plan re-confirmed that identity at runtime
(`status confirmed`, `found_serial_number 066BFF505050505050505050`). `setup` also wrote
down what that discovery cannot see, unprompted, as `probe_inventory: incomplete` with a
note that a probe publishing no virtual COM port would be invisible to it, and named the
two commands that settle it.

## Firmware

`cmake --preset Debug` and `cmake --build --preset Debug` both exited 0 on a tree with no
`build/` in it, [build.txt](build.txt):

```
Memory region         Used Size  Region Size  %age Used
           FLASH:         936 B       512 KB      0.18%
             RAM:           4 B       128 KB      0.00%
```

`text` 936, the figure the 2026-09-03 and 2026-09-04 walks recorded. After the exercise
fix the image is 932 bytes.

## The walk

Timestamps are `date -u` immediately before and after each command. Every command ran
from `~/stm32-starter` except the installer and the clone, which ran from `~`.

| UTC | Command | Result |
|---|---|---|
| 21:34:57 | `command -v agentic-hil uv` | nothing found |
| 21:35:59 | `curl -LsSf https://agentic-hil.github.io/install.sh \| sh` | exit 0, the clock starts |
| 21:36:04 | installer done | uv 0.12.10 and agentic-hil 0.21.5 in `~/.local/bin`, codex registered |
| 21:36:09 | new login shell, `command -v agentic-hil uv` | nothing found (friction 2) |
| 21:36:10 | `export PATH="$HOME/.local/bin:$PATH"`, the README's line | found, `0.21.5` |
| 21:36:52 | `git clone https://github.com/agentic-hil/stm32-starter.git` | exit 0, `ff2cc5c` |
| 21:37:17 | `uv sync` | exit 0, 14 packages |
| 21:37:17 | `uv run pytest -q -s` | exit 0, `3 passed in 1.11s` |
| 21:38:01 | `agentic-hil setup --agent codex` | exit 0, ST-LINK discovered and bound |
| 21:38:19 | `agentic-hil doctor` | exit 0, `verdict ok` |
| 21:38:35 | `cmake --preset Debug` | exit 0 |
| 21:38:36 | `cmake --build --preset Debug` | exit 0 |
| 21:38:50 | `agentic-hil test-reactor --test-config tests/hil/nominal.testconfig.yaml` | |
| 21:38:53 | nominal finished | exit 0, green, the clock stops |
| 21:39:15 | `agentic-hil test-reactor --test-config tests/hil/diagnostic.testconfig.yaml` | |
| 21:39:23 | diagnostic finished | exit 1, `comparator_unmet`, the documented red |
| 21:39:38 | `agentic-hil test-reactor --test-config tests/hil/recovery.testconfig.yaml` | |
| 21:39:41 | recovery finished | exit 0, green |
| 21:40:43 | exercise: one line in `firmware/src/main.c`, then `cmake --build --preset Debug` | exit 0 |
| 21:40:58 to 21:41:07 | the three plans again on the fixed firmware | three green |
| 21:41:24 | `agentic-hil lease-status` | nothing held, no incident |
| 21:41:25 | `agentic-hil doctor` | exit 0 |

| Milestone | Elapsed from the installer line |
|---|---|
| Installer done | 5 s |
| Board-free suite green | 1 min 21 s |
| `doctor` green | 2 min 20 s |
| First green hardware plan | 2 min 54 s |
| Third plan done | 3 min 42 s |
| Three green plans on the fixed firmware | 5 min 8 s |

## The three plans

The README says two of the three go green and `tests/hil/diagnostic.testconfig.yaml`
does not, "and its report names the claim that went unmet and quotes what the board
answered instead". That is what happened. Each run printed the path of the report it
keeps under the state root, and [reports/](reports/) holds all six.

**nominal**, [nominal.txt](nominal.txt), [reports/run-1-nominal.json](reports/run-1-nominal.json):
exit 0, `ok: true`, six steps, `cleanup_ok yes`, `audit_ok yes`. The read that
establishes the board answered:

```
        comparator
          pattern  "state":"READY","diagnostic":"NONE"
        matched_text
          text      "state":"READY","diagnostic":"NONE"
```

**diagnostic**, [diagnostic.txt](diagnostic.txt), [reports/run-2-diagnostic.json](reports/run-2-diagnostic.json):
exit 1, `ok: false`, `failed_step 6`, `step_error_type comparator_unmet`:

```
          Expected pattern did not match the COM port output before this step's
          timeout.
          error_type  comparator_unmet
          comparator
            pattern  "state":"DEGRADED","diagnostic":"E_SELF_TEST"
          received_tail
            text      {"state":"READY","diagnostic":"NONE"}
```

The unmet claim is named and what the board said instead is quoted, which is the README's
sentence met word for word, and `comparator_unmet` is the error type
`.github/workflows/hardware-test.yml` asserts by name. The reactor then recovered the
bench on its own:

```
  recovery
    attempted                   yes
    actions                     reap_processes, reset_halt, probe_target
    outcome                     recovered
    incident_resolved           no
    incident_open               no
```

**recovery**, [recovery.txt](recovery.txt), [reports/run-3-recovery.json](reports/run-3-recovery.json):
exit 0, `ok: true`, `cleanup_ok yes`, `audit_ok yes`.

After the exercise, the same three plans on one firmware revision:
[reports/run-4-nominal-after-fix.json](reports/run-4-nominal-after-fix.json),
[reports/run-5-diagnostic-after-fix.json](reports/run-5-diagnostic-after-fix.json) and
[reports/run-6-recovery-after-fix.json](reports/run-6-recovery-after-fix.json), all
`ok: true`; the full output is in [rerun-nominal.txt](rerun-nominal.txt),
[rerun-diagnostic.txt](rerun-diagnostic.txt) and [rerun-recovery.txt](rerun-recovery.txt).

## What went right

**The installer.** One line, five labelled steps, five seconds, no administrator right,
[install.txt](install.txt). It diagnosed a Python with no `pip` module and fetched `uv`
itself:

```
agentic-hil install: step 2/5  package: python3 has no pip module, so pip cannot install with it; falling back to uv
```

It found the one agent CLI on the `PATH` and registered it without being told, and it
said what it did about the `PATH`:

```
agentic-hil install: step 3/5  PATH: agentic-hil landed in ~/.local/bin, which is not on your PATH
agentic-hil install: PATH: added one line to ~/.bashrc, so the next shell you open finds the command; this run already has it
agentic-hil install: step 4/5  agent: registering the skill and the MCP server for codex
agentic-hil install: agent: codex registered (skill and MCP server, restart pending)
agentic-hil install: step 5/5  restart: no agent CLI of yours is running, so there is nothing to restart
```

**Discovery with no vendor tool**, [setup.txt](setup.txt):

```
     2. Discovery looked for STM32_Programmer_CLI
        (STM32CubeProgrammer): not on this host;
        openocd (OpenOCD): found at /usr/bin/openocd.
        ST-Link serial port(s) on this host:
        066BFF505050505050505050 on
        /dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066BFF505050505050505050-if02.
```

**The order the README insists on held.** `doctor` before `setup` is documented to refuse
with `config_file_not_found`, and a plan before a build with `test_config_invalid:
Firmware artifact does not exist`. Following the documented order, neither was ever met,
and that is why they are absent from the friction list.

**The board-free half is board-free and fast**: `uv sync` plus `uv run pytest -q -s` in
three seconds, [check-plan-suite.txt](check-plan-suite.txt), every test stating its own
worth exactly as the README quotes it.

**A green run left nothing standing**, and the failing plan closed its port in cleanup
and recovered the probe without being asked.

## Friction

Twelve points, none blocking. Number 2 is the one that cost a retry. Each quotes the
decisive line.

### 1. The `uv sync` section comes before the clone that makes it possible

The README's order is: install, then "Run the plans with no board attached", then the
hardware prerequisites, then "Three steps", whose step 1 is the clone. The board-free
section opens with `uv sync`, and there is nothing to sync yet, because the repository
has not been cloned at that point in the text; the section reinforces the order with
"is the first thing to run whether or not a Nucleo is on your desk". A reader following
the page top to bottom runs `uv sync` in their home directory. This walk jumped ahead to
the clone and came back. The commit that files this note says so in that section.

### 2. The installer says the next shell will find the command. It did not.

The installer printed:

```
agentic-hil install: PATH: added one line to ~/.bashrc, so the next shell you open finds the command; this run already has it
```

The next login shell did not find it:

```
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin
command -v agentic-hil uv  ->  cmdv_exit=1
```

A login shell reads `~/.profile`, not `~/.bashrc`, and the bridge between the two, a
`~/.profile` that sources `~/.bashrc`, did not exist in this fresh home directory. In
fairness, `/etc/skel/.profile` on this distribution carries that bridge, so an account
created with `useradd -m` would have it, and the installer's sentence would hold for an
interactive terminal; this simulated home lacked the skeleton, which is a limitation of
this evidence rather than proof of a defect. Two things survive the caveat: the promise
depends on a distribution convention the installer does not check, and Ubuntu's stock
`~/.bashrc` returns early for non-interactive shells, so an appended line there does not
reach `ssh host 'agentic-hil doctor'` or a CI step even on a stock account. The README's
own `export PATH="$HOME/.local/bin:$PATH"` fixed it at once.

### 3. The README says the installer prints the `export` line. It does not.

"The `export` line in the first block is the one the installer prints itself when
`~/.local/bin` is not already on your `PATH`." The directory was not on the `PATH`, and
the installer printed no `export` line: it printed the two `step 3/5 PATH:` lines above,
which say it edited `~/.bashrc`. The `export` line in the README block is the README's,
and it works. Reworded in the commit that files this note.

### 4. The README's account of the `uv` fallback runs the other way round

"The one-line installer above may or may not have left you with `uv`, since it falls back
to `pip --user` where `uv` is absent." Here `uv` was absent and the installer fetched
`uv`, because the Python had no `pip` module. What the reader needs to know is whether
`uv` is there afterwards; here it was, in `~/.local/bin`, and the README's claim that the
`export` line "puts `uv` within reach as well" was right. Reworded in the commit that
files this note.

### 5. `setup` asks for the DUT UART it has already bound

Advice item 10 from `agentic-hil setup`:

```
    10. Detected COM ports: /dev/ttyS31, /dev/ttyS30,
        /dev/ttyS29, /dev/ttyS28, /dev/ttyS27, and 28
        more. Add the DUT UART under com_ports if
        serial feedback is needed.
```

The configuration the same command had just written already held `com_ports.dut_uart` on
the ST-LINK's `by-id` device. The instruction asks for work that is done, and the five
ports it samples are legacy `/dev/ttyS*` placeholders, so the one port that matters is
not among them, which reads at first glance as "it did not find your board". Product
side, in agentic-hil.

### 6. `setup` prints the same paragraph twice

The `config` step's headline text and numbered item 1 beneath it are the same ninety
words, character for character, beginning `'066BFF505050505050505050' is the one ST-Link
this host's USB serial inventory shows`. Product side.

### 7. A green step carries the word `Error`

Step 3 of the nominal plan, on a run that passed:

```
        Target reset with mode 'run'. OpenOCD printed 1 failure-worded line in a run
        its own success marker confirmed; they are carried verbatim in
        backend_warnings.
        success_confirmed      yes
        backend_warnings       Error: Error setting register pc
```

Handled as well as it can be: quoted rather than swallowed, explained, and the step says
`success_confirmed yes`. It is listed because a first-time reader scanning a green run
stops at `Error: Error setting register pc`. Nothing to fix in the product.

### 8. "the reactor's report under `.agentic-hil/reports/`" is not where three reports are

The exercise section says the evidence is "the reactor's report under
`.agentic-hil/reports/`". After three plans that directory held `last-report.json`, the
third plan only, and `last-failure.json`; the first two were overwritten. The reports
that persist are the ones each run prints and keeps under the state root, and the run
says so every time: "This run's own report is kept at
~/.local/state/agentic-hil/projects/<project>/reports/runs/run-<id>.json; later runs do
not overwrite it." The product is right and the README sentence points at the wrong
directory. Reworded in the commit that files this note.

### 9. Nothing says what to pass to `--agent` when your agent is not one of the three

`agentic-hil setup --help` lists `--agent AGENT` with no choices, no default and no word
on what happens when it is omitted. Here the answer was inferable because the installer
had named `codex` in its own step 4, and `--agent codex` worked. A reader whose installer
registered two agents, or none, has to guess. Product side.

### 10. The `init` versus `setup` decision is described in terms a newcomer cannot evaluate

"when the agent registrations belong to somebody else, on a shared bench or under a CI
runner's user, `agentic-hil init` is the first command instead". The distinction is about
who owns the agent registrations in this home directory, not about who else uses the
machine, and "on a shared bench" invites the wrong reading: this walk's home directory
was its own, so `setup` was right, and the sentence made that a decision rather than a
step. Reworded in the commit that files this note.

### 11. Two Agentic HIL versions end up on the machine, unremarked

The installer put 0.21.5 in `~/.local/bin`. `uv sync` then built the project environment
from the committed lock file with 0.21.2 inside it. Both are right and do different jobs,
the one on the `PATH` runs the hardware and the pinned one backs the check-plan suite,
but nothing told a newcomer that two versions are expected, and `doctor` reports only
its own. One sentence added in the commit that files this note.

### 12. The one administrator step could not be exercised

`sudo usermod -aG plugdev,dialout "$USER"`, the re-login and the replug were already
satisfied on this bench and were never walked, and neither was the udev rule. This walk
says nothing about them either way.

## End state

Checked after the last hardware command with the product's own command from inside the
clone, [end-state.txt](end-state.txt):

```
Nothing on this bench is held and no incident is standing.
  project_resource     project:4e20753d6572c68da4f78f98d24a6c82de983111a65c588dad64f41f797b4e23
  owner_active         no
  bench_held           no
  snapshot_atomic      yes
  blocked              no
  incident_stands      no
  auto_recoverable     no
  auto_recover_policy  reset_halt
  lifecycle_state      open
record
  version              2
  state                released
  frontend             reactor
  resources            com:serial:066bff505050505050505050
  updated_at           2026-09-15T21:41:07.061Z
```

No recovery command was needed, nothing was cleared by hand and no state file was
touched. A final `agentic-hil doctor` exited 0 with `verdict ok`. All use of the board
ended at 21:41:25 UTC.

## The exercise

Done, as the README hands it to the agent, with the person at the keyboard in the agent's
place. The failing report pointed at one command: `DIAG ON` produced
`{"state":"READY","diagnostic":"NONE"}` while `STATUS` and `DIAG CLEAR` behaved.
`firmware/src/main.c` matched a literal the documented protocol never sends,
[exercise-fix.diff](exercise-fix.diff):

```c
-    if (text_equals(command, "DIAG ENABLE")) {
+    if (text_equals(command, "DIAG ON")) {
```

`DIAG ON` had fallen through both branches to `report_status()` with `diagnostic_active`
still false, which is exactly the `received_tail` the report quoted. One string literal
changed, no test plan and no protocol touched, `git status --short` one line. Rebuild,
three plans, three green on one revision; the step that had failed:

```
          comparator
            pattern  "state":"DEGRADED","diagnostic":"E_SELF_TEST"
          matched_text
            text      "state":"DEGRADED","diagnostic":"E_SELF_TEST"
```

From reading the failing report to three green plans: under ninety seconds. Everything
stayed inside the clone, uncommitted.

## Files

| File | What it is |
|---|---|
| [install.txt](install.txt) | the installer's full output |
| [path-and-clone.txt](path-and-clone.txt) | the `PATH` check, the README's remedy, the versions, the clone |
| [check-plan-suite.txt](check-plan-suite.txt) | `uv sync` and the board-free suite |
| [setup.txt](setup.txt), [doctor.txt](doctor.txt) | `agentic-hil setup --agent codex` and `agentic-hil doctor`, in full |
| [config.yaml](config.yaml) | the configuration `setup` wrote |
| [build.txt](build.txt) | the CMake configure and build log |
| [nominal.txt](nominal.txt), [diagnostic.txt](diagnostic.txt), [recovery.txt](recovery.txt) | the three plan runs |
| [exercise-fix.diff](exercise-fix.diff) | the one-line firmware fix |
| [rerun-nominal.txt](rerun-nominal.txt), [rerun-diagnostic.txt](rerun-diagnostic.txt), [rerun-recovery.txt](rerun-recovery.txt) | the three plans on the fixed firmware |
| [end-state.txt](end-state.txt) | `lease-status` and the final `doctor` |
| [reports/](reports/) | the six JSON reports the runs kept under the state root |

Every file is verbatim, with two substitutions: the walk's home directory is written as
`~`, and the account name is removed from directory listings.
