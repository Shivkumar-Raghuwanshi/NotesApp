from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Note, NoteHistory
from .serializers import UserSerializer, NoteSerializer, NoteHistorySerializer

class ModelTests(TestCase):
    def test_note_model(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword')
        note = Note.objects.create(
            title='Test Note', content='This is a test note.', owner=user)
        self.assertEqual(note.title, 'Test Note')
        self.assertEqual(note.content, 'This is a test note.')
        self.assertEqual(note.owner, user)

    def test_note_history_model(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword')
        note = Note.objects.create(
            title='Test Note', content='This is a test note.', owner=user)
        history = NoteHistory.objects.create(note=note, line_numbers='1', old_content='This is a test note.',
                                             new_content='This is an updated note.', operation='update', updated_by=user)
        self.assertEqual(history.note, note)
        self.assertEqual(history.line_numbers, '1')
        self.assertEqual(history.old_content, 'This is a test note.')
        self.assertEqual(history.new_content, 'This is an updated note.')
        self.assertEqual(history.operation, 'update')
        self.assertEqual(history.updated_by, user)

        # Access the history through the related_name 'history'
        note_history = note.history.all()
        self.assertIn(history, note_history)


class SerializerTests(TestCase):
    def test_user_serializer(self):
        user_data = {'username': 'testuser',
                     'email': 'test@example.com', 'password': 'testpassword'}
        serializer = UserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())

    def test_note_serializer(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword')
        note = Note.objects.create(
            title='Test Note', content='This is a test note.', owner=user)
        serializer = NoteSerializer(instance=note)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Note')
        self.assertEqual(data['content'], 'This is a test note.')
        self.assertEqual(data['owner'], 'testuser')

    def test_note_history_serializer(self):
        user = User.objects.create_user(
            username='testuser', password='testpassword')
        note = Note.objects.create(
            title='Test Note', content='This is a test note.', owner=user)
        history = NoteHistory.objects.create(note=note, line_numbers='1', old_content='This is a test note.',
                                             new_content='This is an updated note.', operation='update', updated_by=user)
        serializer = NoteHistorySerializer(instance=history)
        data = serializer.data
        self.assertEqual(data['line_numbers'], '1')
        self.assertEqual(data['old_content'], 'This is a test note.')
        self.assertEqual(data['new_content'], 'This is an updated note.')
        self.assertEqual(data['operation'], 'update')
        self.assertEqual(data['updated_by_name'], 'testuser')


class ViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')

    def test_user_create_view(self):
        data = {'username': 'newtestuser',
                'email': 'newtest@example.com', 'password': 'newpassword'}
        response = self.client.post(reverse('signup'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='newtestuser')
        self.assertEqual(user.email, 'newtest@example.com')

    def test_note_create_view(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'Test Note', 'content': 'This is a test note.'}
        response = self.client.post(reverse('note_create'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        note = Note.objects.get(title='Test Note')
        self.assertEqual(note.content, 'This is a test note.')
        self.assertEqual(note.owner, self.user)

    def test_note_share_view(self):
        user2 = User.objects.create_user(
            username='testuser2', password='testpassword')
        self.client.force_authenticate(user=self.user)
        note = Note.objects.create(
            title='Test Note', content='This is a test note.', owner=self.user)
        data = ['testuser2']  # Send the data as a list of usernames
        response = self.client.post(
            reverse('note_share', kwargs={'pk': note.pk}), data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        note.refresh_from_db()
        self.assertIn(user2, note.shared_with.all())

    def test_note_history_view(self):
        self.client.force_authenticate(user=self.user)
        note = Note.objects.create(
            title='Test Note', content='This is a test note.', owner=self.user)
        history = NoteHistory.objects.create(note=note, line_numbers='1', old_content='This is a test note.',
                                             new_content='This is an updated note.', operation='update', updated_by=self.user)
        response = self.client.get(
            reverse('note_history', kwargs={'note_pk': note.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['line_numbers'], '1')
        self.assertEqual(data[0]['old_content'], 'This is a test note.')
        self.assertEqual(data[0]['new_content'], 'This is an updated note.')
        self.assertEqual(data[0]['operation'], 'update')
        self.assertEqual(data[0]['updated_by_name'], 'testuser')


