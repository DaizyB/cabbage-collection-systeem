from django.db import models
from django.conf import settings


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    pass_mark = models.IntegerField(default=80)  # percent


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    prompt = models.TextField()
    correct_answer = models.TextField()


class Submission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answers = models.JSONField(default=dict)
    score = models.IntegerField(null=True, blank=True)
    passed = models.BooleanField(default=False)

    def grade(self):
        # naive auto-grading: match answer text equality
        total = self.quiz.questions.count()
        if total == 0:
            self.score = 0
            self.passed = False
            self.save()
            return
        correct = 0
        for q in self.quiz.questions.all():
            ans = self.answers.get(str(q.id))
            if ans and ans.strip().lower() == q.correct_answer.strip().lower():
                correct += 1
        self.score = int((correct / total) * 100)
        self.passed = self.score >= self.quiz.pass_mark
        self.save()
