import asyncio
import time

def longtime():
	for i in range(10000000):
		time.time()


async def counter(stop):
	i=0
	while i<stop:
		yield i
		i+=1
		await asyncio.sleep(0.0012)#15ms		


async def runner():
	async for i in counter(5):
		print(i)

asyncio.run( runner() )
