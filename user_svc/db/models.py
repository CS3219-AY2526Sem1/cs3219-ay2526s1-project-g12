from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTableUUID
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from utils.utils import AppConfig

config = AppConfig()


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Role(Base):
    """Class representing the roles table in the database.

    Attributes:
        id (int): The primary key of the role.
        role (str): The name of the role.
        users (list[User]): The list of users associated with the role.
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str]

    users: Mapped[list["User"]] = relationship(back_populates="role", lazy="selectin")


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Class representing the user table in the database.

    Attributes:
        id (UUID): The primary key of the user.
        email (str): The email of the user.
        hashed_password (str): The hashed password of the user.
        is_active (bool): Whether the user is active.
        is_superuser (bool): Whether the user is a superuser.
        is_verified (bool): Whether the user is verified.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        role_id (str): The foreign key to the roles table.
        role (Role): The role of the user.
    """
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.id"),
        default=config.default_role_id,
    )

    role: Mapped[Role] = relationship(back_populates="users", lazy="selectin")

class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    """Class representing the access tokens table in the database.

    Attributes:
        id (UUID): The primary key of the access token.
        token (str): The access token.
        user_id (UUID): The foreign key to the users table.
        user (User): The user associated with the access token.
    """
    pass
