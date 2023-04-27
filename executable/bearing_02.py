# Здесь находятся функции необходимые для загрузки страниц с сайта Lenta.com

import undetected_chromedriver as uc # type: ignore
import json, math
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException, \
                                        ElementNotSelectableException, NoSuchElementException, \
                                        ElementClickInterceptedException
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED
from executable.config import initial_driver
from time import sleep as time_sleep
from queue import Queue as one_queue
from multiprocessing import Queue as mp_queue
from random import randint



def _start_driver(initial:initial_driver) -> uc.Chrome:
    # Запуск Скрытного Браузера Chrome
    # Запускаем с опциями
    chrome_options = uc.ChromeOptions()
    
    # Запускаем через прокси сервер
    chrome_options.add_argument(f'--proxy-server={initial.proxy}')

    # Указываем местоположение на экране и размер экрана
    chrome_options.add_argument(f"--window-position={initial.browserLeft},{initial.browserTop}")
    chrome_options.add_argument(f"--window-size={initial.browserWidth},{initial.browserHeight}")

    # Запускаем сам ChromeDriver
    driver = uc.Chrome(options=chrome_options)

    # Запрашиваем стартувыю страницу
    driver.get(initial.start_url)
    # time_sleep(2)
    return driver

def select_sity(driver: uc.Chrome) -> bool:
    # Заставляем Браузер выбрать на сайте интерисующий нас магазин
    
    # Функция ожидания, позволяет Браузеру дождаться загрузки элементов
    wait = WebDriverWait(
        driver,
        timeout=10,
        poll_frequency=1,
        # ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException]
        )
    try:
    # Тут происходит список действий необходимый для выбора магазина
        try:
            element = wait.until(lambda d: d.find_element(by=By.CLASS_NAME, value='address-container__adress-icon-container'))
        except Exception as ex:
            print('!!!select_sity 52',ex)
        time_sleep(0.5)
        element.click()
        
        try:
            element = wait.until(lambda d: d.find_element(by=By.CLASS_NAME, value='store-picker-city__label'))
        except Exception as ex:
            print('!!!select_sity 58',ex)
        time_sleep(0.5)
        element.click()
        
        try:
            elements = wait.until(lambda d: d.find_elements(by=By.CSS_SELECTOR, value='span.cities-list-item__name'))
        except Exception as ex:
            print('!!!select_sity 64',ex)
        for el in elements:
            if 'Липецк' in el.text:
                el.click()
                break
        time_sleep(0.5)
        
        try:
            elements = wait.until(lambda d: d.find_elements(by=By.CSS_SELECTOR, value='span.button__inner'))
        except Exception as ex:
            print('!!!select_sity 72',ex)
        for el in elements:
            if 'Магазины' in el.text:
                el.click()
                break
        time_sleep(0.5)
        
        try:
            elements = wait.until(lambda d: d.find_element(by=By.CLASS_NAME, value='simplebar-content').find_elements(by=By.CLASS_NAME, value="stores-list-item__name"))
        except Exception as ex:
            print('!!!select_sity 81',ex)
        for el in elements:
            if 'ул. Катукова, д. 51' in el.text:
                el.click()
                break
        time_sleep(0.5)
        
        try:
            element = driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Выбрать магазин')]")
        except Exception as ex:
            print('!!!select_sity 90',ex)
        element.click()
    except ElementClickInterceptedException:
        time_sleep(2)
        return False
    else:
        wait.until(lambda d: 'Выбор магазина' not in d.page_source)
        return True



def _get_pagination(driver: uc.Chrome) -> int:
    """
        Получаем количество страниц на странице категории каталога
    """
    try:
        el = driver.find_element(by=By.CLASS_NAME, value='js-catalog-container')
    except Exception as ex:
        return 0
    catalog = json.loads(el.get_attribute('data-catalog-data'))
    pagination = math.ceil(catalog.get('skusCount')/catalog.get('limit'))
    return pagination



def _get_links_queue() -> mp_queue:
    """
        Загружаем из файла список линков на страницы с категориями и
        возвращаем очередь из этих категорий
    """
    
    with open('data/category_link_dict.json', 'r', encoding='utf-8') as file:
        link_dict = json.loads(file.read())

        link_queue: mp_queue[str] = mp_queue()
        for val in link_dict.values():
            link_queue.put(val)
    
    return link_queue



def _get_queue_cat(driver: uc.Chrome) -> one_queue[str] | None:
    """
        Получаем очередь с сылками на каждую страницу в категории каталога
    """
    
    page_url = driver.current_url
    pagination = _get_pagination(driver)
    if pagination is None:
        return None
    my_queue: one_queue[str] = one_queue()
    for key in range(1, pagination+1):
        my_queue.put(f'{page_url}?page={key}')
    return my_queue



def _save_pages(pages_list: list[str], name: str = 'lenta') -> None:
    """
        Сохранение загруженных страниц в файлы
        
        ~~ Вопрос: нужна ли здесь проверка на текущий каталог
    """
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d_%H-%M')
    with ZipFile(f'data/{formatted_date}-{name}.zip', 'w', compression=ZIP_DEFLATED, compresslevel=1) as zip_file:
        for index, page in enumerate(pages_list):
            zip_file.writestr(f'{index:05d}.html', page.encode())

def _get_pages(driver: uc.Chrome, cat_queue: one_queue, count: int, max_request: int = 40) \
    -> tuple[list, one_queue, int]:
    """
        Как это работает:
            Мы получаем очередь из адресов, и потом делаем запрос по каждому адресу.
            Мы прерываем цикл в том случае, если количество запросов превысило лимит и возвращаем список.
            Мы прирываем цикл, если получаем ошибку, и также возвращаем список.
            Когда очередь заканчивается, цикл прерывается и список возвращается
            
        Что мы возвращаем:
            список, для фиксации результата.
            очередь,
                если пуста, перейдем в другую категорию,
                если не пуста, возобновим работу в текущей категории.
            count, для контроля количества запросов в текущей сессии
    """
    
    out_list = []
    while not cat_queue.empty():
        url_cat = cat_queue.get(timeout=10)
        
        # Блок контроля количества запросов
        count +=1
        if count >= max_request:
            cat_queue.put(url_cat)
            count = 0
            return (out_list, cat_queue, count)
        
        # Производим запрос
        driver.get(url_cat)
        time_sleep(1)
        
        page_sourse = driver.page_source
        # При забросе получаем ошибку с сервера или блокирующий экран
        if 'Непредвиденная ошибка' in page_sourse:
            cat_queue.put(url_cat)
            return (out_list, cat_queue, count)
        
        if 'Bad gateway' in page_sourse:
            cat_queue.put(url_cat)
            return (out_list, cat_queue, count)
        
        
        # В случае если все хорошо, мы добавляем страницу и переходим к следующему адресу
        out_list.append(page_sourse)

    return (out_list, cat_queue, count)

def _download_more(driver: uc.Chrome) -> bool:
    """
        Заставляем сервер загрузить все товары на страницу.
        Рандомная задержка требуется, что бы загрузку товаров не заблокировали.
        Возможно подойдет и более короткая задержка.
    """
    
    fault_list = [
        'Не удалось получить товары, попробуйте обновить страницу и повторите попытку',
        'Непредвиденная ошибка',
        'Bad gateway'
    ]
    page_sourse = driver.page_source
    if any(fault in page_sourse for fault in fault_list):
        return False
    
    count = 0
    pagination = _get_pagination(driver)
    if not pagination:
        return False
    
    while True:
        if pagination > 1:
            try:
                element = driver.find_element(by=By.CLASS_NAME, value='catalog-grid__pagination')
            except NoSuchElementException:
                if not count:
                    time_sleep(1)
                    continue
                return True
            except ElementClickInterceptedException:
                return False
            else:
                element.click()
                count += 1
            time_sleep(randint(2,4))
        else:
            return True



def _worker_get_pages(in_Queue: mp_queue, in_driver: initial_driver, results: list) -> None:
    """
        Воркер, который работает через multiprocessing.Process
        Состоит из двух вложенных циклов.
        Первый цикл ищит по категориям, второй цикл загружает все товары на страницу
    """
    
    fault_list = [
        'Непредвиденная ошибка',
        'Bad gateway'
    ]
    
    premiere = True
    url = None
    
    
    while premiere:
        # Запуск экземпляра Google Chrome
        driver = _start_driver(in_driver)
        # Переход на интерисующий нас магазин
        if not select_sity(driver):
            driver.quit()
            continue
        
        while True:
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
            if any(fault in page_sourse for fault in fault_list):
                break
            
            # Запускаем подгрузку товаров, и 
            # в случае если все товары загрузились
            # добавляем страницу к результатам
            condition = _download_more(driver)
            
            if condition:
                results.append(driver.page_source)
                url = None
                break 
            else:
                break
  
        driver.quit()