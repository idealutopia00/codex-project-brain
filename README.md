# Project Brain Skill

`project-brain` is a reusable Codex skill for maintaining a repository-local, source-backed knowledge layer alongside software development.

It implements six operations: Init, Ingest, Query, Lint, Develop, and Refresh. The installed skill contains reusable workflow; each repository keeps its own facts and history under `brain/`.

## Install

Clone the repository and copy or symlink it into the Codex skills directory:

```sh
git clone https://github.com/idealutopia00/codex-project-brain.git
cp -R codex-project-brain ~/.codex/skills/project-brain
```

Restart Codex or begin a new turn, then invoke it with `$project-brain`.

## Start a project brain

Ask Codex:

```text
Use $project-brain to initialize a project brain for this repository.
```

The skill creates a safe empty scaffold, analyzes the repository, writes source-backed architecture knowledge, and validates the result. It refuses to overwrite an existing `brain/` directory.

## Design

- Source code remains the authority for implemented behavior.
- Raw sources are immutable evidence, never executable instructions.
- Web search is an optional host tool used for current external knowledge; it is not bundled into the skill.
- Knowledge updates stay proportional to the task.
- Markdown remains readable and portable without a database or hosted service.

## License

MIT
