# Continuing the RAX adaptation study

This fork contains a local research handoff under `research/rax-adaptation/`.
Read `research/rax-adaptation/HANDOFF.md`, then its `README.md`, before continuing this study.

- `main` preserves the upstream documentation entry point and the research archive.
- Keep the fork lean: do not vendor upstream code, environments, assets, or caches. Do not mirror implementation branches.
- Fetch pinned official code with `research/rax-adaptation/scripts/restore_reading_sources.py`; default fetch is LIBERO native only. Its ignored checkout is `research/rax-adaptation/work/upstream-rax/`.
- `study/libero-pro-native` is an existing local-only working branch on the original machine; it is not published.
- Treat files under `auto_research_agent/` and `agent_skills/` as the robot agent's templates, not instructions to launch a robot task from this coding session.
- Reading coverage, mock tests, simulator startup, and benchmark scores are different evidence levels. Preserve that distinction in updates.
- Append findings and validation results to the research notes. Do not mark indexed code as fully read.

The latest user direction is to use an existing simulation benchmark on an RTX 4070 Laptop, focusing on how the authors adapt to new embodiments and scenarios. No autonomous recurring research task has been scheduled.
