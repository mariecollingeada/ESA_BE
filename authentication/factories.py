# authentication/factories.py
import factory
from django.contrib.auth.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

    # create hashed password automatically
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        pw = extracted or 'ComplexPass123!'
        self.set_password(pw)
        if create:
            self.save()
