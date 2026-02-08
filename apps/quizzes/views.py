from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Quiz, Submission
from django.contrib.auth.decorators import login_required


@csrf_exempt
@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        answers = {}
        # Expect JSON payload
        import json

        data = json.loads(request.body.decode('utf-8'))
        answers = data.get('answers', {})
        sub = Submission.objects.create(quiz=quiz, user=request.user, answers=answers)
        sub.grade()
        return JsonResponse({'ok': True, 'score': sub.score, 'passed': sub.passed})
    return JsonResponse({'ok': False}, status=405)
