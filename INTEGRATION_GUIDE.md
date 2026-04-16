# IPR Module Integration Guide

## Quick Start Integration

### 1. Create the IPR Module Directory Structure

```
idea_portal/
├── ipr/
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   ├── forms.py
│   ├── utils.py
│   ├── config.py
│   └── README.md
```

### 2. Update Your Database Models

Add to `database/models.py`:

```python
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class IPR(db.Model):
    """Intellectual Property Rights/Patent Model"""
    __tablename__ = 'ipr_records'
    
    ipr_id = db.Column(db.Integer, primary_key=True)
    innovation_title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    ipr_type = db.Column(db.String(50), nullable=False, index=True)
    grant_status = db.Column(db.String(50), nullable=False, index=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.faculty_id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.project_id'), nullable=True)
    application_number = db.Column(db.String(100), unique=True, index=True)
    filing_date = db.Column(db.Date)
    grant_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    faculty = db.relationship('Faculty', backref='iprs', lazy=True)
    project = db.relationship('Project', backref='iprs', lazy=True)
    
    def __repr__(self):
        return f'<IPR {self.ipr_id}: {self.innovation_title}>'
    
    def is_granted(self):
        return self.grant_status == 'Granted'
    
    def is_pending(self):
        return self.grant_status in ['Filed', 'Pending']
    
    def is_rejected(self):
        return self.grant_status == 'Rejected'
```

### 3. Update Main App Configuration

In `app.py` or your app factory:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ipr import ipr_bp

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/idea_portal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(ipr_bp)
    
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

### 4. Fix Routes.py Imports

Update `ipr/routes.py` with correct imports:

```python
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
from database.models import IPR, Faculty, Project  # Update these based on your model names
from database.db import db  # Update based on your db instance
from flask_login import current_user, login_required
from auth.decorators import role_required
from .utils import IPRUtils, IPRReportGenerator
from .forms import IPRCreateForm, IPREditForm, IPRSearchForm
from .config import GRANT_STATUSES, IPR_TYPES

# Rest of the routes...
```

### 5. Update Navigation Menu

In `templates/base.html`, add IPR menu items:

```html
<!-- In your navbar/sidebar -->
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="iprDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
        <i class="fas fa-certificate"></i> IPR Management
    </a>
    <ul class="dropdown-menu" aria-labelledby="iprDropdown">
        <li>
            <a class="dropdown-item" href="{{ url_for('ipr.monitoring') }}">
                <i class="fas fa-eye"></i> Monitoring
            </a>
        </li>
        <li>
            <a class="dropdown-item" href="{{ url_for('ipr.analytics') }}">
                <i class="fas fa-chart-bar"></i> Analytics
            </a>
        </li>
        <li>
            <a class="dropdown-item" href="{{ url_for('ipr.management') }}">
                <i class="fas fa-cogs"></i> Management
            </a>
        </li>
        <li><hr class="dropdown-divider"></li>
        <li>
            <a class="dropdown-item" href="{{ url_for('ipr.export_iprs') }}">
                <i class="fas fa-download"></i> Export Data
            </a>
        </li>
    </ul>
</li>
```

### 6. Database Migration

Create and apply migration:

```bash
# Using Flask-Migrate
flask db init  # If first time
flask db migrate -m "Add IPR/Patent module"
flask db upgrade
```

Or create table directly:

```sql
CREATE TABLE ipr_records (
    ipr_id INT PRIMARY KEY AUTO_INCREMENT,
    innovation_title VARCHAR(255) NOT NULL,
    description LONGTEXT,
    ipr_type VARCHAR(50) NOT NULL,
    grant_status VARCHAR(50) NOT NULL,
    faculty_id INT NOT NULL,
    project_id INT,
    application_number VARCHAR(100) UNIQUE,
    filing_date DATE,
    grant_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_faculty (faculty_id),
    INDEX idx_project (project_id),
    INDEX idx_status (grant_status),
    INDEX idx_type (ipr_type),
    INDEX idx_innovation_title (innovation_title),
    
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(project_id) ON DELETE SET NULL
);
```

### 7. Update Requirements

Add to `requirements.txt`:

```
flask==2.3.0
flask-sqlalchemy==3.0.0
flask-wtf==1.1.1
wtforms==3.0.1
flask-login==0.6.2
sqlalchemy==2.0.0
```

Then install:

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create `.env` file:

```env
FLASK_ENV=development
FLASK_APP=app.py
DATABASE_URL=mysql+pymysql://user:password@localhost/idea_portal
SECRET_KEY=your-secret-key-here
```

### Application Settings

In `config.py`:

```python
class Config:
    """Base configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

## Testing the Integration

### 1. Test Database Connection

```python
# In Python shell
from app import create_app, db
from database.models import IPR

app = create_app()
with app.app_context():
    # Test connection
    db.session.execute('SELECT 1')
    print("Database connection successful!")
    
    # Create test IPR
    test_ipr = IPR(
        innovation_title="Test Innovation",
        ipr_type="Patent",
        grant_status="Filed",
        faculty_id=1
    )
    db.session.add(test_ipr)
    db.session.commit()
    print("Test IPR created successfully!")
```

### 2. Test Routes

```bash
# Start Flask server
python app.py

# Test endpoints in browser or curl
curl http://localhost:5000/admin/ipr/monitoring
curl http://localhost:5000/admin/ipr/analytics
curl http://localhost:5000/admin/ipr/management
```

### 3. Test Forms

```python
# Verify forms are working
from ipr.forms import IPRCreateForm

form = IPRCreateForm()
print("Form fields:", form._fields.keys())
```

## Common Issues and Solutions

### Issue 1: Table doesn't exist

**Solution**:
```bash
flask db upgrade
# If using raw SQL:
# Run the SQL create table script above
```

### Issue 2: Models not found

**Solution**: Ensure imports are correct in routes.py:
```python
from database.models import IPR as db_ipr  # Alias if conflict
```

### Issue 3: Templates not found

**Solution**: Verify template files exist in correct directory:
```
templates/
└── admin/
    ├── iprs.html
    ├── ipr_analytics.html
    └── ipr_management.html
```

### Issue 4: Blueprints not registered

**Solution**: Check app.py has blueprint registration:
```python
from ipr import ipr_bp
app.register_blueprint(ipr_bp)
```

### Issue 5: Static files not loading

**Solution**: Ensure Bootstrap and Font Awesome are in base template:
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

## Production Deployment

### 1. Environment Setup

```bash
# Set environment variables
export FLASK_ENV=production
export DATABASE_URL=mysql+pymysql://user:pass@prod-db/idea_portal
export SECRET_KEY=your-production-secret-key
```

### 2. Database Optimization

```sql
-- Add indexes for performance
CREATE INDEX idx_ipr_status_filing ON ipr_records(grant_status, filing_date);
CREATE INDEX idx_ipr_faculty_type ON ipr_records(faculty_id, ipr_type);
CREATE INDEX idx_ipr_project ON ipr_records(project_id);
```

### 3. Run with WSGI Server

```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Using uWSGI
uwsgi --http :8000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

## Security Considerations

1. **SQL Injection**: All queries use SQLAlchemy ORM (safe by default)
2. **CSRF Protection**: Use `@app.before_request` to check CSRF tokens
3. **Authorization**: Use role decorators on routes
4. **Data Validation**: Use WTForms validators
5. **Rate Limiting**: Implement rate limiting for API endpoints

Example with Flask-Limiter:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@ipr_bp.route('/add', methods=['POST'])
@limiter.limit("10 per minute")
def add_ipr():
    # Route implementation
    pass
```

## Performance Tuning

### 1. Database Query Optimization

```python
# Use eager loading
from sqlalchemy.orm import joinedload

iprs = IPR.query.options(
    joinedload(IPR.faculty),
    joinedload(IPR.project)
).all()
```

### 2. Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@ipr_bp.route('/analytics')
@cache.cached(timeout=300)
def analytics():
    # Cached for 5 minutes
    pass
```

### 3. Pagination

```python
from flask_sqlalchemy import Pagination

@ipr_bp.route('/management')
def management():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    iprs = IPR.query.paginate(page=page, per_page=per_page)
    return render_template('ipr_management.html', iprs=iprs)
```

## Support and Documentation

- See `ipr/README.md` for feature documentation
- See `ipr/config.py` for configuration options
- See `ipr/utils.py` for utility functions
- See `ipr/forms.py` for form usage

## Next Steps

1. ✅ Set up database models
2. ✅ Configure and test routes
3. ✅ Create templates
4. ✅ Add to navigation menu
5. ✅ Run database migrations
6. ✅ Test all features
7. ✅ Deploy to production
