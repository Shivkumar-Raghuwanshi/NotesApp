from rest_framework import viewsets, mixins, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from difflib import ndiff
from .models import Note, NoteHistory
from .serializers import UserSerializer, NoteSerializer, NoteHistorySerializer
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            login(request, user)
            return Response({'message': 'Login successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
        
class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        owned_notes = Note.objects.filter(owner=user)
        shared_notes = Note.objects.filter(shared_with=user)
        return (owned_notes | shared_notes).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        note = self.get_object()
        if note.owner != request.user:
            return Response({'error': 'You are not the owner of this note.'}, status=status.HTTP_403_FORBIDDEN)

        shared_with_data = request.data  # Assuming the request.data is a list of usernames
        User = get_user_model()

    # Check if shared_with_data is not empty
        if not shared_with_data:
            return Response({'error': 'No users to share with.'}, status=status.HTTP_400_BAD_REQUEST)

    # Filter users based on provided data (usernames)
        users = User.objects.filter(username__in=shared_with_data)

        if not users:
            return Response({'error': 'Invalid usernames.'}, status=status.HTTP_400_BAD_REQUEST)

    # Add users to the shared_with list
        note.shared_with.add(*users)

    # Retrieve the owner name
        owner_name = note.owner.get_full_name() or note.owner.username

    # Retrieve the shared_with user names
        shared_with_names = [user.get_full_name(
        ) or user.username for user in note.shared_with.all()]

        return Response({
            'message': 'Note shared successfully.',
            'owner': owner_name,
            'shared_with': shared_with_names
        })

class NoteUpdateView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(
            Q(owner=self.request.user) | Q(shared_with=self.request.user)
        ).distinct()

    def perform_update(self, serializer):
        note = self.get_object()  # Retrieve the note instance using get_object()
        old_content = note.content
        new_content = serializer.validated_data['content']
        with transaction.atomic():
            serializer.save()

            # Split the old and new content into lines
            old_lines = old_content.split('\n')
            new_lines = new_content.split('\n')

            # Calculate the diff between the old and new lines
            diff = list(ndiff(old_lines, new_lines))

            for line_number, line in enumerate(diff, start=1):
                if line.startswith('+'):
                    # Addition
                    added_line = line[1:].strip()
                    NoteHistory.objects.create(
                        note=serializer.instance,
                        line_numbers=str(line_number),
                        new_content=added_line,
                        operation='add',
                        updated_by=self.request.user
                    )
                elif line.startswith('-'):
                    # Deletion
                    deleted_line = line[1:].strip()
                    NoteHistory.objects.create(
                        note=serializer.instance,
                        line_numbers=str(line_number),
                        old_content=deleted_line,
                        operation='delete',
                        updated_by=self.request.user
                    )
                elif line.startswith('?'):
                    # Update
                    if '?' in line[1:]:
                        old_line, new_line = line[1:].split('?', 1)
                    else:
                        # Handle the case when there is no delimiter
                        old_line = line[1:]
                        new_line = ''

                    NoteHistory.objects.create(
                        note=serializer.instance,
                        line_numbers=str(line_number),
                        old_content=old_line.strip(),
                        new_content=new_line.strip(),
                        operation='update',
                        updated_by=self.request.user
                    )


class NoteHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NoteHistory.objects.all()
    serializer_class = NoteHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        note_id = self.kwargs['note_pk']
        note = Note.objects.get(id=note_id)
        if note.owner == self.request.user or self.request.user in note.shared_with.all():
            return NoteHistory.objects.filter(note=note)
        else:
            return NoteHistory.objects.none()
