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

      <el-table :data="Array.isArray(reports) ? reports : []" v-loading="loading" stripe>
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
              <el-descriptions-item label="错误日志" v-if="currentReport.result_data.error_log">
                <pre style="white-space: pre-wrap; word-wrap: break-word; color: #F56C6C;">{{ currentReport.result_data.error_log }}</pre>
              </el-descriptions-item>
            </el-descriptions>
            
            <!-- 步骤截图列表 -->
            <el-divider>测试步骤截图</el-divider>
            <div v-if="currentReport.result_data.steps && currentReport.result_data.steps.length > 0">
              <el-timeline>
                <el-timeline-item
                  v-for="(step, index) in currentReport.result_data.steps"
                  :key="index"
                  :timestamp="formatTimestamp(step.timestamp)"
                  :type="step.success ? 'success' : 'danger'"
                  placement="top"
                >
                  <el-card>
                    <div style="display: flex; gap: 20px;">
                      <div style="flex: 1;">
                        <h4 style="margin: 0 0 10px 0;">
                          <el-tag :type="step.success ? 'success' : 'danger'" size="small" style="margin-right: 10px;">
                            {{ step.success ? '成功' : '失败' }}
                          </el-tag>
                          步骤 {{ step.step_index + 1 }}: {{ step.step_name }}
                        </h4>
                        <p style="margin: 5px 0; color: #666;">
                          <strong>操作类型:</strong> {{ step.step_type }}
                        </p>
                        <p v-if="step.comment" style="margin: 5px 0; color: #666;">
                          <strong>注释:</strong> {{ step.comment }}
                        </p>
                        <p v-if="step.error" style="margin: 5px 0; color: #F56C6C;">
                          <strong>错误:</strong> {{ step.error }}
                        </p>
                      </div>
                      <div v-if="step.screenshot_path" style="flex: 0 0 300px;">
                        <el-image
                          :src="getScreenshotUrl(step.screenshot_path)"
                          :preview-src-list="[getScreenshotUrl(step.screenshot_path)]"
                          fit="contain"
                          style="width: 100%; max-height: 200px; border: 1px solid #ddd; border-radius: 4px;"
                          :preview-teleported="true"
                        >
                          <template #error>
                            <div style="display: flex; align-items: center; justify-content: center; height: 100px; color: #999;">
                              截图加载失败
                            </div>
                          </template>
                        </el-image>
                      </div>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
            <div v-else-if="currentReport.result_data.screenshot_path" style="margin-top: 20px;">
              <el-alert title="最终截图" type="info" :closable="false">
                <el-image
                  :src="getScreenshotUrl(currentReport.result_data.screenshot_path)"
                  :preview-src-list="[getScreenshotUrl(currentReport.result_data.screenshot_path)]"
                  fit="contain"
                  style="width: 100%; max-height: 400px; margin-top: 10px; border: 1px solid #ddd; border-radius: 4px;"
                  :preview-teleported="true"
                >
                  <template #error>
                    <div style="display: flex; align-items: center; justify-content: center; height: 200px; color: #999;">
                      截图加载失败
                    </div>
                  </template>
                </el-image>
              </el-alert>
            </div>
            <div v-else style="margin-top: 20px;">
              <el-empty description="暂无截图" :image-size="100" />
            </div>
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
    reports.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载报告失败', error)
    reports.value = []
  } finally {
    loading.value = false
  }
}

const handleView = async (row) => {
  try {
    const data = await reportApi.getReport(row.id)
    currentReport.value = data || {}
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

const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp * 1000).toLocaleString('zh-CN')
}

const getScreenshotUrl = (screenshotPath) => {
  if (!screenshotPath) return ''
  // 将本地路径转换为URL路径
  // 例如: ./uploads/screenshots/case_1/step_0_xxx.png -> /api/uploads/screenshots/case_1/step_0_xxx.png
  let url = screenshotPath.replace(/\\/g, '/')
  if (url.startsWith('./')) {
    url = url.substring(2)
  }
  if (!url.startsWith('/')) {
    url = '/' + url
  }
  // 通过API代理访问
  return `/api${url}`
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

