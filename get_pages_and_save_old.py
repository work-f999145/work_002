from executable.config import drive_1, drive_2
from multiprocessing import Manager, Process
from executable.bearing_01 import  _get_links_queue, _save_pages, _worker_get_pages

"""
    Промежуточный вариант webscrapper.
    Он открывает каждую страницу категории,
    что часто вызывает блокировку со стороны сервера.
    И сохраняет все полученные страницы в формате *.html в zip архив.
"""

if __name__ == '__main__':
    
    the_queue = _get_links_queue()
    # Необходим, что бы остановить воркеры
    for _ in range(2):
        the_queue.put(None)
    
    # Список для возвращения данных
    manager = Manager()
    results = manager.list()
    
    p1 = Process(target=_worker_get_pages, args=(the_queue, drive_1, results))
    p2 = Process(target=_worker_get_pages, args=(the_queue, drive_2, results))
    # Запуск процессов
    p1.start()
    p2.start()
    # Ждем окончание процессов
    p1.join()
    p2.join()
    
    final_results = sum(results, [])
    _save_pages(final_results)