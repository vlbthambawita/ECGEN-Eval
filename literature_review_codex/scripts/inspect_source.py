"""Print selected pages or XML sections from already downloaded review sources."""
import sys,re
from pathlib import Path
sys.path.insert(0,'/tmp/ecg_review_deps')
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1]
sid=sys.argv[1]; folder=next((root/'papers').glob('*/'+sid))
if (folder/'fulltext.xml').exists():
    soup=BeautifulSoup((folder/'fulltext.xml').read_text(),'xml')
    for duplicate in soup.find_all('tex-math'):
        duplicate.decompose()
    import copy
    for original in soup.find_all('sec'):
        section=copy.copy(original)
        for child in section.find_all('sec'):child.decompose()
        title=section.find('title'); title=title.get_text(' ',strip=True) if title else 'untitled'
        if len(sys.argv)<3 or re.search(sys.argv[2],title,re.I):
            print('\n### '+title+'\n'+section.get_text(' ',strip=True))
else:
    t=(folder/'paper.txt').read_text()
    pages=re.split(r'=== PAGE (\d+) ===',t)
    selected=set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv)>2 else None
    for i in range(1,len(pages),2):
        if selected is None or int(pages[i]) in selected:print('=== PAGE '+pages[i]+' ==='+pages[i+1])
