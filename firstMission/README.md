# 🛡️ Authentication API

This API provides user registration and JWT-based authentication for secure access to your application using Djoser and SimpleJWT.

---

## 🔗 Base URL

```
localhost:8000/
```

---

## 📌 Endpoints

---

### ✅ `POST /api/register/`

**Register a new user**

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "your_secure_password",
  "re_password": "your_secure_password",
  "name": "User Fullname",
  "phone_number": "08012345678"
}
```

**Response:**

```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Fullname",
  "phone_number": "08012345678"
}
```

---

### 🔐 `POST /api/jwt/create/`

**Login and get access + refresh tokens**

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "your_secure_password"
}
```

**Response:**

```json
{
  "access": "JWT_ACCESS_TOKEN",
  "refresh": "JWT_REFRESH_TOKEN"
}
```

> 🔑 Use the access token for authenticated requests by setting the header:
> 
> `Authorization: Bearer JWT_ACCESS_TOKEN`

---

### 🔁 `POST /api/jwt/refresh/`

**Refresh the access token using a valid refresh token**

**Request Body:**

```json
{
  "refresh": "JWT_REFRESH_TOKEN"
}
```

**Response:**

```json
{
  "access": "NEW_JWT_ACCESS_TOKEN"
}
```

---

## 📆 Token Expiry

- Access Token: **30 days**
- Refresh Token: **30 days**
- Tokens are configured using **SimpleJWT** in `settings.py`.

---

## ✅ Phone Number Rules

- Must be a valid **Nigerian phone number**
- Accepted formats:
  - `08012345678`
  - `+2348012345678`
- Validation is enforced in the model using regex.

---

## ⚙️ Tech Stack

- Django
- Django REST Framework
- Djoser
- SimpleJWT

---

## 📂 Example `.env` (for development)

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=*
```

---

## ✅ Quick Test URLs

- [POST] `/api/register/` – Register
- [POST] `/api/jwt/create/` – Login
- [POST] `/api/jwt/refresh/` – Refresh Access Token

---

## 🧪 Test With Headers

```http
Authorization: Bearer <your-access-token>
Content-Type: application/json
```

---