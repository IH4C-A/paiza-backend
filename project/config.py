# データベース設定
SECRET_KEY = 'Paiza_nuture'
# パスワードの '@' を '%40' にURLエンコード
SQLALCHEMY_DATABASE_URI = 'mysql://root:P%40ssw0rd@127.0.0.1/paiza_project'
SQLALCHEMY_TRACK_MODIFICATIONS = False