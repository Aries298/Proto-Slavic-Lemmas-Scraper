from bs4 import BeautifulSoup
import time
import requests
import csv

PROTO_SLAVIC_LEMMAS_URL = '''https://en.wiktionary.org/wiki/Category:Proto-Slavic_lemmas'''
SITE_PREFIX = '''https://en.wiktionary.org/'''

# TIME TAKEN 1552 seconds

if __name__ == '__main__':
    next_page_exists = True
    start = time.time()
    r = requests.get(PROTO_SLAVIC_LEMMAS_URL)
    soup = BeautifulSoup(r.content, features="html.parser")

    with open('proto_slavic_lemmas.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Proto-Slavic Word', "Polish Word", "Old Polish Word"])

    while next_page_exists:
        entries = soup.find_all("a", href=lambda href: href and "Reconstruction:Proto-Slavic" in href)
        entries = [SITE_PREFIX + entry['href'] for entry in entries[20:]] # Ignoring the first 20 that are new pages and edits

        for entry in entries:
            subrequest = None
            while subrequest is None:
                try:
                    subrequest = requests.get(entry)
                except requests.exceptions.Timeout:
                    print(f'Exception ocurred while accessing {entry}')
                    time.sleep(2)

            subsoup = BeautifulSoup(subrequest.content, features="html.parser")
            title = subsoup.find("h1", {"class":"firstHeading mw-first-heading"}).span.text

            try:
                polish = subsoup.find('span', {"lang":"pl"}).text
            except AttributeError:
                polish = ""
            try:
                old_polish = subsoup.find('span', {"lang":"zlw-opl"}).text
            except AttributeError:
                old_polish = ""

            with open('proto_slavic_lemmas.csv', 'a', encoding='UTF8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow([title, polish, old_polish])

            print(f"Finished scraping word '{title}'")

        next_button = soup.find("a", text="next page")
        if not next_button: break
        next_page_url = SITE_PREFIX + next_button['href']

        r = None
        while r is None:
            try:
                r = requests.get(next_page_url)
            except requests.exceptions.Timeout:
                print(f'Exception ocurred while accessing {next_page_url}')
                time.sleep(2)
        soup = BeautifulSoup(r.content, features="html.parser")

    end = time.time()
    print(f'It took {end - start} second to execute script')