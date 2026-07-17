from pydantic import BaseModel, field_validator, EmailStr
from datetime import date, datetime


class LocationCreate(BaseModel):
    country: str = "Россия"
    region: str | None = None
    district: str | None = None
    name: str

    @field_validator("country", "region", "district", "name")
    @classmethod
    def format_location_fields(cls, value: str | None) -> str | None:
        if value is None:
            return value
            
        clean_value = value.strip()
        space_words = clean_value.split()
        
        lowercase_exceptions = {"Район", "Улус", "Поселок", "Село", "Деревня", "Город", "Пгт"}
        
        formatted_space_words = []
        for space_word in space_words:
            dash_words = space_word.split("-")
            formatted_dash_words = [w.capitalize() for w in dash_words]
            word_result = "-".join(formatted_dash_words)
            
            if word_result in lowercase_exceptions:
                word_result = word_result.lower()
                
            formatted_space_words.append(word_result)
            
        return " ".join(formatted_space_words)


class LocationResponse(BaseModel):
    id: int
    country: str
    region: str | None 
    district: str | None
    name: str

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name: str
    surname: str
    patronymic: str | None = None
    birth_date: date
    password: str
    email: EmailStr | None = None
    phone_number: str

    @field_validator("email", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value

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
    birth_date: date
    email: str | None = None
    phone_number: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserPublicResponse(BaseModel):
    id: int
    name: str
    surname: str

    model_config = {"from_attributes": True}


class TripCreate(BaseModel): 
    from_location_id: int
    to_location_id: int
    price: int
    seats: int
    date: datetime
    comment: str | None = None


class TripResponse(BaseModel):
    id: int
    driver_id: int
    from_location_id: int
    to_location_id: int
    price: int
    seats: int
    date: datetime
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