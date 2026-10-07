# Recorded hardware evidence

This package supports the article Developing firmware with a coding agent and real board feedback. It contains a prepared maintainer exercise on a real Nucleo-F446RE, recorded on 7 October 2026 in Central European Summer Time (6 October in UTC).

The defect was deliberately present in the starter. The agent changed the firmware command match from `DIAG ENABLE` to `DIAG ON`. All three unchanged hardware plans passed after the correction. This is not an independent benchmark or a fresh installation demonstration.

`source-map.json` maps the six runs to their reports and UART logs and identifies the software versions, source revision, plan hashes and firmware images. The distributed files have private host paths and device identifiers redacted. The source map distinguishes hashes of these copies from hashes of the private originals. Verify distributed files against the redacted-copy hashes.

The canonical reports contain the test verdicts, flashed artifact hashes, expected comparisons and cleanup results. The JSONL logs preserve recorded UART bytes. `firmware.diff` is the one-line source correction; `build-corrected-nominal.json` records the subsequent compilation and linking.

The public starting source and test plans are at [starter commit c644844](https://github.com/agentic-hil/stm32-starter/tree/c64484450bffbb73a29546334633c53e7fff9960). No executable firmware or hardware-access configuration is included in this archive.
