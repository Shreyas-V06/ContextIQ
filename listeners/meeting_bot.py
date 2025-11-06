from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
import requests
import json
import os

# ----------------- Setup -----------------
meeting_router = APIRouter()

RECALL_API_KEY = "a6507dd4dae4dad2007925fe53ed96f925156349"
RECALL_REGION = "us-west-2"
BASE_URL = f"https://{RECALL_REGION}.recall.ai/api/v1"

# If you have static files (like CSS, JS, etc.)
# app.mount("/static", StaticFiles(directory="static"), name="static")


# ----------------- Routes -----------------
@meeting_router.get("/", response_class=JSONResponse)
async def index(request: Request):
    """Simple root endpoint. Returns JSON instead of an HTML page."""
    return JSONResponse({
        "message": "Recall bot API",
        "endpoints": {
            "create_bot": "/start-bot (POST form: meeting_url)",
            "status_page": "/status/{bot_id} (GET)",
            "get_results": "/get-results/{bot_id} (GET)",
        },
    })


@meeting_router.post("/start-bot")
async def start_bot(meeting_url: str = Form(...)):
    """
    Step 3 in the docs: Create Bot
    Takes the meeting URL from the form and sends the bot.
    """
    if not meeting_url:
        raise HTTPException(status_code=400, detail="You forgot the meeting URL")

    headers = {
        "Authorization": RECALL_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "meeting_url": meeting_url,
        "bot_name": "My Bot",
        "recording_config": {
            "transcript": {
                "provider": {
                    "meeting_captions": {}
                }
            }
        }
    }

    try:
        response = requests.post(f"{BASE_URL}/bot", headers=headers, json=payload)
        response.raise_for_status()
        bot_id = response.json().get("id")

        if not bot_id:
            raise HTTPException(status_code=500, detail="No bot_id returned from API")

        return RedirectResponse(url=f"/status/{bot_id}", status_code=303)

    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=500, detail=f"HTTP error: {err} - {response.text}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {err}")


@meeting_router.get("/status/{bot_id}", response_class=JSONResponse)
async def status_page(request: Request, bot_id: str):
    """
    Steps 4-6: Return the bot_id and a link to check results as JSON.
    """
    return JSONResponse({"bot_id": bot_id, "check_results": f"/get-results/{bot_id}"})


@meeting_router.get("/get-results/{bot_id}", response_class=JSONResponse)
async def get_results(request: Request, bot_id: str):
    """
    Step 7 & 8: Retrieve Bot AND PARSE THE TRANSCRIPT — return JSON (no HTML templates).
    """
    headers = {"Authorization": RECALL_API_KEY}

    try:
        response = requests.get(f"{BASE_URL}/bot/{bot_id}", headers=headers)
        response.raise_for_status()
        data = response.json()

        status_list = data.get("status_changes", [])
        status = status_list[-1].get("code") if status_list else None

        if status is None:
            return JSONResponse({"error": "The API response didn't have a 'status_changes' list."}, status_code=500)

        print(f"--- DEBUG: CURRENT BOT STATUS IS: '{status}' ---")

        if status == "failed":
            error_message = data.get("status_changes", [{}])[-1].get("message", "Unknown error")
            return JSONResponse({"status": "failed", "error": error_message}, status_code=500)

        if status != "done":
            return JSONResponse({"status": status, "message": "Bot is not done yet. Refresh to check again."}, status_code=200)

        video_url = None
        transcript_url = None
        formatted_transcript = []

        try:
            if data.get("recordings"):
                recording_data = data["recordings"][0]
                media_shortcuts = recording_data.get("media_shortcuts", {})

                if media_shortcuts.get("video_mixed"):
                    video_url = media_shortcuts["video_mixed"]["data"]["download_url"]

                if media_shortcuts.get("transcript"):
                    transcript_url = media_shortcuts["transcript"]["data"]["download_url"]

                    transcript_response = requests.get(transcript_url)
                    transcript_response.raise_for_status()
                    transcript_data = transcript_response.json()

                    for utterance in transcript_data:
                        speaker_name = utterance.get("participant", {}).get("name", "Unknown Speaker")
                        dialogue = " ".join([word["text"] for word in utterance.get("words", [])])
                        formatted_transcript.append({"speaker": speaker_name, "line": dialogue})

            return JSONResponse({
                "status": "done",
                "video_url": video_url,
                "transcript_url": transcript_url,
                "transcript": formatted_transcript,
            })

        except Exception as e:
            print(f"--- DEBUG: FAILED TO PARSE JSON: {e} ---")
            print(json.dumps(data, indent=2))
            return JSONResponse({"error": f"Failed to parse the results JSON. Error: {e}"}, status_code=500)

    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=500, detail=f"HTTP error: {err} - {response.text}")
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {err}")
