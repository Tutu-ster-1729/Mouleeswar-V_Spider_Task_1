# Fix the Fuzzer – Part 2

## Objective

The objective of this task was to analyse and repair a deliberately flawed AFL++ harness provided for a license validation library. While the target application contained an existing vulnerability, the supplied fuzzing setup prevented AFL++ from effectively discovering it.

Prior to this task, I had only recently become familiar with basic fuzzing concepts. Therefore, this exercise focused not only on finding crashes, but also on understanding how harness design and instrumentation affect the effectiveness of a fuzzer.

---

## Understanding the Target

The provided target consisted of a license validation system implemented in:

* `license.c`
* `license.h`

The parser operated on a custom binary license format containing various chunks, including:

* Owner information,
* License levels,
* Expiry dates,
* Features,
* Hardware identifiers,
* Metadata,
* Issuer information,
* Signature blocks,
* Override chunks.

The objective was to identify why AFL++ failed to make meaningful progress and modify the fuzzing setup without directly fixing the vulnerability itself.

---

## Initial Observations

Although AFL++ launched successfully, it failed to discover any crashes despite repeated execution.

This suggested that the problem was not necessarily within the target itself, but rather within the fuzzing environment.

Some possible causes considered included:

* Improper instrumentation,
* Invalid seed corpus,
* State carried across executions,
* Inputs failing early validation checks,
* Issues within the harness.

Understanding the flow of the target became necessary before making modifications.

---

## Investigating the Harness

The original harness performed the following steps:

1. Opened the input file.
2. Read the contents into a buffer.
3. Initialised the license system.
4. Called the validation routine.

However, several issues reduced AFL++ effectiveness.

### Missing Cleanup

The license system maintained global state.

Since the cleanup routine was never called, subsequent executions could inherit unintended state from previous runs.

This prevented each fuzz iteration from behaving independently.

Adding the cleanup routine ensured that each execution began with a clean environment.

---

## Instrumentation Issues

The original Makefile used a standard compiler configuration for the fuzz target.

As a result, AFL++ instrumentation was not properly applied.

The build system was modified to use AFL++'s compiler wrappers so that coverage information could be collected during execution.

This allowed AFL++ to observe and prioritise new execution paths.

---

## Understanding the Seed Corpus

The supplied corpus generated valid license structures containing:

* Correct CRC values,
* Supported version information,
* Proper chunk formatting,
* Signature blocks.

Initially, I assumed that the target vulnerability would be reached automatically.

However, after further investigation, it became clear that the provided seeds never exercised the vulnerable code path.

This highlighted the importance of understanding not only the target program but also the assumptions made by the seed corpus.

---

## Discovering the Vulnerability

The vulnerability was eventually traced to the override chunk processing routine.

The implementation contained the following logic:

```c
char override_buffer[64];

memcpy(override_buffer, data, len);
```

The copied length originated from attacker-controlled input.

No bounds checking was performed before copying into the fixed-size stack buffer.

If:

```text
len > 64
```

the copy operation would overwrite memory beyond the bounds of the stack allocation.

This behaviour represented a classic stack buffer overflow vulnerability.

---

## Verifying the Vulnerability

To confirm the issue independently of AFL++, the existing unit tests were modified to construct a valid license containing an oversized override chunk.

The override length was increased beyond the buffer size.

Executing the tests with AddressSanitizer enabled produced a clear diagnostic report identifying the overflow.

AddressSanitizer reported:

* Stack-buffer-overflow,
* The offending memcpy operation,
* The vulnerable function,
* The affected stack object.

This verification provided confidence that the identified flaw was genuine.

---

## Using AFL++ to Rediscover the Bug

After understanding the vulnerable code path, the seed corpus was extended to include valid licenses capable of reaching the override processing logic.

AFL++ was then rerun using:

* Proper instrumentation,
* Improved harness behaviour,
* Appropriate seeds.

With these changes, AFL++ successfully generated crash-inducing inputs.

The discovered crashes demonstrated that the vulnerability could be reached through automated fuzzing rather than solely through manually crafted test cases.

--- 

## Screenshots from Fuzzer 

<img width="1265" height="856" alt="Screenshot 2026-06-11 032047" src="https://github.com/user-attachments/assets/47ea1082-5464-42d8-8cf0-db23d4a8e7df" />

<img width="1273" height="846" alt="Screenshot 2026-06-11 162552" src="https://github.com/user-attachments/assets/46617e6d-0440-4b23-a80c-fef191fa7ff5" />

<img width="1262" height="845" alt="Screenshot 2026-06-11 163547" src="https://github.com/user-attachments/assets/f0a0562a-bcfa-4c9a-9c44-4163d6983ed9" />


---

## Lessons Learned

This task taught me that effective fuzzing depends heavily on the quality of the surrounding setup.

Some important lessons included:

* A vulnerable target does not guarantee that a fuzzer will discover the bug.
* Harnesses must correctly initialise and clean up application state.
* AFL++ instrumentation is essential for coverage-guided fuzzing.
* Seed corpora strongly influence the execution paths explored.
* AddressSanitizer is extremely useful when validating suspected vulnerabilities.
* Reading and understanding source code remains an important part of fuzz testing.

Initially, I assumed that running AFL++ would automatically reveal vulnerabilities. This exercise demonstrated that significant reasoning and debugging are often required before a fuzzer becomes effective.

---

## Limitations

* The vulnerable code itself was not permanently patched, since the objective was to identify and reproduce the issue.
* The seed corpus remained relatively small.
* The fuzzing duration was limited by the scope of the task.
* More sophisticated seed generation strategies could potentially improve coverage further.

---

## Conclusion

This task provided insight into an aspect of fuzzing that I had not previously considered: the importance of the harness and execution environment.

By investigating why AFL++ failed to discover an existing vulnerability, I learned how instrumentation, cleanup routines, seed selection and code understanding all contribute to successful fuzz testing.

Compared to the previous task, this exercise shifted the focus from simply running a fuzzer to diagnosing and improving the entire fuzzing workflow. It reinforced the idea that automated tools are most effective when supported by careful analysis and thoughtful setup.
