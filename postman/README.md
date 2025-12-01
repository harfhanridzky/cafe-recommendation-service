# Postman Collection - JWT Authentication Testing

## Cara Import ke Postman

1. Buka Postman
2. Klik **Import** (pojok kiri atas)
3. Pilih file: `postman/Cafe_Recommendation_JWT_Auth.postman_collection.json`
4. Klik **Import**

## Struktur Collection

```
📁 Cafe Recommendation Service - JWT Authentication
├── 📁 0. Health Check
│   ├── Health Check
│   └── Root Info
├── 📁 1. Authentication Flow
│   ├── 1.1 Register New User ✅
│   ├── 1.2 Register Duplicate Email (Should Fail) ❌
│   ├── 1.3 Login - Get JWT Token ✅
│   ├── 1.4 Login - Wrong Password (Should Fail) ❌
│   └── 1.5 Login - Non-existent Email (Should Fail) ❌
├── 📁 2. Protected Endpoints (With JWT)
│   ├── 2.1 Get Current User (/auth/me) 🔒
│   ├── 2.2 Get Recommendations (Protected) 🔒
│   └── 2.3 Get Recommendations with Price Filter 🔒
├── 📁 3. Without JWT (Should Fail)
│   ├── 3.1 Get /auth/me Without Token ❌
│   ├── 3.2 Get Recommendations Without Token ❌
│   └── 3.3 Get Recommendations With Invalid Token ❌
└── 📁 4. Public Endpoints (No Auth Required)
    └── 4.1 Search Cafes (Public) ✅
```

## Cara Testing

### Langkah 1: Pastikan Server Berjalan
```bash
cd /Users/mac/Praktikum/TST_Tubes_Implementation
source venv/bin/activate
uvicorn app.main:app --reload
```

### Langkah 2: Jalankan Request Berurutan

1. **Health Check** - Pastikan server berjalan
2. **Register** - Buat user baru
3. **Login** - Dapatkan JWT token (otomatis tersimpan)
4. **Protected Endpoints** - Test dengan token
5. **Without JWT** - Verifikasi endpoint terlindungi

## Fitur Collection

### Auto-save JWT Token
Setelah login berhasil, token otomatis disimpan ke variable `{{jwt_token}}` dan digunakan di request berikutnya.

### Automated Tests
Setiap request memiliki test script untuk memvalidasi:
- Status code yang benar
- Response body sesuai ekspektasi
- Error handling yang tepat

### Variables
| Variable | Nilai Default | Keterangan |
|----------|---------------|------------|
| `base_url` | `http://localhost:8000` | URL server |
| `jwt_token` | (auto-filled) | Token dari login |
| `user_email` | `testuser@example.com` | Email untuk testing |
| `user_password` | `securepassword123` | Password untuk testing |

## Expected Results

| Request | Expected Status | Keterangan |
|---------|-----------------|------------|
| Register | 201 Created | User berhasil dibuat |
| Register (duplicate) | 400 Bad Request | Email sudah terdaftar |
| Login | 200 OK | Token diterima |
| Login (wrong password) | 401 Unauthorized | Kredensial salah |
| /auth/me (with token) | 200 OK | User info |
| /auth/me (no token) | 403 Forbidden | Tidak terautentikasi |
| /recommendations (with token) | 200 OK | Cafe recommendations |
| /recommendations (no token) | 403 Forbidden | Tidak terautentikasi |
| /recommendations (invalid token) | 401 Unauthorized | Token tidak valid |
| /search | 200 OK | Public endpoint |

## Screenshots untuk Dokumentasi

Saat testing, ambil screenshot untuk:
1. **Register sukses** - menunjukkan user terdaftar
2. **Login sukses** - menunjukkan JWT token diterima
3. **Request dengan token** - menunjukkan akses berhasil
4. **Request tanpa token** - menunjukkan 403 Forbidden
5. **Request dengan token invalid** - menunjukkan 401 Unauthorized
