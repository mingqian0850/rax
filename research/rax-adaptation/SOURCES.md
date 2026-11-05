# Sources and retained third-party material

- RAX upstream: https://github.com/robot-agent-exploration/rax — exact commits for all read branches are in `outputs/source-lock.json`. This fork does not mirror the implementation branches. Fetch pinned commits from the official upstream using the restore script.
- Paper: *Scaling Online Exploration for Robot Agents*, https://arxiv.org/html/2610.22496v1 . The retained HTML states **CC BY 4.0**; attribution and the original author list remain in `work/paper/paper.html`. License: https://creativecommons.org/licenses/by/4.0/ . The text files are a derived extraction for local reading; scripts/styles/navigation/MathML were removed during extraction, so formulas and figures must be checked against the original HTML. They are not an independent publication or a corrected version of the paper.
- LIBERO-PRO: https://github.com/Zxy-MLlab/LIBERO-PRO — commit `eafdb809426b13153aa1e4c42d6601844217dfec`. Recover using the implementation branch's bootstrap script.
- Perturbation data: https://huggingface.co/datasets/zhouxueyang/LIBERO-Pro — revision `c86fc3b8293185a6f373677018ff3e37f8391602`. The retained HF file tree is metadata used for checksum verification; the dataset is not vendored here.
- Learned skills: https://github.com/robot-agent-exploration/skills-lib — three branch commits in the source lock. Restore with the included source-restoration script. The original license/usage conditions of those sources remain applicable.
- Python environment source artifacts are identified in the pip and conda manifests. Local torch binary modification and its original hash are explicitly recorded; neither the binary nor its backup is committed.

The research reports and inspection scripts distinguish upstream statements, code inspection, and local measurements. Nothing in this archive is a new claim that the paper's benchmark scores have been independently reproduced.
