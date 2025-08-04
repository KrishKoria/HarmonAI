# 🎵 HarmonyAI

> **Transform your musical ideas into reality with AI-powered music generation**

HarmonyAI is a cutting-edge AI music generation platform that empowers users to create, customize, and share original music tracks through advanced machine learning technology. Whether you're a music producer, content creator, or simply someone who loves music, HarmonyAI makes professional-quality music creation accessible to everyone.

![Next.js](https://img.shields.io/badge/Next.js-15-black)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)

---

## ✨ Key Features

### 🎼 AI Music Generation

- **Multiple Creation Modes**: Simple description-based, custom lyrics with style tags, or described lyrics
- **Advanced Audio Controls**: Fine-tune guidance scale, inference steps, audio duration, and seeds
- **Style Flexibility**: Create instrumental tracks or add AI-generated/custom lyrics
- **Professional Quality**: Powered by ACE-Step pipeline for high-fidelity audio generation

### 🎵 Music Discovery & Playback

- **Trending Music**: Discover what's popular in the community
- **Category Browsing**: Explore music by genres and moods
- **In-App Player**: Full-featured audio player with seek, volume, and download controls
- **Like & Share**: Engage with the community through likes and publishing

### 🔐 User Experience

- **Seamless Authentication**: GitHub OAuth and email/password login via Better Auth
- **Credit System**: Flexible credit-based model with Polar payment integration
- **Personal Library**: Manage your created tracks with publish/unpublish controls
- **Responsive Design**: Optimized for desktop and mobile devices

### 🎨 Rich Media

- **AI-Generated Cover Art**: Automatic album artwork creation using SDXL-Turbo
- **Smart Categorization**: Automatic genre and mood tagging
- **High-Quality Assets**: Professional-grade audio and visual content

---

## 🏗️ Architecture Overview

### Frontend Stack

- **Framework**: Next.js 15 with App Router and TypeScript
- **UI Library**: Radix UI components with Tailwind CSS v4
- **Authentication**: Better Auth with GitHub OAuth integration
- **Payments**: Polar SDK for credit purchases and billing
- **Database**: Prisma ORM with PostgreSQL
- **State Management**: Zustand for player state
- **Background Jobs**: Inngest for async music generation

### Backend Stack

- **Runtime**: Modal for serverless AI processing
- **AI Models**:
  - ACE-Step pipeline for music generation
  - Qwen2-7B-Instruct LLM for prompt and lyrics generation
  - SDXL-Turbo for cover art creation
- **Storage**: S3-compatible storage (Tigris) for audio and images
- **API**: FastAPI endpoints with Pydantic validation

### Data Architecture

```
User -> Credits -> Song Generation -> Background Processing -> S3 Storage
  |                     |                        |              |
  ↓                     ↓                        ↓              ↓
Auth System      Inngest Queue           Modal AI Pipeline   Asset URLs
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** v18+
- **Python** 3.10+
- **PostgreSQL** database
- **AWS/S3** compatible storage
- **Modal** account for AI processing

### 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/KrishKoria/HarmonAI.git
   cd HarmonAI
   ```

2. **Setup Frontend**

   ```bash
   cd frontend
   pnpm install
   ```

3. **Setup Backend**

   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. **Environment Configuration**

   Create `.env` file in frontend directory:

   ```env
   # Database
   DATABASE_URL="postgresql://username:password@localhost:5432/harmonai"

   # Authentication
   BETTER_AUTH_SECRET="your-auth-secret"
   GITHUB_CLIENT_ID="your-github-client-id"
   GITHUB_CLIENT_SECRET="your-github-client-secret"

   # Polar Payments
   POLAR_ACCESS_TOKEN="your-polar-token"
   POLAR_WEBHOOK_SECRET="your-webhook-secret"

   # Storage
   AWS_ACCESS_KEY_ID="your-access-key"
   AWS_SECRET_ACCESS_KEY="your-secret-key"
   S3_BUCKET_NAME="your-bucket-name"

   # AI Generation Endpoints
   GENERATE_FROM_DESCRIPTION_API_URL="your-modal-endpoint"
   GENERATE_FROM_LYRICS_API_URL="your-modal-endpoint"
   GENERATE_FROM_DESCRIBED_LYRICS_API_URL="your-modal-endpoint"
   ```

5. **Database Setup**

   ```bash
   cd frontend
   pnpm db:generate
   pnpm db:push
   ```

6. **Run Development Servers**

   Frontend:

   ```bash
   cd frontend
   pnpm dev
   ```

   Backend (Modal deployment):

   ```bash
   cd backend
   modal deploy main.py
   ```

---

## 💡 Usage Guide

### Creating Your First Song

1. **Navigate to Create Page**: Click "Create" in the sidebar
2. **Choose Generation Mode**:
   - **Simple**: Describe your song in natural language
   - **Custom**: Use style tags and add your own lyrics
3. **Configure Options**: Toggle instrumental mode, add inspiration tags
4. **Generate**: Click "Create" and wait for background processing
5. **Listen & Share**: Play your generated track and publish to the community

### Advanced Generation Parameters

The platform supports fine-tuning with these parameters:

- **Guidance Scale**: Controls adherence to prompt (default: 15.0)
- **Inference Steps**: Quality vs speed tradeoff (default: 60)
- **Audio Duration**: Track length in seconds (default: 180)
- **Seed**: For reproducible generation (-1 for random)

### Music Discovery

- **Home Page**: Browse trending tracks and category-based collections
- **Player Controls**: Play, pause, seek, volume control, and download
- **Community Features**: Like tracks and view listen counts

---

## 🔧 API Reference

### Generation Endpoints

#### Simple Description

```http
POST /generate_from_description
Content-Type: application/json

{
  "full_described_song": "A dreamy lofi hip hop song with jazz influences",
  "instrumental": false,
  "guidance_scale": 15.0,
  "infer_step": 60,
  "audio_duration": 180
}
```

#### Custom Lyrics

```http
POST /generate_with_lyrics
Content-Type: application/json

{
  "prompt": "electronic, synthwave, 80s, upbeat",
  "lyrics": "[verse]\nNeon lights in the city...",
  "instrumental": false
}
```

#### Described Lyrics

```http
POST /generate_with_described_lyrics
Content-Type: application/json

{
  "prompt": "rock, energetic, guitar-driven",
  "described_lyrics": "lyrics about freedom and adventure",
  "instrumental": false
}
```

### Database Schema

Key models include:

- **User**: Authentication, credits, and profile data
- **Song**: Track metadata, generation parameters, and status
- **Like**: User engagement tracking
- **Category**: Auto-generated genre/mood tags
- **Session/Account**: Authentication session management

---

## 🛠️ Development

### Project Structure

```
HarmonAI/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   │   ├── (auth)/      # Authentication pages
│   │   │   └── (main)/      # Main application
│   │   ├── components/      # React components
│   │   │   ├── ui/          # Radix UI components
│   │   │   └── create/      # Song creation components
│   │   ├── lib/             # Utilities and actions
│   │   ├── store/           # Zustand state management
│   │   └── inngest/         # Background job functions
│   ├── prisma/              # Database schema
│   └── public/              # Static assets
├── backend/                 # Python/Modal backend
│   ├── main.py             # Modal app and API endpoints
│   ├── prompts.py          # LLM prompt templates
│   └── requirements.txt    # Python dependencies
└── README.md
```

### Technology Decisions

**Frontend Choices:**

- **Next.js 15**: Latest features with App Router for optimal performance
- **Better Auth**: Modern authentication with built-in UI components
- **ShadCN UI**: Accessible, styled components for design flexibility
- **Zustand**: Lightweight state management for audio player
- **Inngest**: Reliable background job processing

**Backend Choices:**

- **Modal**: Serverless compute for AI workloads with GPU acceleration
- **ACE-Step**: State-of-the-art music generation pipeline
- **Qwen2-7B**: Powerful LLM for prompt and lyrics generation
- **FastAPI**: High-performance API framework with automatic validation

### Performance Optimizations

- **Streaming Audio**: Progressive loading for large audio files
- **Image Optimization**: Next.js Image component with lazy loading
- **Database Indexing**: Optimized queries with Prisma
- **Background Processing**: Non-blocking music generation
- **CDN Storage**: Fast global asset delivery via S3

---

## 🚀 Deployment

### Frontend Deployment (Vercel)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy with automatic CI/CD

### Backend Deployment (Modal)

1. Install Modal CLI: `pip install modal`
2. Authenticate: `modal token new`
3. Deploy: `modal deploy backend/main.py`

### Database (Railway/Supabase)

1. Create PostgreSQL instance
2. Update `DATABASE_URL` in environment variables
3. Run migrations: `pnpm db:migrate`

---

## 📊 Monitoring & Analytics

- **User Engagement**: Track song creation, plays, and likes
- **Generation Metrics**: Monitor success rates and processing times
- **Resource Usage**: Modal compute costs and S3 storage
- **Error Tracking**: Comprehensive logging and error handling

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow TypeScript best practices
- Use Prettier for code formatting
- Write comprehensive tests
- Update documentation for new features
- Follow conventional commit messages

---

<div align="center">

**[🎵 Try HarmonyAI Now](https://harmony-ai-ten.vercel.app/)**

Made with ❤️ by [Krish Koria](https://www.krishkoria.com/)

</div>
