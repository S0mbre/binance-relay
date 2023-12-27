from datetime import datetime, timezone, timedelta
from typing import List, Any
import httpx, logging, orjson
from pathlib import Path

# ================================================================================================================= #

ENC = 'utf-8'
BINANCE_API_URL = 'https://api.binance.com/api/v3/klines?symbol={}&interval=1{}&startTime={}&endTime={}&limit={}'
BINANCE_BASE_URL = 'https://api.binance.com/api/v3'
BINANCE_LIMIT = 1000
BINANCE_SYMBOL = 'BTCEUR'
INTERVALS = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
           'accept': 'application/json,text/*;q=0.99'}
PROXIES = None

logging.basicConfig(filename=str(Path(__file__).parent / 'log.log'), filemode='w', style='{',
                    format='[{asctime}] [{levelname}] {message}', datefmt='%d.%m.%Y %H:%M:%S',
                    encoding='utf-8', level=logging.INFO) 

# ================================================================================================================= #

def dt2epoch(dt: datetime) -> int:
    return int(dt.timestamp()) * 1000

def epoch2dt(dt: int) -> datetime:
    return datetime.fromtimestamp(dt, timezone.utc)

# ================================================================================================================= #

async def binance_get_data(symbol=BINANCE_SYMBOL, interval='h', klines=7000) -> List[Any]:
    if not interval in INTERVALS:
        raise Exception(f'Interval must be one of: {list(INTERVALS.keys())}')
    interval_ = INTERVALS[interval] 

    dt_now = datetime.now(timezone.utc)    
    chunks = []
    cycles, mod = divmod(klines, BINANCE_LIMIT)
    
    for c in range(cycles):
        dt_start_time = dt_now - timedelta(**{interval_: (klines - c * BINANCE_LIMIT)})
        dt_end_time = dt_now - timedelta(**{interval_: (klines - (c+1) * BINANCE_LIMIT - 1)})
        if dt_end_time > dt_now: dt_end_time = dt_now
        chunks.append((dt2epoch(dt_start_time), dt2epoch(dt_end_time)))

    if mod:
        dt_start_time = dt_now - timedelta(**{interval_: mod})
        chunks.append((dt2epoch(dt_start_time), dt2epoch(dt_now)))

    data = []
    logging.info(f'Getting Binance data in {len(chunks)} chunks ...')

    async with httpx.AsyncClient(headers=HEADERS, base_url=BINANCE_BASE_URL, proxies=PROXIES, verify=False) as client:
        for c in chunks:
            req = client.build_request(method='GET', url='/klines', params={'symbol': symbol, 'interval': f'1{interval}', 
                                                                            'startTime': c[0], 'endTime': c[1], 'limit': BINANCE_LIMIT})
            
            logging.info(f">>> {orjson.dumps({'url': str(req.url), 'headers': str(req.headers)}).decode(ENC)}")

            res = await client.send(req)
            if not res is None and res.is_success:
                res_text = res.text
                res_obj = res.json()       
                logging.debug(f"<<< {res.status_code}: {res_text[:64]} <...>")
                data += res_obj
            else:
                logging.debug(res)
                raise Exception(f'Bad result: {res.text if not res is None else ""}')

    return data