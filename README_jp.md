# UoM オート チェクイン
> このプログラムはまだ中国語の出力のみをサポートしていることに注意してください、
> ご不便をかけて申し訳ありません

[中文版在这](README.md)

[Click Here for English Version](README_en.md)

## 何これ？
分かる人は分かる、わからない人は分かりません、誰でもに聞くな！

## 使い方は？
1. クロンして、pip依存関係プラグインをインストールしてください

```pip install -r requirements.txt```

2. ```config.json```のパラメーターを変更した後だけ```main.py```は実行できます
* 本機で実行の場合は、```webdriver```の後は```local```を変更してください、ぜひ対応するバージョンの
[ChromeDriver](https://chromedriver.chromium.org/downloads)
を使ってください
* リモートウェブドライバーを使用する場合は、```webdriver```の後てドライバーのアドレスを変更してください！
[Docker - browserless/chrome](https://registry.hub.docker.com/r/browserless/chrome) はおすすめします

リモートウェブドライバーを使用は強くおすすめします

このプログラムは時間差は自動的に認識され、自動的に調整されます、手動調整は必要ありません

その日のすべてのチェックインタスクを完了した場合は、スケジュールされたタスクは翌日の0:00に設定され、翌日も実行され続けます。

~~Japanese version translator: Tenjin~~