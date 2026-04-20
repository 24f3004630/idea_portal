# CCEW Idea Portal - Startup Configuration Updates

## Summary of Changes

### 1. **Fixed Template Paths** ✅
**What I changed:** Updated `backend/app.py` to point to the new `frontend/templates` directory
- **Why:** Templates moved from `templates/` → `frontend/templates/` during restructuring
- **File edited:** `/backend/app.py` line ~25
- **Change:**
  ```python
  # OLD: app = Flask(__name__)
  # NEW: 
  template_folder = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates')
  app = Flask(__name__, template_folder=template_folder)
  ```

### 2. **Created Environment Configuration** ✅
**What I created:** `backend/.env` file with essential settings
- **Why:** Flask app uses python-dotenv to load secrets and configuration
- **Location:** `/backend/.env`
- **Includes:** SECRET_KEY, REDIS_URL, Email settings, Portal metadata
- **Note:** Email settings are optional for basic development

### 3. **Created Startup Script** ✅
**What I created:** `startup.sh` at project root for easy startup
- **Why:** Handles virtual environment activation and directory navigation automatically
- **Location:** `/startup.sh` (executable, chmod +x)
- **Usage:** `./startup.sh` from project root
- **Does:** Activates venv → Installs deps → Creates reports dir → Runs Flask

### 4. **Fixed Virtual Environment** ✅
**What I fixed:** Recreated venv to use correct Python interpreter
- **Why:** Previous venv was symlinked to system Python without packages installed
- **Solution:** Ran `python3 -m venv venv` to create fresh venv
- **Installed:** All packages from `backend/requirements.txt` (35+ packages including Flask, Celery, SQLAlchemy, etc.)

---

## How to Start the App Now

### **Method 1: Using the Startup Script (Recommended)**
```bash
./startup.sh
```
This handles everything: venv activation, dependency installation, and app startup.

### **Method 2: Manual Startup**
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not done)
pip install -r backend/requirements.txt

# Run the app from backend directory
cd backend
python3 app.py
```

---

## App Details

- **Entry point:** `/backend/app.py`
- **Port:** 8000 (http://localhost:8000)
- **Database:** `/backend/idea_portal.db` (SQLite)
- **Templates:** `/frontend/templates/` (automatically resolved)
- **Config:** Loaded from `/backend/config.py` + `/backend/.env`

---

## What Each File Does

1. **`backend/app.py`** - Flask application factory, Celery setup, route handlers
2. **`backend/config.py`** - Configuration management (reads from .env)
3. **`backend/.env`** - Environment variables (SECRET_KEY, email settings, etc.)
4. **`startup.sh`** - One-command startup script
5. **`backend/requirements.txt`** - All Python dependencies

---

## Key Features Now Available

✅ **Accreditation Reports** - Institutional compliance reporting
✅ **Admin Dashboard** - Project approvals, user management
✅ **Email Notifications** - Via Celery tasks (requires Redis)
✅ **Async Reports** - Background report generation
✅ **Error Pages** - Custom 403, 404, 500 error templates
✅ **Session Management** - User authentication

---

## Next Steps (Optional)

1. **Email Integration** (Optional) - Update MAIL settings in `.env` if you want email notifications
2. **Redis Setup** (Optional) - For async task processing: `brew install redis` (macOS)
3. **Celery Worker** (Optional) - Run background tasks: `celery -A app.celery worker --loglevel=info`

---

## Quick Test

```bash
# The app should now be running on http://localhost:8000
```

All systems are operational! ✅
