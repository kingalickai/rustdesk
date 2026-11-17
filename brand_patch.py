# -*- coding: utf-8 -*-
import io
p = 'libs/hbb_common/src/config.rs'
s = io.open(p, encoding='utf-8').read()
old = 'RwLock::new(' + chr(34) + 'RustDesk' + chr(34) + '.to_owned())'
new = 'RwLock::new(' + chr(34) + '唐意·远控' + chr(34) + '.to_owned())'
assert old in s, 'APP_NAME default not found'
s = s.replace(old, new, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('[brand] APP_NAME default replaced OK')
