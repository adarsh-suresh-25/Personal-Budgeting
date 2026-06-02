from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from database import SessionLocal, engine
from database import Base

from models import Expense, User

from groq import Groq
from config import GROQ_API_KEY
print("GROQ KEY LOADED:", GROQ_API_KEY[:10])

Base.metadata.create_all(bind=engine)

app = FastAPI()

# -----------------------------
# GROQ CONFIG
# -----------------------------

client = Groq(
    api_key=GROQ_API_KEY
)

# -----------------------------
# CORS
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# MODELS
# -----------------------------

class RegisterData(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

class ExpenseData(BaseModel):
    amount: int
    description: str
    email: str

class ChatData(BaseModel):
    message: str

# -----------------------------
# HOME
# -----------------------------

@app.get("/")
def home():

    return {
        "message": "Backend Working"
    }

# -----------------------------
# REGISTER
# -----------------------------

@app.post("/register")
def register(user: RegisterData):

    db = SessionLocal()

    allowed_domains = [
        "gmail.com",
        "yahoo.com",
        "outlook.com"
    ]

    email_domain = user.email.split("@")[1]

    if email_domain not in allowed_domains:

        return {
            "message": "Only Gmail/Yahoo/Outlook allowed"
        }

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:

        return {
            "message": "Email already exists"
        }

    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password
    )

    db.add(new_user)

    db.commit()

    return {
        "message": "Registration Successful"
    }

# -----------------------------
# LOGIN
# -----------------------------

@app.post("/login")
def login(user: LoginData):

    db = SessionLocal()

    existing_user = db.query(User).filter(
        User.email == user.email,
        User.password == user.password
    ).first()

    if existing_user:

        return {
            "message": "Login Successful",
            "email": existing_user.email
        }

    return {
        "message": "User not registered or incorrect password"
    }

# -----------------------------
# ADD EXPENSE
# -----------------------------

@app.post("/add-expense")
def add_expense(expense: ExpenseData):

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == expense.email
    ).first()

    if not user:

        return {
            "message": "User not found"
        }

    description = expense.description.lower()

    if "zomato" in description or "food" in description:

        category = "Food"

    elif "uber" in description or "travel" in description:

        category = "Travel"

    elif "teddy" in description or "gift" in description:

        category = "Gift"

    elif "amazon" in description or "shopping" in description:

        category = "Shopping"

    else:

        category = "Other"

    new_expense = Expense(
        amount=expense.amount,
        category=category,
        description=expense.description,
        user_id=user.id
    )

    db.add(new_expense)

    db.commit()

    return {
        "message": "Expense Added",
        "category": category
    }

# -----------------------------
# GET USER EXPENSES
# -----------------------------

@app.get("/expenses/{email}")
def get_expenses(email: str):

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        return {
            "expenses": [],
            "total": 0,
            "categories": {},
            "insight": "No user found"
        }

    expenses = db.query(Expense).filter(
        Expense.user_id == user.id
    ).all()

    data = []

    total = 0

    category_totals = {}

    for expense in expenses:

        total += expense.amount

        if expense.category not in category_totals:

            category_totals[expense.category] = 0

        category_totals[expense.category] += expense.amount

        data.append({
            "id": expense.id,
            "amount": expense.amount,
            "category": expense.category,
            "description": expense.description
        })

    insight = "Your spending looks balanced"

    if category_totals.get("Food", 0) > 5000:

        insight = "High food spending detected."

    if total > 20000:

        insight = "Monthly spending is high."

    return {
        "expenses": data,
        "total": total,
        "categories": category_totals,
        "insight": insight
    }

# -----------------------------
# EDIT EXPENSE
# -----------------------------

@app.put("/edit-expense/{expense_id}")
def edit_expense(expense_id: int, expense: ExpenseData):

    db = SessionLocal()

    existing_expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if not existing_expense:

        return {
            "message": "Expense not found"
        }

    description = expense.description.lower()

    if "zomato" in description or "food" in description:

        category = "Food"

    elif "uber" in description or "travel" in description:

        category = "Travel"

    elif "teddy" in description or "gift" in description:

        category = "Gift"

    elif "amazon" in description or "shopping" in description:

        category = "Shopping"

    else:

        category = "Other"

    existing_expense.amount = expense.amount

    existing_expense.description = expense.description

    existing_expense.category = category

    db.commit()

    return {
        "message": "Expense Updated"
    }

# -----------------------------
# DELETE EXPENSE
# -----------------------------

@app.delete("/delete-expense/{expense_id}")
def delete_expense(expense_id: int):

    db = SessionLocal()

    expense = db.query(Expense).filter(
        Expense.id == expense_id
    ).first()

    if not expense:

        return {
            "message": "Expense not found"
        }

    db.delete(expense)

    db.commit()

    return {
        "message": "Expense Deleted"
    }

# -----------------------------
# AI CHATBOT
# -----------------------------

@app.post("/chat")
def chat(data: ChatData):

    user_message = data.message.lower().strip()

    # -----------------------------
    # GREETINGS
    # -----------------------------

    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]

    if any(word in user_message for word in greetings):

        return {
            "reply":
            "Hello 👋 I am your Financial Advisor. I can help with budgeting, savings, investments, expenses, loans, banking and financial planning. How can I help you today?"
        }

    # -----------------------------
    # NAME INTRODUCTION
    # -----------------------------

    if "my name is" in user_message:

        name = user_message.split("my name is")[-1].strip()

        return {
            "reply":
            f"Hello {name.title()} 👋 I am your Financial Advisor. Feel free to ask me anything related to budgeting, savings, investments, expenses, loans, banking or financial planning."
        }

    if "i am" in user_message:

        name = user_message.split("i am")[-1].strip()

        if len(name) < 30:

            return {
                "reply":
                f"Hello {name.title()} 👋 I am your Financial Advisor. How can I help you with your financial goals today?"
            }

    if (
        "your name" in user_message
        or "who are you" in user_message
        or "what are you" in user_message
    ):

        return {
            "reply":
            "I am Budget Control AI, your Financial Advisor. I specialize in budgeting, savings, investments, expense tracking, loans, banking and financial planning."
        }

    # -----------------------------
    # GROQ AI
    # -----------------------------

    try:

        completion = client.chat.completions.create(

            model="llama3-8b-8192",

            messages=[

                {
                    "role": "system",

                    "content":
                    """
                    You are a professional Financial Advisor.

                    You can ONLY answer:

                    - Budgeting
                    - Saving Money
                    - Investments
                    - Mutual Funds
                    - SIP
                    - Expense Management
                    - Banking
                    - Credit Cards
                    - Loans
                    - EMI
                    - Income Planning
                    - Salary Planning
                    - Taxes
                    - Financial Goals
                    - Personal Finance

                    You may also answer:
                    - Greetings
                    - Introduction
                    - Your name

                    If a user asks anything unrelated to finance,
                    respond with:

                    "I am your Financial Advisor and can only assist with budgeting, savings, investments, expenses, loans, banking and financial planning."

                    Keep answers practical,
                    easy to understand,
                    beginner friendly,
                    and provide calculations whenever useful.
                    """
                },

                {
                    "role": "user",
                    "content": data.message
                }

            ]
        )

        reply = completion.choices[0].message.content

        return {
            "reply": reply
        }

    except Exception as e:

        print("CHATBOT ERROR:", str(e))

        return {
            "reply":
            "I'm currently unable to access my financial knowledge service. Please try again in a few moments."
        }