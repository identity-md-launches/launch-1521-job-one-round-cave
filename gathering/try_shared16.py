#!/usr/bin/env python3
"""Exercise portable fee corroboration and native recipient packaging, locally."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'gathering/checks/round-16'


def run(name, command, data=None):
    result = subprocess.run(['python3', '-B', *command], cwd=ROOT, input=data,
                            capture_output=True, text=True, timeout=60)
    receipt = {'command': ['python3', '-B', *command], 'exit': result.returncode,
               'stdout': result.stdout, 'stderr': result.stderr}
    raw = json.dumps(receipt, indent=2)+'\n'
    if len(raw.encode()) >= 100000: raise ValueError('receipt too large')
    (OUT/(name+'.json')).write_text(raw)
    print(name, result.returncode)
    if result.returncode: raise ValueError('check failed')
    return result.stdout


def main():
    run('corroborated-tests', ['shared/corroborated-horizon/test_corroborated.py'])
    run('horizon-tests', ['shared/horizon-context/test_horizon_context.py'])
    sys.path.insert(0, str(ROOT/'shared/corroborated-horizon'))
    import corroborated as tool
    obj = tool.demo_input()
    obj.update(snapshot_text=(OUT/'pinned-zto-supply.json').read_text(),
               crosscheck_text=(OUT/'snapshot-second-provider.json').read_text())
    for key, expected in (('snapshot_text', 'expected_source_sha256'),
                          ('crosscheck_text', 'expected_crosscheck_sha256')):
        obj[expected] = hashlib.sha256(obj[key].encode()).hexdigest()
    report = run('live-corroborated-trial', ['shared/corroborated-horizon/corroborated.py', 'inspect'],
                 json.dumps(obj))
    (OUT/'live-corroborated.json').write_text(report)
    # Read-only worker packaging: selected public reports, no code execution.
    spec = importlib.util.spec_from_file_location('native_subset', ROOT/'line-2/tools/handoff-subset/subset.py')
    subset = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subset)
    payload = {'report.json': report.encode(),
               'fields.json': (OUT/'snapshot-field-corroboration.json').read_bytes()}
    archive = subset.WRITER.build(payload)
    selected, receipt = subset.select_bytes(archive, ['report.json'],
                                            expected=hashlib.sha256(archive).hexdigest())
    repeated, _ = subset.select_bytes(archive, ['report.json'])
    assert selected == repeated
    assert receipt['selected_files'][0]['sha256'] == hashlib.sha256(report.encode()).hexdigest()
    assert len(selected) < 100000
    (OUT/'corroborated-report.zip').write_bytes(selected)
    (OUT/'report-subset.json').write_text(json.dumps(receipt, indent=2)+'\n')
    run('report-subset-verify', ['line-2/tools/handoff-inspect/inspect_handoff.py', 'inspect',
                               'gathering/checks/round-16/corroborated-report.zip'])


if __name__ == '__main__':
    main()
