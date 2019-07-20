from sanic.response import json as res_json, HTTPResponse
from sanic.request import Request
from lib.GA import schedule
import json


async def handle_schedule(req: Request) -> HTTPResponse:
    data = json.loads(req.body.decode("utf8"))
    result = schedule(data)
    return res_json({"fulfillTime": result.fulfill_time, "result": result.row_data})
