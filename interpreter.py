# -*- coding:utf-8 -*-
"""
Lisp解释器。
1.目前不能检测')'是否正确（')'可以多但不能少）
2.不能2个数以上加减乘除，例如：(* 5 2 3)
"""

Number=(int,float)
Symbol=str
List=list


def tokenize(chars):
	return chars.replace('(',' ( ').replace(')',' ) ').split()
	
def parse(program):
	return read_from_tokens(tokenize(program))
	
def read_from_tokens(tokens):
	if len(tokens)==0:
		raise SyntaxError('unexpected EOF while reading')
	token=tokens.pop(0)
	if token=='(':
		L=[]
		while tokens[0] != ')':
			L.append(read_from_tokens(tokens))
		tokens.pop(0)
		return 	L
	elif ')'==token:
		raise SyntaxError('unexpected')
	else:
		return atom(token)
		
def atom(token):
	try: 
		return int(token)
	except ValueError:    
		try: 
			return float(token)
		except ValueError:
			return Symbol(token)
			
			
class Procedure(object):
	def __init__(self,parms,body,env):
		self.parms=parms
		self.body=body
		self.env=env
	
	def __call__(self,*args):
		return eval(self.body, Env(self.parms,args,self.env))

class Env(dict):
	def __init__(self,parms=(),args=(),outer=None):
		self.update(zip(parms,args))
		self.outer=outer
		
	def find(self,var):
		return self if var in self else self.outer.find(var)
			
			
import math
import operator as op

def standard_env():
	env=Env()
	env.update(vars(math))
	env.update({'+':op.add,'-':op.sub,'*':op.mul,'/': lambda a,b: a/b,
				'>':op.gt,'<':op.lt,'>=':op.ge,'<=':op.le,'=':op.eq,
				'abs':	abs,
				'append':op.add,
				'begin':	lambda *x: x[-1],
				'car':	lambda x: x[0],
				'cdr':	lambda x: x[1:],
				'cons':	lambda x,y: [x]+y,
				'eq?':	op.is_,
				'equal?':	op.eq,
				'length':	len,
				'list':		lambda *x: list(x),
				'list?':	lambda x: isinstance(x,list),
				'map':	map,
				'max':	max,
				'min':	min,
				'not':	op.not_,
				'null?':	lambda x: x==[],
				'number?':	lambda x: isinstance(x,Number),
				'procedure?':	callable,
				'round':	round,
				'symbol?':	lambda x: isinstance(x,Symbol),
				})
				
	return env
	
global_env=standard_env()

#Scheme的语句被parse()函数转换成列表后传入参数x
def eval(x,env=global_env):
	if isinstance(x,Symbol):
		return env.find(x)[x]
	elif not isinstance(x,List):
		return x
	elif x[0]=='qoute':
		(_,exp)=x
		return exp
	elif x[0]=='if':
		(_,test,conseq,alt)=x
		#test是列表，eval(test,env)返回True或者Flase
		exp=(conseq if eval(test,env) else alt)
		return eval(exp,env)
	elif x[0]=='define':
		(_,var,exp)=x
		#在环境中设置var=exp，exp要么是个数字，要么是列表
		env[var]=eval(exp,env)
	elif x[0]=='set!':
		(_,var,exp)=x
		env.find(var)[var]=eval(exp,env)
	elif x[0]=='lambda':
		(_,parms,body)=x
		return Procedure(parms,body,env)
		
	else:
		#返回x列表中第一个元素对应的函数
		proc=eval(x[0],env)
		#生成参数列表
		args=[eval(arg,env) for arg in x[1:]]
		#*args导入args中的所有元素(在list或tuple前面加一个*号可以把list或tuple的元素变成可变参数传进去)
		return proc(*args)

def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop." 
    while True:
        val = eval(parse(input(prompt)))
        if val is not None: 
            print(schemestr(val))

def schemestr(exp):
    "Convert a Python object back into a Scheme-readable string."
    if isinstance(exp, List):
		#如果求值结果是列表，将它转换成Scheme的列表表示方式，不转换返回的python列表的格式
		#map(schemestr,exp),将exp中的列表转换成seheme列表，将不是list 又不是str的元素转换成str
        return '(' + ' '.join(map(schemestr, exp)) + ')' 
    else:
        return str(exp)
		

if __name__=='__main__':
	repl()