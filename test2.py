import multiprocessing
import os
import time

NUM_PROCESSES = 2
NUM_QUEUE_ITEMS = 10  # so really 40, because hello and world are processed separately


def worker_main(queue: multiprocessing.Queue, results: list):
    print(os.getpid(),"working")
    while True:
        item = queue.get()#block=True) #block=True означает выполнение блокирующего вызова для ожидания элементов в очереди
        if item is None:
            break
        print(os.getpid(), "got", item)
        # time.sleep(1) # simulate a "long" operation
        results.append(item)
        queue.


# def main():
#     the_queue = multiprocessing.Queue()
    
#     for i in range(NUM_QUEUE_ITEMS):
#         the_queue.put("hello")
#         the_queue.put("world")
    
#     for i in range(NUM_PROCESSES):
#         the_queue.put(None)
    
#     results = []
    
#     the_pool = multiprocessing.Pool(NUM_PROCESSES, worker_main,(the_queue, results))

#     # запретите добавлять что-либо еще в очередь и дождитесь, пока очередь опустеет
#     the_queue.close()
#     the_queue.join_thread()

#     # запретите добавлять что-либо еще в пул процессов и дождитесь завершения всех процессов
#     the_pool.close()
#     the_pool.join()
    
#     print(results)


def main():
    the_queue = multiprocessing.Queue()
    
    for i in range(NUM_QUEUE_ITEMS):
        the_queue.put("hello")
        the_queue.put("world")
    
    for i in range(NUM_PROCESSES):
        the_queue.put(None)
    
    manager = multiprocessing.Manager()
    results = manager.list()
    
    p1 = multiprocessing.Process(target=worker_main, args=(the_queue, results))
    p2 = multiprocessing.Process(target=worker_main, args=(the_queue, results))

    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    
    print(results)

if __name__ == '__main__':
    main()