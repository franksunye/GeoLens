# 🗄️ GEO Insight - 数据库设计文档

## 📋 数据库概述

GEO Insight 使用 PostgreSQL 作为主数据库，通过 Supabase 提供的托管服务。数据库设计遵循第三范式，确保数据一致性和查询性能。

---

## 🎯 设计原则

### 核心原则
- **数据一致性**: 严格的外键约束和事务控制
- **查询性能**: 合理的索引设计和查询优化
- **扩展性**: 支持水平分片和垂直扩展
- **安全性**: 行级安全策略(RLS)和数据加密
- **可维护性**: 清晰的命名规范和文档

### 命名规范
- **表名**: 小写复数形式，下划线分隔 (如: `user_projects`)
- **字段名**: 小写，下划线分隔 (如: `created_at`)
- **主键**: 统一使用 `id` 字段
- **外键**: `{表名}_id` 格式 (如: `user_id`)
- **索引**: `idx_{表名}_{字段名}` 格式

---

## 📊 数据库架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户与认证                              │
├─────────────────────────────────────────────────────────────┤
│  users (用户表)  │  user_sessions (会话表)                    │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                        项目管理                               │
├─────────────────────────────────────────────────────────────┤
│  projects (项目表)  │  project_settings (项目设置表)          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                        检测与分析                              │
├─────────────────────────────────────────────────────────────┤
│  mention_checks     │  geo_scores      │  geo_suggestions   │
│  (引用检测表)        │  (评分表)         │  (建议表)           │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                        系统与配置                              │
├─────────────────────────────────────────────────────────────┤
│  ai_platforms       │  prompt_templates │  system_configs   │
│  (AI平台表)          │  (提示模板表)      │  (系统配置表)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 数据表设计

### 1. 用户表 (users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    full_name VARCHAR(100),
    avatar_url TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    subscription_plan VARCHAR(20) DEFAULT 'free',
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription ON users(subscription_plan, subscription_expires_at);
```

### 2. 项目表 (projects)
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    description TEXT,
    industry VARCHAR(50),
    target_keywords TEXT[], -- PostgreSQL数组类型
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_domain ON projects(domain);
CREATE INDEX idx_projects_active ON projects(is_active, created_at);
```

### 3. AI平台表 (ai_platforms)
```sql
CREATE TABLE ai_platforms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL, -- 'ChatGPT', 'Gemini', 'Perplexity'
    display_name VARCHAR(100) NOT NULL,
    api_endpoint TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit_per_minute INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 初始数据
INSERT INTO ai_platforms (name, display_name, api_endpoint) VALUES
('chatgpt', 'ChatGPT', 'https://api.openai.com/v1/chat/completions'),
('gemini', 'Google Gemini', 'https://generativelanguage.googleapis.com/v1/models'),
('perplexity', 'Perplexity AI', 'https://api.perplexity.ai/chat/completions');
```

### 4. 引用检测表 (mention_checks)
```sql
CREATE TABLE mention_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    platform_id UUID NOT NULL REFERENCES ai_platforms(id),
    prompt TEXT NOT NULL,
    response_text TEXT,
    mentioned BOOLEAN DEFAULT FALSE,
    confidence_score DECIMAL(3,2), -- 0.00-1.00
    context_snippet TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_mention_checks_project ON mention_checks(project_id, created_at DESC);
CREATE INDEX idx_mention_checks_platform ON mention_checks(platform_id);
CREATE INDEX idx_mention_checks_mentioned ON mention_checks(mentioned, created_at);
```

### 5. GEO评分表 (geo_scores)
```sql
CREATE TABLE geo_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    total_score INTEGER CHECK (total_score >= 0 AND total_score <= 100),
    structure_score INTEGER CHECK (structure_score >= 0 AND structure_score <= 100),
    content_score INTEGER CHECK (content_score >= 0 AND content_score <= 100),
    entity_score INTEGER CHECK (entity_score >= 0 AND entity_score <= 100),
    keyword_score INTEGER CHECK (keyword_score >= 0 AND keyword_score <= 100),
    
    -- 详细分析数据
    page_title TEXT,
    meta_description TEXT,
    h1_tags TEXT[],
    h2_tags TEXT[],
    keywords_found TEXT[],
    entities_found JSONB,
    schema_markup JSONB,
    word_count INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_geo_scores_project ON geo_scores(project_id, created_at DESC);
CREATE INDEX idx_geo_scores_url ON geo_scores(url);
CREATE INDEX idx_geo_scores_total ON geo_scores(total_score DESC);
```

### 6. 优化建议表 (geo_suggestions)
```sql
CREATE TABLE geo_suggestions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    geo_score_id UUID REFERENCES geo_scores(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    suggestion_type VARCHAR(50) NOT NULL, -- 'structure', 'content', 'entity', 'keyword'
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'ignored'
    estimated_impact INTEGER CHECK (estimated_impact >= 1 AND estimated_impact <= 10),
    
    -- AI生成的详细建议
    detailed_suggestion TEXT,
    example_implementation TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_geo_suggestions_project ON geo_suggestions(project_id, status);
CREATE INDEX idx_geo_suggestions_score ON geo_suggestions(geo_score_id);
CREATE INDEX idx_geo_suggestions_priority ON geo_suggestions(priority, created_at);
```

### 7. 提示模板表 (prompt_templates)
```sql
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'general', 'industry_specific', 'competitor'
    template TEXT NOT NULL,
    variables JSONB, -- 模板变量定义
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 初始模板数据
INSERT INTO prompt_templates (name, category, template, variables) VALUES
('协作工具推荐', 'general', '推荐几个适合{team_size}人团队使用的{tool_type}工具', 
 '{"team_size": "string", "tool_type": "string"}'),
('项目管理软件', 'general', '有哪些好用的项目管理软件适合{industry}行业？', 
 '{"industry": "string"}');
```

---

## 🔐 安全策略

### Row Level Security (RLS)
```sql
-- 启用RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE mention_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE geo_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE geo_suggestions ENABLE ROW LEVEL SECURITY;

-- 用户只能访问自己的项目
CREATE POLICY "Users can only access their own projects" ON projects
    FOR ALL USING (auth.uid() = user_id);

-- 用户只能访问自己项目的检测记录
CREATE POLICY "Users can only access their project checks" ON mention_checks
    FOR ALL USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = auth.uid()
        )
    );
```

### 数据加密
```sql
-- 敏感字段加密扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 加密存储API密钥等敏感信息
CREATE TABLE user_api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(50) NOT NULL,
    encrypted_key TEXT NOT NULL, -- 使用pgp_sym_encrypt加密
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 📈 性能优化

### 索引策略
```sql
-- 复合索引优化查询
CREATE INDEX idx_mention_checks_project_platform_date 
ON mention_checks(project_id, platform_id, created_at DESC);

-- 部分索引减少存储空间
CREATE INDEX idx_active_projects ON projects(user_id, created_at) 
WHERE is_active = TRUE;

-- 表达式索引支持特殊查询
CREATE INDEX idx_projects_domain_lower ON projects(LOWER(domain));
```

### 查询优化
```sql
-- 使用物化视图加速复杂查询
CREATE MATERIALIZED VIEW project_stats AS
SELECT 
    p.id as project_id,
    p.name,
    COUNT(mc.id) as total_checks,
    COUNT(CASE WHEN mc.mentioned THEN 1 END) as mentioned_count,
    AVG(gs.total_score) as avg_score,
    MAX(mc.created_at) as last_check_date
FROM projects p
LEFT JOIN mention_checks mc ON p.id = mc.project_id
LEFT JOIN geo_scores gs ON p.id = gs.project_id
GROUP BY p.id, p.name;

-- 创建刷新索引
CREATE UNIQUE INDEX idx_project_stats_id ON project_stats(project_id);
```

---

## 🔄 数据迁移

### 版本控制
```sql
-- 数据库版本表
CREATE TABLE schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 迁移脚本示例
-- migrations/001_initial_schema.sql
-- migrations/002_add_geo_suggestions.sql
-- migrations/003_add_prompt_templates.sql
```

### 备份策略
```yaml
自动备份:
  频率: 每日凌晨2点
  保留期: 30天
  存储: Supabase自动备份

手动备份:
  重要操作前: 手动创建备份点
  版本发布前: 完整数据导出
  测试环境: 定期同步生产数据
```

---

## 📊 监控与维护

### 性能监控
```sql
-- 慢查询监控
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC;

-- 表大小监控
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 数据清理
```sql
-- 定期清理过期数据
DELETE FROM mention_checks 
WHERE created_at < NOW() - INTERVAL '90 days';

-- 归档历史数据
CREATE TABLE mention_checks_archive AS
SELECT * FROM mention_checks 
WHERE created_at < NOW() - INTERVAL '1 year';
```

---

*最后更新: 2024-05-30*
*数据库版本: v1.0*
