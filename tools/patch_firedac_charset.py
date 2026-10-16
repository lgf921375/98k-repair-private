from pathlib import Path
import json,struct,hashlib,shutil,subprocess
b=Path('/srv/projects/98k/repair-20261014')
root=b/'work/compat-root/drive_d/MirServer'
active=subprocess.run(['systemctl','list-units','98k-*.service','--state=running','--no-legend','--no-pager'],capture_output=True,text=True).stdout.strip()
assert not active,'Stop and finish all owned 98K runtime trials before patching a stopped copy'
plan=json.loads((b/'evidence/charset-patch-plan.json').read_text())
records=[]
for item in plan:
 calls=[r for a in item['utf8_CharSet_calls'] for r in a['refs']]
 if not calls:continue
 p=root/item['file'];raw=p.read_bytes();d=bytearray(raw)
 original=b/'work/extracted-Server'/item['file']
 assert raw==original.read_bytes(),item['file']+' unexpected preexisting binary change'
 target_off,target_va=item['valid_CharacterSet_strings'][0]
 target_off=int(target_off,16);target_va=int(target_va,16)
 assert raw[target_off:target_off+24]=='CharacterSet'.encode('utf-16le')
 for r in calls:
  o=r['file_offset'];assert d[o-1]==0xba
  assert struct.unpack_from('<I',d,o)[0]==int(r['old_pointer'],16)
  assert d[o-6]==0xb9 and d[o+4]==0xe8
  struct.pack_into('<I',d,o,target_va)
 backup=b/'work/server-before-charset'/item['file'];backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
 p.write_bytes(d)
 records.append({'file':item['file'],'sha256_before':hashlib.sha256(raw).hexdigest(),'sha256_after':hashlib.sha256(d).hexdigest(),'changed_byte_count':sum(x!=y for x,y in zip(raw,d)),'calls':calls,'new_pointer':hex(target_va),'change':'SQL connection utf8 value uses documented CharacterSet key instead of CharSet; no table or game rule edits'})
(b/'evidence/charset-patch-result.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(json.dumps(records,ensure_ascii=False,indent=2))
