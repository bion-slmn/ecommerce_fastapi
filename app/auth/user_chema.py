from pydantic import BaseModel, EmailStr, field_validator, model_validator
import re

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr                  # validates email format automatically
    password: str
    confirm_password: str
    mobile: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        if not v.replace(" ", "").isalpha():
            raise ValueError("Name must contain only letters")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        return v

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v):
        if v is None:
            return v
        cleaned = re.sub(r"[\s\-\+\(\)]", "", v)  # strip spaces, dashes, +, brackets
        if not cleaned.isdigit():
            raise ValueError("Mobile must contain only digits")
        if not (7 <= len(cleaned) <= 15):           # E.164 standard length
            raise ValueError("Mobile number must be between 7 and 15 digits")
        return cleaned

    @model_validator(mode="after")                  # runs after all field validators
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self