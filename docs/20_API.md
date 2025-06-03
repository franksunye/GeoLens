# 🔌 GEO Insight - API接口文档

## 📋 API概述

GEO Insight 提供 RESTful API 服务，支持用户管理、项目管理、AI检测和内容分析等核心功能。所有API遵循REST设计原则，使用JSON格式进行数据交换。

---

## 🌐 基础信息

### API基础URL
```
开发环境: http://localhost:8000/api/v1
生产环境: https://api.geolens.com/api/v1
```

### 认证方式
```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

### 响应格式
```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "timestamp": "2024-05-30T10:00:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": ["email字段不能为空"]
  },
  "timestamp": "2024-05-30T10:00:00Z"
}
```

---

## 🔐 认证接口

### 用户注册
```http
POST /auth/register
```

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "张三"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "full_name": "张三",
      "created_at": "2024-05-30T10:00:00Z"
    },
    "access_token": "jwt-token",
    "refresh_token": "refresh-token"
  }
}
```

### 用户登录
```http
POST /auth/login
```

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

### 刷新令牌
```http
POST /auth/refresh
```

**请求体:**
```json
{
  "refresh_token": "refresh-token"
}
```

### 退出登录
```http
POST /auth/logout
```

---

## 👤 用户管理

### 获取用户信息
```http
GET /users/me
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "full_name": "张三",
    "avatar_url": "https://example.com/avatar.jpg",
    "subscription_plan": "free",
    "created_at": "2024-05-30T10:00:00Z"
  }
}
```

### 更新用户信息
```http
PUT /users/me
```

**请求体:**
```json
{
  "full_name": "李四",
  "avatar_url": "https://example.com/new-avatar.jpg"
}
```

---

## 📁 项目管理

### 创建项目
```http
POST /projects
```

**请求体:**
```json
{
  "name": "Notion品牌监测",
  "domain": "notion.so",
  "description": "监测Notion在AI平台中的表现",
  "industry": "productivity",
  "target_keywords": ["协作工具", "笔记软件", "项目管理"]
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "project-uuid",
    "name": "Notion品牌监测",
    "domain": "notion.so",
    "description": "监测Notion在AI平台中的表现",
    "industry": "productivity",
    "target_keywords": ["协作工具", "笔记软件", "项目管理"],
    "is_active": true,
    "created_at": "2024-05-30T10:00:00Z"
  }
}
```

### 获取项目列表
```http
GET /projects?page=1&limit=10&is_active=true
```

**查询参数:**
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 10, 最大: 100)
- `is_active`: 是否激活 (可选)
- `search`: 搜索关键词 (可选)

### 获取项目详情
```http
GET /projects/{project_id}
```

### 更新项目
```http
PUT /projects/{project_id}
```

### 删除项目
```http
DELETE /projects/{project_id}
```

---

## 🔍 AI引用检测

### 执行检测
```http
POST /mentions/check
```

**请求体:**
```json
{
  "project_id": "project-uuid",
  "prompt": "推荐几个适合团队协作的知识管理工具",
  "platforms": ["chatgpt", "gemini", "perplexity"]
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "check_id": "check-uuid",
    "status": "processing",
    "estimated_completion": "2024-05-30T10:05:00Z"
  }
}
```

### 获取检测结果
```http
GET /mentions/check/{check_id}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "check-uuid",
    "project_id": "project-uuid",
    "prompt": "推荐几个适合团队协作的知识管理工具",
    "status": "completed",
    "results": [
      {
        "platform": "chatgpt",
        "mentioned": true,
        "confidence_score": 0.95,
        "response_text": "Notion是一款非常流行的协作工具...",
        "context_snippet": "...Notion是一款非常流行的协作工具，它结合了笔记、数据库、看板等功能..."
      },
      {
        "platform": "gemini",
        "mentioned": false,
        "confidence_score": 0.12,
        "response_text": "推荐使用Asana、Trello等工具...",
        "context_snippet": null
      }
    ],
    "created_at": "2024-05-30T10:00:00Z",
    "completed_at": "2024-05-30T10:03:00Z"
  }
}
```

### 获取检测历史
```http
GET /mentions/history?project_id={project_id}&page=1&limit=20
```

---

## 📊 GEO评分

### 执行网页评分
```http
POST /geo/score
```

**请求体:**
```json
{
  "project_id": "project-uuid",
  "url": "https://notion.so/product"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "score-uuid",
    "project_id": "project-uuid",
    "url": "https://notion.so/product",
    "total_score": 76,
    "structure_score": 80,
    "content_score": 75,
    "entity_score": 72,
    "keyword_score": 78,
    "analysis": {
      "page_title": "Notion – The all-in-one workspace",
      "meta_description": "A new tool that blends your everyday work apps...",
      "h1_tags": ["The all-in-one workspace"],
      "h2_tags": ["For teams", "For personal use"],
      "keywords_found": ["workspace", "collaboration", "productivity"],
      "entities_found": {
        "PRODUCT": ["Notion"],
        "FEATURE": ["workspace", "collaboration", "database"]
      },
      "word_count": 1250,
      "schema_markup": {
        "type": "SoftwareApplication",
        "name": "Notion"
      }
    },
    "created_at": "2024-05-30T10:00:00Z"
  }
}
```

### 获取评分历史
```http
GET /geo/scores?project_id={project_id}&page=1&limit=20
```

---

## 💡 优化建议

### 生成建议
```http
POST /suggestions/generate
```

**请求体:**
```json
{
  "project_id": "project-uuid",
  "url": "https://notion.so/product",
  "geo_score_id": "score-uuid"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "id": "suggestion-uuid",
        "type": "structure",
        "title": "添加FAQ结构化数据",
        "description": "建议在页面中添加FAQ模块，便于AI识别和引用",
        "priority": "high",
        "estimated_impact": 8,
        "detailed_suggestion": "在页面底部添加常见问题解答部分...",
        "example_implementation": "<script type=\"application/ld+json\">..."
      }
    ]
  }
}
```

### 更新建议状态
```http
PATCH /suggestions/{suggestion_id}
```

**请求体:**
```json
{
  "status": "completed"
}
```

---

## 📈 统计分析

### 项目统计
```http
GET /analytics/project/{project_id}/stats
```

**响应:**
```json
{
  "success": true,
  "data": {
    "total_checks": 45,
    "mentioned_count": 32,
    "mention_rate": 0.71,
    "avg_score": 76.5,
    "score_trend": [
      {"date": "2024-05-01", "score": 72},
      {"date": "2024-05-15", "score": 76},
      {"date": "2024-05-30", "score": 78}
    ],
    "platform_performance": {
      "chatgpt": {"mentions": 15, "total": 20, "rate": 0.75},
      "gemini": {"mentions": 10, "total": 15, "rate": 0.67},
      "perplexity": {"mentions": 7, "total": 10, "rate": 0.70}
    }
  }
}
```

---

## 🔧 系统接口

### 获取AI平台列表
```http
GET /platforms
```

### 获取提示模板
```http
GET /prompts/templates?category=general
```

### 系统健康检查
```http
GET /health
```

**响应:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 86400,
    "database": "connected",
    "redis": "connected",
    "external_apis": {
      "openai": "available",
      "perplexity": "available"
    }
  }
}
```

---

## 📝 错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| VALIDATION_ERROR | 400 | 请求参数验证失败 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| RATE_LIMIT_EXCEEDED | 429 | 请求频率超限 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| SERVICE_UNAVAILABLE | 503 | 服务暂不可用 |

---

## 🚀 API限制

### 频率限制
- **免费用户**: 100次/小时
- **付费用户**: 1000次/小时
- **企业用户**: 10000次/小时

### 数据限制
- **单次检测**: 最多5个平台
- **批量操作**: 最多100条记录
- **文件上传**: 最大10MB

---

*最后更新: 2024-05-30*
*API版本: v1.0*
