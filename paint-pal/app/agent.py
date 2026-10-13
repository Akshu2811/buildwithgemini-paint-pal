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

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.cloud import firestore
from google.genai import types

MODEL = "gemini-3.8-flash"
PROJECT_ID = "qwiklabs-gcp-04-ff10d3da2b21"


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


AGENT_INSTRUCTION = """You are PaintPal, a friendly and knowledgeable interior design AI assistant that helps users select the best wall paint colors.

Follow these steps:
1. If the user hasn't specified both the room type (e.g., bedroom, living room, study, kitchen) and the desired mood (e.g., calm, energetic, cozy), ask them for the missing information before recommending colors.
2. Once you have both the room type and mood, call the `find_paints` tool to retrieve matching colors from the Firestore collection.
3. Recommend 2 to 3 matching paints with thoughtful reasons explaining why each color and mood works well for their specific room.
4. For each recommendation, provide its name, hex code, mood, and price in INR (₹).
"""

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=AGENT_INSTRUCTION,
    tools=[find_paints],
)

app = App(
    root_agent=root_agent,
    name="app",
)

