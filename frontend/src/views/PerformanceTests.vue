<template>
  <div class="performance-tests-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>性能测试</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建测试
          </el-button>
        </div>
      </template>

      <el-table :data="Array.isArray(tests) ? tests : []" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="测试名称" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="jmx_file_path" label="JMX文件" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.jmx_file_path ? '已上传' : '未上传' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="warning" @click="handleUpload(row)">上传JMX</el-button>
            <el-button
              link
              type="success"
              :disabled="!row.jmx_file_path || row.status === 'running'"
              @click="handleRun(row)"
            >
              执行
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
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
        <el-form-item label="测试名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入测试名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 上传文件对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传JMX文件"
      width="500px"
    >
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        accept=".jmx"
      >
        <template #trigger>
          <el-button type="primary">选择文件</el-button>
        </template>
        <template #tip>
          <div class="el-upload__tip">只能上传JMX文件</div>
        </template>
      </el-upload>
      <div v-if="selectedFile" style="margin-top: 10px">
        已选择: {{ selectedFile.name }}
      </div>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUploadSubmit" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { performanceTestApi } from '@/api/performanceTests'
import { projectApi } from '@/api/projects'
import { taskApi } from '@/api/tasks'

const loading = ref(false)
const tests = ref([])
const projects = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('新建测试')
const formRef = ref()
const form = ref({
  id: null,
  project_id: null,
  name: ''
})

const uploadDialogVisible = ref(false)
const uploadRef = ref()
const selectedFile = ref(null)
const uploading = ref(false)
const currentTestId = ref(null)

const rules = {
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  name: [{ required: true, message: '请输入测试名称', trigger: 'blur' }]
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

const loadTests = async () => {
  loading.value = true
  try {
    const data = await performanceTestApi.getTests()
    tests.value = Array.isArray(data) ? data : []
  } catch (error) {
    ElMessage.error('加载测试列表失败')
    tests.value = []
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  dialogTitle.value = '新建测试'
  form.value = {
    id: null,
    project_id: null,
    name: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑测试'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该测试吗？', '提示', { type: 'warning' })
    await performanceTestApi.deleteTest(row.id)
    ElMessage.success('删除成功')
    loadTests()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleUpload = (row) => {
  currentTestId.value = row.id
  selectedFile.value = null
  uploadDialogVisible.value = true
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleUploadSubmit = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  uploading.value = true
  try {
    await performanceTestApi.uploadJmx(currentTestId.value, selectedFile.value)
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    loadTests()
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const handleRun = async (row) => {
  try {
    const result = await performanceTestApi.runTest(row.id)
    ElMessage.success(`任务已提交，任务ID: ${result.task_id}`)
    row.status = 'running'
    pollTaskStatus(result.task_id, row)
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

const pollTaskStatus = async (taskId, testRow) => {
  const maxAttempts = 180 // 性能测试可能需要更长时间
  let attempts = 0
  const interval = setInterval(async () => {
    attempts++
    try {
      const status = await taskApi.getTaskStatus(taskId)
      if (status.status === 'SUCCESS' || status.status === 'FAILURE') {
        clearInterval(interval)
        testRow.status = status.status === 'SUCCESS' ? 'completed' : 'failed'
        if (status.status === 'SUCCESS') {
          ElMessage.success('性能测试执行完成')
        } else {
          ElMessage.error(`性能测试执行失败: ${status.error || '未知错误'}`)
        }
        loadTests()
      }
      if (attempts >= maxAttempts) {
        clearInterval(interval)
        testRow.status = 'failed'
        ElMessage.warning('任务执行超时')
        loadTests()
      }
    } catch (error) {
      clearInterval(interval)
    }
  }, 5000)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.value.id) {
          await performanceTestApi.updateTest(form.value.id, form.value)
          ElMessage.success('更新成功')
        } else {
          await performanceTestApi.createTest(form.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadTests()
      } catch (error) {
        ElMessage.error(form.value.id ? '更新失败' : '创建失败')
      }
    }
  })
}

const getStatusType = (status) => {
  const types = {
    ready: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    ready: '就绪',
    running: '运行中',
    completed: '完成',
    failed: '失败'
  }
  return texts[status] || status
}

onMounted(() => {
  loadProjects()
  loadTests()
})
</script>

<style scoped>
.performance-tests-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

