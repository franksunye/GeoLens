# 🔌 GeoLens - API接口文档

## 📋 API概述

GeoLens 提供专注于GEO (Generative Engine Optimization) 的 RESTful API 服务，支持用户管理、项目管理、内容分析和GEO评分等核心功能。所有API遵循REST设计原则，使用JSON格式进行数据交换。

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

## 📊 内容分析

### 执行内容分析
```http
POST /analysis/analyze
```

**请求体:**
```json
{
  "project_id": "project-uuid",
  "content": "生成式引擎优化(GEO)是一种新型的优化方式，旨在提升品牌在生成式AI中被推荐、被引用的可见性...",
  "title": "GEO优化指南",
  "meta_description": "学习如何优化内容以适应生成式AI",
  "target_keywords": ["GEO", "生成式引擎优化", "AI优化"],
  "brand_keywords": ["GeoLens"]
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "id": "analysis-uuid",
    "project_id": "project-uuid",
    "content_analysis": {
      "seo_analysis": {
        "title_score": 0.85,
        "meta_description_score": 0.90,
        "heading_structure_score": 0.88,
        "overall_score": 0.87
      },
      "readability_analysis": {
        "flesch_reading_ease": 65.2,
        "readability_score": 0.75,
        "reading_level": "适中"
      },
      "structure_analysis": {
        "structure_score": 0.82,
        "heading_hierarchy": ["H1", "H2", "H3"],
        "content_sections": 5
      },
      "content_quality_score": 0.84,
      "recommendations": [
        "建议增加更多相关关键词",
        "优化段落结构以提高可读性"
      ]
    },
    "keyword_analysis": {
      "target_keywords": [
        {
          "keyword": "GEO",
          "frequency": 8,
          "density": 2.1,
          "prominence_score": 8.5
        }
      ],
      "overall_keyword_score": 0.78
    },
    "entity_analysis": {
      "brands": ["GeoLens"],
      "technologies": ["AI", "生成式AI"],
      "total_entities": 5
    },
    "extracted_content": {
      "title": "GEO优化指南",
      "word_count": 380,
      "reading_time": 2
    }
  }
}
```

---

## 🎯 GEO评分

### 计算GEO评分
```http
POST /analysis/geo-score
```

**请求体:**
```json
{
  "project_id": "project-uuid",
  "content": "生成式引擎优化(GEO)是一种新型的优化方式...",
  "title": "GEO优化指南",
  "target_keywords": ["GEO", "生成式引擎优化"],
  "brand_keywords": ["GeoLens"]
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "score_id": "score-uuid",
    "project_id": "project-uuid",
    "geo_score": {
      "overall_score": 78.5,
      "grade": "B+",
      "visibility_estimate": "良好 - 中高AI推荐概率",
      "category_scores": {
        "content_quality": 82.0,
        "technical_optimization": 75.0,
        "keyword_relevance": 80.0,
        "user_experience": 77.0
      },
      "factors": {
        "content_quality": 0.82,
        "content_length": 0.75,
        "readability": 0.80,
        "title_optimization": 0.85,
        "keyword_relevance": 0.80,
        "ai_friendliness": 0.78
      },
      "recommendations": [
        "优化内容结构以提高AI理解度",
        "增加相关概念的明确定义",
        "改进关键词的上下文相关性"
      ],
      "last_updated": "2024-06-03T10:00:00Z"
    },
    "analysis_summary": {
      "content_quality": 0.82,
      "ai_friendliness": 0.78,
      "keyword_relevance": 0.80,
      "entity_count": 5
    }
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

*最后更新: 2024-06-03*
*API版本: v2.0 - GEO专注版本*
