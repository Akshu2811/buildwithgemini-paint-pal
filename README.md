# 🎨 PaintPal · Wall Paint & Room Color Concierge

An agentic interior design assistant that helps homeowners and renters choose the perfect wall paint colors for any room and visualize the transformation in realistic interior previews.

<div align="center">

![PaintPal Demo](demo.gif)

*Screen recording of PaintPal recommending shades for a calm bedroom and visualizing Sage Whisper in the ADK Dev UI.*

</div>

---

## 🌟 Overview

**PaintPal** simplifies home decor and renovation decisions. Users specify their room type (e.g., bedroom, living room, study) and their desired atmosphere (e.g., calm, energetic, cozy). PaintPal consults a curated Firestore paint database, recommends 2–3 matching colors with interior styling rationale, and generates realistic preview images of the room painted in the chosen shade.

---

## 🚀 Implemented Features (`app/`)

The core agent application is implemented with the **Agent Development Kit (ADK)** and powered by **Gemini 3.8 Flash**:

### 1. 🗄️ Firestore Paint Catalog
- Real-time catalog stored in a native Google Cloud Firestore database (`paints` collection).
- Each paint entry contains:
  - `name`: Color title (e.g., *Sage Whisper*, *Ocean Breeze*, *Warm Terracotta*)
  - `hex_code`: Hex color code (e.g., `#B2C9AB`, `#A8D0E6`, `#D97443`)
  - `price_inr`: Price in INR per liter
  - `mood`: Associated vibe (e.g., *calm*, *energetic*, *cozy*)
  - `suitable_rooms`: List of compatible spaces (*bedroom*, *living room*, *study*, etc.)

### 2. 🔍 `find_paints` Tool
- ADK function tool querying Firestore for exact and partial matches on room type and mood.
- Proactively clarifies missing user inputs before querying.
- Returns detailed recommendations including price, hex codes, and personalized explanations.

### 3. 🖼️ Room Image Generation & Cloud Storage Integration
- ADK function tool `generate_room_image(room, paint_name)` that generates high-resolution room previews.
- Uses **`gemini-3.1-flash-lite-image`** on Vertex AI with the paint's exact name and hex code retrieved from Firestore.
- In-memory processing: saves images as ADK session artifacts and streams bytes directly to a public **Google Cloud Storage** bucket without writing to local disk.
- Returns a public image url.

---

## 📋 Planned Features (from `project_brief.md`)

The following capabilities are planned for upcoming iterations:

- ⏳ **Cross-Session Memory (Vertex AI Memory Bank)**: Persisting user preferences, past consultations, and selected color palettes across distinct conversations.
- ⏳ **Interactive A2UI Cards**: Rendering color swatches, palette comparison tables, and interactive cards natively in the chat interface.
- ⏳ **Room Area & Paint Calculator (Code Sandbox)**: Calculating required paint volume in liters and total project cost based on user-provided room dimensions.

---

## 🛠️ Architecture & Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| **Agent Reasoning** | Gemini 3.8 Flash (`gemini-3.8-flash`) | Intent parsing, guidance, recommendations |
| **Image Generation** | Gemini 3.1 Flash Lite Image (`gemini-3.1-flash-lite-image`) | Photorealistic room rendering with color accuracy |
| **Orchestration** | Agent Development Kit (ADK) + `agents-cli` | Agent lifecycle, tool calling, session artifacts |
| **Database** | Google Cloud Firestore | Catalog storage for paint shades and metadata |
| **Object Storage** | Google Cloud Storage | Public hosting for generated room visual previews |

---

## 💻 Local Development

### Prerequisites
- Python 3.11+
- `uv` package manager
- `agents-cli`
- Google Cloud SDK (`gcloud`) authenticated with project access

### Running the Agent

1. **Configure project ID**:
   - Replace `PROJECT_ID` in `app/agent.py` and `seed_paints.py` with your own GCP project.

2. **Install dependencies**:
   ```bash
   cd paint-pal
   uv sync
   ```

3. **Seed the Firestore paint catalog** (if not already seeded):
   ```bash
   python seed_paints.py
   ```

4. **Test the agent via CLI**:
   ```bash
   agents-cli run "I want a calm bedroom, what colors do you suggest?"
   agents-cli run "Show me the bedroom painted in Sage Whisper"
   ```

5. **Launch the interactive playground**:
   ```bash
   agents-cli playground
   ```

---

## 📄 License

Apache License 2.0
