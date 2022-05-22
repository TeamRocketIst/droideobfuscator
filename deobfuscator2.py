import sys, re, os, base64, ast, javalang   
from decrypt2 import c
 
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
    if token.token_type[0] == javalang.tokenizer.String:
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
                print( replace_code_token(tok))
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
    code_tokens = javalang.tokenizer.tokenize(match)
    args = []
    for tok in code_tokens:
        if tok.value == '(':
            break
    for tok in code_tokens:
        #print(tok.value)
        if tok.value == ')':
            break
        else:
            args.append(tok)
    return args
 
def evaluate_to_python(args):
    n_args = []
    c = ""
    for a in args:
        if type(a) == javalang.tokenizer.Separator:
            n_args.append(ast.literal_eval(c))
            c= ""
        elif type(a) == javalang.tokenizer.DecimalInteger:
            c += a.value.replace('L','')
        else:
            c += a.value
    if c != "":
        print(c)
        n_args.append(ast.literal_eval(c))
    return n_args
 
 
def get_types(args):
    n_args = []
    c = ""
    for a in args:
        if type(a) == javalang.tokenizer.Separator:
            continue
        elif type(a) == javalang.tokenizer.Operator:
            continue
        else:
            n_args.append(type(a))
    return n_args
 
def escape_sequences_rules(s):
    # https://docs.python.org/3/reference/lexical_analysis.html
    d = {'\x5c': '\\\\', '"':'\\"', '\a':'\\a', '\b':'\\b', '\f':'\\f', '\n':'\\n', '\r':'\\r', '\t':'\\t', '\v':'\\v', '\n':'\\n'}
    return ''.join(d[c] if c in d else c for c in s)
 
enc_functions = [EncryptFunction(r'mccccc\.kkjjkk\.m677b0413041304130413\(\".*?\", (?:\d+?|\'.*?\'), (?:\d+?|\'.*?\'), (?:\d+?|\'.*?\')\)',
    "mccccc.kkjjkk","b0413Г041304130413Г"),
                 EncryptFunction(r'mccccc\.kkjjkk\.m675b04130413041304130413\(\".*?\", (?:\d+?|\'.*?\'), (?:\d+?|\'.*?\')\)',"mccccc.kkjjkk","b04130413041304130413\u0413")
                 ]
tk_list = DecryptTokenList(20000) 
 
 
if len(sys.argv) > 1:
    for enc_f in enc_functions:
        for root, subdirs, files in os.walk(sys.argv[1]):
            for file in files:
                if file.endswith('.java'):
                    #print(root, file)
                    absolute_path = root + "/" + file
                    f = open(absolute_path)
                    matches = re.findall(enc_f.regex, f.read())
                    #print(matches)
                    f.close()
                    #print(matches)
                    if matches:
                        for match in matches:
                            with open(absolute_path) as f:
                                print(match)
                                args = get_arguments_invocation(match)
                                #print(args[1].value)
                                
                                if args:
                                    if tk_list.add_token(evaluate_to_python(args), get_types(args), match, absolute_path, enc_f.method, enc_f._cls):
                                        all_tokens = c(tk_list.get_tokens())
                                        write_decrypt_tokens_file(all_tokens)
                                        tk_list.reset_tokens()
    if not tk_list.isEmpty():
        all_tokens = c(tk_list.get_tokens())
        write_decrypt_tokens_file(all_tokens)
        tk_list.reset_tokens()