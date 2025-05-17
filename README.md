# Flaskを使用した産学連携バックエンドシステム

## 基本手順~API作成~
①project/views/DBテーブル名_views.pyを作成
②作成したファイルに、テーブルのcrudAPIを作成
```
user_bp = Blueprint('user', __name__)
# 名前はテーブル名_bpで、シングルクウォートの中はテーブル名
```
※ログインユーザーがテーブルのカラムに設定されている場合は、JWTを使用したアクセストークンで判定
参考資料(https://flask-jwt-extended.readthedocs.io/en/stable/)(https://qiita.com/kerobot/items/c5607658171c2aec4f46)
③project/views/__init__.pyに以下の内容を追加
```
# 作成したファイルをimport
from .user_views import user_bp


def register_blueprints(app):
# register_blueprint関数はAPIルート表示のやつ、中はBlueprintの定義名
    app.register_blueprint(user_bp)
```
以上で終わります。

最後に各ファイルの内容を簡単に
app.py...サーバー起動時に動くファイル
project/models.py...DBテーブル定義ファイル
project/config.py...DB接続情報ファイル
project/__init__.py...アプリケーション全体の設定ファイル
project/views/__init__.py...crudAPIルートの定義ファイル
project/views/テーブル名_views.py...crudAPIルート、内部処理作成ファイル。
requirements.txt...今回使用するライブラリ一覧のファイル
