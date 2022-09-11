from time import perf_counter


def run(func,msg='', iter=100_000):
	t = perf_counter()
	for i in range(iter):
		func()
	took = perf_counter()-t
	print(took,msg)
	return took

run(lambda :1, msg = 'for100k')

