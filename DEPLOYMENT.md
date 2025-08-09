# GitHub Pages Deployment Guide

## Quick Setup

### 1. Enable GitHub Pages
1. Go to your repository on GitHub
2. Click **Settings** tab
3. Scroll down to **Pages** section
4. Under **Source**, select **GitHub Actions**
5. The workflow is already configured in `.github/workflows/deploy.yml`

### 2. Deploy Your Backend First
Before deploying the frontend, you need to deploy your backend API:

**Option A: Vercel (Recommended)**
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set the root directory to `.` (project root)
4. Add environment variables:
   - `MONGODB_URI`: Your MongoDB Atlas connection string
   - `JWT_SECRET`: Your JWT secret key
   - `CLIENT_URL`: `https://yourusername.github.io/TODO-list-web`
5. Deploy

**Option B: Railway**
1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Add the same environment variables
4. Deploy

### 3. Update Frontend Configuration
1. Create `client/.env.production`:
   ```
   VITE_API_URL=https://your-backend-url.vercel.app
   ```
2. Commit and push to main branch
3. GitHub Actions will automatically deploy to Pages

### 4. Test Your Deployment
- Frontend: `https://yourusername.github.io/TODO-list-web`
- Check browser dev tools for any API connection errors
- Test login/register functionality
- Test creating/editing todos

## Troubleshooting

**CORS Errors**: Make sure your backend CORS is configured for your GitHub Pages URL
**API Errors**: Verify your backend is running and `VITE_API_URL` is correct
**Build Failures**: Check GitHub Actions tab in your repository for error details

## Local Development
```bash
npm run dev  # Runs both frontend (port 5173) and backend (port 3000)
```
