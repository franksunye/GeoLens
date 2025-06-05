# 🗄️ GeoLens - 数据库设计文档

## 📋 数据库概述

GeoLens 使用 PostgreSQL 作为主数据库，通过 Supabase 提供的托管服务。数据库专注于引用检测相关数据存储，包括用户项目、检测记录、引用分析结果、Prompt模板和历史统计等。

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
│                        引用检测与分析                           │
├─────────────────────────────────────────────────────────────┤
│  mention_checks     │  mention_results │  prompt_templates  │
│  (引用检测表)        │  (检测结果表)     │  (Prompt模板表)     │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                        系统与配置                              │
├─────────────────────────────────────────────────────────────┤
│  ai_providers       │  analysis_templates │  system_configs │
│  (AI服务商表)        │  (分析模板表)        │  (系统配置表)     │
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

### 3. AI服务商表 (ai_providers)
```sql
CREATE TABLE ai_providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL, -- 'openai', 'doubao', 'deepseek'
    display_name VARCHAR(100) NOT NULL,
    api_endpoint TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit_per_minute INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 初始数据
INSERT INTO ai_providers (name, display_name, api_endpoint) VALUES
('openai', 'OpenAI GPT-4', 'https://api.openai.com/v1/chat/completions'),
('doubao', '豆包AI', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'),
('deepseek', 'DeepSeek', 'https://api.deepseek.com/v1/chat/completions');
```

### 4. 引用检测表 (mention_checks)
```sql
CREATE TABLE mention_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    brands JSONB NOT NULL, -- 要检测的品牌列表
    models JSONB NOT NULL, -- 使用的AI模型列表

    -- 检测状态
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed

    -- 统计结果
    total_mentions INTEGER DEFAULT 0,
    mention_rate DECIMAL(5,4), -- 0.0000-1.0000
    avg_confidence DECIMAL(5,4),

    -- 时间记录
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_mention_checks_project ON mention_checks(project_id, created_at DESC);
CREATE INDEX idx_mention_checks_status ON mention_checks(status);
```

### 5. 检测结果表 (mention_results)
```sql
CREATE TABLE mention_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    check_id UUID NOT NULL REFERENCES mention_checks(id) ON DELETE CASCADE,
    model VARCHAR(50) NOT NULL, -- 'doubao', 'deepseek', 'chatgpt'
    brand VARCHAR(100) NOT NULL,

    -- 检测结果
    mentioned BOOLEAN DEFAULT FALSE,
    confidence_score DECIMAL(5,4), -- 0.0000-1.0000
    context_snippet TEXT,
    position INTEGER, -- 在回答中的位置

    -- AI回答原文
    response_text TEXT,
    response_length INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_mention_results_check ON mention_results(check_id);
CREATE INDEX idx_mention_results_brand ON mention_results(brand, mentioned);
CREATE INDEX idx_mention_results_model ON mention_results(model);
```

### 6. Prompt模板表 (prompt_templates)
```sql
CREATE TABLE prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'productivity', 'comparison', 'recommendation'
    template TEXT NOT NULL,
    variables JSONB, -- 模板变量定义
    description TEXT,

    -- 使用统计
    usage_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_prompt_templates_user ON prompt_templates(user_id);
CREATE INDEX idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX idx_prompt_templates_public ON prompt_templates(is_public, usage_count DESC);
```

### 7. 引用统计表 (mention_analytics)
```sql
CREATE TABLE mention_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(50) NOT NULL,
    date DATE NOT NULL,

    -- 统计数据
    total_checks INTEGER DEFAULT 0,
    total_mentions INTEGER DEFAULT 0,
    mention_rate DECIMAL(5,4), -- 0.0000-1.0000
    avg_confidence DECIMAL(5,4),

    -- 上下文分析
    top_contexts JSONB, -- 最常见的提及上下文
    position_stats JSONB, -- 位置统计 (第1位、第2位等)

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_mention_analytics_project ON mention_analytics(project_id, date DESC);
CREATE INDEX idx_mention_analytics_brand ON mention_analytics(brand, date DESC);
CREATE INDEX idx_mention_analytics_model ON mention_analytics(model);
CREATE UNIQUE INDEX idx_mention_analytics_unique ON mention_analytics(project_id, brand, model, date);
```

---

## 📝 初始数据
### AI服务商初始数据
```sql
INSERT INTO ai_providers (name, display_name, api_endpoint) VALUES
('doubao', '豆包AI', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions'),
('deepseek', 'DeepSeek', 'https://api.deepseek.com/v1/chat/completions'),
('openai', 'OpenAI GPT-4', 'https://api.openai.com/v1/chat/completions');
```

### Prompt模板初始数据
```sql
INSERT INTO prompt_templates (name, category, template, variables, description) VALUES
('协作工具推荐', 'productivity', '推荐几个适合{team_size}人团队使用的{tool_type}工具',
 '{"team_size": "string", "tool_type": "string"}', '用于推荐团队协作工具的模板'),
('项目管理软件', 'productivity', '有哪些好用的项目管理软件适合{industry}行业？',
 '{"industry": "string"}', '针对特定行业推荐项目管理软件'),
('知识管理工具', 'productivity', '推荐几个适合{use_case}的知识管理工具',
 '{"use_case": "string"}', '根据使用场景推荐知识管理工具'),
('竞品对比', 'comparison', '对比{brand1}和{brand2}这两个{category}工具的优缺点',
 '{"brand1": "string", "brand2": "string", "category": "string"}', '用于竞品对比分析');
```

---

## 🔐 安全策略

### Row Level Security (RLS)
```sql
-- 启用RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE mention_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE mention_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE mention_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_templates ENABLE ROW LEVEL SECURITY;

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

*最后更新: 2024-06-03*
*数据库版本: v2.0 - 引用检测专注版本*
