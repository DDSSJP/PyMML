# PyMML
MMLで記述された曲を演奏するプログラムです。  
主にFM音源を対象としています。

現在(2026/8/16)は`YMF825`のみ対応しています。

---------------------------------------------------------
## セットアップ
ソフトウェア
- Python 3.14.5以降 (https://www.python.org/)  
  ※追加ライブラリは不要
- FTDI D2XX Drivers (https://ftdichip.com/drivers/d2xx-drivers/)  
  インストールして`ftd2xx.dll`にパスが通った状態にしてください。  
  Virtual COM Port(VCP)ではないので注意してください。

YMF825Board
- ウダデンシ YMF825Board (http://uda.la/fm/)
- 販売：秋月電子 https://akizukidenshi.com/catalog/g/gM-12414/ (販売終了)
- 販売：スイッチサイエンス https://www.switch-science.com/products/3399 (販売終了)

FT232H
- 販売：Adafruit https://www.adafruit.com/product/2264
- 販売：秋月電子 https://akizukidenshi.com/catalog/g/gM-08942/
- 販売：秋月電子 https://akizukidenshi.com/catalog/g/gK-06503/  
  FT232Hが搭載されていればボードメーカーは問いません。

---------------------------------------------------------
## YMF825を接続する
PCからSPIを出力できるデバイス(FT232H)とYMF825ボードがSPIで接続してください。  
YMF825ボードの電源は5Vだけを使用する、かつ、  
SPIデバイスから出力される5V電源を使用する場合の接続方法です。  
ボード側のピンはメーカーによって名称が異なる可能性があります。

|pin|YMF825Board|Adafruit FT232H|
|-|-|-|
|電源|5V|5V|
|GND|GND|GND|
|CLOCK|SCK|D0|
|MOSI|MOSI|D1|
|MISO|MISO|D2|
|SS|SS|D3|
|RESET|RST_N|D4|

---------------------------------------------------------
## 使用できるデバイスの一覧を取得する
使用できるデバイスの一覧は`device.py`を実行すると取得され、  
`device_info_list.json`に保存されます。
```
python device.py
```

出力されるjsonファイルの例
```json
{
    "output datetime": "2025-12-23 12:34:56.123456",
    "device_info_list": [
        {
            "device": "FT232H",
            "id": "FTPVNW8R",
            "detail": {
              ....
            }
        }
    ]
}
```
StandardMMLであれば#Systemのデバイス種別に`"device"`の値を、デバイスIDに`"id"`の値を記述してください。  
`"detail"`はデバイスを特定するための詳細な情報です。選択の参考にしてください。
```
#System sys1 FT232H FTPVNW8R / YMF825
```

---------------------------------------------------------
## 曲を演奏する
```
python play.py filename
```
Pythonにパスを通して、このリポジトリのplay.pyを実行します。  
引数にMMLファイルのファイル名を指定してください。  
パスの区切り文字にはスラッシュ `/` を使用してください。

ファイル名の後ろに`high`をつけるとプロセスの優先度を通常よりも高く設定します。  
演奏がより安定するようになります。この機能はWindowsのみ対応です。
```
python play.py filename high
```

Ctrl+Cで停止すると発音を止めるコマンドを送信します。  
その他の方法で停止すると発音され続ける場合がありますので注意してください。

---------------------------------------------------------
## メモ
MMLを演奏させるまで手順はとても大変です。  
変態紳士向けとなっております。

開発の途中なので、仕様が大きく変わる可能性もあります。  

バグがあるかもしれません。  
見つけた場合はissuesにレポートしていただければ助かります。

デバイス、チップ、MML、コントローラーなどは追加しやすい構造になってます。  
追加したぞ！という方はプルリクください。

---------------------------------------------------------
## ライセンス

MITライセンスとします。
