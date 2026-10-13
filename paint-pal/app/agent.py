# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import uuid

from google import genai
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.cloud import firestore, storage
from google.genai import types

MODEL = "gemini-3.8-flash"
PROJECT_ID = "qwiklabs-gcp-04-ff10d3da2b21"
BUCKET_NAME = "paintpal-qwiklabs-gcp-04-ff10d3da2b21"


def find_paints(room: str = "", mood: str = "") -> list[dict]:
    """Finds paint recommendations from the Firestore catalog based on room type and mood.

    Args:
        room: The type of room (e.g., 'bedroom', 'living room', 'kitchen', 'study', 'bathroom', 'dining room').
        mood: The desired mood or atmosphere (e.g., 'calm', 'energetic', 'cozy').

    Returns:
        A list of matching paint dictionaries containing name, hex_code, price_inr, mood, and suitable_rooms.
    """
    db = firestore.Client(project=PROJECT_ID)
    docs = [d.to_dict() for d in db.collection("paints").stream()]

    norm_room = (room or "").strip().lower()
    norm_mood = (mood or "").strip().lower()

    exact_matches = []
    partial_matches = []

    for data in docs:
        paint_mood = data.get("mood", "").lower()
        suitable_rooms = [r.lower() for r in data.get("suitable_rooms", [])]

        mood_match = (not norm_mood) or (norm_mood in paint_mood) or (paint_mood in norm_mood)
        room_match = (not norm_room) or any(norm_room in r or r in norm_room for r in suitable_rooms)

        if mood_match and room_match:
            exact_matches.append(data)
        elif mood_match or room_match:
            partial_matches.append(data)

    if exact_matches:
        return exact_matches
    if partial_matches:
        return partial_matches
    return docs[:3]


def generate_room_image(room: str, paint_name: str, tool_context: ToolContext = None) -> dict:
    """Generates an image of a room painted in a chosen paint color using the gemini-3.1-flash-lite-image model.

    Looks up the paint name and hex code from Firestore to construct the prompt,
    saves the image as an ADK session artifact, uploads the bytes directly to Cloud Storage,
    and returns the public https URL.

    Args:
        room: The room type to visualize (e.g., 'bedroom', 'living room', 'kitchen', 'study').
        paint_name: The name of the paint color (e.g., 'Sage Whisper', 'Ocean Breeze').
        tool_context: ADK tool context for saving session artifacts.

    Returns:
        A dictionary with room, paint_name, hex_code, and public https image URL.
    """
    db = firestore.Client(project=PROJECT_ID)
    docs = [d.to_dict() for d in db.collection("paints").stream()]

    norm_target = (paint_name or "").strip().lower()
    matched_paint = next(
        (p for p in docs if norm_target and (norm_target in p.get("name", "").lower() or p.get("name", "").lower() in norm_target)),
        None,
    )

    if matched_paint:
        actual_name = matched_paint.get("name", paint_name)
        hex_code = matched_paint.get("hex_code", "")
    else:
        actual_name = paint_name
        hex_code = "#A8D0E6"

    prompt = (
        f"A professional high-resolution interior photograph of a beautifully designed modern {room} "
        f"with all walls painted in {actual_name} (hex code {hex_code}). "
        f"Tasteful interior styling, complementary furniture, and realistic warm natural lighting."
    )

    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )

    candidate = response.candidates[0]
    img_part = next((p for p in candidate.content.parts if p.inline_data), None)
    if not img_part:
        raise RuntimeError("No image data returned from image generation model.")

    img_bytes = img_part.inline_data.data
    mime_type = img_part.inline_data.mime_type or "image/jpeg"

    clean_paint = re.sub(r"[^a-zA-Z0-9]+", "_", actual_name.strip().lower())
    clean_room = re.sub(r"[^a-zA-Z0-9]+", "_", room.strip().lower())
    filename = f"{clean_room}_{clean_paint}_{uuid.uuid4().hex[:6]}.jpg"

    if tool_context:
        artifact_part = types.Part.from_bytes(data=img_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(img_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "room": room,
        "paint_name": actual_name,
        "hex_code": hex_code,
        "public_image_url": public_url,
    }


AGENT_INSTRUCTION = """You are PaintPal, a friendly and knowledgeable interior design AI assistant that helps users select the best wall paint colors and visualize them.

Capabilities:
1. Recommending Paints:
   - If the user hasn't specified both the room type (e.g., bedroom, living room, study, kitchen) and the desired mood (e.g., calm, energetic, cozy), ask them for the missing information before recommending colors.
   - Once you have both the room type and mood, call the `find_paints` tool to retrieve matching colors from the Firestore collection.
   - Recommend 2 to 3 matching paints with thoughtful reasons explaining why each color and mood works well for their specific room.
   - For each recommendation, provide its name, hex code, mood, and price in INR (₹).

2. Visualizing Rooms:
   - When the user asks to see, preview, or generate an image of a room in a specific paint color (e.g., "Show me a bedroom painted in Sage Whisper"), call the `generate_room_image` tool with the room and paint name.
   - In your response, provide the public image URL, embed it using markdown format `![Room Preview](<url>)`, and explain how the shade transforms the room.
"""

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=AGENT_INSTRUCTION,
    tools=[find_paints, generate_room_image],
)

app = App(
    root_agent=root_agent,
    name="app",
)
