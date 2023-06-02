from typing import NamedTuple


class initial_driver(NamedTuple):
    browserWidth: int
    browserHeight: int
    browserLeft: int
    browserTop: int
    proxy: str
    start_url: str
    
drive_1 = initial_driver(1280, 1300, -2560, 0, '45.81.76.252:8000', 'https://lenta.com/catalog/')
drive_2 = initial_driver(1280, 1300, -1280, 0, '45.139.110.3:8000', 'https://lenta.com/catalog/')
drive_3 = initial_driver(1280, 1300, -2560, 0, '45.81.76.252:8000', 'https://lenta.com/catalog/')


list_initial_driver = [drive_1, drive_2]