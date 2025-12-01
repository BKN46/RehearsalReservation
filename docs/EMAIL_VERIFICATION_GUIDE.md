# 邮箱验证功能使用说明

## 功能概述

本系统支持可选的邮箱验证功能。通过环境变量控制是否启用邮箱验证，默认关闭。

## 配置方法

### 1. 环境变量配置

复制 `.env.example` 为 `.env`：

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# 邮箱验证功能开关（默认关闭）
EMAIL_VERIFICATION_ENABLED=true  # 设置为 true 启用

# 邮件服务器配置（仅在启用时需要配置）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # Gmail 使用应用专用密码
MAIL_DEFAULT_SENDER=your-email@gmail.com

# 前端地址（用于生成验证链接）
FRONTEND_URL=http://localhost:5173
```

### 2. Gmail 配置示例

如果使用 Gmail 发送邮件：

1. 登录 Google 账号
2. 前往 https://myaccount.google.com/security
3. 启用两步验证
4. 生成"应用专用密码"
5. 将生成的 16 位密码填入 `MAIL_PASSWORD`

### 3. 其他邮件服务商

- **QQ邮箱**：
  ```
  MAIL_SERVER=smtp.qq.com
  MAIL_PORT=587
  MAIL_USE_TLS=true
  ```

- **163邮箱**：
  ```
  MAIL_SERVER=smtp.163.com
  MAIL_PORT=25
  MAIL_USE_TLS=false
  ```

- **Outlook**：
  ```
  MAIL_SERVER=smtp-mail.outlook.com
  MAIL_PORT=587
  MAIL_USE_TLS=true
  ```

## 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

主要新增依赖：
- Flask-Mail==0.9.1

## 功能特性

### 启用邮箱验证时（EMAIL_VERIFICATION_ENABLED=true）

1. **注册流程**：
   - 用户注册后自动发送验证邮件
   - 账户初始状态为未激活
   - 用户需要点击邮件中的验证链接
   - 验证成功后账户自动激活

2. **验证链接**：
   - 有效期：30 分钟
   - 格式：`http://your-domain/verify-email?token=xxx`
   - 一次性使用

3. **重发功能**：
   - 验证链接过期可重新发送
   - 防止频繁发送（建议在生产环境添加频率限制）

### 关闭邮箱验证时（EMAIL_VERIFICATION_ENABLED=false，默认）

1. **注册流程**：
   - 用户注册后不发送验证邮件
   - 账户需要管理员手动激活
   - 保持原有的管理员审核流程

## API 接口

### 1. 注册（POST /api/auth/register）

**请求**：
```json
{
  "student_id": "20231001",
  "name": "张三",
  "email": "zhangsan@buaa.edu.cn",
  "password": "password123",
  "phone": "13800138000"
}
```

**响应（启用邮箱验证）**：
```json
{
  "message": "Registration successful. Please check your email to verify your account.",
  "user": {...},
  "requires_activation": true,
  "email_sent": true
}
```

**响应（关闭邮箱验证）**：
```json
{
  "message": "Registration successful. Your account needs to be activated by an administrator.",
  "user": {...},
  "requires_activation": true
}
```

### 2. 验证邮箱（POST /api/auth/verify-email）

**请求**：
```json
{
  "token": "verification_token_from_email"
}
```

**响应**：
```json
{
  "message": "Email verified successfully. Your account is now active.",
  "user": {...}
}
```

### 3. 重发验证邮件（POST /api/auth/resend-verification）

**请求**：
```json
{
  "email": "zhangsan@buaa.edu.cn"
}
```

**响应**：
```json
{
  "message": "Verification email sent successfully"
}
```

### 4. 检查验证状态（GET /api/auth/check-verification-status）

需要认证。

**响应**：
```json
{
  "email_verified": true,
  "email_verification_enabled": true
}
```

## 前端页面

### 1. 验证邮箱页面

路由：`/verify-email?token=xxx`

功能：
- 自动验证令牌
- 显示验证结果
- 成功后自动跳转登录（5秒倒计时）
- 失败时提供重发选项

### 2. 注册页面更新

- 根据响应显示不同提示信息
- 邮箱验证成功提示查收邮件
- 关闭验证时提示等待管理员激活

## 数据库迁移

参见 `MIGRATION_EMAIL_VERIFICATION.md`

## 测试

### 1. 测试邮件发送（启用验证）

```bash
# 设置环境变量
export EMAIL_VERIFICATION_ENABLED=true
export MAIL_SERVER=smtp.gmail.com
# ... 其他邮件配置

# 启动后端
python app.py
```

注册一个新用户，检查邮箱是否收到验证邮件。

### 2. 测试验证流程

1. 注册用户
2. 查收邮件
3. 点击验证链接
4. 确认账户已激活
5. 使用账户登录

### 3. 测试关闭验证

```bash
# 设置环境变量
export EMAIL_VERIFICATION_ENABLED=false

# 启动后端
python app.py
```

注册用户应该不会收到邮件，需要管理员手动激活。

## 生产环境建议

1. **使用专业邮件服务**：
   - SendGrid
   - Amazon SES
   - 阿里云邮件推送
   - 腾讯云邮件推送

2. **添加频率限制**：
   - 限制每个邮箱每天可重发次数
   - 防止恶意注册

3. **日志记录**：
   - 记录邮件发送成功/失败
   - 便于排查问题

4. **监控告警**：
   - 邮件发送失败率告警
   - 验证成功率统计

## 故障排查

### 邮件发送失败

1. 检查环境变量是否正确配置
2. 检查邮箱密码（Gmail 需使用应用专用密码）
3. 检查防火墙是否阻止 SMTP 端口
4. 查看后端日志获取详细错误信息

### 验证链接无效

1. 检查令牌是否过期（30分钟有效期）
2. 使用重发功能获取新链接
3. 检查前端 URL 配置是否正确

## 安全注意事项

1. **环境变量保护**：
   - 不要将 `.env` 文件提交到版本控制
   - 使用应用专用密码，不要使用主密码

2. **令牌安全**：
   - 使用加密随机令牌
   - 设置合理的过期时间
   - 验证后立即清除令牌

3. **邮箱验证**：
   - 确保邮箱属于 @buaa.edu.cn 域
   - 防止使用临时邮箱服务

## 总结

- **默认关闭**：不影响现有功能
- **可选启用**：通过环境变量灵活控制
- **向后兼容**：支持管理员审核流程
- **易于配置**：只需修改环境变量
