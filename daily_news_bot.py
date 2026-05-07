import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

client = OpenAI(api_key=OPENAI_API_KEY)

def get_latest_news():
    url = "https://www.insidevina.com/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    articles = []
    for a in soup.select("h2 a")[:5]:
        title = a.text.strip()
        link = a["href"]
        articles.append((title, link))
    return articles

def get_article_text(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    paragraphs = soup.select("p")
    text = " ".join([p.text for p in paragraphs])
    return text[:3000]

def summarize(text):
    prompt = f"다음 뉴스 핵심을 한국어로 3줄 요약:\n{text}"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content

def send_mail(content):
    msg = MIMEText(content)
    msg["Subject"] = f"베트남 뉴스 Daily Brief - {datetime.today().date()}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

def run():
    news = get_latest_news()
    content = ""

    for title, link in news:
        article = get_article_text(link)
        summary = summarize(article)
        content += f"\n📰 {title}\n{summary}\n\n"

    send_mail(content)

run()
