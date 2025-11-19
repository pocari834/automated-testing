<template>
  <div class="api-tests-container">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="测试用例" name="cases">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>API测试用例</span>
              <el-button type="primary" @click="handleCreateCase">
                <el-icon><Plus /></el-icon>
                新建用例
              </el-button>
            </div>
          </template>

          <el-table :data="Array.isArray(cases) ? cases : []" v-loading="casesLoading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="用例名称" />
            <el-table-column prop="method" label="方法" width="100">
              <template #default="{ row }">
                <el-tag :type="getMethodType(row.method)">{{ row.method }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="url" label="URL" show-overflow-tooltip />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEditCase(row)">编辑</el-button>
                <el-button link type="success" @click="handleRunCase(row)">执行</el-button>
                <el-button link type="danger" @click="handleDeleteCase(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="测试套件" name="suites">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>API测试套件</span>
              <el-button type="primary" @click="handleCreateSuite">
                <el-icon><Plus /></el-icon>
                新建套件
              </el-button>
            </div>
          </template>

          <el-table :data="Array.isArray(suites) ? suites : []" v-loading="suitesLoading" stripe>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="套件名称" />
            <el-table-column prop="case_ids" label="用例数量" width="120">
              <template #default="{ row }">
                {{ row.case_ids?.length || 0 }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEditSuite(row)">编辑</el-button>
                <el-button link type="success" @click="handleRunSuite(row)">执行</el-button>
                <el-button link type="danger" @click="handleDeleteSuite(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 用例对话框 -->
    <el-dialog
      v-model="caseDialogVisible"
      :title="caseDialogTitle"
      width="800px"
    >
      <el-form ref="caseFormRef" :model="caseForm" :rules="caseRules" label-width="100px">
        <el-form-item label="项目" prop="project_id">
          <el-select v-model="caseForm.project_id" placeholder="请选择项目" style="width: 100%">
            <el-option
              v-for="project in (Array.isArray(projects) ? projects : [])"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="caseForm.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="请求方法" prop="method">
          <el-select v-model="caseForm.method" placeholder="请选择方法">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="URL" prop="url">
          <el-input v-model="caseForm.url" placeholder="请输入URL" />
        </el-form-item>
        <el-form-item label="Headers">
          <el-input
            v-model="caseForm.headersText"
            type="textarea"
            :rows="3"
            placeholder='JSON格式，如: {"Content-Type": "application/json"}'
          />
        </el-form-item>
        <el-form-item label="Params">
          <el-input
            v-model="caseForm.paramsText"
            type="textarea"
            :rows="3"
            placeholder='JSON格式，如: {"key": "value"}'
          />
        </el-form-item>
        <el-form-item label="Body">
          <el-input
            v-model="caseForm.bodyText"
            type="textarea"
            :rows="4"
            placeholder='JSON格式，如: {"username": "test", "password": "123456"}'
          />
        </el-form-item>
        <el-form-item label="断言">
          <el-input
            v-model="caseForm.assertionsText"
            type="textarea"
            :rows="4"
            placeholder='JSON格式，如: {"status_code": 200, "response_json": {"code": 0}}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="caseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitCase">确定</el-button>
      </template>
    </el-dialog>

    <!-- 套件对话框 -->
    <el-dialog
      v-model="suiteDialogVisible"
      :title="suiteDialogTitle"
      width="600px"
    >
      <el-form ref="suiteFormRef" :model="suiteForm" :rules="suiteRules" label-width="100px">
        <el-form-item label="项目" prop="project_id">
          <el-select v-model="suiteForm.project_id" placeholder="请选择项目" style="width: 100%">
            <el-option
              v-for="project in (Array.isArray(projects) ? projects : [])"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="套件名称" prop="name">
          <el-input v-model="suiteForm.name" placeholder="请输入套件名称" />
        </el-form-item>
        <el-form-item label="测试用例">
          <el-select
            v-model="suiteForm.case_ids"
            multiple
            placeholder="请选择测试用例"
            style="width: 100%"
          >
            <el-option
              v-for="caseItem in (Array.isArray(cases) ? cases : [])"
              :key="caseItem.id"
              :label="caseItem.name"
              :value="caseItem.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="suiteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitSuite">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { apiTestApi } from '@/api/apiTests'
import { projectApi } from '@/api/projects'
import { taskApi } from '@/api/tasks'

const activeTab = ref('cases')
const cases = ref([])
const suites = ref([])
const casesLoading = ref(false)
const suitesLoading = ref(false)
const projects = ref([])

const caseDialogVisible = ref(false)
const caseDialogTitle = ref('新建用例')
const caseFormRef = ref()
const caseForm = ref({
  id: null,
  project_id: null,
  name: '',
  method: 'GET',
  url: '',
  headersText: '',
  paramsText: '',
  bodyText: '',
  assertionsText: ''
})

const suiteDialogVisible = ref(false)
const suiteDialogTitle = ref('新建套件')
const suiteFormRef = ref()
const suiteForm = ref({
  id: null,
  project_id: null,
  name: '',
  case_ids: []
})

const caseRules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  method: [{ required: true, message: '请选择请求方法', trigger: 'change' }],
  url: [{ required: true, message: '请输入URL', trigger: 'blur' }]
}

const suiteRules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  name: [{ required: true, message: '请输入套件名称', trigger: 'blur' }]
}

const loadProjects = async () => {
  try {
    const data = await projectApi.getProjects({ limit: 1000 })
    // 确保 data 是数组
    projects.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载项目失败', error)
    projects.value = []
  }
}

const loadCases = async () => {
  casesLoading.value = true
  try {
    const data = await apiTestApi.getCases()
    // 确保 data 是数组
    cases.value = Array.isArray(data) ? data : []
  } catch (error) {
    ElMessage.error('加载用例失败')
    cases.value = []
  } finally {
    casesLoading.value = false
  }
}

const loadSuites = async () => {
  suitesLoading.value = true
  try {
    const data = await apiTestApi.getSuites()
    // 确保 data 是数组
    suites.value = Array.isArray(data) ? data : []
  } catch (error) {
    ElMessage.error('加载套件失败')
    suites.value = []
  } finally {
    suitesLoading.value = false
  }
}

const handleTabChange = (tab) => {
  if (tab === 'cases') {
    loadCases()
  } else {
    loadSuites()
  }
}

const handleCreateCase = () => {
  caseDialogTitle.value = '新建用例'
  caseForm.value = {
    id: null,
    project_id: null,
    name: '',
    method: 'GET',
    url: '',
    headersText: '',
    paramsText: '',
    bodyText: '',
    assertionsText: ''
  }
  caseDialogVisible.value = true
}

const handleEditCase = (row) => {
  caseDialogTitle.value = '编辑用例'
  caseForm.value = {
    id: row.id,
    project_id: row.project_id,
    name: row.name,
    method: row.method,
    url: row.url,
    headersText: row.headers ? JSON.stringify(row.headers, null, 2) : '',
    paramsText: row.params ? JSON.stringify(row.params, null, 2) : '',
    bodyText: row.body ? JSON.stringify(row.body, null, 2) : '',
    assertionsText: row.assertions ? JSON.stringify(row.assertions, null, 2) : ''
  }
  caseDialogVisible.value = true
}

const handleDeleteCase = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用例吗？', '提示', { type: 'warning' })
    await apiTestApi.deleteCase(row.id)
    ElMessage.success('删除成功')
    loadCases()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleRunCase = async (row) => {
  try {
    const result = await apiTestApi.runCase(row.id)
    ElMessage.success(`任务已提交，任务ID: ${result.task_id}`)
    // 可以在这里轮询任务状态
    pollTaskStatus(result.task_id)
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

const handleCreateSuite = () => {
  suiteDialogTitle.value = '新建套件'
  suiteForm.value = {
    id: null,
    project_id: null,
    name: '',
    case_ids: []
  }
  suiteDialogVisible.value = true
}

const handleEditSuite = (row) => {
  suiteDialogTitle.value = '编辑套件'
  suiteForm.value = {
    id: row.id,
    project_id: row.project_id,
    name: row.name,
    case_ids: row.case_ids || []
  }
  suiteDialogVisible.value = true
}

const handleDeleteSuite = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该套件吗？', '提示', { type: 'warning' })
    await apiTestApi.deleteSuite(row.id)
    ElMessage.success('删除成功')
    loadSuites()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleRunSuite = async (row) => {
  try {
    const result = await apiTestApi.runSuite(row.id)
    ElMessage.success(`任务已提交，任务ID: ${result.task_id}`)
    pollTaskStatus(result.task_id)
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

const pollTaskStatus = async (taskId) => {
  const maxAttempts = 60
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
  }, 2000)
}

const handleSubmitCase = async () => {
  if (!caseFormRef.value) return
  await caseFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const data = {
          project_id: caseForm.value.project_id,
          name: caseForm.value.name,
          method: caseForm.value.method,
          url: caseForm.value.url,
          headers: parseJSON(caseForm.value.headersText),
          params: parseJSON(caseForm.value.paramsText),
          body: parseJSON(caseForm.value.bodyText),
          assertions: parseJSON(caseForm.value.assertionsText)
        }
        if (caseForm.value.id) {
          await apiTestApi.updateCase(caseForm.value.id, data)
          ElMessage.success('更新成功')
        } else {
          await apiTestApi.createCase(data)
          ElMessage.success('创建成功')
        }
        caseDialogVisible.value = false
        loadCases()
      } catch (error) {
        ElMessage.error(caseForm.value.id ? '更新失败' : '创建失败')
      }
    }
  })
}

const handleSubmitSuite = async () => {
  if (!suiteFormRef.value) return
  await suiteFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const data = {
          project_id: suiteForm.value.project_id,
          name: suiteForm.value.name,
          case_ids: suiteForm.value.case_ids
        }
        if (suiteForm.value.id) {
          await apiTestApi.updateSuite(suiteForm.value.id, data)
          ElMessage.success('更新成功')
        } else {
          await apiTestApi.createSuite(data)
          ElMessage.success('创建成功')
        }
        suiteDialogVisible.value = false
        loadSuites()
      } catch (error) {
        ElMessage.error(suiteForm.value.id ? '更新失败' : '创建失败')
      }
    }
  })
}

const parseJSON = (str) => {
  if (!str || !str.trim()) return null
  try {
    return JSON.parse(str)
  } catch {
    return null
  }
}

const getMethodType = (method) => {
  const types = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger'
  }
  return types[method] || 'info'
}

onMounted(() => {
  loadProjects()
  loadCases()
})
</script>

<style scoped>
.api-tests-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

