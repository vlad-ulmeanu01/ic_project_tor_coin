"""import asyncio
import time
import multiprocessing as mp

def func(x: int):
    for i in range(100):
        time.sleep(x / 50)
        print(f"{x} ", end = '', flush = True)

def main():
    #print(f"CPU count: {mp.cpu_count()}")
    #pool = mp.Pool(mp.cpu_count())
    procs = []
    for i in range(15):
        procs.append(mp.Process(target = func, args = (i, )))
        procs[i].start()

    for i in range(5):
        procs[i].join()

    #for i in range(1, 5):
    #    pool.apply_async(func, args = (i))
    #pool.close()
    #pool.join()

if __name__ == "__main__":
    main()"""
    
import multiprocessing as mp

class Nuj:
    def __init__(self, x):
        self.x = x

def func(nuj: Nuj):
    print(f"adresa in cod: {nuj}")

def main():
    nuj = Nuj(3)
    print(f"adresa in main: {nuj}")
    func(nuj)

    proc = mp.Process(target = func, args = (nuj, ))
    proc.start()
    proc.join()
    
if __name__ == "__main__":
    main()