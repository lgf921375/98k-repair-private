#!/usr/bin/env python3
import hashlib,json,subprocess,zipfile,shutil,time
from pathlib import Path
B=Path('/srv/projects/98k/repair-20261014');R=B/'work/compat-root'
E=B/'evidence/app-newchar-20261015/login-ui-state-20261016'
stage=R/'apk-out/login-ui-v2-20261016';stage.mkdir(parents=True,exist_ok=True)
source=B/'output/98k-serverip-20261015-arm32-candidate.apk'
payload=B/'work/patch-candidates/98k-client-login-guard-v2-20261016.candidate.so'
out=B/'output/98k-loginui-v2-20261016-arm32-candidate.apk'
payload_sha='7e9a5d19a00f7ee6ccc55b5e57b6531d492d654e1344ad56b460fa274445112e'
assert source.is_file() and payload.is_file() and hashlib.sha256(payload.read_bytes()).hexdigest()==payload_sha
assert not out.exists()
signer=R/'usr/share/java/apksigner.jar'; assert signer.is_file()
def log(x): print(time.strftime('%Y-%m-%dT%H:%M:%S'),x,flush=True)
def run(cmd,name):
 log(name)
 with (E/('v2-'+name+'.log')).open('w') as f: subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=360)
unsigned=stage/'unsigned.apk'; aligned=stage/'aligned.apk'
with zipfile.ZipFile(source) as src,zipfile.ZipFile(unsigned,'w',allowZip64=True) as dst:
 infos=src.infolist()
 assert 'lib/armeabi-v7a/libgame.so' in {x.filename for x in infos}
 for i,info in enumerate(infos,1):
  n=info.filename
  if n.startswith('META-INF/') and n.upper().endswith(('.MF','.SF','.RSA','.DSA','.EC')): continue
  if n=='lib/armeabi-v7a/libgame.so': dst.writestr(info,payload.read_bytes())
  else:
   with src.open(info) as a,dst.open(info,'w') as b: shutil.copyfileobj(a,b,1024*1024)
  if i%800==0:log(f'ZIP {i}/{len(infos)}')
run(['chroot',str(R),'/usr/bin/zipalign','-f','-p','4','/apk-out/login-ui-v2-20261016/unsigned.apk','/apk-out/login-ui-v2-20261016/aligned.apk'],'align')
unsigned.unlink()
run(['java','-Xmx256m','-jar',str(signer),'sign','--ks',str(B/'keys/98k-candidate.p12'),'--ks-pass','file:'+str(B/'keys/store-pass.txt'),'--ks-key-alias','98k-candidate','--out',str(out),str(aligned)],'sign')
run(['java','-Xmx256m','-jar',str(signer),'verify','--verbose','--print-certs',str(out)],'signature')
shutil.copyfile(out,stage/'signed.apk')
run(['chroot',str(R),'/usr/bin/zipalign','-c','-p','4','/apk-out/login-ui-v2-20261016/signed.apk'],'align-verify')
changed=[]
with zipfile.ZipFile(source) as before,zipfile.ZipFile(out) as after:
 assert after.testzip() is None
 sb=set(before.namelist()); sa=set(after.namelist())
 assert {x for x in sb if not x.startswith('META-INF/')}=={x for x in sa if not x.startswith('META-INF/')}
 for n in sorted(sb&sa):
  if n.startswith('META-INF/'): continue
  if n=='lib/armeabi-v7a/libgame.so':
   assert hashlib.sha256(after.read(n)).hexdigest()==payload_sha
   assert before.read(n)!=after.read(n)
   changed.append(n)
  else:
   h1=hashlib.sha256();h2=hashlib.sha256()
   with before.open(n) as x,after.open(n) as y:
    for z in iter(lambda:x.read(2**20),b''):h1.update(z)
    for z in iter(lambda:y.read(2**20),b''):h2.update(z)
   assert h1.digest()==h2.digest(),n
 assert changed==['lib/armeabi-v7a/libgame.so']
sig=(E/'v2-signature.log').read_text().lower()
assert 'verified using v2 scheme (apk signature scheme v2): true' in sig
assert 'verified using v3 scheme (apk signature scheme v3): true' in sig
assert '4ff6bc600d59ec1591231e2b3b238b05844a3539f8c1c1d0e192b522298c3c30' in sig
h=hashlib.sha256()
with out.open('rb') as f:
 for x in iter(lambda:f.read(2**20),b''):h.update(x)
res={'apk':str(out),'bytes':out.stat().st_size,'sha256':h.hexdigest(),'payload_sha256':payload_sha,
     'changed_non_signature_entries':changed,'v2_signature':True,'v3_signature':True,'zipalign':True,'zip_crc':True,
     'same_signing_cert_as_prior_candidate':True,'phone_test':'NOT_TESTED','empty_input_fix':'CANDIDATE','registration_reenable':'CANDIDATE'}
(E/'apk-v2-validation.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
for p in (aligned,stage/'signed.apk'):
 if p.exists(): p.unlink()
print('APK_V2_COMPLETE')
print('APK_SHA256',res['sha256'])
print('APK_BYTES',res['bytes'])
print('OUT',out)
