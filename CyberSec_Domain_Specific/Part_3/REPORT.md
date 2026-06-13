# Open-Source Fuzzing – Part 3

## Objective

The objective of this task was to independently select an open-source software project, develop a custom fuzzing harness for it, and use AFL++ to search for potential vulnerabilities.

Unlike the previous two parts, the focus of this exercise was not on reproducing an already known issue. Instead, it involved applying the concepts learned earlier to a real-world application and documenting the methodology and observations.

As I had only recently become familiar with fuzzing concepts, this task served as an opportunity to practise setting up an end-to-end fuzzing workflow on software that I chose myself.

---

## Choosing the Target

For this task, I selected **cJSON** as the target application.

cJSON is a lightweight open-source JSON parsing library written in C. It is widely used due to its simplicity and small codebase.

Some reasons for choosing cJSON included:

* The codebase was relatively small and approachable.
* JSON parsers naturally process externally supplied input.
* The library is actively used in real applications.
* It provided a realistic target while remaining manageable for a beginner.

Although mature software tends to be more robust, I felt that cJSON would provide a good learning experience for applying fuzzing techniques independently.

---

## Understanding the Library

Before writing the harness, I briefly examined how cJSON operated.

The primary functionality relevant to this task involved:

* Receiving JSON text,
* Parsing the text into an internal representation,
* Returning either a valid JSON object or an error indication.

The parsing entry point used by the harness was:

```text
cJSON_Parse()
```

Successful parses produced dynamically allocated JSON objects which required cleanup after use.

---

## Designing the Harness

A custom harness was written specifically for this task.

The harness performed the following steps:

1. Opened the input file provided by AFL++.
2. Read the entire contents into memory.
3. Appended a null terminator.
4. Passed the resulting buffer to the JSON parser.
5. Deleted any successfully created JSON objects.
6. Released allocated memory before terminating.

The intention was to expose the parser directly to AFL++-generated inputs while ensuring that memory allocated during execution was properly cleaned up.

Compared to the previous task, this harness was significantly simpler, but writing it independently helped reinforce the purpose of a fuzzing harness.

---

## Seed Corpus

A small seed corpus was manually created.

The initial seeds included simple valid JSON examples such as:

```text
{}
```

```text
[]
```

```text
{"name":"Bub"}
```

Although these examples were minimal, they provided AFL++ with valid starting points from which mutations could be generated.

This approach encouraged deeper parser exploration compared to beginning with entirely random inputs.

---

## Building the Target

The target was compiled using AFL++ instrumentation.

AddressSanitizer support was also enabled during compilation to improve the visibility of any memory-related errors encountered during fuzzing.

This setup allowed AFL++ to observe code coverage and identify inputs that exercised previously unexplored execution paths.

---

## Fuzzing Procedure

The fuzzing workflow consisted of:

1. Preparing the seed corpus.
2. Compiling the target and harness using AFL++.
3. Launching AFL++ with the prepared inputs.
4. Monitoring the AFL++ dashboard.
5. Allowing execution to continue until sufficient coverage growth had been observed.

During execution, particular attention was given to:

* Corpus growth,
* Coverage improvements,
* Saved crashes,
* Saved hangs,
* Stability metrics.

---

## Results

The fuzzer was allowed to execute for approximately thirty minutes.

During this period, AFL++ reported:

* More than six hundred thousand executions,
* A corpus growth to approximately 383 interesting inputs,
* Around 81 newly discovered execution edges,
* Stable execution behaviour.

Notably:

* No crashes were observed.
* No hangs were observed.
* Stability remained at 100%.

Despite the absence of vulnerabilities, AFL++ continued to discover new execution paths through the parser.

<img width="632" height="430" alt="Screenshot 2026-06-12 161831" src="https://github.com/user-attachments/assets/be1e197d-afef-4d2f-b0a8-bb8e7b7d6bce" />

---

## Analysis of Findings

Initially, I expected that a successful fuzzing session would necessarily produce crashes.

However, this task demonstrated that this assumption is not always correct.

The absence of crashes may be explained by several factors:

* cJSON is a mature and widely used library.
* Many obvious bugs may already have been discovered and corrected.
* The fuzzing duration was limited.
* The seed corpus remained relatively small.

Even without vulnerabilities being identified, the coverage improvements indicated that AFL++ actively exercised previously unexplored portions of the parser.

From a testing perspective, this still represents a meaningful result.

---

## Lessons Learned

This task helped consolidate the concepts introduced in the previous exercises.

Some of the key lessons learned include:

* Choosing an appropriate target is an important part of fuzzing.
* A custom harness should expose the application's critical functionality while maintaining proper cleanup.
* Seed selection strongly influences the effectiveness of the fuzzer.
* Coverage growth itself is useful information.
* The absence of crashes does not imply that fuzzing was unsuccessful.
* Real-world software testing often involves documenting negative findings in addition to positive ones.

Prior to this exercise, I associated fuzzing primarily with finding vulnerabilities. This task broadened my understanding by showing that fuzzing is also a method of systematically exploring software behaviour.

---

## Limitations

* The fuzzing duration was relatively short.
* Only a small manually generated seed corpus was used.
* No advanced AFL++ techniques such as dictionaries or parallel fuzzing were employed.
* The study focused solely on JSON parsing functionality.
* Deeper analysis of uncovered execution paths was outside the scope of this task.

---

## Conclusion

This task provided an opportunity to apply the concepts learned from earlier fuzzing exercises to an independently chosen open-source project.

By selecting a target, writing a custom harness, preparing a seed corpus and analysing AFL++ results, I gained a better appreciation of the practical workflow involved in real-world fuzz testing.

Although no vulnerabilities were discovered during the allocated testing period, the experience reinforced the importance of methodology, documentation and analytical reasoning. It also demonstrated that meaningful insights can still be obtained even when the final outcome is the absence of crashes.
