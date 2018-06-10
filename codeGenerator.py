from pythonds.basic.stack import Stack
import sys

code_block = [
    "(ASSIGN, #END_OF_CODE, MAIN_RETURN, )",
    "(JP, MAIN_START, , )",
]
function_table = {}
symbol_table = [{}]
current_scope = 0
data_address = 100
array_address = 500
temp_address = 1000
ss = Stack()
param_list = []
saved_data_addr = 0
saved_code_addr = 0


def lookup_symbol(symbol):
    current_scope = True
    for table in reversed(symbol_table):
        if symbol in table:
            return current_scope, table[symbol]
        current_scope = False
    return False, None

def lookup_function(name):
    return function_table.get(name, None)


def add_var(name, type):
    global data_address, symbol_table
    symbol_table[current_scope][name] = [type, data_address]
    data_address += 4
    return data_address - 4
    
def allocate_array(size):
    global array_address
    array_address += size
    return array_address - size

def new_func():
    global saved_code_addr, saved_data_addr, data_address, param_list
    saved_code_addr = len(code_block)
    saved_data_addr = data_address
    data_address = data_address + 8
    new_scope()
    for (type, name) in param_list:
        add_var(name, type)
    param_list = [type for (type, _) in param_list]
    
def add_func(t, f, params):
    global function_table
    function_table[f] = [t, saved_code_addr, saved_data_addr, params]
    
def new_scope():
    global current_scope
    symbol_table.append({})
    current_scope = current_scope + 1
    
def clear_scope():
    global current_scope
    del symbol_table[current_scope]
    current_scope = current_scope - 1
    
def ss_push(token):
    print('request to push', token[1])
    print('before push stack: ',ss.items)
    excluded_tokens = ['{', '}', '(', ')', '[', ']', ',', ';', 'if', 'else', 'while', 'return', 'EOF', '=']
    if token[1] not in excluded_tokens:
        ss.push(token[1])    
    if token[1] == 'else':
        handle_else()
    elif token[1] == 'while':
        handle_while()
    print('after push stack: ',ss.items)
    
def panic(s):
    print("ERROR:", s)
    sys.exit(1)

def make_temp():
    global temp_address
    temp_address = temp_address + 4
    return ("temp", temp_address - 4)

def make_operand(operand):
    if isinstance(operand, int):
        return "#"+str(operand)
    elif isinstance(operand, tuple):
        if operand[0] == "temp" or operand[0] == "result":
            return str(operand[1])
        else:
            return "@"+str(operand[1])
    elif operand is None:
        panic("Invalid use of value of void function")
    else:
        symbol_ptr = lookup_symbol(operand)[1]
        if symbol_ptr is None:
            panic("Unbound variable: %s" % operand)
        return str(symbol_ptr[1])
    
def get_type(operand):
    if isinstance(operand, int) or isinstance(operand, tuple):
        return 'int'
    elif isinstance(operand, str):
        symbol_ptr = lookup_symbol(operand)[1]
        if symbol_ptr is None:
            panic("Unbound variable: %s" % operand)
        return symbol_ptr[0]
    elif operand is None:
        panic("Invalid use of value of void function")
    
def func_call():
    params = ss.pop()
    ID = ss.pop()
    f = lookup_function(ID)
    if f is None:
        if ID != 'output':
            panic("Undefined function: %s" % ID)
        if not len(params)==1 or not get_type(params[0])=='int':
            panic("Invalid argument for function output.")
        code_block.append("(PRINT, %s, , )" % (make_operand(params[0])))
        ss.push(None)
        return
    if len(params) != len(f[3]):
        print("boz", params, f[3])
        panic("Invalid number of parameters for function: %s" % ID)
    for (i,param) in enumerate(params):
        if get_type(param) != f[3][i]:
            panic("%dth parameter of %s has wrong type." %(i+1, ID))
        code_block.append("(ASSIGN, %s, %d, )" % (make_operand(param), f[2] + i*4 + 8))
    return_address = len(code_block)
    code_block.append("(ASSIGN, #%d, %d, )" % (return_address + 2, f[2]))
    code_block.append("(JP, %d, , )" % f[1])
    if f[0] == "int":
        ss.push(('result', f[2] + 4))
    else:
        ss.push(None)

def handle_if_while():
    print('request to handle if_while')
    print('before handle stack', ss.items)
    exp = ss.pop()
    code_block.append("(JPF, %s, PLACEHOLDER, )" % make_operand(exp))
    ss.push(len(code_block) - 1)
    print('after handle stack', ss.items)

def handle_else():
    code_block.append("(JP, PLACEHOLDER, , )")
    if_saved = ss.pop()
    code_block[if_saved] = code_block[if_saved].replace('PLACEHOLDER', str(len(code_block)))
    ss.push(len(code_block) - 1)

def handle_while():
    ss.push(len(code_block))
        
def generate_code(rule_num):
    print('request to reduce', rule_num)
    print('before reduce stack', ss.items)
    global param_list
    #var dec
    if rule_num == 6:
        ID = ss.pop()
        TS = ss.pop()
        if TS == "int":
            if not lookup_symbol(ID)[0]:
                add_var(ID, 'int')
            else:
                panic("Duplicate declaration.")
        else:
             panic("Invalid type-specifier.")
    
    elif rule_num == 7:
        num = ss.pop()
        ID = ss.pop()
        TS = ss.pop()
        if TS == "int":
            if not lookup_symbol(ID)[0]:
                array_first = allocate_array(num)
                var_address = add_var(ID, 'array')
                code_block.append("(ASSIGN, #%d, %d, )" % (array_first, var_address))
            else:
                panic("Duplicate declaration.")
        else:
            panic("Invalid type-specifier.")
    
    #param in func dec
    elif rule_num == 15:
        ID = ss.pop()
        TS = ss.pop()
        if TS == "int":
            if not lookup_symbol(ID)[0]:
                param_list.append(("int", ID))
            else:
                panic("Duplicate declaration.")
        else:
            panic("Invalid type-specifier.")
    elif rule_num == 16:
        ID = ss.pop()
        TS = ss.pop()
        if TS == "int":
            if not lookup_symbol(ID)[0]:
                param_list.append(("array", ID))
            else:
                panic("Duplicate declaration.")
        else:
            panic("Invalid type-specifier.")
    
    #func dec
    elif rule_num == 10:
        #ss.pop()
        ID = ss.pop()
        TS = ss.pop()
        if ID == 'main':
            code_block[0] = code_block[0].replace('MAIN_RETURN', str(saved_data_addr))
            code_block[1] = code_block[1].replace('MAIN_START', str(saved_code_addr))
        add_func(TS, ID, param_list)
        param_list = []
        code_block.append("(JP, @%d, , )" % (saved_data_addr))
        
    # void in fun def
    elif rule_num == 12:
        ss.pop()
    
    # cmpnd_stmnt
    elif rule_num == 17:
        clear_scope()
    
    #empty arg
    elif rule_num == 53:
        ss.push([])
    #arg list
    elif rule_num == 54:
        item = ss.pop()
        rest = ss.pop()
        ss.push(rest + [item])
    #first arg
    elif rule_num == 55:
        item = ss.pop()
        ss.push([item])
    
    #func call
    elif rule_num == 51:
        func_call()
    

    # array access    
    elif rule_num == 36:
        num = ss.pop()
        ID = ss.pop()
        symbol_ptr = lookup_symbol(ID)
        if symbol_ptr is None:
            panic("Undefined array: %s" % ID)
        if symbol_ptr[0] != 'array':
            panic("%s is not array" % ID)
        if get_type(num) != 'int':
            panic("array index is not integer: %s" % ID)
        temp1 = make_temp()
        code_block.append("(MULT, #4, %s, %d)" % (make_operand(num), temp1[1]))
        code_block.append("(ADD, %d, %d, %d)" % (temp1[1], symbol_ptr[1], temp1[1]))
        ss.push(('array_access', temp1[1]))
    #assign
    elif rule_num == 33:
        rhs = ss.pop()
        lhs = ss.pop()
        rhs_ok = get_type(rhs) == 'int'
        lhs_ok = (isinstance(lhs, tuple) and (lhs[0] == 'array_access')) or isinstance(lhs,str)
        if not lhs_ok or not rhs_ok: 
            panic("Illegal assignment")
        code_block.append("(ASSIGN, %s, %s, )" % (make_operand(rhs),make_operand(lhs)))
        ss.push(lhs)
    #end if    
    elif rule_num == 29:
        jump_ip = ss.pop()
        code_block[jump_ip] = code_block[jump_ip].replace('PLACEHOLDER', str(len(code_block))) # shayaaaaad # bekhaaaad
    #end while
    elif rule_num == 30:
        jump_ip = ss.pop()
        start = ss.pop()
        code_block.append("(JP, %d, , )" % start)
        code_block[jump_ip] = code_block[jump_ip].replace('PLACEHOLDER', str(len(code_block))) # shayaaaaad # bekhaaaad
    
    #return
    elif rule_num == 31:
        code_block.append("(JP, @%d, , )" % (saved_data_addr))
    #return exp
    elif rule_num == 32:
        return_value = ss.pop()
        code_block.append("(ASSIGN, %s, %d, )" % (make_operand(return_value), saved_data_addr + 4))
        code_block.append("(JP, @%d, , )" % (saved_data_addr))
    #EOF
    elif rule_num == 1:
        code_block[0] = code_block[0].replace('END_OF_CODE', str(len(code_block)))
        code_block.append('(JPF, #1, 0, )')
    #relop    
    elif rule_num == 37:
        oprand2=ss.pop()
        op=ss.pop()
        oprand1=ss.pop()
        temp=make_temp()
        if not (get_type(oprand1)=='int' and get_type(oprand2)=='int'):
            panic('Illegal type.')
        if op == '<':
            code_block.append('(LT, %s, %s, %s)'% (make_operand(oprand1),make_operand(oprand2),make_operand(temp)))
        else:
            code_block.append('(EQ, %s, %s, %s)'% (make_operand(oprand1),make_operand(oprand2),make_operand(temp)))
        ss.push(temp)
    #additive_expression
    elif rule_num == 41:
        oprand2=ss.pop()
        op=ss.pop()
        oprand1=ss.pop()
        temp=make_temp()
        if not (get_type(oprand1)=='int' and get_type(oprand2)=='int'):
            panic('Illegal type.')
        if op == '+':
            code_block.append('(ADD, %s, %s, %s)'% (make_operand(oprand1),make_operand(oprand2),make_operand(temp)))
        else:
            code_block.append('(SUB, %s, %s, %s)'% (make_operand(oprand1),make_operand(oprand2),make_operand(temp)))
        ss.push(temp)
    #MULT    
    elif rule_num==45:
        oprand2=ss.pop()
        ss.pop()
        oprand1=ss.pop()
        temp=make_temp()
        if not (get_type(oprand1)=='int' and get_type(oprand2)=='int'):
            panic('Illegal type.')
        code_block.append('(MULT, %s, %s, %s)'% (make_operand(oprand1),make_operand(oprand2),make_operand(temp)))
        ss.push(temp)
    #statement
    elif rule_num==27:
        ss.pop()

    print('before reduce stack', ss.items)
