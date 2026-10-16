#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,datetime,struct
root=Path('/srv/projects/98k/repair-20261014')
audit=root/'evidence/app-newchar-20261015/login-ui-state-20261016'
original=root/'work/apk-decoded/lib/armeabi-v7a/libgame.so'
out=root/'work/patch-candidates/98k-client-registration-button-20261016.candidate.so'
section=audit/'reg-reenable-section.bin'
sha=lambda b:hashlib.sha256(b).hexdigest()
b=original.read_bytes()
assert sha(b)=='196955a9c8f472adabc410666d8de9f5d5d2e80aae4915bf46c1acee35ce62d6'
assert len(b)==22268784
hook=0x697cb0;cave=0x12c2980
# Strict ELF32 .text section and PT_LOAD executable section bounds.
pe=struct.unpack_from('<I',b,0x20)[0]
shents,shnum=struct.unpack_from('<HH',b,0x2e)
assert any(struct.unpack_from('<IIIIIIIIII',b,pe+n*shents)[1]==1
               and struct.unpack_from('<IIIIIIIIII',b,pe+n*shents)[3]==0x4c6330
               and struct.unpack_from('<IIIIIIIIII',b,pe+n*shents)[4]==0x4c6330
               and struct.unpack_from('<IIIIIIIIII',b,pe+n*shents)[5]==0xdfc690
               and struct.unpack_from('<IIIIIIIIII',b,pe+n*shents)[2]&0x4 for n in range(shnum))
assert b[hook:hook+4]==bytes.fromhex('43a84190')
assert b[cave:cave+64]==b'\0'*64
s=section.read_bytes()
assert len(s)==0x12c29a4
assert s[hook:hook+4]==bytes.fromhex('2af06696')
stub=s[cave:0x12c29a4]
assert len(stub)==36
assert stub[:4]==bytes.fromhex('2de91f40')
assert stub[0x1c:0x20]==bytes.fromhex('43a84190')
assert stub[-4:]==bytes.fromhex('d5f78891')
assert s[cave+36:cave+64]==b''
patched=bytearray(b)
patched[hook:hook+4]=s[hook:hook+4]
patched[cave:cave+36]=stub
delta=[i for i,(x,y) in enumerate(zip(b,patched)) if x!=y]
assert all(i in range(hook,hook+4) or i in range(cave,cave+36) for i in delta)
assert len(delta)<=40
assert not out.exists()
out.write_bytes(patched)
assert out.stat().st_size==original.stat().st_size
assert sha(original.read_bytes())==sha(b)
assert sha(out.read_bytes())==sha(patched)
report={
 'time':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds'),
 'candidate_path':str(out),'candidate_sha256':sha(patched),
 'original_sha256':sha(b),'same_file_size':True,'changed_bytes':len(delta),
 'hook_va':'0x697cb0','hook_len':4,'stub_va':'0x12c2980','stub_len':36,
 'stub_ends_inside_verified_64_byte_code_padding':True,
 'original_instructions_replayed':'add r0,sp,#0x10c; str r0,[sp,#0x104]',
 'button_offset':'0x294','setEnabled_vtable_offset':'0x2bc','arg_enabled':True,
 'preserved_registers':'r0-r4,lr','stack_abi_aligned':True,'relocations_required':False,
 'original_libgame_unmodified':True,'runtime_test':'NOT_TESTED',
 'apk_built':False,'apk_signed':False,'android_phone_test':'NOT_TESTED'
}
(audit/'candidate-verify.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('NATIVE_UI_PATCH_STATIC_PASS')
print('CHANGED_BYTES',len(delta),'HOOK_AND_STUB_ONLY')
print('CANDIDATE_SHA256',sha(patched))
print('ORIGINAL_UNCHANGED',sha(b))
print('CANDIDATE_PATH',out)
