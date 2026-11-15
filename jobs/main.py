
print("========== UPDATED MAIN.PY LOADED ==========")

from jobs.api import fetch_jobs
from jobs.skills import extract_skills, skill_explanations


ROLE_TYPICAL_SKILLS = {
    "data analyst": ["sql", "excel", "python", "power bi", "tableau", "statistics", "data visualization"],
    "business analyst": ["sql", "excel", "power bi", "data analysis", "communication"],
    "data scientist": ["python", "sql", "machine learning", "statistics", "pandas", "numpy"],
    "software engineer": ["python", "java", "git", "data structures", "algorithms", "database"],
}


def normalize_skills(user_skills):
    if isinstance(user_skills, str):
        user_skills = user_skills.split(",")

    return list(dict.fromkeys(
        skill.strip().lower()
        for skill in user_skills
        if skill.strip()
    ))


def calculate_role_score(title, desired_role):
    title = title.lower().strip()
    desired_role = desired_role.lower().strip()

    if desired_role in title:
        if any(level in title for level in [
            "manager", "director", "lead", "staff", "principal"
        ]):
            return 70

        if "senior" in title or "sr." in title:
            return 85

        return 100

    related_roles = {
        "data analyst": [
            "business analyst",
            "reporting analyst",
            "business intelligence",
            "data analytics",
            "analytics specialist",
            "data support analyst",
            "reporting specialist"
        ],
        "software engineer": [
            "software developer",
            "application developer",
            "backend developer",
            "frontend developer"
        ],
        "data scientist": [
            "machine learning engineer",
            "ml engineer"
        ],
        "business analyst": [
            "business intelligence analyst",
            "data analyst"
        ],
        "project manager": [
            "program manager"
        ]
    }

    for related_role in related_roles.get(desired_role, []):
        if related_role in title:
            return 70

    return 0


def match_jobs(user_skills, desired_role):
    user_skills = normalize_skills(user_skills)
    desired_role = desired_role.strip().lower()

    if not desired_role:
        raise ValueError("Please enter a desired job role.")

    if not user_skills:
        raise ValueError("Please enter at least one skill.")

    job_data = fetch_jobs(desired_role)
    jobs = job_data.get("jobs", [])

    results = []

    print("\n========== MATCHING DEBUG ==========")
    print("TOTAL JOBS:", job_data.get("total_count", 0))
    print("JOBS RECEIVED:", len(jobs))
    print("USER SKILLS:", user_skills)
    print("DESIRED ROLE:", desired_role)

    for job in jobs:
        title = job.get("title") or ""
        company = job.get("company") or "Unknown"
        location = job.get("location") or "Not specified"
        salary = job.get("salary") or "Not specified"
        description = job.get("description") or job.get("snippet") or ""
        link = job.get("link") or ""

        role_score = calculate_role_score(title, desired_role)

        if role_score == 0:
            print("FILTERED OUT:", title)
            continue

        required_skills = extract_skills(title + " " + description)
        skill_source = "posting"
        if not required_skills:
            required_skills = ROLE_TYPICAL_SKILLS.get(desired_role, [])
            skill_source = "role_typical" if required_skills else "none"

        matched_skills = [
            skill for skill in required_skills
            if skill in user_skills
        ]

        missing_skills = [
            skill for skill in required_skills
            if skill not in user_skills
        ]

        if required_skills:
            skill_score = (
                len(matched_skills) / len(required_skills)
            ) * 100

            if skill_source == "posting":
                overall_score = role_score * 0.5 + skill_score * 0.5
            else:
                overall_score = role_score * 0.7 + skill_score * 0.3

        else:
            skill_score = None
            overall_score = float(role_score)

        explanations = skill_explanations(missing_skills)

        missing_skill_details = []

        for skill in missing_skills:
            missing_skill_details.append({
                "name": skill,
                "explanation": explanations.get(
                    skill,
                    f"Learn {skill} to improve your job readiness."
                )
            })

        print("\nJOB:", title)
        print("COMPANY:", company)
        print("SNIPPET:", repr(description)[:200])
        print("ROLE SCORE:", role_score)
        print("SKILL SOURCE:", skill_source)
        print("REQUIRED SKILLS:", required_skills)
        print("MATCHED SKILLS:", matched_skills)
        print("MISSING SKILLS:", missing_skills)
        print("SKILL SCORE:", skill_score)
        print("OVERALL SCORE:", overall_score)

        results.append({
            "company": company,
            "title": title,
            "location": location,
            "salary": salary,
            "role_score": round(role_score, 2),
            "required_skills": required_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skill_details,
            "skill_score": (
                round(skill_score, 2)
                if skill_score is not None else None
            ),
            "overall_score": round(overall_score, 2),
            "skill_source": skill_source,
            "link": link
        })

    results.sort(key=lambda x: x["overall_score"], reverse=True)

    print("\nRELEVANT JOBS:", len(results))
    print("========== END DEBUG ==========")

    return {
        "desired_role": desired_role,
        "user_skills": user_skills,
        "total_jobs_found": job_data.get("total_count", 0),
        "relevant_jobs": len(results),
        "results": results
    }
