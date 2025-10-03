from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

from nlp.transliteration import transliterate_ukrainian_to_english

from elastic.business_search import search_businesses


def process_time_llm_response(response):
    try:
        data = json.loads(response)
        if data['time']:
            return {"datetime": data['time']}
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
            return {"datetime": new_time.isoformat()}

    except Exception:
        return {"datetime": str(datetime.now().isoformat())}


def process_business_llm_response(response):
    try:
        data = json.loads(response)
        print("Extracted business:", data["business"])
        print("data", data)
        if not data["business"]:
            return {"business_id": None}
        
        # If there is business in Ukrainian
        if data["language"] == "uk":
            data["orig_uk_to_en_transliteration"] = transliterate_ukrainian_to_english(data["business"])
            data["lemma_uk_to_en_transliteration"] = transliterate_ukrainian_to_english(data["uk_lemma"])

        filtered_data = {k: v for k, v in data.items() if k != "language" and v != ""}
        

        #TODO Clean up the function
        print("Try to search by:", set(filtered_data.values()))
        matched_businesses = search_businesses(set(filtered_data.values()))
        print("Matched businesses:", matched_businesses)
        
        # Return the matched businesses or None if no matches
        if matched_businesses:
            return {"businesses": matched_businesses}
        
        return {"business_id": None}
        
    except Exception as e:
        # TODO add logging
        print(e)
        return {"business_id": None}
