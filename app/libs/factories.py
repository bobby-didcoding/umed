from factory import lazy_attribute, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from apps.care_provider.models import CareProvider
from apps.patient.models import Patient
from apps.study.models import Study
from django.contrib.auth.models import User

Faker.seed(0)
fake = Faker(locale="en_GB")


class CareProviderFactory(DjangoModelFactory):

    class Meta:
        model = CareProvider

    name = lazy_attribute(
        lambda u: fake.sentence(nb_words=3) + str(fake.random_number(5, fix_len=True))
    )
    ods = lazy_attribute(lambda u: str(fake.random_number(5, fix_len=True)))
    contact = lazy_attribute(lambda u: fake.name() + str(fake.random_number(5, fix_len=True)))


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User

    first_name = lazy_attribute(lambda u: fake.first_name())
    last_name = lazy_attribute(lambda u: fake.last_name())
    username = lazy_attribute(lambda u: f"{fake.user_name()}{fake.pyint()}")
    email = lazy_attribute(lambda u: f"{fake.pyint()}{fake.email()}")
    password = "password0101"


class StudyFactory(DjangoModelFactory):

    class Meta:
        model = Study

    name = lazy_attribute(
        lambda u: fake.sentence(nb_words=3) + str(fake.random_number(5, fix_len=True))
    )


class PatientFactory(DjangoModelFactory):

    class Meta:
        model = Patient

    user = SubFactory(UserFactory)
    study = SubFactory(Study)
