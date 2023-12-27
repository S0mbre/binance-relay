from fastapi import (APIRouter, status, HTTPException, Query)
from fastapi.responses import ORJSONResponse
from typing import Optional
import traceback
from typing import List, Any

import api.crud as crud

# ================================================================================================================= #

NL = '\n'
router = APIRouter()

# ================================================================================================================= #

@router.get('/klines', response_model=List[Any], tags=['Klines'])
async def klines(symbol: str = Query(..., description='Символ'),
                 interval: Optional[str] = Query(None, description='Интервал'),
                 klines: Optional[int] = Query(None, description='Лимит')):
    try:
        res = await crud.binance_get_data(symbol, interval or 'h', klines or 7000)
        return ORJSONResponse(status_code=200, content=res)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=traceback.format_exc()
        )