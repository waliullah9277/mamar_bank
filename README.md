# 🏦 Mamar Bank

A modern and simple **banking system** web application where users can register, log in, view their dashboard, and perform simulated transactions like deposits and withdrawals. Built using **Django** and **Tailwind CSS**, this project aims to demonstrate core banking system functionality with clean UI and secure authentication.

🔗 **Live Demo**: [https://mamar-banks-s9ge.onrender.com](https://mamar-banks-s9ge.onrender.com)

---

## 🚀 Features

- 🔐 User registration and login with validation  
- 🏦 Dashboard with balance summary  
- 💰 Deposit and withdraw (simulated transactions)  
- 📜 Transaction history tracking  
- 🖼️ Responsive layout with clean Tailwind CSS design  
- 🔄 Password show/hide toggle for better UX  

---

## 🛠️ Tech Stack

- **Backend**: Python, Django  
- **Frontend**: Tailwind CSS, HTML5, CSS, JavaScript  
- **Database**: SQLite (easily switchable to PostgreSQL)  
- **Deployment**: Render  

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/mamar-bank.git
cd mamar-bank
```

### 2. Create and activate virtual environment

```bash
python -m venv env
```

- **Windows:**
  ```bash
  env\Scripts\activate
  ```
- **Linux/Mac:**
  ```bash
  source env/bin/activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` in your browser.

### 6. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

---

## 👤 Author

- **Md. Waliullah**  
  GitHub: [@waliullah9277](https://github.com/waliullah9277)  
  Email: waliullah9252@gmail.com  

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and contribute.
