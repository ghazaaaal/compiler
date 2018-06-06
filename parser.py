from pythonds.basic.stack import Stack
import io
from grammar import grammar
from scanner import scanner
from table_manage import table_action,table_goto
from follows import follows
from codeGenerator import handle_if_while,new_scope,generate_code,ss_push,code_block,new_func

action= [[]]
goto=[[]]
alaki1=[]
alaki2=[]
out=[]
with io.open('parseTable.txt', 'r') as f:
  old_c='\t'
  s=''
  cnt=0;
  while True:
    c = f.read(1)
    if not c:
      print("End of File")
      break
    if (cnt<24):
      if c.__eq__('\t'):
        if (not old_c.__eq__('\t')):
          if s[0].__eq__('\t'):
            s=s[1:]
          alaki1.append(s)
          cnt=cnt+1
          s=''
          old_c = c
        else:
          s=c
          old_c = c
          alaki1.append(s)
          cnt = cnt + 1
      else:
        s=s+c
        old_c = c
    else:
      if (cnt-24<28):
        if c.__eq__('\t'):
          if (not old_c.__eq__('\t')):
            if s[0].__eq__('\t'):
              s = s[1:]
            alaki2.append(s)
            cnt = cnt + 1
            s = ''
            old_c = c
          else:
            s = c
            old_c = c
            alaki2.append(s)
            cnt = cnt + 1
        if c.__eq__('\n'):
          if old_c.__eq__('\t'):
            alaki2.append('\t')
          else:
            if s[0].__eq__('\t'):
              s=s[1:]
            alaki2.append(s)
          action.append(alaki1)
          goto.append(alaki2)
          alaki1=[]
          alaki2=[]
          s='\t'
          old_c='\t'
          cnt=0
        else:
          if (s.__eq__('\t')):
            s=''
          s = s + c
          old_c = c


action.remove([])
goto.remove([])
print(action)
print(goto)

grammar=grammar()
print(grammar)

inp=scanner()

print(inp)

s_input=Stack()
s_input.push(('z',''))
for i in range(0,inp.__len__()):
  #print(inp[inp.__len__()-1-i])
  s_input.push(inp[inp.__len__()-1-i])

s_parsser=Stack()
s_parsser.push((0,''))

map_action=table_action()
map_goto=table_goto()
follow=follows()

alaki=Stack()

while True:
  if s_parsser.size()>=13:
    char=''
    str=''
    alaki.push(s_parsser.peek())
    s_parsser.pop()
    alaki.push(s_parsser.peek())
    s_parsser.pop()
    char=alaki.peek()[0]
    if char=='l':
      for j in range(5):
        alaki.push(s_parsser.peek())
        s_parsser.pop()
        alaki.push(s_parsser.peek())
        s_parsser.pop()
        str=str+alaki.peek()[0]
      if not str.__eq__('jFibE'):
        new_scope()
      else:
        new_func()
      for j in range(6):
        s_parsser.push(alaki.peek())
        alaki.pop()
        s_parsser.push(alaki.peek())
        alaki.pop()
    else:
      s_parsser.push(alaki.peek())
      alaki.pop()
      s_parsser.push(alaki.peek())
      alaki.pop()

  if s_parsser.size()>=9:
    str=''
    for j in range(4):
      alaki.push(s_parsser.peek())
      s_parsser.pop()
      alaki.push(s_parsser.peek())
      s_parsser.pop()
      str=str+alaki.peek()[0]
    if str.__eq__('jQio'):
      handle_if_while()
    elif str.__eq__('jQiq'):
      handle_if_while()
    for j in range(4):
      s_parsser.push(alaki.peek())
      alaki.pop()
      s_parsser.push(alaki.peek())
      alaki.pop()

  s=action[s_parsser.peek()[0]][map_action.index(s_input.peek()[0])]
  #print(s)
  if s[0].__eq__('s'):
    indx=int(s[1:])
    s_parsser.push(s_input.peek())
    s_parsser.push((indx,''))
    #print('push', s_input.peek())
    print(s_input.peek())
    ss_push(s_input.peek())
    s_input.pop()
    #print(s_parsser.peek())
  elif s[0].__eq__('r'):
    indx=int(s[1:])
    rule=grammar[indx]
    print('reduce', rule)
    generate_code(indx)
    for i in range(0, rule.__len__()-1):
      if not rule[i+1].__eq__(''):
        s_parsser.pop()
        #print(s_parsser.peek())
        s_parsser.pop()
    #print(map_goto.index(rule[0]))
    #print(goto[s_parsser.peek()])
    #print(goto[s_parsser.peek()[0]][map_goto.index(rule[0])])
    indx=int(goto[s_parsser.peek()[0]][map_goto.index(rule[0])])
    #print(s_parsser.peek())
    #if indx==8:
     # s_parsser.push((rule[0],'g'))
    #elif indx==9:
     # s_parsser.push((rule[0],'h'))
    #elif indx==39:
     # s_parsser.push((rule[0],'t'))
    #elif indx==40:
     # s_parsser.push((rule[0],'u'))
    #elif indx==43:
     # s_parsser.push((rule[0],'w'))
    #elif indx==44:
     # s_parsser.push((rule[0],'x'))
    #else:
    s_parsser.push((rule[0],''))

    s_parsser.push((indx,''))
    #print(indx)
    #print(s_parsser.peek())
    #print(s_input.peek())
  elif s.__eq__('acc'):
    print("Parsed Successfully!")
    print(code_block)
    break
  else:
    print("Panic Mode")
    temp=s_parsser.peek()[0]

    s_parsser.pop()
    while not(s_parsser.isEmpty()) and not(s_parsser.peek()[0] in map_goto):
      temp=s_parsser.peek()[0]
      s_parsser.pop()
    if s_parsser.isEmpty():
      while s_input.isEmpty():
        s_input.pop()
      break
    else:
      non_terminal=s_parsser.peek()[0]
      #if goto[temp][map_goto.index(non_terminal)].__eq__('\t'):
       # print('Error')
        #break
      s_parsser.push((temp,''))
      non_terminal_follow=follow[map_goto.index(non_terminal)]
      #print(non_terminal_follow)
      #print(s_input.peek()[0])
      while not(s_input.isEmpty()) and not(s_input.peek()[0] in non_terminal_follow):
        s_input.pop()
      if s_input.isEmpty():
        while not s_parsser.isEmpty():
          s_parsser.pop()
        break


