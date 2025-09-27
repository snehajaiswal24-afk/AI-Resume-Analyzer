from flask import Flask, render_template, request, send_file
import os
import PyPDF2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from fpdf import FPDF

app = Flask(__name__)

# ----------------- Job Role Database -----------------
job_roles = {
    "Software Developer": ["python", "java", "c++", "git", "sql", "problem solving"],
    "Data Analyst": ["python", "sql", "excel", "statistics", "data visualization"],
    "Web Developer": ["html", "css", "javascript", "react", "node"],
    "Machine Learning Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pandas", "numpy"],
    "Project Manager": ["leadership", "communication", "teamwork", "time management", "organization"],
    "Digital Marketer": ["seo", "content creation", "social media", "analytics", "creativity"]
}

motivation = {
    "python": "🔥 Add Python projects on GitHub to shine in interviews!",
    "java": "☕ Java practice = confidence in software jobs!",
    "sql": "💾 Build a SQL project using real datasets.",
    "excel": "📊 Learn Pivot Tables + Dashboards = instant upgrade!",
    "html": "🎨 Make a portfolio site to showcase HTML/CSS.",
    "css": "🌈 Add responsive design to stand out!",
    "javascript": "⚡ Build a mini web app with JS to impress.",
    "machine learning": "🤖 Try Kaggle competitions to boost ML skills.",
    "leadership": "👑 Show group projects where you led a team.",
    "communication": "🗣️ Highlight presentations & clear reports.",
    "teamwork": "🤝 Add examples of collaborations.",
    "seo": "📈 Optimize a blog or site with SEO.",
    "content creation": "🎥 Try making YouTube/blog content.",
    "creativity": "✨ Show creative design or project ideas."
}

skills_db = list(set(sum(job_roles.values(), [])))


# ----------------- Resume Processing -----------------
def extract_text(file):
    try:
        if file.filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        else:
            text = file.read().decode("utf-8")
    except Exception as e:
        text = ""
        print("Error reading file:", e)
    return text.lower()


def extract_skills(text):
    return [skill for skill in skills_db if skill in text]


def calculate_match(skills, req_skills):
    matched = set(skills).intersection(set(req_skills))
    missing = set(req_skills) - set(skills)
    score = int((len(matched) / len(req_skills)) * 100)
    return score, list(matched), list(missing)


def suggest_future_roles(user_skills):
    suggestions = {}
    for role, req_skills in job_roles.items():
        matched = set(user_skills).intersection(set(req_skills))
        score = int((len(matched) / len(req_skills)) * 100)
        if score > 0:
            missing = set(req_skills) - set(user_skills)
            suggestions[role] = {"score": score, "missing": list(missing)}
    return suggestions


# ----------------- Routes -----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files["resume"]
        dream_role = request.form.get("dream_role", "").strip()

        text = extract_text(file)
        extracted_skills = extract_skills(text)

        # Role matches
        role_matches = {}
        for role, req_skills in job_roles.items():
            score, matched, missing = calculate_match(extracted_skills, req_skills)
            role_matches[role] = {"score": score, "matched": matched, "missing": missing}

        # Dream role
        dream_match = None
        if dream_role in job_roles:
            score, matched, missing = calculate_match(extracted_skills, job_roles[dream_role])
            dream_match = {"role": dream_role, "score": score, "matched": matched, "missing": missing}

        # Future suggestions
        future_suggestions = suggest_future_roles(extracted_skills)

        # ATS Score = Average of all roles
        ats_score = sum([data["score"] for data in role_matches.values()]) // len(role_matches)

        return render_template("result.html",
                               extracted_skills=extracted_skills,
                               role_matches=role_matches,
                               dream_match=dream_match,
                               motivation=motivation,
                               future_suggestions=future_suggestions,
                               ats_score=ats_score)
    return render_template("index.html")


@app.route("/download-report", methods=["POST"])
def download_report():
    data = request.form.get("report_data")
    report = json.loads(data)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "AI Resume Analyzer Report", ln=True, align="C")

    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Extracted Skills: {report['skills']}")
    pdf.multi_cell(0, 10, f"ATS Score: {report['ats_score']}%")

    for role, details in report["roles"].items():
        pdf.multi_cell(0, 10, f"{role} → {details['score']}% match")
        pdf.multi_cell(0, 10, f"Matched: {details['matched']}")
        pdf.multi_cell(0, 10, f"Missing: {details['missing']}")

    filepath = "static/resume_report.pdf"
    pdf.output(filepath)

    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
