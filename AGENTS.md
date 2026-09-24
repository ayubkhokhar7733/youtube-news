# Antigravity Instructions: YouTube Automation Engine (New Flow / Motivational Flow Base)

## 📌 Project Overview
This repository contains a standalone, fully autonomous YouTube video generation engine cloned from a production base to serve as a clean foundation for a **new YouTube channel with fresh content**.
All ties, history, queues, credentials, and git connections to the previous channel have been disconnected so the original setup continues running undisturbed.

- **Workspace Goal**: Launch a new automated channel (customizable niche, topics, scripts, and branding).
- **Core Formats**: 16:9 Landscape master video (1920x1080) + 9:16 vertical Shorts (1080x1920).
- **Media Engine**: Concurrent Pexels + Pixabay stock sourcing with connection pooling.
- **Narrator**: Neural Edge-TTS with millisecond word-level ASS subtitles.
- **Compositor**: Direct FFmpeg zero-memory compositing with audio ducking.

---

## 🏗️ Architecture & Core Components

| Module | File | Purpose |
| :--- | :--- | :--- |
| **Pipeline Controller** | [`pipeline.py`](file:///pipeline.py) | Master orchestrator coordinating all 7 generation and publishing stages. |
| **Script Generation** | [`core/script_generator.py`](file:///core/script_generator.py) | Groq Llama-3.3-70B prompt engine; generates rich 300s documentary scripts. |
| **TTS & Timing** | [`core/tts_engine.py`](file:///core/tts_engine.py) | Edge-TTS integration producing crystal-clear audio and millisecond word timestamps. |
| **Media Sourcing** | [`core/media_searcher.py`](file:///core/media_searcher.py) | Dual Pexels + Pixabay candidate aggregator; targets 720p HD landscape media. |
| **Video Compositor** | [`core/video_composer.py`](file:///core/video_composer.py) | Direct FFmpeg composition; Ken Burns effects, audio ducking, burned-in ASS subtitles. |
| **Thumbnail Generator** | [`thumbnail_gen.py`](file:///thumbnail_gen.py) | Pillow 1280x720 graphic engine; produces high-CTR maxres thumbnails with punchy text badges. |
| **Shorts Extractor** | [`shorts_extractor.py`](file:///shorts_extractor.py) | Auto-scores narrative peaks and extracts 2 vertical 9:16 Shorts with centered word subtitles. |
| **Topic Selector** | [`topic_selector.py`](file:///topic_selector.py) | 40-topic queue with 90-day anti-collision guard and automatic Groq self-refill loop. |
| **SEO Metadata** | [`metadata_generator.py`](file:///metadata_generator.py) | Generates pattern-rotated titles (A/B/C/D/E), SEO descriptions, tags, and categories. |
| **YouTube Client** | [`youtube_uploader.py`](file:///youtube_uploader.py) | Headless OAuth 2.0 client; uploads video, custom thumbnail, and playlists. |
| **Auth Setup** | [`youtube_auth_setup.py`](file:///youtube_auth_setup.py) | Local one-time OAuth token generator creating `YOUTUBE_REFRESH_TOKEN`. |

---

## 🔑 Environment & Secrets Configuration

The engine requires the following environment variables (stored in `.env` locally and in GitHub Repository Secrets):

1. `GROQ_API_KEY`: Groq API key for Llama-3.3-70b script & metadata generation.
2. `PEXELS_API_KEY`: Pexels stock video & photo API key.
3. `PIXABAY_API_KEY`: Pixabay stock video & photo API key.
4. `YOUTUBE_CLIENT_ID`: Google Cloud OAuth Desktop Client ID.
5. `YOUTUBE_CLIENT_SECRET`: Google Cloud OAuth Desktop Client Secret.
6. `YOUTUBE_REFRESH_TOKEN`: Permanent OAuth 2.0 refresh token for YouTube Data API v3.

---

## 🚀 Quick Commands for New Environments

- **Install dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
- **Ensure FFmpeg is installed and on system PATH**:
  ```bash
  ffmpeg -version
  ```
- **Run local pipeline test**:
  ```bash
  py pipeline.py --auto-topic --duration 300 --privacy private
  ```
- **Re-authenticate YouTube on a new machine**:
  ```bash
  py youtube_auth_setup.py
  ```
- **Switch to Full Public Publishing**:
  In `.github/workflows/publish.yml` line 90, change `'private'` to `'public'`.
