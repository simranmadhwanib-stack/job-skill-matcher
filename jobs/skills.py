
import re
import html

# Technical and job-related skills
common_skills = [
    "python", "sql", "excel", "power bi", "tableau",
    "java", "c++", "machine learning", "deep learning",
    "data visualization", "statistics",
    "pandas", "numpy", "scikit-learn", "tensorflow",
    "pytorch", "aws", "azure", "git", "github",
    "mysql", "postgresql", "database",
    "data modeling", "etl", "matplotlib",
    "seaborn", "data cleaning", "data analysis"
]


def clean_text(text):
    # Convert HTML entities
    text = html.unescape(text)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Convert text to lowercase
    return text.lower()


def extract_skills(text):
    if not text:
        return []

    text = clean_text(text)

    found_skills = []

    for skill in common_skills:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):
            found_skills.append(skill)

    return found_skills


def skill_explanations(missing_skills):
    explanations = {}

    for skill in missing_skills:
        explanations[skill] = (
            f"Learn {skill} to improve your suitability "
            "for this job role."
        )

    return explanations
