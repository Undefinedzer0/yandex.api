import os
import sys

import pygame as pg
import requests


class mapa:

    def __init__(self):
        self.x = 135
        self.y = 63
        self.spn = (3.0, 3.0)
        self.l = ['sat', 'map', 'skl']
        self.index = 0
        self.pt = ''
        self.params = {}
        self.set_params()
        self.address = ''

    def set_params(self):
        self.params = {
            'll': str(self.x) + ',' + str(self.y),
            'l': str(self.l[self.index % 3]),
            'spn': str(self.spn[0]) + ',' + str(self.spn[1]),
            'pt': self.pt
        }

    def request(self):
        search_api_server = 'http://static-maps.yandex.ru/1.x/'
        response = requests.get(search_api_server, params=self.params)
        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        return response

    def change_spn(self, x, y):
        if 0 <= x < 20 and 0 <= y < 20:
            self.spn = (x, y)
            self.set_params()
            return self.request()
        return 0

    def change_coord(self, way):
        if way == 0 and -170 < self.x < 170:
            self.x += self.spn[0]
        if way == 1 and -170 < self.x < 170:
            self.x -= self.spn[0]
        if way == 2 and -80 < self.y < 80:
            self.y -= self.spn[1]
        if way == 3 and -80 < self.y < 80:
            self.y += self.spn[1]
        self.set_params()
        return self.request()

    def change_type(self):
        self.index += 1
        self.set_params()
        return self.request()

    def find(self, text):
        global text_output, posting
        search_api_server = "http://geocode-maps.yandex.ru/1.x/"
        params = {
            'geocode': text,
            'format': 'json',
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b'
        }
        response = requests.get(search_api_server, params=params)
        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        json_response = response.json()
        try:
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            toponym_coodrinates = toponym["Point"]["pos"]
            text_output = toponym["metaDataProperty"]["GeocoderMetaData"]['Address']['formatted']
            try:
                post = toponym["metaDataProperty"]["GeocoderMetaData"]['Address']['postal_code']
                
                if posting:
                    text_output += " " + post
            except:    
                pass
            toponym_coodrinates = toponym_coodrinates.split()
            self.x = float(toponym_coodrinates[0])
            self.y = float(toponym_coodrinates[1])
            self.pt = f'{self.x},{self.y},pm2ntm'
        except:
            pass
        self.set_params()
        return self.request()

    def clear_all(self):
        global text_output
        self.pt = ''
        text_output = ''
        return self.request()

    def add_post(self):
        global posting
        posting = not posting
        return self.request()

map1 = mapa()

# Запишем полученное изображение в файл.
map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(map1.request().content)

# Инициализируем pygame
pg.init()
posting = False
screen = pg.display.set_mode((1400, 800))
# Рисуем картинку, загружаемую из только что созданного файла.
screen.blit(pg.image.load(map_file), (0, 0))
# Переключаем экран и ждем закрытия окна.
font = pg.font.Font(None, 32)
input_box = pg.Rect(200, 500, 140, 32)
color_active = pg.Color('dodgerblue2')
color_inactive = pg.Color('lightskyblue3')
color = color_inactive
active = False
text1 = ''
text = ''
text_output = ''
output_box = pg.Rect(200, 700, 340, 32)

running = True
while running:
    # внутри игрового цикла ещё один цикл
    # приема и обработки сообщений
    for event in pg.event.get():
        # при закрытии окна
        if event.type == pg.QUIT:
            running = False
        x = 0
        if event.type == pg.KEYDOWN:
            if event.key == 1073741902:
                x = map1.change_spn(map1.spn[0] / 1.2, map1.spn[1] / 1.2)
            if event.key == 1073741899:
                x = map1.change_spn(map1.spn[0] * 1.2, map1.spn[1] * 1.2)
            if event.key - 1073741903 in [0, 1, 2, 3]:
                x = map1.change_coord(event.key - 1073741903)
            if event.key == 116:
                x = map1.change_type()
            if event.key == 127:  # Del
                x = map1.clear_all()
            if event.key == 112:
                x = map1.add_post()
                map1.find(text1)
            if active:
                if event.key == 13:
                    x = map1.find(text)
                    text1 = text
                    text = ''
                elif event.key == 8:
                    text = text[:-1]
                else:
                    text += event.unicode
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if input_box.collidepoint(event.pos):
                # Toggle the active variable.
                active = not active
            else:
                active = False
            # Change the current color of the input box.
            color = color_active if active else color_inactive
        if x == 0:
            pass
        else:
            with open(map_file, "wb") as file:
                try:
                    file.write(x.content)
                except:
                    pass
        screen.fill((0, 0, 0))
        try:
            screen.blit(pg.image.load(map_file), (0, 0))
        except:
            pass
        # обновление экрана
        txt_surface = font.render(text, True, color)
        txt_surface2 = font.render(text_output, True, color_inactive)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width() + 10)
        width2 = max(800, txt_surface2.get_width() + 100)
        input_box.w = width
        output_box.w = width2
        # Blit the text.
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        screen.blit(txt_surface2, (output_box.x + 5, output_box.y + 5))
        # Blit the input_box rect.
        pg.draw.rect(screen, color, input_box, 2)
        pg.draw.rect(screen, color_inactive, output_box, 2)
        pg.display.flip()
pg.quit()

# Удаляем за собой файл с изображением.
os.remove(map_file)
