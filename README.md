# CareerEquity AI
### AI-Powered Employee Workload, Salary Equity & Career Growth Prediction System
> *"Understand Work. Analyse Equity. Build Better Careers."*

CareerEquity AI is an intelligent enterprise workforce analytics web application developed in accordance with the project specification. The platform combines full-stack Django architecture with Scikit-learn Machine Learning models to support workload rebalancing, salary equity auditing, and transparent employee career growth.

---

## 🚀 Key Modules & Capabilities

### 1. Workload Imbalance & Burnout Prevention (ML)
* **Algorithm**: **Random Forest Classifier** (`Alpha/ml_engine/workload_model.py`)
* **Features**: Evaluates active deliverables, total committed hours, task complexity weights ($\text{High} = 3\times, \text{Medium} = 2\times, \text{Low} = 1\times$), actual vs. estimated variance, and overdue penalties.
* **Outputs**: Computes a continuous Workload Intensity Score (0–100) and predicts operational states: `Underutilized`, `Balanced`, `High Workload`, and `Overloaded (Burnout Risk)`.
* **AI Task Redistribution**: Automatically scans team capacity and recommends optimal task reassignments from overloaded employees to available peers.

### 2. Fair Salary Range Prediction & Explainable AI (ML)
* **Algorithm**: **Random Forest Regressor** (`Alpha/ml_engine/salary_model.py`)
* **Features**: Professional tenure, job level tier, verified competencies count, weighted skill proficiency sums, and delivery performance.
* **Output Band**: Predicts market-calibrated compensation bounds (Min, Median, Max) rather than rigid single values.
* **Explainable AI (XAI)**: SHAP-style local feature attribution breaking down exact rupee contributions from experience (+₹2.0L), job level (+₹3.5L), skills (+₹2.5L), and delivery track record.
* **Same-Level Peer Equity**: Computes cohort statistics (Cohort Median, P25, P75) to flag unexplained compensation disparities for HR review.

### 3. Career Progression & Promotion Readiness
* **Engine**: Competency Gap & Readiness Analyzer (`Alpha/ml_engine/career_engine.py`)
* **Interactive Target Role Selection**: Employees can select any target higher position across the organization.
* **Promotion Readiness Meter**: Computes a transparent Readiness Index percentage (0–100%).
* **Granular Competency Mapping**: Separates skills into **Matched Competencies**, **Proficiency Gaps**, and **Missing Competencies**.
* **Personalized Growth Roadmap**: Generates a customized 4-stage milestone timeline (Technical Foundation ➔ Applied Practice ➔ Leadership ➔ Promotion Review).

---

## 🛠️ Technology Stack
* **Backend**: Python 3.12, Django 4.2+ (MVC Architecture, ORM, Role-Based Access Control)
* **Machine Learning**: Scikit-Learn (Random Forest, Decision Trees), NumPy, Pandas, Joblib
* **Frontend**: HTML5, Responsive CSS3, JavaScript, Chart.js (Live dynamic charts)
* **Database**: SQLite (default zero-config out of the box) with optional PostgreSQL support (`USE_POSTGRES=True`)

---

## ⚡ Quick Start & Run Instructions

```bash
# 1. Navigate to the project directory
cd CAREEREQUITY

# 2. Apply database migrations
python manage.py migrate

# 3. Seed realistic showcase dataset (creates HR admin, positions, skills, employees)
python manage.py seed_demo_data

# 4. Start the development server
python manage.py runserver
```

Open your browser at: **`http://127.0.0.1:8000/`**

---

## 🔑 Login Credentials

| Role | Username / ID | Password | Key Showcase Feature |
| :--- | :--- | :--- | :--- |
| **HR Manager / Admin** | `hr_admin` *(or `prtanya53@gmail.com`)* | `password123` | Workforce Intelligence Dashboard, Chart.js Workload Pressure Chart, AI Task Rebalancing Suggestions, Salary Equity Audits |
| **Employee (Alex)** | `alex_dev` *(or `EMP101`)* | `password123` | **Balanced Workload**, AI Salary Prediction Range & XAI Factor Bars, **75% Promotion Readiness** & 4-Stage Growth Roadmap |
| **Employee (Priya)** | `priya_lead` *(or `EMP102`)* | `password123` | **Overloaded / Burnout Alert** case (triggers AI redistribution in HR portal) |
| **Employee (Sneha)** | `sneha_data` *(or `EMP104`)* | `password123` | **Pay Disparity / Salary Audit** review case (below fair market band) |
| **Employee (Rahul)** | `rahul_qa` *(or `EMP103`)* | `password123` | **Underutilized / Capacity Available** peer candidate |

---

## 📁 Repository Structure
```
c:/Users/HP/clg-pro-1/
├── CAREEREQUITY/                  # Core Django & ML Project
│   ├── manage.py                 # Django command-line utility
│   ├── db.sqlite3                # Pre-seeded SQLite database
│   ├── CAREEREQUITY/             # Project settings, URLs, WSGI
│   │   ├── settings.py           # Auto-fallback database config
│   │   ├── urls.py               # Root URL configuration
│   └── Alpha/                    # Main Application
│       ├── models.py             # Relational data schema (Roles, Positions, Tasks, Skills)
│       ├── views.py              # Application controllers with live ML inference
│       ├── urls.py               # Route routing
│       ├── ml_engine/            # Machine Learning Models & Inference
│       │   ├── workload_model.py # RF Classifier + Redistribution Engine
│       │   ├── salary_model.py   # RF Regressor + XAI Factor Attribution
│       │   ├── career_engine.py  # Competency Gap & Roadmap Generator
│       │   ├── trainer.py        # Model serialization script
│       │   └── saved_models/     # Serialized .joblib model files
│       ├── templates/Alpha/      # Modern HTML Templates
│       │   ├── login.html        # Smart role-detecting login
│       │   ├── hr_dashboard.html # 8-page tabbed HR command center
│       │   ├── employee_career.html   # Promotion readiness & roadmap
│       │   ├── employee_salary.html   # Predicted market range & XAI
│       │   └── employee_workload.html # Workload intensity & burnout risk
│       └── static/               # Stylesheets and JavaScript assets
└── README.md                     # Project documentation
```

---

## ⚖️ Governance & Ethical AI Scope
In accordance with responsible AI standards, CareerEquity AI models provide **decision-support estimates**. The system does not make autonomous hiring, termination, or compensation decisions; all personnel actions remain strictly under authorized human review.
