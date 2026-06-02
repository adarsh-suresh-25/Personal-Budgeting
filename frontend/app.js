let chart = null;

// SHOW LOGIN
function showLogin() {
  const loginForm = document.getElementById("loginForm");

  const registerForm = document.getElementById("registerForm");

  if (loginForm && registerForm) {
    loginForm.style.display = "block";

    registerForm.style.display = "none";
  }

  const loginTab = document.getElementById("loginTab");

  const registerTab = document.getElementById("registerTab");

  if (loginTab && registerTab) {
    loginTab.classList.add("active-tab");

    registerTab.classList.remove("active-tab");
  }
}

// SHOW REGISTER
function showRegister() {
  const loginForm = document.getElementById("loginForm");

  const registerForm = document.getElementById("registerForm");

  if (loginForm && registerForm) {
    loginForm.style.display = "none";

    registerForm.style.display = "block";
  }

  const loginTab = document.getElementById("loginTab");

  const registerTab = document.getElementById("registerTab");

  if (loginTab && registerTab) {
    registerTab.classList.add("active-tab");

    loginTab.classList.remove("active-tab");
  }
}

// REGISTER
async function register() {
  const name = document.getElementById("registerName").value;

  const email = document.getElementById("registerEmail").value;

  const password = document.getElementById("registerPassword").value;

  try {
    const response = await fetch("http://127.0.0.1:8000/register", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        name,
        email,
        password,
      }),
    });

    const data = await response.json();

    alert(data.message);

    if (data.message === "Registration Successful") {
      showLogin();
    }
  } catch (error) {
    console.log(error);

    alert("Registration Failed");
  }
}

// LOGIN
async function login() {
  const email = document.getElementById("loginEmail").value;

  const password = document.getElementById("loginPassword").value;

  try {
    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        email,
        password,
      }),
    });

    const data = await response.json();

    if (data.message === "Login Successful") {
      localStorage.setItem("userEmail", data.email);

      window.location.href = "dashboard.html";
    } else {
      alert(data.message);
    }
  } catch (error) {
    console.log(error);

    alert("Login Failed");
  }
}

// LOAD EXPENSES
async function loadExpenses() {
  const email = localStorage.getItem("userEmail");

  if (!email) {
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:8000/expenses/${email}`);

    const data = await response.json();

    // TOTAL
    const totalExpenses = document.getElementById("totalExpenses");

    if (totalExpenses) {
      totalExpenses.innerText = `₹${data.total}`;
    }

    // INSIGHT
    const insight = document.getElementById("insightText");

    if (insight) {
      insight.innerText = data.insight;
    }

    // TABLE
    const tableBody = document.getElementById("expenseTableBody");

    if (tableBody) {
      tableBody.innerHTML = "";

      data.expenses.forEach((expense) => {
        tableBody.innerHTML += `

                    <tr>

                        <td>₹${expense.amount}</td>

                        <td>${expense.category}</td>

                        <td>${expense.description}</td>

                        <td>

                            <button
                                onclick="editExpense(
                                    ${expense.id},
                                    ${expense.amount},
                                    '${expense.description}'
                                )">

                                Edit

                            </button>

                            <button
                                onclick="deleteExpense(
                                    ${expense.id}
                                )">

                                Delete

                            </button>

                        </td>

                    </tr>
                `;
      });
    }

    // PIE CHART
    const labels = Object.keys(data.categories);

    const values = Object.values(data.categories);

    const ctx = document.getElementById("expenseChart");

    if (ctx) {
      if (chart) {
        chart.destroy();
      }

      chart = new Chart(ctx, {
        type: "pie",

        data: {
          labels: labels,

          datasets: [
            {
              data: values,

              backgroundColor: [
                "#3b82f6",
                "#10b981",
                "#f59e0b",
                "#ef4444",
                "#8b5cf6",
              ],
            },
          ],
        },

        options: {
          responsive: true,
        },
      });
    }
  } catch (error) {
    console.log(error);
  }
}

// ADD EXPENSE
async function addExpense() {
  const amount = document.getElementById("amount").value;

  const description = document.getElementById("description").value;

  const email = localStorage.getItem("userEmail");

  console.log(amount);
  console.log(description);
  console.log(email);

  if (amount === "" || description === "") {
    alert("Please fill all fields");

    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/add-expense", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        amount: parseInt(amount),

        description: description,

        email: email,
      }),
    });

    const data = await response.json();

    console.log(data);

    alert("Expense Added Successfully");

    // CLEAR INPUTS
    document.getElementById("amount").value = "";

    document.getElementById("description").value = "";

    // RELOAD
    loadExpenses();
  } catch (error) {
    console.log(error);

    alert("Error Adding Expense");
  }
}

// DELETE EXPENSE
async function deleteExpense(id) {
  try {
    await fetch(`http://127.0.0.1:8000/delete-expense/${id}`, {
      method: "DELETE",
    });

    alert("Expense Deleted");

    loadExpenses();
  } catch (error) {
    console.log(error);
  }
}

// EDIT EXPENSE
async function editExpense(id, oldAmount, oldDescription) {
  const newAmount = prompt("Enter New Amount", oldAmount);

  const newDescription = prompt("Enter New Description", oldDescription);

  if (!newAmount || !newDescription) {
    return;
  }

  const email = localStorage.getItem("userEmail");

  try {
    await fetch(`http://127.0.0.1:8000/edit-expense/${id}`, {
      method: "PUT",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        amount: parseInt(newAmount),

        description: newDescription,

        email: email,
      }),
    });

    alert("Expense Updated");

    loadExpenses();
  } catch (error) {
    console.log(error);
  }
}

// LOGOUT
function logout() {
  localStorage.removeItem("userEmail");

  window.location.href = "login.html";
}

// AUTO LOAD
window.onload = function () {
  if (window.location.pathname.includes("dashboard.html")) {
    loadExpenses();
  }
};

// -----------------------------
// AI CHATBOT
// -----------------------------

async function sendMessage() {
  const input = document.getElementById("chatInput");

  const chatMessages = document.getElementById("chatMessages");

  const message = input.value;

  if (message.trim() === "") {
    return;
  }

  // USER MESSAGE

  chatMessages.innerHTML += `

    <div class="user-message">
      ${message}
    </div>

  `;

  input.value = "";

  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        message: message,
      }),
    });

    const data = await response.json();

    // BOT MESSAGE

    chatMessages.innerHTML += `

      <div class="bot-message">
        ${data.reply}
      </div>

    `;

    chatMessages.scrollTop = chatMessages.scrollHeight;
  } catch (error) {
    console.log(error);

    alert("Chatbot Error");
  }
}

// TOGGLE CHATBOT

function toggleChatbot() {
  const panel = document.getElementById("chatbotPanel");

  const icon = document.querySelector(".chatbot-icon");

  panel.classList.toggle("active");

  if (panel.classList.contains("active")) {
    icon.style.display = "none";
  } else {
    icon.style.display = "block";
  }
}

// SEND MESSAGE

async function sendMessage() {
  const input = document.getElementById("chatInput");

  const message = input.value;

  if (message.trim() === "") {
    return;
  }

  const chatMessages = document.getElementById("chatMessages");

  // USER MESSAGE

  chatMessages.innerHTML += `
  
    <div class="user-message">
      ${message}
    </div>
  
  `;

  input.value = "";

  // AUTO SCROLL

  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        message: message,
      }),
    });

    const data = await response.json();

    // BOT MESSAGE

    chatMessages.innerHTML += `
    
      <div class="bot-message">
        ${data.reply}
      </div>
    
    `;

    chatMessages.scrollTop = chatMessages.scrollHeight;
  } catch (error) {
    console.log(error);

    chatMessages.innerHTML += `
    
      <div class="bot-message">
        Error connecting to AI assistant.
      </div>
    
    `;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("chatInput");

  if (input) {
    input.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        sendMessage();
      }
    });
  }
});
