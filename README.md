# TODO List Web Application

A full-stack, modular TODO list web application with user authentication and MongoDB backend.

## Features

- ✅ **Full Authentication System** - Register, login, logout with JWT tokens
- ✅ **Enhanced Task Management** - Add, edit, delete, filter, and sort tasks
- ✅ **Rich Task Details** - Priority, due dates, categories, descriptions
- ✅ **MongoDB Integration** - Cloud database with local fallback
- ✅ **Responsive Design** - Works on desktop and mobile
- ✅ **Modular Architecture** - Clean, maintainable code structure
- ✅ **Modern UI/UX** - Pixel art theme with smooth animations

## Technologies

**Frontend:**
- React 18 with Vite
- React Router for navigation
- Modern hooks and context API
- Vitest + Testing Library for testing

**Backend:**
- Node.js with Express.js
- MongoDB Atlas with Mongoose ODM
- JWT authentication with bcrypt
- Security middleware (Helmet, CORS, Rate limiting)

## Deployment

### Frontend (GitHub Pages)

1. **Automatic Deployment**: Push to main branch triggers GitHub Actions
2. **Manual Setup**: 
   - Go to your GitHub repository settings
   - Navigate to Pages section
   - Select "GitHub Actions" as source
   - The workflow will automatically deploy on push to main

### Backend (Vercel/Railway/Render)

1. **Deploy Backend First**: Deploy your backend to Vercel, Railway, or Render
2. **Update Environment**: Create `.env.production` in client folder:
   ```
   VITE_API_URL=https://your-backend-url.vercel.app
   ```
3. **Rebuild**: The GitHub Actions will use this URL for production builds

### Local Development

```bash
# Install dependencies
npm install
cd client && npm install && cd ..

# Start both frontend and backend
npm run dev

# Backend only (port 3000)
npm run dev:backend

# Frontend only (port 5173)  
npm run dev:frontend
```

