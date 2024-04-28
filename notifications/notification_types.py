from typing import NewType, Type, Union

from django.contrib.auth.base_user import AbstractBaseUser

AbstractUser = NewType("AbstractUser", AbstractBaseUser)  # type: ignore[valid-newtype]

OptionalAbstractUser = Union[None, Type[AbstractUser]]
