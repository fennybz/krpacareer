import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import re
import io

st.set_page_config(page_title="KrpaCareer — Careers by Grace", page_icon="🙏", layout="wide", initial_sidebar_state="expanded")

# --- CSS + Fonts ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600;700;800&family=Caveat:wght@700&display=swap" rel="stylesheet">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600;700;800&family=Caveat:wght@700&display=swap');
/* Remove Streamlit top padding */
.block-container { padding-top: 1rem !important; }
header[data-testid="stHeader"] { display: none !important; }
body, .stApp { font-family: 'Inter', sans-serif; }
.brand-logo {
    text-align: center; padding: 0 0 5px 0;
}
.brand-name {
    font-family: 'Playfair Display', serif; font-size: 2.8em; font-weight: 900;
    background: linear-gradient(135deg, #f59e0b, #f97316, #ef4444, #ec4899, #8b5cf6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: -1px;
}
.brand-kr { color: #f59e0b; }
.brand-tagline {
    font-family: 'Caveat', cursive; font-size: 1.3em; color: #94a3b8;
    margin-top: -5px; letter-spacing: 1px;
}
.brand-divider {
    height: 3px; border: none; margin: 10px auto 20px auto; width: 60%;
    background: linear-gradient(90deg, transparent, #f59e0b, #8b5cf6, transparent);
}
.job-card { background:linear-gradient(135deg,#1e1e2e,#2d2d44); border:1px solid #3d3d5c; border-radius:12px; padding:20px; margin-bottom:16px; }
.job-card:hover { transform:translateY(-2px); box-shadow:0 8px 25px rgba(0,0,0,0.3); }
.job-title { font-family:'Inter',sans-serif; font-size:1.2em; font-weight:700; color:#60a5fa; margin-bottom:4px; }
.company-name { font-size:1em; color:#c084fc; font-weight:600; }
.job-meta { color:#94a3b8; font-size:0.85em; margin-top:8px; }
.tag { display:inline-block; background:#374151; color:#e2e8f0; padding:3px 10px; border-radius:20px; font-size:0.78em; margin-right:6px; margin-top:6px; }
.tag-remote { background:#065f46; color:#6ee7b7; }
.tag-match { background:#1e3a5f; color:#60a5fa; }
.tag-h1b-yes { background:#065f46; color:#6ee7b7; font-weight:600; }
.tag-h1b-likely { background:#1e3a5f; color:#93c5fd; font-weight:600; }
.tag-h1b-no { background:#7f1d1d; color:#fca5a5; font-weight:600; }
.tag-h1b-unknown { background:#374151; color:#9ca3af; }
.apply-btn { display:inline-block; background:linear-gradient(135deg,#f59e0b,#8b5cf6); color:white!important; padding:8px 20px; border-radius:8px; text-decoration:none; font-weight:600; margin-top:10px; font-family:'Inter',sans-serif; }
.apply-btn:hover { opacity:0.85; color:white!important; }
.stat-card { background:linear-gradient(135deg,#1e1e2e,#2d2d44); border:1px solid #3d3d5c; border-radius:10px; padding:16px; text-align:center; }
.stat-number { font-size:2em; font-weight:800; color:#f59e0b; font-family:'Playfair Display',serif; }
.stat-label { color:#94a3b8; font-size:0.85em; font-family:'Inter',sans-serif; }
.freshness-new { color:#34d399; font-weight:700; }
.freshness-recent { color:#fbbf24; font-weight:600; }
.freshness-older { color:#94a3b8; }
div[data-testid="stSidebar"] { background:linear-gradient(180deg,#0f172a,#1e1b4b); }
div[data-testid="stSidebar"] .stMarkdown h2 { font-family:'Playfair Display',serif; color:#f59e0b; }
</style>
""", unsafe_allow_html=True)

# ─── Role Config ───
ROLES = {
    "Cloud Integration Engineer": {"keywords": ["cloud", "integration", "aws", "azure", "api", "engineer", "devops", "infrastructure"], "cat": "software-dev", "muse_cats": ["Engineering", "IT"]},
    "AI Automation Engineer": {"keywords": ["ai", "automation", "machine learning", "ml", "python", "engineer", "llm", "generative"], "cat": "software-dev", "muse_cats": ["Engineering", "Data Science"]},
    "Cloud Integration & AI Engineer": {"keywords": ["cloud", "ai", "integration", "aws", "api", "machine learning", "engineer"], "cat": "software-dev", "muse_cats": ["Engineering", "IT"]},
    "AWS Cloud/Application Engineer": {"keywords": ["aws", "cloud", "application", "engineer", "lambda", "ec2", "infrastructure", "devops"], "cat": "software-dev", "muse_cats": ["Engineering", "IT"]},
    "Generative AI Engineer": {"keywords": ["ai", "generative", "llm", "gpt", "machine learning", "nlp", "python", "engineer"], "cat": "software-dev", "muse_cats": ["Engineering", "Data Science"]},
    "Solutions/Cloud Solutions Engineer": {"keywords": ["solutions", "cloud", "engineer", "architect", "aws", "azure", "technical"], "cat": "software-dev", "muse_cats": ["Engineering", "IT"]},
    "MuleSoft Integration Engineer": {"keywords": ["mulesoft", "integration", "api", "anypoint", "middleware", "engineer", "java"], "cat": "software-dev", "muse_cats": ["Engineering"]},
    "Salesforce Integration Engineer": {"keywords": ["salesforce", "integration", "api", "apex", "engineer", "crm", "cloud"], "cat": "software-dev", "muse_cats": ["Engineering", "IT"]},
    "Data Engineer": {"keywords": ["data engineer", "data pipeline", "data platform", "etl", "sql", "spark", "snowflake", "warehouse", "databricks", "airflow"], "cat": "data", "muse_cats": ["Data Science", "Engineering", "IT"]},
    "ML Engineer": {"keywords": ["machine learning", "ml engineer", "ai", "python", "tensorflow", "pytorch", "model", "deep learning"], "cat": "data", "muse_cats": ["Data Science", "Engineering"]},
    "DevOps Engineer": {"keywords": ["devops", "ci/cd", "docker", "kubernetes", "aws", "terraform", "infrastructure", "sre"], "cat": "devops-sysadmin", "muse_cats": ["Engineering", "IT"]},
    "Business Intelligence Engineer": {"keywords": ["business intelligence", "bi engineer", "data warehouse", "etl", "sql", "tableau", "power bi", "looker"], "cat": "data", "muse_cats": ["Data Science", "Engineering"]},
    "Business Intelligence Analyst": {"keywords": ["business intelligence", "bi analyst", "analytics", "tableau", "power bi", "sql", "reporting", "dashboards"], "cat": "data", "muse_cats": ["Data and Analytics", "Data Science"]},
    "Data Analyst": {"keywords": ["data analyst", "analytics", "sql", "python", "tableau", "excel", "reporting", "visualization"], "cat": "data", "muse_cats": ["Data and Analytics", "Data Science"]},
    "Senior Data Engineer": {"keywords": ["senior data engineer", "data pipeline", "spark", "snowflake", "airflow", "sql", "python", "data platform"], "cat": "data", "muse_cats": ["Data Science", "Engineering"]},
    "Apache PySpark Developer": {"keywords": ["pyspark", "spark", "apache", "python", "data engineer", "etl", "hadoop", "databricks", "big data"], "cat": "data", "muse_cats": ["Data Science", "Engineering"]},
    "SQL Developer": {"keywords": ["sql developer", "sql", "database", "stored procedures", "plsql", "tsql", "oracle", "sql server", "mysql"], "cat": "data", "muse_cats": ["Data Science", "Engineering", "IT"]},
}

# ─── Resume Parsing ───
def extract_text_from_pdf(uploaded_file):
    from PyPDF2 import PdfReader
    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    text = " ".join(page.extract_text() or "" for page in reader.pages)
    uploaded_file.seek(0)
    return text

def extract_text_from_docx(uploaded_file):
    from docx import Document
    doc = Document(io.BytesIO(uploaded_file.read()))
    text = "\n".join(p.text for p in doc.paragraphs)
    uploaded_file.seek(0)
    return text

SKILL_DB = {
    "cloud": ["aws", "azure", "gcp", "google cloud", "cloud", "ec2", "s3", "lambda", "cloudfront", "terraform", "ecs", "eks", "rds", "dynamodb", "sqs", "sns", "api gateway", "cloudwatch", "iam", "vpc"],
    "integration": ["mulesoft", "anypoint", "api", "rest", "soap", "graphql", "integration", "middleware", "etl", "kafka", "rabbitmq", "webhook", "microservices"],
    "ai_ml": ["ai", "machine learning", "ml", "deep learning", "nlp", "llm", "gpt", "claude", "generative ai", "langchain", "openai", "bedrock", "sagemaker", "tensorflow", "pytorch", "rag", "prompt engineering"],
    "programming": ["python", "java", "javascript", "typescript", "node.js", "react", "sql", "nosql", "bash", "go", "rust", "c#", ".net", "scala", "ruby"],
    "devops": ["docker", "kubernetes", "k8s", "ci/cd", "jenkins", "github actions", "ansible", "helm", "grafana", "prometheus", "datadog", "splunk", "devops", "sre"],
    "salesforce": ["salesforce", "apex", "visualforce", "lightning", "lwc", "soql", "force.com", "heroku", "marketing cloud", "service cloud", "cpq"],
    "data": ["data engineer", "data pipeline", "spark", "hadoop", "snowflake", "redshift", "bigquery", "databricks", "airflow", "dbt", "data warehouse", "pandas"],
    "general": ["agile", "scrum", "jira", "confluence", "git", "linux", "security", "oauth", "saml", "architecture"],
}

def extract_skills(text):
    text_lower = text.lower()
    found = {}
    for cat, skills in SKILL_DB.items():
        matched = [s for s in skills if s.lower() in text_lower]
        if matched:
            found[cat] = matched
    return found

# Major companies known to sponsor H1B visas (from USCIS H1B employer data)
H1B_SPONSOR_COMPANIES = {
    "google", "meta", "amazon", "microsoft", "apple", "netflix", "salesforce",
    "oracle", "ibm", "intel", "cisco", "adobe", "vmware", "nvidia", "qualcomm",
    "uber", "lyft", "airbnb", "stripe", "palantir", "snowflake", "databricks",
    "coinbase", "robinhood", "doordash", "instacart", "pinterest", "snap",
    "twitter", "x corp", "linkedin", "github", "atlassian", "twilio", "okta",
    "datadog", "splunk", "servicenow", "workday", "palo alto networks",
    "crowdstrike", "zscaler", "fortinet", "elastic", "confluent", "mongodb",
    "hashicorp", "cloudflare", "fastly", "akamai", "veeva systems",
    "deloitte", "accenture", "cognizant", "infosys", "tcs", "wipro", "hcl",
    "capgemini", "ey", "ernst & young", "kpmg", "pwc", "mckinsey", "bain",
    "boston consulting", "jpmorgan", "jp morgan", "goldman sachs", "morgan stanley",
    "bank of america", "citigroup", "citi", "wells fargo", "capital one",
    "american express", "visa inc", "mastercard", "paypal", "square", "block",
    "tesla", "spacex", "boeing", "lockheed martin", "raytheon", "northrop grumman",
    "general electric", "ge", "siemens", "honeywell", "3m", "johnson & johnson",
    "pfizer", "merck", "abbvie", "amgen", "gilead", "regeneron", "moderna",
    "unitedhealth", "anthem", "cigna", "humana", "cvs health",
    "walmart", "target", "costco", "home depot", "lowes",
    "samsung", "sony", "toshiba", "panasonic", "lg",
    "sap", "dell", "hp", "hewlett packard", "lenovo",
    "zoom", "slack", "dropbox", "box", "asana", "monday.com",
    "figma", "canva", "notion", "airtable", "miro",
    "epic systems", "cerner", "medidata", "veracyte",
    "walmart global tech", "target tech", "disney", "comcast", "verizon", "at&t",
    "t-mobile", "sprint", "charter communications",
    "red hat", "canonical", "suse", "docker", "github",
    "bloomberg", "thomson reuters", "reuters", "factset",
    "two sigma", "citadel", "jane street", "de shaw", "bridgewater",
    "applied materials", "lam research", "kla", "asml", "synopsys", "cadence",
    "marvell", "broadcom", "texas instruments", "analog devices", "microchip",
}

def detect_h1b_status(job):
    """Scan job title/description for H1B/visa sponsorship signals."""
    text = f"{job.get('title','')} {job.get('description','')}".lower()
    company = job.get("company", "").lower().strip()

    # Negative signals — company explicitly won't sponsor
    no_sponsor = ["no sponsorship", "not sponsor", "no visa sponsor", "cannot sponsor", "will not sponsor",
                  "won't sponsor", "unable to sponsor", "not able to sponsor", "does not sponsor",
                  "without sponsorship", "no h1b", "no h-1b", "us citizens only",
                  "must be a u.s. citizen", "must be us citizen", "permanent resident only",
                  "green card required", "no work visa", "citizen or permanent resident only",
                  "not eligible for sponsorship", "u.s. person", "clearance required",
                  "security clearance", "public trust"]
    for phrase in no_sponsor:
        if phrase in text:
            return "no_sponsor"

    # Positive signals — company sponsors or is open to it
    yes_sponsor = ["h1b sponsor", "h-1b sponsor", "visa sponsor", "sponsorship available",
                   "will sponsor", "h1b transfer", "h-1b transfer", "immigration sponsor",
                   "visa assistance", "work visa sponsor", "open to sponsorship",
                   "sponsorship provided", "h1b friendly", "h-1b friendly",
                   "h1b", "h-1b", "work authorization sponsor", "immigration support",
                   "visa support", "relocation assistance"]
    for phrase in yes_sponsor:
        if phrase in text:
            return "h1b_friendly"

    # Fallback — check if company is a known H1B sponsor
    if company:
        for known in H1B_SPONSOR_COMPANIES:
            if known in company or company in known:
                return "h1b_likely"

    return "unknown"

def compute_match_score(job, resume_skills):
    if not resume_skills:
        return 0, []
    all_skills = set()
    for skills in resume_skills.values():
        all_skills.update(s.lower() for s in skills)
    job_text = f"{job.get('title','')} {job.get('description','')} {job.get('category','')} {' '.join(job.get('tags',[]))}".lower()
    matched = [s for s in all_skills if s in job_text]
    score = min(100, int((len(matched) / max(len(all_skills), 1)) * 250))
    return score, matched

# ─── API Functions ───
@st.cache_data(ttl=300)
def fetch_themuse(query="engineer", page=0, muse_category="Engineering"):
    _non_usa = {"tokyo", "japan", "london", "uk", "united kingdom", "england",
        "berlin", "germany", "paris", "france", "india", "mumbai", "bangalore",
        "bengaluru", "hyderabad", "pune", "chennai", "delhi", "canada", "toronto",
        "vancouver", "montreal", "dublin", "ireland", "australia", "sydney",
        "melbourne", "singapore", "netherlands", "amsterdam", "spain", "madrid",
        "barcelona", "italy", "milan", "rome", "sweden", "stockholm",
        "switzerland", "zurich", "geneva", "austria", "vienna", "poland",
        "warsaw", "portugal", "lisbon", "belgium", "brussels", "norway", "oslo",
        "denmark", "copenhagen", "finland", "helsinki", "czech", "prague",
        "romania", "bucharest", "hungary", "budapest", "israel", "tel aviv",
        "south korea", "seoul", "china", "beijing", "shanghai", "hong kong",
        "taiwan", "brazil", "sao paulo", "mexico", "argentina", "buenos aires",
        "colombia", "philippines", "manila", "indonesia", "vietnam", "thailand",
        "bangkok", "pakistan", "nigeria", "south africa", "kenya", "egypt",
        "new zealand", "auckland", "scotland", "edinburgh", "glasgow", "wales",
        "manchester", "leeds", "bristol", "birmingham", "dubai", "uae",
        "saudi arabia", "qatar", "turkey", "istanbul", "russia", "moscow",
        "ukraine", "kyiv", "malaysia", "kuala lumpur", "bonn", "cologne",
        "munich", "hamburg", "frankfurt", "osaka", "nagoya", "yokohama"}
    try:
        resp = requests.get("https://www.themuse.com/api/public/jobs",
                           params={"page": page, "category": muse_category, "location": "United States"},
                           headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        qwords = [w.lower() for w in query.split() if len(w) > 2] if query else []
        jobs = []
        for j in resp.json().get("results",[]):
            title = j.get("name","")
            company = j.get("company",{}).get("name","")
            locs = ", ".join(loc.get("name","") for loc in j.get("locations",[])) or "See posting"
            # Skip non-USA locations
            if any(nusa in locs.lower() for nusa in _non_usa):
                continue
            desc = re.sub(r'<[^>]+>', ' ', j.get("contents","") or "").strip()
            pub = j.get("publication_date","")
            if qwords:
                txt = f"{title} {desc} {company}".lower()
                if not any(w in txt for w in qwords): continue
            cat_list = j.get("categories",[])
            cat = cat_list[0].get("name","") if cat_list else ""
            lvl_list = j.get("levels",[])
            lvl = lvl_list[0].get("name","") if lvl_list else ""
            jobs.append({"title": title, "company": company, "location": locs,
                         "url": j.get("refs",{}).get("landing_page",""), "date": pub[:19] if pub else "",
                         "category": cat, "job_type": lvl, "salary": "", "tags": [],
                         "description": desc, "source": "TheMuse"})
        return jobs
    except: return []

@st.cache_data(ttl=300)
def fetch_adzuna(query="software engineer", location="us", api_id="", api_key=""):
    if not api_id or not api_key: return []
    try:
        resp = requests.get(f"https://api.adzuna.com/v1/api/jobs/{location}/search/1",
                           params={"app_id": api_id, "app_key": api_key, "what": query, "results_per_page": 50, "sort_by": "date", "max_days_old": 7}, timeout=15)
        resp.raise_for_status()
        return [{"title": j.get("title",""), "company": j.get("company",{}).get("display_name",""),
                 "location": j.get("location",{}).get("display_name",""), "url": j.get("redirect_url",""),
                 "date": j.get("created",""), "category": j.get("category",{}).get("label",""), "job_type": j.get("contract_type",""),
                 "salary": f"${j['salary_min']:,.0f}-${j['salary_max']:,.0f}" if j.get("salary_min") and j.get("salary_max") else "",
                 "tags": [], "description": j.get("description","") or "", "source": "Adzuna"} for j in resp.json().get("results",[])]
    except: return []

@st.cache_data(ttl=300)
def fetch_jobs_live(query="software engineer", api_key="", location="United States"):
    """Fetch from Jobs Live API (Google Jobs — LinkedIn, Indeed, Glassdoor results)."""
    if not api_key: return []
    try:
        headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": "jobs-live.p.rapidapi.com"}
        resp = requests.get("https://jobs-live.p.rapidapi.com/search",
                           params={"query": query, "location": location},
                           headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        results = data.get("results", [])
        jobs = []
        for j in results:
            jobs.append({
                "title": j.get("title", ""),
                "company": j.get("company", ""),
                "location": j.get("location", ""),
                "url": j.get("link", j.get("url", "")),
                "date": j.get("posted_at", j.get("date", "")),
                "category": j.get("via", ""),
                "job_type": "",
                "salary": j.get("salary", ""),
                "tags": [],
                "description": j.get("description", "") or "",
                "source": "Google Jobs (LinkedIn/Indeed/Glassdoor)",
            })
        return jobs
    except: return []

# ─── Helpers ───
def parse_date(date_str):
    if not date_str: return None
    if isinstance(date_str, (int, float)):
        try: return datetime.utcfromtimestamp(date_str)
        except: return None
    if not isinstance(date_str, str): return None
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S+00:00", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try: return datetime.strptime(date_str[:26].replace("+00:00",""), fmt.replace("Z",""))
        except ValueError: continue
    return None

def freshness_label(date_str):
    dt = parse_date(date_str)
    if not dt: return "Unknown", "freshness-older"
    days = (datetime.utcnow() - dt).days
    hours = (datetime.utcnow() - dt).seconds // 3600
    if days == 0:
        return ("Just posted!", "freshness-new") if hours <= 1 else (f"{hours}h ago", "freshness-new")
    elif days <= 2: return f"{days}d ago", "freshness-new"
    elif days <= 7: return f"{days}d ago", "freshness-recent"
    else: return f"{days}d ago", "freshness-older"

def render_job_card(job, idx):
    fresh_text, fresh_class = freshness_label(job["date"])
    tags_html = ""
    # H1B sponsorship tag
    h1b = detect_h1b_status(job)
    if h1b == "h1b_friendly":
        tags_html += '<span class="tag tag-h1b-yes">H1B Friendly</span>'
    elif h1b == "h1b_likely":
        tags_html += '<span class="tag tag-h1b-likely">Likely Sponsors H1B</span>'
    elif h1b == "no_sponsor":
        tags_html += '<span class="tag tag-h1b-no">No Sponsorship</span>'

    if job.get("job_type"):
        cls = "tag tag-remote" if "remote" in job["job_type"].lower() else "tag"
        tags_html += f'<span class="{cls}">{job["job_type"]}</span>'
    if job.get("category"):
        tags_html += f'<span class="tag">{job["category"]}</span>'
    if job.get("salary"):
        tags_html += f'<span class="tag">{job["salary"]}</span>'
    for t in (job.get("tags") or [])[:4]:
        tags_html += f'<span class="tag">{t}</span>'

    # Match score
    match_html = ""
    resume_skills = st.session_state.get("resume_skills")
    if resume_skills:
        score, matched = compute_match_score(job, resume_skills)
        if score >= 70: mc, mb, ml = "#34d399", "#065f46", "Excellent"
        elif score >= 45: mc, mb, ml = "#60a5fa", "#1e3a5f", "Good"
        elif score >= 25: mc, mb, ml = "#fbbf24", "#78350f", "Partial"
        else: mc, mb, ml = "#94a3b8", "#374151", "Low"
        match_html = f'<div style="float:right;text-align:center;background:{mb};border-radius:10px;padding:8px 14px;min-width:80px;"><div style="font-size:1.4em;font-weight:800;color:{mc};">{score}%</div><div style="font-size:0.7em;color:{mc};">{ml} Match</div></div>'
        for m in matched[:5]:
            tags_html += f'<span class="tag tag-match">{m}</span>'

    desc = re.sub(r'<[^>]+>', ' ', job.get("description","")).strip()
    if len(desc) > 200: desc = desc[:200] + "..."

    st.markdown(f"""<div class="job-card">{match_html}
<div class="job-title">{job["title"]}</div><div class="company-name">{job["company"]}</div>
<div class="job-meta">{job.get("location","")} &bull; <span class="{fresh_class}">{fresh_text}</span> &bull; <span class="tag">{job["source"]}</span></div>
<div style="margin-top:8px">{tags_html}</div>
<div style="color:#cbd5e1;font-size:0.85em;margin-top:10px;">{desc}</div>
<a href="{job.get('url','#')}" target="_blank" class="apply-btn">Apply Now</a></div>""", unsafe_allow_html=True)


# ═══════════════════ SIDEBAR ═══════════════════
st.sidebar.markdown("## Filters")

# Multi-role selection
selected_roles = st.sidebar.multiselect(
    "Target Roles (select multiple)",
    list(ROLES.keys()),
    default=["Cloud Integration Engineer", "AI Automation Engineer"],
    help="Select one or more roles — jobs matching ANY selected role will appear"
)

if selected_roles:
    st.sidebar.caption(f"{len(selected_roles)} role(s) selected — click Search Jobs to find matches")

# Build combined search query and keywords from selected roles
combined_keywords = set()
search_queries = []
for role in selected_roles:
    rd = ROLES[role]
    combined_keywords.update(rd["keywords"])
    search_queries.append(role.split("/")[0].replace("&","").strip())

search_query = ", ".join(search_queries[:3]) if search_queries else ""

freshness_filter = st.sidebar.selectbox("Posted within", ["Any time", "Last 24 hours", "Last 3 days", "Last 7 days", "Last 14 days"])
h1b_filter = st.sidebar.selectbox("H1B Sponsorship", ["All Jobs", "H1B Friendly / Likely", "No Sponsorship", "Unknown Only"])

source_filter = st.sidebar.multiselect("Sources", ["TheMuse", "Google Jobs", "Adzuna"],
                                        default=["TheMuse", "Google Jobs"])

st.sidebar.markdown("---")
st.sidebar.markdown("### Resume Upload")
st.sidebar.caption("Upload to see match % on each job")
uploaded_resume = st.sidebar.file_uploader("Resume (PDF or DOCX)", type=["pdf", "docx"], key="resume_upload")

if uploaded_resume:
    if "resume_skills" not in st.session_state or st.session_state.get("resume_name") != uploaded_resume.name:
        with st.sidebar, st.spinner("Analyzing resume..."):
            text = extract_text_from_pdf(uploaded_resume) if uploaded_resume.name.endswith(".pdf") else extract_text_from_docx(uploaded_resume)
            st.session_state.resume_text = text
            st.session_state.resume_skills = extract_skills(text)
            st.session_state.resume_name = uploaded_resume.name
    sk = st.session_state.resume_skills
    st.sidebar.success(f"{uploaded_resume.name} — {sum(len(v) for v in sk.values())} skills")
    with st.sidebar.expander("Detected Skills"):
        for cat, sl in sk.items():
            st.markdown(f"**{cat.replace('_',' ').title()}:** {', '.join(sl)}")
else:
    for k in ["resume_skills","resume_text","resume_name"]:
        st.session_state.pop(k, None)

st.sidebar.markdown("---")
st.sidebar.markdown("### API Keys")
st.sidebar.caption("For Google Jobs (LinkedIn, Indeed, Glassdoor)")
rapidapi_key = st.sidebar.text_input("RapidAPI Key", type="password", help="Your RapidAPI key for Google Jobs / Jobs Live API")
adzuna_id = st.sidebar.text_input("Adzuna App ID", type="password")
adzuna_key = st.sidebar.text_input("Adzuna API Key", type="password")
adzuna_country = st.sidebar.selectbox("Adzuna Country", ["us","gb","ca","au","de","fr","in"], index=0) if adzuna_id else "us"

sort_options = ["Newest first", "Company A-Z", "Title A-Z"]
if st.session_state.get("resume_skills"): sort_options.insert(0, "Best Match")
sort_by = st.sidebar.selectbox("Sort by", sort_options)

st.sidebar.markdown("---")
st.sidebar.markdown("### Bookmarks")
if "bookmarks" not in st.session_state: st.session_state.bookmarks = []
st.sidebar.caption(f"{len(st.session_state.bookmarks)} saved")
if st.sidebar.button("Clear bookmarks"): st.session_state.bookmarks = []

# ═══════════════════ MAIN ═══════════════════
st.markdown("""
<div class="brand-logo">
    <div class="brand-name">KrpaCareer</div>
    <div class="brand-tagline">Careers by Grace</div>
</div>
<hr class="brand-divider">
""", unsafe_allow_html=True)

col_s, col_c = st.columns([1, 5])
with col_s:
    search_clicked = st.button("Search Jobs", type="primary", use_container_width=True)
with col_c:
    if st.button("Clear Cache & Refresh"):
        st.cache_data.clear()
        st.rerun()

# Auto-search on first load if roles are selected
needs_search = search_clicked or (selected_roles and "all_jobs" not in st.session_state)

if needs_search:
    with st.spinner("Fetching jobs from all sources..."):
        all_jobs = []

        # Build ONE combined query for paid APIs (JSearch/Adzuna) to save quota
        # e.g. "Cloud Integration Engineer OR AI Automation Engineer OR Data Engineer"
        combined_query = " OR ".join(selected_roles[:5]) if selected_roles else "software engineer"

        # Build per-role queries for free APIs (no quota concerns)
        free_queries = set()
        muse_cats_to_search = set()
        for role in selected_roles:
            parts = role.replace("/", " ").replace("&", " ").split()
            free_queries.add(" ".join(parts[:3]))
            for mc in ROLES[role].get("muse_cats", ["Engineering"]):
                muse_cats_to_search.add(mc)
        if not free_queries:
            free_queries.add("engineer")
        if not muse_cats_to_search:
            muse_cats_to_search.add("Engineering")

        # TheMuse — search each category with multiple pages
        if "TheMuse" in source_filter:
            for mc in muse_cats_to_search:
                for pg in range(3):
                    all_jobs.extend(fetch_themuse(query=search_query, page=pg, muse_category=mc))

        # Google Jobs — search PER ROLE for maximum results
        # Each query returns 10-20 jobs, so 5 roles = 50-100+ results
        if "Google Jobs" in source_filter and rapidapi_key:
            for role in selected_roles:
                all_jobs.extend(fetch_jobs_live(query=role, api_key=rapidapi_key))

        # Adzuna — search per role
        if "Adzuna" in source_filter and adzuna_id and adzuna_key:
            for role in selected_roles:
                all_jobs.extend(fetch_adzuna(query=role, api_id=adzuna_id, api_key=adzuna_key, location=adzuna_country))

        # Deduplicate by title+company
        seen = set()
        unique = []
        for j in all_jobs:
            key = (j["title"].lower().strip(), j["company"].lower().strip())
            if key not in seen:
                seen.add(key)
                unique.append(j)
        st.session_state.all_jobs = unique

all_jobs = st.session_state.get("all_jobs", [])

# Freshness filter
if freshness_filter != "Any time":
    max_days = {"Last 24 hours":1, "Last 3 days":3, "Last 7 days":7, "Last 14 days":14}[freshness_filter]
    cutoff = datetime.utcnow() - timedelta(days=max_days)
    all_jobs = [j for j in all_jobs if not parse_date(j["date"]) or parse_date(j["date"]) >= cutoff]

# H1B filter
if h1b_filter != "All Jobs":
    if h1b_filter == "H1B Friendly / Likely":
        all_jobs = [j for j in all_jobs if detect_h1b_status(j) in ("h1b_friendly", "h1b_likely")]
    elif h1b_filter == "No Sponsorship":
        all_jobs = [j for j in all_jobs if detect_h1b_status(j) == "no_sponsor"]
    elif h1b_filter == "Unknown Only":
        all_jobs = [j for j in all_jobs if detect_h1b_status(j) == "unknown"]

# Relevance filter — multi-word phrases match as phrases, single words match individually
if combined_keywords or search_query:
    # Separate multi-word phrases from single words
    phrase_kws = [k.lower() for k in combined_keywords if " " in k]  # e.g. "data engineer", "data pipeline"
    single_kws = [k.lower() for k in combined_keywords if " " not in k]
    # Add search query words
    for w in search_query.replace(",", " ").split():
        if len(w) > 2 and w.lower() not in single_kws:
            single_kws.append(w.lower())

    if phrase_kws or single_kws:
        scored = []
        for j in all_jobs:
            title = j.get("title","").lower()
            body = f"{title} {j.get('description','')} {' '.join(j.get('tags',[]))} {j.get('category','')}".lower()
            relevance = 0
            # Phrase matches in title are worth a lot
            for pk in phrase_kws:
                if pk in title: relevance += 10
                elif pk in body: relevance += 3
            # Single word matches
            for kw in single_kws:
                if kw in title: relevance += 3
                elif kw in body: relevance += 1
            if relevance >= 4:
                j["_relevance"] = relevance
                scored.append(j)
        # Sort by relevance first, then let the user's sort override
        scored.sort(key=lambda x: x.get("_relevance", 0), reverse=True)
        all_jobs = scored

# Sort
if sort_by == "Best Match" and st.session_state.get("resume_skills"):
    all_jobs.sort(key=lambda j: compute_match_score(j, st.session_state.resume_skills)[0], reverse=True)
elif sort_by == "Newest first":
    all_jobs.sort(key=lambda j: parse_date(j.get("date","")) or datetime.min, reverse=True)
elif sort_by == "Company A-Z":
    all_jobs.sort(key=lambda j: j.get("company","").lower())
elif sort_by == "Title A-Z":
    all_jobs.sort(key=lambda j: j.get("title","").lower())

# Stats
sources_found = set(j["source"] for j in all_jobs)
today_count = sum(1 for j in all_jobs if parse_date(j.get("date","")) and (datetime.utcnow() - parse_date(j["date"])).days == 0)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="stat-card"><div class="stat-number">{len(all_jobs)}</div><div class="stat-label">Jobs Found</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="stat-card"><div class="stat-number">{today_count}</div><div class="stat-label">Posted Today</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="stat-card"><div class="stat-number">{len(sources_found)}</div><div class="stat-label">Sources</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="stat-card"><div class="stat-number">{len(st.session_state.bookmarks)}</div><div class="stat-label">Bookmarked</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Tabs
tab_list, tab_resume, tab_bm, tab_export, tab_setup = st.tabs(["Job Listings", "Resume Profile", "Bookmarks", "Export", "API Setup"])

with tab_list:
    if not all_jobs:
        st.info("Select your **target roles** in the sidebar and click **Search Jobs** to find matching positions.")
    else:
        per_page = 20
        total_pages = max(1, (len(all_jobs) + per_page - 1) // per_page)
        page = st.number_input("Page", 1, total_pages, 1, 1)
        start = (page - 1) * per_page
        end = start + per_page
        st.caption(f"Showing {start+1}-{min(end, len(all_jobs))} of {len(all_jobs)} jobs")
        for idx, job in enumerate(all_jobs[start:end]):
            render_job_card(job, idx)
            if st.button("Bookmark", key=f"bm_{start+idx}"):
                if job not in st.session_state.bookmarks:
                    st.session_state.bookmarks.append(job)
                    st.toast(f"Bookmarked: {job['title']}")

with tab_resume:
    if st.session_state.get("resume_skills"):
        st.markdown("### Your Skills Profile")
        st.caption(f"From: **{st.session_state.get('resume_name','')}**")
        sk = st.session_state.resume_skills
        cols = st.columns(min(len(sk), 4))
        for i, (cat, sl) in enumerate(sk.items()):
            with cols[i % len(cols)]:
                st.markdown(f'<div class="stat-card"><div class="stat-number">{len(sl)}</div><div class="stat-label">{cat.replace("_"," ").title()}</div></div>', unsafe_allow_html=True)
                for s in sl: st.markdown(f"- {s}")
        if all_jobs:
            st.markdown("---")
            st.markdown("### Top 10 Matches")
            scored = [(j, *compute_match_score(j, sk)) for j in all_jobs]
            scored.sort(key=lambda x: x[1], reverse=True)
            for j, score, matched in scored[:10]:
                if score > 0:
                    st.markdown(f"**{score}%** — [{j['title']}]({j['url']}) at {j['company']} — {', '.join(matched[:5])}")
    else:
        st.info("Upload your resume (PDF/DOCX) in the sidebar to see your skills profile and match scores.")

with tab_bm:
    if not st.session_state.bookmarks:
        st.info("No bookmarked jobs yet. Click 'Bookmark' on any listing.")
    else:
        for idx, job in enumerate(st.session_state.bookmarks):
            render_job_card(job, f"bm_{idx}")
            if st.button("Remove", key=f"rm_{idx}"):
                st.session_state.bookmarks.pop(idx)
                st.rerun()

with tab_export:
    if all_jobs:
        export_jobs = [{**j, "h1b_status": {"h1b_friendly":"H1B Friendly","h1b_likely":"Likely Sponsors","no_sponsor":"No Sponsorship","unknown":"Unknown"}[detect_h1b_status(j)]} for j in all_jobs]
        df = pd.DataFrame(export_jobs)[["title","company","location","date","category","job_type","salary","h1b_status","url","source"]]
        df.columns = ["Title","Company","Location","Posted","Category","Type","Salary","H1B Status","Apply Link","Source"]
        st.download_button("Download CSV", df.to_csv(index=False), "job_listings.csv", "text/csv", use_container_width=True)
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("Search for jobs first.")
    if st.session_state.bookmarks:
        bdf = pd.DataFrame(st.session_state.bookmarks)[["title","company","location","date","url","source"]]
        st.download_button("Download Bookmarks CSV", bdf.to_csv(index=False), "bookmarks.csv", "text/csv", use_container_width=True)

with tab_setup:
    st.markdown("""
### Free Sources (no keys needed)
- **TheMuse** — 700+ US engineering jobs from major companies

### Optional API Keys (free tiers)

**Google Jobs** (LinkedIn, Indeed, Glassdoor — USA)
1. Go to [RapidAPI - Jobs Live](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jobs-live)
2. Sign up free
3. Copy your X-RapidAPI-Key and paste in sidebar

**Adzuna** (US, UK, CA, AU, DE, FR, IN)
1. Go to [Adzuna Developer](https://developer.adzuna.com/)
2. Register free — 250 requests/month
3. Paste App ID and Key in sidebar
    """)
