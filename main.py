
# nodetypes
NT_ATOM = "ATOM"
NT_FWD = "FWD"
NT_ASSIGN = "ASSIGN"
NT_VAR = "VAR"
NT_EXPR = "EXPRESSION"
NT_NONE = "NONE"
NT_ADD = "ADD"
NT_MUL = "MULTIPLY"
NT_SUB = "SUBTRACT"
NT_DIV = "DIVIDE"
NT_MOD = "MODULO"
NT_LPAREN = "LPAREN"
NT_RPAREN = "RPAREN"

UN_NODES = [
	NT_VAR,
	NT_EXPR
]

BIN_NODES = [
	NT_FWD,
	NT_ASSIGN,
	NT_ADD
]

LBIND = {
	NT_ADD: 3,
	NT_SUB: 3,
	NT_MUL: 4,
	NT_DIV: 4,
	NT_MOD: 2,
	NT_ASSIGN: 1.1,
	NT_FWD: 0.1
}
RBIND = {
	NT_FWD: 0,
	NT_ASSIGN: 1,
	NT_ADD: 3.1,
	NT_SUB: 3.1,
	NT_MUL: 4.1,
	NT_DIV: 4.1,
	NT_MOD: 2.1
}

class Debug:
	def __init__(self):
		self.logging = False
	def log(self, *args, **kwargs):
		if self.logging:
			print(*args, **kwargs)

debug = Debug()

class Node:
	def __init__(self, Type=NT_ATOM, left=None, right=None, state=dict([])):
		self.type = Type
		if Type in BIN_NODES:
			if left==None or right==None: raise ValueError("primary or secondary None value given for binary operation")
		if Type in UN_NODES:
			if left==None: raise ValueError("primary None value given for unary operation")
		self.left = left
		self.right = right
		self.state = state

	def copy(self, other):		# copies another node into self
		self.type=other.type
		self.left=other.left
		self.right=other.right
		self.state=other.state

	def run(self):
		if self.type==NT_FWD:		# fwd node: left is code, right is code. returns atom
			self.left.state = self.state
			self.left.run()
			self.right.state = self.left.state
			self.right.run()
			ret = Node(NT_ATOM,state=self.state)
			self.copy(ret)
			return
		if self.type==NT_ASSIGN:	# assign node: left is var, right is expr. returns atom
			if self.left.type != NT_VAR: raise SyntaxError("not a variable")
			self.right.state = self.state			
			self.right.run()
			ret = Node(NT_ATOM,left=self.right.left,state=self.right.state)
			ret.state[self.left.left] = self.right.left
			self.copy(ret)
		if self.type==NT_EXPR:		# expression node: left is evaluable. returns atom
			if self.left.type==NT_VAR:
				self.left = self.state[self.left.left]
				self.type = NT_ATOM
			else:
				self.left.state = self.state
				self.left.run()
				self.copy(self.left)
		if self.type==NT_VAR:		# var node: left is var name. returns atom
			self.left = self.state[self.left]
			self.type = NT_ATOM
		if self.type==NT_ADD:		# add node: left is expr, right is expr. returns atom
			self.left.state = self.state
			self.left.run()
			self.right.state = self.left.state
			self.right.run()
			ret = Node(NT_ATOM, left=0, state=self.right.state)
			ret.left += float(self.left.left)
			ret.left += float(self.right.left)
			self.copy(ret)
		if self.type==NT_SUB:		# sub node: left is expr, right is expr. returns atom
			self.left.state = self.state
			self.left.run()
			self.right.state = self.left.state
			self.right.run()
			ret = Node(NT_ATOM, left=0, state=self.right.state)
			ret.left += float(self.left.left)
			ret.left -= float(self.right.left)
			self.copy(ret)
		if self.type==NT_MUL:		# mul node: left is expr, right is expr. returns atom
			self.left.state = self.state
			self.left.run()
			self.right.state = self.left.state
			self.right.run()
			ret = Node(NT_ATOM, left=0, state=self.right.state)
			ret.left += float(self.left.left)
			ret.left *= float(self.right.left)
			self.copy(ret)
		if self.type==NT_DIV:		# div node: left is expr, right is expr. returns atom
			self.left.state = self.state
			self.left.run()
			self.right.state = self.left.state
			self.right.run()
			ret = Node(NT_ATOM, left=0, state=self.right.state)
			ret.left += float(self.left.left)
			ret.left /= float(self.right.left)
			self.copy(ret)
		if self.type==NT_MOD:		# mod node: left is expr, right is expr. returns atom
			self.left.state = self.state
			self.left.run()
			self.right.state = self.left.state
			self.right.run()
			ret = Node(NT_ATOM, left=0, state=self.right.state)
			ret.left += float(self.left.left)
			ret.left %= float(self.right.left)
			self.copy(ret)
	def __str__(self):
		return "".join([str(i) for i in [
			"(type: ",			
			self.type,
			", left: ",
			self.left,
			", right: ",
			self.right,
			")"
		]])


def lexer(string):
	tokens = []
	while string:
		curr = string[0]
		if curr in "\n\t ":pass
		elif False: 
			pass
		elif curr in "123456789":
			res = ""
			while string and string[0] in "0123456789":
				curr = string[0]
				res += curr
				string = string[1:]
			tokens.append(Node(NT_EXPR, left=Node(NT_ATOM, left=int(res))))
			continue
		elif curr == "(":
			tokens.append(Node(NT_LPAREN))
		elif curr == ")":
			tokens.append(Node(NT_RPAREN))
		elif curr=="=":
			tokens.append(Node(NT_ASSIGN, left=-1, right=-1))
		elif curr==";":
			if len(tokens)>0 and tokens[-1].type != NT_FWD:
				tokens.append(Node(NT_FWD, left=-1, right=-1))
		elif curr=="+":
			tokens.append(Node(NT_ADD, left=-1, right=-1))
		elif curr=="-":
			tokens.append(Node(NT_SUB, left=-1, right=-1))
		elif curr=="*":
			tokens.append(Node(NT_MUL, left=-1, right=-1))
		elif curr=="/":
			tokens.append(Node(NT_DIV, left=-1, right=-1))
		elif curr=="%":
			tokens.append(Node(NT_MOD, left=-1, right=-1))
		else:
			tokens.append(Node(NT_VAR, left=curr))
		string = string[1:]
	return tokens + [Node(NT_NONE)]*(tokens[-1].type == NT_FWD)


# Parser rekursiv machen
def parse(tokens):
	def parse_expr(tokens, i=0):
		out = []
		while i < len(tokens):
			tok = tokens[i]
			if tok.type == NT_LPAREN:
				subexpr, i = parse_expr(tokens, i + 1)
				out.append(Node(NT_EXPR, left=subexpr))
			elif tok.type == NT_RPAREN:
				break
			else:
				out.append(tok)
			i += 1
		return reduce_expr(out), i

	def reduce_expr(tokens):
		while len(tokens)>1:
			debug.log([str(i)for i in tokens])
			binds = [None for i in tokens]
			for i in range(len(tokens)):
				if i==0:
					prev = Node(NT_NONE)
				else:
					prev = tokens[i-1]
				if i==len(tokens)-1:
					nxt = Node(NT_NONE)
				else:
					nxt = tokens[i+1]
				curr = tokens[i]
				if not (nxt.type in LBIND.keys() or prev.type in RBIND.keys()):
					continue
				if not nxt.type in LBIND.keys():
					nxtval = -1
				else: nxtval = LBIND[nxt.type]
				if not prev.type in RBIND.keys():
					prevval= -1
				else: prevval = RBIND[prev.type]
				binds[i] = prevval==max(prevval, nxtval) # true if it binds to the left
			newtokens = []	
			debug.log(binds)
			for i in range(len(tokens)):
				if i==0:
					prev=None
				else:
					prev=binds[i-1]
				curr=binds[i]
				if i==len(binds)-1:
					nxt = None
				else:
					nxt=binds[i+1]
				if curr == True or curr == False:
					continue
				left = (not(tokens[i].type in LBIND.keys()) or prev==False)
				right= (not(tokens[i].type in RBIND.keys()) or nxt==True)
				if left and right:
					if tokens[i].type in LBIND.keys():
						leftnode = tokens[i-1]
					else:
						leftnode= None
					if tokens[i].type in RBIND.keys():
						rightnode= tokens[i+1]
					else:rightnode=None
					newtokens.append(Node(NT_EXPR, left=Node(tokens[i].type,left=leftnode,right=rightnode)))
				else:
					if prev==False:
						newtokens.append(tokens[i-1])
					newtokens.append(tokens[i])
					if nxt == True:
						newtokens.append(tokens[i+1])
			tokens = newtokens
		return tokens[0]


	tree, _ = parse_expr(tokens)
	return tree





def main():
	state = dict([])
	while True:
		_1 = lexer(input("> "))
		_2 = parse(_1)
		_2.state = state
		_2.run()
		state = _2.state
		print(state)
	return 0


if __name__=="__main__":
	print("exited with code {}".format(main()))

