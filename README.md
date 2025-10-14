# StoryCraftThis is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/pages/api-reference/create-next-app).

An AI-powered story creation platform that helps writers craft thoughtful and robust stories. Whether you're drafting a novel or planning a Dungeons and Dragons campaign, StoryCraft leverages multiple LLM providers (Google, Claude, OpenAI) to help you generate beautiful and rich characters, plots, scenes, chapters, lore, and worlds.## Getting Started

## 🏗️ Monorepo StructureFirst, run the development server:

````bash

storycraft/npm run dev

├── frontend/          # React + MUI + TanStack Router# or

├── backend/           # FastAPI + SQLAlchemy + SQLiteyarn dev

├── _old_nextjs/       # Original Next.js files (backup)# or

└── package.json       # Root workspace configurationpnpm dev

```# or

bun dev

## ✨ Features```



- **Rich Story Creation**: Draft novels with AI-powered chapters, plots, and scenesOpen [http://localhost:3000](http://localhost:3000) with your browser to see the result.

- **Deep Character Development**: Generate detailed characters with backgrounds, motivations, and personality traits

- **World Building**: Create immersive worlds with detailed lore, locations, and historiesYou can start editing the page by modifying `pages/index.js`. The page auto-updates as you edit the file.

- **Multi-LLM Support**: Connect to Google, Claude, or OpenAI for AI assistance

- **Dark Mode UI**: Beautiful dark-themed interface built with Material-UI v7[API routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes) can be accessed on [http://localhost:3000/api/hello](http://localhost:3000/api/hello). This endpoint can be edited in `pages/api/hello.js`.

- **File-based Routing**: Powered by TanStack Router for optimal performance

The `pages/api` directory is mapped to `/api/*`. Files in this directory are treated as [API routes](https://nextjs.org/docs/pages/building-your-application/routing/api-routes) instead of React pages.

## 🚀 Tech Stack

This project uses [`next/font`](https://nextjs.org/docs/pages/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

### Frontend

- **React 18**: Modern React with hooks## Learn More

- **Material-UI v7**: Component library with dark theme

- **TanStack Router**: Type-safe file-based routingTo learn more about Next.js, take a look at the following resources:

- **Vite**: Fast build tool and dev server

- **Axios**: HTTP client for API communication- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.

- [Learn Next.js](https://nextjs.org/learn-pages-router) - an interactive Next.js tutorial.

### Backend

- **FastAPI**: Modern, fast Python web frameworkYou can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

- **SQLAlchemy**: SQL toolkit and ORM

- **SQLite**: Lightweight database## Deploy on Vercel

- **Pydantic**: Data validation

- **Multiple LLM SDKs**: OpenAI, Anthropic, Google AIThe easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.



## 📋 PrerequisitesCheck out our [Next.js deployment documentation](https://nextjs.org/docs/pages/building-your-application/deploying) for more details.


- **Node.js** 18+ and npm
- **Python** 3.10+
- **pip** (Python package manager)
- API keys for at least one LLM provider:
  - OpenAI API key
  - Anthropic (Claude) API key
  - Google AI API key

## 🛠️ Installation

### 1. Install Root Dependencies

```powershell
npm install
```

### 2. Install Frontend Dependencies

```powershell
cd frontend
npm install
cd ..
```

### 3. Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
cd ..
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```powershell
cd backend
Copy-Item .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

## 🏃 Running the Application

### Development Mode (Both Frontend and Backend)

```powershell
npm run dev:all
```

This will start:
- Frontend at http://localhost:3000
- Backend at http://localhost:8000
- API docs at http://localhost:8000/docs

### Run Frontend Only

```powershell
npm run dev:frontend
# or
cd frontend
npm run dev
```

### Run Backend Only

```powershell
npm run dev:backend
# or
cd backend
python -m uvicorn main:app --reload --port 8000
```

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Available Endpoints

#### Stories
- `GET /api/stories` - List all stories
- `POST /api/stories` - Create a new story
- `GET /api/stories/{id}` - Get story details
- `PUT /api/stories/{id}` - Update a story
- `DELETE /api/stories/{id}` - Delete a story

#### Characters
- `GET /api/characters` - List all characters
- `POST /api/characters` - Create a new character
- `GET /api/characters/{id}` - Get character details
- `PUT /api/characters/{id}` - Update a character
- `DELETE /api/characters/{id}` - Delete a character

#### Worlds
- `GET /api/worlds` - List all worlds
- `POST /api/worlds` - Create a new world
- `GET /api/worlds/{id}` - Get world details
- `PUT /api/worlds/{id}` - Update a world
- `DELETE /api/worlds/{id}` - Delete a world

#### LLM Generation
- `POST /api/llm/generate` - Generate content using AI
- `GET /api/llm/providers` - Get available LLM providers

## 🗄️ Database Models

### Story
- Chapters
- Scenes
- Associated Characters
- Associated Worlds
- Plots

### Character
- Name, Description, Background
- Personality, Appearance, Motivations
- Relationships (JSON)

### World
- Name, Description, History
- Geography, Culture
- Magic System, Technology Level
- Locations

### Additional Models
- Chapter (part of Story)
- Scene (part of Chapter)
- Location (part of World)
- Plot (part of Story)

## 🎨 Frontend Structure

```
frontend/
├── src/
│   ├── routes/         # TanStack Router file-based routes
│   │   ├── __root.jsx  # Root layout with navigation
│   │   ├── index.jsx   # Home page
│   │   ├── stories.jsx # Stories list
│   │   ├── characters.jsx
│   │   └── worlds.jsx
│   ├── theme/
│   │   └── darkTheme.js # MUI dark theme configuration
│   ├── main.jsx        # App entry point
│   └── routeTree.gen.ts # Generated route tree (auto-generated)
├── index.html
├── vite.config.js
└── package.json
```

## 🐍 Backend Structure

```
backend/
├── routers/
│   ├── characters.py   # Character CRUD endpoints
│   ├── stories.py      # Story CRUD endpoints
│   ├── worlds.py       # World CRUD endpoints
│   └── llm.py          # LLM integration endpoints
├── models.py           # SQLAlchemy models
├── database.py         # Database configuration
├── main.py             # FastAPI app entry point
├── requirements.txt    # Python dependencies
└── .env               # Environment variables (create from .env.example)
```

## 🔧 Development Tips

### Frontend Hot Reload
Vite provides instant hot module replacement. Changes to React components will update instantly.

### Backend Hot Reload
The FastAPI server runs with `--reload` flag, automatically restarting when Python files change.

### Database Migrations
The database schema is automatically created on first run. To reset:

```powershell
cd backend
Remove-Item storycraft.db
# Restart the backend - tables will be recreated
```

### TanStack Router DevTools
The router devtools are available in development mode at the bottom-right of the frontend.

## 🚢 Building for Production

### Frontend

```powershell
cd frontend
npm run build
```

The built files will be in `frontend/dist/`

### Backend

The FastAPI app can be deployed using:

```powershell
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📝 Next Steps

1. **Implement AI-Powered Generation**:
   - Add prompts for character generation
   - Create story chapter generation flows
   - Build world-building AI assistants

2. **Enhance UI Components**:
   - Create detailed forms for entities
   - Add rich text editors for content
   - Implement drag-and-drop organization

3. **Add Authentication**:
   - User accounts and login
   - Multi-user story collaboration
   - Personal story libraries

4. **Advanced Features**:
   - Export stories to various formats (PDF, EPUB, etc.)
   - Story timeline visualization
   - Character relationship graphs
   - World map integration

## 🤝 Contributing

This is a monorepo project. Please ensure:
- Frontend code follows React best practices
- Backend code follows PEP 8 guidelines
- API endpoints are documented
- UI components are reusable and themed

## 📄 License

Private project - All rights reserved

## 🙏 Acknowledgments

- Material-UI for the beautiful component library
- TanStack for the amazing routing solution
- FastAPI for the modern Python web framework
- All the LLM providers for enabling AI-powered creativity
````
