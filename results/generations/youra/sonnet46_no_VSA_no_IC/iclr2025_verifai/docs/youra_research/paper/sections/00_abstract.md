# Abstract

Static analysis tools catch fewer than one in three of the code generation failures
that stump GPT-4o-mini on EvalPlus — the remaining errors are semantic divergences
that blind reprompting cannot reliably fix. We propose *specification-aligned repair*:
a structured oracle that provides the model with three components simultaneously —
the problem docstring's formal intent, a failing test's input/expected-output pair,
and the model's actual incorrect output — giving it the minimum information needed
for targeted algorithmic repair. To enable controlled evaluation of this approach,
we verify that the 134-problem GPT-4o-mini EvalPlus failure set is fully recoverable
from archive: all 134 failure IDs, stored incorrect solutions, EvalPlus API access,
and deterministic test selection are confirmed (4/4 conditions, 5/5 tests pass).
Six tasks with incomplete archive records yield a 128-task working set with adequate
statistical power for a pre-registered 3-condition McNemar comparison of specification-aligned
repair against blind reprompting and a round-0 baseline. Our contribution is the data
infrastructure and experimental design; the comparative results are forthcoming from
the pre-registered mechanism experiments.
