from time import perf_counter

IFOR = 0.001
def run(func,msg='', iter=100_000):
	t = perf_counter()
	for i in range(iter):
		func()
	took = perf_counter()-t
	mul = took/IFOR
	print( f"{took},{msg} X{mul:.4f}")
	return took

IFOR = run(lambda :1, msg = 'for100k')

