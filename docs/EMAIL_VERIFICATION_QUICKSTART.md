# 邮箱验证功能 - 快速开始

## 功能说明

已实现邮箱验证功能，**默认关闭**，通过环境变量控制。

## 快速配置

### 1. 保持关闭（默认，无需配置）

不需要任何配置，系统将继续使用管理员审核流程。

### 2. 启用邮箱验证

#### 步骤一：安装依赖

```bash
cd backend
pip install Flask-Mail==0.9.1
```

#### 步骤二：配置环境变量

创建或编辑 `backend/.env` 文件：

```bash
EMAIL_VERIFICATION_ENABLED=true
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
FRONTEND_URL=http://localhost:5173
```

#### 步骤三：数据库迁移

```bash
cd backend/instance
sqlite3 rehearsal.db
```

执行 SQL：

```sql
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN verification_token VARCHAR(100);
ALTER TABLE users ADD COLUMN verification_token_expires DATETIME;
UPDATE users SET email_verified = 1;
.quit
```

#### 步骤四：重启服务

```bash
cd backend
python app.py
```

## 详细文档

- 完整使用说明：`EMAIL_VERIFICATION_GUIDE.md`
- 数据库迁移：`backend/MIGRATION_EMAIL_VERIFICATION.md`

## 新增文件

### 后端
- `backend/email_service.py` - 邮件发送服务
- `backend/MIGRATION_EMAIL_VERIFICATION.md` - 迁移说明

### 前端
- `frontend/src/views/VerifyEmail.vue` - 邮箱验证页面

### 文档
- `EMAIL_VERIFICATION_GUIDE.md` - 详细使用指南

## 修改文件

### 后端
- `backend/.env.example` - 添加邮箱验证配置项
- `backend/requirements.txt` - 添加 Flask-Mail 依赖
- `backend/models.py` - User 模型添加验证字段
- `backend/app.py` - 初始化邮件服务
- `backend/routes/auth.py` - 添加验证相关 API

### 前端
- `frontend/src/services/api.js` - 添加 authService
- `frontend/src/router/index.js` - 添加验证页面路由
- `frontend/src/views/Register.vue` - 更新注册提示
- `frontend/src/stores/auth.js` - 修改注册逻辑

## API 端点

- `POST /api/auth/verify-email` - 验证邮箱
- `POST /api/auth/resend-verification` - 重发验证邮件
- `GET /api/auth/check-verification-status` - 检查验证状态

## 注意事项

1. **Gmail 用户**：需要生成"应用专用密码"
2. **数据备份**：迁移前请备份数据库
3. **现有用户**：已存在的用户邮箱自动标记为已验证
4. **默认关闭**：不影响现有系统功能
