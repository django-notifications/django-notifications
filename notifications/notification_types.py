from typing import NewType

from django.contrib.auth.base_user import AbstractBaseUser

AbstractUser = NewType("AbstractUser", AbstractBaseUser)  # type: ignore[valid-newtype]
