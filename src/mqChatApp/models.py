from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.

class UserManager(BaseUserManager):
    '''
    custom manager for the user model
    '''
    def create_user(self, **kwargs):
        if not kwargs.get("email"):
            raise Exception("Email must be added for a user!")
        password = kwargs.pop("password")
        user = self.model(**kwargs)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, **kwargs):
        '''
        superuser creator
        '''
        user = self.create_user(**kwargs)
        user.is_admin = True
        user.is_superuser = True
        user.save()
        return user

    
class User(AbstractBaseUser):
    '''base user table(model)'''
    id = models.AutoField(primary_key=True)
    name = models.CharField('name of user', max_length=500, null=False, blank=False)
    surname = models.CharField('user surname', max_length=500, null=True, blank=True)
    username = models.CharField('username of user', max_length=500, null=False, blank=False)
    email = models.EmailField('user email', null=False, blank=False, unique=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'username']

    def __str__(self):
        return self.email

    # class Meta:
    #     indexes = ['id', 'email']
    #     permissioins = ['can_edit_user', 'can_create_user']
    #     ordering = '-name'