"""Host-side validation of the three hardware test plans.

These tests run anywhere Python runs: no board, no probe, no serial port, no
Agentic HIL configuration. They call the reactor's own loader, so a plan that
passes here is one the reactor's loader accepts: the closed schema, the step
vocabulary and the format version gate. The reactor also checks a plan against
this bench's configured devices and permissions before the first hardware
action, and that half needs a configuration, so it happens on the bench rather
than here. A plan red here is a plan no bench would run.

What that is worth, and what it is not, is printed by every test below:

    PASS  configuration and test semantics validated in simulator
    NEEDS PHYSICAL FIXTURE  electrical behavior not verified

Nothing here executes, emulates or models the STM32. A green run says the plans
are well formed and say what the exercise says they say. It says nothing about
whether the firmware answers.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml
from agentic_hil.test_reactor import load_test_config

REPO_ROOT = Path(__file__).parents[2]
PLAN_DIR = REPO_ROOT / "tests" / "hil"
PLAN_NAMES = ("nominal", "diagnostic", "recovery")

SCOPE_LINES = (
    "PASS  configuration and test semantics validated in simulator",
    "NEEDS PHYSICAL FIXTURE  electrical behavior not verified",
)

FIRMWARE_IMAGE = "build/Debug/stm32-starter.elf"
PROBE = "dut"
SERIAL_LINE = "dut_uart"

# The diagnostic protocol the firmware speaks over the ST-LINK virtual COM port,
# stated once. Each entry is the command a plan sends and the claim the plan
# makes about the answer.
PROTOCOL = {
    "nominal": ("STATUS\n", '"state":"READY","diagnostic":"NONE"'),
    "diagnostic": ("DIAG ON\n", '"state":"DEGRADED","diagnostic":"E_SELF_TEST"'),
    "recovery": ("DIAG CLEAR\n", '"state":"READY","diagnostic":"NONE"'),
}

# A plan states a test. A bench states the hardware. Anything matching one of
# these in a plan file would be the second document leaking into the first, and
# the plan would stop being portable between benches.
#
# Only values are checked here. A bench *key* (`baudrate`, `probe_id`,
# `interface_cfg`, `allow_write`) is already refused by the plan schema, which is
# closed at the root and on every step, and the loader in the test above proves
# that. A bench *value* is not: `COM5` is a schema-valid device name and an
# absolute path is a schema-valid `image_path`, so these four are the patterns
# with something left to catch.
BENCH_DETAIL = {
    "a Windows COM port": re.compile(r"\bCOM\d+\b"),
    "a POSIX tty device": re.compile(r"/dev/tty|/dev/serial"),
    "a Windows absolute path": re.compile(r"[A-Za-z]:[\\/]"),
    # `[\s-]*` rather than `\s*`, because a step is a list item and
    # `yaml.safe_dump` renders its first key behind the `- ` marker.
    "a POSIX absolute path": re.compile(r"(?m)^[\s-]*[a-z_]+:\s*/"),
}


def announce_scope() -> None:
    """State this suite's boundary, and prove the repository states the same one.

    The two lines are a claim about what a green run means, so a run that prints
    them while README.md advertises something else would be the one failure this
    suite exists to prevent.
    """
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    for line in SCOPE_LINES:
        assert line in readme, f"README.md does not publish the scope line {line!r}"
        print(line)


def plan_path(name: str) -> Path:
    return PLAN_DIR / f"{name}.testconfig.yaml"


def load_plan(name: str):
    return load_test_config(str(plan_path(name)), work_dir=str(REPO_ROOT))


def plan_data(name: str) -> str:
    """The plan's data with its prose removed.

    What a plan *says* is the document, not the comments explaining it, so this
    is what the bench-detail check reads: a comment is free to use the word
    `baudrate` while the plan itself must never carry one.
    """
    document = yaml.safe_load(plan_path(name).read_text(encoding="utf-8"))
    return yaml.safe_dump(document, default_flow_style=False, sort_keys=False)


def writes(plan) -> list[str]:
    return [step.arguments["text"] for step in plan.steps if step.action == "uart_write"]


def claims(plan) -> list[str]:
    return [
        step.arguments["comparator"]["pattern"]
        for step in plan.steps
        if step.action == "uart_read" and "comparator" in step.arguments
    ]


def test_hardware_plans_are_accepted_by_the_reactor() -> None:
    """Every shipped plan passes the loader the reactor itself runs.

    That covers the closed schema, the step vocabulary and the version gate: a
    plan reaching for an action its own `version:` does not contain is refused
    here by name, rather than working on one install and failing on another.
    """
    found = sorted(path.name for path in PLAN_DIR.glob("*.testconfig.yaml"))
    assert found == sorted(f"{name}.testconfig.yaml" for name in PLAN_NAMES), found

    for name in PLAN_NAMES:
        plan = load_plan(name)
        assert plan.steps, f"{name} plan has no steps"
        assert plan.name.startswith("nucleo-f446re-"), plan.name

        actions = [step.action for step in plan.steps]
        assert actions[:3] == ["flash", "uart_open", "reset"], (name, actions)

        flash = plan.steps[0]
        assert flash.arguments["image_path"] == FIRMWARE_IMAGE, (name, flash.arguments)
        assert flash.arguments["reset_after_flash"] is False, (name, flash.arguments)
        assert flash.device == PROBE, (name, flash.device)

        opened = plan.steps[1]
        assert opened.arguments["clear_buffer"] is True, (name, opened.arguments)
        assert opened.device == SERIAL_LINE, (name, opened.device)

        assert plan.steps[2].arguments["mode"] == "run", (name, plan.steps[2].arguments)

    announce_scope()


def test_hardware_plans_state_the_diagnostic_protocol() -> None:
    """The three plans drive the three protocol commands and claim the three
    documented answers, once each, in the order the exercise describes.

    This is the semantic half: a plan that loads is well formed, and a plan that
    loads and stimulates the wrong command is a well formed test of the wrong
    thing.
    """
    for name in PLAN_NAMES:
        plan = load_plan(name)
        command, answer = PROTOCOL[name]

        assert command in writes(plan), (name, writes(plan))
        assert any(answer in claim for claim in claims(plan)), (name, claims(plan))

        # Every plan first proves the board restarted under this run, so a claim
        # below it is a claim about this boot.
        assert any('"event":"boot"' in claim for claim in claims(plan)), (name, claims(plan))

    recovery = load_plan("recovery")
    assert writes(recovery) == ["DIAG ON\n", "DIAG CLEAR\n"], writes(recovery)
    assert not any("E_SELF_TEST" in claim for claim in claims(recovery)), claims(recovery)

    # Everything the three plans send, taken together, is the protocol and
    # nothing else: a plan that reached for a fourth, undocumented command would
    # be testing a firmware this repository does not describe.
    stimulated = {command.strip() for name in PLAN_NAMES for command in writes(load_plan(name))}
    assert stimulated == {"STATUS", "DIAG ON", "DIAG CLEAR"}, stimulated

    announce_scope()


def test_hardware_plans_name_no_bench_hardware() -> None:
    """A plan says what the test does. The bench says what the hardware is.

    Each plan routes by logical name only, so the same file runs unchanged on a
    developer's desk and on the CI bench, and a reviewer reading the pull
    request sees a test rather than somebody's serial port.
    """
    for name in PLAN_NAMES:
        document = plan_data(name)
        for description, pattern in BENCH_DETAIL.items():
            match = pattern.search(document)
            assert match is None, f"{name} plan names {description}: {match.group(0)!r}"

        plan = load_plan(name)
        for index, step in enumerate(plan.steps):
            assert step.device in (PROBE, SERIAL_LINE), (name, index, step.device)
            assert step.route_keys == ["device"], (name, index, step.route_keys)

    announce_scope()
