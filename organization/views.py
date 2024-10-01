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

    # def retrieve(self, request, *args, **kwargs):
    #     return render(request, 'create_course.html')
    
# Teacher Views
# class TeacherCourseViewSet(viewsets.ModelViewSet):
#     serializer_class = CourseSerializer
#     permission_classes = [AllowAny]

#     def get_queryset(self):
#         # Only show courses for the authenticated teacher
#         return Course.objects.filter(teacher=self.request.user)

#     def list(self, request, *args, **kwargs):
#         courses = self.get_queryset()
#         return render(request, 'create_farm.html', {'courses': courses})

#     def create(self, request, *args, **kwargs):
#         # Overriding the create method to handle course creation
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(teacher=request.user)  # Assign the course to the logged-in teacher
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        return super().create(request, *args, **kwargs)


# Student Views
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

# Submission Views
# class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):  # Only allows read operations
#     serializer_class = SubmissionSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         # Show submissions for the logged-in student
#         return Submission.objects.filter(student=self.request.user)

#     def list(self, request, *args, **kwargs):
#         submissions = self.get_queryset()
#         return render(request, 'view_marks.html', {'submissions': submissions})
    


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
        quiz = Quiz.objects.get(id=request.data['quiz'])
        answers = request.data['answers']
        questions = Question.objects.filter(quiz=quiz)
        marks_awarded = 0
        for question in questions:
            submitted_answer = answers.get(str(question.id))  # Get the answer from the submitted answers
            if submitted_answer == question.correct_answer:  # Check if the answer is correct
                marks_awarded += question.points  # Add points for the correct answer
        submission = StudentQuizSubmission.objects.create(
            student=student,
            quiz=quiz,
            answers=answers,
            marks_awarded=marks_awarded  # Set the calculated marks
        )
        
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
            grade=grade
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