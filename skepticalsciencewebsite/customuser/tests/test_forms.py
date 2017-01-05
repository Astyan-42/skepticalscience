from io import BytesIO
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import InMemoryUploadedFile
from customuser.forms import CustomUserUpdateForm


class CustomUserUpdateFormTestCase(TestCase):

    def setUp(self):
        im = Image.new(mode='RGB', size=(200, 200))  # create a new image using PIL
        im_io = BytesIO()  # a BytesIO object for saving image
        im.save(im_io, 'JPEG')  # save the image to im_io
        im_io.seek(0)  # seek to the beginning
        self.image = InMemoryUploadedFile(im_io, None, 'test-name.jpg', 'image/jpeg', im_io.getbuffer().nbytes, None)

    def test_valid(self):
        form_data = {'email': 'v@v.com', 'submit': 'Submit', 'workplace': '', 'job_title': 'r',
                     'first_name': 'Azfd', 'description': '', 'middle_name': 'dsqvc',
                     'last_name': 'fqsv', 'country': ''}
        form_files = {'phd_image': self.image}
        form = CustomUserUpdateForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_save_new_file(self):
        form_data = {'email': 'v@v.com', 'submit': 'Submit', 'workplace': '', 'job_title': 'r',
                     'first_name': 'Azfd', 'description': '', 'middle_name': 'dsqvc',
                     'last_name': 'fqsv', 'country': ''}
        form_files = {'phd_image': self.image}
        form = CustomUserUpdateForm(data=form_data, files=form_files)
        data = form.save()
        self.assertIsNotNone(data.phd_update_date)

    # need to test the case where the image is already save in the media/PHDs/****** folder
    # def test_save_old_file(self):
    #     form_data = {'email': 'v@v.com', 'submit': 'Submit', 'workplace': '', 'job_title': 'r',
    #                  'first_name': 'Azfd', 'description': '', 'middle_name': 'dsqvc',
    #                  'last_name': 'fqsv', 'country': ''}
    #     form_files = {'phd_image': self.phd_image}
    #     form = CustomUserUpdateForm(data=form_data, files=form_files)
    #     data = form.save()
    #     self.assertIsNotNone(data.phd_update_date)