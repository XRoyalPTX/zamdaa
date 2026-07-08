from pydantic import BaseModel, field_validator, EmailStr
import datetime


class LocationCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def format_location_name(cls, value: str) -> str:
        clean_value = value.strip()
        
        words = clean_value.split("-")
        formatted_words = [word.capitalize() for word in words]
        return "-".join(formatted_words)


class LocationResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name: str
    surname: str
    patronymic: str | None = None
    birth_date: datetime.date
    login: str
    password: str
    email: EmailStr
    phone_number: str

    @field_validator("name")
    @classmethod
    def format_name(cls, value: str) -> str:
        clean_value = value.strip()
        
        words = clean_value.split("-")
        formatted_words = [word.capitalize() for word in words]
        return "-".join(formatted_words)
    
    @field_validator("surname")
    @classmethod
    def format_surname(cls, value: str) -> str:
        clean_value = value.strip()
        
        words = clean_value.split("-")
        formatted_words = [word.capitalize() for word in words]
        return "-".join(formatted_words)
    
    @field_validator("patronymic")
    @classmethod
    def format_patronymic(cls, value: str) -> str:
        clean_value = value.strip()
        
        words = clean_value.split("-")
        formatted_words = [word.capitalize() for word in words]
        return "-".join(formatted_words)
    
    @field_validator("phone_number")
    @classmethod
    def check_phone_number(cls, value: str) -> str:
        clean_phone = value.strip()
        if len(clean_phone) < 11:
            raise ValueError("Номер телефона слишком короткий")
        return clean_phone
    
    @field_validator("password")
    @classmethod
    def check_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Пароль должен содержать 8 и более символов")
        special_symbols = '!@#$%^&_'
        numbers = '0123456789'
        if not any(char in numbers for char in value):
            raise ValueError("Пароль должен содержать хотя бы одно число")

        if not any(char in special_symbols for char in value):
            raise ValueError("Пароль должен содержать хотя бы один спецсимвол !@#$%^&_")
        return value


class UserResponse(BaseModel):
    id: int
    name: str
    surname: str
    patronymic: str | None = None
    birth_date: datetime.date
    login: str
    email: str
    phone_number: str
    is_active: bool

    model_config = {"from_attributes": True}


class TripCreate(BaseModel): 
    from_location_id: int
    to_location_id: int
    price: int
    seats: int
    date: datetime.datetime
    comment: str | None = None


class TripResponse(BaseModel):
    id: int
    driver_id: int
    from_location_id: int
    to_location_id: int
    price: int
    seats: int
    date: datetime.datetime
    comment: str | None = None

    model_config = {"from_attributes": True}


class TripRequestCreate(BaseModel):
    trip_id: int
    seats_requested: int = 1


class TripRequestResponse(BaseModel):
    id: int
    requester_id: int
    trip_id: int
    seats_requested: int
    status: str

    model_config = {"from_attributes": True}