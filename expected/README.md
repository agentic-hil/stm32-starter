# Reference reports

What a finished run looks like, so a fresh run has something to be compared against.

## simulator-junit.xml

The reference report for the simulator suite: three test cases, zero failures, zero errors, zero skipped.

These are the exact bytes pytest writes, which is one line with no trailing newline, with three attributes replaced. `hostname`, `timestamp` and `time` say nothing about whether the tests passed and differ on every machine and every run, so `hostname` reads `reference` and every `timestamp` and `time` is zeroed. Nothing else is touched, and [.gitattributes](../.gitattributes) keeps the file out of end-of-line normalisation so those bytes survive a checkout on any platform.

Produce your own, pin the same three attributes, and the two files are identical:

```bash
uv run pytest -q -s --junitxml=artifacts/simulator-junit.xml
uv run python - artifacts/simulator-junit.xml <<'PY'
import re, sys
path = sys.argv[1]
text = open(path, encoding="utf-8", newline="").read()
for pattern, pinned in (
    (r'hostname="[^"]*"', 'hostname="reference"'),
    (r'timestamp="[^"]*"', 'timestamp="1970-01-01T00:00:00+00:00"'),
    (r'time="[^"]*"', 'time="0.000"'),
):
    text = re.sub(pattern, pinned, text)
open(path, "w", encoding="utf-8", newline="").write(text)
PY
diff artifacts/simulator-junit.xml expected/simulator-junit.xml
```

`diff` printing nothing is the pass. Anything it prints is a test that was added, renamed, removed, or that did not pass. On Windows those three run under Git Bash or WSL; from PowerShell, replace the last one with `fc.exe /b artifacts\simulator-junit.xml expected\simulator-junit.xml`.

The same report is uploaded as the `simulator-junit` artifact by [.github/workflows/simulator.yml](../.github/workflows/simulator.yml) on every push and pull request.

## The hardware run

`agentic-hil test-reactor` does not write JUnit XML. A hardware run's evidence is the reactor's own report, written to `.agentic-hil/reports/last-report.json` in the workspace, with the canonical copy under the operator's state root, and `last-failure.json` beside it when a run failed. It carries what a JUnit file cannot: the digest of the exact configuration the run was permitted by, one entry per executed step with the tool result unchanged, and the contact marker that says whether the board was reached at all.

No reference hardware report is committed here yet. When one is, it comes from this sequence on a real Nucleo-F446RE and from nowhere else:

1. the shipped firmware fails `tests/hil/diagnostic.testconfig.yaml` and passes the other two plans;
2. a coding agent makes the smallest firmware fix;
3. all three plans pass;
4. the three plans pass again on the same firmware revision, unchanged;
5. the reports are stored together with the board identity, the firmware revision, the toolchain versions and the run duration.

A simulator result is not a substitute for any of that, and neither is a hand-edited report. [validation/README.md](../validation/README.md) is the gate.
