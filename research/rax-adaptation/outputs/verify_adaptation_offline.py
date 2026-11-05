"""Exercise RAX's real adaptation importer without a model, GPU or robot.

From the repository: runtime/envs/host/bin/python
research/rax-adaptation/outputs/verify_adaptation_offline.py
The original workspace layout is also supported. The fixture is synthetic.
"""
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
REPO = Path(os.environ['RAX_SOURCE_REPO']).resolve() if os.environ.get('RAX_SOURCE_REPO') else next(
    (p for p in [ROOT / 'work/upstream-rax', *Path(__file__).resolve().parents, ROOT / 'rax']
     if (p / 'services/adaptation.py').is_file()), ROOT / 'work/upstream-rax')
if not (REPO / 'services/adaptation.py').is_file():
    raise SystemExit('Restore the pinned sources first, or set RAX_SOURCE_REPO to the LIBERO native checkout')
sys.path.insert(0, str(REPO))
from services import adaptation, transfer


def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main():
    checks = {}
    (ROOT / 'work').mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='adaptation-check-', dir=ROOT/'work') as tmp:
        base = Path(tmp)
        source = base/'source'
        ws = source/'agent-workspace'
        put(ws/'memory/PROGRESS.md', 'exploration-only evidence')
        put(ws/'code/controller.py', 'def main(ctx):\n    return "frozen program"\n')
        put(ws/'runtime/frames/private.txt', 'old frame history')
        put(ws/'formal-results.json', 'held-out outcomes')
        frozen = source/'bundles'/'freeze'
        frozen.parent.mkdir(parents=True)
        manifest, _ = transfer.pack(frozen, workspace=ws, parts=('memory', 'code'),
                                    metadata={'session_id': None, 'frozen_at': 1})
        manifest['directory'] = 'freeze'
        state = {'configuration': {'task': 'libero_goal_1', 'mode': 'auto-research',
                                   'agent_cli': 'codex', 'eval_seed': 0},
                 'exploration_checkpoint': {'bundle': 'freeze'},
                 'bundles': {'freeze': manifest}, 'results': []}
        put(source/'state.json', json.dumps(state))
        # Simulate later live-workspace changes after formal evaluation.
        put(ws/'memory/PROGRESS.md', 'FORMAL EVALUATION INFORMATION MUST NOT TRANSFER')
        target = base/'target'
        target.mkdir()
        dest, home = target/'agent-workspace', target/'codex-home'
        dest.mkdir()
        home.mkdir()
        config = SimpleNamespace(root=target, adaptation_source=str(source),
            task='libero_goal_1', agent_cli='codex', adaptation_context='clear',
            transfer_parts=('memory', 'code'), transfer_mb=100,
            eval_seed=6, agent_formal=False, exploration_seeds=(1,2,3,4,5))
        session = adaptation.import_source(config, dest, home)
        checks['uses_frozen_exploration_memory'] = (dest/'memory/PROGRESS.md').read_text() == 'exploration-only evidence'
        checks['carries_program'] = (dest/'code/controller.py').read_text() == (frozen/'transfer/code/controller.py').read_text()
        checks['excludes_frame_history'] = not (dest/'runtime').exists()
        checks['excludes_formal_result_file'] = not (dest/'formal-results.json').exists()
        checks['clear_context_has_no_session'] = session is None
        checks['writes_adaptation_note'] = '5 exploration episodes' in (dest/'ADAPTATION.md').read_text()
        checks['source_live_memory_unchanged'] = (ws/'memory/PROGRESS.md').read_text().startswith('FORMAL EVALUATION')
        config.task = 'libero_spatial_0'
        try:
            adaptation.source_trial(config)
        except ValueError:
            checks['rejects_different_task'] = True
        else:
            checks['rejects_different_task'] = False
        (ROOT/'outputs/adaptation-note-example.md').write_text((dest/'ADAPTATION.md').read_text())
    report = {'kind':'synthetic_offline_mechanism_check', 'benchmark_success_rate':None,
              'model_calls':0, 'gpu_used':False, 'checks':checks, 'passed':all(checks.values())}
    (ROOT/'outputs/adaptation-offline-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
