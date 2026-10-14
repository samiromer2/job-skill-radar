import re

SKILLS = {
    "Python": [r"python"],
    "Docker": [r"docker"],
    "AWS": [r"aws", r"amazon web services"],
    "CI/CD": [r"ci/cd", r"github actions", r"jenkins"],
    "SQL": [r"sql"],
    "Kubernetes": [r"kubernetes", r"k8s"],
}

def extract_skills(text: str) -> set[str]:
    text = text.lower()
    return {
        skill for skill, patterns in SKILLS.items()
        if any(re.search(rf"(?<!\w){p}(?!\w)", text) for p in patterns)
    }