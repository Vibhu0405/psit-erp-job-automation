# 🚀 ERP Job Automation Bot (Streamlit)

An automated ERP job application and notification system built with **Python + Streamlit**.

This app:

- Logs into ERP
- Scans job inbox
- Filters jobs based on:
  - Not already applied
  - Last date not expired (IST)
- Automatically applies to eligible jobs
- Extracts complete job description (exact HTML content)
- Sends formatted email notifications via SMTP
- Displays structured results inside Streamlit UI

---

## 🌐 Live Demo

Visit the deployed app here:

👉 https://2401640140215.streamlit.app

Click **"Run Job Automation"** to execute the workflow.

---

## ⚙️ Local Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/erp-job-automation.git
cd erp-job-automation
