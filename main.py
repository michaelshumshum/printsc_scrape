from requests import get
from random import choice
from bs4 import BeautifulSoup
from time import sleep
import threading
import queue

chars = [c for c in 'abdefghijklmnopqrstuvwxyz1234567890']
q = queue.Queue()
e = threading.Event()
e.set()


class Logger:

    class Severity:
        pass

    class Moderate(Severity):
        pass

    class Error(Severity):
        pass

    class Success(Severity):
        pass

    class Warn(Severity):
        pass

    @classmethod
    def log(cls, text, severity=Moderate):
        output = ''
        if not isinstance(severity(), cls.Severity):
            raise TypeError(f'must be Logger.Severity, not {severity.__name__}')
        if isinstance(severity(), cls.Moderate):
            output += '[INFO]'
        elif isinstance(severity(), cls.Error):
            output += '[31m[ERROR][0m'
        elif isinstance(severity(), cls.Success):
            output += '[32m[SUCCESS][0m'
        elif isinstance(severity(), cls.Warn):
            output += '[33m[WARN][0m'
        print(output + ' ' + text)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
}

with open('imgur_empty.png', 'rb') as f:
    imgur_empty = f.read()

invalid_src = b'<title>Attention Required! | Cloudflare</title>'


def save_image(q, e):
    while e.is_set():
        if not q.empty():
            name, bytes = q.get()
            if bytes == imgur_empty:
                Logger.log(text=f'Skipping {name} due to deleted imgur source', severity=Logger.Moderate)
                continue
            if invalid_src in bytes:
                Logger.log(text=f'Skipping "{name}" due to deletion', severity=Logger.Moderate)
                continue
            with open(f'images/{name}.png', 'wb+') as f:
                Logger.log(text=f'Saved "{name}"', severity=Logger.Success)
                f.write(bytes)


def get_image(q, e):
    while e.is_set():
        try:
            id = ''.join(choice(chars) for i in range(6))
            url = 'https://prnt.sc/' + id
            html = get(url, headers=headers).text
            element = BeautifulSoup(html, 'html.parser').find('img', {'class': 'no-click screenshot-image'})
            if element is None:
                Logger.log(text=f'Skipping "{id}" due to unknown reason', severity=Logger.Warn)
                sleep(1)
                continue
            src = element.get('src')
            if src[:2] == '//':
                continue
            q.put((id, get(src, headers=headers).content))
        except KeyboardInterrupt:
            break
        except Exception as e:
            Logger.log(text=e, severity=Logger.Error)
            raise KeyboardInterrupt
            e.clear()
            break


threads = [threading.Thread(target=save_image, args=(q, e,)),
           threading.Thread(target=get_image, args=(q, e,)),
           threading.Thread(target=get_image, args=(q, e,))]

for thread in threads:
    thread.start()
    Logger.log(text=f'Started {thread}', severity=Logger.Moderate)

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        e.clear()
        for thread in threads:
            thread.join()
            Logger.log(text=f'Stopped {thread}', severity=Logger.Moderate)
        Logger.log(text='Stopped', severity=Logger.Moderate)
        break
