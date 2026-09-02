from .cochairs import render as render_cochairs
from .projects import render as render_projects

DIAGRAMS = {
    "cochairs": ("hl7au-cochairs.svg", render_cochairs),
    "projects": ("hl7au-projects.svg", render_projects),
}
