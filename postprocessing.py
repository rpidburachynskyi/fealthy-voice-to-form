from datetime import datetime
from dateutil.relativedelta import relativedelta
import json


def process_time_response(response):
    try:
        data = json.loads(response)
        if data['time']:
            return( str({"datetime":data['time']}))
        else:
            time_obj = datetime.now()

            if data["action"] == "+":
                time_change = relativedelta(
                    years=data["years"] or 0,
                    months=data["months"] or 0,
                    days=data["days"] or 0,
                    hours=data["hours"] or 0,
                    minutes=data["minutes"] or 0
                )
                new_time = time_obj + time_change
            elif data["action"] == "-":
                time_change = relativedelta(
                    years=-(data["years"] or 0),
                    months=-(data["months"] or 0),
                    days=-(data["days"] or 0),
                    hours=-(data["hours"] or 0),
                    minutes=-(data["minutes"] or 0)
                )
                new_time = time_obj + time_change
            return str({"datetime":new_time.isoformat()})

    except Exception:
        return( str({"datetime": str(datetime.now().isoformat())}))
