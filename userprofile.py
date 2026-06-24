'''
User Profile.
This is a test program to understand how we can use pydantic.
'''

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, computed_field
from datetime import date

class UserProfile(BaseModel):
    user_id: int
    username: str = Field(min_length=3, max_length=20) #use of min and max length
    email: EmailStr #use of internal email validator
    age: int = Field(ge=18, le=120) #use of greater and less than
    rating: float = Field(ge=0.0, le=5.0) #use of greater and less than
    date_of_birth: date
    subjects: dict[str, float] = Field(default_factory=dict)  # {"Math": 85.0, "Science": 90.0}

    #custom validation for username
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()

    #custom validation for date of birth
    @field_validator('date_of_birth')
    @classmethod
    def dob_in_past(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError('Date of birth must be in the past')
        return v

    #custom validation at model level after the pydantic applies its vaidation rules
    @model_validator(mode='after')
    def age_matches_dob(self) -> 'UserProfile':
        calculated_age = (date.today() - self.date_of_birth).days // 365
        if abs(calculated_age - self.age) > 1:
            raise ValueError(f'Age {self.age} does not match date of birth (expected ~{calculated_age})')
        return self

    @computed_field
    @property
    def average_marks(self) -> float:
        if not self.subjects:
            return 0.0
        return round(sum(self.subjects.values()) / len(self.subjects), 2)

    @computed_field
    @property
    def grade(self) -> str:
        avg = self.average_marks
        if avg >= 90: return "A"
        elif avg >= 75: return "B"
        elif avg >= 60: return "C"
        elif avg >= 45: return "D"
        else: return "F"


#------------------------------------------------------------------------------------------------------------------------
#Testing...
from pydantic import ValidationError

# 1. BaseModel - basic type coercion and validation
try:
    u = UserProfile(user_id="42", username="alice", email="alice@example.com",
                    age=25, rating=4.5, date_of_birth=date(1999, 5, 10))
    print(u)  # user_id gets coerced from "42" -> 42
except ValidationError as e:
    print(e)


print('-'*100)

# 2. Field - min/max length on username
try:
    UserProfile(user_id=1, username="ab",  # too short, min=3
                email="a@b.com", age=25, rating=3.0, date_of_birth=date(1999, 1, 1))
except ValidationError as e:
    print(e)


print('-'*100)


# 3. Field - ge/le on age and rating
try:
    UserProfile(user_id=1, username="alice", email="a@b.com",
                age=15,       # below ge=18
                rating=9.9,   # above le=5.0
                date_of_birth=date(2007, 1, 1))
except ValidationError as e:
    print(e)


print('-'*100)


# 4. EmailStr - invalid email format
try:
    UserProfile(user_id=1, username="alice", email="not-an-email",
                age=25, rating=3.0, date_of_birth=date(1999, 1, 1))
except ValidationError as e:
    print(e)


print('-'*100)


# 5. field_validator - username must be alphanumeric
try:
    UserProfile(user_id=1, username="ali ce",  # space not allowed
                email="a@b.com", age=25, rating=3.0, date_of_birth=date(1999, 1, 1))
except ValidationError as e:
    print(e)


print('-'*100)


# 6. field_validator - date_of_birth must be in the past
try:
    UserProfile(user_id=1, username="alice", email="a@b.com",
                age=25, rating=3.0, date_of_birth=date(2099, 1, 1))  # future date
except ValidationError as e:
    print(e)


print('-'*100)


# 7. model_validator - age vs date_of_birth mismatch
try:
    UserProfile(user_id=1, username="alice", email="a@b.com",
                age=50,                          # claims 50
                rating=3.0,
                date_of_birth=date(1999, 5, 10)) # but DOB says ~25
except ValidationError as e:
    print(e)


print('-'*100)

# 8. computed field
u = UserProfile(
    user_id=1,
    username="alice",
    email="alice@example.com",
    age=27,
    rating=4.5,
    date_of_birth=date(1999, 5, 10),
    subjects={
        "Math": 88.0,
        "Science": 91.0,
        "English": 74.0,
        "History": 60.0
    }
)

print(u.average_marks)  # 78.25
print(u.grade)          # B
print(u)
#print(u.model_dump())