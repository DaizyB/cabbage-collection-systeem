from django.urls import path
from . import views

urlpatterns = [
    path('submit/<int:quiz_id>/', views.submit_quiz, name='submit-quiz'),
]
