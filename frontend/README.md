# 测试平台前端

基于 Vue 3 + Element Plus 的测试平台前端应用。

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Element Plus** - Vue 3 UI 组件库
- **Vue Router** - 官方路由管理器
- **Axios** - HTTP 客户端
- **Pinia** - 状态管理
- **Vite** - 构建工具

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口
│   │   ├── index.js
│   │   ├── projects.js
│   │   ├── apiTests.js
│   │   ├── uiTests.js
│   │   ├── performanceTests.js
│   │   ├── reports.js
│   │   └── tasks.js
│   ├── views/            # 页面组件
│   │   ├── Projects.vue
│   │   ├── APITests.vue
│   │   ├── UITests.vue
│   │   ├── PerformanceTests.vue
│   │   └── Reports.vue
│   ├── layout/           # 布局组件
│   │   └── index.vue
│   ├── router/           # 路由配置
│   │   └── index.js
│   ├── App.vue
│   ├── main.js
│   └── style.css
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 安装和运行

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

## 功能特性

### 1. 项目管理
- 项目列表展示
- 创建、编辑、删除项目
- 项目名称搜索

### 2. API 测试管理
- 测试用例管理（CRUD）
- 测试套件管理
- 用例执行（异步）
- 套件批量执行

### 3. UI 测试管理
- UI 测试用例管理
- Playwright 脚本编辑
- 测试执行和结果查看

### 4. 性能测试管理
- 性能测试创建
- JMX 文件上传
- 测试执行和结果查看
- 性能指标展示

### 5. 测试报告
- 报告列表查看
- 报告详情展示
- 按类型筛选
- 通过率统计

## 设计特点

- **蓝白配色方案**: 主色调为蓝色 (#409EFF)，背景为白色
- **侧边栏导航**: 左侧固定导航栏，支持折叠
- **响应式布局**: 适配不同屏幕尺寸
- **Element Plus 组件**: 使用成熟的 UI 组件库
- **异步任务处理**: 支持任务状态轮询和结果展示

## API 配置

前端通过 Vite 代理转发 API 请求到后端：

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

确保后端服务运行在 `http://localhost:8000`

## 注意事项

1. 确保后端 API 服务已启动
2. 确保后端已配置 CORS 允许前端域名访问
3. 任务执行状态会定期轮询，可能需要等待较长时间
4. UI 测试脚本需要符合 Playwright 语法规范

