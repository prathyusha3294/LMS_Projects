from django.urls import path,include
from rest_framework import routers 
from organization.views import * 

app_name = 'organization'

course_create_router = routers.SimpleRouter()
course_create_router.register('master/course/create',CreateCourseViewSet,basename='create_course')

course_titles_router = routers.SimpleRouter()
course_titles_router.register('master/course/titles', CourseTitlesView, basename='course_titles')

# teacher_router = routers.SimpleRouter()
# teacher_router.register('master/course', TeacherCourseViewSet, basename = 'teacher')

quiz_router = routers.SimpleRouter()
quiz_router.register('master/quiz', QuizViewSet, basename = 'quiz')

student_router = routers.SimpleRouter()
student_router.register('master/student', StudentCourseViewSet, basename = 'student')

quizretrive_router = routers.SimpleRouter()
quizretrive_router.register('quizretrive', QuizRetrieveViewSet, basename = 'quizrrr')

get_quiz_router = routers.SimpleRouter()
get_quiz_router.register('getquiz', GetQuizViewSet, basename='getquiz')

student_submission_router = routers.SimpleRouter()
student_submission_router.register('submission',StudentQuizSubmissionViewSet,basename='Student')

performance_report_router = routers.SimpleRouter()
performance_report_router.register('performance/report',PerformanceReportViewSet, basename='performance')

teacher_router = routers.SimpleRouter()
teacher_router.register('master/teacher',TeacherViewset, basename='teacher')

# signup_router = routers.SimpleRouter()
# signup_router.register('signup',SignUpView, basename='usersignup')

# login_router = routers.SimpleRouter()
# login_router.register('login', SignInView, basename='usersignin')


urlpatterns = [
    path('',include(course_create_router.urls)),
    path('',include(course_titles_router.urls)),
    path('',include(teacher_router.urls)),
    path('',include(quiz_router.urls)),
    path('',include(quizretrive_router.urls)),
    path('',include(get_quiz_router.urls)),
    path('',include(student_router.urls)),
    path('',include(student_submission_router.urls)),
    path('',include(performance_report_router.urls)),
    # path('',include(signup_router.urls)),
    # path('',include(login_router.urls)),
    # path('register/', signup_page, name='signup'),
    # path('signin/', signin_page, name='signin')
]
