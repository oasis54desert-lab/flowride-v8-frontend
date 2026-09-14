from pathlib import Path
p = Path('app.py')
s = p.read_text(encoding='utf-8')
s = s.replace('/v18/analyze_default', '/v18/analyze_default2')
s = s.replace('/v18/export_default_csv', '/v18/export_default2_csv')
p.write_text(s, encoding='utf-8')
print('Updated V18 frontend endpoints to robust runtime')
