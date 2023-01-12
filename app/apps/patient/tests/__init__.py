from django.test import TestCase
from apps.patient.models import Patient
from apps.study.models import Study
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class ContactTestCase(TestCase):

    """
    Test suite for Patient
    """
    def setUp(self):

        user_one_kwargs = {
            "username": "UserOne",
            "first_name": "User",
            "last_name": "One",
            "email": 'user.one@umed.io',
            "password": make_password("Password8080"),
            "is_active": True,
        }
        user_two_kwargs = {
            "username": "UserTwo",
            "first_name": "User",
            "last_name": "Two",
            "email": 'user.two@umed.io',
            "password": make_password("Password8080"),
            "is_active": True,
        }
        user_three_kwargs = {
            "username": "UserThree",
            "first_name": "User",
            "last_name": "Three",
            "email": 'user.three@umed.io',
            "password": make_password("Password8080"),
            "is_active": True,
        }
        user_one = User.objects.create(**user_one_kwargs)
        user_two = User.objects.create(**user_two_kwargs)
        user_three = User.objects.create(**user_three_kwargs)
        study_a = Study.objects.create(name="Study A")
        study_b = Study.objects.create(name="Study B")
        study_c = Study.objects.create(name="Study C")
        self.patient_one = Patient.objects.create(user = user_one, study = study_a, status=0, cancelled=0)
        self.patient_two = Patient.objects.create(user = user_two, study = study_b, status=0, cancelled=0)
        self.patient_three = Patient.objects.create(user = user_three, study = study_c, status=0, cancelled=0)
        self.patients = [self.patient_one, self.patient_two, self.patient_three]

    def test_in_study(self):
        '''
        test Managers
        '''
        for patient in self.patients:
            self.assertEqual(patient.in_study, True)

