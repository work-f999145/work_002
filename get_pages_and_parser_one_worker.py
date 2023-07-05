from executable.config import drive_1, drive_2
from multiprocessing import Manager, Process
from executable.bearing_02 import  _get_links_queue, _worker_get_pages
from executable.parser import _worker, run_parser, _save_data_frame
from tqdm import tqdm

"""
    Главный парсер.
    Собирает информацию с сайта Lenta.com, выбирая перед этим необходимый город и магазин.
    После сбора информации, производит парсинг данных,
    В результате чего сохраняет всю информацию в виде pd.DataFrame в зип файл.
    
    webscrapping происходит через прокси сервера, по одному процессу на каждый сервер.
    В нем используется ссистема подгрузки страниц.
    
    Парсинг данных осуществляется в много процессорном режиме, 
    уже после сбора данных, для минизации задержек
"""

def get_pages_main() -> list[str]:
    """
        Запуск webscrapper.
        Он запускается по количеству прокси серверов.
        Результатом будет список из полных данных страниц.
    """
    
    the_queue = _get_links_queue()
    # Необходим, что бы остановить воркеры
    for _ in range(2):
        the_queue.put(None)
    
    # Список для возвращения данных
    manager = Manager()
    results = manager.list()
    p1 = Process(target=_worker_get_pages, args=(the_queue, drive_1, results, False))
    # p2 = Process(target=_worker_get_pages, args=(the_queue, drive_2, results))
    # Запуск процессов
    p1.start()
    # p2.start()
    # Ждем окончание процессов
    p1.join()
    # p2.join()
    p1.close()
    
    # final_results = sum(results, [])
    # _save_pages(final_results)
    return results

def get_DataFrame(pages_list:list[str]):
    """
        Запуск парсера данных.
        Парсер запускается в многопроцессорном режиме,
        что позволяет значительно снизить время обработки данных.
        Результаты в формате pd.DataFrame сохраняются в csv файл, помещенный в zip архив.
    """
    
    results = run_parser(_worker, pages_list)
    _save_data_frame(results)

if __name__ == '__main__':
    pages_list = get_pages_main()
    get_DataFrame(pages_list)