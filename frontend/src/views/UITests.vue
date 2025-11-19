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
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Document, View } from '@element-plus/icons-vue'
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

const handleRun = async (row) => {
  try {
    console.log('开始执行 UI 测试用例:', row.id)
    const result = await uiTestApi.runCase(row.id)
    console.log('执行结果:', result)
    if (result && result.task_id) {
    ElMessage.success(`任务已提交，任务ID: ${result.task_id}`)
    pollTaskStatus(result.task_id)
    } else {
      ElMessage.warning('任务提交成功，但未返回任务ID')
    }
  } catch (error) {
    console.error('执行 UI 测试失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '执行失败'
    ElMessage.error(`执行失败: ${errorMsg}`)
  }
}

const pollTaskStatus = async (taskId) => {
  const maxAttempts = 120 // UI测试可能需要更长时间
  let attempts = 0
  const interval = setInterval(async () => {
    attempts++
    try {
      const status = await taskApi.getTaskStatus(taskId)
      if (status.status === 'SUCCESS' || status.status === 'FAILURE') {
        clearInterval(interval)
        if (status.status === 'SUCCESS') {
          ElMessage.success('测试执行完成')
        } else {
          ElMessage.error(`测试执行失败: ${status.error || '未知错误'}`)
        }
      }
      if (attempts >= maxAttempts) {
        clearInterval(interval)
        ElMessage.warning('任务执行超时')
      }
    } catch (error) {
      clearInterval(interval)
    }
  }, 3000)
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

def test_ui_case():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 访问起始网址
        page.goto("${visualConfig.value.startUrl}")
        page.wait_for_load_state('networkidle')
        
`
  
  visualConfig.value.steps.forEach((step, index) => {
    script += `        # 步骤 ${index + 1}: ${getStepTypeName(step.type)}\n`
    
    switch (step.type) {
      case 'goto':
        const gotoUrl = step.selector || step.value || visualConfig.value.startUrl
        if (gotoUrl) {
          script += `        page.goto("${gotoUrl}")\n`
          script += `        page.wait_for_load_state('networkidle')\n`
        }
        break
      case 'click':
        if (step.selector) {
          script += `        page.click("${step.selector}")\n`
          script += `        page.wait_for_load_state('networkidle')\n`
        }
        break
      case 'fill':
        if (step.selector && step.value) {
          script += `        page.fill("${step.selector}", "${step.value}")\n`
        }
        break
      case 'wait':
        if (step.selector) {
          script += `        page.wait_for_selector("${step.selector}", timeout=10000)\n`
        }
        break
      case 'screenshot':
        const screenshotName = step.value || `screenshot_${index + 1}`
        script += `        page.screenshot(path="${screenshotName}.png")\n`
        break
      case 'sleep':
        const seconds = step.value || 1
        script += `        time.sleep(${seconds})\n`
        break
      case 'assert_title':
        if (step.value) {
          script += `        assert page.title() == "${step.value}", f"标题不匹配，期望: ${step.value}, 实际: {page.title()}"\n`
        }
        break
      case 'assert_text':
        if (step.selector && step.value) {
          script += `        text = page.locator("${step.selector}").text_content()\n`
          script += `        assert "${step.value}" in text, f"文本不匹配，期望包含: ${step.value}, 实际: {text}"\n`
        }
        break
      case 'get_text':
        if (step.selector) {
          script += `        text = page.locator("${step.selector}").text_content()\n`
          script += `        print(f"获取的文本: {text}")\n`
        }
        break
    }
    script += '\n'
  })
  
  script += `        browser.close()

if __name__ == "__main__":
    test_ui_case()
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

