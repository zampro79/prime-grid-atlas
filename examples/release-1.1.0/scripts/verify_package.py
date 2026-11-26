"""Read-only integrity/privacy/link checker using only the standard library.
Run: python scripts/verify_package.py --package .
Checksum identity is separate from numerical/scientific validity.
"""
import argparse,hashlib,json,re,struct,zlib
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def png_metadata(file):
    data=file.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';at=8;chunks=[];text=[]
    while at<len(data):
        size=struct.unpack('>I',data[at:at+4])[0];kind=data[at+4:at+8];body=data[at+8:at+8+size]
        crc=struct.unpack('>I',data[at+8+size:at+12+size])[0]
        assert zlib.crc32(kind+body)&0xffffffff==crc
        chunks.append(kind.decode())
        if kind==b'tEXt':text.append(body.decode('latin1'))
        elif kind==b'zTXt':
            key,rest=body.split(b'\0',1);text.append(key.decode('latin1')+' '+zlib.decompress(rest[1:]).decode('latin1'))
        elif kind==b'iTXt':
            key,rest=body.split(b'\0',1);flag,method=rest[:2];lang,translated,value=rest[2:].split(b'\0',2)
            if flag:value=zlib.decompress(value)
            text.append(key.decode('latin1')+' '+translated.decode('utf8')+' '+value.decode('utf8'))
        elif kind==b'eXIf':raise AssertionError('EXIF requires explicit review')
        at+=size+12
        if kind==b'IEND':break
    assert at==len(data)
    return {'chunks':chunks,'text':text,'size':list(struct.unpack('>II',data[16:24]))}

def validate(root):
    root=root.resolve();files=sorted(f for f in root.rglob('*') if f.is_file());privacy=[];pngs={};links=0
    checksums=0
    for sums in root.rglob('SHA256SUMS'):
        for line in sums.read_text().splitlines():
            expected,name=line.split(None,1);f=(sums.parent/name.strip().removeprefix('*')).resolve()
            assert f.is_relative_to(root) and f.is_file() and sha(f)==expected,(sums,name)
            checksums+=1
    # Full account paths and credential signatures, not generic detection literals.
    patterns=[r'/(?:home|Users)/[A-Za-z0-9_.-]+/',r'[A-Za-z]:\\Users\\[A-Za-z0-9_.-]+',
              r'gh[pousr]_[A-Za-z0-9]{20,}',r'github_pat_[A-Za-z0-9_]{20,}',r'AKIA[0-9A-Z]{16}',
              r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
    for file in files:
        rel=file.relative_to(root).as_posix()
        assert not file.is_symlink()
        assert file.suffix.lower() not in ('.pyc','.core','.log') and file.name not in ('core','.env')
        if file.suffix.lower()=='.png':
            meta=png_metadata(file);pngs[rel]=meta;text='\n'.join(meta['text'])
        else:text=file.read_text(encoding='utf8')
        for pat in patterns:
            if re.search(pat,text):privacy.append({'path':rel,'kind':'private-path-or-secret-signature'})
        if file.suffix in ('.md','.html'):
            # The fenced README proposal contains future destinations, not active links.
            active=re.sub(r'```.*?```','',text,flags=re.S)
            targets=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',active)+re.findall(r'(?:href|src)="([^"]+)"',active)
            for target in targets:
                target=target.split('#',1)[0]
                if not target or re.match(r'^[a-zA-Z]+:',target):continue
                f=(file.parent/target).resolve()
                assert f.is_relative_to(root) and f.exists(),(rel,target)
                links+=1
        if file.suffix=='.json':json.loads(text)
    assert not privacy,privacy
    assert len(pngs)==11
    return {'status':'PASS','files':len(files),'pngs':len(pngs),'local_links':links,
            'checksum_entries':checksums,'private_path_or_secret_findings':privacy,'PNG_metadata':pngs,
            'scope':'All public textual files and PNG ancillary metadata scanned; visual screenshot review recorded separately. No artifact rewritten.'}

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--package',type=Path,required=True);v=a.parse_args()
    print(json.dumps(validate(v.package),indent=2))
if __name__=='__main__':main()
