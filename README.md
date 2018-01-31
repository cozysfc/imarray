# imarray

imarrayはnumpy.ndarrayを用いたオレオレデータ構造でnumpyの行列演算, 幾つかのPIL API, 画像の表示やファイルの入出力等を行ないます. 
このimarrayを用いて, DCT変換とそれを用いたJPEG変換のデモを実装しました. 

![](https://github.com/cozysfc/imarray/blob/master/images/Lenna_jpeg_example_domain_striped.jpg)

## 構成

デモはimarray.py, jpeg.pyの２つからなります.
* imarray.imarray: numpy.ndarrayをbaseとして画像処理を行いやすいようにデータ構造を実装,
                   numpyの行列演算, 幾つかのPIL API, ファイルの入出力機能等を持つ.

* jpeg.DCT       : 二次元の離散cosine変換を行う, 
                   Frequency Domainを出力するtoFreq,
                   Space Domainを出力するtoSpace関数を持つ.

* jpeg.JPEG      : 上記のimarray, DCTを用いて実装. 画像のFrequency Domainのうち
                   切り捨てる高周波数のレベルを指定して高周波数を消去し画像を出力する.


## デモプログラム

demo.pyにデモのプログラムを実装しています.

demo.pyでは, images/Lenna.jpgを読み込み,

* 各周波数切り捨てのレベル(level\_i, level\_j)により高周波を消去した画像を生成します.
* 高周波数のレベルは(level\_i=0\~8, level\_j=0~8)64段階あり、それら全ての画像を生成します.
* 生成した64の画像を一つに合わせて'images/Lenna-8x8.jpg'に出力します.
* 以下のような画像が生成されます(左上から右下に向かって圧縮率が低くなっていく).

![実行例](https://github.com/cozysfc/imarray/blob/master/images/Lenna_jpeg_example_8x8_concatenated.jpg)

## デモの実行まで

### セットアップ

pip install -r myjpeg/requirements.txt


### 実行

```
python demo.py
```


### 実行確認環境

* MacOS 10.12.3


## 参考

1. [好きなコトして何が悪い！](http://tony-mooori.blogspot.jp/2016/02/dctpythonpython.html)
2. [Wikipedia:JPEG](https://ja.wikipedia.org/wiki/JPEG)
3. [Wikipedia:離散コサイン変換](https://ja.wikipedia.org/wiki/%E9%9B%A2%E6%95%A3%E3%82%B3%E3%82%B5%E3%82%A4%E3%83%B3%E5%A4%89%E6%8F%9B)
4. [Two Dimensional Discrete Cosine Transform (DCT-II) in Python](http://www.answermysearches.com/two-dimensional-discrete-cosine-transform-dct-ii-in-python/350/)
