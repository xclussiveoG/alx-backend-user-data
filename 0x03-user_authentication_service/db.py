#!/usr/bin/env python3

"""DB module."""
from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.session import Session

# noinspection PyCompatibility
from user import Base, User


class DB:
    """DB class."""

    def __init__(self) -> None:
        """Initialize a new DB instance."""
        echo = getenv("ECHO") == "True"

        self._engine = create_engine("sqlite:///a.db", echo=echo)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object."""
        if self.__session is None:
            db_session = sessionmaker(bind=self._engine)
            self.__session = db_session()
        return self.__session

    @staticmethod
    def _valid_attributes(**kwargs) -> bool:
        """Validate keyword arguments against User class attributes.

        Check if the provided keyword arguments are valid attributes of the
        User class.

        Args:
            **kwargs: Arbitrary keyword arguments representing user attributes.

        Returns:
            bool: True if all provided keys are valid User attributes,
            False otherwise.
        """
        user_dict_keys = set(User.__dict__.keys())
        kw_dict_keys = set(kwargs.keys())

        if not kw_dict_keys.issubset(user_dict_keys):
            return False

        return True

    def add_user(self, email: str, hashed_password: str) -> User:
        """Create and save a new user to the database.

        Args:
            email (str): The email of the user.
            hashed_password (str): A secure and safe password for the user.

        Returns:
            User: A new user object is returned on success.
        """
        db_user = User(email=email, hashed_password=hashed_password)
        self._session.add(db_user)

        self._session.commit()
        return db_user

    def find_user_by(self, **kwargs) -> User:
        """Search and return user by a given field.

        Args:
            **kwargs: Arbitrary keyword arguments representing user attributes.

        Raises:
            InvalidRequestError: If no keyword arguments are provided or if
             any provided key is not a valid user attribute.
            NoResultFound: If no user is found with the given attributes.

        Returns:
            User: The user object that matches the given attributes.
        """
        if not kwargs:
            raise InvalidRequestError("No search parameters provided.")

        if not self._valid_attributes(**kwargs):
            raise InvalidRequestError("Invalid search parameters provided.")

        db_user = self._session.query(User).filter_by(**kwargs).first()
        if not db_user:
            raise NoResultFound("No user found with the given parameters.")

        return db_user

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update an instance of a user.

        Args:
            user_id (int): The ID of the user to update.
            **kwargs: Arbitrary keyword arguments representing user attributes
             to update.

        Raises:
            ValueError: If any provided key is not a valid user attribute.
        """
        if not self._valid_attributes(**kwargs):
            raise ValueError("Unrecognized arguments for User.")

        db_user = self.find_user_by(id=user_id)
        for key, value in kwargs.items():
            setattr(db_user, key, value)

        self._session.add(db_user)
        self._session.commit()
