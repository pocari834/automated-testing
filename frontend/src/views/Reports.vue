<template>
  <div class="reports-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>测试报告</span>
          <div>
            <el-select
              v-model="filterType"
              placeholder="筛选类型"
              style="width: 150px; margin-right: 10px"
              clearable
              @change="loadReports"
            >
              <el-option label="API测试" value="api" />
              <el-option label="UI测试" value="ui" />
              <el-option label="性能测试" value="performance" />
            </el-select>
            <el-button @click="loadReports">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="reports" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="报告名称" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)">{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率" width="120">
          <template #default="{ row }">
            <span :style="{ color: row.pass_rate >= 80 ? '#67C23A' : '#F56C6C' }">
              {{ row.pass_rate !== null ? row.pass_rate.toFixed(2) + '%' : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时(秒)" width="120">
          <template #default="{ row }">
            {{ row.duration ? row.duration.toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 报告详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="currentReport?.name"
      width="900px"
    >
      <div v-if="currentReport">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="报告ID">{{ currentReport.id }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ getTypeText(currentReport.type) }}</el-descriptions-item>
          <el-descriptions-item label="通过率">
            <span :style="{ color: currentReport.pass_rate >= 80 ? '#67C23A' : '#F56C6C' }">
              {{ currentReport.pass_rate !== null ? currentReport.pass_rate.toFixed(2) + '%' : '-' }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="耗时">
            {{ currentReport.duration ? currentReport.duration.toFixed(2) + '秒' : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间" :span="2">
            {{ formatDate(currentReport.start_time) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>测试结果</el-divider>

        <!-- API测试结果 -->
        <div v-if="currentReport.type === 'api'">
          <el-card v-if="currentReport.result_data">
            <pre style="white-space: pre-wrap; word-wrap: break-word;">{{ JSON.stringify(currentReport.result_data, null, 2) }}</pre>
          </el-card>
        </div>

        <!-- UI测试结果 -->
        <div v-if="currentReport.type === 'ui'">
          <el-card v-if="currentReport.result_data">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="执行状态">
                <el-tag :type="currentReport.result_data.success ? 'success' : 'danger'">
                  {{ currentReport.result_data.success ? '成功' : '失败' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="耗时">
                {{ currentReport.result_data.duration?.toFixed(2) }}秒
              </el-descriptions-item>
              <el-descriptions-item label="截图路径" v-if="currentReport.result_data.screenshot_path">
                {{ currentReport.result_data.screenshot_path }}
              </el-descriptions-item>
              <el-descriptions-item label="错误日志" v-if="currentReport.result_data.error_log">
                <pre style="white-space: pre-wrap; word-wrap: break-word; color: #F56C6C;">{{ currentReport.result_data.error_log }}</pre>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </div>

        <!-- 性能测试结果 -->
        <div v-if="currentReport.type === 'performance'">
          <el-card v-if="currentReport.result_data && currentReport.result_data.metrics">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="总样本数">
                {{ currentReport.result_data.metrics.total_samples }}
              </el-descriptions-item>
              <el-descriptions-item label="成功样本数">
                {{ currentReport.result_data.metrics.successful_samples }}
              </el-descriptions-item>
              <el-descriptions-item label="失败样本数">
                {{ currentReport.result_data.metrics.failed_samples }}
              </el-descriptions-item>
              <el-descriptions-item label="错误率">
                <span :style="{ color: currentReport.result_data.metrics.error_rate < 1 ? '#67C23A' : '#F56C6C' }">
                  {{ currentReport.result_data.metrics.error_rate?.toFixed(2) }}%
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="平均响应时间">
                {{ currentReport.result_data.metrics.average_response_time?.toFixed(2) }}ms
              </el-descriptions-item>
              <el-descriptions-item label="95%分位值">
                {{ currentReport.result_data.metrics.p95_response_time?.toFixed(2) }}ms
              </el-descriptions-item>
              <el-descriptions-item label="99%分位值">
                {{ currentReport.result_data.metrics.p99_response_time?.toFixed(2) }}ms
              </el-descriptions-item>
              <el-descriptions-item label="吞吐量">
                {{ currentReport.result_data.metrics.throughput?.toFixed(2) }} 请求/秒
              </el-descriptions-item>
            </el-descriptions>
            <div v-if="currentReport.result_data.html_report_path" style="margin-top: 20px">
              <el-alert
                title="HTML报告已生成"
                type="success"
                :closable="false"
              >
                <template #default>
                  <p>报告路径: {{ currentReport.result_data.html_report_path }}</p>
                </template>
              </el-alert>
            </div>
          </el-card>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { reportApi } from '@/api/reports'

const loading = ref(false)
const reports = ref([])
const filterType = ref('')

const detailDialogVisible = ref(false)
const currentReport = ref(null)

const loadReports = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterType.value) {
      params.report_type = filterType.value
    }
    const data = await reportApi.getReports(params)
    reports.value = data
  } catch (error) {
    console.error('加载报告失败', error)
  } finally {
    loading.value = false
  }
}

const handleView = async (row) => {
  try {
    const data = await reportApi.getReport(row.id)
    currentReport.value = data
    detailDialogVisible.value = true
  } catch (error) {
    console.error('加载报告详情失败', error)
  }
}

const getTypeTag = (type) => {
  const tags = {
    api: 'primary',
    ui: 'success',
    performance: 'warning'
  }
  return tags[type] || 'info'
}

const getTypeText = (type) => {
  const texts = {
    api: 'API测试',
    ui: 'UI测试',
    performance: '性能测试'
  }
  return texts[type] || type
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.reports-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

