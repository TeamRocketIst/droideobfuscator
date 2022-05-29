import sys, re, os, base64, ast, javalang, argparse, json
from decrypt import c, init_session
from utils import init_argparse

class EncryptFunction(object):
    """docstring for EncryptFunction"""
    def __init__(self, regex, method, _cls):
        super(EncryptFunction, self).__init__()
        self.regex = regex
        self.method = method
        self._cls = _cls
 
class DecryptToken:
    def __init__(self, token, token_type, match, absolute_path, _cls, method):
        super(DecryptToken, self).__init__()
        self.token = token
        self.token_type = token_type
        self.match = match
        self.absolute_path = absolute_path
        self.method = method
        self._cls = _cls
 
def replace_code_token(token):
    #for token in tokens:
    if token.token_type[0] == str:
        return '"'+escape_sequences_rules(token.token)+'"'
    elif token.token_type[0] == javalang.tokenizer.Integer:
        return token.token
 
 
def write_decrypt_tokens_file(tokens):
    d = {}
    for token in tokens:
        if token.absolute_path in d.keys():
            d[token.absolute_path].append(token)
        else:
            d[token.absolute_path] = [token]
    for absolute_path in d.keys():
        with open(absolute_path, 'r') as f:
            file_code = f.read()
            for tok in d[absolute_path]:
                print(replace_code_token(tok))
                file_code = file_code.replace(tok.match, replace_code_token(tok))
                print(tok.match, tok.token)
            if file_code != '':
                with open(absolute_path, 'w') as f:
                    f.write(file_code)
 
 
class DecryptTokenList:
    def __init__(self, limit = 100):
        super(DecryptTokenList, self).__init__()
        self.args = []
        self.limit = limit
 
    def add_token(self, token, token_type, match, abs_path, method, _cls):
        self.args.append(DecryptToken(token, token_type, match, abs_path, method, _cls))
        return len(self.args) == self.limit
 
    def reset_tokens(self):
        self.args = []
 
    def get_tokens(self):
        return self.args
 
    def isEmpty(self):
        return len(self.args) == 0
 
def get_arguments_invocation(match):
    code_tokens = javalang.tokenizer.tokenize(match+';')
    exp = javalang.parser.Parser(code_tokens).parse_expression()
    if type(exp) == javalang.tree.ClassCreator:
        for selector in exp.selectors:
            if type(selector) == javalang.tree.MethodInvocation:
                return selector.arguments
            else:
                raise NotImplementedError(type(selectorl))
    elif type(exp) == javalang.tree.MethodInvocation:
        return exp.arguments
    
    #exit(0)
    """args = []
    for tok in code_tokens:
        if tok.value == '(':
            break
    for tok in code_tokens:
        #print(tok.value)
        if tok.value == ')':
            break
        else:
            args.append(tok)
    return args"""
 
def evaluate_to_python(args):
    n_args = []
    for a in args:
        #print(ast.literal_eval(a.value),type(ast.literal_eval(a.value)), a)
        if type(a) == javalang.tree.Literal:
            n_args.append(ast.literal_eval(a.value))
        elif type(a) == javalang.tree.ArrayCreator:
            array = bytearray()
            for element in a.initializer.initializers:
                if type(element) == javalang.tree.Literal:
                    array.append(ast.literal_eval(element.value))
                else:
                    continue
                    raise NotImplementedError("Can't evaluate "+str(type(element)) +"inside of a"+ str(type(a))+ " yet")

            n_args.append(array)
        else:
            raise NotImplementedError("Can't evaluate "+str(type(a)) +" yet")
    #print(n_args)
    return n_args
 
 
def get_types(args):
    n_args = []
    for a in args:
        n_args.append(type(a))
    return n_args
 
def escape_sequences_rules(s):
    # https://docs.python.org/3/reference/lexical_analysis.html
    d = {'\x5c': '\\\\', '"':'\\"', '\a':'\\a', '\b':'\\b', '\f':'\\f', '\n':'\\n', '\r':'\\r', '\t':'\\t', '\v':'\\v', '\n':'\\n'}
    return ''.join(d[c] if c in d else c for c in s)

if __name__ == '__main__':
    args = init_argparse().parse_args()
    if args.apk:
        init_session(apk_file=args.apk[0])
    else:
        init_session(package=args.pkg)

    enc_functions = []
    jadx_dir = args.dir
    json_configs = json.load(args.config)
    for enc_f in json_configs['Array']:
        enc_functions.append(EncryptFunction(enc_f["regex"], enc_f["class"], enc_f["method"]))

    tk_list = DecryptTokenList(20000) 


    for enc_f in enc_functions:
        for root, subdirs, files in os.walk(jadx_dir):
            for file in files:
                if file.endswith('.java'):
                    #print(root, file)
                    absolute_path = root + "/" + file
                    f = open(absolute_path)
                    fr = f.read()
                    matches = re.findall(enc_f.regex, fr)
                    #print(matches)
                    f.close()
                    if matches:
                        #print(matches)
                        #print(fr)
                        for match in matches:
                            #print(match)
                            args = get_arguments_invocation(match)
                            #print(args)
                            #print(args[1].value)
                            
                            if args:
                                eval_p = evaluate_to_python(args)
                                if tk_list.add_token(eval_p, get_types(eval_p), match, absolute_path, enc_f.method, enc_f._cls):
                                    all_tokens = c(tk_list.get_tokens())
                                    write_decrypt_tokens_file(all_tokens)
                                    tk_list.reset_tokens()
    if not tk_list.isEmpty():
        all_tokens = c(tk_list.get_tokens())
        write_decrypt_tokens_file(all_tokens)
        tk_list.reset_tokens()
