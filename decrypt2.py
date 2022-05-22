from __future__ import print_function
import frida
import sys, os, queue, javalang
 
class DecryptToken:
    def __init__(self, token, token_type, match, absolute_path):
        super(DecryptToken, self).__init__()
        self.token = token
        self.token_type = token_type
        self.match = match
        self.absolute_path = absolute_path
 
def get_current_package():
    return os.popen("pwd | awk -F '/' '{print $6}'").read()
 
 
q = queue.Queue()
package = get_current_package().rstrip()
cmd = 'adb shell "ps | grep \'%s\' | awk \'{print \\$2}\'"'%package
device = frida.get_usb_device()
pid = device.spawn(package) #int(os.popen(cmd).read().rstrip().split('\n')[0])
device.resume(pid)    
session = device.attach(pid)
 
 
def token_to_frida(index, tokens):
    #print(tokens.token_type[index])
    if tokens.token_type[index] == javalang.tokenizer.String and len(tokens.token[index]) != 1:
        return "Java.use('java.lang.String').$new(%s)" % str(list([ord(x) for x in tokens.token[index]]))
    elif tokens.token_type[index] == javalang.tokenizer.String and len(tokens.token[index]) == 1:
        return "String.fromCharCode(%d)" % ord(tokens.token[index])
    elif tokens.token_type[index] == javalang.tokenizer.DecimalInteger and (tokens.token[index] >= 0 and tokens.token[index] <= 0xff):
        return "String.fromCharCode(%d)" % tokens.token[index]
    elif tokens.token_type[index] == javalang.tokenizer.DecimalInteger:
        return "Java.use('java.lang.Long').parseLong('%d')" % tokens.token[index]
 
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
    var a%d = Java.use('%s');
    var byteArray%d = a%d.%s(%s);
    send(byteArray%d);
    """
    apply_script = "Java.perform(function x () {\n"
    for i,tok in enumerate(tokens):
        apply_script += script % (i,tok._cls, i,i, tok.method,tokens_to_frida_args(tok),i)
    apply_script += "});"
    return apply_script
 
def dec_fun(data):
    script = generate_frida_payloads(data)
    #print(script)
    script = session.create_script(script)
    script.on('message', on_message)
    script.load()
    output_data = []
    for t in data:
        output_data.append(DecryptToken(q.get(), t.token_type, t.match, t.absolute_path))
    return output_data
 
def c(data):
    return dec_fun(data)