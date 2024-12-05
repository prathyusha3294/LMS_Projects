from rest_framework import serializers
from .models import Course, Quiz, Question, StudentQuizSubmission, PerformanceReport,UserProfile
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login

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

class SignUpSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password','role']  
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        User = get_user_model()  # Get the user model class
        role = validated_data.pop('role')  # Extract the role from validated_data

        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])  # Set the password correctly
        user.save()

        # Create user profile with the extracted role
        UserProfile.objects.create(user=user, role=role)
        return user


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()