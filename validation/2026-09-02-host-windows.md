# Host side gate, Windows, 2026-09-02

Evidence for the four items under "Host side, no board required" in
[README.md](README.md), walked on Windows from a fresh clone. No board was
attached. No hardware path was exercised: `agentic-hil setup`, `agentic-hil
init`, `agentic-hil doctor` and `agentic-hil test-reactor` were not run, and no
debugger, serial device or CAN adapter was opened.

## Environment

| Item | Value |
|---|---|
| Date | 2026-09-02 |
| OS | Microsoft Windows 11 Pro, 10.0.26200.9168, 25H2, 64 bit |
| Shells | Git Bash (MSYS2) for items 1 to 4, Windows PowerShell 5.1 for the second byte comparison |
| Clone | fresh clone of `agentic-hil/stm32-starter`, branch `validation/host-gate`, commit `7930720` |
| uv | `uv 0.11.27 (19fc8b03b 2026-07-06 x86_64-pc-windows-msvc)`, `C:\Users\mail\.local\bin\uv.exe` |
| Python | CPython 3.13.14, virtual environment created by `uv sync` |
| CMake | `cmake version 4.3.1`, `C:\ST\STM32CubeCLT_1.22.0\CMake\bin\cmake.exe` |
| Ninja | `1.13.2`, `C:\ST\STM32CubeCLT_1.22.0\Ninja\bin\ninja.exe` |
| arm-none-eabi-gcc | `arm-none-eabi-gcc.exe (GNU Tools for STM32 14.3.rel1.20251027-0700) 14.3.1 20250623`, `C:\ST\STM32CubeCLT_1.22.0\GNU-tools-for-STM32\bin\arm-none-eabi-gcc.exe` |
| STM32CubeCLT | 1.22.0, supplies all three build tools above |

## Item 1: fresh clone plus `uv sync`

Windows only. The Linux and macOS halves of this item were not walked and stay
open.

```
$ uv sync
Using CPython 3.13.14
Creating virtual environment at: .venv
Resolved 19 packages in 15ms
Installed 14 packages in 329ms
 + agentic-hil==0.16.0
 + attrs==26.1.0
 + colorama==0.4.6
 + iniconfig==2.3.0
 + jsonschema==4.26.0
 + jsonschema-specifications==2025.9.1
 + packaging==26.3
 + pluggy==1.6.0
 + pygments==2.21.0
 + pyserial==3.5
 + pytest==9.1.1
 + pyyaml==6.0.3
 + referencing==0.37.0
 + rpds-py==2026.6.3
```

Exit status 0. 14 packages installed, `agentic-hil==0.16.0` among them, which
satisfies the `agentic-hil>=0.16.0` floor in `pyproject.toml`.

Wall clock, measured on a repeat run after deleting `.venv`, with the uv package
cache warm: `real 0m0.414s`.

The virtual environment `uv sync` creates on Windows has `.venv/Scripts/` and no
`.venv/bin/`.

## Item 2: the three simulator tests and the scope statement

```
$ uv run pytest -s
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\mail\work\ahil-starter
configfile: pyproject.toml
testpaths: tests/simulator
plugins: agentic-hil-0.16.0
collected 3 items

tests\simulator\test_hardware_plans.py PASS  configuration and test semantics validated in simulator
NEEDS PHYSICAL FIXTURE  electrical behavior not verified
.PASS  configuration and test semantics validated in simulator
NEEDS PHYSICAL FIXTURE  electrical behavior not verified
.PASS  configuration and test semantics validated in simulator
NEEDS PHYSICAL FIXTURE  electrical behavior not verified
.

============================== 3 passed in 1.20s ==============================
```

Summary line: `3 passed in 1.20s`. Exit status 0.

The scope statement printed once per test case, three times in total, verbatim:

```
PASS  configuration and test semantics validated in simulator
NEEDS PHYSICAL FIXTURE  electrical behavior not verified
```

Wall clock `real 0m4.345s`, of which pytest reported 1.20s.

## Item 3: fresh report identical to `expected/simulator-junit.xml`

The three commands from [expected/README.md](../expected/README.md), run in Git
Bash, which is the route that README names for Windows.

```
$ uv run pytest -q -s --junitxml=artifacts/simulator-junit.xml
[scope statement, three times, as above]
3 passed in 0.62s
```

Exit status 0. Wall clock `real 0m1.123s`.

```
$ uv run python - artifacts/simulator-junit.xml <<'PY'
[the normalisation script from expected/README.md, unchanged]
PY
```

Exit status 0.

```
$ diff artifacts/simulator-junit.xml expected/simulator-junit.xml
$ echo $?
0
```

`diff` printed nothing and exited 0, which `expected/README.md` names as the
pass.

Second, independent comparison with the PowerShell route the same README names:

```
PS> fc.exe /b artifacts\simulator-junit.xml expected\simulator-junit.xml
Vergleichen der Dateien ARTIFACTS\simulator-junit.xml und EXPECTED\SIMULATOR-JUNIT.XML
FC: Keine Unterschiede gefunden
```

Exit status 0. ("No differences encountered", German system locale.)

| File | Bytes | SHA256 |
|---|---|---|
| `artifacts/simulator-junit.xml` | 619 | `5991B868360DDDCA8E68C7171A3975566ADFBC237A6DFAF4098E5757590A5D20` |
| `expected/simulator-junit.xml` | 619 | `5991B868360DDDCA8E68C7171A3975566ADFBC237A6DFAF4098E5757590A5D20` |

`artifacts/` is gitignored, so the generated report was not committed.

## Item 4: the `Debug` and `Release` presets

Both presets configured and built with `arm-none-eabi-gcc` from STM32CubeCLT
1.22.0. Both configure runs reported the same compiler:

```
-- The C compiler identification is GNU 14.3.1
-- Found assembler: C:/ST/STM32CubeCLT_1.22.0/GNU-tools-for-STM32/bin/arm-none-eabi-gcc.exe
```

```
$ cmake --preset Debug
-- Configuring done (3.3s)
-- Generating done (0.0s)
-- Build files have been written to: C:/Users/mail/work/ahil-starter/build/Debug

$ cmake --build --preset Debug
[1/3] Building ASM object CMakeFiles/stm32-starter.dir/firmware/src/startup_stm32f446xx.S.obj
[2/3] Building C object CMakeFiles/stm32-starter.dir/firmware/src/main.c.obj
[3/3] Linking C executable stm32-starter.elf
Memory region         Used Size  Region Size  %age Used
           FLASH:         936 B       512 KB      0.18%
             RAM:           4 B       128 KB      0.00%
```

```
$ cmake --preset Release
-- Configuring done (0.6s)
-- Generating done (0.0s)
-- Build files have been written to: C:/Users/mail/work/ahil-starter/build/Release

$ cmake --build --preset Release
[1/3] Building ASM object CMakeFiles/stm32-starter.dir/firmware/src/startup_stm32f446xx.S.obj
[2/3] Building C object CMakeFiles/stm32-starter.dir/firmware/src/main.c.obj
[3/3] Linking C executable stm32-starter.elf
Memory region         Used Size  Region Size  %age Used
           FLASH:         620 B       512 KB      0.12%
             RAM:           4 B       128 KB      0.00%
```

All four commands exited 0.

The image path: `tests/hil/nominal.testconfig.yaml:23`,
`tests/hil/diagnostic.testconfig.yaml:16` and
`tests/hil/recovery.testconfig.yaml:21` each name
`image_path: build/Debug/stm32-starter.elf`. That file exists after the Debug
build.

| Artifact | Bytes | text | data | bss | dec |
|---|---|---|---|---|---|
| `build/Debug/stm32-starter.elf` | 29856 | 936 | 0 | 4 | 940 |
| `build/Release/stm32-starter.elf` | 5952 | 620 | 0 | 4 | 624 |

`arm-none-eabi-readelf -h build/Debug/stm32-starter.elf`:

```
  Class:                             ELF32
  Data:                              2's complement, little endian
  Type:                              EXEC (Executable file)
  Machine:                           ARM
  Entry point address:               0x80002bd
  Flags:                             0x5000400, Version5 EABI, hard-float ABI
```

`build/` is gitignored, so no build output was committed.

## Durations

| Command | Wall clock |
|---|---|
| `uv sync` (repeat run, `.venv` deleted, package cache warm) | 0.414 s |
| `uv run pytest -s` | 4.345 s |
| `uv run pytest -q -s --junitxml=artifacts/simulator-junit.xml` | 1.123 s |
| `cmake --preset Debug` | 3.385 s |
| `cmake --build --preset Debug` | 0.443 s |
| `cmake --preset Release` | 0.683 s |
| `cmake --build --preset Release` | 0.284 s |

## What stayed open

- Item 1 is closed for Windows only. Linux and macOS were not walked from this
  machine and that half of the item stays open.
- Every item under "Bench side, board required" and under "Remote CI" stays
  open. No board was attached.

## Documentation defects found while walking this

Both are Windows instructions that do not run as written. Neither blocks the
four items above, because both sit on alternative routes.

1. `README.md`, the "Without `uv`" fallback. The inline comment
   `# .venv\Scripts\pip on Windows` annotates the `pip` line only, but the line
   after it, `.venv/bin/pytest -q -s`, has the same problem: a Windows virtual
   environment has `.venv\Scripts\` and no `.venv/bin/`, confirmed on the
   environment `uv sync` created here.

2. `expected/README.md` says "On Windows those three run under Git Bash or WSL;
   from PowerShell, replace the last one with `fc.exe /b ...`". Replacing the
   last one is not enough. The second command is a shell heredoc, which
   PowerShell cannot parse:

   ```
   uv run python - artifacts/simulator-junit.xml <<'PY'
                                                 ~
   Der Operator "<" ist fuer zukuenftige Versionen reserviert.
   ```

   ("The operator `<` is reserved for future use.") The Git Bash route in this
   note is the one that works.

## Follow-up, same day

The two documentation defects recorded above are fixed in ad52542 (README fallback lines) and 18abac8 (expected/README.md PowerShell route, which also found that PowerShell's `diff` is an alias of `Compare-Object` and compares the two path strings rather than the files). cf475e7 raises the agentic-hil floor from 0.16.0 to 0.21.0 with the lock refreshed; on 0.21.0 the simulator suite still reports `3 passed` and the report is byte-identical to `expected/simulator-junit.xml` (619 bytes, SHA256 5991B868360DDDCA8E68C7171A3975566ADFBC237A6DFAF4098E5757590A5D20), the same bytes this note recorded on 0.16.0.
