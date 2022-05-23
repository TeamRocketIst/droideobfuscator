# droideobfuscator
Tool to decrypt strings in android applications.

This tool uses frida to evaluate string obfuscation functions in android applications.

By just providing the regular expression,class and the function the tool will be able to generate a frida script and replace the results in the decompiled code by jadx.

Only works with simple functions that have `String` , `long`, `char` literals as arguments.

Only static method are supported right now (if the constructor doesn't have any arguments it will work for non-static).

Usage:
```python
usage: deobfuscator.py -D [DIRECTORY] --apk [APK_FILES]

Deobfuscate strings.

optional arguments:
  -h, --help       show this help message and exit
  --apk [APK ...]  apk file or multiple if splitted.
  --pkg PKG        Package name of the application.
  --dir DIR        Directory of the jadx decompiled code. -> $ jadx -d dec_code example.apk
  --config CONFIG  config json with the classes

```

Command execution example:
```bash
$ python deobfuscator.py --pkg com.clashof.lights --dir ~/clash_jadx --config config.json
```

Example on how to obtain an optimal jadx file:
```bash
jadx --no-imports --show-bad-code -d clash_jadx clash.apk

```

Config file example:
```json
{
   "Array":[
      {
         "class":"com.supercell.titan.z1",
         "method":"a",
         "regex":"com\\.supercell\\.titan\\.z1\\.a\\(\".*?\"\\)"
      }
   ]
}
```

Field explaination:

- class -> class to be imported.
- method -> Method that will run.
- regex -> regular expression that will match the functions to be replaced in `.java` files .
