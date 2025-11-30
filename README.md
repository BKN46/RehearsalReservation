# 排练室预约系统

基于 Vue.js + Flask + SQLite 的排练室预约管理系统

## 功能特性

### 1. 用户系统
- ✅ 用户注册（学号 + 姓名 + 校内邮箱 + 密码）
- ✅ 校内邮箱验证（必须以 @buaa.edu.cn 结尾）
- ✅ 可选填写手机号
- ✅ 用户登录/登出
- ✅ 个人信息管理

### 2. 预约系统
- ✅ 支持多校区（学院路校区、沙河校区）
- ✅ 按小时预约时间段
  - 上午：8:00-12:00
  - 下午：13:00-18:00
  - 晚上：19:00-22:00
- ✅ 并发控制（支持最高20并发场景）
- ✅ 数据库悲观锁防止冲突
- ✅ 仅可预约一周内的时间
- ✅ 查看本周预约情况
- ✅ 取消预约功能

### 3. 管理系统（仅管理员）
- ✅ 设置不可预约时间段
- ✅ 管理钥匙管理员信息
- ✅ 禁用/启用用户权限
- ✅ 查看所有用户

### 4. 钥匙管理系统
- ✅ 已预约用户登记取钥匙
- ✅ 公示钥匙领取记录
- ✅ 显示当前钥匙管理员信息

### 5. 设备借用系统
- ✅ 登记借用设备
- ✅ 确认归还设备
- ✅ 查看当前借用情况
- ✅ 个人借用记录

### 6. 设备登记系统
- ✅ 登记个人设备信息
  - 所在校区
  - 设备类型
  - 设备名称
  - 放置位置
  - 共享状态
  - 联系方式
  - 备注
- ✅ 查看所有设备列表
- ✅ 筛选共享设备
- ✅ 编辑/删除个人设备

## 技术栈

### 后端
- **框架**: Flask 3.0
- **数据库**: SQLite
- **ORM**: Flask-SQLAlchemy
- **认证**: Flask-JWT-Extended
- **跨域**: Flask-CORS

### 前端
- **框架**: Vue 3
- **构建工具**: Vite 6
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **UI组件**: Element Plus
- **HTTP客户端**: Axios

## 项目结构

```
RehearsalReservation/
├── backend/                 # Flask 后端
│   ├── app.py              # 应用入口
│   ├── models.py           # 数据库模型
│   ├── routes/             # API路由
│   │   ├── auth.py         # 认证相关
│   │   ├── reservation.py  # 预约相关
│   │   ├── admin.py        # 管理员相关
│   │   ├── key_management.py  # 钥匙管理
│   │   └── equipment.py    # 设备管理
│   ├── requirements.txt    # Python依赖
│   └── .env.example        # 环境变量示例
│
└── frontend/               # Vue 前端
    ├── public/
    ├── src/
    │   ├── assets/         # 静态资源
    │   ├── components/     # Vue组件
    │   ├── router/         # 路由配置
    │   ├── stores/         # Pinia状态管理
    │   ├── services/       # API服务
    │   ├── utils/          # 工具函数
    │   ├── views/          # 页面组件
    │   ├── App.vue         # 根组件
    │   └── main.js         # 入口文件
    ├── package.json        # npm依赖
    └── vue.config.js       # Vue配置
```

## 安装指南

### 环境要求
- Python 3.8+
- Node.js 14+
- npm 或 yarn

### 后端安装

1. 进入后端目录
```powershell
cd backend
```

2. 创建虚拟环境（推荐）
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. 安装依赖
```powershell
pip install -r requirements.txt
```

4. 配置环境变量
```powershell
Copy-Item .env.example .env
# 编辑 .env 文件，设置密钥
```

5. 运行后端
```powershell
python app.py
```

后端将在 `http://localhost:5000` 启动

**默认管理员账号**:
- 邮箱: `admin@buaa.edu.cn`
- 密码: `admin123`

### 前端安装

1. 进入前端目录
```powershell
cd frontend
```

2. 安装依赖
```powershell
npm install
```

3. 运行开发服务器
```powershell
npm run dev
```

前端将在 `http://localhost:8080` 启动

4. 构建生产版本
```powershell
npm run build
```

## API 文档

### 认证相关 (`/api/auth`)

#### 注册
- **POST** `/api/auth/register`
- Body: `{ student_id, name, email, password, phone? }`

#### 登录
- **POST** `/api/auth/login`
- Body: `{ email, password }`

#### 获取当前用户
- **GET** `/api/auth/me`
- Headers: `Authorization: Bearer <token>`

#### 更新用户信息
- **PUT** `/api/auth/update-profile`
- Headers: `Authorization: Bearer <token>`
- Body: `{ name?, phone?, password? }`

### 预约相关 (`/api/reservation`)

#### 获取校区列表
- **GET** `/api/reservation/campuses`

#### 创建预约
- **POST** `/api/reservation/create`
- Headers: `Authorization: Bearer <token>`
- Body: `{ campus_id, date, start_hour, end_hour }`

#### 获取我的预约
- **GET** `/api/reservation/my-reservations`
- Headers: `Authorization: Bearer <token>`

#### 获取本周预约
- **GET** `/api/reservation/weekly?campus_id=<id>`

#### 取消预约
- **DELETE** `/api/reservation/<id>`
- Headers: `Authorization: Bearer <token>`

### 钥匙管理 (`/api/key`)

#### 登记取钥匙
- **POST** `/api/key/pickup/<reservation_id>`
- Headers: `Authorization: Bearer <token>`

#### 获取钥匙领取情况
- **GET** `/api/key/pickups?campus_id=<id>`

#### 获取钥匙管理员
- **GET** `/api/key/managers/<campus_id>`

### 设备管理 (`/api/equipment`)

#### 借用设备
- **POST** `/api/equipment/borrow`
- Headers: `Authorization: Bearer <token>`
- Body: `{ equipment_name, equipment_type?, notes? }`

#### 归还设备
- **POST** `/api/equipment/borrow/<id>/return`
- Headers: `Authorization: Bearer <token>`

#### 登记设备
- **POST** `/api/equipment/register`
- Headers: `Authorization: Bearer <token>`
- Body: `{ campus_id, equipment_type, equipment_name, location, is_shared, contact, notes? }`

#### 获取设备列表
- **GET** `/api/equipment/list?campus_id=<id>&is_shared=<bool>`

### 管理员功能 (`/api/admin`)

#### 创建不可预约时间
- **POST** `/api/admin/unavailable-times`
- Headers: `Authorization: Bearer <token>` (需要管理员权限)
- Body: `{ campus_id, date, start_hour, end_hour, reason? }`

#### 管理钥匙管理员
- **POST** `/api/admin/key-managers`
- **PUT** `/api/admin/key-managers/<id>`
- **DELETE** `/api/admin/key-managers/<id>`

#### 管理用户
- **GET** `/api/admin/users`
- **PUT** `/api/admin/users/<id>/toggle-active`

## 数据库设计

### 主要表结构

#### users (用户表)
- id: 主键
- student_id: 学号（唯一）
- name: 姓名
- email: 邮箱（唯一，@buaa.edu.cn）
- password_hash: 密码哈希
- phone: 手机号
- is_admin: 是否管理员
- is_active: 是否启用

#### campuses (校区表)
- id: 主键
- name: 校区名称

#### reservations (预约表)
- id: 主键
- user_id: 用户ID
- campus_id: 校区ID
- date: 日期
- start_hour: 开始时间
- end_hour: 结束时间
- status: 状态
- key_picked_up: 是否已取钥匙

#### equipment (设备表)
- id: 主键
- user_id: 所有者ID
- campus_id: 校区ID
- equipment_type: 设备类型
- equipment_name: 设备名称
- location: 放置位置
- is_shared: 是否共享
- contact: 联系方式

## 并发控制

系统使用 SQLAlchemy 的悲观锁机制处理并发预约：

```python
# 在事务中使用 with_for_update() 获取行级锁
query.with_for_update().first()
```

这确保在高并发场景（最高20并发）下，同一时间段不会被多次预约。

## 开发说明

### 添加新功能

1. **后端**: 在 `backend/routes/` 下创建新的路由文件
2. **前端**: 在 `frontend/src/views/` 下创建新的页面组件
3. 在 `frontend/src/services/api.js` 中添加API调用函数
4. 在 `frontend/src/router/index.js` 中添加路由

### 数据库迁移

如果修改了数据模型，需要删除现有数据库重新初始化：

```powershell
cd backend
Remove-Item rehearsal.db
python app.py  # 会自动创建新数据库
```

## 注意事项

1. **安全性**: 生产环境请修改 `.env` 文件中的密钥
2. **邮箱验证**: 目前只验证邮箱格式，未实现邮件发送
3. **时间段**: 可预约时间固定为 8:00-12:00、13:00-18:00、19:00-22:00
4. **预约限制**: 只能预约未来一周内的时间

## 许可证

MIT License

## 作者

排练室预约系统开发团队
