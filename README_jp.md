# UoM オート チェクイン
> このプログラムはまだ中国語だけの出力のみをサポートしていることにご注意してください、
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

このプログラムは時間差は自動的に認識され、自動的に調整されます、手動調整は必要ありません\
その日のすべてのチェックインタスクを完了した場合は、スケジュールされたタスクは翌日の6:00に設定され、翌日も実行され続けます。\
`--config_path xxx.json`を使って設定ファイルを変更できます
### 今は`--username=xxx --password=xxx...`という形でも設定できます、変量の名は`config.json`と同じです
## Dockerの使い方(x86_64とarm64V8はテストされています)
### 1.Docker Hubを使う場合(おすすめです)
* `docker pull sahuidhsu/uom_autocheckin`を执行してください（ARM64の方は`sahuidhsu/uom_autocheckin:arm64`を使ってください）
* `docker run -d --name=uom_checkin -e xxx=xxx -e xxx=xxx -e xxx=xxx... sahuidhsu/uom_autocheckin`を执行しってください（ARM64の方は最後に`:arm64`を追加してください）、こちの`xxx=xxx`は
config.jsonのフォマートと同じです，例えば `-e username=u11451hh -e password=123456 -e webdriver=http://example.com:1145/webdriver -e tgbot_token=xxx...`

### 2.自分でDockerfileを使う場合(別なアーキテクチャを使い場合、成功するかは不明です)
* このレポジトリをクロんして、 元目録で`docker build -t uom_checkin .`を执行しってください（最後の`.`は必要です）
* `docker run -d --name=uom_checkin -e xxx=xxx -e xxx=xxx -e xxx=xxx... uom_checkin`を执行しってください、こちの`xxx=xxx`は
config.jsonのフォマートと同じです，例えば `-e username=u11451hh -e password=123456 -e webdriver=http://example.com:1145/webdriver -e tgbot_token=xxx...`


### `docker logs uom_checkin`で実行中のコンテナのログを表示できます

日本語版のREADME翻訳者: [LTY_CK_TS](https://github.com/sahuidhsu)\
母語ではないのでもし何か違うたらごめんなさい