from django.urls import path
from . import views

app_name = "instruction"

urlpatterns = [
    path("api/sessions/start", view.start_session, name="start_session"),
    path("api/annotations/save/", views.save_annotation, name="save_annotation"),
    path("api/flags/add/", views.flag_slide, name="flag_slide"),
]
