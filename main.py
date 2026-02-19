import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import pytz
import pandas as pd

# -------------------------
# STREAMLIT PAGE CONFIG
# -------------------------
st.set_page_config(page_title="ERP Job Automation", layout="wide")

st.title("🚀 ERP Job Automation Bot")

# -------------------------
# LOAD ENV VARIABLES
# -------------------------
LOGIN_URL = os.getenv("LOGIN_URL")
JOB_INBOX_URL = os.getenv("JOB_INBOX_URL")
ERP_USERNAME = os.getenv("ERP_USERNAME")
ERP_PASSWORD = os.getenv("ERP_PASSWORD")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("SENDER_EMAIL_ADDRESS")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# -------------------------
# RUN BUTTON
# -------------------------
if st.button("Run Job Automation"):

    st.info("Logging into ERP...")

    session = requests.Session()
    session.post(LOGIN_URL, data={
        "username": ERP_USERNAME,
        "password": ERP_PASSWORD
    })

    response = session.get(JOB_INBOX_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    ist = pytz.timezone("Asia/Kolkata")
    current_time = datetime.now(ist)

    jobs = soup.find_all("div", class_="row g-0")[:5]

    results = []
    email_sent_jobs = []

    for job in jobs:

        company_name = job.find("td", string="Company Name")
        company_name = company_name.find_next("td").text.strip() if company_name else "Unknown"

        last_date_tag = job.find("td", string="Last Date to Apply")
        expired = False
        last_date_text = ""

        if last_date_tag:
            last_date_text = last_date_tag.find_next("td").text.strip()
            try:
                last_date = datetime.strptime(last_date_text, "%d %b %Y [%H:%M]")
                last_date = ist.localize(last_date)
                if current_time > last_date:
                    expired = True
            except:
                pass

        applied_img = job.find("img", src=lambda x: x and "applied_successfully.png" in x)

        if applied_img:
            results.append([company_name, "Already Applied", applied_img.get("title", "")])
            continue

        if expired:
            results.append([company_name, "Expired", last_date_text])
            continue

        link_tag = job.find("a", href=True)
        if not link_tag:
            continue

        link = link_tag["href"]
        job_id = link.strip("/").split("/")[-2]

        # OPEN JOB PAGE
        job_page = session.get(link)
        job_soup = BeautifulSoup(job_page.text, "html.parser")

        panel_body = job_soup.find("div", class_="panel-body")

        if panel_body:
            for form in panel_body.find_all("form"):
                form.decompose()
            full_html_content = str(panel_body)
        else:
            full_html_content = "<p>No content found</p>"

        # APPLY
        interested_url = f"https://erp.psit.ac.in/CR/Student_job_inbox_update/1/{job_id}"
        session.get(interested_url)

        # BUILD EMAIL
        html_content = f"""
        <html>
        <body>
        <h2>{company_name}</h2>
        {full_html_content}
        <hr>
        <p>Automated ERP Job Notification</p>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Job Applied: {company_name}"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = RECEIVER_EMAIL
        msg.attach(MIMEText(html_content, "html"))

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECEIVER_EMAIL, msg.as_string())
            server.quit()

            email_sent_jobs.append(company_name)
            results.append([company_name, "Applied + Email Sent", "Success"])

        except Exception as e:
            results.append([company_name, "Email Failed", str(e)])

    # -------------------------
    # DISPLAY RESULTS
    # -------------------------
    df = pd.DataFrame(results, columns=["Company", "Status", "Details"])

    st.success("Process Completed ✅")
    st.dataframe(df, use_container_width=True)

    if email_sent_jobs:
        st.subheader("📧 Emails Sent For:")
        for name in email_sent_jobs:
            st.write(f"✔ {name}")
