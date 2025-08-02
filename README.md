# ⚡ Energy Sector BI Dashboard

An interactive dashboard for visualizing energy sector data using Python, Dash, and Plotly.

![Dashboard Preview](docs/screenshot.png) <!-- Optional: add a screenshot in /docs -->

---

## 📊 Features

- Date range filtering
- Tabs for different insights:
  - Overview
  - Generation Analysis
  - Customer Trends
  - Infrastructure Tracking
  - Renewable Energy Focus
- Responsive layout using Dash Bootstrap Components

---

## 🚀 Demo

🌐 Try it live: [https://your-render-link.onrender.com](https://your-render-link.onrender.com)  
_(Replace with actual link once deployed)_

---

## 🗂️ Dataset

- File: `merged1_energy_data.csv`
- Format: Time-series energy metrics by month

---

## 📦 Tech Stack

- Dash 2.17.1
- Plotly 5.17.0
- Pandas 2.1.4
- Gunicorn (for deployment)
- Render (cloud hosting)

---

## ⚙️ Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/elvis07jr/energy-dashboard.git
   cd energy-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python app.py
   ```

---

## 🌍 Deployment on Render

### ✅ Required Files

- `app.py` *(or update `Procfile` if different)*
- `requirements.txt`
- `Procfile`
- `merged1_energy_data.csv`

### 🔧 `Procfile` Example:

If your main file is `app.py`:
```
web: gunicorn app:server
```

If your file is named `dashboard.py`, use:
```
web: gunicorn dashboard:server
```

---

## 📸 Screenshots

Place images in the `/docs` folder. Example embed:
```markdown
![Dashboard](docs/screenshot.png)
```

---

## 📬 Contact

Built with 💡 by [@elvis07jr](https://github.com/elvis07jr)

---
## Project Structure
---
```bash
energy-dashboard/
├── app.py                 # Your main dashboard file
├── requirements.txt       # Dependencies
├── your_energy_data.csv  # Your CSV file
├── .gitignore            # Git ignore file
├── Procfile              # For Heroku deployment
└── README.md             # Project description
```
