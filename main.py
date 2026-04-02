#@title HK Quant Master V10.10 (Ultimate: Dividend Bug Fixed & AI Prompt)
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import json
import warnings
import time
import math
import os
import urllib.parse
from tqdm import tqdm

warnings.filterwarnings('ignore')

# ==============================================================================
# 0. Futu API 初始化與防呆偵測
# ==============================================================================
FUTU_CTX = None
try:
    from futu import OpenQuoteContext, RET_OK, KLType, AuType
    FUTU_CTX = OpenQuoteContext(host='127.0.0.1', port=11111)
    print("✅ 成功連接 Futu OpenD (127.0.0.1:11111)，將優先使用富途獲取績效與股息。")
except Exception as e:
    FUTU_CTX = None
    print("⚠️ 未偵測到 Futu OpenD 運行 (或未安裝 futu-api)。系統自動切換為 Yahoo Finance 備用數據源。")

# ==============================================================================
# 1. 基礎設定與資料獲取
# ==============================================================================
START_DATE = "2000-01-01"
END_DATE = datetime.datetime.now().strftime('%Y-%m-%d')
UPDATE_TIME = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

WATCHLIST = [
    '0001.HK', '0002.HK', '0003.HK', '0005.HK', '0006.HK', '0011.HK', '0012.HK', '0016.HK', '0017.HK', '0020.HK',
    '0027.HK', '0066.HK', '0083.HK', '0101.HK', '0119.HK', '0135.HK', '0144.HK', '0151.HK', '0168.HK', '0175.HK',
    '0200.HK', '0241.HK', '0256.HK', '0267.HK', '0268.HK', '0270.HK', '0272.HK', '0285.HK', '0288.HK', '0291.HK',
    '0316.HK', '0322.HK', '0336.HK', '0345.HK', '0354.HK', '0358.HK', '0386.HK', '0388.HK', '0390.HK', '0460.HK',
    '0520.HK', '0522.HK', '0552.HK', '0576.HK', '0586.HK', '0598.HK', '0604.HK', '0656.HK', '0669.HK', '0688.HK',
    '0700.HK', '0728.HK', '0753.HK', '0762.HK', '0772.HK', '0778.HK', '0780.HK', '0813.HK', '0823.HK', '0836.HK',
    '0853.HK', '0857.HK', '0861.HK', '0868.HK', '0883.HK', '0902.HK', '0909.HK', '0914.HK', '0916.HK', '0934.HK',
    '0939.HK', '0941.HK', '0960.HK', '0968.HK', '0981.HK', '0992.HK', '0998.HK', '1024.HK', '1030.HK', '1038.HK',
    '1044.HK', '1055.HK', '1066.HK', '1071.HK', '1088.HK', '1093.HK', '1099.HK', '1109.HK', '1113.HK', '1119.HK',
    '1138.HK', '1157.HK', '1177.HK', '1193.HK', '1209.HK', '1211.HK', '1258.HK', '1299.HK', '1308.HK', '1313.HK',
    '1316.HK', '1336.HK', '1339.HK', '1347.HK', '1368.HK', '1378.HK', '1398.HK', '1516.HK', '1530.HK', '1658.HK',
    '1772.HK', '1787.HK', '1801.HK', '1810.HK', '1818.HK', '1833.HK', '1876.HK', '1898.HK', '1919.HK', '1928.HK',
    '1929.HK', '1997.HK', '2005.HK', '2007.HK', '2013.HK', '2015.HK', '2018.HK', '2020.HK', '2186.HK', '2192.HK',
    '2202.HK', '2238.HK', '2269.HK', '2313.HK', '2318.HK', '2319.HK', '2331.HK', '2333.HK', '2359.HK', '2380.HK',
    '2388.HK', '2600.HK', '2618.HK', '2628.HK', '2669.HK', '2688.HK', '2689.HK', '2727.HK', '2858.HK', '2866.HK',
    '2869.HK', '2877.HK', '2883.HK', '2899.HK', '3311.HK', '3319.HK', '3323.HK', '3328.HK', '3331.HK', '3606.HK',
    '3618.HK', '3633.HK', '3690.HK', '3692.HK', '3738.HK', '3800.HK', '3868.HK', '3888.HK', '3899.HK', '3900.HK',
    '3908.HK', '3933.HK', '3958.HK', '3968.HK', '3983.HK', '3988.HK', '3990.HK', '3993.HK', '6030.HK', '6098.HK',
    '6110.HK', '6160.HK', '6618.HK', '6690.HK', '6806.HK', '6837.HK', '6862.HK', '6865.HK', '6881.HK', '6969.HK',
    '9618.HK', '9633.HK', '9866.HK', '9868.HK', '9888.HK', '9922.HK', '9959.HK', '9988.HK', '9992.HK', '9999.HK'
]
WATCHLIST = list(set(WATCHLIST))

HK_STOCK_NAMES = {
    '0001.HK': '長和', '0002.HK': '中電控股', '0003.HK': '香港中華煤氣', '0005.HK': '匯豐控股', '0006.HK': '電能實業',
    '0011.HK': '恒生銀行', '0012.HK': '恆基地產', '0016.HK': '新鴻基地產', '0017.HK': '新世界發展', '0020.HK': '會德豐',
    '0027.HK': '銀河娛樂', '0066.HK': '港鐵公司', '0083.HK': '信和置業', '0101.HK': '恒隆地產', '0119.HK': '保利置業',
    '0135.HK': '昆侖能源', '0144.HK': '招商局港口', '0151.HK': '中國旺旺', '0168.HK': '青島啤酒', '0175.HK': '吉利汽車',
    '0200.HK': '新濠國際', '0241.HK': '阿里健康', '0256.HK': '冠和', '0267.HK': '中信股份', '0268.HK': '金蝶國際',
    '0270.HK': '粵海投資', '0272.HK': '瑞安房地產', '0285.HK': '比亞迪電子', '0288.HK': '萬洲國際', '0291.HK': '華潤啤酒',
    '0316.HK': '東方海外實業', '0322.HK': '康師傅控股', '0336.HK': '華寶國際', '0345.HK': '維他奶', '0354.HK': '中國軟件國際',
    '0358.HK': '江西銅業', '0386.HK': '中國石化', '0388.HK': '香港交易所', '0390.HK': '中國中鐵', '0460.HK': '四環醫藥',
    '0520.HK': '呷哺呷哺', '0522.HK': 'ASM太平洋', '0552.HK': '中國通信服務', '0576.HK': '浙江滬杭甬', '0586.HK': '海螺環保',
    '0598.HK': '中國外運', '0604.HK': '深圳控股', '0656.HK': '復星國際', '0669.HK': '創科實業', '0688.HK': '中國海外發展',
    '0700.HK': '騰訊控股', '0728.HK': '中國電信', '0753.HK': '中國國航', '0762.HK': '中國聯通', '0772.HK': '閱文集團',
    '0778.HK': '置富產業信託', '0780.HK': '同程旅行', '0813.HK': '世茂集團', '0823.HK': '領展房產基金', '0836.HK': '華潤電力',
    '0853.HK': '微創醫療', '0857.HK': '中國石油股份', '0861.HK': '神州控股', '0868.HK': '信義玻璃', '0883.HK': '中國海洋石油',
    '0902.HK': '華能國際', '0909.HK': '明源雲', '0914.HK': '海螺水泥', '0916.HK': '龍源電力', '0934.HK': '中石化冠德',
    '0939.HK': '建設銀行', '0941.HK': '中國移動', '0960.HK': '龍湖集團', '0968.HK': '信義光能', '0981.HK': '中芯國際',
    '0992.HK': '聯想集團', '0998.HK': '中信銀行', '1024.HK': '快手-W', '1030.HK': '新城發展', '1038.HK': '長江基建集團',
    '1044.HK': '恆安國際', '1055.HK': '中國南方航空', '1066.HK': '威高股份', '1071.HK': '華電國際', '1088.HK': '中國神華',
    '1093.HK': '石藥集團', '1099.HK': '國藥控股', '1109.HK': '華潤置地', '1113.HK': '長實集團', '1119.HK': '創夢天地',
    '1138.HK': '中遠海能', '1157.HK': '中聯重科', '1177.HK': '中國生物製藥', '1193.HK': '華潤燃氣', '1209.HK': '華潤萬象生活',
    '1211.HK': '比亞迪股份', '1258.HK': '中國有色礦業', '1299.HK': '友邦保險', '1308.HK': '海豐國際', '1313.HK': '華潤水泥',
    '1316.HK': '耐世特', '1336.HK': '新華保險', '1339.HK': '中國人民保險', '1347.HK': '華虹半導體', '1368.HK': '特步國際',
    '1378.HK': '中國宏橋', '1398.HK': '工商銀行', '1516.HK': '融創服務', '1530.HK': '新城悅服務', '1658.HK': '郵儲銀行',
    '1772.HK': '贛鋒鋰業', '1787.HK': '山東黃金', '1801.HK': '信達生物', '1810.HK': '小米集團-W', '1818.HK': '招金礦業',
    '1833.HK': '平安好醫生', '1876.HK': '百威亞太', '1898.HK': '中煤能源', '1919.HK': '中遠海控', '1928.HK': '金沙中國',
    '1929.HK': '周大福', '1997.HK': '九龍倉置業', '2005.HK': '理文造紙', '2007.HK': '碧桂園', '2013.HK': '微盟集團',
    '2015.HK': '理想汽車-W', '2018.HK': '瑞聲科技', '2020.HK': '安踏體育', '2186.HK': '綠葉製藥', '2192.HK': '醫渡科技',
    '2202.HK': '萬科企業', '2238.HK': '廣汽集團', '2269.HK': '藥明生物', '2313.HK': '申洲國際', '2318.HK': '中國平安',
    '2319.HK': '蒙牛乳業', '2331.HK': '李寧', '2333.HK': '長城汽車', '2359.HK': '藥明康德', '2380.HK': '中國電力',
    '2382.HK': '舜宇光學科技', '2388.HK': '中銀香港', '2600.HK': '中國鋁業', '2618.HK': '京東物流', '2628.HK': '中國人壽',
    '2669.HK': '中海物業', '2688.HK': '新奧能源', '2689.HK': '玖龍紙業', '2727.HK': '上海電氣', '2858.HK': '易鑫集團',
    '2866.HK': '中遠海發', '2869.HK': '綠城服務', '2877.HK': '神威藥業', '2883.HK': '中海油田服務', '2899.HK': '紫金礦業',
    '3311.HK': '中國建築國際', '3319.HK': '雅生活服務', '3323.HK': '中國建材', '3328.HK': '交通銀行', '3331.HK': '維達國際',
    '3606.HK': '福耀玻璃', '3618.HK': '重慶農商行', '3633.HK': '中裕燃氣', '3690.HK': '美團-W', '3692.HK': '翰森製藥',
    '3738.HK': '阜博集團', '3800.HK': '協鑫科技', '3868.HK': '信義能源', '3888.HK': '金山軟件', '3899.HK': '中集安瑞科',
    '3900.HK': '綠城中國', '3908.HK': '中金公司', '3933.HK': '聯邦制药', '3958.HK': '東方證券', '3968.HK': '招商銀行',
    '3983.HK': '中海石油化學', '3988.HK': '中國銀行', '3990.HK': '美的集團', '3993.HK': '洛陽鉬業', '6030.HK': '中信証券',
    '6098.HK': '碧桂園服務', '6110.HK': '滔搏', '6160.HK': '百濟神州', '6618.HK': '京東健康', '6690.HK': '海爾智家',
    '6806.HK': '申萬宏源', '6837.HK': '海通證券', '6862.HK': '海底撈', '6865.HK': '福萊特玻璃', '6881.HK': '中國銀河',
    '6969.HK': '思摩爾國際', '9618.HK': '京東集團-SW', '9633.HK': '農夫山泉', '9866.HK': '蔚來-SW', '9868.HK': '小鵬汽車-W',
    '9888.HK': '百度集團-SW', '9922.HK': '九毛九', '9959.HK': '星盛商業', '9988.HK': '阿里巴巴-SW', '9992.HK': '泡泡瑪特',
    '9999.HK': '網易-S'
}

HK_LOT_SIZES = {
    '0001.HK': 500, '0002.HK': 500, '0003.HK': 1000, '0005.HK': 400, '0006.HK': 500,
    '0011.HK': 100, '0012.HK': 1000, '0016.HK': 1000, '0017.HK': 1000, '0020.HK': 1000,
    '0027.HK': 1000, '0066.HK': 500, '0083.HK': 1000, '0101.HK': 1000, '0119.HK': 1000,
    '0135.HK': 1000, '0144.HK': 2000, '0151.HK': 2000, '0168.HK': 100, '0175.HK': 2000,
    '0200.HK': 1000, '0241.HK': 1000, '0256.HK': 2000, '0267.HK': 500, '0268.HK': 2000,
    '0270.HK': 2000, '0272.HK': 2000, '0285.HK': 500, '0288.HK': 2000, '0291.HK': 400,
    '0316.HK': 500, '0322.HK': 500, '0336.HK': 1000, '0345.HK': 1000, '0354.HK': 2000,
    '0358.HK': 1000, '0386.HK': 2000, '0388.HK': 100, '0390.HK': 2000, '0460.HK': 2000,
    '0520.HK': 1000, '0522.HK': 100, '0552.HK': 2000, '0576.HK': 2000, '0586.HK': 2000,
    '0598.HK': 2000, '0604.HK': 2000, '0656.HK': 500, '0669.HK': 500, '0688.HK': 2000,
    '0700.HK': 100, '0728.HK': 2000, '0753.HK': 1000, '0762.HK': 2000, '0772.HK': 200,
    '0778.HK': 1000, '0780.HK': 400, '0813.HK': 1000, '0823.HK': 500, '0836.HK': 1000,
    '0853.HK': 500, '0857.HK': 2000, '0861.HK': 500, '0868.HK': 2000, '0883.HK': 1000,
    '0902.HK': 2000, '0909.HK': 400, '0914.HK': 500, '0916.HK': 1000, '0934.HK': 2000,
    '0939.HK': 1000, '0941.HK': 500, '0960.HK': 500, '0968.HK': 2000, '0981.HK': 500,
    '0992.HK': 2000, '0998.HK': 1000, '1024.HK': 100, '1030.HK': 1000, '1038.HK': 500,
    '1044.HK': 500, '1055.HK': 1000, '1066.HK': 2000, '1071.HK': 2000, '1088.HK': 500,
    '1093.HK': 1000, '1099.HK': 200, '1109.HK': 2000, '1113.HK': 500, '1119.HK': 1000,
    '1138.HK': 2000, '1157.HK': 500, '1177.HK': 2000, '1193.HK': 500, '1209.HK': 400,
    '1211.HK': 500, '1258.HK': 2000, '1299.HK': 200, '1308.HK': 500, '1313.HK': 2000,
    '1316.HK': 2000, '1336.HK': 1000, '1339.HK': 2000, '1347.HK': 500, '1368.HK': 1000,
    '1378.HK': 1000, '1398.HK': 1000, '1516.HK': 1000, '1530.HK': 1000, '1658.HK': 500,
    '1772.HK': 500, '1787.HK': 500, '1801.HK': 200, '1810.HK': 200, '1818.HK': 1000,
    '1833.HK': 500, '1876.HK': 100, '1898.HK': 1000, '1919.HK': 500, '1928.HK': 400,
    '1929.HK': 200, '1997.HK': 1000, '2005.HK': 1000, '2007.HK': 2000, '2013.HK': 400,
    '2015.HK': 100, '2018.HK': 500, '2020.HK': 200, '2186.HK': 1000, '2192.HK': 200,
    '2202.HK': 500, '2238.HK': 500, '2269.HK': 500, '2313.HK': 200, '2318.HK': 500,
    '2319.HK': 1000, '2331.HK': 500, '2333.HK': 500, '2359.HK': 100, '2380.HK': 2000,
    '2382.HK': 100, '2388.HK': 500, '2600.HK': 2000, '2618.HK': 200, '2628.HK': 1000,
    '2669.HK': 1000, '2688.HK': 100, '2689.HK': 1000, '2727.HK': 2000, '2858.HK': 1000,
    '2866.HK': 2000, '2869.HK': 2000, '2877.HK': 1000, '2883.HK': 1000, '2899.HK': 500,
    '3311.HK': 1000, '3319.HK': 500, '3323.HK': 2000, '3328.HK': 1000, '3331.HK': 2000,
    '3606.HK': 200, '3618.HK': 2000, '3633.HK': 1000, '3690.HK': 100, '3692.HK': 200,
    '3738.HK': 500, '3800.HK': 5000, '3868.HK': 2000, '3888.HK': 100, '3899.HK': 1000,
    '3900.HK': 500, '3908.HK': 500, '3933.HK': 2000, '3958.HK': 500, '3968.HK': 500,
    '3983.HK': 2000, '3988.HK': 1000, '3990.HK': 100, '3993.HK': 2000, '6030.HK': 500,
    '6098.HK': 500, '6110.HK': 1000, '6160.HK': 100, '6618.HK': 100, '6690.HK': 200,
    '6806.HK': 500, '6837.HK': 500, '6862.HK': 500, '6865.HK': 200, '6881.HK': 1000,
    '6969.HK': 500, '9618.HK': 50, '9633.HK': 200, '9866.HK': 10, '9868.HK': 200,
    '9888.HK': 100, '9922.HK': 1000, '9959.HK': 1000, '9988.HK': 100, '9992.HK': 200,
    '9999.HK': 100
}

print(f"⏳ 1/5 啟動下載 Agent 獲取市場大數據 (從 2000 年至今)...")

hsi_df = yf.download(["2800.HK", "^HSI", "^VIX"], start=START_DATE, end=END_DATE, progress=False, threads=True)
hsi_c = hsi_df['Close']['2800.HK'].ffill()
if hsi_c.isna().all(): hsi_c = hsi_df['Close']['^HSI'].ffill()

hsi_v = hsi_df['Volume']['2800.HK'].ffill()
if hsi_v.isna().all(): hsi_v = hsi_df['Volume']['^HSI'].ffill()

vix_c = hsi_df['Close']['^VIX'].ffill()

def secured_download_agent(tickers, period_start, period_end):
    prices_dict = {'Open': {}, 'High': {}, 'Low': {}, 'Close': {}}
    for i in range(0, len(tickers), 30):
        batch = tickers[i:i + 30]
        data = yf.download(batch, start=period_start, end=period_end, progress=False, threads=True, group_by='ticker')
        for ticker in batch:
            try:
                df_t = data if len(batch) == 1 else data[ticker]
                if not df_t.empty and not df_t.isna().all().all():
                    prices_dict['Open'][ticker] = df_t['Open']
                    prices_dict['High'][ticker] = df_t['High']
                    prices_dict['Low'][ticker] = df_t['Low']
                    prices_dict['Close'][ticker] = df_t['Close']
            except Exception: pass
        time.sleep(0.5)
    return (pd.DataFrame(prices_dict['Open']).ffill(),
            pd.DataFrame(prices_dict['High']).ffill(),
            pd.DataFrame(prices_dict['Low']).ffill(),
            pd.DataFrame(prices_dict['Close']).ffill())

opens, highs, lows, closes = secured_download_agent(WATCHLIST, START_DATE, END_DATE)

valid_idx = closes.index.drop_duplicates(keep='first').sort_values()
opens = opens.reindex(valid_idx)
highs = highs.reindex(valid_idx)
lows = lows.reindex(valid_idx)
closes = closes.reindex(valid_idx)

hsi_c = hsi_c.reindex(closes.index).ffill()
hsi_v = hsi_v.reindex(closes.index).ffill()
vix_c = vix_c.reindex(closes.index).ffill()

print("⏳ 2/5 計算技術指標、BOLL布林通道與大盤嚴格版 FTD...")

hsi_200ma = hsi_c.rolling(200).mean()
sma20_all = closes.rolling(20).mean()
std20_all = closes.rolling(20).std()
upper_bb_all = sma20_all + (2 * std20_all)
lower_bb_all = sma20_all - (2 * std20_all)
donchian_high_all = highs.rolling(20).max().shift(1)

ret_120d = closes.pct_change(120)

rsi_period = 28
delta = closes.diff()
gain = delta.where(delta > 0, 0).ewm(alpha=1/rsi_period, adjust=False).mean()
loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/rsi_period, adjust=False).mean()
rs = gain / loss.replace(0, np.nan)
rsi_all = 100 - (100 / (1 + rs))

# ==============================================================================
# [V10.10 更新] 基本面抓取防呆 (修復 Yahoo Finance 股息率小數點錯誤)
# ==============================================================================
fin_cache = {}
def get_fundamentals(ticker):
    if ticker in fin_cache: return fin_cache[ticker]

    # Futu API 優先
    if FUTU_CTX is not None:
        try:
            futu_tk = f"HK.{ticker.split('.')[0]}"
            ret_snap, snap_data = FUTU_CTX.get_market_snapshot([futu_tk])
            div, pe, pb = "N/A", "N/A", "N/A"
            if ret_snap == RET_OK and not snap_data.empty:
                raw_div = snap_data['dividend_yield'].iloc[0]
                if pd.notna(raw_div) and raw_div > 0:
                    div = round(raw_div, 2)
                    if div > 40: div = "異常"  # 防呆機制
                
                pe_val = snap_data['pe_rate'].iloc[0]
                if pd.notna(pe_val): pe = round(pe_val, 2)
                
                pb_val = snap_data['pb_rate'].iloc[0]
                if pd.notna(pb_val): pb = round(pb_val, 2)
            
            start_str = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
            ret_kline, k_data, _ = FUTU_CTX.request_history_kline(futu_tk, start=start_str, end=END_DATE, ktype=KLType.K_DAY, autype=AuType.QFQ)
            earn_pct = 0
            if ret_kline == RET_OK and not k_data.empty:
                first_c = k_data['close'].iloc[0]
                last_c = k_data['close'].iloc[-1]
                earn_pct = round(((last_c - first_c) / first_c) * 100, 2)

            if earn_pct >= 15: earn_label = f"強勁 (+{earn_pct}%)"
            elif earn_pct > 0: earn_label = f"復甦 (+{earn_pct}%)"
            elif earn_pct < 0: earn_label = f"衰退 ({earn_pct}%)"
            else: earn_label = "無"

            div_str = f"{div}%" if isinstance(div, (int, float)) else div
            fin_cache[ticker] = {"div": div_str, "earn_label": earn_label, "pe": pe, "pb": pb, "roe": "N/A"}
            return fin_cache[ticker]
        except Exception:
            pass

    # Yahoo Finance 備用機制 (安全計算股息率)
    try:
        tk_info = yf.Ticker(ticker).info
        
        # 使用絕對派息金額 / 現價，避免 YF 的 percentage 錯置 Bug
        div_rate = tk_info.get('dividendRate') or tk_info.get('trailingAnnualDividendRate')
        c_price = tk_info.get('currentPrice') or tk_info.get('previousClose')
        
        if div_rate and c_price and c_price > 0:
            div = round((div_rate / c_price) * 100, 2)
        else:
            raw_div = tk_info.get('dividendYield') or 0
            div = round(raw_div, 2) if raw_div > 1 else round(raw_div * 100, 2)
            
        if div > 40:
            div_str = "異常"
        else:
            div_str = f"{div}%"
            
        earn_growth = tk_info.get('earningsGrowth') or tk_info.get('revenueGrowth') or 0
        earn_pct = round(earn_growth * 100, 2)

        if earn_pct >= 15: earn_label = f"強勁 (+{earn_pct}%)"
        elif earn_pct > 0: earn_label = f"復甦 (+{earn_pct}%)"
        elif earn_pct < 0: earn_label = f"衰退 ({earn_pct}%)"
        else: earn_label = "無"

        pe = round(tk_info.get('trailingPE'), 2) if tk_info.get('trailingPE') else "N/A"
        pb = round(tk_info.get('priceToBook'), 2) if tk_info.get('priceToBook') else "N/A"
        
        raw_roe = tk_info.get('returnOnEquity')
        roe = f"{round(raw_roe * 100, 2)}%" if raw_roe else "N/A"

        fin_cache[ticker] = {"div": div_str, "earn_label": earn_label, "pe": pe, "pb": pb, "roe": roe}
    except:
        fin_cache[ticker] = {"div": "N/A", "earn_label": "無", "pe": "N/A", "pb": "N/A", "roe": "N/A"}
    return fin_cache[ticker]


# --- 寬鬆版 RSI (< 30) 全市場掃描 (非回測策略,僅供參考) ---
latest_rsi_relaxed = {}
for ticker in closes.columns:
    try:
        rval = rsi_all[ticker].iloc[-1]
        cprice = closes[ticker].iloc[-1]
        if not pd.isna(rval) and not pd.isna(cprice) and cprice >= 5.0 and rval < 30:
            lot = HK_LOT_SIZES.get(ticker, 100)
            latest_rsi_relaxed[ticker] = {
                "ticker": ticker,
                "name": HK_STOCK_NAMES.get(ticker, "港股"),
                "rsi": round(float(rval), 2),
                "price": round(float(cprice), 2),
                "lot_size": lot,
                "lot_cost": round(float(cprice) * lot, 2),
                "tv_ticker": f"HKEX:{int(ticker.split('.')[0])}" if ticker.split('.')[0].isdigit() else ticker,
                "in_strategy": bool(rval < 25)
            }
    except: pass

recent_days = int(252 * 1.5)
recent_hsi_c = hsi_c.iloc[-recent_days:]
recent_hsi_sma = hsi_200ma.iloc[-recent_days:]
recent_hsi_v = hsi_v.iloc[-recent_days:]
recent_hsi_dates = recent_hsi_c.index.strftime('%Y-%m-%d').tolist()

ftd_signals = []
for i in range(1, len(recent_hsi_c)):
    prev_c = recent_hsi_c.iloc[i-1]
    cur_c = recent_hsi_c.iloc[i]
    if pd.isna(prev_c) or pd.isna(cur_c): continue

    lookback_start = max(0, i - 60)
    recent_peak = recent_hsi_c.iloc[lookback_start:i].max()

    pct_change = ((cur_c - prev_c) / prev_c) * 100
    vol_increase = recent_hsi_v.iloc[i] > recent_hsi_v.iloc[i-1]

    if cur_c <= recent_peak * 0.90 and pct_change >= 1.5 and vol_increase:
        ftd_signals.append({
            "date": recent_hsi_dates[i],
            "price": round(cur_c, 2),
            "label": f"底部反彈 +{pct_change:.1f}%"
        })

hsi_json_data = {
    "dates": recent_hsi_dates,
    "closes": [round(x, 2) if not pd.isna(x) else None for x in recent_hsi_c],
    "sma200": [round(x, 2) if not pd.isna(x) else None for x in recent_hsi_sma],
    "ftds": ftd_signals
}

def safe_list(series):
    return [None if pd.isna(x) else round(float(x), 2) for x in series.tolist()]

def clean_nans(obj):
    if isinstance(obj, dict): return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list): return [clean_nans(v) for v in obj]
    if isinstance(obj, float):
        if pd.isna(obj) or math.isnan(obj) or np.isnan(obj) or np.isinf(obj): return None
    return obj

# ==============================================================================
# 3. 實盤回測引擎模組化
# ==============================================================================
print("⏳ 3/5 啟動多重情境回測引擎 (RSI 28/25 + Turtle)...")

def run_backtest(scenario_name, max_pos_limit, entry_price_df, slippage=0.0):
    start_idx = 250
    real_portfolio = {}
    completed_trades = []
    pnl_history = []

    is_t_plus_1 = (entry_price_df is opens)
    end_idx = len(closes) - 1 if is_t_plus_1 else len(closes)

    def process_exits(current_date_str, i_idx):
        tickers_to_remove = []
        for ticker, trade in real_portfolio.items():
            trade['Bars_Held'] += 1
            h, l, c = highs[ticker].iloc[i_idx], lows[ticker].iloc[i_idx], closes[ticker].iloc[i_idx]
            if pd.isna(h) or pd.isna(l) or pd.isna(c): continue

            is_closed = False
            if h >= trade['TP']:
                trade['Exit_Date'], trade['Exit_Price'], trade['Status'], trade['Exit_Reason'] = current_date_str, trade['TP'], 'Win', 'TP'
                trade['PnL_%'] = round(((trade['TP'] - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                is_closed = True
            elif l <= trade['SL']:
                trade['Exit_Date'], trade['Exit_Price'], trade['Status'], trade['Exit_Reason'] = current_date_str, trade['SL'], 'Loss', 'SL'
                trade['PnL_%'] = round(((trade['SL'] - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                is_closed = True
            elif "RSI" in trade['Type']:
                if trade['Bars_Held'] >= 15 and c <= trade['Entry_Price']:
                    trade['Exit_Date'], trade['Exit_Price'], trade['Status'], trade['Exit_Reason'] = current_date_str, c, 'Loss', 'Time_SL'
                    trade['PnL_%'] = round(((c - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                    is_closed = True
                elif trade['Bars_Held'] >= 30:
                    trade['Exit_Date'], trade['Exit_Price'] = current_date_str, c
                    trade['Status'] = 'Win' if c > trade['Entry_Price'] else 'Loss'
                    trade['Exit_Reason'] = 'Max_Hold'
                    trade['PnL_%'] = round(((c - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                    is_closed = True
            elif "海龜" in trade['Type']:
                if trade['Bars_Held'] >= 60:
                    trade['Exit_Date'], trade['Exit_Price'] = current_date_str, c
                    trade['Status'] = 'Win' if c > trade['Entry_Price'] else 'Loss'
                    trade['Exit_Reason'] = 'Max_Hold'
                    trade['PnL_%'] = round(((c - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                    is_closed = True

            if is_closed:
                completed_trades.append(trade)
                pnl_history.append({"Date": current_date_str, "Type": trade['Type'], "PnL": trade['PnL_%']})
                tickers_to_remove.append(ticker)

        for tid in tickers_to_remove:
            del real_portfolio[tid]

    todays_all_signals = []

    for i in tqdm(range(start_idx, end_idx), desc=scenario_name):
        current_date = closes.index[i]
        date_str = current_date.strftime('%Y-%m-%d')
        cur_hsi, cur_hsi_200 = hsi_c.iloc[i], hsi_200ma.iloc[i]
        if pd.isna(cur_hsi) or pd.isna(cur_hsi_200): continue

        is_bull = cur_hsi > cur_hsi_200
        cur_vix = round(vix_c.iloc[i] if not pd.isna(vix_c.iloc[i]) else 18.0, 2)

        day_120_rets = ret_120d.iloc[i].dropna()
        pqr_ranks = day_120_rets.rank(pct=True) * 100 if not day_120_rets.empty else pd.Series()

        process_exits(date_str, i)
        daily_signals = []

        if cur_vix < 15:
            continue

        for ticker in closes.columns:
            if ticker in real_portfolio: continue
            c = closes[ticker].iloc[i]
            if pd.isna(c) or c < 5.0: continue

            pqr_score = round(pqr_ranks.get(ticker, 0), 2)
            dh = donchian_high_all[ticker].iloc[i]
            rsi_val = rsi_all[ticker].iloc[i]

            signal = None
            if 15 <= cur_vix <= 35 and is_bull and c > dh and pqr_score >= 80:
                signal = {"Type": "PQR 海龜突破", "Priority": 1, "SL": c * 0.90, "TP": c * 1.30}
            elif cur_vix >= 15 and rsi_val < 25:
                signal = {"Type": "RSI 均值回歸 (28/25)", "Priority": 2, "SL": c * 0.90, "TP": c * 1.15}

            if signal:
                if is_t_plus_1:
                    raw_price = entry_price_df[ticker].iloc[i+1]
                    entry_date_str = closes.index[i+1].strftime('%Y-%m-%d')
                else:
                    raw_price = entry_price_df[ticker].iloc[i]
                    entry_date_str = date_str

                if pd.isna(raw_price): continue
                final_entry_price = raw_price * (1 + slippage)
                fin = get_fundamentals(ticker)
                lot = HK_LOT_SIZES.get(ticker, 100)

                fin_str = f"股息: {fin['div']}, 動能: {fin['earn_label']}<br>P/E: {fin['pe']} | P/B: {fin['pb']} | ROE: {fin['roe']}"

                daily_signals.append({
                    "Trade_ID": f"{ticker}_{entry_date_str}", "Ticker": ticker, "Stock_Name": HK_STOCK_NAMES.get(ticker, "港股"),
                    "TV_Ticker": f"HKEX:{int(ticker.split('.')[0])}" if ticker.split('.')[0].isdigit() else ticker,
                    "Type": signal['Type'], "Priority": signal['Priority'], "PQR_Score": pqr_score, "RSI_Value": round(rsi_val, 2),
                    "Entry_Date": entry_date_str, "Entry_Price": round(final_entry_price, 2), "Entry_VIX": cur_vix,
                    "SL": round(signal['SL'], 2), "TP": round(signal['TP'], 2), "Status": "Active",
                    "Exit_Date": "-", "Exit_Price": 0.0, "Bars_Held": 0, "PnL_%": 0.0, "Exit_Reason": "-",
                    "Lot_Size": lot, "Lot_Cost": round(final_entry_price * lot, 2),
                    "financial_data": fin_str
                })

        if i == end_idx - 1:
            todays_all_signals = daily_signals.copy()

        if daily_signals:
            slots_available = max_pos_limit - len(real_portfolio)
            if slots_available > 0:
                daily_signals.sort(key=lambda x: (x['Priority'], -x['PQR_Score']))
                for sig in daily_signals[:slots_available]:
                    real_portfolio[sig['Ticker']] = sig

    for sig in todays_all_signals:
        if sig['Ticker'] not in real_portfolio:
            sig['Status'] = 'Active'
            real_portfolio[sig['Ticker']] = sig

    all_res_trades = completed_trades + list(real_portfolio.values())
    all_res_trades.sort(key=lambda x: x['Entry_Date'], reverse=True)
    return all_res_trades, pnl_history

# ==============================================================================
# 4. 執行情境比較
# ==============================================================================
print("\n⏳ 4/5 執行情境比較與效能測試...")

trades_A, pnl_A = run_backtest("Scenario A", 3, opens, slippage=0.002)
trades_C, pnl_C = run_backtest("Scenario C", 100, opens, slippage=0.002)

def get_metrics(trades):
    closed = [t for t in trades if t['Status'] != 'Active']
    if not closed: return 0, 0, 0
    wins = sum(1 for t in closed if t['Status'] == 'Win')
    win_rate = (wins / len(closed)) * 100
    avg_pnl = sum(t['PnL_%'] for t in closed) / len(closed)
    total_trades = len(closed)
    return total_trades, round(win_rate, 2), round(avg_pnl, 2)

results = [
    {"Scenario": "A (殘酷現實 - 3檔/T+1/有滑價)", **dict(zip(['Trades', 'WinRate(%)', 'AvgPnL(%)'], get_metrics(trades_A)))},
    {"Scenario": "C (無限制版 - 無限/T+1/有滑價)", **dict(zip(['Trades', 'WinRate(%)', 'AvgPnL(%)'], get_metrics(trades_C)))}
]

print("\n📊 V10.10 情境對比報告:")
print(pd.DataFrame(results).to_string(index=False))
print("\n")

if FUTU_CTX: FUTU_CTX.close()

# ==============================================================================
# 5. 實盤日誌 Auto-Logging
# ==============================================================================
print("⏳ 處理實盤追蹤日誌 Auto-Logging...")
LOG_FILE = 'hk_quant_future_log.json'
try:
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            future_log_data = json.load(f)
    else:
        future_log_data = []
except:
    future_log_data = []

last_valid_date = valid_idx[-1].strftime('%Y-%m-%d')
today_signals = [t for t in trades_C if t['Status'] == 'Active' and t['Entry_Date'] == last_valid_date]

existing_ids = {item['Trade_ID'] for item in future_log_data}
new_logs_added = 0
for sig in today_signals:
    if sig['Trade_ID'] not in existing_ids:
        log_entry = sig.copy()
        log_entry['Log_Time'] = UPDATE_TIME
        future_log_data.append(log_entry)
        new_logs_added += 1

future_log_data.sort(key=lambda x: x['Log_Time'], reverse=True)

with open(LOG_FILE, 'w', encoding='utf-8') as f:
    json.dump(future_log_data, f, ensure_ascii=False, indent=4)
print(f"✅ Auto-Logging 完成,今日新增 {new_logs_added} 筆追蹤紀錄。")

# ==============================================================================
# 6. 生成 HTML Dashboard 報告
# ==============================================================================
today_dt = datetime.datetime.now()
valid_dates_list = [d.strftime('%Y-%m-%d') for d in closes.index]

def enrich_chart_data(trade_list):
    for t in trade_list:
        ticker = t['Ticker']
        t['current_price'] = round(float(closes[ticker].iloc[-1]), 2)
        t['Hold_Days'] = t['Bars_Held']
        lot = HK_LOT_SIZES.get(ticker, 100)
        t['Lot_Size'] = lot
        t['Lot_Cost'] = round(t['current_price'] * lot, 2)

        entry_idx = valid_dates_list.index(t['Entry_Date'])
        exit_idx_to_use = valid_dates_list.index(t['Exit_Date']) if t['Status'] != 'Active' else len(closes) - 1

        start_chart_idx = max(0, entry_idx - 150)
        end_chart_idx = min(len(closes), exit_idx_to_use + 40)
        if t['Status'] == 'Active': end_chart_idx = len(closes)

        t['chart_dates'] = closes.index[start_chart_idx:end_chart_idx].strftime('%Y-%m-%d').tolist()
        t['chart_prices'] = safe_list(closes[ticker].iloc[start_chart_idx:end_chart_idx])
        t['chart_sma20'] = safe_list(sma20_all[ticker].iloc[start_chart_idx:end_chart_idx])
        t['chart_ubb'] = safe_list(upper_bb_all[ticker].iloc[start_chart_idx:end_chart_idx])
        t['chart_lbb'] = safe_list(lower_bb_all[ticker].iloc[start_chart_idx:end_chart_idx])
    return trade_list

five_years_ago_str = (pd.to_datetime(END_DATE) - pd.DateOffset(years=5)).strftime('%Y-%m-%d')

trades_A_5y = [t for t in trades_A if t['Status'] == 'Active' or t['Entry_Date'] >= five_years_ago_str]
trades_A_enriched = enrich_chart_data(trades_A_5y)

trades_C_5y = [t for t in trades_C if t['Status'] == 'Active' or t['Entry_Date'] >= five_years_ago_str]
one_year_ago_str = (pd.to_datetime(END_DATE) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')

for t in trades_C_5y:
    if t['Entry_Date'] >= one_year_ago_str or t['Status'] == 'Active':
        enrich_chart_data([t])
    else:
        t['current_price'] = round(float(closes[t['Ticker']].iloc[-1]), 2)
        t['Hold_Days'] = t['Bars_Held']
        lot = HK_LOT_SIZES.get(t['Ticker'], 100)
        t['Lot_Size'] = lot
        t['Lot_Cost'] = round(t['current_price'] * lot, 2)
        t['chart_dates'], t['chart_prices'], t['chart_sma20'], t['chart_ubb'], t['chart_lbb'] = [], [], [], [], []

active_trades_unlimited = [t for t in trades_C if t['Status'] == 'Active']
for t in active_trades_unlimited:
    t['current_price'] = round(float(closes[t['Ticker']].iloc[-1]), 2)
    t['Hold_Days'] = t['Bars_Held']
    lot = HK_LOT_SIZES.get(t['Ticker'], 100)
    t['Lot_Size'] = lot
    t['Lot_Cost'] = round(t['current_price'] * lot, 2)
enrich_chart_data(active_trades_unlimited)

def get_vix(d_str):
    try: return round(float(vix_c.loc[pd.to_datetime(d_str)]), 2)
    except: return 18.0

pnl_df = pd.DataFrame(pnl_A)
pnl_json_all = {"dates": [], "vix": [], "total": [], "turtle": [], "rsi": []}
pnl_json_5y = {"dates": [], "vix": [], "total": [], "turtle": [], "rsi": []}

if not pnl_df.empty:
    pnl_df['Date'] = pd.to_datetime(pnl_df['Date'])
    pnl_df = pnl_df.sort_values('Date').reset_index(drop=True)
    pnl_df['Real_PnL'] = pnl_df['PnL'] * 0.10

    unique_dates_all = sorted(pnl_df['Date'].unique())
    total_cum_all = pnl_df.groupby('Date')['Real_PnL'].sum().cumsum()
    t_df_all = pnl_df[pnl_df['Type'].str.contains('PQR|海龜')].groupby('Date')['Real_PnL'].sum().cumsum()
    r_df_all = pnl_df[pnl_df['Type'].str.contains('RSI')].groupby('Date')['Real_PnL'].sum().cumsum()

    pnl_json_all["dates"] = [d.strftime('%Y-%m-%d') for d in unique_dates_all]
    pnl_json_all["vix"] = [get_vix(d) for d in unique_dates_all]
    pnl_json_all["total"] = [round(total_cum_all.get(d, 0), 2) for d in unique_dates_all]
    pnl_json_all["turtle"] = [round(t_df_all[t_df_all.index <= d].iloc[-1], 2) if not t_df_all[t_df_all.index <= d].empty else 0 for d in unique_dates_all]
    pnl_json_all["rsi"] = [round(r_df_all[r_df_all.index <= d].iloc[-1], 2) if not r_df_all[r_df_all.index <= d].empty else 0 for d in unique_dates_all]

    pnl_df_5y = pnl_df[pnl_df['Date'] >= pd.to_datetime(five_years_ago_str)]
    unique_dates_5y = sorted(pnl_df_5y['Date'].unique())

    if len(unique_dates_5y) > 0:
        total_cum_5y = pnl_df_5y.groupby('Date')['Real_PnL'].sum().cumsum()
        t_df_5y = pnl_df_5y[pnl_df_5y['Type'].str.contains('PQR|海龜')].groupby('Date')['Real_PnL'].sum().cumsum()
        r_df_5y = pnl_df_5y[pnl_df_5y['Type'].str.contains('RSI')].groupby('Date')['Real_PnL'].sum().cumsum()

        pnl_json_5y["dates"] = [d.strftime('%Y-%m-%d') for d in unique_dates_5y]
        pnl_json_5y["vix"] = [get_vix(d) for d in unique_dates_5y]
        pnl_json_5y["total"] = [round(total_cum_5y.get(d, 0), 2) for d in unique_dates_5y]
        pnl_json_5y["turtle"] = [round(t_df_5y[t_df_5y.index <= d].iloc[-1], 2) if not t_df_5y[t_df_5y.index <= d].empty else 0 for d in unique_dates_5y]
        pnl_json_5y["rsi"] = [round(r_df_5y[r_df_5y.index <= d].iloc[-1], 2) if not r_df_5y[r_df_5y.index <= d].empty else 0 for d in unique_dates_5y]

print("⏳ 5/5 正在生成 V10.10 HTML...")
json_str_active_unl = json.dumps(clean_nans(active_trades_unlimited), ensure_ascii=False).replace('</', '<\\/')
json_str_C = json.dumps(clean_nans(trades_C_5y), ensure_ascii=False).replace('</', '<\\/')
json_str_A = json.dumps(clean_nans(trades_A_enriched), ensure_ascii=False).replace('</', '<\\/')
future_log_json_str = json.dumps(clean_nans(future_log_data), ensure_ascii=False).replace('</', '<\\/')
relaxed_rsi_json_str = json.dumps(clean_nans(list(latest_rsi_relaxed.values())), ensure_ascii=False).replace('</', '<\\/')

dates_json_str = json.dumps(valid_dates_list, ensure_ascii=False)
pnl_json_all_str = json.dumps(pnl_json_all, ensure_ascii=False)
pnl_json_5y_str = json.dumps(pnl_json_5y, ensure_ascii=False)
hsi_json_str = json.dumps(clean_nans(hsi_json_data), ensure_ascii=False)

html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <title>HK Quant Master V10.10 - 終極打擊面板</title>
    <style>
        body {{ background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; scroll-behavior: smooth; }}
        .card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }}
        .tab-active {{ background-color: #2563eb; color: white; border-bottom: 2px solid #60a5fa; }}
        .tab-inactive {{ background-color: transparent; color: #94a3b8; border-bottom: 2px solid transparent; }}
        .tab-inactive:hover {{ color: white; background-color: rgba(255,255,255,0.05); }}
        th.sortable:hover {{ color: #ffffff; background-color: #334155; cursor: pointer; user-select: none; }}
        .row-selected {{ background-color: rgba(59, 130, 246, 0.2) !important; border-left: 4px solid #3b82f6; }}
        .nav-container::-webkit-scrollbar {{ display: none; }}
        .nav-container {{ -ms-overflow-style: none; scrollbar-width: none; }}
        .grok-btn {{ background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%); border: 1px solid #e94560; }}
        .grok-btn:hover {{ background: linear-gradient(135deg, #0f3460 0%, #e94560 100%); }}
        .gemini-btn {{ background: linear-gradient(135deg, #000000 0%, #171717 100%); border: 1px solid #c084fc; }}
        .gemini-btn:hover {{ background: linear-gradient(135deg, #2e1065 0%, #3b0764 100%); }}
        .perplexity-btn {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #14b8a6; }}
        .perplexity-btn:hover {{ background: linear-gradient(135deg, #0f172a 0%, #134e4a 100%); }}
        .tv-btn {{ background: #131722; border: 1px solid #2962ff; }}
        .tv-btn:hover {{ background: #1e222d; border-color: #5b9cf6; }}
        .relaxed-badge {{ background: rgba(251, 146, 60, 0.15); border: 1px solid #fb923c; color: #fb923c; }}
        .strategy-badge {{ background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; color: #ef4444; }}
    </style>
</head>
<body class="p-4">
    <div class="max-w-7xl mx-auto w-full">
        <div class="card p-6 mb-6 flex flex-col md:flex-row justify-between items-start md:items-center shadow-lg border-b-4 border-blue-500">
            <div>
                <h1 class="text-3xl font-black text-white mb-1">HK Quant Master <span class="text-blue-500">V10.10 Pro</span></h1>
                <p class="text-slate-400 text-sm">防呆股息修復 | Futu 雙軌引擎 | 完美排序 | 三大 AI 聯合診斷</p>
                <div class="text-xs mt-1 text-slate-500 font-bold">最後更新時間:{UPDATE_TIME}</div>

                <div class="flex flex-wrap gap-3 mt-4">
                    <a href="https://www.patreon.com/c/teachthe66yearsoldmominvest" target="_blank" class="flex items-center bg-[#FF424D] hover:bg-[#FF424D]/80 text-white text-xs font-bold py-1.5 px-3 rounded shadow transition-colors">
                        🔥 Patreon: 每日一篇教66歲丫媽學投資
                    </a>
                    <a href="https://www.threads.net/@teachthe66yearsoldmominvest" target="_blank" class="flex items-center bg-zinc-800 hover:bg-zinc-700 text-white text-xs font-bold py-1.5 px-3 rounded shadow transition-colors border border-zinc-600">
                        🧵 Threads: @teachthe66yearsoldmominvest
                    </a>
                </div>
            </div>
            <div class="mt-4 md:mt-0 text-right bg-slate-900 p-4 rounded-lg border border-slate-700 self-stretch md:self-auto flex flex-col justify-center">
                <div class="text-sm text-slate-300">最新 VIX 指數:<span class="text-xl font-bold text-yellow-400 block mt-1">{vix_c.iloc[-1]:.2f}</span></div>
            </div>
        </div>

        <div class="nav-container flex border-b border-slate-700 mb-6 space-x-1 overflow-x-auto whitespace-nowrap">
            <button onclick="switchTab('tab-scan')" id="btn-scan" class="tab-btn tab-active px-4 py-3 font-bold rounded-t-lg">🎯 活躍推薦 (無限制)</button>
            <button onclick="switchTab('tab-unlimited')" id="btn-unlimited" class="tab-btn tab-inactive px-4 py-3 font-bold rounded-t-lg text-pink-400">💯 全市場潛在訊號</button>
            <button onclick="switchTab('tab-future-log')" id="btn-future-log" class="tab-btn tab-inactive px-4 py-3 font-bold rounded-t-lg text-orange-400">📝 實盤追蹤日誌</button>
            <button onclick="switchTab('tab-hsi')" id="btn-hsi" class="tab-btn tab-inactive px-4 py-3 font-bold rounded-t-lg text-cyan-400">📊 大盤環境 (HSI)</button>
            <button onclick="switchTab('tab-pnl-5y')" id="btn-pnl-5y" class="tab-btn tab-inactive px-4 py-3 font-bold rounded-t-lg text-yellow-400">📈 回測績效與資金曲線</button>
            <button onclick="switchTab('tab-manual')" id="btn-manual" class="tab-btn tab-inactive px-4 py-3 font-bold rounded-t-lg text-purple-400">📖 說明書</button>
        </div>

        <div id="tab-scan" class="tab-content block">
            <div class="card p-6 mb-4 bg-gradient-to-r from-slate-800 to-slate-900 border-l-4 border-blue-500 shadow-xl">
                <h2 class="text-xl font-bold text-white mb-1">🎯 活躍推薦 — 無限制全市場 (情境 C)</h2>
                <p class="text-slate-400 text-sm">點擊 ✨Gemini、🤖Grok 或 🌐Perplexity，系統將自動複製該股最新數據並開啟 AI 分析網頁。</p>
            </div>

            <div class="sticky top-0 z-40 bg-[#0f172a] pt-2 pb-4 border-b border-slate-700 shadow-2xl mb-4">
                <div class="card p-4 flex flex-col relative border-t-4 border-blue-500">
                    <div class="flex justify-between items-center mb-2">
                        <h3 id="chart_title_scan" class="text-lg font-bold text-white">點擊表格並使用鍵盤 ↑ ↓ 極速切換圖表</h3>
                        <span class="text-xs text-slate-400 bg-slate-800 px-2 py-1 rounded">資料來源: 情境 C (無資金排擠)</span>
                    </div>
                    <div class="h-[250px] w-full relative bg-[#0f172a] rounded"><canvas id="myChartScan" class="w-full h-full"></canvas></div>
                </div>
            </div>

            <h3 class="text-lg font-bold text-white mb-3 px-1">📌 策略持倉中 (RSI&lt;25 / 海龜突破)</h3>
            <div class="overflow-x-auto border border-slate-700 rounded-lg shadow-lg mb-8">
                <table class="w-full text-left border-collapse whitespace-nowrap">
                    <thead class="bg-slate-800">
                        <tr class="text-slate-300 text-sm border-b border-slate-700">
                            <th class="p-3 sortable" onclick="sortTableGen('activeTableBody', 0)">進場日 ↕</th>
                            <th class="p-3 sortable" onclick="sortTableGen('activeTableBody', 1)">標的 ↕</th>
                            <th class="p-3 sortable" onclick="sortTableGen('activeTableBody', 2)">策略與 PQR ↕</th>
                            <th class="p-3">基本面快照</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('activeTableBody', 4)">進場價 ↕</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('activeTableBody', 5)">一手總價 ↕</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('activeTableBody', 6)">最新價 ↕</th>
                            <th class="p-3 text-center sortable" onclick="sortTableGen('activeTableBody', 7)">交易日 ↕</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('activeTableBody', 8)">浮動損益 ↕</th>
                            <th class="p-3 text-center">🤖 AI 聯合診斷</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-slate-300" id="activeTableBody"></tbody>
                </table>
            </div>

            <h3 class="text-lg font-bold text-white mb-3 px-1 flex items-center gap-2">
                🔍 寬鬆 RSI &lt; 30 全市場掃描 <span class="relaxed-badge text-xs px-2 py-0.5 rounded">非回測策略・僅供參考</span>
            </h3>
            <div class="overflow-x-auto border border-orange-900/50 rounded-lg shadow-lg">
                <table class="w-full text-left border-collapse whitespace-nowrap">
                    <thead class="bg-slate-800">
                        <tr class="text-orange-300 text-sm border-b border-slate-700">
                            <th class="p-3 sortable" onclick="sortTableGen('relaxedRsiBody', 0)">標的 ↕</th>
                            <th class="p-3 text-center sortable" onclick="sortTableGen('relaxedRsiBody', 1)">RSI(28) ↕</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('relaxedRsiBody', 2)">現價 ↕</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('relaxedRsiBody', 3)">一手成本 ↕</th>
                            <th class="p-3 text-center sortable" onclick="sortTableGen('relaxedRsiBody', 4)">策略內? ↕</th>
                            <th class="p-3 text-center">操作</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-slate-300" id="relaxedRsiBody"></tbody>
                </table>
            </div>
        </div>

        <div id="tab-unlimited" class="tab-content hidden">
            <div class="card p-6 mb-6 bg-gradient-to-r from-slate-800 to-slate-900 border-l-4 border-pink-400 shadow-xl">
                <div class="flex flex-wrap justify-between items-center gap-3 mb-2">
                    <h2 class="text-xl font-bold text-white">💯 全市場歷史訊號 (無限制版覆盤)</h2>
                    <button onclick="switchTab('tab-pnl-5y')" class="bg-yellow-600 hover:bg-yellow-500 text-white text-xs font-bold py-2 px-4 rounded shadow transition-colors">
                        📈 查看資金排擠後真實績效 →
                    </button>
                </div>
            </div>
            
            <div class="flex flex-wrap gap-3 mb-4 p-4 card items-center">
                <select id="filterYearUnl" onchange="filterUnlimitedTable()" class="bg-slate-900 text-white p-2 border border-slate-600 rounded text-sm focus:outline-none focus:border-pink-500">
                    <option value="">📆 所有年份 (近5年)</option>
                </select>
                <select id="filterTypeUnl" onchange="filterUnlimitedTable()" class="bg-slate-900 text-white p-2 border border-slate-600 rounded text-sm focus:outline-none focus:border-pink-500">
                    <option value="">🎯 所有策略</option>
                    <option value="海龜">🐢 PQR 海龜突破</option>
                    <option value="RSI">🛡️ RSI 均值回歸</option>
                </select>
                <select id="filterStatusUnl" onchange="filterUnlimitedTable()" class="bg-slate-900 text-white p-2 border border-slate-600 rounded text-sm focus:outline-none focus:border-pink-500">
                    <option value="">⚡ 所有狀態</option>
                    <option value="Active">🔔 持倉中 (Active)</option>
                    <option value="Win">🟢 獲利出場 (Win)</option>
                    <option value="Loss">🔴 停損/時間出場 (Loss)</option>
                </select>
                <input type="text" id="searchInputUnl" onkeyup="filterUnlimitedTable()" placeholder="🔍 搜尋代碼/名稱..." class="bg-slate-900 text-white p-2 border border-slate-600 rounded text-sm w-40 focus:outline-none focus:border-pink-500">
            </div>

            <div class="sticky top-0 z-40 bg-[#0f172a] pt-2 pb-4 border-b border-slate-700 shadow-2xl mb-4">
                <div class="card p-4 flex flex-col relative border-t-4 border-pink-500">
                    <div class="flex justify-between items-center mb-2">
                        <h3 id="chart_title_unl" class="text-lg font-bold text-white">點擊表格並使用鍵盤 ↑ ↓ 極速切換圖表</h3>
                    </div>
                    <div class="h-[250px] w-full relative bg-[#0f172a] rounded"><canvas id="myChartUnl" class="w-full h-full"></canvas></div>
                </div>
            </div>

            <div class="overflow-x-auto border border-slate-700 rounded-lg shadow-lg">
                <table class="w-full text-left border-collapse whitespace-nowrap">
                    <thead class="bg-slate-800">
                        <tr class="text-slate-300 text-sm border-b border-slate-700">
                            <th class="p-3 sortable" onclick="sortTableGen('unlimitedTableBody', 0)">進場日 ↕</th>
                            <th class="p-3 sortable" onclick="sortTableGen('unlimitedTableBody', 1)">標的 ↕</th>
                            <th class="p-3 sortable" onclick="sortTableGen('unlimitedTableBody', 2)">策略與 PQR ↕</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('unlimitedTableBody', 3)">進場價 ↕</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('unlimitedTableBody', 4)">出場價 ↕</th>
                            <th class="p-3 text-center sortable" onclick="sortTableGen('unlimitedTableBody', 5)">交易日 ↕</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('unlimitedTableBody', 6)">淨利/浮動 ↕</th>
                            <th class="p-3 text-center">狀態</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-slate-300" id="unlimitedTableBody"></tbody>
                </table>
            </div>
        </div>

        <div id="tab-future-log" class="tab-content hidden">
            <div class="card p-6 mb-6 border-l-4 border-orange-400 shadow-xl bg-slate-800">
                <h2 class="text-2xl font-bold text-white mb-2">📝 實盤追蹤日誌 (Auto Future Logging)</h2>
                <p class="text-slate-400 text-sm">系統會在每次執行時,自動提取「當日最新」的全市場潛在推薦,並永久保存在本地 `hk_quant_future_log.json` 中。</p>
            </div>

            <div class="overflow-x-auto border border-slate-700 rounded-lg shadow-lg">
                <table class="w-full text-left border-collapse whitespace-nowrap">
                    <thead class="bg-slate-900">
                        <tr class="text-orange-300 text-sm border-b border-slate-700">
                            <th class="p-3 sortable" onclick="sortTableGen('futureLogTableBody', 0)">紀錄時間 ↕</th>
                            <th class="p-3 sortable" onclick="sortTableGen('futureLogTableBody', 1)">觸發日 ↕</th>
                            <th class="p-3 sortable" onclick="sortTableGen('futureLogTableBody', 2)">標的 ↕</th>
                            <th class="p-3 sortable" onclick="sortTableGen('futureLogTableBody', 3)">策略 ↕</th>
                            <th class="p-3 text-right sortable" onclick="sortTableGen('futureLogTableBody', 4)">進場價 ↕</th>
                            <th class="p-3 text-right">SL / TP</th>
                            <th class="p-3 text-center">環境參數 (VIX/RSI/PQR)</th>
                            <th class="p-3 text-center">AI 複檢</th>
                        </tr>
                    </thead>
                    <tbody class="text-sm text-slate-300" id="futureLogTableBody"></tbody>
                </table>
            </div>
        </div>

        <div id="tab-hsi" class="tab-content hidden">
            <div class="card p-6 border-t-4 border-cyan-400 shadow-xl mb-6">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
                    <div>
                        <h2 class="text-2xl font-bold text-white">📊 恆生指數 (HSI) 近 1.5 年大盤環境分析</h2>
                        <p class="text-slate-400 text-sm mt-1">趨勢判定 (SMA200) 與 底部強勢放量日 (FTD) 追蹤</p>
                    </div>
                    <div class="flex gap-4 text-xs font-bold mt-4 md:mt-0 bg-slate-900 p-3 rounded border border-slate-700">
                        <div class="flex items-center"><span class="w-4 h-1 bg-cyan-400 mr-2 rounded"></span> HSI 收盤價</div>
                        <div class="flex items-center"><span class="w-4 h-1 bg-purple-500 mr-2 rounded border-dashed border-t-2"></span> SMA200 (牛熊分界)</div>
                        <div class="flex items-center"><span class="text-yellow-400 text-lg mr-1">★</span> FTD (底部量增反彈)</div>
                    </div>
                </div>
                <div class="h-[500px] w-full bg-[#0f172a] rounded p-2 border border-slate-700 mt-4 relative">
                    <canvas id="hsiChart" class="w-full h-full"></canvas>
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="card p-5 bg-slate-800">
                    <h3 class="text-lg font-bold text-white mb-2">🐢 海龜突破發動條件 (順勢)</h3>
                    <ul class="space-y-2 text-sm text-slate-300 mt-3">
                        <li class="flex items-center"><span class="mr-2">✅</span> VIX 位於 15 ~ 35 之間</li>
                        <li class="flex items-center"><span class="mr-2">✅</span> 大盤指數 (HSI) <strong class="text-green-400 ml-1">大於</strong> SMA200</li>
                        <li class="flex items-center text-slate-500"><span class="mr-2">💡</span> <span class="italic">大盤走多時發動,突破前高進場,追求波段爆發。</span></li>
                    </ul>
                </div>
                <div class="card p-5 bg-slate-800">
                    <h3 class="text-lg font-bold text-white mb-2">🛡️ RSI 均值回歸發動條件 (逆勢)</h3>
                    <ul class="space-y-2 text-sm text-slate-300 mt-3">
                        <li class="flex items-center"><span class="mr-2">✅</span> VIX <strong class="text-red-400 ml-1">大於 15</strong> (不可在死水區)</li>
                        <li class="flex items-center"><span class="mr-2">✅</span> 個股 RSI(28) <strong class="text-red-400 ml-1">小於 25</strong> (極度恐慌)</li>
                        <li class="flex items-center text-slate-500"><span class="mr-2">💡</span> <span class="italic">無視大盤趨勢,專挑恐慌錯殺股搶反彈,見好就收。</span></li>
                    </ul>
                </div>
            </div>
        </div>

        <div id="tab-pnl-5y" class="tab-content hidden">
            <div class="card p-6 border-t-4 border-yellow-400 shadow-xl mb-6">
                <div class="flex justify-between items-center mb-2">
                    <h2 class="text-2xl font-bold text-white">📈 近 5 年實盤資金曲線與 VIX 區間標示</h2>
                    <div class="flex gap-4 text-xs font-bold">
                        <div class="flex items-center"><span class="w-3 h-3 bg-red-500/20 mr-1 rounded"></span> VIX > 35 (極度恐慌)</div>
                        <div class="flex items-center"><span class="w-3 h-3 bg-green-500/10 mr-1 rounded"></span> VIX 15~35 (順勢黃金區)</div>
                        <div class="flex items-center"><span class="w-3 h-3 bg-slate-500/20 mr-1 rounded"></span> VIX < 15 (死水)</div>
                    </div>
                </div>
                <p class="text-slate-400 text-sm">資金基準: 嚴格遵守單筆 10% 資金排擠限制 (情境A)</p>
                <div class="h-[500px] w-full bg-[#0f172a] rounded p-2 border border-slate-700 mt-4">
                    <canvas id="pnlChart5y" class="w-full h-full"></canvas>
                </div>
            </div>

            <div class="card p-6 border-t-4 border-green-500 shadow-xl mb-6">
                <div class="flex justify-between items-center mb-2">
                    <h2 class="text-2xl font-bold text-white">🌍 2000-2026 全歷史大週期資金曲線與 VIX 標示</h2>
                </div>
                <div class="h-[500px] w-full bg-[#0f172a] rounded p-2 border border-slate-700 mt-4">
                    <canvas id="pnlChartAll" class="w-full h-full"></canvas>
                </div>
            </div>

            <div class="card p-6 mb-6 bg-gradient-to-r from-slate-800 to-slate-900 border-l-4 border-yellow-400 shadow-xl">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-xl font-bold text-white">⚙️ 歷史覆盤與動態績效評估 (近 5 年已平倉交易)</h2>
                    <span class="text-xs bg-blue-900 text-blue-300 px-2 py-1 rounded">基準: 單筆 10% 資金配置 (情境 A)</span>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-5 gap-4 text-center mb-6">
                    <div class="bg-slate-900 p-3 rounded border border-slate-700">
                        <div class="text-xs text-slate-400 mb-1">符合筆數</div>
                        <div id="dyn-count" class="text-xl font-bold text-white">0</div>
                    </div>
                    <div class="bg-slate-900 p-3 rounded border border-slate-700">
                        <div class="text-xs text-slate-400 mb-1">勝率 (Win Rate)</div>
                        <div id="dyn-wr" class="text-xl font-bold text-blue-400">0%</div>
                    </div>
                    <div class="bg-slate-900 p-3 rounded border border-slate-700">
                        <div class="text-xs text-slate-400 mb-1">年化報酬 (Ann. Return)</div>
                        <div id="dyn-ann" class="text-xl font-bold text-green-400">0%</div>
                    </div>
                    <div class="bg-slate-900 p-3 rounded border border-slate-700">
                        <div class="text-xs text-slate-400 mb-1">最大回撤 (MDD)</div>
                        <div id="dyn-mdd" class="text-xl font-bold text-red-400">0%</div>
                    </div>
                    <div class="bg-slate-900 p-3 rounded border border-slate-700">
                        <div class="text-xs text-slate-400 mb-1">夏普值 (Sharpe)</div>
                        <div id="dyn-sharpe" class="text-xl font-bold text-yellow-400">0.00</div>
                    </div>
                </div>

                <div class="flex flex-wrap gap-3 mb-4 card items-center">
                    <select id="filterYear" onchange="filterTable()" class="bg-slate-900 text-white p-2 border border-slate-600 rounded text-sm focus:outline-none focus:border-blue-500">
                        <option value="">📆 所有年份 (近5年)</option>
                    </select>
                    <select id="filterType" onchange="filterTable()" class="bg-slate-900 text-white p-2 border border-slate-600 rounded text-sm focus:outline-none focus:border-blue-500">
                        <option value="">🎯 所有策略</option>
                        <option value="海龜">🐢 PQR 海龜突破</option>
                        <option value="RSI">🛡️ RSI 均值回歸</option>
                    </select>
                    <select id="filterStatus" onchange="filterTable()" class="bg-slate-900 text-white p-2 border border-slate-600 rounded text-sm focus:outline-none focus:border-blue-500">
                        <option value="">⚡ 所有狀態</option>
                        <option value="Win">🟢 獲利出場 (Win)</option>
                        <option value="Loss">🔴 停損/時間出場 (Loss)</option>
                    </select>
                    <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="🔍 搜尋股票代碼..." class="bg-slate-900 text-white p-2 border border-slate-600 rounded text-sm w-40 focus:outline-none focus:border-blue-500">
                </div>

                <div class="overflow-x-auto border border-slate-700 rounded-lg">
                    <table class="w-full text-left border-collapse whitespace-nowrap">
                        <thead class="bg-slate-800">
                            <tr class="text-slate-300 text-sm border-b border-slate-700">
                                <th class="p-3 sortable" onclick="sortTableGen('historyTableBodyA', 0)">進場日 ↕</th>
                                <th class="p-3 sortable" onclick="sortTableGen('historyTableBodyA', 1)">標的 ↕</th>
                                <th class="p-3 sortable" onclick="sortTableGen('historyTableBodyA', 2)">策略 ↕</th>
                                <th class="p-3 text-right sortable" onclick="sortTableGen('historyTableBodyA', 3)">進場價 ↕</th>
                                <th class="p-3 text-right sortable" onclick="sortTableGen('historyTableBodyA', 4)">出場價 ↕</th>
                                <th class="p-3 text-right sortable" onclick="sortTableGen('historyTableBodyA', 5)">淨利 ↕</th>
                                <th class="p-3 text-center">狀態</th>
                                <th class="p-3 text-center">看圖 (切至無限制版)</th>
                            </tr>
                        </thead>
                        <tbody class="text-sm text-slate-300" id="historyTableBodyA"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="tab-manual" class="tab-content hidden card p-8 leading-relaxed text-slate-300">
            <h2 class="text-2xl font-bold text-blue-400 mb-6 border-b border-slate-700 pb-2">📖 V10.10 系統說明書 (User Manual)</h2>

            <div class="mb-6">
                <h3 class="text-lg font-bold text-white mb-2">⚙️ 1. 核心邏輯與風控 (Core Engine & Risk)</h3>
                <ul class="list-disc pl-6 space-y-2">
                    <li><strong class="text-blue-300">防仙股濾網:</strong> 系統自動排除所有股價 <strong>低於 $5 港幣</strong> 的標的,避免流動性風險。</li>
                    <li><strong class="text-blue-300">PQR 搶位戰:</strong> 當訊號超過剩餘資金空位時,將依據 120 日動能評分 (PQR Score) 排序,優先買入最強勢的股票。</li>
                    <li><strong class="text-blue-300">AI 雙重診斷:</strong> 表格內提供 <strong>✨ Gemini</strong> 與 <strong>🤖 Grok</strong> 按鈕。系統會將該筆交易的「技術條件、基本面、一手總價」等打包成繁體中文提示詞，供 AI 驗證。</li>
                </ul>
            </div>

            <div class="mb-6">
                <h3 class="text-lg font-bold text-white mb-2">⚔️ 2. 雙引擎與 VIX 區間發動條件</h3>
                <ul class="list-disc pl-6 space-y-3">
                    <li><span class="bg-slate-700 text-slate-300 px-2 py-0.5 rounded text-xs font-bold mr-2">VIX < 15</span><strong class="text-white">⚪ 死水區間強制空倉:</strong><br>市場缺乏波動,所有策略勝率極低,系統無條件保留現金。</li>
                    <li><span class="bg-green-900 text-green-400 px-2 py-0.5 rounded text-xs font-bold mr-2">VIX 15~35</span><strong class="text-white">🟢 順勢引擎 (PQR 海龜突破):</strong><br>尋找突破 20 日高點且 PQR > 80 的強勢股 (大盤需站上 200MA)。停利 +30%,停損 -10%。</li>
                    <li><span class="bg-red-900 text-red-400 px-2 py-0.5 rounded text-xs font-bold mr-2">VIX >= 15</span><strong class="text-white">🔴 逆勢引擎 (RSI 均值回歸):</strong><br>尋找長週期 <strong>RSI(28) < 25</strong> 的極端超跌股。停利 +15%,停損 -10%。</li>
                </ul>
            </div>
        </div>

        <div class="text-center mt-12 mb-4 flex flex-col items-center justify-center">
            <p class="mb-3 font-bold tracking-wider text-slate-300 text-sm">📊 累積訪客數</p>
            <img src="https://komarev.com/ghpvc/?username=hk-quant-master&label=Views&color=0ea5e9&style=flat" alt="Hits">
        </div>

    </div>

    <script>
        const activeUnlData = {json_str_active_unl};
        const signalsDataA = {json_str_A};
        const signalsDataC = {json_str_C};
        const futureLogData = {future_log_json_str};
        const relaxedRsiData = {relaxed_rsi_json_str};

        const allDates = {dates_json_str};
        const pnlDataAll = {pnl_json_all_str};
        const pnlData5y = {pnl_json_5y_str};
        const hsiData = {hsi_json_str};

        let chartInstanceScan = null;
        let chartInstanceAll = null;
        let chartInstanceUnl = null;

        let pnlChart5y = null;
        let pnlChartAll = null;
        let hsiChart = null;
        let currentRowIndex = -1;

        // === Text Clipboard Fallback ===
        function copyToClipboard(text) {{
            if (navigator.clipboard && window.isSecureContext) {{
                return navigator.clipboard.writeText(text);
            }} else {{
                let textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.position = "fixed";
                textArea.style.left = "-999999px";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                return new Promise((res, rej) => {{
                    document.execCommand('copy') ? res() : rej();
                    textArea.remove();
                }});
            }}
        }}

        // === AI Links Builder (JS for Grok & Gemini) ===
        function buildPromptText(row) {{
            const pqr = row.PQR_Score ? row.PQR_Score : 'N/A';
            const rsi = row.RSI_Value ? row.RSI_Value : (row.rsi ? row.rsi : 'N/A');
            const price = row.current_price || row.price || row.Entry_Price || 'N/A';
            const fin = row.financial_data ? row.financial_data.replace(/<br>/g, ', ') : 'N/A';
            const lotSize = row.Lot_Size || row.lot_size || 100;
            const lotCost = row.Lot_Cost || row.lot_cost || 'N/A';
            const strat = row.Type || 'RSI 寬鬆觀察';
            
            let stratCondition = "";
            if (strat.includes("海龜")) {{
                stratCondition = "1. VIX 恐慌指數介於 15 ~ 35 (健康的趨勢環境)\\n2. 恆生指數 (HSI) 位於 200 日均線之上 (多頭格局)\\n3. 該股價突破近 20 日高點 (唐奇安通道上軌)\\n4. 該股 120 日動能 PQR 分數 >= 80 (市場前 20% 強勢)";
            }} else if (strat.includes("RSI")) {{
                stratCondition = "1. VIX 恐慌指數 >= 15 (市場具備波動度)\\n2. 該股 28 日 RSI < 25 (極度超賣區間)";
            }} else {{
                stratCondition = "1. 該股 28 日 RSI 目前小於 30 (接近超賣區間)";
            }}
            
            const tk = row.Ticker || row.ticker || '';
            const nm = row.Stock_Name || row.name || '';

            return `請扮演一位頂尖的港股量化分析師。我的一個量化交易系統剛剛為【${{tk}} ${{nm}}】發出了買進/觀察訊號。
請務必【全程使用繁體中文】回答，並執行以下驗證與分析：

[系統當前偵測數據]
- 觸發策略：${{strat}}
- 最新股價：$$${{price}} HKD
- RSI(28) 數值：${{rsi}}
- 120日動能 PQR 分數：${{pqr}} / 100
- 基本面快照：${{fin}}
- 預估一手成本：$$${{lotCost}} HKD

[該策略的技術觸發條件]
${{stratCondition}}

請根據你的最新網路搜尋與圖表分析能力，完成以下任務：
1. 【公司與市場定位】：請簡要介紹該公司的主營業務，及其在所屬行業/市場中的地位與競爭力。
2. 【技術條件雙重驗證】：請幫我核實上述的「技術觸發條件」是否真實反映在該股最新的 K 線圖表與大盤環境中？
3. 【基本面與籌碼/消息面】：這家公司近期的基本面是否穩健？有沒有任何隱藏的地雷（如盈警、配股、大行降評、政策打壓）導致它被錯殺或假突破？
4. 【最終實戰建議】：綜合以上，這個量化訊號目前值得跟單買進嗎？請給出明確的「強烈買進 (BUY)」、「觀望 (HOLD)」或「避開 (AVOID)」結論，並說明停損建議。`;
        }}

        function copyAndOpenAI(tradeId, isRelaxed, targetAi) {{
            let row;
            if (isRelaxed) {{
                row = relaxedRsiData.find(r => r.ticker === tradeId);
            }} else {{
                row = activeUnlData.find(s => s.Trade_ID === tradeId) || 
                      futureLogData.find(s => s.Trade_ID === tradeId) ||
                      signalsDataA.find(s => s.Trade_ID === tradeId) ||
                      signalsDataC.find(s => s.Trade_ID === tradeId);
            }}
            if (!row) return;
            const prompt = buildPromptText(row);
            
            let url = "";
            if(targetAi === 'gemini') url = "https://gemini.google.com/app";
            else if(targetAi === 'grok') url = `https://grok.com/?q=${{encodeURIComponent(prompt)}}`;
            else if(targetAi === 'perplexity') url = `https://www.perplexity.ai/?q=${{encodeURIComponent(prompt)}}`;

            copyToClipboard(prompt).then(() => {{
                if(targetAi === 'gemini') {{
                    alert("✅ 提示詞已複製到剪貼簿！\\n即將為您開啟 Gemini，請在對話框直接貼上 (Ctrl+V / Cmd+V) 即可送出分析。");
                }}
                window.open(url, "_blank");
            }}).catch(() => {{
                if(targetAi === 'gemini') {{
                    window.prompt("您的瀏覽器阻擋了自動複製，請手動複製以下提示詞，然後前往 Gemini：", prompt);
                }}
                window.open(url, "_blank");
            }});
        }}

        function buildActionBtns(row) {{
            return `<div class="flex gap-1 justify-center">
                <button onclick="copyAndOpenAI('${{row.Trade_ID}}', false, 'gemini'); event.stopPropagation();" class="gemini-btn text-[10px] font-bold px-2 py-1 rounded text-[#c084fc] hover:text-white transition-colors" title="複製提示詞並開啟 Gemini">✨ Gemini</button>
                <button onclick="copyAndOpenAI('${{row.Trade_ID}}', false, 'grok'); event.stopPropagation();" class="grok-btn text-[10px] font-bold px-2 py-1 rounded text-red-400 hover:text-white transition-colors" title="Grok AI 專業分析">🤖 Grok</button>
                <button onclick="copyAndOpenAI('${{row.Trade_ID}}', false, 'perplexity'); event.stopPropagation();" class="perplexity-btn text-[10px] font-bold px-2 py-1 rounded text-[#2dd4bf] hover:text-white transition-colors" title="Perplexity 深度搜尋">🌐 Perplex</button>
            </div>`;
        }}

        function buildActionBtnsSimple(row) {{
            return `<div class="flex gap-1 justify-center">
                <button onclick="copyAndOpenAI('${{row.ticker}}', true, 'gemini'); event.stopPropagation();" class="gemini-btn text-[10px] font-bold px-2 py-1 rounded text-[#c084fc] hover:text-white transition-colors" title="複製提示詞並開啟 Gemini">✨ Gemini</button>
                <button onclick="copyAndOpenAI('${{row.ticker}}', true, 'grok'); event.stopPropagation();" class="grok-btn text-[10px] font-bold px-2 py-1 rounded text-red-400 hover:text-white transition-colors" title="Grok AI 專業分析">🤖 Grok</button>
                <button onclick="copyAndOpenAI('${{row.ticker}}', true, 'perplexity'); event.stopPropagation();" class="perplexity-btn text-[10px] font-bold px-2 py-1 rounded text-[#2dd4bf] hover:text-white transition-colors" title="Perplexity 深度搜尋">🌐 Perplex</button>
            </div>`;
        }}

        // === Plugin: Exit Reason Annotation ===
        const exitReasonPlugin = {{
            id: 'exitReasonPlugin',
            afterDraw: (chart) => {{
                const ctx = chart.ctx;
                const tradeData = chart.config.data.customTradeData;
                if(!tradeData || tradeData.Status === 'Active') return;
                chart.data.datasets.forEach((dataset, i) => {{
                    if (dataset.label === '出場') {{
                        const meta = chart.getDatasetMeta(i);
                        meta.data.forEach((point) => {{
                            if (!point.skip) {{
                                ctx.save();
                                ctx.fillStyle = tradeData.Status === 'Win' ? '#4ade80' : '#f87171';
                                ctx.font = 'bold 13px "Segoe UI"';
                                ctx.textAlign = 'left';
                                ctx.fillText(tradeData.Exit_Reason, point.x + 10, point.y - 12);
                                ctx.restore();
                            }}
                        }});
                    }}
                }});
            }}
        }};

        // === Plugin: VIX Background Zones ===
        const vixBackgroundPlugin = {{
            id: 'vixBackgroundPlugin',
            beforeDraw: (chart) => {{
                const ctx = chart.ctx;
                const xAxis = chart.scales.x;
                const yAxis = chart.scales.y;
                const vixData = chart.config.data.vixData;
                if(!vixData || vixData.length === 0) return;
                ctx.save();
                const topY = yAxis.top;
                const bottomY = yAxis.bottom;
                for(let i = 0; i < vixData.length - 1; i++) {{
                    let v = vixData[i];
                    let color = 'rgba(0,0,0,0)';
                    if(v > 35) color = 'rgba(239, 68, 68, 0.1)';
                    else if(v < 15) color = 'rgba(100, 116, 139, 0.2)';
                    else color = 'rgba(34, 197, 94, 0.05)';
                    let xStart = xAxis.getPixelForValue(i);
                    let xEnd = xAxis.getPixelForValue(i+1);
                    ctx.fillStyle = color;
                    ctx.fillRect(xStart, topY, xEnd - xStart, bottomY - topY);
                }}
                ctx.restore();
            }}
        }};

        Chart.register(exitReasonPlugin, vixBackgroundPlugin);

        // === Helpers ===
        function populateYearFilter() {{
            let yearsA = [...new Set(signalsDataA.filter(s => s.Status !== 'Active').map(s => s.Entry_Date.substring(0,4)))];
            let yearsC = [...new Set(signalsDataC.filter(s => s.Status !== 'Active').map(s => s.Entry_Date.substring(0,4)))];
            let allY = [...new Set([...yearsA, ...yearsC])].sort().reverse();

            let sel = document.getElementById("filterYear");
            let selUnl = document.getElementById("filterYearUnl");

            allY.forEach(y => {{
                let opt = document.createElement('option'); opt.value = y; opt.innerText = "📆 " + y + " 年";
                sel.appendChild(opt);
                let opt2 = document.createElement('option'); opt2.value = y; opt2.innerText = "📆 " + y + " 年";
                selUnl.appendChild(opt2);
            }});
        }}

        function buildStatusBadge(row) {{
            if (row.Status === 'Active') return `<span class="px-2 py-1 bg-yellow-900/50 text-yellow-400 rounded text-xs animate-pulse">Active</span>`;
            if (row.Exit_Reason === 'TP') return `<span class="px-2 py-1 bg-green-900/50 text-green-400 rounded text-xs">Win (TP)</span>`;
            if (row.Exit_Reason === 'Time_SL') return `<span class="px-2 py-1 bg-orange-900/50 text-orange-400 rounded text-xs">Time SL</span>`;
            if (row.Exit_Reason === 'Max_Hold') return `<span class="px-2 py-1 bg-blue-900/50 text-blue-400 rounded text-xs">Max Hold</span>`;
            return `<span class="px-2 py-1 bg-red-900/50 text-red-400 rounded text-xs">Loss (SL)</span>`;
        }}

        function buildTvLink(tvTicker, displayTicker) {{
            return `<a href="https://www.tradingview.com/chart/?symbol=${{tvTicker}}&interval=1D" target="_blank" class="text-blue-400 hover:text-blue-300 underline underline-offset-2" onclick="event.stopPropagation()" title="前往TradingView查看 SMA20/50 (需自行儲存範本)">${{displayTicker}}</a>`;
        }}

        // === Render Active Table (Unlimited from Scenario C) ===
        function renderActiveTable() {{
            const tbody = document.getElementById('activeTableBody');
            tbody.innerHTML = "";
            const actives = activeUnlData;

            if(actives.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="12" class="p-6 text-center text-slate-500">目前空手,無活躍觸發標的。</td></tr>`;
                return;
            }}

            actives.forEach(row => {{
                let pnl = ((row.current_price - row.Entry_Price) / row.Entry_Price) * 100;
                let pnlClr = pnl > 0 ? "text-green-400" : "text-red-400";
                let pnlStr = `<span class="${{pnlClr}} font-bold">${{pnl>0?'+':''}}${{pnl.toFixed(2)}}%</span>`;
                let pqrBadge = `<span class="text-[10px] ml-1 bg-purple-900/50 text-purple-300 border border-purple-700 px-1 rounded">PQR: ${{row.PQR_Score}}</span>`;
                let tvLink = buildTvLink(row.TV_Ticker, row.Ticker);
                let lotSize = row.Lot_Size || 100;
                let lotCost = row.Lot_Cost || (row.current_price * lotSize);

                let tr = document.createElement('tr');
                tr.className = "trade-row active-trade-row border-b border-slate-800 hover:bg-slate-700/50 cursor-pointer";
                tr.setAttribute('data-trade-id', row.Trade_ID);
                tr.onclick = function() {{
                    document.querySelectorAll('.active-trade-row').forEach(el => el.classList.remove('row-selected'));
                    tr.classList.add('row-selected');
                    const visibleRows = Array.from(document.querySelectorAll('.active-trade-row'));
                    currentRowIndex = visibleRows.indexOf(tr);
                    loadChart(row.Trade_ID, 'myChartScan', activeUnlData);
                }};

                tr.innerHTML = `
                    <td class="p-3 text-blue-300 font-bold" data-sort="${{row.Entry_Date}}">${{row.Entry_Date}}</td>
                    <td class="p-3 font-bold" data-sort="${{row.Ticker}}">${{tvLink}}<br><span class="text-xs text-slate-400 font-normal">${{row.Stock_Name}}</span></td>
                    <td class="p-3 text-sm" data-sort="${{row.PQR_Score}}">${{row.Type}}<br>${{pqrBadge}}</td>
                    <td class="p-3 text-xs text-slate-400 leading-relaxed">${{row.financial_data}}</td>
                    <td class="p-3 text-right font-bold text-white" data-sort="${{row.Entry_Price}}">$${{row.Entry_Price}}</td>
                    <td class="p-3 text-right text-yellow-100" data-sort="${{lotCost}}">${{lotSize}}股<br><span class="text-[10px] text-slate-500">約$${{lotCost.toLocaleString()}}</span></td>
                    <td class="p-3 text-right text-blue-300 font-bold" data-sort="${{row.current_price}}">$${{row.current_price}}</td>
                    <td class="p-3 text-center text-yellow-400 font-bold" data-sort="${{row.Hold_Days}}">${{row.Hold_Days}}</td>
                    <td class="p-3 text-right bg-slate-900/30" data-sort="${{pnl}}">${{pnlStr}}</td>
                    <td class="p-3 text-center">${{buildActionBtns(row)}}</td>
                `;
                tbody.appendChild(tr);
            }});

            if(actives.length > 0) {{
                let firstRow = document.querySelector('#activeTableBody tr');
                firstRow.classList.add('row-selected');
                currentRowIndex = 0;
                loadChart(actives[0].Trade_ID, 'myChartScan', activeUnlData);
            }}
        }}

        // === Render Relaxed RSI Table ===
        function renderRelaxedRsiTable() {{
            const tbody = document.getElementById('relaxedRsiBody');
            tbody.innerHTML = "";

            if(relaxedRsiData.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="7" class="p-6 text-center text-slate-500">目前無股票 RSI(28) 低於 30。</td></tr>`;
                return;
            }}

            const sorted = [...relaxedRsiData].sort((a,b) => a.rsi - b.rsi);
            sorted.forEach(row => {{
                let inStratBadge = row.in_strategy
                    ? `<span class="strategy-badge text-xs px-2 py-0.5 rounded font-bold">RSI&lt;25 策略內</span>`
                    : `<span class="relaxed-badge text-xs px-2 py-0.5 rounded">25≤RSI&lt;30 觀察</span>`;
                let tvLink = buildTvLink(row.tv_ticker, row.ticker);

                let tr = document.createElement('tr');
                tr.className = "border-b border-slate-800 hover:bg-slate-700/50";
                tr.innerHTML = `
                    <td class="p-3 font-bold" data-sort="${{row.ticker}}">${{tvLink}}<br><span class="text-xs text-slate-400 font-normal">${{row.name}}</span></td>
                    <td class="p-3 text-center font-bold ${{row.rsi < 25 ? 'text-red-400' : 'text-orange-400'}}" data-sort="${{row.rsi}}">${{row.rsi}}</td>
                    <td class="p-3 text-right text-white" data-sort="${{row.price}}">$${{row.price}}</td>
                    <td class="p-3 text-right text-yellow-300 font-bold" data-sort="${{row.lot_cost}}">$$${{row.lot_cost.toLocaleString()}}</td>
                    <td class="p-3 text-center" data-sort="${{row.in_strategy ? 1 : 0}}">${{inStratBadge}}</td>
                    <td class="p-3 text-center">${{buildActionBtnsSimple(row)}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // === Render Scenario A History (for Performance tab) ===
        function renderTable(data) {{
            const tbody = document.getElementById('historyTableBodyA');
            tbody.innerHTML = "";
            let closedTrades = data.filter(d => d.Status !== 'Active');

            closedTrades.forEach(row => {{
                let pnlClr = row['PnL_%'] > 0 ? "text-green-400" : "text-red-400";
                let pnlStr = `<span class="${{pnlClr}} font-bold">${{row['PnL_%']>0?'+':''}}${{row['PnL_%'].toFixed(2)}}%</span>`;
                let tvLink = buildTvLink(row.TV_Ticker, row.Ticker);
                
                let jumpBtn = `<button onclick="jumpToUnlimitedChart('${{row.Trade_ID}}'); event.stopPropagation();" class="bg-slate-700 hover:bg-slate-600 text-white px-3 py-1 rounded text-xs shadow border border-slate-500">📊 看圖</button>`;

                let tr = document.createElement('tr');
                tr.className = "border-b border-slate-800 hover:bg-slate-700/50";
                tr.innerHTML = `
                    <td class="p-3 text-blue-300 font-bold" data-sort="${{row.Entry_Date}}">${{row.Entry_Date}}</td>
                    <td class="p-3 font-bold" data-sort="${{row.Ticker}}">${{tvLink}}<br><span class="text-xs text-slate-400 font-normal">${{row.Stock_Name}}</span></td>
                    <td class="p-3 text-sm text-slate-300" data-sort="${{row.Type}}">${{row.Type}}</td>
                    <td class="p-3 text-right text-slate-300" data-sort="${{row.Entry_Price}}">$${{row.Entry_Price}}</td>
                    <td class="p-3 text-right text-slate-300" data-sort="${{row.Exit_Price}}">$${{row.Exit_Price}}</td>
                    <td class="p-3 text-right bg-slate-900/30" data-sort="${{row['PnL_%']}}">${{pnlStr}}</td>
                    <td class="p-3 text-center">${{buildStatusBadge(row)}}</td>
                    <td class="p-3 text-center">${{jumpBtn}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}
        
        function jumpToUnlimitedChart(tradeId) {{
            switchTab('tab-unlimited');
            setTimeout(() => {{
                let targetRow = document.querySelector(`.unl-trade-row[data-trade-id='${{tradeId}}']`);
                if(targetRow) {{
                    document.querySelectorAll('.unl-trade-row').forEach(el => el.classList.remove('row-selected'));
                    targetRow.classList.add('row-selected');
                    targetRow.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                }}
                loadChart(tradeId, 'myChartUnl', signalsDataC);
            }}, 100);
        }}

        // === Render Scenario C Unlimited ===
        function renderUnlimitedTable(data) {{
            const tbody = document.getElementById('unlimitedTableBody');
            tbody.innerHTML = "";

            data.forEach(row => {{
                let isAct = row.Status === 'Active';
                let pnl = isAct ? ((row.current_price - row.Entry_Price) / row.Entry_Price) * 100 : row['PnL_%'];
                let pnlClr = pnl > 0 ? "text-green-400" : "text-red-400";
                let pnlStr = `<span class="${{pnlClr}} font-bold">${{pnl>0?'+':''}}${{pnl.toFixed(2)}}%</span>`;
                let pqrBadge = `<span class="text-[10px] ml-1 bg-purple-900/50 text-purple-300 border border-purple-700 px-1 rounded">PQR: ${{row.PQR_Score}}</span>`;
                let tvLink = buildTvLink(row.TV_Ticker, row.Ticker);
                let exitP = isAct ? `- ($${{row.current_price}})` : `$${{row.Exit_Price}}`;

                let tr = document.createElement('tr');
                tr.className = "trade-row unl-trade-row border-b border-slate-800 hover:bg-slate-700/50 cursor-pointer";
                tr.setAttribute('data-trade-id', row.Trade_ID);
                tr.onclick = function() {{
                    document.querySelectorAll('.unl-trade-row').forEach(el => el.classList.remove('row-selected'));
                    tr.classList.add('row-selected');
                    const visibleRows = Array.from(document.querySelectorAll('.unl-trade-row')).filter(el => el.style.display !== 'none');
                    currentRowIndex = visibleRows.indexOf(tr);
                    loadChart(row.Trade_ID, 'myChartUnl', signalsDataC);
                }};

                tr.innerHTML = `
                    <td class="p-3 text-blue-300 font-bold" data-sort="${{row.Entry_Date}}">${{row.Entry_Date}}</td>
                    <td class="p-3 font-bold" data-sort="${{row.Ticker}}">${{tvLink}}<br><span class="text-xs text-slate-400 font-normal">${{row.Stock_Name}}</span></td>
                    <td class="p-3 text-sm" data-sort="${{row.PQR_Score}}">${{row.Type}}<br>${{pqrBadge}}</td>
                    <td class="p-3 text-right" data-sort="${{row.Entry_Price}}">$${{row.Entry_Price}}</td>
                    <td class="p-3 text-right text-slate-300" data-sort="${{isAct?row.current_price:row.Exit_Price}}">${{exitP}}</td>
                    <td class="p-3 text-center" data-sort="${{row.Hold_Days}}">${{row.Hold_Days}}</td>
                    <td class="p-3 text-right bg-slate-900/30" data-sort="${{pnl}}">${{pnlStr}}</td>
                    <td class="p-3 text-center">${{buildStatusBadge(row)}}</td>
                `;
                tbody.appendChild(tr);
            }});

            if(data.length > 0) {{
                let firstRow = document.querySelector('#unlimitedTableBody tr');
                if(firstRow) {{
                    firstRow.classList.add('row-selected');
                    currentRowIndex = 0;
                    loadChart(data[0].Trade_ID, 'myChartUnl', signalsDataC);
                }}
            }}
        }}

        // === Render Future Log ===
        function renderFutureLogTable() {{
            const tbody = document.getElementById('futureLogTableBody');
            tbody.innerHTML = "";

            if(futureLogData.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="8" class="p-6 text-center text-slate-500">尚無追蹤紀錄。系統將在每次更新時自動加入當日訊號。</td></tr>`;
                return;
            }}

            futureLogData.forEach(row => {{
                let tvLink = buildTvLink(row.TV_Ticker, row.Ticker);
                let envSnap = `VIX: <span class="text-yellow-400">${{row.Entry_VIX}}</span> | RSI: <span class="text-pink-400">${{row.RSI_Value || 'N/A'}}</span> | PQR: <span class="text-purple-400">${{row.PQR_Score}}</span>`;

                let tr = document.createElement('tr');
                tr.className = "border-b border-slate-800 hover:bg-slate-700/50";

                tr.innerHTML = `
                    <td class="p-3 text-orange-300 text-xs" data-sort="${{row.Log_Time}}">${{row.Log_Time}}</td>
                    <td class="p-3 text-blue-300 font-bold" data-sort="${{row.Entry_Date}}">${{row.Entry_Date}}</td>
                    <td class="p-3 font-bold" data-sort="${{row.Ticker}}">${{tvLink}}<br><span class="text-xs text-slate-400 font-normal">${{row.Stock_Name}}</span></td>
                    <td class="p-3 text-sm" data-sort="${{row.Type}}">${{row.Type}}</td>
                    <td class="p-3 text-right font-bold text-white" data-sort="${{row.Entry_Price}}">$${{row.Entry_Price}}</td>
                    <td class="p-3 text-right text-xs"><span class="text-red-400">SL: ${{row.SL}}</span><br><span class="text-green-400">TP: ${{row.TP}}</span></td>
                    <td class="p-3 text-center text-xs bg-slate-900/50 rounded">${{envSnap}}</td>
                    <td class="p-3 text-center">${{buildActionBtns(row)}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // === Dynamic Performance Metrics ===
        function calculateDynamicMetrics(trades) {{
            let closedTrades = trades.filter(t => t.Status !== 'Active');
            document.getElementById('dyn-count').innerText = closedTrades.length;
            if(closedTrades.length === 0) {{
                document.getElementById('dyn-wr').innerText = "0%";
                document.getElementById('dyn-ann').innerText = "0%";
                document.getElementById('dyn-mdd').innerText = "0%";
                document.getElementById('dyn-sharpe').innerText = "0.00";
                return;
            }}

            let wins = closedTrades.filter(t => t.Status === 'Win').length;
            document.getElementById('dyn-wr').innerText = ((wins / closedTrades.length) * 100).toFixed(1) + "%";

            let dailyRet = new Float64Array(allDates.length);
            closedTrades.forEach(t => {{
                let sIdx = allDates.indexOf(t.Entry_Date);
                let eIdx = allDates.indexOf(t.Exit_Date);
                if(sIdx !== -1 && eIdx !== -1 && eIdx >= sIdx) {{
                    let days = eIdx - sIdx + 1;
                    let daily = (t['PnL_%'] / 100 * 0.10) / days;
                    for(let i=sIdx; i<=eIdx; i++) dailyRet[i] += daily;
                }}
            }});

            let equity = 1.0, peak = 1.0, mdd = 0.0, sum = 0, sumSq = 0, count = 0;
            let started = false;
            for(let i=0; i<dailyRet.length; i++) {{
                let r = dailyRet[i];
                if(r !== 0) started = true;
                if(started) {{
                    equity *= (1 + r);
                    if(equity > peak) peak = equity;
                    let dd = (equity - peak) / peak;
                    if(dd < mdd) mdd = dd;
                    sum += r; sumSq += r * r; count++;
                }}
            }}

            let years = count / 252;
            let ann = years > 0 ? (Math.pow(equity, 1/years) - 1) * 100 : 0;
            let mean = count > 0 ? sum / count : 0;
            let variance = count > 0 ? (sumSq / count) - (mean * mean) : 0;
            let std = Math.sqrt(variance);
            let sharpe = std > 0 ? (mean / std) * Math.sqrt(252) : 0;

            document.getElementById('dyn-ann').innerText = (ann>0?'+':'') + ann.toFixed(2) + "%";
            document.getElementById('dyn-mdd').innerText = (mdd*100).toFixed(2) + "%";
            document.getElementById('dyn-sharpe').innerText = sharpe.toFixed(2);
        }}

        // === Filters ===
        function filterTable() {{
            let yearF = document.getElementById("filterYear").value;
            let typeF = document.getElementById("filterType").value;
            let statusF = document.getElementById("filterStatus").value;
            let searchF = document.getElementById("searchInput").value.toUpperCase();

            let filtered = signalsDataA.filter(s => {{
                if(s.Status === 'Active') return false;
                let matchYear = yearF === "" || s.Entry_Date.startsWith(yearF);
                let matchType = typeF === "" || s.Type.includes(typeF);
                let matchStatus = true;
                if(statusF !== "") {{
                    if(statusF === "Win") matchStatus = (s.Status === "Win");
                    else if(statusF === "Time_SL") matchStatus = (s.Exit_Reason === "Time_SL");
                    else if(statusF === "Max_Hold") matchStatus = (s.Exit_Reason === "Max_Hold");
                    else if(statusF === "Loss") matchStatus = (s.Status === "Loss" && s.Exit_Reason === "SL");
                }}
                let matchSearch = searchF === "" || s.Ticker.includes(searchF) || (s.Stock_Name && s.Stock_Name.includes(searchF));
                return matchYear && matchType && matchStatus && matchSearch;
            }});

            renderTable(filtered);
            calculateDynamicMetrics(filtered);
        }}

        function filterUnlimitedTable() {{
            let yearF = document.getElementById("filterYearUnl").value;
            let typeF = document.getElementById("filterTypeUnl").value;
            let statusF = document.getElementById("filterStatusUnl").value;
            let searchF = document.getElementById("searchInputUnl").value.toUpperCase();

            let filtered = signalsDataC.filter(s => {{
                let matchYear = yearF === "" || s.Entry_Date.startsWith(yearF);
                let matchType = typeF === "" || s.Type.includes(typeF);
                let matchStatus = true;
                if(statusF !== "") {{
                    if(statusF === "Active") matchStatus = (s.Status === "Active");
                    else if(statusF === "Win") matchStatus = (s.Status === "Win");
                    else if(statusF === "Loss") matchStatus = (s.Status === "Loss");
                }}
                let matchSearch = searchF === "" || s.Ticker.includes(searchF) || (s.Stock_Name && s.Stock_Name.includes(searchF));
                return matchYear && matchType && matchStatus && matchSearch;
            }});

            renderUnlimitedTable(filtered);
        }}

        // === ULTIMATE SAFE SORTING ALGORITHM ===
        let sortDirs = {{}};
        function sortTableGen(tbodyId, colIdx) {{
            const tbody = document.getElementById(tbodyId);
            const rows = Array.from(tbody.querySelectorAll("tr"));
            if (typeof sortDirs[tbodyId + colIdx] === 'undefined') sortDirs[tbodyId + colIdx] = true;
            let asc = sortDirs[tbodyId + colIdx];
            sortDirs[tbodyId + colIdx] = !asc;

            rows.sort((a, b) => {{
                let cellA = a.children[colIdx];
                let cellB = b.children[colIdx];
                
                if (!cellA || !cellB) return 0;

                let valA = cellA.hasAttribute('data-sort') ? cellA.getAttribute('data-sort') : cellA.innerText.trim();
                let valB = cellB.hasAttribute('data-sort') ? cellB.getAttribute('data-sort') : cellB.innerText.trim();

                // 判斷是否為 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
                let isDateA = /^\d{{4}}-\d{{2}}-\d{{2}}/.test(valA);
                let isDateB = /^\d{{4}}-\d{{2}}-\d{{2}}/.test(valB);

                if (isDateA && isDateB) {{
                    return asc ? valA.localeCompare(valB) : valB.localeCompare(valA);
                }}

                let n1 = parseFloat(valA);
                let n2 = parseFloat(valB);

                if(!isNaN(n1) && !isNaN(n2)) {{
                    return asc ? n1 - n2 : n2 - n1;
                }}
                
                return asc ? String(valA).localeCompare(String(valB)) : String(valB).localeCompare(String(valA));
            }});
            
            tbody.innerHTML = "";
            rows.forEach(r => tbody.appendChild(r));
        }}

        function sortActiveTable(tb, col) {{ sortTableGen(tb, col); }}

        function loadChart(tradeId, canvasId, sourceDataArray) {{
            const sig = sourceDataArray.find(s => s.Trade_ID === tradeId);
            if (!sig) return;

            const titleEl = document.getElementById(canvasId === 'myChartScan' ? 'chart_title_scan' : (canvasId === 'myChartUnl' ? 'chart_title_unl' : 'chart_title_all'));
            if(titleEl) titleEl.innerHTML = sig.Ticker + " " + sig.Stock_Name + " <span class='text-sm text-slate-400'>(" + sig.Type + ")</span>";

            const ctx = document.getElementById(canvasId).getContext('2d');
            let targetChart = null;
            if(canvasId === 'myChartScan') targetChart = chartInstanceScan;
            else if(canvasId === 'myChartUnl') targetChart = chartInstanceUnl;
            else targetChart = chartInstanceAll;

            if (targetChart) targetChart.destroy();

            if (!sig.chart_dates || sig.chart_dates.length === 0) {{
                if(titleEl) titleEl.innerHTML += " <span class='text-red-400 text-xs'>(超過一年的數據為節省效能未渲染圖表)</span>";
                return;
            }}

            const entryIdx = sig.chart_dates.indexOf(sig.Entry_Date);
            const exitIdx = sig.Exit_Date !== "-" ? sig.chart_dates.indexOf(sig.Exit_Date) : sig.chart_dates.length - 1;
            const entryData = sig.chart_dates.map((d, idx) => (idx === entryIdx) ? sig.Entry_Price : null);
            const exitData = sig.chart_dates.map((d, idx) => (idx === exitIdx && sig.Status !== 'Active') ? sig.Exit_Price : null);

            let newChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: sig.chart_dates.map(d => d.substring(5)),
                    customTradeData: sig,
                    datasets: [
                        {{ label: '進場', data: entryData, backgroundColor: '#eab308', pointStyle: 'triangle', pointRadius: 8, showLine: false, order: 0 }},
                        {{ label: '出場', data: exitData, backgroundColor: sig.Status === 'Win' ? '#4ade80' : '#f87171', pointStyle: 'crossRot', pointRadius: 8, showLine: false, order: 1 }},
                        {{ label: '價格', data: sig.chart_prices, borderColor: '#3b82f6', tension: 0.1, pointRadius: 0, order: 2 }},
                        {{ label: 'SMA20', data: sig.chart_sma20, borderColor: '#c084fc', borderDash: [2,2], borderWidth: 1.5, pointRadius: 0, order: 3 }},
                        {{ label: 'BOLL上軌', data: sig.chart_ubb, borderColor: '#64748b', borderDash: [4,4], borderWidth: 1, pointRadius: 0, order: 4 }},
                        {{ label: 'BOLL下軌', data: sig.chart_lbb, borderColor: '#64748b', borderDash: [4,4], borderWidth: 1, pointRadius: 0, order: 5 }}
                    ]
                }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    scales: {{ x: {{ ticks: {{ color: '#94a3b8' }} }}, y: {{ ticks: {{ color: '#94a3b8' }} }} }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#e2e8f0' }} }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    let label = context.dataset.label || '';
                                    if (label === '出場') return label + ': ' + context.parsed.y + ' (' + sig.Exit_Reason + ')';
                                    return label + ': ' + context.parsed.y;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
            
            if (canvasId === 'myChartScan') chartInstanceScan = newChart; 
            else if (canvasId === 'myChartUnl') chartInstanceUnl = newChart;
            else chartInstanceAll = newChart;
        }}

        function renderPnLCharts() {{
            if(!pnlChart5y && pnlData5y.dates && pnlData5y.dates.length > 0) {{
                const ctx5y = document.getElementById('pnlChart5y').getContext('2d');
                pnlChart5y = new Chart(ctx5y, {{
                    type: 'line',
                    data: {{
                        labels: pnlData5y.dates,
                        vixData: pnlData5y.vix,
                        datasets: [
                            {{ label: '近5年總資金', data: pnlData5y.total, borderColor: '#eab308', borderWidth: 3, pointRadius: 0, tension: 0.1 }},
                            {{ label: 'PQR 突破貢獻', data: pnlData5y.turtle, borderColor: '#4ade80', borderWidth: 1, borderDash: [3,3], pointRadius: 0, tension: 0.1 }},
                            {{ label: 'RSI 逆勢貢獻', data: pnlData5y.rsi, borderColor: '#f87171', borderWidth: 1, borderDash: [3,3], pointRadius: 0, tension: 0.1 }}
                        ]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false, interaction: {{ mode: 'index', intersect: false }} }}
                }});
            }}

            if(!pnlChartAll && pnlDataAll.dates && pnlDataAll.dates.length > 0) {{
                const ctxAll = document.getElementById('pnlChartAll').getContext('2d');
                pnlChartAll = new Chart(ctxAll, {{
                    type: 'line',
                    data: {{
                        labels: pnlDataAll.dates,
                        vixData: pnlDataAll.vix,
                        datasets: [
                            {{ label: '歷史總資金 (2000-2026)', data: pnlDataAll.total, borderColor: '#22c55e', borderWidth: 3, pointRadius: 0, tension: 0.1 }},
                            {{ label: 'PQR 突破貢獻', data: pnlDataAll.turtle, borderColor: '#3b82f6', borderWidth: 1, borderDash: [3,3], pointRadius: 0, tension: 0.1 }},
                            {{ label: 'RSI 逆勢貢獻', data: pnlDataAll.rsi, borderColor: '#ef4444', borderWidth: 1, borderDash: [3,3], pointRadius: 0, tension: 0.1 }}
                        ]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false, interaction: {{ mode: 'index', intersect: false }} }}
                }});
            }}

            if(!hsiChart && hsiData.dates && hsiData.dates.length > 0) {{
                const ctxHsi = document.getElementById('hsiChart').getContext('2d');
                let ftdData = new Array(hsiData.dates.length).fill(null);
                hsiData.ftds.forEach(f => {{
                    let idx = hsiData.dates.indexOf(f.date);
                    if (idx !== -1) ftdData[idx] = f.price;
                }});

                hsiChart = new Chart(ctxHsi, {{
                    type: 'line',
                    data: {{
                        labels: hsiData.dates,
                        datasets: [
                            {{ label: 'FTD (強勢底部反彈)', data: ftdData, backgroundColor: '#facc15', borderColor: '#ca8a04', pointStyle: 'star', pointRadius: 10, pointHoverRadius: 14, showLine: false, order: 0 }},
                            {{ label: 'HSI 指數', data: hsiData.closes, borderColor: '#22d3ee', borderWidth: 2, pointRadius: 0, tension: 0.1, order: 2 }},
                            {{ label: 'SMA200', data: hsiData.sma200, borderColor: '#a855f7', borderWidth: 2, borderDash: [5,5], pointRadius: 0, tension: 0.1, order: 1 }}
                        ]
                    }},
                    options: {{ 
                        responsive: true, maintainAspectRatio: false, 
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        let label = context.dataset.label || '';
                                        if (label.includes('FTD')) {{
                                            let ftdObj = hsiData.ftds.find(f => f.date === context.label);
                                            return label + ': ' + context.parsed.y + ' (' + (ftdObj ? ftdObj.label : '') + ')';
                                        }}
                                        return label + ': ' + context.parsed.y;
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            }}
        }}

        // === Keyboard Navigation ===
        document.addEventListener('keydown', function(e) {{
            if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'SELECT') return;

            let activeTabId = document.querySelector('.tab-content:not(.hidden)').id;
            let rowClass = null; let canvasId = null; let dataSource = null;
            
            if (activeTabId === 'tab-scan') {{ rowClass = '.active-trade-row'; canvasId = 'myChartScan'; dataSource = activeUnlData; }}
            else if (activeTabId === 'tab-pnl-5y') {{ rowClass = '.history-trade-row'; canvasId = 'myChartAll'; dataSource = signalsDataA; }}
            else if (activeTabId === 'tab-unlimited') {{ rowClass = '.unl-trade-row'; canvasId = 'myChartUnl'; dataSource = signalsDataC; }}
            
            if (!rowClass) return;
            const visibleRows = Array.from(document.querySelectorAll(rowClass)).filter(el => el.style.display !== 'none');
            if (visibleRows.length === 0) return;

            if (e.key === 'ArrowDown') {{
                e.preventDefault();
                currentRowIndex = (currentRowIndex + 1) % visibleRows.length;
                let nextRow = visibleRows[currentRowIndex];
                document.querySelectorAll(rowClass).forEach(el => el.classList.remove('row-selected'));
                nextRow.classList.add('row-selected');
                nextRow.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                loadChart(nextRow.getAttribute('data-trade-id'), canvasId, dataSource);
            }}
            else if (e.key === 'ArrowUp') {{
                e.preventDefault();
                currentRowIndex = (currentRowIndex - 1 + visibleRows.length) % visibleRows.length;
                let prevRow = visibleRows[currentRowIndex];
                document.querySelectorAll(rowClass).forEach(el => el.classList.remove('row-selected'));
                prevRow.classList.add('row-selected');
                prevRow.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                loadChart(prevRow.getAttribute('data-trade-id'), canvasId, dataSource);
            }}
        }});

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(btn => {{ btn.classList.remove('tab-active'); btn.classList.add('tab-inactive'); }});
            document.getElementById(tabId).classList.remove('hidden');

            let btnId = tabId.replace('tab-', 'btn-');
            document.getElementById(btnId).classList.remove('tab-inactive');
            document.getElementById(btnId).classList.add('tab-active');

            if (tabId.includes('pnl') || tabId.includes('hsi')) renderPnLCharts();
        }}

        // Init All
        populateYearFilter();
        renderActiveTable();
        renderRelaxedRsiTable();
        renderTable(signalsDataA);
        renderUnlimitedTable(signalsDataC);
        renderFutureLogTable();
        calculateDynamicMetrics(signalsDataA.filter(s => s.Status !== 'Active'));

    </script>
</body>
</html>
"""

with open("index.html", 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"🎉 成功！生成 HK Quant Master V10.10 終極 Dashboard：index.html")
try:
    from google.colab import files
    files.download("index.html")
except:
    pass
