# note, this uses threading. I don't think tornado likes that.
# basically, we need to re-do Queue around tornado's event loop.

from multiprocessing import Pool
def f(x):
    return x*x
import time
def slow(x):
    time.sleep(3)
    return x

if __name__ == '__main__':
    pool = Pool(processes=4)              # start 4 worker processes
    def cb(x): 
        print x
    for i in range(10):
        pool.apply_async(f, (i,), callback=cb)    # evaluate "f(10)" asynchronously

    time.sleep(3)
