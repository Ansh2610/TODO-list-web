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
- HTML5, CSS3, JavaScript (ES6+)
- Modular architecture with separate managers
- Responsive design with CSS Grid/Flexbox

**Backend:**
- Node.js with Express.js
- MongoDB Atlas with Mongoose ODM
- JWT authentication with bcrypt
- Security middleware (Helmet, CORS, Rate limiting)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Ansh2610/TODO-list-web.git
cd TODO-list-web
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Environment Configuration
1. Create a `.env` file in the project root:
   ```bash
   # Create .env file (Windows)
   type nul > .env
   
   # Or create manually and add the following:
   ```

2. Add your configuration to `.env`:
   ```
   NODE_ENV=development
   PORT=3000
   MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/todo-app?retryWrites=true&w=majority
   JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
   JWT_EXPIRES_IN=24h
   CLIENT_URL=http://localhost:3000
   ```

3. Generate a secure JWT secret:
   ```bash
   # On Windows PowerShell:
   [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((1..32 | ForEach {[char](Get-Random -Min 65 -Max 90)})) -join '')
   
   # Or use any random 32+ character string
   ```

### 4. MongoDB Atlas Setup
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a new cluster
3. Create a database user
4. Add your IP address to Network Access
5. Get the connection string and update `.env`

### 5. Start the Application
```bash
# Development mode (with auto-restart)
npm run dev

# Production mode
npm start
```

### 6. Access the Application
- Open your browser to `http://localhost:3000`
- Register a new account or use the test setup script

## Project Structure

```
TODO-list-web/
├── server.js              # Express server
├── index.html             # Main application
├── auth.html              # Authentication page
├── scripts/
│   ├── app.js             # Main application orchestrator
│   ├── todoManager.js     # Core business logic
│   ├── storage.js         # API and storage management
│   ├── ui.js              # UI management and DOM manipulation
│   └── auth.js            # Authentication management
├── styles/
│   ├── main.css           # Main styles and theme
│   ├── auth.css           # Authentication page styles
│   └── responsive.css     # Mobile responsive styles
├── server/
│   ├── models/            # MongoDB schemas
│   ├── routes/            # API endpoints
│   └── middleware/        # Authentication middleware
└── .gitignore             # Git ignore file
```

## Development

### Testing Authentication
Run the test setup script in browser console:
```javascript
// Loads test-setup.js to simulate logged-in user
```

### API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `GET /api/todos` - Get user's todos
- `POST /api/todos` - Create new todo
- `PUT /api/todos/:id` - Update todo
- `DELETE /api/todos/:id` - Delete todo

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Input validation and sanitization
- Rate limiting
- CORS protection
- Helmet security headers
- Environment variable protection

## Deployment

The application is designed to work with:
- **Backend**: Heroku, Railway, Render, or any Node.js hosting
- **Database**: MongoDB Atlas (cloud)
- **Frontend**: Can be served statically or with the backend

## License

MIT License - feel free to use this project for learning and development!
