# 🔌 GeoLens - API接口文档

## 📋 API概述

GeoLens 提供专业的AI引用检测 RESTful API 服务。当前版本v0.7.0专注于核心引用检测功能，支持多模型并行检测、数据持久化和历史记录管理。已完成端到端验证，生产就绪。

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
POST /api/v1/auth/register
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
POST /api/v1/auth/login
```

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

### 刷新Token
```http
POST /api/v1/auth/refresh
```

**请求体:**
```json
{
  "refresh_token": "refresh-token"
}
```

---

## 👤 用户管理

### 获取用户信息
```http
GET /api/v1/auth/me
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
PUT /api/v1/auth/me
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
POST /api/v1/projects/
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
GET /api/v1/projects/?page=1&limit=10&is_active=true
```

**查询参数:**
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 10, 最大: 100)
- `is_active`: 是否激活 (可选)
- `search`: 搜索关键词 (可选)

### 获取项目详情
```http
GET /api/v1/projects/{project_id}
```

### 更新项目
```http
PUT /api/v1/projects/{project_id}
```

### 删除项目
```http
DELETE /api/v1/projects/{project_id}
```

---

## 🔍 引用检测

### 执行引用检测 ✅ 已验证
```http
POST /api/v1/api/check-mention
```

**请求体:**
```json
{
  "project_id": "project-uuid",
  "prompt": "推荐几个适合团队协作的知识管理工具",
  "brands": ["Notion", "Obsidian", "Roam Research"],
  "models": ["doubao", "deepseek"],
  "api_keys": {
    "DOUBAO_API_KEY": "your-key",
    "DEEPSEEK_API_KEY": "your-key"
  },
  "max_tokens": 300,
  "temperature": 0.3,
  "parallel_execution": true,
  "metadata": {}
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "check_id": "check-uuid",
    "project_id": "project-uuid",
    "user_id": "user-uuid",
    "prompt": "推荐几个适合团队协作的知识管理工具",
    "brands": ["Notion", "Obsidian", "Roam Research"],
    "status": "completed",
    "results": [
      {
        "model": "doubao",
        "response_text": "我推荐以下几个优秀的知识管理工具：1. Notion - 功能全面的工作空间...",
        "mentions": [
          {
            "brand": "Notion",
            "mentioned": true,
            "confidence": 0.95,
            "context": "Notion - 功能全面的工作空间，支持文档、数据库、看板等多种功能",
            "position": 1
          },
          {
            "brand": "Obsidian",
            "mentioned": false,
            "confidence": 0.05,
            "context": null,
            "position": null
          }
        ],
        "processing_time_ms": 1250,
        "error": null
      }
    ],
    "summary": {
      "total_mentions": 1,
      "mention_rate": 0.33,
      "avg_confidence": 0.95,
      "models_used": ["doubao"],
      "brands_checked": ["Notion", "Obsidian", "Roam Research"]
    },
    "created_at": "2024-06-03T10:00:00Z",
    "completed_at": "2024-06-03T10:02:30Z"
  },
  "message": "引用检测完成"
}
```

### 获取检测历史
```http
GET /api/v1/api/get-history?project_id={project_id}&page=1&limit=20
```

**查询参数:**
- `project_id`: 项目ID (必需)
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 20, 最大: 100)
- `brand`: 筛选特定品牌 (可选)
- `model`: 筛选特定模型 (可选)

**响应:**
```json
{
  "success": true,
  "data": {
    "checks": [
      {
        "id": "check-uuid-1",
        "prompt": "推荐几个适合团队协作的知识管理工具",
        "brands_checked": ["Notion", "Obsidian"],
        "models_used": ["doubao", "deepseek"],
        "total_mentions": 3,
        "mention_rate": 0.75,
        "created_at": "2024-06-03T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "pages": 3
    }
  }
}
```

---

## 📝 Prompt模板管理

### 保存自定义Prompt模板
```http
POST /api/v1/api/save-prompt
```

**请求体:**
```json
{
  "name": "协作工具推荐",
  "category": "productivity",
  "template": "推荐几个适合{team_size}人团队使用的{tool_type}工具",
  "variables": {
    "team_size": "string",
    "tool_type": "string"
  },
  "description": "用于推荐团队协作工具的模板"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "template-uuid",
    "name": "协作工具推荐",
    "category": "productivity",
    "template": "推荐几个适合{team_size}人团队使用的{tool_type}工具",
    "variables": {
      "team_size": "string",
      "tool_type": "string"
    },
    "usage_count": 0,
    "created_at": "2024-06-03T10:00:00Z"
  }
}
```

---

## 📊 引用频率分析

### 获取品牌引用统计
```http
GET /api/v1/api/analytics/mentions?project_id={project_id}&brand={brand}&timeframe=30d
```

**查询参数:**
- `project_id`: 项目ID (必需)
- `brand`: 品牌名称 (可选，不指定则返回所有品牌)
- `timeframe`: 时间范围 (7d, 30d, 90d, 默认30d)
- `model`: 筛选特定模型 (可选)

**响应:**
```json
{
  "success": true,
  "data": {
    "brand": "Notion",
    "timeframe": "30d",
    "total_checks": 45,
    "total_mentions": 32,
    "mention_rate": 0.71,
    "model_performance": {
      "doubao": {
        "checks": 20,
        "mentions": 15,
        "rate": 0.75,
        "avg_confidence": 0.92
      },
      "deepseek": {
        "checks": 15,
        "mentions": 10,
        "rate": 0.67,
        "avg_confidence": 0.88
      },
      "chatgpt": {
        "checks": 10,
        "mentions": 7,
        "rate": 0.70,
        "avg_confidence": 0.90
      }
    },
    "trend_data": [
      {"date": "2024-05-01", "mentions": 5, "checks": 7},
      {"date": "2024-05-15", "mentions": 8, "checks": 12},
      {"date": "2024-05-30", "mentions": 12, "checks": 15}
    ],
    "top_contexts": [
      "推荐作为团队协作工具",
      "适合知识管理和文档整理",
      "支持多种内容类型的工作空间"
    ]
  }
}
```

### 竞品对比分析
```http
GET /api/v1/api/analytics/compare?project_id={project_id}&brands=Notion,Obsidian,Roam
```

**响应:**
```json
{
  "success": true,
  "data": {
    "comparison": [
      {
        "brand": "Notion",
        "mention_rate": 0.75,
        "avg_confidence": 0.92,
        "total_mentions": 32
      },
      {
        "brand": "Obsidian",
        "mention_rate": 0.45,
        "avg_confidence": 0.85,
        "total_mentions": 18
      },
      {
        "brand": "Roam Research",
        "mention_rate": 0.30,
        "avg_confidence": 0.78,
        "total_mentions": 12
      }
    ],
    "insights": [
      "Notion在团队协作场景中被提及最多",
      "Obsidian在个人知识管理场景表现较好"
    ]
  }
}
```

---

## 🎯 品牌检测专用API

### 仅执行品牌检测 ✅ 已实现
```http
POST /api/v1/api/detect-brands-only
```

**请求体:**
```json
{
  "text": "我推荐使用Notion来管理团队知识，它比Obsidian更适合协作",
  "brands": ["Notion", "Obsidian", "Roam Research"],
  "strategy": "improved"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "results": {
      "Notion": {
        "mentioned": true,
        "confidence": 0.95,
        "contexts": ["我推荐使用Notion来管理团队知识"],
        "positions": [6],
        "detection_method": "exact_match"
      },
      "Obsidian": {
        "mentioned": true,
        "confidence": 0.90,
        "contexts": ["它比Obsidian更适合协作"],
        "positions": [25],
        "detection_method": "exact_match"
      }
    },
    "statistics": {
      "total_brands": 3,
      "mentioned_brands": 2,
      "mention_rate": 0.67
    },
    "strategy_used": "improved"
  },
  "message": "品牌检测完成"
}
```

### 比较检测策略 ✅ 已实现
```http
POST /api/v1/api/compare-strategies
```

**请求体:**
```json
{
  "text": "我推荐使用Notion来管理团队知识",
  "brands": ["Notion", "Obsidian"],
  "strategy": "improved"
}
```

### 获取可用策略 ✅ 已实现
```http
GET /api/v1/api/strategies
```

**响应:**
```json
{
  "success": true,
  "data": {
    "strategies": ["simple", "improved", "hybrid"],
    "default_strategy": "improved",
    "descriptions": {
      "simple": "简单字符串匹配",
      "improved": "改进的检测算法（推荐）",
      "hybrid": "混合策略"
    }
  },
  "message": "获取策略列表成功"
}
```

---

## 🚧 计划中功能

### 计划中功能 (未来版本)

**优化建议系统**
- 基于引用检测结果的优化建议
- 品牌可见性提升策略
- 竞品分析洞察
- 内容优化建议

**高级分析功能**
- 项目统计仪表板
- 趋势预测分析
- 自定义报告生成

---

## 🔌 AI服务API

### 获取AI提供商列表
```http
GET /api/v1/ai/providers
```

### AI聊天完成
```http
POST /api/v1/ai/chat
```

### 品牌分析
```http
POST /api/v1/ai/analyze/brand
```

### AI服务健康检查
```http
GET /api/v1/ai/health
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

### 引用检测服务健康检查
```http
GET /api/v1/api/health
```

**响应:**
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "id": "doubao",
        "name": "豆包",
        "provider": "ByteDance",
        "status": "active",
        "rate_limit": 60
      },
      {
        "id": "deepseek",
        "name": "DeepSeek",
        "provider": "DeepSeek",
        "status": "active",
        "rate_limit": 100
      }
    ]
  }
}
```

### 获取Prompt模板列表
```http
GET /api/v1/api/prompts/templates?category=productivity&page=1&limit=10
```

**响应:**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": "template-uuid",
        "name": "协作工具推荐",
        "category": "productivity",
        "template": "推荐几个适合{team_size}人团队使用的{tool_type}工具",
        "usage_count": 25,
        "created_at": "2024-06-01T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 15,
      "pages": 2
    }
  }
}
```

### 获取项目统计
```http
GET /api/v1/projects/stats
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
- **单次检测**: 最多5个AI模型，10个品牌
- **批量操作**: 最多100条记录
- **Prompt长度**: 最大2000字符

---

*最后更新: 2024-06-03*
*API版本: v2.0 - 引用检测专注版本*
