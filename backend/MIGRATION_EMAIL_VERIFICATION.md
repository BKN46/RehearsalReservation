# 邮箱验证功能 - 数据库迁移说明

## 新增字段

已在 `User` 模型中添加以下字段：

1. `email_verified` (Boolean) - 邮箱是否已验证，默认 False
2. `verification_token` (String, 100) - 邮箱验证令牌，唯一
3. `verification_token_expires` (DateTime) - 验证令牌过期时间

## 迁移方法

### 方法一：删除并重建数据库（开发环境）

如果是开发环境且可以清空数据：

```bash
cd backend
rm instance/rehearsal.db
python app.py
```

这将自动创建新的数据库结构。

### 方法二：使用 SQLite 手动添加字段（保留数据）

如果需要保留现有数据：

```bash
cd backend/instance
sqlite3 rehearsal.db
```

在 SQLite 命令行中执行：

```sql
-- 添加新字段
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN verification_token VARCHAR(100);
ALTER TABLE users ADD COLUMN verification_token_expires DATETIME;

-- 为所有现有用户设置邮箱已验证（因为他们是在功能开启前注册的）
UPDATE users SET email_verified = 1;

-- 退出
.quit
```

### 方法三：使用 Flask-Migrate（推荐用于生产环境）

如果项目配置了 Flask-Migrate：

```bash
cd backend
flask db migrate -m "Add email verification fields"
flask db upgrade
```

## 验证迁移

运行以下 Python 代码检查字段是否添加成功：

```python
from app import app
from models import db, User

with app.app_context():
    # 检查第一个用户的新字段
    user = User.query.first()
    if user:
        print(f"Email verified: {user.email_verified}")
        print(f"Verification token: {user.verification_token}")
        print("Migration successful!")
```

## 注意事项

1. 迁移前请备份数据库文件
2. 对于现有用户，建议将 `email_verified` 设置为 `True`
3. 新注册的用户将根据 `EMAIL_VERIFICATION_ENABLED` 配置决定是否需要验证
