import requests
import os
from dotenv import load_dotenv
import time
from time import sleep
import sys
from datetime import datetime
import json

load_dotenv()


class YandexAPIClient:
    BASE_YANDEX_DISK_URL = 'https://cloud-api.yandex.net/v1/disk'

    def __init__(self, token_ya, folder):
        self.token_ya = token_ya
        self.folder = folder
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': 'OAuth ' + self.token_ya}
        self.params = {'path': self.folder}
        self.folder_url = '/resources'
        self.upload_url = '/resources/upload'

    def get_folder_yandex_disk(self):
        response = requests.get(self.BASE_YANDEX_DISK_URL + self.folder_url,
                                params=self.params, headers=self.headers)
        return response.status_code

    def put_folder_yandex_disk(self):
        response = requests.put(self.BASE_YANDEX_DISK_URL + self.folder_url,
                                params=self.params, headers=self.headers)
        if response.status_code == 409:
            return 'На Яндекс.Диске папка создана.'
        else:
            return 'Возникла ошибка с кодом: ', response.status_code

    def upload_file_yandex_disk(self, info_vk, operation_num):
        text = 'Запускаю программу по загрузке файлов на Яндекс.Диск.'
        print(f'{text:~^151}')
        sleep(3)
        print(f'Проверяем наличие папки {self.folder} на Яндекс.Диске.')
        if self.get_folder_yandex_disk() == 200:
            print('Папка уже имеется.')
            sleep(2)
        else:
            print('Папка не создана. Создаю.')
            sleep(2)
            self.put_folder_yandex_disk()
            print(f'Папка {self.folder} готова к эксплуатации.')
            sleep(2)
        print('Загружаем фотографии на диск.')
        sleep(2)
        photos_list = []
        toolbar_width = 40
        sys.stdout.write("Прогресс выполнения задачи: [%s]" % (" " *
                                                               toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width + 1))
        for key, value in info_vk.items():
            json_dict = {'file_name': key, 'size': value[1]}
            photos_list.append(json_dict)
            params = {'path': f'{self.folder}/{key}', 'url': value[0]}
            response = requests.post(self.BASE_YANDEX_DISK_URL +
                                     self.upload_url, params=params,
                                     headers=self.headers)
            time.sleep(0.01)
            sys.stdout.write(">>>")
            sys.stdout.flush()
        sys.stdout.write("]\n")
        sleep(1)
        with open('photos_info.json', 'w') as f:
            json.dump(photos_list, f)
        print(f'Загрузка завершена, {operation_num} фото было '
              f'сохранено на Яндекс.Диске.')


class VKAPIClient:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131',
            'extended': 'likes'
        }

    def _build_url(self, api_method):
        return f'{self.API_BASE_URL}/{api_method}'

    def get_profile_photos(self):
        print('Подключаюсь к профилю человека.')
        sleep(1)
        params = self.get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': 'profile'})
        response = requests.get(self._build_url('photos.get'), params=params)
        print('Начинаю загрузку сведений о фотографиях.')
        sleep(1)
        return response.json()

    def save_info_profile_photos(self):
        items = self.get_profile_photos()
        operation_num = 0
        toolbar_width = 20
        sys.stdout.write("Прогресс выполнения задачи: [%s]" % (" " *
                                                               toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width + 1))
        photo_dict = dict()
        for item in items['response']['items']:
            photo_likes = str(item['likes']['count'])
            for size in item['sizes']:
                photo_list = []
                if size['type'] == 'w':
                    photo_list.append(size['url'])
                    photo_list.extend(size['type'])
                    if f'{photo_likes}.jpg' in photo_dict:
                        date = item['date']
                        photo_likes += f'_{datetime.fromtimestamp(
                            date).strftime('%Y-%m-%d')}'
                    photo_dict[f'{photo_likes}.jpg'] = photo_list
                    operation_num += 1
                    time.sleep(0.1)
                    sys.stdout.write(">>>")
                    sys.stdout.flush()
        sys.stdout.write("]\n")
        print('Загрузка информации завершена.')
        sleep(2)
        return photo_dict, operation_num


if __name__ == '__main__':
    vk_client = VKAPIClient(os.getenv('TOKEN_VK'), os.getenv('VK_USER_ID'))
    information_vk, operation_num = vk_client.save_info_profile_photos()
    yandex_client = YandexAPIClient(os.getenv('TOKEN_YANDEX_DISK'),
                                    os.getenv('NEW_FOLDER'))
    yandex_client.upload_file_yandex_disk(information_vk, operation_num)
