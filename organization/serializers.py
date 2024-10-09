from rest_framework import serializers
from .models import Course, Quiz, Question, StudentQuizSubmission, PerformanceReport

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'teacher']
        extra_kwargs = {
            'teacher': {'read_only': True}  # Set the teacher field as read-only
        }
        



class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)  # Allows nested questions

    class Meta:
        model = Quiz
        fields = ['title', 'marks', 'course', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')  # Pop the questions data
        quiz = Quiz.objects.create(**validated_data)  # Create the quiz instance
        
        # Create the questions for the quiz
        for question_data in questions_data:
            # Explicitly pass the quiz object while creating questions
            Question.objects.create(quiz=quiz, **question_data) 
        
        return quiz
    
    
class StudentQuizSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentQuizSubmission
        fields = ['student', 'quiz', 'answers', 'marks_awarded']

class PerformanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReport
        fields = ['student', 'quiz', 'total_marks', 'marks_obtained', 'grade']

class UserSignUpSerializer(serializers.Serializer):
    role = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, required=True)
    mobile = serializers.CharField(required=False,allow_blank=True)
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    country = serializers.CharField(required=True)