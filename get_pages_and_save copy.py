from executable.config import list_initial_driver, initial_driver, drive_1, drive_2
from executable.bearing import  _start_driver, select_sity, \
                                _get_links_queue, _get_queue_cat, \
                                _save_pages, time_sleep
from multiprocessing import Manager, Process
from multiprocessing import Queue as mp_Queue





def _worker_get_pages(in_Queue: mp_Queue, in_driver: initial_driver, results: list) -> None:
    """
        Воркер, который работает через multiprocessing.Process
        Состоит из двух вложенных циклов.
        Первый цикл ищит по категориям, второй цикл ищит по страницам категорий
    """
    
    premiere = True
    url = None
    cat_continue = False
    
    while premiere:
        # Запуск экземпляра Google Chrome
        driver = _start_driver(in_driver)
        # Переход на интерисующий нас магазин
        select_sity(driver)
        
        count = 0
        
        while True:
            if not cat_continue:
                # Получение из очереди ссылки на страницу категории
                if url is None:
                    url = in_Queue.get(timeout=10)
                    if url is None:
                        premiere = False
                        print('X'*40)
                        print('очередь закончилась')
                        break
                
                driver.get(url)
                time_sleep(2)
                page_sourse = driver.page_source
                if 'Непредвиденная ошибка' in page_sourse:
                    break
                # Получение очереди ссылок на страницы в текущей категории
                cat_queue = _get_queue_cat(driver)
                
                out_list = []
                # Цикл по сбору страниц текущей категории
                while True:
                    url_cat = cat_queue.get(timeout=10)
                    driver.get(url_cat)
                    time_sleep(1)
                    page_sourse = driver.page_source
                    if 'Непредвиденная ошибка' in page_sourse:
                        break
                    count += 1
                    out_list.append(page_sourse)
                    # В однопоточном варианте очереди это условие работает
                    if cat_queue.empty():
                        results.append(out_list)
                        url = None
                        break
                # Все страницы пройдены или возникла непредвиденная ошибка
                if (url is not None) or (count >= 60):
                    time_sleep(3)
                    break
            else:
                pass
            
            
        driver.quit()


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