import collections

MUL = 0
DIV = 1
ADD = 2
SUB = 3
CAT = 4
GT = 5
GE = 6
LT = 7
LE = 8
EQ = 9
NEQ = 10
NEG = 11
AND = 12
OR = 13
NOT = 14
START = 17
SET = 18
RESOLVE = 19

debugOp = [''] * 20

debugOp[MUL] = '*'
debugOp[DIV] = '/'
debugOp[ADD] = '+'
debugOp[SUB] = '-'
debugOp[CAT] = '~'
debugOp[GT] = '>'
debugOp[GE] = '>='
debugOp[LT] = '<'
debugOp[LE] = '<='
debugOp[EQ] = '=='
debugOp[NEQ] = '!='
debugOp[NEG] = '~'
debugOp[AND] = '&&'
debugOp[OR] = '||'
debugOp[NOT] = '!'
debugOp[SET] = '='
debugOp[RESOLVE] = 'RESOLVE'

priority = [0] * 20

priority[NOT] = 9
priority[NEG] = 9
priority[MUL] = 8
priority[DIV] = 8
priority[ADD] = 7
priority[SUB] = 7
priority[CAT] = 6
priority[GT] = 5
priority[GE] = 5
priority[LT] = 5
priority[LE] = 5
priority[EQ] = 4
priority[NEQ] = 4
priority[AND] = 3
priority[OR] = 3
priority[SET] = 1

def debug(s: str):
	#print(s)
	pass

class MathEval:

	def __init__(self):
		self.ops = []
		self.vals = []
		self.lastSymbol = None
		self.assignSymbol = None
		self.inNumeric = False
		self.inString0 = False
		self.inString1 = False
		self.inSymbol = False
		self.syntaxError = -1
		self.val = ''
		self.everUsed = False

	def GetNum(self, key):
		try:
			return int(key)
		except ValueError:
			return 0

	def IsNum(self, key):
		try:
			int(key)
			return True
		except ValueError:
			return False

	def Operate(self, count):
		debug(f"Operate {count} on ops={self.ops} vals={self.vals}")
		while count > 0:
			op = self.ops.pop()
			debug(f"op={debugOp[op]}")
			if op == START:
				return
			v = self.vals.pop()
			debug(f"popped val {v}")

			if op == NEG:
				debug("Operate Negating {v}")
				self.vals.append(str(-self.GetNum(v)))
				count -= 1
				continue

			if op == NOT:
				debug("Operate Notting {v}")
				self.vals.append('1' if self.GetNum(v) == 0 else '0')
				count -= 1
				continue

			if len(self.vals)<=0:
				debug(f"vals is empty when count is {count}")

			r = self.vals.pop()
			debug(f"operating v = {v} {debugOp[op]} {r}")

			if op == SET:
				self.assignFn(self.assignSymbol,v)
			elif op == CAT:
				v = r + v
			elif op == ADD:
				v = str(self.GetNum(v) + self.GetNum(r))
			elif op == SUB:
				v = str(self.GetNum(r) - self.GetNum(v))
			elif op == MUL:
				v = str(self.GetNum(r) * self.GetNum(v))
			elif op == DIV:
				v = str(self.GetNum(r) // self.GetNum(v))
			elif op == GT:
				v = '1' if self.GetNum(r) > self.GetNum(v) else '0'
			elif op == GE:
				v = '1' if self.GetNum(r) >= self.GetNum(v) else '0'
			elif op == LT:
				v = '1' if self.GetNum(r) < self.GetNum(v) else '0'
			elif op == LE:
				v = '1' if self.GetNum(r) <= self.GetNum(v) else '0'
			elif op == EQ:
				v = '1' if self.GetNum(r) == self.GetNum(v) else '0'
			elif op == NEQ:
				v = '1' if self.GetNum(r) != self.GetNum(v) else '0'
			elif op == AND:
				v = '1' if (self.GetNum(r) != 0) and (self.GetNum(v)!= 0) else '0'
			elif op == OR:
				v = '1' if (self.GetNum(r) != 0) or (self.GetNum(v)!= 0) else '0'
			debug("v -> {v}")
			self.vals.append(v)

			count -= 1

	def DoString(self, s, stopChar, i, expr):
		end = i == len(expr) - 2
		if end and s != stopChar:
			self.val += s
		if s == stopChar or end:
			debug(f"String is [{self.val}]")
			self.vals.append(self.val)
			self.val = ''
			return (i,False)
		# Escape character
		if s == "\\" and expr[i + 1] == stopChar:
			i += 1
			s = expr[i]
		self.val += s
		return (i,True)

	def DoSymbol(self, s):
		if s.isalnum() or s=='_' or s=='.' or s==':':
			self.val += s
			return True
		# We might need the original symbol if it turns out we're assigning
		self.lastSymbol = self.val

		debug(f"Interpreting {self.val}")
		result = self.interpretFn(self.val)
		if result==None:
			result = self.val
		if len(self.ops) > 0:
			if self.ops[-1] == NEG:
				# Negating
				debug(f"inSymbol Negating {result}")
				self.ops.pop()
				result = str(-self.GetNum(result))
			elif self.ops[-1] == NOT:
				# Notting
				debug(f"inSymbol Notting {result}")
				self.ops.pop()
				result = '1' if self.GetNum(result) == 0 else '0'
		debug(f"inSymbol appending {result}")
		self.vals.append(result)
		self.inSymbol = False
		self.val = ''
		return False

	def DoNumeric(self,s):
		if s.isdigit():
			self.val += s
			return True
		if len(self.ops) > 0 and self.ops[-1] == NEG:
			debug(f"inNumeric Negating {self.val}")
			self.vals.append(str(-self.GetNum(self.val)))
			self.ops.pop()
		elif len(self.ops) > 0 and self.ops[-1] == NOT:
			debug(f"inNumeric Notting {self.val}")
			self.vals.append('1' if self.GetNum(self.val) == 0 else '0')
			self.ops.pop()
		else:
			debug(f"inNumeric appending {self.val}")
			self.vals.append(self.val)
		self.inNumeric = False
		self.val = ''
		return False

	def Evaluate(self, input, interpretFn, assignFn):
		self.interpretFn = interpretFn
		self.assignFn = assignFn
		expr = "(" + input + ")"
		if self.everUsed:
			self.__init__()
		self.everUsed = True

		lastWasOp = True

		i = -1
		iEnd = len(expr) - 1
		while i < iEnd:
			i += 1
			s = expr[i]
			#debug(f"EVAL {s} and i={i}")
			if self.inString0:
				(i,self.inString0) = self.DoString(s, '\"', i, expr)
				continue
			if self.inString1:
				(i,self.inString1) = self.DoString(s, '\'', i, expr)
				continue
			if self.inSymbol:
				con = self.DoSymbol(s)
				if con: continue
			if self.inNumeric:
				con = self.DoNumeric(s)
				if con: continue

			topOp = self.ops[-1] if len(self.ops) > 0 else -1
			op = -1

			if s == '(':
				self.ops.append(START)
				continue
			elif s == '\"':					
				self.inString0 = True
				self.val = ''
				if not lastWasOp and self.assignSymbol:
					op = RESOLVE
				lastWasOp = False
			elif s == '\'':
				self.inString1 = True
				self.val = ''
				if not lastWasOp and self.assignSymbol:
					op = RESOLVE
				lastWasOp = False
			elif s.isdigit():
				self.inNumeric = True
				self.val = s
				if not lastWasOp and self.assignSymbol:
					op = RESOLVE
				lastWasOp = False
			elif s.isalpha():
				self.inSymbol = True
				self.val = s
				if not lastWasOp and self.assignSymbol:
					op = RESOLVE
				lastWasOp = False
			elif s.isspace():
				pass
			elif s == '~':
				op = CAT
			elif s == '+':
				op = ADD
			elif s == '-':
				op = SUB
			elif s == '*':
				op = MUL
			elif s == '/':
				op = DIV
			elif s == '<':
				if expr[i + 1] == '=':
					op = LE
					i += 1
				else:
					op = LT
			elif s == '>':
				if expr[i + 1] == '=':
					op = GE
					i += 1
				else:
					op = GT
			elif s == '=':
				if expr[i + 1] == '=':
					op = EQ
					i += 1
				else:
					op = SET
					self.assignSymbol = self.lastSymbol
			elif s == '!':
				if expr[i + 1] == '=':
					op = NEQ
					i += 1
				else:
					op = NOT
			elif s == '&':
				if expr[i + 1] == '&':
					i += 1
					debug(f"int & i={i}")
				op = AND
			elif s == '|':
				op = OR
				if expr[i + 1] == '|':
					i += 1
			elif s == ')':
				op = RESOLVE
			else:
				if syntaxError == -1:
					syntaxError = i

			if op==RESOLVE:
				self.Operate(len(self.ops))
				continue
			
			if op >= 0:
				if lastWasOp and op == SUB:
					self.ops.append(NEG)
					continue
				self.lastSymbol = None
				if priority[op] <= priority[topOp]:
					debug(f"{debugOp[op]} lower or same precedence as {debugOp[topOp]}")
					self.Operate(1)
				debug(f"pushing {debugOp[op]}")
				self.ops.append(op)
				lastWasOp = True

		return "" if len(self.vals) <= 0 else self.vals.pop()

def MathAssign(expr, interpretFn):
	varDict = {}
	def assign(symbol,value):
		nonlocal varDict
		varDict[symbol] = value

	mathEval = MathEval()
	mathEval.Evaluate(expr, interpretFn, assign)
	return varDict

def test_mathEval():
	def interp(symbol):
		if symbol == "a":
			return "1"
		if symbol == "b":
			return "5"
		if symbol == "c":
			return "hello"
		if symbol == "d":
			return "world"
		if symbol == "e":
			return "0"
		return None

	def test(expr, expect, expectSynLine=-1, expectVarList={}):
		varList = {}
		def assign(symbol,value):
			nonlocal varList
			debug(f"Assigning {symbol} = {value}")
			varList[symbol] = value

		debug(f"TESTING {expr}")
		mathEval = MathEval()
		result = mathEval.Evaluate(expr, interp, assign)
		if not varList == expectVarList:
			print(f"FAILURE  [{expr}] got varlist {varList} but wanted {expectVarList}")
			exit(1)
		if result != expect:
			print(f"FAILURE  [{expr}] = [{result}] but should be [{expect}]")
			exit(1)
		if mathEval.syntaxError>=0 and mathEval.syntaxError!=expectSynLine:
			print(f"Math: Syntax error in [{expr}] at char {mathEval.syntaxError}")
			exit(1)
		
	def runAll():
		test("myvar=10", "10", -1, {"myvar": "10"})
		test("v1=-5+88 v2=!b", "0", -1, {"v1": "83", "v2": "0"})
		test(
			"cmd=hello param1='the world' param2=\"bob\"", "bob", -1,
			{"cmd": "hello", "param1": "the world", "param2": "bob"}
		)
		test("'hello world'", "hello world")
		test("\"hello world\"", "hello world")
		test("'hello '~'world'", "hello world")
		test("('hello' ~ ' ') ~ 'world'", "hello world")
		test("c~' '~d", "hello world")

		test("", "")
		test("!0", "1")
		test("!32", "0")
		test("!a && b", "0")
		test("b+!a", "5")
		test("1!=5", "1")
		test("77!=70+7", "0")
		test("b!=a", "1")
		test("a==1 && !e", "1")
		test("0", "0")
		test("1", "1")
		test("1+1", "2")
		test("1>0", "1")
		test("1<0", "0")
		test("1>=0", "1")
		test("1<=0", "0")
		test("10==10", "1")
		test("1==0", "0")
		test("305-7", "298")
		test("4+5*-2", "-6")
		test("-40*3+11", "-109")
		test("-7*-4", "28")
		test("2*2+4*4", "20")
		test("8+9*8-1020*4", "-4000")
		test("2*2+4<8+9*8-1000*4", "0")
		test("10/2", "5")
		test("(2*6)-(20/5)", "8")
		test("a+1", "2")
		test("2+a", "3")
		test("a>b", "0")
		test("a<b", "1")
		test("a+b", "6")
		test("-11==-b-6", "1")
		test("((4*a)+(8*b))", "44")
		test("((4*a)+(8*b)) < 5", "0")
		test("66+(5-(3*2))+1*4", "69")
		test("8*(2+4)*100", "4800")
		test("10-9-8-7-6-5-4-3-2-1", "-35")
		test("-b--7--a", "3")
		test("-b", "-5")
		test("-11==-b-6", "1")
		test("(b+6==11)+10", "11")
		test("10+(b+6==11)", "11")
		test("e==0 && notDefined", "0")
		test("'   '", "   ")
		test("'a  '", "a  ")
		test("'  b'", "  b")
		test("''~1~2~3", "123")
		test("'a'~3", "a3")
		test("''~(5+a+1)~'k'", "7k")
		test("''~111~\"a\"~222", "111a222")
		test("'12'~4", "124")
		test("c~b", "hello5")
		test("'hello", "hello")
		test("a>0 && b>0", "1")
		test("e==0 && a", "1")

	runAll()

if __name__ == '__main__':
	debug("Running tests")
	test_mathEval()