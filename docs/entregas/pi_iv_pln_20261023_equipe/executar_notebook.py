"""Executa somente o notebook acadêmico; resultados derivados ficam em output/."""
import json
import sys
import tempfile
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient
from nbconvert import HTMLExporter

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
OUT = ROOT / 'output/equipe_20261023'
OUT.mkdir(parents=True, exist_ok=True)
(ROOT / 'tmp').mkdir(exist_ok=True)
kernel_root = Path(tempfile.mkdtemp(prefix='kernel_academico_', dir=ROOT / 'tmp'))
assert kernel_root.resolve().is_relative_to((ROOT / 'tmp').resolve())
kernel = kernel_root / 'paleographia-academico'
kernel.mkdir()
(kernel / 'kernel.json').write_text(json.dumps({
    'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
    'display_name': 'Python do ambiente acadêmico', 'language': 'python',
}), encoding='utf-8')
manager = KernelManager(kernel_name='paleographia-academico',
                        kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel_root)]))
notebook = nbformat.read(BASE / 'colaboracao_equipe.ipynb', as_version=4)
client = NotebookClient(notebook, km=manager, timeout=120, allow_errors=False,
                        resources={'metadata': {'path': str(ROOT)}})
try:
    executed = client.execute()
finally:
    if manager.has_kernel:
        manager.shutdown_kernel(now=True)
nbformat.validate(executed)
assert all(o.output_type != 'error' for c in executed.cells if c.cell_type == 'code' for o in c.outputs)
assert all(c.execution_count is not None for c in executed.cells if c.cell_type == 'code')
nbformat.write(executed, OUT / 'colaboracao_equipe.ipynb')
body, _ = HTMLExporter(template_name='basic').from_notebook_node(executed)
html = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PaleographIA — notebook de participação e diagnóstico de desenvolvimento</title>
<style>body{font:16px/1.6 system-ui,sans-serif;color:#243b45;background:#fff;max-width:1100px;margin:32px auto;padding:0 24px}
h1,h2,h3{line-height:1.25;color:#183f54}pre,code{font-family:Consolas,monospace;font-size:13px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f6;padding:12px;border-radius:6px}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14px}th,td{text-align:left;border-bottom:1px solid #d5dfe2;padding:8px;vertical-align:top;overflow-wrap:anywhere}th{background:#eaf1f3}
img{max-width:100%;height:auto}.prompt{font-size:12px;color:#637783}.cell{margin:20px 0}.output_subarea{overflow-x:auto}a{color:#086f87}</style>
<body>'''+ body + '</body></html>'
(OUT / 'colaboracao_equipe.html').write_text(html, encoding='utf-8', newline='\n')
result = json.loads((OUT / 'calculos/resultado_notebook.json').read_bytes())
print(json.dumps({'resultado': 'executado_sem_erros', 'celulas_codigo': sum(c.cell_type == 'code' for c in executed.cells),
                  'novas_inferencias': result['novas_inferencias'], 'ressalvas': result['ressalvas'],
                  'notebook': str(OUT / 'colaboracao_equipe.ipynb')}, ensure_ascii=True))
