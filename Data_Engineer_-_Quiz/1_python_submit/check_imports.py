import importlib.util
paths = [
    'src/scraper.py',
    'src/transformer.py',
    'src/framework.py'
]
for p in paths:
    full = p
    spec = importlib.util.spec_from_file_location(full, full)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(full + ' OK')
