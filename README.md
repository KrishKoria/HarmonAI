# HarmonyAI

HarmonyAI is an AI-powered music generation platform that enables users to create, customize, and listen to AI-generated songs. It combines a modern web frontend with a powerful backend leveraging state-of-the-art machine learning models for music and lyric generation.

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Frontend Components](#frontend-components)
- [Backend Overview](#backend-overview)
- [Getting Started](#getting-started)
- [Usage](#usage)

---

## Features

- **AI Music Generation:** Generate original music tracks from text descriptions, custom lyrics, or described lyrics.
- **Customizable Song Creation:** Choose between simple (description-based) or custom (style tags, lyrics, instrumental) song generation modes.
- **Song Management:** Search, rename, publish/unpublish, and download generated tracks.
- **Audio Playback:** In-app player with play, pause, seek, and volume controls.
- **User Authentication:** Secure login and user management with Better Auth UI and Polar SDK.
- **Credits & Upgrades:** Track usage credits and access upgrade options.
- **Responsive UI:** Modern, mobile-friendly interface built with Next.js, React, Radix UI, and Tailwind CSS.
- **Cloud Storage:** Generated audio and cover art are stored on AWS S3.

---

## Architecture Overview

- **Frontend:**

  - Built with Next.js (React, TypeScript)
  - State management with Zustand
  - UI components from Radix UI and custom design system
  - Authentication via Better Auth UI and Polar SDK
  - Communicates with backend via REST API endpoints

- **Backend:**

  - Python (Modal, HuggingFace, custom models)
  - Music and lyric generation using deep learning pipelines
  - S3 integration for storing generated files
  - Exposes endpoints for song generation and metadata retrieval

- **Database:**
  - Prisma ORM (schema not shown)
  - Stores user, song, and metadata

---

## Frontend Components

- **AppSidebar:** Navigation sidebar with branding, menu, credits, upgrade, and user profile.
- **SongPanel:** Song creation panel with simple/custom modes, inspiration/style tags, lyrics (auto/write), and instrumental toggle.
- **TrackList:** Displays list of generated tracks with search, publish/unpublish, rename, and download options.
- **SongCard:** Card UI for individual songs, showing artwork, title, artist, play/like controls, and listen/like counts.
- **SoundBar:** Audio player with playback controls, seek, volume, and download.
- **UI Components:** Button, Card, Dialog, Dropdown, Input, Label, Slider, Tabs, Tooltip, etc. (see `src/components/ui/`)
- **Hooks & Store:** Custom hooks (e.g., `use-mobile`) and Zustand store for player state.

---

## Backend Overview

- **main.py:**
  - Defines Modal app and music generation server
  - Loads and manages ML models for music, lyrics, and cover art
  - Exposes endpoints for:
    - Generating music from description
    - Generating music with custom lyrics
    - Generating music with described lyrics
  - Handles S3 upload and returns metadata (audio key, cover image, categories)
- **prompts.py:**
  - Contains prompt templates for music and lyric generation
- **requirements.txt:**
  - Lists Python dependencies (Modal, HuggingFace, boto3, etc.)

---

## Getting Started

### Prerequisites

- Node.js (v18+ recommended)
- Python 3.10+
- AWS credentials for S3 access
- Modal account (for backend deployment)

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/KrishKoria/HarmonAI.git
   cd HarmonAI
   ```
2. **Install frontend dependencies:**
   ```sh
   cd frontend
   pnpm install
   # or
   npm install
   ```
3. **Install backend dependencies:**
   ```sh
   cd ../backend
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**

   - Set AWS and Modal credentials as required.
   - Configure S3 bucket name and endpoints.

5. **Run the backend (locally or on Modal):**
   ```sh
   python main.py
   # or deploy via Modal CLI
   ```
6. **Run the frontend:**
   ```sh
   cd ../frontend
   pnpm dev
   # or
   npm run dev
   ```

---

## Usage

- **Create a Song:**
  - Use the SongPanel to describe your song or enter custom styles/lyrics.
  - Click "Create" to generate a new track.
- **Manage Songs:**
  - View, search, rename, publish/unpublish, and download your tracks in the TrackList.
- **Playback:**
  - Use the SoundBar to play, pause, seek, and adjust volume for any track.
- **Profile & Credits:**
  - Access your profile, view credits, and upgrade via the sidebar.

---
