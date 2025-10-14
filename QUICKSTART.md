# StoryCraft Quick Start Guide

## What's Been Set Up

Your StoryCraft monorepo is now configured with:

### ✅ Frontend (React + MUI + TanStack Router)

- **React 18** with Vite for fast development
- **Material-UI v7** with beautiful dark theme
- **TanStack Router** for file-based routing
- Four routes already created: Home, Stories, Characters, Worlds
- Full navigation bar with MUI AppBar
- Responsive layout with Container components

### ✅ Backend (FastAPI + SQLAlchemy + SQLite)

- **FastAPI** server with automatic API documentation
- **SQLAlchemy ORM** with comprehensive database models
- **CRUD endpoints** for Stories, Characters, and Worlds
- **LLM integration** supporting OpenAI, Anthropic, and Google
- **CORS enabled** for frontend-backend communication

### ✅ Database Models

All models are defined and ready:

- **Story** (with chapters, scenes, plots)
- **Character** (with relationships, personality, background)
- **World** (with locations, lore, culture)
- **Chapter** & **Scene**
- **Location** & **Plot**

## Next Steps to Run

### 1. Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Configure API Keys

```powershell
cd backend
Copy-Item .env.example .env
# Edit .env and add your API keys
cd ..
```

### 3. Run the Application

**Option A: Run both frontend and backend together**

```powershell
npm run dev:all
```

**Option B: Run separately**

Terminal 1 (Frontend):

```powershell
npm run dev:frontend
```

Terminal 2 (Backend):

```powershell
npm run dev:backend
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## What You Can Do Now

1. **View the UI**: Navigate to http://localhost:3000 to see the dark-themed interface
2. **Explore API**: Check http://localhost:8000/docs for interactive API documentation
3. **Test Endpoints**: Use the Swagger UI to test CRUD operations
4. **Generate with AI**: Use the `/api/llm/generate` endpoint (after adding API keys)

## File Structure

```
storycraft/
├── frontend/
│   ├── src/
│   │   ├── routes/        # Your page components
│   │   ├── theme/         # MUI dark theme
│   │   └── main.jsx       # Entry point
│   ├── vite.config.js
│   └── package.json
│
├── backend/
│   ├── routers/           # API endpoints
│   ├── models.py          # Database models
│   ├── database.py        # DB configuration
│   ├── main.py            # FastAPI app
│   └── requirements.txt   # Python deps
│
└── package.json           # Root config
```

## Development Workflow

1. **Frontend Changes**: Edit files in `frontend/src/` - hot reload is enabled
2. **Backend Changes**: Edit files in `backend/` - auto-reload is enabled
3. **New Routes**: Add `.jsx` files to `frontend/src/routes/`
4. **New API Endpoints**: Add routers in `backend/routers/`
5. **Database Changes**: Modify `backend/models.py`

## Troubleshooting

### Frontend not starting?

```powershell
cd frontend
Remove-Item -Recurse node_modules
npm install
```

### Backend not starting?

```powershell
cd backend
pip install -r requirements.txt --force-reinstall
```

### Database issues?

```powershell
cd backend
Remove-Item storycraft.db
# Database will be recreated on next backend start
```

## Features to Implement Next

1. **AI Character Generator**: Use LLM endpoints to generate character details
2. **Story Editor**: Rich text editor for writing chapters
3. **World Map**: Visual world builder
4. **Export**: PDF/EPUB export functionality
5. **Collaboration**: Multi-user features

## Important Notes

- The frontend proxies `/api` requests to `http://localhost:8000`
- CORS is configured to allow `http://localhost:3000`
- Database is SQLite (file-based, no setup required)
- TanStack Router generates `routeTree.gen.ts` automatically
- MUI theme uses deep purple (#9c27b0) and cyan (#00bcd4) as primary/secondary colors

## Getting Help

- **Frontend Issues**: Check Vite/React/MUI documentation
- **Backend Issues**: Check FastAPI/SQLAlchemy documentation
- **Router Issues**: Check TanStack Router documentation
- **API Testing**: Use http://localhost:8000/docs

Happy creating! 🎨📖✨
