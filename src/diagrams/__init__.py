from .cochairs import render as render_cochairs
from .governance import render as render_governance
from .projects import render as render_projects

DIAGRAMS = {
    "cochairs": ("hl7au-cochairs.svg", render_cochairs),
    "governance": ("hl7au-governance.svg", render_governance),
    "projects": ("hl7au-projects.svg", render_projects),
}
