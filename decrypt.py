from __future__ import print_function
import frida
import sys, os, queue, javalang
from utils import get_package_name

class DecryptToken:
    def __init__(self, token, token_type, match, absolute_path):
        super(DecryptToken, self).__init__()
        self.token = token
        self.token_type = token_type
        self.match = match
        self.absolute_path = absolute_path
 
 
def init_session(apk_file=None,package=None):
    global q
    global session
    q = queue.Queue()
    if package is None and apk_file is not None:
        package = get_package_name(apk_file)    
    #cmd = 'adb shell "ps | grep \'%s\' | awk \'{print \\$2}\'"'%package
    device = frida.get_usb_device()
    #print(device)
    pid = device.spawn(package) #int(os.popen(cmd).read().rstrip().split('\n')[0])
    #print(pid)
    device.resume(pid)    
    session = device.attach(pid)
 
 
def token_to_frida(index, tokens):
    #print(tokens.token_type[index])
    #exit(0)
    if tokens.token_type[index] == str and len(tokens.token[index]) != 1:
        return "Java.use('java.lang.String').$new(%s)" % str(list([ord(x) for x in tokens.token[index]]))
    elif tokens.token_type[index] == str and len(tokens.token[index]) == 1:
        return "String.fromCharCode(%d)" % ord(tokens.token[index])
    elif tokens.token_type[index] == int and (tokens.token[index] >= 0 and tokens.token[index] <= 0xff):
        return "String.fromCharCode(%d)" % tokens.token[index]
    elif tokens.token_type[index] == int:
        return "Java.use('java.lang.Long').parseLong('%d')" % tokens.token[index]
    elif tokens.token_type[index] == bytearray:
        return "%s" % str(list(tokens.token[index]))
 
def tokens_to_frida_args(tokens):
    output = []
    for i in range(len(tokens.token)):
        output.append(token_to_frida(i, tokens))
    #print(output)
    return ','.join(output)
 
def on_message(message, data):
    if 'payload' in message.keys():
        q.put(str(message['payload']))
    else:
        print(message)
 
 
def generate_frida_payloads(data):
    tokens = data
    script = """
    var a%d = Java.use('%s').$new();
    var byteArray%d = a%d.%s(%s);
    send(byteArray%d);
    """
    apply_script = "Java.perform(function x () {\n"
    for i,tok in enumerate(tokens):
        apply_script += script % (i,tok._cls, i,i, tok.method, tokens_to_frida_args(tok),i)
    apply_script += "});"
    #print(apply_script)
    return apply_script
 
def dec_fun(data):
    script = generate_frida_payloads(data)
    #print(script)
    script = session.create_script(script)
    script.on('message', on_message)
    script.load()
    output_data = []
    for t in data:
        c = q.get()
        output_data.append(DecryptToken(c, t.token_type, t.match, t.absolute_path))
    return output_data
 
def c(data):
    return dec_fun(data)
