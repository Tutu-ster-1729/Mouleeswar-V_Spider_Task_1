# Vault Sweep

## Overview

Vault Sweep is a Bash-based security auditing tool designed to scan a directory recursively for potentially dangerous shell scripts and insecure environment configuration files. The tool identifies common security risks, allows users to fix dangerous file permissions interactively, sanitizes environment files, and records all actions in an audit log with timestamps.

---

## Dangerous Patterns Detected

### 1. Destructive Commands

The following command patterns were classified as dangerous:

* `rm -rf`
* `mkfs`
* `shutdown`
* `reboot`

These commands were flagged because they can delete critical data, format storage devices, or interrupt system availability. If executed unintentionally or maliciously, they can cause severe damage to a system.

### 2. Suspicious Download-and-Execute Patterns

The following patterns were flagged:

* `curl ... | sh`
* `curl ... | bash`
* `wget ... | sh`
* `wget ... | bash`

These patterns download code from external sources and execute it immediately without inspection. This is a common malware delivery technique and represents a significant security risk.

### 3. Insecure Permissions

Scripts with world-writable permissions (`777`) were flagged.

World-writable scripts allow any user on the system to modify executable files, making them vulnerable to tampering and privilege escalation attacks. The tool provides an interactive option to remove the world-write permission and logs the action taken.

---

## Environment File Sanitization

The tool scans environment files such as:

* `.env`
* `.env.example`
* `.env.local`

A sanitized copy is generated as `.env.sanitized`.

### Accepted Format

The following formats are considered valid:

```env
API_KEY=spider26
PORT=3000
_DEBUG=false
```

Variable names must:

* Begin with a letter or underscore
* Contain only letters, digits, and underscores
* Not contain spaces around the equals sign

### Rejected Patterns

#### Spaces Around Assignment Operator

Rejected:

```env
KEY = value
```

Reason:

Environment variables should not contain spaces around the `=` operator.

---

#### Invalid Variable Names

Rejected:

```env
SERVER-NAME=test
```

Reason:

Hyphens are not valid characters in environment variable names.

---

#### Quoted Values

Rejected:

```env
USER="admin"
```

Reason:

The task specification identified quoted values as invalid and unsafe for this audit process.

---

#### Sensitive Secrets

Rejected:

```env
PASSWORD=secret123
TOKEN=abc123
SECRET=mysecret
```

Reason:

Sensitive credentials should not be stored in committed environment files. Such values can expose secrets if the repository becomes public or is shared accidentally.

---

#### PATH Modifications

Rejected:

```env
PATH=/tmp
export PATH=$PATH:/tmp
```

Reason:

Modifying the system PATH can introduce unsafe executable search locations and may allow malicious binaries to be executed unintentionally.

---

## Technical Challenges and Solutions

### Recursive File Discovery

The tool needed to scan all shell scripts and environment files recursively. This was implemented using the `find` command, allowing the script to process files across nested directory structures.

### Interactive Permission Fixing

A challenge occurred when prompting users to fix file permissions interactively. Since file paths were being supplied through process substitution, the `read` command initially consumed data from the input stream instead of the terminal.

This was resolved by reading directly from `/dev/tty`, ensuring user prompts always received keyboard input correctly.

### Regex-Based Validation

Regular expressions were used extensively for:

* Detecting dangerous shell commands
* Identifying suspicious download-and-execute patterns
* Validating environment variable names
* Filtering sensitive keys and malformed entries

Careful regex design was required to minimize false positives while still detecting unsafe patterns effectively.

---