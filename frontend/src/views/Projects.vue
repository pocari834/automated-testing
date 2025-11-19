<template>
  <div class="projects-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>项目管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建项目
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchName"
          placeholder="搜索项目名称"
          style="width: 300px"
          clearable
          @clear="loadProjects"
          @keyup.enter="loadProjects"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="loadProjects">搜索</el-button>
      </div>

      <!-- 项目列表 -->
      <el-table
        v-loading="loading"
        :data="Array.isArray(projects) ? projects : []"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadProjects"
          @current-change="loadProjects"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入项目描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { projectApi } from '@/api/projects'

const loading = ref(false)
const projects = ref([])
const searchName = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('新建项目')
const formRef = ref()
const form = ref({
  id: null,
  name: '',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }]
}

const loadProjects = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchName.value) {
      params.name = searchName.value
    }
    const data = await projectApi.getProjects(params)
    // 确保 data 是数组
    if (Array.isArray(data)) {
      projects.value = data
      total.value = data.length
    } else {
      projects.value = []
      total.value = 0
      console.error('返回的数据不是数组:', data)
    }
  } catch (error) {
    ElMessage.error('加载项目列表失败')
    projects.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  dialogTitle.value = '新建项目'
  form.value = { id: null, name: '', description: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑项目'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该项目吗？', '提示', {
      type: 'warning'
    })
    await projectApi.deleteProject(row.id)
    ElMessage.success('删除成功')
    loadProjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.value.id) {
          await projectApi.updateProject(form.value.id, form.value)
          ElMessage.success('更新成功')
        } else {
          await projectApi.createProject(form.value)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadProjects()
      } catch (error) {
        ElMessage.error(form.value.id ? '更新失败' : '创建失败')
      }
    }
  })
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.projects-container {
  height: 100%;
}

.box-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>

