<template>
  <div class="ui-tests-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>UI测试用例</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建用例
          </el-button>
        </div>
      </template>

      <el-table :data="Array.isArray(cases) ? cases : []" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" />
        <el-table-column prop="project_id" label="项目ID" width="100" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="success" @click="handleRun(row)">执行</el-button>
            <el-button link type="info" @click="handleView(row)">查看</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="项目" prop="project_id">
          <el-select v-model="form.project_id" placeholder="请选择项目" style="width: 100%">
            <el-option
              v-for="project in (Array.isArray(projects) ? projects : [])"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入用例名称" />
        </el-form-item>
        
        <!-- 模式切换 -->
        <el-form-item label="编辑模式">
          <el-radio-group v-model="editMode">
            <el-radio label="visual">可视化模式</el-radio>
            <el-radio label="code">代码模式</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 可视化模式 -->
        <div v-if="editMode === 'visual'">
          <el-form-item label="起始网址">
            <el-input 
              v-model="visualConfig.startUrl" 
              placeholder="例如: https://example.com"
              style="width: 100%"
            >
              <template #prepend>URL</template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="操作步骤">
            <div class="steps-container">
              <div 
                v-for="(step, index) in visualConfig.steps" 
                :key="index"
                class="step-item"
              >
                <el-card shadow="hover" style="margin-bottom: 10px">
                  <template #header>
                    <div style="display: flex; justify-content: space-between; align-items: center">
                      <span>步骤 {{ index + 1 }}: {{ getStepTypeName(step.type) }}</span>
                      <div>
                        <el-button 
                          link 
                          type="danger" 
                          size="small"
                          @click="removeStep(index)"
                          :disabled="visualConfig.steps.length <= 1"
                        >
                          删除
                        </el-button>
                        <el-button 
                          link 
                          type="primary" 
                          size="small"
                          @click="moveStepUp(index)"
                          :disabled="index === 0"
                        >
                          上移
                        </el-button>
                        <el-button 
                          link 
                          type="primary" 
                          size="small"
                          @click="moveStepDown(index)"
                          :disabled="index === visualConfig.steps.length - 1"
                        >
                          下移
                        </el-button>
                      </div>
                    </div>
                  </template>
                  
                  <el-form :model="step" label-width="80px" size="small">
                    <el-form-item label="操作类型">
                      <el-select v-model="step.type" style="width: 100%">
                        <el-option label="访问网址" value="goto" />
                        <el-option label="点击元素" value="click" />
                        <el-option label="输入文本" value="fill" />
                        <el-option label="等待元素" value="wait" />
                        <el-option label="截图" value="screenshot" />
                        <el-option label="等待时间" value="sleep" />
                        <el-option label="断言标题" value="assert_title" />
                        <el-option label="断言文本" value="assert_text" />
                        <el-option label="获取文本" value="get_text" />
                      </el-select>
                    </el-form-item>
                    
                    <el-form-item 
                      v-if="step.type === 'goto'"
                      label="网址"
                    >
                      <el-input 
                        v-model="step.selector" 
                        placeholder="例如: https://example.com"
                      />
                    </el-form-item>
                    
                    <el-form-item 
                      v-if="step.type === 'click' || step.type === 'wait' || step.type === 'assert_text' || step.type === 'get_text'"
                      label="选择器"
                    >
                      <el-input 
                        v-model="step.selector" 
                        placeholder="CSS选择器，如: #id, .class, button"
                      />
                    </el-form-item>
                    
                    <el-form-item 
                      v-if="step.type === 'fill'"
                      label="选择器"
                    >
                      <el-input 
                        v-model="step.selector" 
                        placeholder="输入框选择器，如: input[name='username']"
                      />
                    </el-form-item>
                    
                    <el-form-item 
                      v-if="step.type === 'fill'"
                      label="输入内容"
                    >
                      <el-input 
                        v-model="step.value" 
                        placeholder="要输入的文本"
                      />
                    </el-form-item>
                    
                    <el-form-item 
                      v-if="step.type === 'sleep'"
                      label="等待时间(秒)"
                    >
                      <el-input-number 
                        v-model="step.value" 
                        :min="0.1" 
                        :max="60" 
                        :step="0.1"
                        style="width: 100%"
                      />
                    </el-form-item>
                    
                    <el-form-item 
                      v-if="step.type === 'assert_title'"
                      label="期望标题"
                    >
                      <el-input 
                        v-model="step.value" 
                        placeholder="期望的页面标题"
                      />
                    </el-form-item>
                    
                    <el-form-item 
                      v-if="step.type === 'assert_text'"
                      label="期望文本"
                    >
                      <el-input 
                        v-model="step.value" 
                        placeholder="期望的文本内容"
                      />
                    </el-form-item>
                    
                    <el-form-item 
                      v-if="step.type === 'screenshot'"
                      label="截图名称"
                    >
                      <el-input 
                        v-model="step.value" 
                        placeholder="截图文件名（可选）"
                      />
                    </el-form-item>
                  </el-form>
                </el-card>
              </div>
              
              <el-button 
                type="primary" 
                plain 
                @click="addStep"
                style="width: 100%"
              >
                <el-icon><Plus /></el-icon>
                添加步骤
              </el-button>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button type="success" @click="generateScript">
              <el-icon><Document /></el-icon>
              生成脚本
            </el-button>
            <el-button type="info" @click="previewScript">
              <el-icon><View /></el-icon>
              预览脚本
            </el-button>
          </el-form-item>
        </div>

        <!-- 代码模式 -->
        <el-form-item v-if="editMode === 'code'" label="测试脚本" prop="script">
          <el-input
            v-model="form.script"
            type="textarea"
            :rows="15"
            placeholder="请输入Playwright Python测试脚本"
          />
        </el-form-item>
        
        <el-form-item v-if="editMode === 'code'">
          <el-alert
            title="脚本示例"
            type="info"
            :closable="false"
            style="margin-top: 10px"
          >
            <template #default>
              <pre style="margin: 0; font-size: 12px;">from playwright.sync_api import sync_playwright

def test_example():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com")
        assert page.title() == "Example Domain"
        browser.close()</pre>
            </template>
          </el-alert>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看脚本对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="查看脚本"
      width="800px"
    >
      <el-input
        v-model="viewScript"
        type="textarea"
        :rows="20"
        readonly
      />
    </el-dialog>

    <!-- 预览脚本对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="预览生成的脚本"
      width="900px"
    >
      <el-input
        v-model="previewScriptContent"
        type="textarea"
        :rows="25"
        readonly
        style="font-family: 'Courier New', monospace;"
      />
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="() => { form.script = previewScriptContent; previewDialogVisible = false }">
          使用此脚本
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行进度对话框 -->
    <el-dialog
      v-model="progressDialogVisible"
      title="测试执行进度"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="!isExecuting"
    >
      <div v-if="taskStatus">
        <el-progress
          :percentage="taskStatus.progress || 0"
          :status="getProgressStatus()"
          :stroke-width="20"
        />
        <div style="margin-top: 20px;">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="当前步骤">
              {{ taskStatus.current_step || '等待开始...' }}
            </el-descriptions-item>
            <el-descriptions-item label="状态信息">
              <span v-if="taskStatus.status === 'PENDING' && !taskStatus.status_message" style="color: #E6A23C;">
                等待 Celery Worker 处理...（如果长时间无响应，请检查 Worker 是否运行）
              </span>
              <span v-else>
                {{ taskStatus.status_message || taskStatus.status || '未知' }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="执行状态">
              <el-tag :type="getStatusTag(taskStatus.status)">
                {{ getStatusText(taskStatus.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="错误信息" v-if="taskStatus.error">
              <pre style="white-space: pre-wrap; word-wrap: break-word; color: #F56C6C; margin: 0;">{{ taskStatus.error }}</pre>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <div v-else style="text-align: center; padding: 20px;">
        <el-icon class="is-loading" style="font-size: 24px;"><Loading /></el-icon>
        <p>正在启动测试...</p>
      </div>
      <template #footer>
        <el-button
          v-if="!isExecuting"
          type="primary"
          @click="progressDialogVisible = false"
        >
          关闭
        </el-button>
        <el-button
          v-else
          type="danger"
          @click="handleCancelExecution"
        >
          取消执行
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document, View, Loading } from '@element-plus/icons-vue'
import { uiTestApi } from '@/api/uiTests'
import { projectApi } from '@/api/projects'
import { taskApi } from '@/api/tasks'

const loading = ref(false)
const cases = ref([])
const projects = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('新建用例')
const formRef = ref()
const form = ref({
  id: null,
  project_id: null,
  name: '',
  script: ''
})

const viewDialogVisible = ref(false)
const viewScript = ref('')

// 可视化构建器相关
const editMode = ref('visual') // 'visual' 或 'code'
const visualConfig = ref({
  startUrl: '',
  steps: [
    { type: 'goto', selector: '', value: '' }
  ]
})

const previewDialogVisible = ref(false)
const previewScriptContent = ref('')

const rules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  script: [
    { 
      required: true, 
      message: '请输入测试脚本或使用可视化模式生成', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (editMode.value === 'code' && !value) {
          callback(new Error('请输入测试脚本'))
        } else if (editMode.value === 'visual' && !visualConfig.value.startUrl) {
          callback(new Error('请先输入起始网址并生成脚本'))
        } else {
          callback()
        }
      }
    }
  ]
}

const loadProjects = async () => {
  try {
    const data = await projectApi.getProjects({ limit: 1000 })
    projects.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载项目失败', error)
    projects.value = []
  }
}

const loadCases = async () => {
  loading.value = true
  try {
    const data = await uiTestApi.getCases()
    cases.value = Array.isArray(data) ? data : []
  } catch (error) {
    ElMessage.error('加载用例失败')
    cases.value = []
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  dialogTitle.value = '新建用例'
  editMode.value = 'visual'
  form.value = {
    id: null,
    project_id: null,
    name: '',
    script: ''
  }
  // 重置可视化配置
  visualConfig.value = {
    startUrl: '',
    steps: [
      { type: 'click', selector: '', value: '' }
    ]
  }
  // 确保项目列表已加载
  if (projects.value.length === 0) {
    loadProjects()
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑用例'
  form.value = { ...row }
  // 默认使用代码模式编辑已有用例
  editMode.value = 'code'
  visualConfig.value = {
    startUrl: '',
    steps: [{ type: 'goto', selector: '', value: '' }]
  }
  dialogVisible.value = true
}

const handleView = (row) => {
  viewScript.value = row.script
  viewDialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用例吗？', '提示', { type: 'warning' })
    await uiTestApi.deleteCase(row.id)
    ElMessage.success('删除成功')
    loadCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const progressDialogVisible = ref(false)
const taskStatus = ref(null)
const isExecuting = ref(false)
let pollInterval = null

const handleRun = async (row) => {
  try {
    console.log('开始执行 UI 测试用例:', row.id)
    
    // 打开进度对话框
    progressDialogVisible.value = true
    taskStatus.value = null
    isExecuting.value = true
    
    const result = await uiTestApi.runCase(row.id)
    console.log('执行结果:', result)
    if (result && result.task_id) {
    ElMessage.success(`任务已提交，任务ID: ${result.task_id}`)
    pollTaskStatus(result.task_id)
    } else {
      ElMessage.warning('任务提交成功，但未返回任务ID')
      isExecuting.value = false
      progressDialogVisible.value = false
    }
  } catch (error) {
    console.error('执行 UI 测试失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '执行失败'
    ElMessage.error(`执行失败: ${errorMsg}`)
    isExecuting.value = false
    progressDialogVisible.value = false
  }
}

const handleCancelExecution = () => {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
  isExecuting.value = false
  ElMessage.warning('已取消执行监控，但任务可能仍在后台运行')
}

const pollTaskStatus = async (taskId) => {
  const maxAttempts = 300 // UI测试可能需要更长时间（5分钟 / 1秒）
  let attempts = 0
  
  pollInterval = setInterval(async () => {
    attempts++
    try {
      const status = await taskApi.getTaskStatus(taskId)
      taskStatus.value = status
      
      // 如果状态一直是 PENDING，显示提示信息
      if (status.status === 'PENDING' && attempts > 5) {
        // 超过5秒还是 PENDING，可能是 Worker 未运行
        taskStatus.value = {
          ...status,
          status_message: status.status_message || '任务等待中，请确保 Celery Worker 正在运行...',
          progress: 0
        }
      }
      
      if (status.status === 'SUCCESS' || status.status === 'FAILURE') {
        clearInterval(pollInterval)
        pollInterval = null
        isExecuting.value = false
        
        // 更新进度到100%
        if (status.status === 'SUCCESS') {
          taskStatus.value = {
            ...status,
            progress: 100,
            current_step: '测试完成',
            status_message: '所有步骤执行成功'
          }
          ElMessage.success('测试执行完成')
        } else {
          taskStatus.value = {
            ...status,
            progress: status.progress || 0,
            current_step: '测试失败',
            status_message: status.error || '未知错误'
          }
          ElMessage.error(`测试执行失败: ${status.error || '未知错误'}`)
        }
        
        // 刷新用例列表
        loadCases()
      }
      if (attempts >= maxAttempts) {
        clearInterval(pollInterval)
        pollInterval = null
        isExecuting.value = false
        ElMessage.warning('任务执行超时')
      }
    } catch (error) {
      console.error('查询任务状态失败:', error)
      clearInterval(pollInterval)
      pollInterval = null
      isExecuting.value = false
    }
  }, 1000) // 每1秒查询一次（更频繁的更新）
}

const getProgressStatus = () => {
  if (!taskStatus.value) return null
  if (taskStatus.value.status === 'FAILURE') return 'exception'
  if (taskStatus.value.status === 'SUCCESS') return 'success'
  return null
}

const getStatusTag = (status) => {
  const tags = {
    'PENDING': 'info',
    'STARTED': 'warning',
    'PROGRESS': 'primary',
    'SUCCESS': 'success',
    'FAILURE': 'danger'
  }
  return tags[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'PENDING': '等待中',
    'STARTED': '已开始',
    'PROGRESS': '执行中',
    'SUCCESS': '成功',
    'FAILURE': '失败'
  }
  return texts[status] || status
}

// 可视化构建器函数
const getStepTypeName = (type) => {
  const names = {
    'goto': '访问网址',
    'click': '点击元素',
    'fill': '输入文本',
    'wait': '等待元素',
    'screenshot': '截图',
    'sleep': '等待时间',
    'assert_title': '断言标题',
    'assert_text': '断言文本',
    'get_text': '获取文本'
  }
  return names[type] || type
}

const addStep = () => {
  visualConfig.value.steps.push({
    type: 'click',
    selector: '',
    value: ''
  })
}

const removeStep = (index) => {
  if (visualConfig.value.steps.length > 1) {
    visualConfig.value.steps.splice(index, 1)
  }
}

const moveStepUp = (index) => {
  if (index > 0) {
    const steps = visualConfig.value.steps
    ;[steps[index], steps[index - 1]] = [steps[index - 1], steps[index]]
  }
}

const moveStepDown = (index) => {
  const steps = visualConfig.value.steps
  if (index < steps.length - 1) {
    ;[steps[index], steps[index + 1]] = [steps[index + 1], steps[index]]
  }
}

const generateScript = () => {
  if (!visualConfig.value.startUrl) {
    ElMessage.warning('请先输入起始网址')
    return
  }
  
  let script = `from playwright.sync_api import sync_playwright
import time
import os
import json

# 截图目录
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "./screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 步骤结果列表
step_results = []

def take_screenshot(page, step_index, step_name, comment=""):
    """截图并记录步骤信息"""
    # 输出步骤信息，用于进度检测
    print(f"[STEP {step_index}] {step_name}: {comment}")
    screenshot_name = f"step_{step_index}_{step_name.replace(' ', '_')}.png"
    screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_name)
    page.screenshot(path=screenshot_path)
    step_results.append({
        "step_index": step_index,
        "step_name": step_name,
        "step_type": step_name,
        "success": True,
        "screenshot_path": screenshot_path,
        "comment": comment,
        "timestamp": time.time()
    })
    return screenshot_path

def test_ui_case():
    global step_results
    step_results = []
    
    with sync_playwright() as p:
        # 优化浏览器启动：使用更快的配置
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        # 设置更短的超时时间
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            ignore_https_errors=True
        )
        page = context.new_page()
        
        # 设置全局超时（30秒）
        page.set_default_timeout(30000)
        page.set_default_navigation_timeout(30000)
        
        try:
            print("[INFO] 开始执行测试...")
            # 步骤 0: 访问起始网址（优化：使用 load 而不是 networkidle）
            print(f"[INFO] 正在访问: ${visualConfig.value.startUrl}")
            page.goto("${visualConfig.value.startUrl}", wait_until='load', timeout=30000)
            # 只等待 DOM 加载完成，不等待所有网络请求
            page.wait_for_load_state('domcontentloaded')
            take_screenshot(page, 0, "访问起始网址", "已访问: ${visualConfig.value.startUrl}")
            
`
  
  visualConfig.value.steps.forEach((step, index) => {
    const stepIndex = index + 1
    const stepName = getStepTypeName(step.type)
    script += `            # 步骤 ${stepIndex}: ${stepName}\n`
    
    switch (step.type) {
      case 'goto':
        const gotoUrl = step.selector || step.value || visualConfig.value.startUrl
        if (gotoUrl) {
          script += `            page.goto("${gotoUrl}", wait_until='load', timeout=30000)\n`
          script += `            page.wait_for_load_state('domcontentloaded', timeout=5000)\n`
          script += `            take_screenshot(page, ${stepIndex}, "访问网址", "已访问: ${gotoUrl}")\n`
        }
        break
      case 'click':
        if (step.selector) {
          script += `            page.click("${step.selector}", timeout=10000)\n`
          script += `            # 等待页面可能的变化（缩短等待时间）\n`
          script += `            page.wait_for_timeout(500)\n`
          script += `            take_screenshot(page, ${stepIndex}, "点击元素", "已点击: ${step.selector}")\n`
        }
        break
      case 'fill':
        if (step.selector && step.value) {
          script += `            page.fill("${step.selector}", "${step.value}")\n`
          script += `            take_screenshot(page, ${stepIndex}, "输入文本", "在 ${step.selector} 中输入: ${step.value}")\n`
        }
        break
      case 'wait':
        if (step.selector) {
          script += `            page.wait_for_selector("${step.selector}", timeout=10000, state='visible')\n`
          script += `            take_screenshot(page, ${stepIndex}, "等待元素", "已等待元素出现: ${step.selector}")\n`
        }
        break
      case 'screenshot':
        const screenshotName = step.value || `screenshot_${stepIndex}`
        script += `            screenshot_path = take_screenshot(page, ${stepIndex}, "截图", "手动截图: ${screenshotName}")\n`
        break
      case 'sleep':
        const seconds = step.value || 1
        // 限制 sleep 时间，避免过长等待
        const sleepTime = Math.min(parseFloat(seconds) || 1, 5)
        script += `            page.wait_for_timeout(int(${sleepTime * 1000}))\n`
        script += `            take_screenshot(page, ${stepIndex}, "等待时间", f"等待了 ${sleepTime} 秒")\n`
        break
      case 'assert_title':
        if (step.value) {
          script += `            actual_title = page.title()\n`
          script += `            assert actual_title == "${step.value}", f"标题不匹配，期望: ${step.value}, 实际: {actual_title}"\n`
          script += `            take_screenshot(page, ${stepIndex}, "断言标题", f"标题验证通过: ${step.value}")\n`
        }
        break
      case 'assert_text':
        if (step.selector && step.value) {
          script += `            text = page.locator("${step.selector}").text_content()\n`
          script += `            assert "${step.value}" in text, f"文本不匹配，期望包含: ${step.value}, 实际: {text}"\n`
          script += `            take_screenshot(page, ${stepIndex}, "断言文本", f"文本验证通过，包含: ${step.value}")\n`
        }
        break
      case 'get_text':
        if (step.selector) {
          script += `            text = page.locator("${step.selector}").text_content()\n`
          script += `            print(f"获取的文本: {text}")\n`
          script += `            take_screenshot(page, ${stepIndex}, "获取文本", f"获取到的文本: {text}")\n`
        }
        break
    }
    script += '\n'
  })
  
  script += `            # 最终截图
            final_screenshot = take_screenshot(page, 999, "测试完成", "所有步骤执行完成")
            
            context.close()
            browser.close()
            
            # 返回步骤结果
            return {
                "success": True,
                "steps": step_results,
                "final_screenshot": final_screenshot
            }
        except Exception as e:
            # 错误时也截图
            error_screenshot = take_screenshot(page, -1, "执行错误", f"发生错误: {str(e)}")
            step_results.append({
                "step_index": -1,
                "step_name": "执行错误",
                "step_type": "error",
                "success": False,
                "screenshot_path": error_screenshot,
                "comment": f"错误信息: {str(e)}",
                "timestamp": time.time(),
                "error": str(e)
            })
            browser.close()
            return {
                "success": False,
                "steps": step_results,
                "error": str(e),
                "error_screenshot": error_screenshot
            }

if __name__ == "__main__":
    result = test_ui_case()
    print(json.dumps(result, indent=2, ensure_ascii=False))
`
  
  form.value.script = script
  ElMessage.success('脚本已生成！')
}

const previewScript = () => {
  generateScript()
  previewScriptContent.value = form.value.script
  previewDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  // 如果是可视化模式，先生成脚本
  if (editMode.value === 'visual') {
    if (!visualConfig.value.startUrl) {
      ElMessage.warning('请先输入起始网址')
      return
    }
    generateScript()
  }
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = { ...form.value }
        
        if (form.value.id) {
          await uiTestApi.updateCase(form.value.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await uiTestApi.createCase(submitData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadCases()
      } catch (error) {
        ElMessage.error(form.value.id ? '更新失败' : '创建失败')
      }
    }
  })
}

onMounted(() => {
  loadProjects()
  loadCases()
})
</script>

<style scoped>
.ui-tests-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.steps-container {
  max-height: 500px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #fafafa;
}

.step-item {
  margin-bottom: 10px;
}
</style>

