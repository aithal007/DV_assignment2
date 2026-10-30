from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts/build_story_report.py'
s=p.read_text(encoding='utf-8');a=s.index('def build():\n');b=s.index("if __name__=='__main__':",a)
s=s[:a]+'''def build():
    import sys
    figures=compose_report()
    from readable_report_pdf import write
    write(figures,sys.modules[__name__])


'''+s[b:]
p.write_text(s,encoding='utf-8')
print('Enabled figure pages with adjacent explanations')
