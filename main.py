#@title HK Quant Master V6.97 (表格對齊修復 + 5年資金曲線版)
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import json
import warnings
import time
import math
from tqdm import tqdm

warnings.filterwarnings('ignore')

# ==============================================================================
# 1. 設定觀察名單、參數與中文名稱對照表
# ==============================================================================
START_DATE = "2020-01-01" 
END_DATE = datetime.datetime.now().strftime('%Y-%m-%d')

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
    '0011.HK': '恒生銀行', '0012.HK': '恆基地產', '0016.HK': '新鴻基地產', '0017.HK': '新世界發展', '0020.HK': '商汤-W',
    '0027.HK': '銀河娛樂', '0066.HK': '港鐵公司', '0083.HK': '信和置業', '0101.HK': '恒隆地產', '0119.HK': '保利置業集團', 
    '0135.HK': '昆侖能源', '0144.HK': '招商局港口', '0151.HK': '中國旺旺', '0168.HK': '青島啤酒股份', '0175.HK': '吉利汽車',
    '0200.HK': '新濠國際發展', '0241.HK': '阿里健康', '0256.HK': '冠城鐘錶珠寶', '0267.HK': '中信股份', '0268.HK': '金蝶國際', 
    '0270.HK': '粵海投資', '0272.HK': '瑞安房地產', '0285.HK': '比亞迪電子', '0288.HK': '萬洲國際', '0291.HK': '華潤啤酒',
    '0316.HK': '東方海外國際', '0322.HK': '康師傅控股', '0336.HK': '華寶國際', '0345.HK': '維他奶國際', '0354.HK': '中國軟件國際', 
    '0358.HK': '江西銅業股份', '0386.HK': '中國石油化工股份', '0388.HK': '香港交易所', '0390.HK': '中國中鐵', '0460.HK': '四環醫藥',
    '0520.HK': '呷哺呷哺', '0522.HK': 'ASMPT', '0552.HK': '中國通信服務', '0576.HK': '浙江滬杭甬', '0586.HK': '海螺創業', 
    '0598.HK': '中國外運', '0604.HK': '深圳控股', '0656.HK': '復星國際', '0669.HK': '創科實業', '0688.HK': '中國海外發展',
    '0700.HK': '騰訊控股', '0728.HK': '中國電信', '0753.HK': '中國國航', '0762.HK': '中國聯通', '0772.HK': '閱文集團', 
    '0778.HK': '置富產業信託', '0780.HK': '同程旅行', '0813.HK': '世茂集團', '0823.HK': '領展房產基金', '0836.HK': '華潤電力',
    '0853.HK': '微創醫療', '0857.HK': '中國石油股份', '0861.HK': '神州控股', '0868.HK': '信義玻璃', '0883.HK': '中國海洋石油', 
    '0902.HK': '華能國際電力', '0909.HK': '明源雲', '0914.HK': '海螺水泥', '0916.HK': '龍源電力', '0934.HK': '中石化冠德',
    '0939.HK': '建設銀行', '0941.HK': '中國移動', '0960.HK': '龍湖集團', '0968.HK': '信義光能', '0981.HK': '中芯國際', 
    '0992.HK': '聯想集團', '0998.HK': '中信銀行', '1024.HK': '快手-W', '1030.HK': '新城發展', '1038.HK': '長江基建集團',
    '1044.HK': '恒安國際', '1055.HK': '中國南方航空', '1066.HK': '威高股份', '1071.HK': '華電國際電力', '1088.HK': '中國神華', 
    '1093.HK': '石藥集團', '1099.HK': '國藥控股', '1109.HK': '華潤置地', '1113.HK': '長實集團', '1119.HK': '創夢天地',
    '1138.HK': '中遠海能', '1157.HK': '中聯重科', '1177.HK': '中國生物製藥', '1193.HK': '華潤燃氣', '1209.HK': '華潤萬象生活', 
    '1211.HK': '比亞迪股份', '1258.HK': '中國有色礦業', '1299.HK': '友邦保險', '1308.HK': '海豐國際', '1313.HK': '華潤建材科技',
    '1316.HK': '耐世特', '1336.HK': '新華保險', '1339.HK': '中國人民保險', '1347.HK': '華虹半導體', '1368.HK': '特步國際', 
    '1378.HK': '中國宏橋', '1398.HK': '工商銀行', '1516.HK': '融創服務', '1530.HK': '三生製藥', '1658.HK': '郵儲銀行',
    '1772.HK': '贛鋒鋰業', '1787.HK': '山東黃金', '1801.HK': '信達生物', '1810.HK': '小米集團-W', '1818.HK': '招金礦業', 
    '1833.HK': '平安好醫生', '1876.HK': '百威亞太', '1898.HK': '中煤能源', '1919.HK': '中遠海控', '1928.HK': '金沙中國',
    '1929.HK': '周大福', '1997.HK': '九龍倉置業', '2005.HK': '聯邦制藥', '2007.HK': '碧桂園', '2013.HK': '微盟集團', 
    '2015.HK': '理想汽車-W', '2018.HK': '瑞聲科技', '2020.HK': '安踏體育', '2186.HK': '綠葉製藥', '2192.HK': '醫渡科技',
    '2202.HK': '萬科企業', '2238.HK': '廣汽集團', '2269.HK': '藥明生物', '2313.HK': '申洲國際', '2318.HK': '中國平安', 
    '2319.HK': '蒙牛乳業', '2331.HK': '李寧', '2333.HK': '長城汽車', '2359.HK': '藥明康德', '2380.HK': '中國電力',
    '2388.HK': '中銀香港', '2600.HK': '中國鋁業', '2618.HK': '京東物流', '2628.HK': '中國人壽', '2669.HK': '中海物業', 
    '2688.HK': '新奧能源', '2689.HK': '玖龍紙業', '2727.HK': '上海電氣', '2858.HK': '易鑫集團', '2866.HK': '中遠海發',
    '2869.HK': '綠城服務', '2877.HK': '神威藥業', '2883.HK': '中海油田服務', '2899.HK': '紫金礦業', '3311.HK': '中國建築國際', 
    '3319.HK': '雅生活服務', '3323.HK': '中國建材', '3328.HK': '交通銀行', '3331.HK': '維達國際', '3606.HK': '福耀玻璃',
    '3618.HK': '重慶農村商業銀行', '3633.HK': '中裕能源', '3690.HK': '美團-W', '3692.HK': '翰森製藥', '3738.HK': '阜博集團', 
    '3800.HK': '協鑫科技', '3868.HK': '信義能源', '3888.HK': '金山軟件', '3899.HK': '中集安瑞科', '3900.HK': '綠城中國',
    '3908.HK': '中金公司', '3933.HK': '聯邦制藥', '3958.HK': '東方證券', '3968.HK': '招商銀行', '3983.HK': '中海石油化學', 
    '3988.HK': '中國銀行', '3990.HK': '美的置業', '3993.HK': '洛陽鉬業', '6030.HK': '中信証券', '6098.HK': '碧桂園服務',
    '6110.HK': '滔搏', '6160.HK': '百濟神州', '6618.HK': '京東健康', '6690.HK': '海爾智家', '6806.HK': '申萬宏源', 
    '6837.HK': '海通證券', '6862.HK': '海底撈', '6865.HK': '福萊特玻璃', '6881.HK': '中國銀河', '6969.HK': '思摩爾國際',
    '9618.HK': '京東集團-SW', '9633.HK': '農夫山泉', '9866.HK': '蔚來-SW', '9868.HK': '小鵬汽車-W', '9888.HK': '百度集團-SW', 
    '9922.HK': '九毛九', '9959.HK': '聯易融科技-W', '9988.HK': '阿里巴巴-SW', '9992.HK': '泡泡瑪特', '9999.HK': '網易-S'
}

print(f"⏳ 1/4 啟動下載 Agent 獲取大數據 (涵蓋近 5 年區間)...")

hsi_df = yf.download(["2800.HK", "^HSI", "^VIX"], start=START_DATE, end=END_DATE, progress=False, threads=True) 
hsi_c = hsi_df['Close']['2800.HK'].ffill()
if hsi_c.isna().all(): hsi_c = hsi_df['Close']['^HSI'].ffill()
vix_c = hsi_df['Close']['^VIX'].ffill()

def secured_download_agent(tickers, period_start, period_end):
    prices_dict = {'High': {}, 'Low': {}, 'Close': {}, 'Volume': {}}
    for i in range(0, len(tickers), 30):
        batch = tickers[i:i + 30]
        data = yf.download(batch, start=period_start, end=period_end, progress=False, threads=True, group_by='ticker')
        for ticker in batch:
            try:
                df_t = data if len(batch) == 1 else data[ticker]
                if not df_t.empty and not df_t.isna().all().all():
                    prices_dict['High'][ticker] = df_t['High']
                    prices_dict['Low'][ticker] = df_t['Low']
                    prices_dict['Close'][ticker] = df_t['Close']
                    prices_dict['Volume'][ticker] = df_t['Volume']
            except Exception: pass
        time.sleep(0.5)
    return (pd.DataFrame(prices_dict['High']).ffill(),
            pd.DataFrame(prices_dict['Low']).ffill(),
            pd.DataFrame(prices_dict['Close']).ffill(),
            pd.DataFrame(prices_dict['Volume']).fillna(0))

highs, lows, closes, volumes = secured_download_agent(WATCHLIST, START_DATE, END_DATE)

# 修復日期錯亂
valid_idx = closes.index.drop_duplicates(keep='first').sort_values()
highs = highs.reindex(valid_idx)
lows = lows.reindex(valid_idx)
closes = closes.reindex(valid_idx)
volumes = volumes.reindex(valid_idx)

hsi_c = hsi_c.reindex(closes.index).ffill()
vix_c = vix_c.reindex(closes.index).ffill()

print("⏳ 2/4 計算技術指標、大盤狀態與防護網...")

hsi_200ma = hsi_c.rolling(200).mean()
sma50_all = closes.rolling(50).mean()
breadth_pct = ((closes > sma50_all).sum(axis=1) / closes.notna().sum(axis=1)) * 100
breadth_pct = breadth_pct.fillna(0)

sma20_all = closes.rolling(20).mean()
std20_all = closes.rolling(20).std()
lower_bb_all = sma20_all - (2 * std20_all)
donchian_high_all = highs.rolling(20).max().shift(1)
high_250 = highs.rolling(250).max()
stock_200ma = closes.rolling(200).mean()

delta = closes.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss.replace(0, np.nan)
rsi_all = 100 - (100 / (1 + rs))

returns = closes.pct_change()
volatility_60d = returns.rolling(60).std() * np.sqrt(252)

fin_cache = {}
def get_fundamentals(ticker):
    if ticker in fin_cache: return fin_cache[ticker]
    try:
        tk_info = yf.Ticker(ticker).info
        raw_div = tk_info.get('dividendYield') or tk_info.get('trailingAnnualDividendYield') or 0
        div = round(raw_div, 2) if raw_div > 1 else round(raw_div * 100, 2)
        earn_growth = tk_info.get('earningsGrowth') or tk_info.get('revenueGrowth') or 0
        earn_pct = round(earn_growth * 100, 2)
        
        if earn_pct >= 15: earn_label = f"強勁 (+{earn_pct}%)"
        elif earn_pct > 0: earn_label = f"復甦 (+{earn_pct}%)"
        elif earn_pct < 0: earn_label = f"衰退 ({earn_pct}%)"
        else: earn_label = "無"
        
        pe = round(tk_info.get('trailingPE'), 2) if tk_info.get('trailingPE') else "N/A"
        pb = round(tk_info.get('priceToBook'), 2) if tk_info.get('priceToBook') else "N/A"
        roe = round(tk_info.get('returnOnEquity') * 100, 2) if tk_info.get('returnOnEquity') else "N/A"
        
        fin_cache[ticker] = {"div": div, "earn_growth_val": earn_pct, "earn_label": earn_label, "pe": pe, "pb": pb, "roe": roe}
    except:
        fin_cache[ticker] = {"div": 0, "earn_growth_val": 0, "earn_label": "無", "pe": "N/A", "pb": "N/A", "roe": "N/A"}
    return fin_cache[ticker]

def safe_list(series):
    return [None if pd.isna(x) else round(float(x), 2) for x in series.tolist()]

def clean_nans(obj):
    if isinstance(obj, dict): return {k: clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list): return [clean_nans(v) for v in obj]
    if isinstance(obj, float):
        if pd.isna(obj) or math.isnan(obj) or np.isnan(obj) or np.isinf(obj): return None
    return obj

print("⏳ 3/4 啟動 5年期 雙引擎動態回溯 (套用 V6.8 終極濾網與 20天強制出場)...")

lookback_bars = 252 * 5 
start_idx = len(closes) - lookback_bars
if start_idx < 250: start_idx = 250 

active_trades = {}
completed_trades = []
pnl_history = []

for i in tqdm(range(start_idx, len(closes)), desc="回測進度"):
    current_date = closes.index[i]
    date_str = current_date.strftime('%Y-%m-%d')

    cur_hsi = hsi_c.iloc[i]
    cur_hsi_200 = hsi_200ma.iloc[i]
    if pd.isna(cur_hsi) or pd.isna(cur_hsi_200): continue
    is_bull = cur_hsi > cur_hsi_200
    
    cur_breadth = breadth_pct.iloc[i]
    cur_vix = vix_c.iloc[i] if not pd.isna(vix_c.iloc[i]) else 18.0

    tickers_to_remove = []
    
    for ticker, trade in active_trades.items():
        trade['Bars_Held'] += 1
        h = highs[ticker].iloc[i]
        l = lows[ticker].iloc[i]
        c = closes[ticker].iloc[i]
        cur_ma20 = sma20_all[ticker].iloc[i]
        
        if pd.isna(h) or pd.isna(l) or pd.isna(c): continue
            
        is_closed = False
        
        if h >= trade['TP']:
            trade['Exit_Date'] = date_str
            trade['Exit_Idx'] = i
            trade['Exit_Price'] = trade['TP']
            trade['Status'] = 'Win'
            trade['Exit_Reason'] = 'TP'
            trade['PnL_%'] = round(((trade['TP'] - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
            trade['Hold_Days'] = (current_date - pd.to_datetime(trade['Entry_Date'])).days
            completed_trades.append(trade)
            pnl_history.append({"Date": date_str, "Type": trade['Type'], "PnL": trade['PnL_%']})
            tickers_to_remove.append(ticker)
            is_closed = True
            continue
            
        if trade['Type'] == "海龜突破 (順勢)":
            if trade.get('Pool') == "動能池":
                if not pd.isna(cur_ma20) and c < cur_ma20:
                    trade['Exit_Date'] = date_str
                    trade['Exit_Idx'] = i
                    trade['Exit_Price'] = c
                    trade['Status'] = 'Loss'
                    trade['Exit_Reason'] = 'MA20_SL'
                    trade['PnL_%'] = round(((c - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                    trade['Hold_Days'] = (current_date - pd.to_datetime(trade['Entry_Date'])).days
                    completed_trades.append(trade)
                    pnl_history.append({"Date": date_str, "Type": trade['Type'], "PnL": trade['PnL_%']})
                    tickers_to_remove.append(ticker)
                    is_closed = True
                elif l <= trade['SL']:
                    trade['Exit_Date'] = date_str
                    trade['Exit_Idx'] = i
                    trade['Exit_Price'] = trade['SL']
                    trade['Status'] = 'Loss'
                    trade['Exit_Reason'] = 'SL'
                    trade['PnL_%'] = round(((trade['SL'] - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                    trade['Hold_Days'] = (current_date - pd.to_datetime(trade['Entry_Date'])).days
                    completed_trades.append(trade)
                    pnl_history.append({"Date": date_str, "Type": trade['Type'], "PnL": trade['PnL_%']})
                    tickers_to_remove.append(ticker)
                    is_closed = True
            else:
                if l <= trade['SL']:
                    trade['Exit_Date'] = date_str
                    trade['Exit_Idx'] = i
                    trade['Exit_Price'] = trade['SL']
                    trade['Status'] = 'Loss'
                    trade['Exit_Reason'] = 'SL'
                    trade['PnL_%'] = round(((trade['SL'] - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                    trade['Hold_Days'] = (current_date - pd.to_datetime(trade['Entry_Date'])).days
                    completed_trades.append(trade)
                    pnl_history.append({"Date": date_str, "Type": trade['Type'], "PnL": trade['PnL_%']})
                    tickers_to_remove.append(ticker)
                    is_closed = True
                    
        elif trade['Type'] == "RSI 超跌抄底 (逆勢)":
            if l <= trade['SL']:
                trade['Exit_Date'] = date_str
                trade['Exit_Idx'] = i
                trade['Exit_Price'] = trade['SL']
                trade['Status'] = 'Loss'
                trade['Exit_Reason'] = 'SL'
                trade['PnL_%'] = round(((trade['SL'] - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                trade['Hold_Days'] = (current_date - pd.to_datetime(trade['Entry_Date'])).days
                completed_trades.append(trade)
                pnl_history.append({"Date": date_str, "Type": trade['Type'], "PnL": trade['PnL_%']})
                tickers_to_remove.append(ticker)
                is_closed = True
            elif not is_closed and trade['Bars_Held'] >= 10 and c <= trade['Entry_Price']:
                trade['Exit_Date'] = date_str
                trade['Exit_Idx'] = i
                trade['Exit_Price'] = c
                trade['Status'] = 'Loss'
                trade['Exit_Reason'] = 'Time_SL'
                trade['PnL_%'] = round(((c - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                trade['Hold_Days'] = (current_date - pd.to_datetime(trade['Entry_Date'])).days
                completed_trades.append(trade)
                pnl_history.append({"Date": date_str, "Type": trade['Type'], "PnL": trade['PnL_%']})
                tickers_to_remove.append(ticker)
                is_closed = True
            elif not is_closed and trade['Bars_Held'] >= 20:
                trade['Exit_Date'] = date_str
                trade['Exit_Idx'] = i
                trade['Exit_Price'] = c
                trade['Status'] = 'Win' if c > trade['Entry_Price'] else 'Loss'
                trade['Exit_Reason'] = 'Max_Hold'
                trade['PnL_%'] = round(((c - trade['Entry_Price']) / trade['Entry_Price']) * 100, 2)
                trade['Hold_Days'] = (current_date - pd.to_datetime(trade['Entry_Date'])).days
                completed_trades.append(trade)
                pnl_history.append({"Date": date_str, "Type": trade['Type'], "PnL": trade['PnL_%']})
                tickers_to_remove.append(ticker)

    for ticker in tickers_to_remove:
        del active_trades[ticker]

    if cur_breadth > 60: continue 

    for ticker in closes.columns:
        if ticker in active_trades: continue
        c = closes[ticker].iloc[i]
        
        if pd.isna(c) or c < 3.0: continue

        signal_type = None
        trade_pool = "-"
        sl_price = 0
        tp_price = 0

        cur_vol = volatility_60d[ticker].iloc[i]
        if pd.isna(cur_vol): cur_vol = 0.50

        if is_bull:
            if cur_vix < 15 and cur_breadth >= 40:
                dh = donchian_high_all[ticker].iloc[i]
                c_200ma = stock_200ma[ticker].iloc[i]
                if not pd.isna(dh) and c > dh and not pd.isna(c_200ma) and c > c_200ma:
                    fin = get_fundamentals(ticker)
                    if fin['earn_growth_val'] >= 0:
                        signal_type = "海龜突破 (順勢)"
                        trade_pool = "震盪池" if cur_vol < 0.35 else "動能池"
                        sl_price = c * 0.90 if trade_pool == "震盪池" else c * 0.85 
                        tp_price = c * 1.30
        else:
            if cur_vix <= 35:
                rsi_val = rsi_all[ticker].iloc[i]
                lbb = lower_bb_all[ticker].iloc[i]
                c_h250 = high_250[ticker].iloc[i]
                c_200ma = stock_200ma[ticker].iloc[i]
                
                # V6.8 RSI 濾網
                if not pd.isna(rsi_val) and not pd.isna(lbb) and not pd.isna(c_h250) and not pd.isna(c_200ma):
                    if rsi_val < 18 and c < lbb and c > (c_h250 * 0.40):
                        bias_200 = (c - c_200ma) / c_200ma
                        if bias_200 > -0.20:
                            fin = get_fundamentals(ticker)
                            if fin['earn_growth_val'] >= 0:
                                signal_type = "RSI 超跌抄底 (逆勢)"
                                trade_pool = "逆勢池"
                                sl_price = c * 0.88
                                tp_price = c * 1.20

        if signal_type:
            active_trades[ticker] = {
                "Trade_ID": f"{ticker}_{date_str}",
                "Ticker": ticker,
                "Stock_Name": HK_STOCK_NAMES.get(ticker, ""),
                "TV_Ticker": f"HKEX:{int(ticker.split('.')[0])}" if ticker.split('.')[0].isdigit() else ticker,
                "Type": signal_type,
                "Pool": trade_pool,
                "Entry_Date": date_str,
                "Entry_Idx": i,
                "Entry_Price": round(c, 2),
                "Entry_VIX": round(cur_vix, 2),
                "SL": round(sl_price, 2),
                "TP": round(tp_price, 2),
                "Status": "Active",
                "Exit_Reason": "-",
                "Exit_Date": "-",
                "Hold_Days": 0,
                "Bars_Held": 0,
                "RSI": round(rsi_all[ticker].iloc[i], 1),
                "PnL_%": 0.0
            }

all_5y_trades = completed_trades + list(active_trades.values())
all_5y_trades.sort(key=lambda x: x['Entry_Date'], reverse=True)

# 準備 PnL 圖表資料
pnl_df = pd.DataFrame(pnl_history)
pnl_json = {"dates": [], "total": [], "turtle": [], "rsi": []}

if not pnl_df.empty:
    pnl_df['Date'] = pd.to_datetime(pnl_df['Date'])
    pnl_df = pnl_df.sort_values('Date').reset_index(drop=True)
    pnl_df['Cum_Total'] = pnl_df['PnL'].cumsum()
    
    t_df = pnl_df[pnl_df['Type'] == '海龜突破 (順勢)'].copy()
    t_df['Cum_Turtle'] = t_df['PnL'].cumsum()
    
    r_df = pnl_df[pnl_df['Type'] == 'RSI 超跌抄底 (逆勢)'].copy()
    r_df['Cum_RSI'] = r_df['PnL'].cumsum()
    
    unique_dates = sorted(pnl_df['Date'].unique())
    dates_str = [d.strftime('%Y-%m-%d') for d in unique_dates]
    
    curr_t = 0
    curr_r = 0
    for d in unique_dates:
        t_match = t_df[t_df['Date'] <= d]
        if not t_match.empty: curr_t = t_match.iloc[-1]['Cum_Turtle']
        
        r_match = r_df[r_df['Date'] <= d]
        if not r_match.empty: curr_r = r_match.iloc[-1]['Cum_RSI']
        
        pnl_json["turtle"].append(round(curr_t, 2))
        pnl_json["rsi"].append(round(curr_r, 2))
        
    pnl_json["dates"] = dates_str
    
    pnl_by_date = pnl_df.groupby('Date')['PnL'].sum().cumsum()
    pnl_json["total"] = [round(pnl_by_date[d], 2) for d in unique_dates]

today_dt = datetime.datetime.now()
for t in all_5y_trades:
    fin = get_fundamentals(t['Ticker'])
    t['div_yield'] = fin['div']
    t['earn_label'] = fin['earn_label']
    t['pe_ratio'] = fin['pe']
    t['pb_ratio'] = fin['pb']
    t['roe'] = fin['roe']
    t['financial_data'] = f"股息: {fin['div']}% | 動能: {fin['earn_label']}<br>P/E: {fin['pe']} | P/B: {fin['pb']} | ROE: {fin['roe']}%"
    t['current_price'] = round(float(closes[t['Ticker']].iloc[-1]), 2)
    if t['Status'] == 'Active':
        t['Hold_Days'] = (today_dt - pd.to_datetime(t['Entry_Date'])).days
        
    entry_idx = t['Entry_Idx']
    exit_idx_to_use = t['Exit_Idx'] if t['Status'] != 'Active' else len(closes) - 1
    
    start_chart_idx = max(0, entry_idx - 375)
    end_chart_idx = min(len(closes), exit_idx_to_use + 40)
    if t['Status'] == 'Active': end_chart_idx = len(closes)
    if end_chart_idx - start_chart_idx < 375: start_chart_idx = max(0, end_chart_idx - 375)
    
    ticker = t['Ticker']
    t['chart_dates'] = closes.index[start_chart_idx:end_chart_idx].strftime('%Y-%m-%d').tolist()
    t['chart_prices'] = safe_list(closes[ticker].iloc[start_chart_idx:end_chart_idx])
    t['chart_sma20'] = safe_list(sma20_all[ticker].iloc[start_chart_idx:end_chart_idx])
    t['chart_lbb'] = safe_list(lower_bb_all[ticker].iloc[start_chart_idx:end_chart_idx])

recent_signals = [t for t in all_5y_trades if t['Status'] == 'Active' and t['Bars_Held'] <= 10]

# ==============================================================================
# HTML 渲染與策略獨立計算
# ==============================================================================
html_5y_rows = ""

stats = {
    "Turtle": {"closed": 0, "wins": 0, "time_sl": 0, "ma20_sl": 0, "sl": 0, "max_hold": 0, "compounded": 1.0},
    "RSI": {"closed": 0, "wins": 0, "time_sl": 0, "ma20_sl": 0, "sl": 0, "max_hold": 0, "compounded": 1.0}
}
global_counters = {"TP": 0, "MA20_SL": 0, "Time_SL": 0, "Max_Hold": 0, "Hard_SL": 0, "Active": 0}

for row in all_5y_trades:
    is_turtle = "海龜" in row['Type']
    strat_key = "Turtle" if is_turtle else "RSI"
    type_color = "text-green-400" if is_turtle else "text-red-400"
    
    pool_badge = f"<br><span class='text-[10px] px-1.5 py-0.5 rounded bg-slate-700 text-slate-300'>{row.get('Pool', '-')}</span>"
    type_display = f"<span class='{type_color}'>{row['Type']}</span>{pool_badge}"

    exit_date_str = ""
    pnl_str = "-"
    
    if row['Status'] in ['Win', 'Loss']:
        exit_date_str = f"<br><span class='text-[10px] text-slate-400'>於 {row['Exit_Date']} 結算</span>"
        pnl_val = row['PnL_%']
        pnl_color = "text-green-400" if pnl_val > 0 else "text-red-400"
        sign = "+" if pnl_val > 0 else ""
        pnl_str = f"<span class='{pnl_color} font-bold'>{sign}{pnl_val:.2f}%</span>"
        
        stats[strat_key]['closed'] += 1
        stats[strat_key]['compounded'] *= (1 + (pnl_val / 100))
        
        if row['Exit_Reason'] == 'TP': 
            stats[strat_key]['wins'] += 1
            global_counters["TP"] += 1
        elif row['Exit_Reason'] == 'MA20_SL':
            stats[strat_key]['ma20_sl'] += 1
            global_counters["MA20_SL"] += 1
        elif row['Exit_Reason'] == 'Time_SL':
            stats[strat_key]['time_sl'] += 1
            global_counters["Time_SL"] += 1
        elif row['Exit_Reason'] == 'Max_Hold':
            stats[strat_key]['max_hold'] += 1
            global_counters["Max_Hold"] += 1
        elif row['Exit_Reason'] == 'SL':
            stats[strat_key]['sl'] += 1
            global_counters["Hard_SL"] += 1
            
        hold_str = f"{row['Hold_Days']}天"
        
    else:
        unrealized_pnl = ((row['current_price'] - row['Entry_Price']) / row['Entry_Price']) * 100
        pnl_color = "text-green-400" if unrealized_pnl > 0 else "text-red-400"
        sign = "+" if unrealized_pnl > 0 else ""
        pnl_str = f"<span class='{pnl_color} text-xs'>浮動 {sign}{unrealized_pnl:.2f}%</span>"
        hold_str = f"<span class='text-yellow-400 font-bold'>{row['Hold_Days']}天</span>"
        global_counters["Active"] += 1

    if row['Exit_Reason'] == 'TP':
        status_badge = f'<span class="px-2 py-1 bg-green-900/50 text-green-400 border border-green-700 rounded text-xs font-bold">Win</span>{exit_date_str}'
    elif row['Exit_Reason'] == 'Max_Hold':
        clr = "green" if row['Status'] == 'Win' else "red"
        status_badge = f'<span class="px-2 py-1 bg-{clr}-900/50 text-{clr}-400 border border-{clr}-700 rounded text-xs font-bold" title="達到最大持有天數">20D Exit</span>{exit_date_str}'
    elif row['Status'] == 'Loss':
        if row.get('Exit_Reason') == 'Time_SL':
            status_badge = f'<span class="px-2 py-1 bg-orange-900/50 text-orange-400 border border-orange-700 rounded text-xs font-bold" title="10日未獲利停損">Time SL</span>{exit_date_str}'
        elif row.get('Exit_Reason') == 'MA20_SL':
            status_badge = f'<span class="px-2 py-1 bg-purple-900/50 text-purple-400 border border-purple-700 rounded text-xs font-bold" title="跌破 MA20 動態停損">MA20 SL</span>{exit_date_str}'
        else:
            status_badge = f'<span class="px-2 py-1 bg-red-900/50 text-red-400 border border-red-700 rounded text-xs font-bold">Loss</span>{exit_date_str}'
    else:
        status_badge = '<span class="px-2 py-1 bg-yellow-900/50 text-yellow-400 border border-yellow-700 rounded text-xs font-bold animate-pulse">Active</span>'

    curr_p_color = "text-green-400 font-bold" if row['current_price'] > row['Entry_Price'] else "text-red-400 font-bold" if row['current_price'] < row['Entry_Price'] else "text-slate-300"

    html_5y_rows += f"""
        <tr class="trade-row border-b border-slate-800 hover:bg-slate-700/50 transition cursor-pointer" 
            data-trade-id="{row['Trade_ID']}" 
            onclick="selectRow(this); loadChart('{row['Trade_ID']}', 'myChart5y')">
            <td class="p-3 text-blue-300 font-bold">{row['Entry_Date']}</td>
            <td class="p-3 font-bold text-white">{row['Ticker']}<br><span class="text-xs text-slate-400 font-normal">{row['Stock_Name']}</span></td>
            <td class="p-3 text-sm">{type_display}</td>
            <td class="p-3 text-right font-bold text-slate-300">{row['Entry_VIX']}</td>
            <td class="p-3 text-xs text-slate-400 leading-relaxed">{row['financial_data']}</td>
            <td class="p-3 text-right">${row['Entry_Price']}</td>
            <td class="p-3 text-xs text-right">
                <span class="text-red-400">SL: ${row['SL']}</span><br>
                <span class="text-green-400">TP: ${row['TP']}</span>
            </td>
            <td class="p-3 text-right {curr_p_color}">${row['current_price']}</td>
            <td class="p-3 text-center">{hold_str}</td>
            <td class="p-3 text-right bg-slate-900/30" data-pnl="{row['PnL_%'] if row['Status'] != 'Active' else unrealized_pnl}">{pnl_str}</td>
            <td class="p-3 text-center leading-tight status-col">{status_badge}</td>
        </tr>
    """

if not html_5y_rows: html_5y_rows = '<tr><td colspan="11" class="p-4 text-center text-slate-500">近 5 年尚無觸發紀錄。請留意濾網設定可能過於嚴格。</td></tr>'

t_closed = stats['Turtle']['closed']
t_win_rate = (stats['Turtle']['wins'] / t_closed * 100) if t_closed else 0
t_ma20_rate = (stats['Turtle']['ma20_sl'] / t_closed * 100) if t_closed else 0
t_time_rate = (stats['Turtle']['time_sl'] / t_closed * 100) if t_closed else 0
t_sl_rate = (stats['Turtle']['sl'] / t_closed * 100) if t_closed else 0
turtle_pnl = (stats['Turtle']['compounded'] - 1) * 100

r_closed = stats['RSI']['closed']
r_win_rate = (stats['RSI']['wins'] / r_closed * 100) if r_closed else 0
r_time_rate = (stats['RSI']['time_sl'] / r_closed * 100) if r_closed else 0
r_max_hold_rate = (stats['RSI']['max_hold'] / r_closed * 100) if r_closed else 0
r_sl_rate = (stats['RSI']['sl'] / r_closed * 100) if r_closed else 0
rsi_pnl = (stats['RSI']['compounded'] - 1) * 100

is_bull_market = (hsi_c.iloc[-1] > hsi_200ma.iloc[-1]) if len(hsi_c) > 0 else False

print("⏳ 4/4 正在生成 Dashboard HTML (轉換防呆 JSON)...")
all_chart_data = clean_nans(all_5y_trades)
json_str = json.dumps(all_chart_data, ensure_ascii=False).replace('</', '<\\/')
pnl_json_str = json.dumps(pnl_json, ensure_ascii=False)

html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <title>HK Quant Master V6.95 - 每日一篇教66歲丫媽學投資</title>
    <style>
        body {{ background-color: #0f172a; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        .card {{ background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }}
        .bull-text {{ color: #10b981; }}
        .bear-text {{ color: #ef4444; }}
        .info-badge {{ font-size: 0.70rem; padding: 4px 6px; border-radius: 6px; background: rgba(30, 41, 59, 0.8); border: 1px solid #475569; text-align: center; }}
        .tab-btn {{ transition: all 0.3s ease; }}
        .tab-active {{ background-color: #2563eb; color: white; border-bottom: 2px solid #60a5fa; }}
        .tab-inactive {{ background-color: transparent; color: #94a3b8; border-bottom: 2px solid transparent; hover:text-white; }}
        th.sortable:hover {{ color: #ffffff; background-color: #334155; cursor: pointer; }}
        .row-selected {{ background-color: rgba(59, 130, 246, 0.2) !important; border-left: 4px solid #3b82f6; }}
    </style>
</head>
<body class="p-4">
    <div class="max-w-6xl mx-auto w-full">

        <a href="https://www.threads.com/@teachthe66yearsoldmominvest" target="_blank" class="block w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white text-center py-3 rounded-lg font-bold mb-4 shadow-lg hover:from-purple-500 hover:to-blue-500 transition text-lg tracking-wide">
            ✨ 追蹤【每日一篇教66歲丫媽學投資】Threads 帳號 (@teachthe66yearsoldmominvest)，學習更多簡單實用的投資策略！ ✨
        </a>

        <div class="card p-6 mb-6 flex flex-col md:flex-row justify-between items-center shadow-lg border-b-4 border-blue-500">
              <div>
                <h1 class="text-3xl font-black text-white mb-2">HK Quant Master V6.95 <span class="text-blue-500">終極全功能版</span></h1>
                <p class="text-slate-400 text-sm">支援上下左右鍵快速切圖 | 5年系統資金曲線 | 20天強制防死魚 | RSI 神級濾網</p>
                    <div class="mt-3 flex items-center space-x-2">
                    <span class="text-xs text-slate-500 font-bold">累積瀏覽次數：</span>
                    <img src="https://visitor-badge.laobi.icu/badge?page_id=hk-quant-master-YOURNAME" alt="visitors">
                </div>
            </div>
            <div class="mt-4 md:mt-0 text-right bg-slate-900 p-4 rounded-lg border border-slate-700">
                <p class="text-xs text-slate-400 mb-1">大盤狀態</p>
                <div class="text-xl font-bold {'bull-text' if is_bull_market else 'bear-text'}">{"🟢 牛市狀態" if is_bull_market else "🔴 熊市/震盪狀態"}</div>
                <div class="text-sm mt-2 text-slate-300">目前解鎖引擎：<span class="font-bold text-yellow-400">{"Donchian Turtle (海龜突破)" if is_bull_market else "RSI Reversion (抄底)"}</span></div>
            </div>
        </div>

        <div class="flex border-b border-slate-700 mb-6 space-x-2">
            <button onclick="switchTab('tab-scan')" id="btn-scan" class="tab-btn tab-active px-6 py-3 font-bold rounded-t-lg">📊 活躍標的 (10日內)</button>
            <button onclick="switchTab('tab-5y')" id="btn-5y" class="tab-btn tab-inactive px-6 py-3 font-bold rounded-t-lg">💯 歷史覆盤與單線圖</button>
            <button onclick="switchTab('tab-pnl')" id="btn-pnl" class="tab-btn tab-inactive px-6 py-3 font-bold rounded-t-lg text-yellow-400">📈 5年系統資金曲線</button>
            <button onclick="switchTab('tab-manual')" id="btn-manual" class="tab-btn tab-inactive px-6 py-3 font-bold rounded-t-lg">📖 系統說明書</button>
        </div>

        <div id="tab-scan" class="tab-content block">
            <div class="flex flex-col lg:flex-row gap-6">
                <div class="lg:w-2/5 flex flex-col gap-4">
                    <h2 class="text-xl font-bold border-b border-slate-700 pb-2">🎯 10日內觸發且仍在持倉 ({len(recent_signals)})</h2>
"""

if not recent_signals:
    html_content += f"""
                    <div class="card p-6 text-center text-slate-500">
                        <p class="text-4xl mb-2">🛡️</p>
                        <p>過去 10 天內無新觸發或持倉標的。</p>
                        <p class="text-xs mt-2 text-slate-400">系統已開啟「衰退股剔除」、「低價股剔除」與「VIX 限制」，寧願空手，絕不接刀。</p>
                    </div>
"""
else:
    for sig in recent_signals:
        badge_color = "bg-green-900/50 text-green-400 border-green-700" if "海龜" in sig['Type'] else "bg-red-900/50 text-red-400 border-red-700"
        day_text = f"⚡ 已持倉 {sig['Bars_Held']} 個交易日"
        day_color = "text-yellow-400"
        div_color = "text-green-400 font-black" if sig['div_yield'] >= 6 else "text-slate-300"
        earn_color = "text-green-400" if "+" in sig['earn_label'] else "text-red-400" if "衰退" in sig['earn_label'] else "text-slate-400"

        html_content += f"""
                    <div class="card p-4 cursor-pointer hover:bg-slate-700 transition shadow" onclick="loadChart('{sig['Trade_ID']}', 'myChartScan')">
                        <div class="flex justify-between items-center mb-2">
                            <div class="text-2xl font-black text-white">{sig['Ticker']} <span class="text-lg text-slate-300 ml-1">{sig['Stock_Name']}</span></div>
                            <div class="text-xs px-2 py-1 rounded border {badge_color} whitespace-nowrap ml-2">{sig['Type']} [{sig['Pool']}]</div>
                        </div>
                        <div class="text-xs font-bold {day_color} mb-3 border-b border-slate-700 pb-2">
                            {day_text} | 進場 RSI: {sig['RSI']} | 進場日: {sig['Entry_Date']}
                        </div>
                        <div class="grid grid-cols-3 gap-2 text-center bg-slate-900 p-2 rounded border border-slate-700">
                            <div><div class="text-[10px] text-slate-500">進場價</div><div class="font-bold text-white">${sig['Entry_Price']}</div></div>
                            <div><div class="text-[10px] text-red-400">防守底線</div><div class="font-bold text-red-400">${sig['SL']}</div></div>
                            <div><div class="text-[10px] text-green-400">目標止盈</div><div class="font-bold text-green-400">${sig['TP']}</div></div>
                        </div>
                    </div>
"""

html_content += f"""
                </div>
                <div class="lg:w-3/5 flex flex-col">
                    <div class="card p-4 mb-4 flex justify-between items-center bg-gradient-to-r from-slate-800 to-slate-900">
                        <h3 id="chart_title_scan" class="text-xl font-bold text-white">圖表預覽</h3>
                        <a id="tv_link_scan" href="#" target="_blank" class="hidden bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold py-2 px-4 rounded transition shadow">
                            📊 在 TradingView 開啟
                        </a>
                    </div>
                    <div class="card p-4 h-[400px] w-full relative bg-[#0f172a] shadow-inner mb-4">
                        <canvas id="myChartScan" class="w-full h-full relative z-20"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-5y" class="tab-content hidden">
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div class="card p-4 border-l-4 border-green-500 shadow relative">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-lg font-bold text-white">🐢 海龜突破 (順勢)</h3>
                        <div class="text-right">
                            <span class="text-slate-400 block text-xs">累積淨損益 (複利)</span>
                            <span class="font-black text-xl {'text-green-400' if turtle_pnl >= 0 else 'text-red-400'}">{'+' if turtle_pnl > 0 else ''}{turtle_pnl:.2f}%</span>
                        </div>
                    </div>
                    <div class="text-sm text-slate-400">近 5 年總平倉數: <span class="text-white font-bold">{t_closed}</span> 筆</div>
                    
                    <div class="grid grid-cols-4 gap-2 text-center text-xs mt-3 border-t border-slate-700 pt-3">
                        <div><span class="text-slate-400 block mb-1">達標 (Win)</span><span class="font-bold text-green-400">{t_win_rate:.1f}%</span></div>
                        <div><span class="text-slate-400 block mb-1">MA20 停損</span><span class="font-bold text-purple-400">{t_ma20_rate:.1f}%</span></div>
                        <div><span class="text-slate-400 block mb-1">20天極限</span><span class="font-bold text-orange-400">{t_time_rate:.1f}%</span></div>
                        <div><span class="text-slate-400 block mb-1">硬止損 (Lose)</span><span class="font-bold text-red-400">{t_sl_rate:.1f}%</span></div>
                    </div>
                </div>
                
                <div class="card p-4 border-l-4 border-red-500 shadow relative">
                    <div class="flex justify-between items-start mb-2">
                        <h3 class="text-lg font-bold text-white">📉 RSI 抄底 (V6.8 終極版)</h3>
                        <div class="text-right">
                            <span class="text-slate-400 block text-xs">累積淨損益 (複利)</span>
                            <span class="font-black text-xl {'text-green-400' if rsi_pnl >= 0 else 'text-red-400'}">{'+' if rsi_pnl > 0 else ''}{rsi_pnl:.2f}%</span>
                        </div>
                    </div>
                    <div class="text-sm text-slate-400">近 5 年總平倉數: <span class="text-white font-bold">{r_closed}</span> 筆</div>
                    
                    <div class="grid grid-cols-4 gap-2 text-center text-xs mt-3 border-t border-slate-700 pt-3">
                        <div><span class="text-slate-400 block mb-1">達標 (Win)</span><span class="font-bold text-green-400">{r_win_rate:.1f}%</span></div>
                        <div><span class="text-slate-400 block mb-1">10天未發動</span><span class="font-bold text-orange-400">{r_time_rate:.1f}%</span></div>
                        <div><span class="text-slate-400 block mb-1">20天極限</span><span class="font-bold text-yellow-400">{r_max_hold_rate:.1f}%</span></div>
                        <div><span class="text-slate-400 block mb-1">硬止損 (Lose)</span><span class="font-bold text-red-400">{r_sl_rate:.1f}%</span></div>
                    </div>
                </div>
            </div>

            <div class="sticky top-0 z-40 bg-[#0f172a] pt-2 pb-4 border-b border-slate-700 shadow-2xl mb-6">
                <div class="card p-4 flex flex-col border-t-4 border-blue-500 relative">
                    <div class="flex justify-between items-center mb-2">
                        <h3 id="chart_title_5y" class="text-lg font-bold text-white">請點擊下方表格，並使用 <span class="text-yellow-400 bg-slate-800 px-2 rounded">↑</span> <span class="text-yellow-400 bg-slate-800 px-2 rounded">↓</span> 鍵極速切換圖表</h3>
                        <a id="tv_link_5y" href="#" target="_blank" class="hidden bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold py-1 px-3 rounded transition shadow">
                            📊 完整 TradingView
                        </a>
                    </div>
                    <div class="h-[300px] w-full relative bg-[#0f172a] rounded">
                        <canvas id="myChart5y" class="w-full h-full relative z-20"></canvas>
                    </div>
                </div>
            </div>

            <div class="flex flex-wrap gap-3 mb-5 text-sm font-bold bg-slate-900 p-3 rounded-lg border border-slate-700 justify-around shadow-inner">
                <div class="px-3 py-1 bg-green-900/40 text-green-400 border border-green-700/50 rounded">🟢 TP 達標: {global_counters['TP']}</div>
                <div class="px-3 py-1 bg-purple-900/40 text-purple-400 border border-purple-700/50 rounded">🟣 MA20 斬倉: {global_counters['MA20_SL']}</div>
                <div class="px-3 py-1 bg-orange-900/40 text-orange-400 border border-orange-700/50 rounded">🟠 時間認錯: {global_counters['Time_SL']}</div>
                <div class="px-3 py-1 bg-yellow-900/40 text-yellow-400 border border-yellow-700/50 rounded">⏳ 20天到期: {global_counters['Max_Hold']}</div>
                <div class="px-3 py-1 bg-red-900/40 text-red-400 border border-red-700/50 rounded">🔴 跌破底線: {global_counters['Hard_SL']}</div>
            </div>

            <div class="mt-4 pr-2">
                <div class="flex flex-col md:flex-row justify-between items-center mb-4 gap-4">
                    <h2 class="text-xl font-bold text-blue-400">💯 近 5 年交易日追蹤表格</h2>
                    <div class="flex gap-2">
                        <select id="filterStatus" onchange="filterTable()" class="bg-slate-900 text-slate-300 p-2 border border-slate-600 rounded text-sm focus:outline-none focus:border-blue-500">
                            <option value="">所有狀態</option>
                            <option value="Win">🟢 達標 (Win)</option>
                            <option value="Loss">🔴 止損 (Loss)</option>
                            <option value="MA20 SL">🟣 MA20 停損</option>
                            <option value="Time SL">🟠 時間認錯 (Time SL)</option>
                            <option value="20D Exit">⏳ 20天極限出場</option>
                        </select>
                        <select id="filterStrategy" onchange="filterTable()" class="bg-slate-900 text-slate-300 p-2 border border-slate-600 rounded text-sm focus:outline-none focus:border-blue-500">
                            <option value="">所有策略</option>
                            <option value="順勢">🐢 海龜突破 (順勢)</option>
                            <option value="逆勢">📉 RSI 抄底 (逆勢)</option>
                        </select>
                        <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="🔍 搜尋..." class="bg-slate-900 text-white p-2 border border-slate-600 rounded text-sm w-32 focus:outline-none focus:border-blue-500">
                    </div>
                </div>

                <div class="overflow-x-auto border border-slate-700 rounded-lg">
                    <table id="logTable" class="w-full text-left border-collapse whitespace-nowrap" data-sort-dir="desc">
                        <thead class="bg-slate-800">
                            <tr class="text-slate-300 text-sm border-b border-slate-700 shadow-md">
                                <th class="p-3 sortable" onclick="sortTable(0)">進場日期 ↕</th>
                                <th class="p-3 sortable" onclick="sortTable(1)">代號與名稱 ↕</th>
                                <th class="p-3 sortable" onclick="sortTable(2)">策略與分池 ↕</th>
                                <th class="p-3 text-right sortable" onclick="sortTable(3)">進場 VIX ↕</th>
                                <th class="p-3">觸發時財務快照</th>
                                <th class="p-3 text-right sortable" onclick="sortTable(5)">進場價 ↕</th>
                                <th class="p-3 text-right">防線 / 止盈</th>
                                <th class="p-3 text-right sortable" onclick="sortTable(7)">最新/出場價 ↕</th>
                                <th class="p-3 text-center sortable" onclick="sortTable(8)">天數 ↕</th>
                                <th class="p-3 text-right sortable" onclick="sortTable(9)">實際/浮動損益 ↕</th>
                                <th class="p-3 text-center sortable" onclick="sortTable(10)">狀態 ↕</th>
                            </tr>
                        </thead>
                        <tbody class="text-sm text-slate-300" id="logTableBody">
                            {html_5y_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="tab-pnl" class="tab-content hidden">
            <div class="card p-6 border-t-4 border-yellow-400 shadow-xl">
                <h2 class="text-2xl font-bold text-white mb-2">📈 近 5 年系統累積資金曲線 (Cumulative PnL Curve)</h2>
                <p class="text-slate-400 text-sm mb-6">採用固定資金比例 (Fixed Allocation) 繪製，無複利失真，真實反映策略期望值與避震能力。</p>
                <div class="h-[500px] w-full bg-[#0f172a] rounded p-2 border border-slate-700">
                    <canvas id="pnlChart" class="w-full h-full"></canvas>
                </div>
                <div class="mt-6 bg-slate-800 p-4 rounded-lg text-sm text-slate-300 leading-relaxed">
                    <ul class="list-disc pl-5 space-y-2">
                        <li><strong class="text-blue-400">藍線 (全局系統)</strong>：雙引擎協同作戰，平穩度極高。</li>
                        <li><strong class="text-green-400">綠線 (海龜順勢)</strong>：負責在大多頭時期 (如 VIX 低於 15 且大盤站上年線) 創造極限爆發力。</li>
                        <li><strong class="text-red-400">紅線 (RSI 逆勢)</strong>：套用 V6.8 終極濾網後，徹底擺脫無止境的破底，在熊市中安穩賺取反彈。</li>
                    </ul>
                </div>
            </div>
        </div>

        <div id="tab-manual" class="tab-content hidden card p-8 leading-relaxed">
            <h2 class="text-2xl font-bold text-blue-400 mb-4 border-b border-slate-700 pb-2">📖 V6.95 系統說明書 (User Manual)</h2>
            <h3 class="text-lg font-bold text-white mt-6 mb-2">1. 鍵盤看盤與動態線圖 (V6.9 大升級)</h3>
            <p class="text-slate-300 mb-4">點擊「近 5 年結算紀錄」中的任意一筆交易，接著直接使用鍵盤的 <strong class="text-yellow-400">上下鍵 (↑ ↓) 或 左右鍵 (← →)</strong>。此時下方的表格會自動往下滾動，而上方的圖表會牢牢釘在螢幕上半部。系統會自動以單線圖展開該筆交易「前後 1.5 年」的歷史走勢，讓你如專業操盤手般極速覆盤！</p>
            <h3 class="text-lg font-bold text-white mt-6 mb-2">2. RSI 時間停損與「20天防死魚」極限</h3>
            <p class="text-slate-300 mb-4">為了解決資金閒置問題，系統導入了絕對時間極限：</p>
            <ul class="list-disc pl-6 text-slate-300 mb-4 space-y-2">
                <li><strong class="text-orange-400">第 10 天弱勢檢驗：</strong> 如果進場後第 10 天，收盤價依然低於進場價，系統認錯，以 <b>Time SL</b> 微幅虧損平倉。</li>
                <li><strong class="text-yellow-400">第 20 天絕對極限：</strong> 如果熬到了第 20 天，不管目前是賺 10% 還是賠 2%，系統直接強制收回資金 (<b>20D Exit</b>)。絕不允許逆勢抄底的股票變成一灘死水！</li>
            </ul>
        </div>

    </div>

    <script>
        let currentRowIndex = -1;

        function selectRow(rowEl) {{
            document.querySelectorAll('.trade-row').forEach(el => el.classList.remove('row-selected'));
            rowEl.classList.add('row-selected');
            const visibleRows = Array.from(document.querySelectorAll('.trade-row')).filter(el => el.style.display !== 'none');
            currentRowIndex = visibleRows.indexOf(rowEl);
        }}

        document.addEventListener('keydown', function(e) {{
            if (document.getElementById('tab-5y').classList.contains('hidden')) return;
            if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'SELECT') return;

            const visibleRows = Array.from(document.querySelectorAll('.trade-row')).filter(el => el.style.display !== 'none');
            if (visibleRows.length === 0) return;

            if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {{
                e.preventDefault(); 
                currentRowIndex = (currentRowIndex + 1) % visibleRows.length;
                let nextRow = visibleRows[currentRowIndex];
                selectRow(nextRow);
                nextRow.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                loadChart(nextRow.getAttribute('data-trade-id'), 'myChart5y');
            }} 
            else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {{
                e.preventDefault();
                currentRowIndex = (currentRowIndex - 1 + visibleRows.length) % visibleRows.length;
                let prevRow = visibleRows[currentRowIndex];
                selectRow(prevRow);
                prevRow.scrollIntoView({{ block: 'center', behavior: 'smooth' }});
                loadChart(prevRow.getAttribute('data-trade-id'), 'myChart5y');
            }}
        }});

        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => {{
                el.classList.add('hidden');
            }});
            
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('tab-active');
                btn.classList.add('tab-inactive');
            }});

            document.getElementById(tabId).classList.remove('hidden');
            document.getElementById('btn-' + tabId.split('-')[1]).classList.remove('tab-inactive');
            document.getElementById('btn-' + tabId.split('-')[1]).classList.add('tab-active');
            
            if(tabId === 'tab-pnl') renderPnLChart();
        }}

        function filterTable() {{
            currentRowIndex = -1; 
            let input = document.getElementById("searchInput").value.toUpperCase();
            let statusFilter = document.getElementById("filterStatus").value;
            let stratFilter = document.getElementById("filterStrategy").value;
            
            let tr = document.getElementById("logTableBody").getElementsByTagName("tr");
            for (let i = 0; i < tr.length; i++) {{
                let textContent = tr[i].innerText.toUpperCase();
                let rowStatus = tr[i].cells[10].innerText;
                let rowStrat = tr[i].cells[2].innerText;
                
                let matchSearch = textContent.indexOf(input) > -1;
                let matchStatus = statusFilter === "" || rowStatus.includes(statusFilter);
                let matchStrat = stratFilter === "" || rowStrat.includes(stratFilter);
                
                if (matchSearch && matchStatus && matchStrat) {{
                    tr[i].style.display = "";
                }} else {{
                    tr[i].style.display = "none";
                }}
            }}
        }}

        function sortTable(n) {{
            currentRowIndex = -1; 
            let table = document.getElementById("logTable");
            let tbody = document.getElementById("logTableBody");
            let rows = Array.from(tbody.rows);
            let asc = table.getAttribute('data-sort-dir') === 'asc';
            table.setAttribute('data-sort-dir', asc ? 'desc' : 'asc');
            
            rows.sort((r1, r2) => {{
                let val1 = r1.cells[n].innerText.replace(/[%$,+\-天浮動]/g, '').trim();
                let val2 = r2.cells[n].innerText.replace(/[%$,+\-天浮動]/g, '').trim();
                
                if (n === 9) {{
                    val1 = r1.cells[n].getAttribute('data-pnl') || "0";
                    val2 = r2.cells[n].getAttribute('data-pnl') || "0";
                }}

                let num1 = parseFloat(val1);
                let num2 = parseFloat(val2);

                if (!isNaN(num1) && !isNaN(num2)) {{
                    return asc ? num1 - num2 : num2 - num1;
                }}
                return asc ? val1.localeCompare(val2) : val2.localeCompare(val1);
            }});
            
            rows.forEach(r => tbody.appendChild(r));
        }}

        const signalsData = {json_str};
        const pnlData = {pnl_json_str};
        let chartInstanceScan = null;
        let chartInstance5y = null;
        let pnlChartInstance = null;

        function loadChart(tradeId, canvasId) {{
            try {{
                const sig = signalsData.find(s => s.Trade_ID === tradeId);
                if (!sig) return;

                let titleId = canvasId === 'myChartScan' ? 'chart_title_scan' : 'chart_title_5y';
                let tvLinkId = canvasId === 'myChartScan' ? 'tv_link_scan' : 'tv_link_5y';

                const titleEl = document.getElementById(titleId);
                if(titleEl) titleEl.innerHTML = sig.Ticker + " " + sig.Stock_Name + " <span class='text-sm text-slate-400 ml-2'>(" + sig.Type + ")</span>";
                
                const tvLink = document.getElementById(tvLinkId);
                if(tvLink) {{
                    tvLink.href = `https://www.tradingview.com/chart/?symbol=${{sig.TV_Ticker}}`;
                    tvLink.classList.remove('hidden');
                }}

                const canvas = document.getElementById(canvasId);
                const ctx = canvas.getContext('2d');

                let targetChart = canvasId === 'myChartScan' ? chartInstanceScan : chartInstance5y;
                if (targetChart) {{ targetChart.destroy(); }}

                const entryIdx = sig.chart_dates.indexOf(sig.Entry_Date);
                const exitIdxInArray = sig.Exit_Date !== "-" ? sig.chart_dates.indexOf(sig.Exit_Date) : sig.chart_dates.length - 1;
                
                const slData = sig.chart_dates.map((d, idx) => (entryIdx !== -1 && idx >= entryIdx && idx <= exitIdxInArray) ? sig.SL : null);
                const tpData = sig.chart_dates.map((d, idx) => (entryIdx !== -1 && idx >= entryIdx && idx <= exitIdxInArray) ? sig.TP : null);
                const entryData = sig.chart_dates.map((d, idx) => (idx === entryIdx) ? sig.Entry_Price : null);
                const exitData = sig.chart_dates.map((d, idx) => (idx === exitIdxInArray && sig.Status !== 'Active') ? sig.Exit_Price : null);
                
                const displayLabels = sig.chart_dates.map(d => d.substring(5));

                let newChart = new Chart(ctx, {{
                    type: 'line',
                    data: {{
                        labels: displayLabels,
                        datasets: [
                            {{
                                label: '進場點',
                                data: entryData,
                                backgroundColor: '#eab308',
                                borderColor: '#eab308',
                                pointRadius: 8,
                                pointStyle: 'triangle',
                                showLine: false,
                                order: 0
                            }},
                            {{
                                label: '出場點',
                                data: exitData,
                                backgroundColor: sig.Status === 'Win' ? '#4ade80' : '#f87171',
                                borderColor: sig.Status === 'Win' ? '#4ade80' : '#f87171',
                                pointRadius: 8,
                                pointStyle: 'crossRot',
                                showLine: false,
                                order: 1
                            }},
                            {{
                                label: '目標止盈 (TP)',
                                data: tpData,
                                borderColor: '#4ade80',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                pointRadius: 0,
                                fill: false,
                                order: 2
                            }},
                            {{
                                label: '防守底線 (SL)',
                                data: slData,
                                borderColor: '#f87171',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                pointRadius: 0,
                                fill: false,
                                order: 3
                            }},
                            {{
                                label: '收盤價',
                                data: sig.chart_prices,
                                borderColor: '#3b82f6',
                                borderWidth: 2,
                                tension: 0.1,
                                pointRadius: 0,
                                pointHitRadius: 10,
                                order: 4
                            }},
                            {{
                                label: '20日均線',
                                data: sig.chart_sma20,
                                borderColor: '#c084fc',
                                borderWidth: 1.5,
                                borderDash: [2, 2],
                                tension: 0.1,
                                pointRadius: 0,
                                order: 5
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{
                            legend: {{ labels: {{ color: '#e2e8f0' }} }},
                            tooltip: {{ mode: 'index', intersect: false }}
                        }},
                        scales: {{
                            x: {{ ticks: {{ color: '#94a3b8', maxTicksLimit: 12 }}, grid: {{ color: '#334155' }} }},
                            y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
                        }}
                    }}
                }});

                if (canvasId === 'myChartScan') chartInstanceScan = newChart;
                else chartInstance5y = newChart;

            }} catch (e) {{
                console.error("圖表載入失敗: ", e);
            }}
        }}

        function renderPnLChart() {{
            if(pnlChartInstance) return; 
            
            const ctx = document.getElementById('pnlChart').getContext('2d');
            pnlChartInstance = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: pnlData.dates,
                    datasets: [
                        {{
                            label: '全局系統 (Overall)',
                            data: pnlData.total,
                            borderColor: '#3b82f6',
                            borderWidth: 3,
                            tension: 0.1,
                            pointRadius: 0
                        }},
                        {{
                            label: '海龜突破 (順勢引擎)',
                            data: pnlData.turtle,
                            borderColor: '#4ade80',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            tension: 0.1,
                            pointRadius: 0
                        }},
                        {{
                            label: 'RSI 抄底 (逆勢引擎)',
                            data: pnlData.rsi,
                            borderColor: '#f87171',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            tension: 0.1,
                            pointRadius: 0
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#e2e8f0', font: {{ size: 14 }} }} }}
                    }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8', maxTicksLimit: 10 }}, grid: {{ color: '#334155' }} }},
                        y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});
        }}

        if (signalsData.length > 0) {{
            const recentSigs = signalsData.filter(s => s.Status === 'Active' && s.Bars_Held <= 10);
            if (recentSigs.length > 0) {{
                setTimeout(() => loadChart(recentSigs[0].Trade_ID, 'myChartScan'), 200);
            }}
            
            setTimeout(() => {{
                let firstRow = document.querySelector('#logTableBody tr');
                if(firstRow) {{
                    selectRow(firstRow);
                    loadChart(signalsData[0].Trade_ID, 'myChart5y');
                }}
            }}, 200);
        }}
    </script>
</body>
</html>
"""

filename = "index.html"
with open(filename, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"🎉 成功！生成 HK Quant Master V6.97 (表格對齊修復版)：{filename}")
try:
    from google.colab import files
    files.download(filename)
except:
    pass
