"""
Central registry for all registration views.
Import views from here; definitions live in api/v1/<endpoint>/views.py.
"""

from registration.api.v1.answer.views import RegistrationAnswerView
from registration.api.v1.state.views import RegistrationStateView
from registration.api.v1.submit.views import RegistrationSubmitView

__all__ = [
    "RegistrationStateView",
    "RegistrationAnswerView",
    "RegistrationSubmitView",
]
