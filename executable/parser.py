from bs4 import BeautifulSoup as BS
from zipfile import ZipFile
from pathlib import Path
import pandas as pd
import numpy as np
from multiprocessing import Pool
from multiprocessing import cpu_count
from sys import stdout, argv
import lxml
from datetime import datetime

def _open_zip_file(path_to_file: Path) -> list[str]:
    pages_list = []
    with ZipFile(path_to_file, 'r') as zf:
        for item in zf.filelist:
            with zf.open(item.filename) as file:
                pages_list.append(file.read())
    return pages_list


def _get_products(cart: BS, category: str) -> pd.DataFrame:
    # Скидка если есть
    sale = cart.find('div', class_='lui-sku-product-card-preview').find('span', class_='lui-badge lui-badge_discount') # Нужно проверить на большом количестве
    try:
        sale = sale.text
    except AttributeError as ex:
        sale = np.nan
    
    # Название продукта
    name = cart.find('div', class_='lui-sku-product-card-text lui-sku-product-card-text--view-primary').get_text(strip=True)

    # Страна производитель
    made_in = cart.find('div', class_='lui-sku-product-card-text lui-sku-product-card-text--view-secondary').get_text(strip=True)

    # Цены
    try:
        price = cart.find('div', class_='lui-sku-product-card-price').find('div', class_='lui-priceText lui-priceText--view_regular').stripped_strings
    except AttributeError:
        try:
            price = cart.find('div', class_='lui-sku-product-card-price').find('div', class_='lui-priceText lui-priceText--view_primary').stripped_strings
        except AttributeError:
            price = np.nan
    try:
        price = float('.'.join(list(price)[:2]).replace('\xa0', ''))
    except TypeError as ex:
        price = np.nan
    
    try:
        price_on_cart = cart.find('div', class_='lui-sku-product-card-price').find('div', class_='lui-priceText lui-priceText--view_secondary').stripped_strings
    except AttributeError:
        try:
            price_on_cart = cart.find('div', class_='lui-sku-product-card-price').find('div', class_='lui-priceText lui-priceText--view_secondary lui-priceText--discont').stripped_strings
        except AttributeError:
            price_on_cart = np.nan
    try:     
        price_on_cart = float('.'.join(list(price_on_cart)[:2]).replace('\xa0', ''))
    except TypeError as ex:
        price_on_cart = np.nan

    
    df = pd.DataFrame([[category, name, made_in, sale, price, price_on_cart]], columns=['Категория', 'Название', 'Страна', 'Скидка', 'Цена', 'Цена по карте'])
    return df


def _worker(page: str) -> list[pd.DataFrame]:
    soup = BS(page, 'lxml')
    table = soup.find('div', class_='catalog-grid__grid catalog-grid')
    try:
        category = soup.find('div', class_='catalog-view__header').find('h1', class_='catalog-view__title').get_text(strip=True)
        carts = table.find_all('a', class_='lui-card lui-sku-product-card sku-card-small-container catalog-grid-sku-product-card')
    except AttributeError:
        return [pd.DataFrame()]
    products_list = []
    for cart in carts:
        products_list.append(_get_products(cart, category))
    return products_list



def run_parser(func, page_list: list[str]) -> pd.DataFrame:
    with Pool(cpu_count()//2) as pool:
        out_list_list = pool.map(func=func, iterable=page_list)
        out_list = sum(out_list_list, [])
        result = pd.concat(out_list, ignore_index=True, sort=False)
        return result

def _save_data_frame(results: pd.DataFrame):
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d_%H-%M')
    folder = Path('data')
    file = f'{formatted_date}-lenta.zip'
    path_to_file = folder.joinpath(file)
    compression_opts = dict(method='zip', archive_name=f'{formatted_date}-lenta.csv')
    results.to_csv(
        path_to_file, 
        index=False,
        compression=compression_opts
        )

def main():
    path_to_file = Path(argv[1])
    # path_to_file = Path(r'c:\works\work_002\data\2023-04-25_00-30-lenta.zip')
    page_list = _open_zip_file(path_to_file)
    result = run_parser(_worker, page_list)
    stdout.write(result.to_json())

if __name__ == '__main__':
    main()

