import requests
from bs4 import BeautifulSoup
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction


class NpmjsExtension(Extension):

    def __init__(self):
        super(NpmjsExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument()
        maxSize = int(extension.preferences['max_search_result'])
        if not query:
            return

        PUPI = 'https://pypi.org'
        search_query = f"{PUPI}/search/?q={query}"

        r = requests.get(search_query)
        if r.status_code != 200:
            return

        data = r.text
        soup = BeautifulSoup(data, 'html.parser')
        links = soup.find_all('a', {"class": "package-snippet"})
        links = links[:maxSize]

        results = []
        for link in links:
            try:
                url = PUPI + link['href']
                name = link.find(
                    'span', {"class": "package-snippet__name"}).text
                version = link.find(
                    'span', {"class": "package-snippet__version"}).text
                description = link.find(
                    'p', {"class": "package-snippet__description"}).text
                results.append({"url": url,
                                "name": name,
                                "version": version,
                                "description": description}
                               )
            except Exception as e:
                continue

        items = []
        for result in results:
            items.append(ExtensionResultItem(icon='images/white-cube.png',
                                             name=result['name'],
                                             description=result['description'],
                                             on_enter=OpenUrlAction(
                                                 result['url'])
                                             )
                         )

        return RenderResultListAction(items)


if __name__ == '__main__':
    NpmjsExtension().run()
