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

      <el-table :data="cases" v-loading="loading" stripe>
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
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="测试脚本" prop="script">
          <el-input
            v-model="form.script"
            type="textarea"
            :rows="15"
            placeholder="请输入Playwright Python测试脚本"
          />
        </el-form-item>
        <el-form-item>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
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

const rules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  script: [{ required: true, message: '请输入测试脚本', trigger: 'blur' }]
}

const loadProjects = async () => {
  try {
    const data = await projectApi.getProjects({ limit: 1000 })
    projects.value = data
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

const loadCases = async () => {
  loading.value = true
  try {
    const data = await uiTestApi.getCases()
    cases.value = data
  } catch (error) {
    ElMessage.error('加载用例失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  dialogTitle.value = '新建用例'
  form.value = {
    id: null,
    project_id: null,
    name: '',
    script: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑用例'
  form.value = { ...row }
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
    const result = await uiTestApi.runCase(row.id)
    ElMessage.success(`任务已提交，任务ID: ${result.task_id}`)
    pollTaskStatus(result.task_id)
  } catch (error) {
    ElMessage.error('执行失败')
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

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.value.id) {
          await uiTestApi.updateCase(form.value.id, form.value)
          ElMessage.success('更新成功')
        } else {
          await uiTestApi.createCase(form.value)
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
</style>

