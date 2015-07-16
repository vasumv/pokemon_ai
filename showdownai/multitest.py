from multiprocessing import Process
from showdown import main
import time

def run():
    p1 = Process(target=main)
    p1.start()
