<template>
  <div class="page">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="选择考试">
          <el-select v-model="filterForm.examId" placeholder="请选择考试" style="width: 250px" @change="onExamChange">
            <el-option
              v-for="exam in exams"
              :key="exam.id"
              :label="`${exam.name} - ${exam.exam_date}`"
              :value="exam.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <div v-if="filterForm.examId">
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon reserved">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.reservedCount }}</div>
                <div class="stat-label">已预约器材</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon available">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.availableCount }}</div>
                <div class="stat-label">可用器材</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon bow">
                <el-icon><Tools /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.bowCount }}</div>
                <div class="stat-label">弓</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon arrow">
                <el-icon><Position /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.arrowCount }}</div>
                <div class="stat-label">箭</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="tabs-card">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="已预约器材" name="reserved">
            <div class="tab-actions">
              <el-button type="primary" @click="loadReservations">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
            <el-table :data="reservations" stripe border>
              <el-table-column prop="equipment_name" label="器材名称" />
              <el-table-column prop="equipment_type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="typeTagType(row.equipment_type)">{{ row.equipment_type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="equipment_serial" label="器材编号" />
              <el-table-column prop="assigned_to_name" label="分配给" width="120">
                <template #default="{ row }">
                  {{ row.assigned_to_name || '公共器材' }}
                </template>
              </el-table-column>
              <el-table-column prop="reservation_time" label="预约时间" width="180" />
              <el-table-column label="使用时间段" width="200">
                <template #default="{ row }">
                  {{ row.start_time }} - {{ row.end_time }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="reservationStatusTagType(row.status)">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="showEditDialog(row)">
                    编辑
                  </el-button>
                  <el-button type="danger" link size="small" @click="handleDelete(row)">
                    取消预约
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="可用器材" name="available">
            <div class="tab-actions">
              <el-button type="success" @click="showBatchReserveDialog" :disabled="selectedEquipment.length === 0">
                <el-icon><CalendarPlus /></el-icon> 批量预约 ({{ selectedEquipment.length }})
              </el-button>
              <el-button @click="loadAvailableEquipment">
                <el-icon><Refresh /></el-icon> 刷新
              </el-button>
            </div>
            <el-table :data="availableEquipment" stripe border @selection-change="handleSelectionChange">
              <el-table-column type="selection" width="55" />
              <el-table-column prop="name" label="器材名称" />
              <el-table-column prop="type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="typeTagType(row.type)">{{ row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="serial_number" label="器材编号" />
              <el-table-column prop="brand" label="品牌" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag type="success">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="预约统计" name="statistics">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <span>各类型器材预约数量</span>
                  </template>
                  <div class="chart-container">
                    <el-table :data="typeStats" border>
                      <el-table-column prop="type" label="器材类型" />
                      <el-table-column prop="total" label="总数" width="100" align="center" />
                      <el-table-column prop="reserved" label="已预约" width="100" align="center" />
                      <el-table-column prop="available" label="可用" width="100" align="center" />
                      <el-table-column label="使用率" width="150">
                        <template #default="{ row }">
                          <el-progress
                            :percentage="Math.round((row.reserved / row.total) * 100)"
                            :status="getUsageStatus(row.reserved, row.total)"
                          />
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <span>器材使用情况概览</span>
                  </template>
                  <div class="chart-container">
                    <el-descriptions :column="1" border>
                      <el-descriptions-item label="器材总数">
                        {{ usageStats.totalEquipment }}
                      </el-descriptions-item>
                      <el-descriptions-item label="已预约数量">
                        <el-tag type="warning">{{ usageStats.reservedEquipment }}</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="可用数量">
                        <el-tag type="success">{{ usageStats.availableEquipment }}</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="分配给会员">
                        <el-tag type="primary">{{ usageStats.assignedToMember }}</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="公共器材">
                        <el-tag type="info">{{ usageStats.publicEquipment }}</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="整体使用率">
                        <el-progress
                          :percentage="usageStats.usageRate"
                          :status="usageStats.usageRate >= 80 ? 'warning' : 'success'"
                        />
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <el-dialog v-model="batchReserveDialogVisible" title="批量预约器材" width="500px">
      <el-form :model="batchReserveForm" label-width="120px">
        <el-form-item label="已选器材">
          <el-tag
            v-for="item in selectedEquipment"
            :key="item.id"
            style="margin-right: 8px; margin-bottom: 8px"
            closable
            @close="removeFromSelection(item)"
          >
            {{ item.name }} ({{ item.serial_number }})
          </el-tag>
        </el-form-item>
        <el-form-item label="使用日期">
          <el-date-picker
            v-model="batchReserveForm.use_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker
            v-model="batchReserveForm.start_time"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker
            v-model="batchReserveForm.end_time"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="分配类型">
          <el-radio-group v-model="batchReserveForm.assign_type">
            <el-radio value="public">公共器材</el-radio>
            <el-radio value="member">指定会员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="batchReserveForm.assign_type === 'member'" label="选择会员">
          <el-select v-model="batchReserveForm.assigned_to" placeholder="请选择会员" style="width: 100%" filterable>
            <el-option
              v-for="member in members"
              :key="member.id"
              :label="`${member.name} - ${member.phone} (${member.tech_level})`"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchReserveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchReserve">确定预约</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑预约" width="500px">
      <el-form :model="editForm" label-width="120px">
        <el-form-item label="器材名称">
          <el-input v-model="editForm.equipment_name" disabled />
        </el-form-item>
        <el-form-item label="使用日期">
          <el-date-picker
            v-model="editForm.use_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker
            v-model="editForm.start_time"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker
            v-model="editForm.end_time"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="分配类型">
          <el-radio-group v-model="editForm.assign_type">
            <el-radio value="public">公共器材</el-radio>
            <el-radio value="member">指定会员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="editForm.assign_type === 'member'" label="选择会员">
          <el-select v-model="editForm.assigned_to" placeholder="请选择会员" style="width: 100%" filterable>
            <el-option
              v-for="member in members"
              :key="member.id"
              :label="`${member.name} - ${member.phone} (${member.tech_level})`"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="已预约" value="已预约" />
            <el-option label="使用中" value="使用中" />
            <el-option label="已归还" value="已归还" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getExamEquipmentReservations,
  getAvailableEquipmentForExam,
  batchReserveEquipment,
  updateExamEquipmentReservation,
  deleteExamEquipmentReservation,
  getLevelExams,
  getMembers
} from '../api'

const activeTab = ref('reserved')
const exams = ref([])
const members = ref([])
const reservations = ref([])
const availableEquipment = ref([])
const selectedEquipment = ref([])

const filterForm = reactive({
  examId: ''
})

const stats = reactive({
  reservedCount: 0,
  availableCount: 0,
  bowCount: 0,
  arrowCount: 0,
  guardCount: 0
})

const batchReserveDialogVisible = ref(false)
const batchReserveForm = reactive({
  use_date: '',
  start_time: '',
  end_time: '',
  assign_type: 'public',
  assigned_to: null
})

const editDialogVisible = ref(false)
const editForm = reactive({
  id: null,
  equipment_name: '',
  use_date: '',
  start_time: '',
  end_time: '',
  assign_type: 'public',
  assigned_to: null,
  status: ''
})

const typeStats = computed(() => {
  const types = ['弓', '箭', '护具']
  return types.map(type => {
    const total = availableEquipment.value.filter(e => e.type === type).length +
                  reservations.value.filter(r => r.equipment_type === type).length
    const reserved = reservations.value.filter(r => r.equipment_type === type).length
    return {
      type,
      total,
      reserved,
      available: total - reserved
    }
  })
})

const usageStats = computed(() => {
  const totalEquipment = reservations.value.length + availableEquipment.value.length
  const reservedEquipment = reservations.value.length
  const availableEquipmentCount = availableEquipment.value.length
  const assignedToMember = reservations.value.filter(r => r.assigned_to || r.reserved_for_member_id).length
  const publicEquipment = reservations.value.filter(r => !r.assigned_to && !r.reserved_for_member_id).length
  const usageRate = totalEquipment > 0 ? Math.round((reservedEquipment / totalEquipment) * 100) : 0

  return {
    totalEquipment,
    reservedEquipment,
    availableEquipment: availableEquipmentCount,
    assignedToMember,
    publicEquipment,
    usageRate
  }
})

const typeTagType = (type) => {
  const map = { '弓': 'primary', '箭': 'success', '护具': 'warning' }
  return map[type] || 'info'
}

const reservationStatusTagType = (status) => {
  const map = { '已预约': 'warning', '使用中': 'primary', '已归还': 'success', '已取消': 'danger' }
  return map[status] || 'info'
}

const getUsageStatus = (reserved, total) => {
  const rate = (reserved / total) * 100
  if (rate >= 80) return 'warning'
  if (rate >= 50) return ''
  return 'success'
}

const loadExams = async () => {
  try {
    const res = await getLevelExams()
    exams.value = res.data
  } catch (e) {
    ElMessage.error('加载考试列表失败')
  }
}

const loadMembers = async () => {
  try {
    const res = await getMembers()
    members.value = res.data
  } catch (e) {
    ElMessage.error('加载会员列表失败')
  }
}

const loadReservations = async () => {
  if (!filterForm.examId) return
  try {
    const res = await getExamEquipmentReservations({ exam_id: filterForm.examId })
    reservations.value = res.data
    updateStats()
  } catch (e) {
    ElMessage.error('加载预约列表失败')
  }
}

const loadAvailableEquipment = async () => {
  if (!filterForm.examId) return
  try {
    const res = await getAvailableEquipmentForExam({ exam_id: filterForm.examId })
    availableEquipment.value = res.data
    selectedEquipment.value = []
    updateStats()
  } catch (e) {
    ElMessage.error('加载可用器材失败')
  }
}

const updateStats = () => {
  stats.reservedCount = reservations.value.length
  stats.availableCount = availableEquipment.value.length
  stats.bowCount = reservations.value.filter(r => r.equipment_type === '弓').length +
                   availableEquipment.value.filter(e => e.type === '弓').length
  stats.arrowCount = reservations.value.filter(r => r.equipment_type === '箭').length +
                     availableEquipment.value.filter(e => e.type === '箭').length
  stats.guardCount = reservations.value.filter(r => r.equipment_type === '护具').length +
                     availableEquipment.value.filter(e => e.type === '护具').length
}

const onExamChange = () => {
  loadReservations()
  loadAvailableEquipment()
}

const handleSelectionChange = (val) => {
  selectedEquipment.value = val
}

const removeFromSelection = (item) => {
  selectedEquipment.value = selectedEquipment.value.filter(e => e.id !== item.id)
}

const showBatchReserveDialog = () => {
  if (selectedEquipment.value.length === 0) {
    ElMessage.warning('请先选择要预约的器材')
    return
  }
  const exam = exams.value.find(e => e.id === filterForm.examId)
  batchReserveForm.use_date = exam?.exam_date || new Date().toISOString().split('T')[0]
  batchReserveForm.start_time = '09:00'
  batchReserveForm.end_time = '12:00'
  batchReserveForm.assign_type = 'public'
  batchReserveForm.assigned_to = null
  batchReserveDialogVisible.value = true
}

const handleBatchReserve = async () => {
  if (!batchReserveForm.use_date || !batchReserveForm.start_time || !batchReserveForm.end_time) {
    ElMessage.warning('请填写完整的时间段信息')
    return
  }
  if (batchReserveForm.assign_type === 'member' && !batchReserveForm.assigned_to) {
    ElMessage.warning('请选择分配的会员')
    return
  }

  try {
    await batchReserveEquipment({
      exam_id: filterForm.examId,
      equipment_ids: selectedEquipment.value.map(e => e.id),
      use_date: batchReserveForm.use_date,
      start_time: batchReserveForm.start_time,
      end_time: batchReserveForm.end_time,
      assign_type: batchReserveForm.assign_type,
      assigned_to: batchReserveForm.assign_type === 'member' ? batchReserveForm.assigned_to : null
    })
    ElMessage.success('批量预约成功')
    batchReserveDialogVisible.value = false
    loadReservations()
    loadAvailableEquipment()
  } catch (e) {
    ElMessage.error('批量预约失败')
  }
}

const showEditDialog = (row) => {
  editForm.id = row.id
  editForm.equipment_name = row.equipment_name
  if (row.use_date) {
    editForm.use_date = row.use_date
    const s = row.start_time || ''
    const e = row.end_time || ''
    editForm.start_time = (s.split(' ')[1] || s).substring(0, 5)
    editForm.end_time = (e.split(' ')[1] || e).substring(0, 5)
  } else {
    const s = row.start_time || ''
    const e = row.end_time || ''
    editForm.use_date = s.split(' ')[0]
    editForm.start_time = (s.split(' ')[1] || s).substring(0, 5)
    editForm.end_time = (e.split(' ')[1] || e).substring(0, 5)
  }
  const assignedId = row.assigned_to || row.reserved_for_member_id
  editForm.assign_type = assignedId ? 'member' : 'public'
  editForm.assigned_to = assignedId
  editForm.status = row.status
  editDialogVisible.value = true
}

const handleUpdate = async () => {
  if (!editForm.use_date || !editForm.start_time || !editForm.end_time) {
    ElMessage.warning('请填写完整的时间段信息')
    return
  }
  if (editForm.assign_type === 'member' && !editForm.assigned_to) {
    ElMessage.warning('请选择分配的会员')
    return
  }

  try {
    await updateExamEquipmentReservation(editForm.id, {
      use_date: editForm.use_date,
      start_time: editForm.start_time,
      end_time: editForm.end_time,
      assign_type: editForm.assign_type,
      assigned_to: editForm.assign_type === 'member' ? editForm.assigned_to : null,
      status: editForm.status
    })
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    loadReservations()
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要取消该预约吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteExamEquipmentReservation(row.id)
      ElMessage.success('取消预约成功')
      loadReservations()
      loadAvailableEquipment()
    } catch (e) {
      ElMessage.error('取消预约失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadExams()
  loadMembers()
})
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-card :deep(.el-card__body) {
  padding-bottom: 0;
}

.stats-row {
  margin-bottom: 0;
}

.stat-card {
  margin-bottom: 0;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.stat-icon.reserved {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.available {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-icon.bow {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.arrow {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.tabs-card {
  margin-top: 0;
}

.tab-actions {
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
}

.chart-card {
  height: 100%;
}

.chart-container {
  min-height: 300px;
}
</style>
