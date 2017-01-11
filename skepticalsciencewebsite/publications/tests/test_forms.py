from io import BytesIO
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model
from publications.models import Licence
from publications.forms import PublicationCreateForm, PublicationCorrectForm, CommentForm

# only test the view

# class PublicationCreateFormTestCase(TestCase):
#
#     def setUp(self):
#         im = Image.new(mode='RGB', size=(200, 200))  # create a new image using PIL
#         im_io = BytesIO()  # a BytesIO object for saving image
#         im.save(im_io, 'JPEG')  # save the image to im_io
#         im_io.seek(0)  # seek to the beginning
#         self.file1 = InMemoryUploadedFile(im_io, None, 'test-name.jpg', 'image/jpeg', im_io.getbuffer().nbytes, None)
#         self.file2 = InMemoryUploadedFile(im_io, None, 'test-name2.jpg', 'image/jpeg', im_io.getbuffer().nbytes, None)
#         User = get_user_model()
#         self.user = User.objects.create_user(username="testuser", password="azerty123", email="test@tests.com")
#         self.user.save()
#         self.licence = Licence.objects.create(short_name='licence')
#         self.licence.save()
#
#     def test_valid(self):
#         form_data = {"title": 't1', "resume": 'r1', "first_author": self.user.pk, "licence": self.licence.pk,
#                      "sciences": '', "authors": '', "last_author": ''}
#         form_files = {'source_creation': self.file1, 'pdf_creation': self.file2}
#         form = PublicationCreateForm(data=form_data, files=form_files)
#         self.assertTrue(form.is_valid())


# class PublicationCorrectFormTestCase(TestCase):
#
#     def setUp(self):
#         im = Image.new(mode='RGB', size=(200, 200))  # create a new image using PIL
#         im_io = BytesIO()  # a BytesIO object for saving image
#         im.save(im_io, 'JPEG')  # save the image to im_io
#         im_io.seek(0)  # seek to the beginning
#         self.file1 = InMemoryUploadedFile(im_io, None, 'test-name.jpg', 'image/jpeg', im_io.getbuffer().nbytes, None)
#         self.file2 = InMemoryUploadedFile(im_io, None, 'test-name2.jpg', 'image/jpeg', im_io.getbuffer().nbytes, None)
#
#     def test_valid(self):
#         form_data = {"resume": 'r1'}
#         form_files = {'source_final': self.file1, 'pdf_final': self.file2}
#         form = PublicationCorrectForm(data=form_data, files=form_files)
#         self.assertTrue(form.is_valid())


# class CommentFormTestCase(TestCase):
#
#     def test_valid(self):
#         form_data = {"author_fake_pseudo": "fpseudo", "comment_type": "type1", "title": "title", "content": "content"}
#         form = CommentForm(data=form_data)
#         self.assertTrue(form.is_valid())



