from django.db import models

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

class Company(models.Model):
    first_name = models.CharField(max_length=55)
    last_name = models.CharField(max_length=55)
    state = models.CharField(max_length=55)
    country = models.CharField(max_length=55)
    mobile = models.CharField(max_length=55)
    

class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    role = models.CharField(max_length=7, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    
class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    teacher = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    marks = models.IntegerField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE,null=True)  # ForeignKey to associate with Quiz
    question_text = models.TextField(blank=True, null=True)
    options = ArrayField(models.CharField(max_length=255, blank=True, null=True), size=4) 
    correct_answer = models.CharField(max_length=255)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text


class StudentQuizSubmission(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    answers = models.JSONField()  # Stores student's answers
    marks_awarded = models.IntegerField(default=0)  # Marks awarded by teacher after submission
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.quiz}"

class PerformanceReport(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE,blank=True,null=True)
    total_marks = models.IntegerField()  
    marks_obtained = models.IntegerField()  
    grade = models.CharField(max_length=2)  
    def __str__(self):
        return f"Report for {self.student} - {self.quiz}"
