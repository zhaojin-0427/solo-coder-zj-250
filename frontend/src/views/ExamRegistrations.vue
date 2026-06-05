<template>
  <div class="page">
    <el-card class="card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <div style="display: flex; align-items: center; gap: 16px">
            <span>考试报名管理</span>
            <el-select
              v-model="selectedExamId"
              placeholder="请选择考试"
              style="width: 300px"
              @change="handleExamChange"
            >
              <el-option
                v-for="exam in exams"
                :key="exam.id"
                :label="exam.name"
                :value="exam.id"
              />
            </el-select>
          </div>
          <el-button
            type="primary"
            :disabled="!selectedExamId"
            @click="showAddDialog"
          >
            <el-icon><Plus /></el-icon> 新增报名
          </el-button>
        </div>
      </template>

      <div v-if="selectedExam" class="exam-info">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="info-item">
              <span class="label">考试名称：</span>
              <span class="value">{{ selectedExam.name }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <span class="label">目标等级：</span>
              <el-tag type="warning">{{ selectedExam.target_level }}</el-tag>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <span class="label">报名容量：</span>
              <span class="value">
                {{ registeredCount }}/{{ selectedExam.registration_capacity }}
              </span>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 12px">
          <el-col :span="8">
            <div class="info-item">
              <span class="label">已报名人数：</span>
              <span class="value highlight">{{ registeredCount }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <span class="label">报名截止：</span>
              <span class="value">{{ selectedExam.registration_deadline }}</span>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <span class="label">弓型限制：</span>
              <span class="value">{{ selectedExam.bow_type_restriction || '无限制' }}</span>
            </div>
          </el-col>
        </el-row>
      </div>

      <el-divider v-if="selectedExam" />

      <div v-if="selectedExam" class="stats-panel">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="stat-card passed">
              <div class="stat-icon">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.passed }}</div>
                <div class="stat-label">通过人数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card failed">
              <div class="stat-icon">
                <el-icon><CircleClose /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.failed }}</div>
                <div class="stat-label">未通过人数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card promoted">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.promoted }}</div>
                <div class="stat-label">晋级人数</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <el-table
        v-if="selectedExam"
        :data="registrations"
        stripe
        border
        style="margin-top: 20px"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="member_name" label="会员姓名" width="120" />
        <el-table-column prop="member_phone" label="手机号" width="140" />
        <el-table-column prop="current_level" label="当前等级" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.current_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="registration_time" label="报名时间" width="180" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="showDetail(row)"
            >
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button
              v-if="row.status === '已报名'"
              type="danger"
              size="small"
              @click="cancelRegistration(row)"
            >
              <el-icon><Delete /></el-icon> 取消
            </el-button>
            <el-button
              v-if="row.status === '已完成' && !row.is_finalized"
              type="success"
              size="small"
              @click="finalizeRegistration(row)"
            >
              <el-icon><Cpu /></el-icon> 结算
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-else description="请选择考试查看报名信息" />
    </el-card>

    <el-dialog v-model="addDialogVisible" title="新增报名" width="600px">
      <el-form :model="addForm" label-width="120px">
        <el-form-item label="选择会员">
          <el-select
            v-model="addForm.member_id"
            placeholder="请选择会员"
            style="width: 100%"
            filterable
            @change="checkEligibility"
          >
            <el-option
              v-for="member in availableMembers"
              :key="member.id"
              :label="`${member.name} (${member.phone} - ${member.tech_level})`"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <div v-if="eligibilityResult" class="eligibility-result">
        <el-alert
          :title="eligibilityResult.eligible ? '资格校验通过' : '资格校验不通过'"
          :type="eligibilityResult.eligible ? 'success' : 'error'"
          :closable="false"
        >
          <div v-if="eligibilityResult.details" class="check-details">
            <div
              v-for="(item, index) in eligibilityResult.details"
              :key="index"
              class="check-item"
            >
              <span class="check-label">{{ item.name }}：</span>
              <el-tag :type="item.passed ? 'success' : 'danger'" size="small">
                {{ item.passed ? '通过' : '不通过' }}
              </el-tag>
              <span v-if="item.message" class="check-message">
                {{ item.message }}
              </span>
            </div>
          </div>
        </el-alert>
      </div>

      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!eligibilityResult?.eligible"
          @click="submitRegistration"
        >
          确认报名
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="报名详情" width="600px">
      <el-descriptions v-if="detailData" :column="2" border>
        <el-descriptions-item label="报名ID">
          {{ detailData.id }}
        </el-descriptions-item>
        <el-descriptions-item label="会员姓名">
          {{ detailData.member_name }}
        </el-descriptions-item>
        <el-descriptions-item label="手机号">
          {{ detailData.member_phone }}
        </el-descriptions-item>
        <el-descriptions-item label="当前等级">
          <el-tag>{{ detailData.current_level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="报名时间">
          {{ detailData.registration_time }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(detailData.status)">
            {{ detailData.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="考试名称" :span="2">
          {{ detailData.exam_name }}
        </el-descriptions-item>
        <el-descriptions-item label="总成绩" v-if="detailData.total_score !== null">
          {{ detailData.total_score }} 环
        </el-descriptions-item>
        <el-descriptions-item label="排名" v-if="detailData.ranking">
          第 {{ detailData.ranking }} 名
        </el-descriptions-item>
        <el-descriptions-item label="是否通过" v-if="detailData.is_passed !== null">
          <el-tag :type="detailData.is_passed ? 'success' : 'danger'">
            {{ detailData.is_passed ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="是否晋级" v-if="detailData.level_upgraded !== null && detailData.level_upgraded !== undefined">
          <el-tag :type="detailData.level_upgraded ? 'success' : 'info'">
            {{ detailData.level_upgraded ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getExamRegistrations,
  checkRegistrationEligibility,
  createExamRegistration,
  deleteExamRegistration,
  getLevelExams,
  getMembers,
  finalizeRegistration as finalizeReg
} from '../api'

const exams = ref([])
const members = ref([])
const registrations = ref([])
const selectedExamId = ref(null)
const selectedExam = ref(null)
const registeredCount = ref(0)

const addDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const eligibilityResult = ref(null)
const detailData = ref(null)

const addForm = ref({
  member_id: null,
  exam_id: null
})

const stats = ref({
  passed: 0,
  failed: 0,
  promoted: 0
})

const availableMembers = computed(() => {
  if (!selectedExamId.value) return []
  const registeredMemberIds = registrations.value.map(r => r.member_id)
  return members.value.filter(m => !registeredMemberIds.includes(m.id))
})

const getStatusType = (status) => {
  const types = {
    '已报名': 'primary',
    '已完成': 'success',
    '已取消': 'info',
    '进行中': 'warning'
  }
  return types[status] || 'info'
}

const loadData = async () => {
  try {
    const [res1, res2] = await Promise.all([
      getLevelExams(),
      getMembers()
    ])
    exams.value = res1.data
    members.value = res2.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
}

const handleExamChange = async (examId) => {
  selectedExam.value = exams.value.find(e => e.id === examId)
  if (selectedExam.value) {
    await loadRegistrations()
  }
}

const loadRegistrations = async () => {
  try {
    const res = await getExamRegistrations({ exam_id: selectedExamId.value })
    registrations.value = res.data
    registeredCount.value = res.data.length
    calculateStats()
  } catch (e) {
    ElMessage.error('加载报名列表失败')
  }
}

const calculateStats = () => {
  stats.value = {
    passed: registrations.value.filter(r => r.is_passed === true).length,
    failed: registrations.value.filter(r => r.is_passed === false).length,
    promoted: registrations.value.filter(r => r.level_upgraded === true).length
  }
}

const showAddDialog = () => {
  addForm.value = {
    member_id: null,
    exam_id: selectedExamId.value
  }
  eligibilityResult.value = null
  addDialogVisible.value = true
}

const checkEligibility = async (memberId) => {
  if (!memberId) {
    eligibilityResult.value = null
    return
  }
  try {
    const res = await checkRegistrationEligibility({
      member_id: memberId,
      exam_id: selectedExamId.value
    })
    eligibilityResult.value = res.data
  } catch (e) {
    ElMessage.error('资格校验失败')
  }
}

const submitRegistration = async () => {
  if (!addForm.value.member_id) {
    ElMessage.warning('请选择会员')
    return
  }
  try {
    await createExamRegistration({
      member_id: addForm.value.member_id,
      exam_id: selectedExamId.value
    })
    ElMessage.success('报名成功')
    addDialogVisible.value = false
    loadRegistrations()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '报名失败')
  }
}

const cancelRegistration = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定取消会员「${row.member_name}」的报名吗？`,
      '确认取消',
      { type: 'warning' }
    )
    await deleteExamRegistration(row.id)
    ElMessage.success('取消报名成功')
    loadRegistrations()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('取消失败')
  }
}

const finalizeRegistration = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定结算「${row.member_name}」的成绩和排名吗？`,
      '确认结算',
      { type: 'warning' }
    )
    await finalizeReg(row.id)
    ElMessage.success('结算成功')
    loadRegistrations()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('结算失败')
  }
}

const showDetail = (row) => {
  detailData.value = {
    ...row,
    exam_name: selectedExam.value?.name
  }
  detailDialogVisible.value = true
}

onMounted(loadData)
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.card {
  margin-top: 20px;
}
.exam-info {
  padding: 10px 0;
}
.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.info-item .label {
  color: #909399;
  font-weight: 500;
}
.info-item .value {
  color: #303133;
}
.info-item .value.highlight {
  color: #409eff;
  font-weight: bold;
  font-size: 16px;
}
.stats-panel {
  margin-top: 10px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 10px;
  border: none;
}
.stat-card.passed {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
}
.stat-card.failed {
  background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%);
}
.stat-card.promoted {
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
}
.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}
.stat-card.passed .stat-icon {
  background: #67c23a;
  color: white;
}
.stat-card.failed .stat-icon {
  background: #f56c6c;
  color: white;
}
.stat-card.promoted .stat-icon {
  background: #409eff;
  color: white;
}
.stat-content {
  flex: 1;
}
.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}
.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 4px;
}
.eligibility-result {
  margin-top: 20px;
}
.check-details {
  margin-top: 10px;
}
.check-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  font-size: 13px;
}
.check-label {
  color: #606266;
  min-width: 100px;
}
.check-message {
  color: #909399;
  margin-left: 8px;
}
</style>
