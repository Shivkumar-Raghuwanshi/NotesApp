from django.urls import path
# from django.contrib.auth.views import LoginView
# from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.UserCreate.as_view(), name='signup'),
    path('notes/create/', views.NoteViewSet.as_view({'post': 'create'}), name='note_create'),
    path('notes/', views.NoteViewSet.as_view({'get': 'list'}), name='note_list'),
    path('notes/<int:pk>/', views.NoteViewSet.as_view({'get': 'retrieve'}), name='note_detail'),
    path('notes/<int:pk>/share/', views.NoteViewSet.as_view({'post': 'share'}), name='note_share'),
    path('notes/<int:pk>/update/', views.NoteUpdateView.as_view({'put': 'update'}), name='note_update'),
    path('notes/version-history/<int:note_pk>/', views.NoteHistoryViewSet.as_view({'get': 'list'}), name='note_history'),
]