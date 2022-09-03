import aiohttp
import asyncio
import bs4
import time
import random
import datetime
import platform
from db.models import TelegramUsers
from db.models import engine
from aiogram import Bot
from config import API_TOKEN
from sqlalchemy.orm import Session


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}


async def sent_messages(message: str):
    bot = Bot(token=API_TOKEN)

    session = Session(engine)

    users = session.query(TelegramUsers).all()
    for user in users:
        if len(message) > 4096:
            for x in range(0, len(message), 4096):
                await bot.send_message(user.telegram_id, message[x:x + 4096], disable_web_page_preview=True)
        else:
            await bot.send_message(user.telegram_id, message, disable_web_page_preview=True)

    await bot.close()
    session.close()


def create_text_message_new_articles(articles: list) -> str:
    result = "--new articles--\ncount=" + str(len(articles)) + "\n"
    count = 1
    for article in articles:
        result = result + str(count) + ") "
        result = result + "title=" + article["title"]
        result = result + "\nlink=" + article["link"] + "\n"
        count = count + 1
    return result


def parse_page(page) -> list:
    soup = bs4._soup(page, "html.parser")
    list_result_articles = []
    main_article = soup.find("div", {"class": "article"})
    articles = soup.find_all("div", {"class": "article clearfix"})
    articles.append(main_article)
    for article in articles:
        a = article.find("h3", {"class": "sub_title"}).find("a")
        link = "https://www.tesmanian.com" + a.get("href")
        title = a.get_text()
        list_result_articles.append({"title": title, "link": link})
    return list_result_articles


def check_new_articles(current: list, previous: list) -> list:

    new_articles = []
    for current_article in current:
        find_title = False
        find_link = False
        for previous_article in previous:
            if current_article["title"] == previous_article["title"]:
                find_title = True
            if current_article["link"] == previous_article["link"]:
                find_link = True
            if find_link is True and find_title is True:
                break
        if find_link is True and find_title is True:
            continue
        if find_link is False and find_title is False:
            new_articles.append(current_article)

    return new_articles


def delete_duplicates(articles: list):
    for article1 in articles:
        number_of_matches = 0
        for article2 in articles:
            if article1["title"] == article2["title"] and article1["link"] == article2["link"]:
                number_of_matches = number_of_matches + 1
        if number_of_matches > 1:
            articles.remove(article1)


async def run():
    for _ in range(5):
        await main()
        time.sleep(300)


async def main():
    async with aiohttp.ClientSession() as session:
        previous_articles = []
        while True:
            async with session.get('https://www.tesmanian.com/', headers=headers) as response:
                if 599 >= response.status >= 500:
                    time.sleep(100)
                elif 499 >= response.status >= 400:
                    return 4

                print("--time=", datetime.datetime.now())
                print("status:", response.status)
                page = await response.text()
                current_articles = parse_page(page)
                new_articles = check_new_articles(current_articles, previous_articles)
                delete_duplicates(new_articles)
                if len(new_articles) != 0:
                    await sent_messages(create_text_message_new_articles(new_articles))
                    print(new_articles)
                else:
                    print("there are no new articles")
                previous_articles = current_articles
                time.sleep(random.randint(14, 16))


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
