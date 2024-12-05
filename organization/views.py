from rest_framework import generics
from django.shortcuts import render
from .models import *
from organization.serializers import *
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status,mixins
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import Group
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token

class CourseTitlesView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = CourseSerializer

    def list(self, request, *args, **kwargs):
        courses = Course.objects.all()  # Fetch all course objects\
        return render(request, 'pages/home.html', {'courses': courses})
    
class CreateCourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(teacher=self.request.user)

    def list(self, request, *args, **kwargs):
        courses = self.get_queryset()
        return render(request, 'course_farm.html', {'courses': courses})
    
    def create(self, request, *args, **kwargs):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(teacher=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show quizzes for courses taught by the authenticated teacher
        return Quiz.objects.filter(course__teacher=self.request.user)

    def list(self, request, *args, **kwargs):
        quizzes = self.get_queryset()
        courses = Course.objects.filter(teacher=self.request.user) 
        return render(request, 'create_quiz.html', {'quizzes': quizzes, 'courses': courses})

    def create(self, request, *args, **kwargs):
        course_id = request.data.get('course')
        quiz_title = request.data.get('title')

        # Check if a quiz with the given title for the selected course already exists
        existing_quiz = Quiz.objects.filter(course_id=course_id, title=quiz_title).first()

        if existing_quiz:
            # If the quiz exists, append the questions to the existing quiz
            new_questions_data = request.data.get('questions', [])
            for question_data in new_questions_data:
                # Create question instances and link them to the existing quiz
                Question.objects.create(quiz=existing_quiz, **question_data)

            return Response({"message": "Questions appended to the existing quiz."}, status=status.HTTP_200_OK)
        else:
            # If the quiz doesn't exist, create a new one
            return super().create(request, *args, **kwargs)

class TeacherViewset(viewsets.ViewSet):
    def list(self, request, *args, **kwargs):
        return render(request, 'teacher_dashboard.html')
    
class StudentCourseViewSet(viewsets.ReadOnlyModelViewSet):  # Only allows read operations
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Show all available courses for students
        return Course.objects.all()

    def list(self, request, *args, **kwargs):
        courses = self.get_queryset()
        return render(request, 'student_dashboard.html', {'courses': courses})

class GetQuizViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()

    def list(self, request, *args, **kwargs):
        # Fetch all quizzes and serialize the data
        quizzes = self.get_queryset()
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # Fetch a single quiz by ID
        quiz = self.get_object()
        serializer = self.get_serializer(quiz)
        # return Response(serializer.data, status=status.HTTP_200_OK)
        return render(request, 'take_quiz.html', {'quiz': serializer.data})

# This viewset renders the quiz page based on quiz ID
class QuizRetrieveViewSet(viewsets.ViewSet):
    queryset = Quiz.objects.all()  # Define the queryset for quizzes

    def retrieve(self, request, pk=None):
        try:
            quiz = Quiz.objects.get(pk=pk)  # Retrieve quiz based on the primary key (ID)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Use the serializer to serialize the quiz data
        serializer = QuizSerializer(quiz)

        # Render the quiz in the 'take_quiz.html' template with serialized data
        return render(request, 'take_quiz.html', {'quiz': serializer.data})

class StudentQuizSubmissionViewSet(viewsets.ModelViewSet):
    queryset = StudentQuizSubmission.objects.all()
    serializer_class = StudentQuizSubmissionSerializer
    
    def list(self, request, *args, **kwargs):
        quiz_id = request.query_params.get('quiz_id')
        if quiz_id:
            submission = StudentQuizSubmission.objects.filter(student=request.user, quiz_id=quiz_id)
        else:
            submission = StudentQuizSubmission.objects.filter(student=request.user)
        serializer = self.get_serializer(submission, many=True)
        # return Response(serializer.data)
        return render(request, 'quiz_submit.html', {'reports': serializer.data})

    def create(self, request, *args, **kwargs):
        student = request.user  # Assuming authenticated student
        course_name = request.data.get('course_name')  # Get course name from request data

        try:
            # Fetch the course based on the course name
            course = Course.objects.get(name=course_name)
            # Fetch the quiz where the title matches the course name
            quiz = Quiz.objects.filter(course=course, title=course.name).latest('created_at')
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found for this course"}, status=status.HTTP_404_NOT_FOUND)

        # Process the answers submitted by the student
        answers = request.data.get('answers')
        questions = Question.objects.filter(quiz=quiz)
        
        marks_awarded = 0
        for question in questions:
            submitted_answer = answers.get(str(question.id)) 
            if submitted_answer == question.correct_answer:
                marks_awarded += question.points  
        submission = StudentQuizSubmission.objects.create(
            student=student,
            quiz=quiz,
            answers=answers,
            marks_awarded=marks_awarded
        )
        
        # Return the success response with the marks awarded
        return Response({'message': 'Submission successful', 'marks_awarded': marks_awarded}, status=status.HTTP_201_CREATED)


class PerformanceReportViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReport.objects.all()
    serializer_class = PerformanceReportSerializer

    def list(self, request, *args, **kwargs):
        reports = PerformanceReport.objects.filter(student=request.user)
        serializer = self.get_serializer(reports, many=True)
        # return Response(serializer.data)
        return render(request, 'student_report.html', {'reports': serializer.data})

    def create(self, request, *args, **kwargs):
        quiz = Quiz.objects.get(id=request.data['quiz'])
        student = request.user
        marks_obtained = request.data['marks_obtained']
        total_marks = quiz.marks

        # Calculate grade
        grade = self.calculate_grade(marks_obtained, total_marks)

        # Create report
        report = PerformanceReport.objects.create(
            student=student,
            quiz=quiz,
            total_marks=total_marks,
            marks_obtained=marks_obtained,
        )
        return Response({'message': 'Report created successfully'}, status=status.HTTP_201_CREATED)

    def calculate_grade(self, marks_obtained, total_marks):
        percentage = (marks_obtained / total_marks) * 100
        if percentage >= 90:
            return 'A'
        elif percentage >= 75:
            return 'B'
        elif percentage >= 50:
            return 'C'
        else:
            return 'F'
        