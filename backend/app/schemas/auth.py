from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    fullName: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=6)
    countryCode: str
    companyName: str | None = None
    companyAbout: str | None = None
    companyWebsite: str | None = None
    companyIndustry: str | None = None
    companyPhone: str | None = None

    @field_validator("countryCode")
    @classmethod
    def cc(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) != 2 or not v.isalpha():
            raise ValueError("Country code must be ISO alpha-2")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
