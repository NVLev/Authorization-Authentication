

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict



class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=6, description="Пароль (минимум 6 символов)")


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """Схема для чтения пользователя"""
    id: int
    is_active: bool
    created_at: datetime
    roles: List[str] = []  # Список названий ролей

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Схема для логина"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Схема ответа с токенами"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Token(BaseModel):
    """Схема токена (для refresh)"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Схема для refresh токена"""
    refresh_token: str



class RoleBase(BaseModel):
    """Базовая схема роли"""
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class RoleCreate(RoleBase):
    """Схема для создания роли"""
    pass


class RoleRead(RoleBase):
    """Схема для чтения роли"""
    id: int

    model_config = ConfigDict(from_attributes=True)




class BusinessElementBase(BaseModel):
    """Базовая схема бизнес-элемента"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class BusinessElementCreate(BusinessElementBase):
    """Схема для создания бизнес-элемента"""
    pass


class BusinessElementRead(BusinessElementBase):
    """Схема для чтения бизнес-элемента"""
    id: int

    model_config = ConfigDict(from_attributes=True)




class AccessRuleBase(BaseModel):
    """Базовая схема правила доступа"""
    role_id: int
    element_id: int
    read_permission: bool = False
    read_all_permission: bool = False
    create_permission: bool = False
    update_permission: bool = False
    update_all_permission: bool = False
    delete_permission: bool = False
    delete_all_permission: bool = False


class AccessRuleCreate(AccessRuleBase):
    """Схема для создания правила доступа"""
    pass


class AccessRuleUpdate(BaseModel):
    """Схема для обновления правила доступа"""
    read_permission: Optional[bool] = None
    read_all_permission: Optional[bool] = None
    create_permission: Optional[bool] = None
    update_permission: Optional[bool] = None
    update_all_permission: Optional[bool] = None
    delete_permission: Optional[bool] = None
    delete_all_permission: Optional[bool] = None


class AccessRuleRead(AccessRuleBase):
    """Схема для чтения правила доступа"""
    id: int
    role_name: Optional[str] = None  # Название роли (для удобства)
    element_name: Optional[str] = None  # Название элемента (для удобства)

    model_config = ConfigDict(from_attributes=True)




class ProjectBase(BaseModel):
    """Базовая схема проекта"""
    title: str = Field(..., max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Схема для создания проекта"""
    pass


class ProjectUpdate(BaseModel):
    """Схема для обновления проекта"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class ProjectRead(ProjectBase):
    """Схема для чтения проекта"""
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class PermissionsResponse(BaseModel):
    """Схема ответа с правами пользователя"""
    user_id: int
    email: str
    roles: List[str]
    permissions: dict  # {"projects": {"read": true, "create": false, ...}, ...}


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""
    detail: str