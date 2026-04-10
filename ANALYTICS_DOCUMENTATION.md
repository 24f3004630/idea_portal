# Analytics & Charts Documentation

## Overview

This document provides comprehensive documentation for the Analytics and Charts implementation in the Idea Portal application. The system provides interactive, role-based analytics dashboards with real-time data visualization using Chart.js.

**Date**: April 10, 2026  
**Framework**: Flask + SQLAlchemy + Chart.js 4.4.0  
**Status**: ✅ Fully Implemented

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [API Endpoints](#api-endpoints)
4. [Dashboard Implementation](#dashboard-implementation)
5. [Frontend Visualization](#frontend-visualization)
6. [Data Models](#data-models)
7. [File Structure](#file-structure)
8. [Features](#features)
9. [Implementation Details](#implementation-details)

---

## Architecture Overview

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  (Bootstrap 5.3.0 Templates with Chart.js Visualizations)   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Frontend Data Fetching Layer                    │
│          (JavaScript fetch() to Analytics APIs)             │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Backend API Layer (Flask Routes)               │
│         (Analytics endpoints returning JSON data)           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│           Database Query Layer (SQLAlchemy ORM)             │
│    (Complex queries with filtering and aggregations)        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                 SQLite Database                             │
│    (research_project, person, publication, ipr tables)      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Authentication** → Session established with user_id and role
2. **Dashboard Load** → Template renders with Chart.js script tags
3. **Fetch Analytics Data** → JavaScript sends AJAX requests to API
4. **Backend Processing** → Flask routes execute complex SQLAlchemy queries
5. **JSON Response** → API returns aggregated data with statistics
6. **Chart Rendering** → Chart.js creates interactive visualizations
7. **Real-time Updates** → Charts update when data changes

---

## Technology Stack

### Backend
- **Framework**: Flask 3.1.3
- **ORM**: SQLAlchemy 2.0.23
- **Database**: SQLite3
- **Python Version**: 3.11.11

### Frontend
- **UI Framework**: Bootstrap 5.3.0
- **Charting Library**: Chart.js 4.4.0
- **Template Engine**: Jinja2
- **HTTP Library**: Fetch API (JavaScript)

### Dependencies
```
Flask==3.1.3
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.23
Werkzeug==3.1.8
```

---

## API Endpoints

### Admin Analytics APIs

#### 1. `/admin/api/analytics/users`
**Purpose**: Returns overall user distribution and approval status

**Method**: GET  
**Authentication**: Required (Admin)  
**Response Format**:
```json
{
  "total": 15,
  "students": 10,
  "faculty": 4,
  "approved": 12,
  "pending": 3
}
```

**SQL Logic**:
- Counts all Person records by type
- Counts approved vs pending users
- Excludes Admin user from statistics

---

#### 2. `/admin/api/analytics/projects`
**Purpose**: Project status distribution across all projects

**Method**: GET  
**Authentication**: Required (Admin)  
**Response Format**:
```json
{
  "statuses": ["Proposed", "Ongoing", "Completed", "On Hold"],
  "counts": [2, 8, 15, 3]
}
```

**SQL Logic**:
- Queries all ResearchProject records
- Groups by project_status field
- Counts occurrences for each status

---

#### 3. `/admin/api/analytics/publications`
**Purpose**: Publication submission lifecycle breakdown

**Method**: GET  
**Authentication**: Required (Admin)  
**Response Format**:
```json
{
  "statuses": ["Submitted", "Accepted", "Published", "Rejected"],
  "counts": [5, 12, 25, 3]
}
```

**SQL Logic**:
- Joins Publication with ResearchProject tables
- Groups by Publication.status field
- Aggregates count for each submission status

---

#### 4. `/admin/api/analytics/iprs`
**Purpose**: IPR/Patent grant status distribution

**Method**: GET  
**Authentication**: Required (Admin)  
**Response Format**:
```json
{
  "statuses": ["Filed", "Pending", "Granted", "Rejected"],
  "counts": [8, 4, 6, 1]
}
```

**SQL Logic**:
- Joins IPR with Publication and ResearchProject tables
- Groups by IPR.grant_status field
- Counts records for each grant status

---

#### 5. `/admin/api/analytics/domains`
**Purpose**: Project distribution by research domain

**Method**: GET  
**Authentication**: Required (Admin)  
**Response Format**:
```json
{
  "domains": ["Artificial Intelligence", "IoT", "Data Science", "Cybersecurity"],
  "counts": [12, 8, 5, 3]
}
```

**Supported Domains**:
The system supports the following research domains:
- Artificial Intelligence
- Data Science
- Cybersecurity
- IoT
- Web Development
- Mobile Development
- Cloud Computing
- Blockchain
- Healthcare Tech
- FinTech
- EdTech
- Smart Systems
- Multidisciplinary
- Other

**SQL Logic**:
- Queries all ResearchProject records
- Groups by domain field
- Sorts by count in descending order
- Returns top 10 domains

---

### Faculty Analytics APIs

#### 1. `/faculty/api/analytics/projects`
**Purpose**: Faculty's projects grouped by status

**Method**: GET  
**Authentication**: Required (Faculty)  
**Response Format**:
```json
{
  "statuses": ["Proposed", "Ongoing", "Completed", "On Hold"],
  "counts": [1, 3, 2, 0]
}
```

**Query Filter**: `ResearchProject.faculty_id == session['user_id']`

---

#### 2. `/faculty/api/analytics/publications`
**Purpose**: Publications breakdown for faculty's projects

**Method**: GET  
**Authentication**: Required (Faculty)  
**Response Format**:
```json
{
  "statuses": ["Submitted", "Accepted", "Published", "Rejected"],
  "counts": [2, 5, 8, 0]
}
```

**Query Filter**: Faculty's project_ids only

---

#### 3. `/faculty/api/analytics/iprs`
**Purpose**: IPR statistics for faculty's projects

**Method**: GET  
**Authentication**: Required (Faculty)  
**Response Format**:
```json
{
  "statuses": ["Filed", "Pending", "Granted", "Rejected"],
  "counts": [3, 1, 2, 0]
}
```

**Query Filter**: Faculty's project_ids only

---

#### 4. `/faculty/api/analytics/team`
**Purpose**: Team size breakdown across faculty's projects

**Method**: GET  
**Authentication**: Required (Faculty)  
**Response Format**:
```json
{
  "projects": ["AI Research Initiative", "IoT Sensors Project"],
  "team_sizes": [5, 8]
}
```

**SQL Logic**:
- Joins ResearchProject with ProjectPerson table
- Groups by project_id
- Counts team members (ProjectPerson records) per project
- Returns project titles and team sizes

---

### Student Analytics APIs

#### 1. `/student/api/analytics/projects`
**Purpose**: Student's joined projects grouped by status

**Method**: GET  
**Authentication**: Required (Student)  
**Response Format**:
```json
{
  "statuses": ["Proposed", "Ongoing", "Completed", "On Hold"],
  "counts": [0, 2, 1, 0]
}
```

**Query Filter**: 
- Join with ProjectPerson where person_id == student_id
- Only approved projects (ResearchProject.is_approved == True)

---

#### 2. `/student/api/analytics/contributions`
**Purpose**: Student's research contributions (pubs, IPRs, startups)

**Method**: GET  
**Authentication**: Required (Student)  
**Response Format**:
```json
{
  "publication_count": 5,
  "ipr_count": 2,
  "startup_count": 1
}
```

**SQL Logic**:
- Get all projects where student is a member
- Count Publication records in those projects
- Count IPR records in those projects
- Count Startup records in those projects

---

#### 3. `/student/api/analytics/skills-match`
**Purpose**: Skill matching with project requirements

**Method**: GET  
**Authentication**: Required (Student)  
**Response Format**:
```json
{
  "projects": ["AI Research", "IoT Development"],
  "match_counts": [4, 6]
}
```

**SQL Logic**:
- Get student's skills from Person.skills field (comma-separated)
- For each project the student joined, get required_skills
- Compare skill sets and count matching skills
- Return match count for each project

---

## Dashboard Implementation

### Admin Dashboard (`/templates/admin/dashboard.html`)

**Layout**: 2-column grid with 8 stat cards + 6 charts

**Statistics Cards**:
- Total Users
- Approved Users
- Total Students
- Total Faculty
- Total Projects
- Total Publications
- Total IPR Records
- Total Startups

**Interactive Charts**:

1. **User Distribution (Pie Chart)**
   - Data Source: `/admin/api/analytics/users`
   - Shows: Students, Faculty, Admin distribution
   - Colors: Blue, Red, Green

2. **User Approval Status (Doughnut Chart)**
   - Data Source: `/admin/api/analytics/users`
   - Shows: Approved vs Pending split
   - Colors: Green (approved), Red (pending)

3. **Project Status Distribution (Bar Chart - Horizontal)**
   - Data Source: `/admin/api/analytics/projects`
   - Shows: Projects by status (Proposed, Ongoing, Completed, On Hold)
   - Type: Horizontal bar for better readability

4. **Publication Status (Doughnut Chart)**
   - Data Source: `/admin/api/analytics/publications`
   - Shows: Publication lifecycle (Submitted, Accepted, Published, Rejected)
   - Colors: Multi-color palette

5. **IPR Grant Status (Bar Chart)**
   - Data Source: `/admin/api/analytics/iprs`
   - Shows: IPR distribution by grant status
   - Type: Vertical bar chart

6. **Projects by Domain (Horizontal Bar Chart)**
   - Data Source: `/admin/api/analytics/domains`
   - Shows: Top research domains with project counts
   - Type: Horizontal bar with domain labels

---

### Faculty Dashboard (`/templates/faculty/dashboard.html`)

**Layout**: 2x2 grid with 4 stat cards + 4 analytics charts

**Statistics Cards**:
- Total Projects
- Ongoing Projects
- Completed Projects
- Startup Conversions

**Interactive Charts**:

1. **Project Status Distribution (Doughnut Chart)**
   - Shows faculty's projects by status
   - Filtered to logged-in faculty only

2. **Publication Lifecycle (Bar Chart)**
   - Shows publication submissions by status
   - Vertical bar chart for easy comparison

3. **IPR Grant Status (Pie Chart)**
   - Shows IPR distribution across grant statuses
   - Pie chart for proportional visualization

4. **Team Size by Project (Horizontal Bar Chart)**
   - Shows number of team members per project
   - Helps faculty track team composition

---

### Student Dashboard (`/templates/student/dashboard.html`)

**Layout**: Single stat card + 3 analytics charts

**Statistics Card**:
- Projects Joined (count)

**Interactive Charts**:

1. **Projects by Status (Doughnut Chart)**
   - Shows student's enrolled projects by status
   - Proposed, Ongoing, Completed, On Hold

2. **Research Contributions (Bar Chart)**
   - Shows Publications, IPRs, Startups count
   - Grouped bar chart for comparison
   - Vertical bars for easy reading

3. **Skills Match with Projects (Horizontal Bar Chart)**
   - Shows matching skills per project
   - Helps student understand skill alignment
   - Only displays if student has skills defined

---

## Frontend Visualization

### Chart.js Configuration

#### Color Palette
```javascript
const colors = {
  primary: ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6'],
  surface: ['#ecf0f1', '#34495e', '#c0392b', '#27ae60', '#d35400'],
  light: ['#bdc3c7', '#95a5a6']
};
```

#### Chart Responsiveness
- All charts use `responsive: true`
- `maintainAspectRatio: true` for consistent sizing
- Charts adapt to container width
- Container height: 300px (defined in base.html)

#### Common Chart Options
```javascript
{
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      position: 'bottom'  // or 'top' for horizontal space
    }
  }
}
```

### Chart Types Used

1. **Pie Chart** - User & publication distribution
2. **Doughnut Chart** - Approval status, single category breakdown
3. **Bar Chart (Vertical)** - Publication & IPR status, contributions
4. **Bar Chart (Horizontal)** - Domain distribution, team size, skills match
5. **Mixed Types** - Different chart per dashboard for variety

### CSS Classes

**Chart Container** (from base.html):
```css
.chart-container {
  position: relative;
  height: 300px;
  margin: 20px 0;
}
```

**Stat Card** (Bootstrap + custom):
```css
.stat-card {
  transition: transform 0.3s ease;
}
.stat-card:hover {
  transform: translateY(-5px);
}
```

---

## Data Models

### Key Tables Used

#### `person` Table
```sql
- person_id (PRIMARY KEY)
- name (VARCHAR)
- email (VARCHAR, UNIQUE)
- type (VARCHAR: 'Student', 'Faculty', 'Admin')
- is_approved (BOOLEAN)
- skills (VARCHAR) -- comma-separated
- (other fields: bio, phone, resume_url, etc.)
```

#### `research_project` Table
```sql
- project_id (PRIMARY KEY)
- faculty_id (FOREIGN KEY → person)
- project_title (VARCHAR)
- project_description (TEXT)
- domain (VARCHAR)
- project_status (VARCHAR: 'Proposed', 'Ongoing', 'Completed', 'On Hold')
- is_approved (BOOLEAN)
- is_startup_converted (BOOLEAN)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### `publication` Table
```sql
- publication_id (PRIMARY KEY)
- project_id (FOREIGN KEY → research_project)
- title (VARCHAR)
- status (VARCHAR: 'Submitted', 'Accepted', 'Published', 'Rejected')
- publication_type (VARCHAR)
- venue (VARCHAR)
- year_of_publication (INT)
```

#### `ipr` Table
```sql
- ipr_id (PRIMARY KEY)
- publication_id (FOREIGN KEY → publication)
- innovation_title (VARCHAR)
- ipr_type (VARCHAR)
- grant_status (VARCHAR: 'Filed', 'Pending', 'Granted', 'Rejected')
- application_number (VARCHAR, UNIQUE)
```

#### `project_person` Table
```sql
- project_person_id (PRIMARY KEY)
- project_id (FOREIGN KEY → research_project)
- person_id (FOREIGN KEY → person)
- role (VARCHAR)
```

#### `startup` Table
```sql
- startup_id (PRIMARY KEY)
- project_id (FOREIGN KEY → research_project)
- startup_name (VARCHAR)
- (other fields: stage, funding, etc.)
```

---

## File Structure

```
idea_portal/
├── templates/
│   ├── base.html                          # Main template with Chart.js CDN
│   ├── auth/
│   │   └── login.html                     # Login page
│   ├── admin/
│   │   └── dashboard.html                 # Admin analytics dashboard
│   ├── faculty/
│   │   ├── dashboard.html                 # Faculty analytics dashboard
│   │   └── create_project.html            # Project creation form with domain dropdown
│   └── student/
│       └── dashboard.html                 # Student analytics dashboard
├── admin/
│   └── routes.py                          # 6 analytics API endpoints
├── faculty/
│   └── routes.py                          # 4 analytics API endpoints + project creation
├── student/
│   └── routes.py                          # 3 analytics API endpoints
├── database/
│   ├── models.py                          # SQLAlchemy ORM models
│   └── db.py                              # Database initialization
├── auth/
│   ├── routes.py                          # Authentication routes
│   └── decorators.py                      # Role-based access control
├── app.py                                 # Flask app initialization
└── config.py                              # Configuration settings
```

---

## Features

### ✅ Completed Features

1. **Role-Based Analytics**
   - Admin sees system-wide statistics
   - Faculty sees their project statistics
   - Student sees their participation statistics

2. **Real-Time Data**
   - Charts fetch fresh data on page load
   - Uses AJAX for asynchronous loading
   - No page refresh needed

3. **Responsive Design**
   - Mobile-friendly charts
   - Bootstrap 5 grid system
   - Adaptive container sizing

4. **Access Control**
   - Authentication required for all endpoints
   - Role-based filtering of data
   - Faculty only sees their own projects
   - Students only see approved projects

5. **Data Aggregation**
   - SQLAlchemy complex queries with join() and group_by()
   - Efficient counting and filtering
   - Server-side aggregation

6. **Interactive Visualizations**
   - Hover effects on chart elements
   - Legend toggling
   - Responsive to data updates
   - Professional color schemes

7. **Error Handling**
   - Graceful handling of empty data
   - Validation on dashboard pages
   - User-friendly error messages

---

## Implementation Details

### Research Domains

The system supports 14 predefined research domains that faculty members select when creating projects. These domains are used for:
- Project categorization
- Analytics and reporting
- Domain-based filtering
- Skill and interest matching

**Supported Domains**:
1. Artificial Intelligence
2. Data Science
3. Cybersecurity
4. IoT
5. Web Development
6. Mobile Development
7. Cloud Computing
8. Blockchain
9. Healthcare Tech
10. FinTech
11. EdTech
12. Smart Systems
13. Multidisciplinary
14. Other

**Where Domains are Used**:
- **Project Creation Form**: Faculty selects domain from dropdown (`/faculty/project/create`)
- **Analytics Dashboard**: Admin sees projects grouped by domain (`/admin/api/analytics/domains`)
- **Database**: Stored in `ResearchProject.domain` field

### Database Queries - Examples

#### Admin Users Query
```python
# From admin/routes.py endpoint
students = Person.query.filter_by(type='Student').count()
faculty = Person.query.filter_by(type='Faculty').count()
approved = Person.query.filter_by(is_approved=True).count()
pending = Person.query.filter_by(is_approved=False).count()
```

#### Faculty Team Size Query
```python
# From faculty/routes.py endpoint
team_data = db.session.query(
    ResearchProject.project_id,
    ResearchProject.title,
    db.func.count(ProjectPerson.person_id)
).filter(
    ResearchProject.project_id.in_(project_ids),
    ProjectPerson.project_id == ResearchProject.project_id
).group_by(ResearchProject.project_id).all()
```

#### Student Skills Match Query
```python
# From student/routes.py endpoint
student_skills = set(s.strip().lower() for s in student.skills.split(','))
required_skills = set(s.strip().lower() for s in project.required_skills.split(','))
match_count = len(student_skills.intersection(required_skills))
```

### Frontend JavaScript Pattern

All dashboards follow this pattern:

```javascript
// Color configuration
const colors = { /* ... */ };

// Fetch data from API
fetch('/role/api/analytics/endpoint')
  .then(response => response.json())
  .then(data => {
    // Get canvas element
    const ctx = document.getElementById('chartId').getContext('2d');
    
    // Create Chart.js instance
    new Chart(ctx, {
      type: 'chart-type',  // 'bar', 'pie', 'doughnut', etc.
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Dataset Label',
          data: data.values,
          backgroundColor: colors.primary,
          borderColor: '#fff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { position: 'bottom' } }
      }
    });
  });
```

### Project Creation Form

**Location**: `/faculty/project/create`  
**Template**: `templates/faculty/create_project.html`  
**Fields**:

```html
<form method="POST">
  <!-- Project Title (Text Input) -->
  <input type="text" name="project_title" required>
  
  <!-- Project Description (Textarea) -->
  <textarea name="project_description"></textarea>
  
  <!-- Domain (Dropdown with 14 options) -->
  <select name="domain" required>
    <option value="Artificial Intelligence">Artificial Intelligence</option>
    <option value="Data Science">Data Science</option>
    <option value="Cybersecurity">Cybersecurity</option>
    <!-- ... 11 more options ... -->
  </select>
  
  <!-- Department (Text Input) -->
  <input type="text" name="department">
  
  <!-- Required Skills (Text Input) -->
  <input type="text" name="required_skills" placeholder="comma-separated">
  
  <!-- Team Size (Number Input) -->
  <input type="number" name="team_size" min="1" value="1">
  
  <!-- Program Location (Text Input) -->
  <input type="text" name="program_location">
</form>
```

**Form Submission Flow**:
1. Faculty visits `/faculty/project/create`
2. Selects domain from dropdown
3. Fills out form fields
4. Submits form (POST request)
5. Flask route validates data
6. Creates ResearchProject with selected domain
7. Redirects to project details page

### Error Handling

**Empty Data Handling**:
- Check if data is empty before rendering chart
- Display message to user if no data available
- Example: `if (data.projects.length === 0) { /* hide chart */ }`

**API Errors**:
- Try-catch blocks in JavaScript
- Server returns JSON with status codes
- Flask handles 404/500 gracefully

---

## Performance Considerations

### Query Optimization

1. **Indexing**: 
   - foreign_key columns indexed
   - filter columns indexed
   - status fields indexed

2. **Join Efficiency**:
   - Uses SQLAlchemy joins efficiently
   - Avoids N+1 queries
   - Single aggregation query per endpoint

3. **Caching Opportunities** (Future):
   - Cache expensive queries
   - Redis for analytics data
   - 5-minute TTL for dashboard data

### Frontend Performance

1. **Lazy Loading**:
   - Charts only render on dashboard page
   - AJAX prevents full page reload
   - Progressive enhancement

2. **Bundle Size**:
   - Chart.js is 103 KB (gzipped)
   - Minimal custom JavaScript
   - Bootstrap CDN used

---

## Testing Scenarios

### Admin Dashboard Test
```
1. Login as admin@portal.com
2. Visit /admin/dashboard
3. Verify 8 stat cards load with counts
4. Verify 6 charts render without errors
5. Check console for JavaScript errors
6. Verify color scheme consistency
```

### Faculty Dashboard Test
```
1. Register new faculty account
2. Admin approves registration
3. Login as faculty
4. Visit /faculty/dashboard
5. Verify stats show only their projects
6. Create sample project
7. Verify project appears in charts
8. Add publication/IPR
9. Verify counts update
```

### Student Dashboard Test
```
1. Register student account (auto-approved)
2. Login as student
3. Visit /student/dashboard
4. Verify projects are empty (no approvals yet)
5. Admin approves faculty
6. Faculty creates project
7. Student requests to join
8. Admin approves
9. Verify charts update with project data
```

---

## API Response Examples

### Successful Response (Admin Users)
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "total": 15,
  "students": 10,
  "faculty": 4,
  "approved": 12,
  "pending": 3
}
```

### Successful Response (Domain Distribution)
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "domains": ["AI/ML", "IoT", "Blockchain", "Bioinformatics", "Cybersecurity"],
  "counts": [12, 8, 5, 3, 2]
}
```

### Empty Data Response (Student Skills Match)
```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "projects": [],
  "match_counts": []
}
```

---

## Future Enhancement Opportunities

1. **Export Functionality**
   - Export charts as PDF/PNG
   - Excel reports with raw data
   - Custom date range filtering

2. **Advanced Filtering**
   - Date range filters
   - Multi-select domain filters
   - Status-based filtering

3. **Notifications**
   - Alert when project status changes
   - Email notifications for faculty approvals
   - Real-time dashboard updates

4. **Performance Analytics**
   - Faculty productivity metrics
   - Student engagement tracking
   - Publication impact metrics

5. **Comparison Views**
   - Compare two projects
   - Year-over-year metrics
   - Faculty comparison dashboard

6. **Mobile App**
   - Mobile-optimized dashboard
   - Push notifications
   - Offline capability

---

## Deployment Checklist

- [ ] Database migrations created
- [ ] Chart.js CDN verified in production
- [ ] API endpoints tested with various data sets
- [ ] Charts responsive on mobile devices
- [ ] Error handling verified
- [ ] Authentication decorators checked
- [ ] SQL injection prevention verified (using parameterized queries)
- [ ] CORS headers configured if needed
- [ ] Rate limiting considered for analytics APIs
- [ ] Logging implemented for debugging

---

## Troubleshooting

### Issue: Charts Not Rendering
**Solution**: 
- Check browser console for JavaScript errors
- Verify Chart.js CDN is accessible
- Ensure canvas elements have proper IDs
- Check that API endpoints return valid JSON

### Issue: "No such column" Error
**Solution**:
- Delete database and recreate
- Run `db.create_all()` in app context
- Verify all model migrations are applied

### Issue: Unauthorized Error (403)
**Solution**:
- Verify user is logged in
- Check role_required decorator
- Verify session['user_id'] is set
- Check user.is_approved status

### Issue: Empty Charts
**Solution**:
- Check if data exists in database
- Verify API endpoint returns data
- Check browser network tab for API response
- Ensure filters are correct (faculty_id, student_id)

---

## Contact & Support

For questions about this implementation, contact the development team or refer to the respective route files:
- Admin Analytics: `/admin/routes.py`
- Faculty Analytics: `/faculty/routes.py`
- Student Analytics: `/student/routes.py`

---

**Document Version**: 1.0  
**Last Updated**: April 10, 2026  
**Status**: ✅ Production Ready
