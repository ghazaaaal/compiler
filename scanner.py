import re

def scanner():
	output = []
	with open('test1.txt') as fin:
		code = fin.read()
		code = re.sub("\/\*(?s:.)*?\*\/", "", code, flags=re.MULTILINE)
		for item in re.findall("(?<=[\[\{<\(=;,\*\+\-])\s*([+-][0-9]+)|\s*(?:([0-9]+)|(==)|([a-zA-Z0-9]+)|(.))", code):
			if item[0]:
				output.append(('e', int(item[0])))

			elif item[1]:
				output.append(('e', int(item[1])))

			elif item[2]:
				output.append(('u', item[2]))

			elif item[3]:
				if "int" == item[3]:
					output.append(('g', item[3]))

				elif "void" == item[3]:
					output.append(('h', item[3]))

				elif "if" == item[3]:
					output.append(('o', item[3]))

				elif "else" == item[3]:
					output.append(('p', item[3]))

				elif "while" == item[3]:
					output.append(('q', item[3]))

				elif "return" == item[3]:
					output.append(('r', item[3]))

				elif "EOF" == item[3]:
					output.append(('a', item[3]))

				else:
					output.append(('b', item[3]))

			else:
				if "{" == item[4]:
					output.append(('l', item[4]))

				elif "}" == item[4]:
					output.append(('m', item[4]))

				elif "[" == item[4]:
					output.append(('d', item[4]))

				elif "]" == item[4]:
					output.append(('f', item[4]))

				elif "(" == item[4]:
					output.append(('i', item[4]))

				elif ")" == item[4]:
					output.append(('j', item[4]))

				elif "*" == item[4]:
					output.append(('y', item[4]))

				elif "+" == item[4]:
					output.append(('w', item[4]))

				elif "-" == item[4]:
					output.append(('x', item[4]))

				elif "<" == item[4]:
					output.append(('t', item[4]))

				elif "=" == item[4]:
					output.append(('s', item[4]))

				elif ";" == item[4]:
					output.append(('c', item[4]))

				elif "," == item[4]:
					output.append(('k', item[4]))

				else:
					output = []
					return ("\nERROR: \"" + item[4] + "\" is invalid.")
	return output

