"""Fetch open primary sources selected during screening; never traverses sibling folders."""
from pathlib import Path
import sys,json,re,requests,concurrent.futures,xml.etree.ElementTree as ET
sys.path.insert(0,'/tmp/ecg_review_deps')
from bs4 import BeautifulSoup
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
SEARCH=ROOT/'papers/search_sources'
NS={'a':'http://www.w3.org/2005/Atom','ar':'http://arxiv.org/schemas/atom'}

def make_candidates():
    # Index selections are fixed against archived search responses, not live ranking.
    chosen={0:'Nunez_2024_Augmentation',1:'Speziale_2026_Amyloidosis',4:'Huang_2025_MIDT',6:'Pohl_2025_MultiBeat',10:'Bondar_2025_FlowECG',11:'Yehuda_2024_MultiODE',12:'Sviridov_2025_cNVAE',13:'Oladunni_2026_Complementarity',14:'Skorik_2024_SSSDnle',16:'Lai_2025_ECGTwin',17:'Wang_2025_SEDiff',18:'Jin_2025_UniECG',22:'Wang_2026_PGLRF',28:'Hu_2024_DigitalTwin',32:'Fang_2025_PPGFlow',33:'Cardoso_2023_Bayesian',36:'Kong_2024_fGAN',38:'Jang_2025_CoFE',39:'Li_2025_CLEPGAN',46:'Xu_2025_DFNet'}
    rows=[]
    for i,e in enumerate(ET.parse(SEARCH/'arxiv_api.xml').findall('a:entry',NS)):
        if i not in chosen:continue
        aid=e.find('a:id',NS).text.rsplit('/',1)[-1]
        rows.append(dict(study_id=chosen[i],title=' '.join(e.find('a:title',NS).text.split()),authors=' and '.join(x.find('a:name',NS).text for x in e.findall('a:author',NS)),year=chosen[i].split('_')[1],arxiv=aid,doi=e.findtext('ar:doi','',NS),first_public_date=e.find('a:published',NS).text[:10],updated=e.find('a:updated',NS).text[:10],peer_reviewed_date='',status='preprint; publication status to verify',venue=e.findtext('ar:journal_ref','arXiv',NS),landing_url='https://arxiv.org/abs/'+aid,abstract=' '.join(e.find('a:summary',NS).text.split()),source_key='arxiv:'+str(i)))
    eps={x['id']:x for f in SEARCH.glob('europepmc*.json') for x in json.loads(f.read_text())['resultList']['result']}
    chosenp={'42877876':'Zanchi_2026_Validation','42372472':'Russo_2026_Robustness','41142907':'Lai_2025_DiffuSETS','40132047':'Adib_2025_GANComparison','38266299':'X_2024_BiLSTMCBAM','38390581':'X_2024_FEMVAE','38926539':'X_2024_CECGGAN','41205561':'Kranz_2025_ECGEN','41823858':'Qiu_2026_PhysDiff','42583232':'Ji_2026_P2Es','40703115':'Zanchi_2025_Brugada','42115724':'Tiwari_2026_Minority','42356824':'Zhang_2026_QualityGAN','40899558':'Hegde_2025_Utility','42664696':'Xiao_2026_Disentangled','42914828':'Dissanayake_2026_MultiStep','41161556':'Lin_2025_TransDiff','42752421':'Zhang_2026_MorphDiff','40845011':'X_2025_PCCGAN','41336838':'Xiao_2025_VariableBeta','39820006':'X_2025_DisentangleAE','42480127':'X_2026_TransferGAN','41335953':'X_2025_InvertibleGAN','40460597':'X_2025_SSLGAN','41335641':'X_2025_ClassifierDiff','41337268':'X_2025_Attacks','42172249':'Guan_2026_WearECG'}
    for key,sid in chosenp.items():
        x=eps[key]; authors=x.get('authorList',{}).get('author',[])
        first=(authors[0].get('lastName','Unknown') if authors else x.get('authorString','Unknown').split()[0]);sid=sid.replace('X_',re.sub(r'[^A-Za-z]','',first)+'_',1) if sid.startswith('X_') else sid
        rows.append(dict(study_id=sid,title=x['title'].rstrip('.'),authors=' and '.join(a.get('fullName','') for a in authors),year=sid.split('_')[1],arxiv='',doi=x.get('doi',''),first_public_date=x.get('firstPublicationDate',''),peer_reviewed_date=x.get('firstPublicationDate',''),status='peer-reviewed',venue=x.get('journalInfo',{}).get('journal',{}).get('title',''),pmid=key,pmcid=x.get('pmcid','') or ('PMC13667384' if key=='42877876' else ''),landing_url='https://doi.org/'+x.get('doi',''),abstract=BeautifulSoup(x.get('abstractText',''),'html.parser').get_text(' '),source_key='epmc:'+key))
    for row in rows:
        if row['study_id']=='Lai_2025_DiffuSETS':row.update(arxiv='2501.05932v1',first_public_date='2025-01-10')
        if row['study_id']=='Ji_2026_P2Es':row.update(arxiv='2509.25480v1',first_public_date='2025-09-29')
        if row['study_id']=='Guan_2026_WearECG':row.update(arxiv='2510.11442v1',first_public_date='2025-10-13')
    (ROOT/'candidates.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
    return rows

def fetch(row):
    dest=ROOT/'papers'/row['year']/row['study_id'];dest.mkdir(parents=True,exist_ok=True)
    attempts=[];files=[]
    targets=[]
    if row.get('pmcid'):targets.append(('fulltext.xml','https://www.ebi.ac.uk/europepmc/webservices/rest/'+row['pmcid']+'/fullTextXML'))
    if row.get('arxiv'):
        targets += [('paper.pdf','https://arxiv.org/pdf/'+row['arxiv']),('landing.html','https://arxiv.org/abs/'+row['arxiv'])]
    if row.get('doi') and not targets:targets.append(('publisher.html','https://doi.org/'+row['doi']))
    for name,url in targets:
        path=dest/name
        try:
            if path.exists():data=path.read_bytes();status=200
            else:
                r=requests.get(url,timeout=50,headers={'User-Agent':'ECG-literature-review/1.0 (academic source retrieval)'});data=r.content;status=r.status_code
            valid=status==200 and ((name.endswith('.pdf') and data.startswith(b'%PDF')) or (name.endswith('.xml') and b'<article' in data) or (name.endswith('.html') and len(data)>5000 and b'Just a moment' not in data[:5000]))
            attempts.append(dict(url=url,http_status=status,valid=valid,bytes=len(data)))
            if not valid:continue
            path.write_bytes(data);files.append(str(path.relative_to(ROOT)))
            if name.endswith('.pdf'):
                pdf=PdfReader(path);text='\n\n'.join('=== PAGE '+str(i+1)+' ===\n'+p.extract_text() for i,p in enumerate(pdf.pages));(dest/'paper.txt').write_text(text);row['pdf_pages']=len(pdf.pages)
            elif name=='fulltext.xml':
                soup=BeautifulSoup(data,'xml')
                # Preserve sections and equation/table text in a line-addressable derivative.
                for el in soup.find_all(['title','p','disp-formula','table-wrap','ref']):el.insert_before('\n');el.insert_after('\n')
                (dest/'fulltext.txt').write_text(soup.get_text(' ',strip=False))
            elif name=='publisher.html':
                soup=BeautifulSoup(data,'html.parser')
                for el in soup(['script','style']):el.decompose()
                (dest/'publisher.txt').write_text(soup.get_text('\n',strip=True))
        except Exception as e:attempts.append(dict(url=url,error=str(e)))
    row.update(files=files,attempts=attempts)
    return row

if __name__=='__main__':
    rows=make_candidates()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results=[]
        for row in pool.map(fetch,rows):
            results.append(row); print(row['study_id'],row.get('pdf_pages',''),','.join(Path(f).name for f in row['files']),flush=True)
            (ROOT/'source_manifest.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
