import os, re, json, datetime, pathlib, httpx
from itertools import cycle
import numpy as np
import matplotlib.pyplot as plt

root = pathlib.Path(__file__).parent.resolve()

TOKEN = os.environ.get("GH_TOKEN", "")
USE_PROXY = False

def gen_chart():
    if USE_PROXY:
        http_client = httpx.Client(proxies={
            'http': 'http://127.0.0.1:1080',
            'https': 'http://127.0.0.1:1080'
        })
    else:
        http_client = httpx.Client()

    percents = http_client.get('https://wakatime.com/share/@4d6204f0-5919-472a-8a52-3bf2a4c287e7/fc38b846-9952-4092-b215-1e9679710d20.json')
    times = http_client.get('https://wakatime.com/share/@4d6204f0-5919-472a-8a52-3bf2a4c287e7/958247f1-bb04-4e59-9db9-aa4af08eb4d5.json')

    lang_labels = []
    lang_percents = []
    for d in percents.json()['data']:
        lang_labels.append(d['name'])
        lang_percents.append(d['percent'])

    other_percent = sum(filter(lambda p: p < 5, lang_percents))
    lang_labels, lang_percents = map(list, zip(*filter(lambda t: t[1] >= 5, zip(lang_labels, lang_percents))))
    lang_labels.append('Other')
    lang_percents.append(other_percent)

    fallback_colors = cycle(["#ef476f","#ffd166","#06d6a0","#118ab2","#073b4c"])
    lang_colors = []
    with open('github_colors.json') as f:
        d = json.load(f)
        for lang in lang_labels:
            lang = lang.lower()
            if lang in d:
                lang_colors.append(d[lang])
            else:
                lang_colors.append(next(fallback_colors))

    total_time_s = 0
    for d in times.json()['data']:
        total_time_s += d['grand_total']['total_seconds']
    n_hour = int(total_time_s / 3600)
    n_minutes = int((total_time_s % 3600) / 60)
    dpi = 96
    px_height = 300
    px_width = 300
    plt.figure(figsize=(px_height/dpi, px_width/dpi), dpi=dpi)
    plt.pie(lang_percents, labels=lang_labels, colors=lang_colors, wedgeprops={'width': 0.382}, startangle=180, counterclock=False)
    plt.annotate(f'{n_hour} h {n_minutes} min', (0, 0), ha='center', va='center')
    plt.title('Coding Time This Week')
    plt.tight_layout()
    plt.savefig(root / 'asset/codingtime.svg')

if __name__ == "__main__":
    gen_chart()
