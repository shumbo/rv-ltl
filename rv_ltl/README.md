## Installation

Install `rv-ltl` from PyPI.

```bash
pip install rv-ltl
```

## Usage

### Construct Proposition

First, construct a proposition to evaluate. Click the name of the class for details.

| Class                           | Description                                                               |
| ------------------------------- | ------------------------------------------------------------------------- |
| `rv_ltl.proposition.Atomic`     | An atomic proposition that takes `True` or `False` at each step           |
| `rv_ltl.proposition.Not`        | The logical **NOT** of the proposition                                    |
| `rv_ltl.proposition.And`        | The logical **AND** of the proposition                                    |
| `rv_ltl.proposition.Or`         | The logical **OR** of the proposition                                     |
| `rv_ltl.proposition.Next`       | The proposition at the next step                                          |
| `rv_ltl.proposition.Until`      | If the first proposition is true **until** the second proposition is true |
| `rv_ltl.proposition.Eventually` | If the proposition becomes **eventually** true                            |
| `rv_ltl.proposition.Always`     | If the proposition is **always** true                                     |
| `rv_ltl.proposition.Implies`    | If the first proposition **implies** the second proposition               |

### Evaluation with Monitor

Then, create a monitor using the constructed proposition, and evaluate the trace using the monitor.

Use `rv_ltl.proposition.Proposition.create_monitor` to create a monitor.

**Example:**

```python
A = Atomic()
phi = Eventually(And(A, Atomic(identifier="B")))
monitor = phi.create_monitor()
```

Use `rv_ltl.monitor.Monitor.update` to feed a trace into the monitor. The update takes a dictionary whose keys are the atomic propositions and values are booleans (`True` or `False`). Instead of passing the instance of `rv_ltl.proposition.Atomic`, you may use the identifier (string) to specify atomic variables. `rv_ltl.monitor.Monitor.update` raises `rv_ltl.exception.MissingAtomicsException` if not all atomic propositions in the given monitor are specified.

**Example:**

```python
monitor.update({A: True, "B": False})
```

Use `rv_ltl.monitor.Monitor.evaluate` to evaluate the proposition based on the trace that is accepted by the monitor.

**Example:**

```python
monitor.evaluate() # -> B4.PRESUMABLY_FALSE
```

This method would return `rv_ltl.b4.B4`, our four-valued boolean representation. In this case, `A AND B` at the first step evaluates to false, but because it may eventually be true, `rv_ltl.b4.B4.PRESUMABLY_FALSE` is returned.
