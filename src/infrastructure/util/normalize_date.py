import pandas as pd
from datetime import datetime

def normalize_date(obj):
    """
    obj の中に含まれる 'date' を datetime に統一する。
    dict / list / tuple / pandas.Timestamp / str に対応。
    """

    # 日付型そのものなら正規化して返す
    if isinstance(obj, datetime):
        return obj
    if isinstance(obj, pd.Timestamp):
        return obj.to_pydatetime()
    if isinstance(obj, str):
        try:
            # "datetime.datetime(...)" や "Timestamp(...)" も吸収
            return pd.to_datetime(obj).to_pydatetime()
        except Exception:
            return obj  # 日付でない純粋な文字列ならそのまま返す

    # dict の場合：キーが date の場合に正規化
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if "date" in k.lower():  # date, trade_date, triggerDate など全部検知
                new_obj[k] = normalize_date(v)
            else:
                new_obj[k] = normalize_date(v)
        return new_obj

    # list や tuple の場合：中身を再帰的に処理
    if isinstance(obj, (list, tuple)):
        return type(obj)(normalize_date(v) for v in obj)

    # それ以外（数値・Noneなど）はそのまま
    return obj
