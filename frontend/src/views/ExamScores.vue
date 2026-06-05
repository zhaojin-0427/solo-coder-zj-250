<template>
  <div class="page">
    <el-card class="filter-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="20" color="#409EFF"><EditPen /></el-icon>
          <span>轮次成绩录入</span>
        </div>
      </template>
      <el-form :inline="true" :model="filterForm" label-width="100px">
        <el-form-item label="选择考试">
          <el-select v-model="filterForm.exam_id" placeholder="请选择考试" style="width: 280px" @change="onExamChange">
            <el-option v-for="e in exams" :key="e.id" :label="`${e.name} (${e.target_level})`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择考生">
          <el-select v-model="filterForm.registration_id" placeholder="请选择考生" style="width: 280px" :disabled="!filterForm.exam_id" @change="onRegistrationChange">
            <el-option v-for="r in registrations" :key="r.id" :label="`${r.member_name} (${r.bow_type})`" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择轮次">
          <el-select v-model="filterForm.round_number" placeholder="请选择轮次" style="width: 180px" :disabled="!filterForm.registration_id" @change="onRoundChange">
            <el-option v-for="n in availableRounds" :key="n" :label="`第${n}轮`" :value="n" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-descriptions v-if="selectedExam" :column="4" border size="small" class="exam-info">
        <el-descriptions-item label="考试名称">{{ selectedExam.name }}</el-descriptions-item>
        <el-descriptions-item label="目标等级">
          <el-tag type="warning">{{ selectedExam.target_level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="每轮箭数">
          <span style="font-weight: bold; color: #409EFF">{{ selectedExam.arrows_per_round }} 支</span>
        </el-descriptions-item>
        <el-descriptions-item label="总轮数">
          <span style="font-weight: bold; color: #67C23A">{{ selectedExam.total_rounds }} 轮</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="10">
        <el-card class="form-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" color="#409EFF"><Edit /></el-icon>
              <span>{{ isEditMode ? '修改轮次成绩' : '录入轮次成绩' }}</span>
              <el-tag v-if="filterForm.round_number" type="primary" style="margin-left: 10px">
                第{{ filterForm.round_number }}轮
              </el-tag>
            </div>
          </template>

          <el-form :model="scoreForm" label-width="100px">
            <div class="arrows-input">
              <div v-for="(arrow, index) in arrowScores" :key="index" class="arrow-item">
                <label class="arrow-label">第{{ index + 1 }}箭</label>
                <el-input-number
                  v-model="arrowScores[index]"
                  :min="0"
                  :max="10"
                  :precision="0"
                  :disabled="!filterForm.round_number"
                  @change="calculateRoundTotal"
                  style="width: 100%"
                />
              </div>
            </div>

            <el-form-item label="本轮总分" style="margin-top: 20px">
              <el-input-number
                v-model="scoreForm.round_total"
                :min="0"
                :max="maxRoundScore"
                disabled
                style="width: 100%"
              />
              <span class="score-hint">
                满分 {{ maxRoundScore }} 环
              </span>
            </el-form-item>

            <el-form-item label="备注">
              <el-input v-model="scoreForm.notes" type="textarea" :rows="2" placeholder="本轮备注信息" :disabled="!filterForm.round_number" />
            </el-form-item>

            <el-form-item>
              <el-button v-if="isEditMode" type="success" style="width: 100%" @click="updateScore" :disabled="!canSubmit">
                <el-icon><Check /></el-icon> 保存修改
              </el-button>
              <el-button v-else type="primary" style="width: 100%" @click="createScore" :disabled="!canSubmit">
                <el-icon><Check /></el-icon> 提交本轮成绩
              </el-button>
              <el-button v-if="isEditMode" style="width: 100%; margin-top: 10px" @click="cancelEdit">
                取消修改
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="selectedRegistration" class="registration-info">
            <el-divider>考生当前状态</el-divider>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="考生姓名">{{ selectedRegistration.member_name }}</el-descriptions-item>
              <el-descriptions-item label="弓型">{{ selectedRegistration.bow_type }}</el-descriptions-item>
              <el-descriptions-item label="当前总分">
                <span style="font-weight: bold; color: #E6A23C; font-size: 18px">{{ currentTotalScore }}</span>
                <span style="color: #999; margin-left: 5px">/ {{ maxTotalScore }} 环</span>
              </el-descriptions-item>
              <el-descriptions-item label="已完成轮数">
                <span style="font-weight: bold; color: #67C23A">{{ completedRounds }}</span>
                <span style="color: #999; margin-left: 5px">/ {{ selectedExam?.total_rounds || 0 }} 轮</span>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" color="#409EFF"><List /></el-icon>
              <span>已录入轮次成绩</span>
              <el-tag v-if="roundScores.length > 0" type="success" style="margin-left: 10px">
                共 {{ roundScores.length }} 轮
              </el-tag>
            </div>
          </template>

          <el-table :data="roundScores" stripe border empty-text="暂无成绩数据">
            <el-table-column prop="round_number" label="轮次" width="80" align="center">
              <template #default="{ row }">
                <el-tag type="primary">第{{ row.round_number }}轮</el-tag>
              </template>
            </el-table-column>
            <el-table-column v-for="n in maxArrowsPerRound" :key="`arrow${n}`" :label="`第${n}箭`" width="70" align="center">
              <template #default="{ row }">
                <span :class="getArrowScoreClass(getArrowScore(row, n - 1))">{{ getArrowScore(row, n - 1) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="round_total" label="本轮总分" width="100" align="center">
              <template #default="{ row }">
                <span style="font-weight: bold; color: #409EFF">{{ row.round_total }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
            <el-table-column label="操作" width="140" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="editScore(row)">修改</el-button>
                <el-button type="danger" size="small" @click="deleteScore(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getExamRoundScores,
  createExamRoundScore,
  updateExamRoundScore,
  deleteExamRoundScore,
  getLevelExams,
  getExamRegistrations
} from '../api'

const exams = ref([])
const registrations = ref([])
const roundScores = ref([])
const isEditMode = ref(false)
const editingScoreId = ref(null)

const filterForm = ref({
  exam_id: '',
  registration_id: '',
  round_number: ''
})

const scoreForm = ref({
  round_total: 0,
  notes: ''
})

const arrowScores = ref([])

const selectedExam = computed(() => {
  return exams.value.find(e => e.id === filterForm.value.exam_id)
})

const selectedRegistration = computed(() => {
  return registrations.value.find(r => r.id === filterForm.value.registration_id)
})

const maxArrowsPerRound = computed(() => {
  return selectedExam.value?.arrows_per_round || 6
})

const maxRoundScore = computed(() => {
  return maxArrowsPerRound.value * 10
})

const maxTotalScore = computed(() => {
  return (selectedExam.value?.arrows_per_round || 0) * (selectedExam.value?.total_rounds || 0) * 10
})

const availableRounds = computed(() => {
  if (!selectedExam.value) return []
  const total = selectedExam.value.total_rounds || 0
  const usedRounds = roundScores.value.map(s => s.round_number)
  const rounds = []
  for (let i = 1; i <= total; i++) {
    if (!usedRounds.includes(i) || (isEditMode.value && i === filterForm.value.round_number)) {
      rounds.push(i)
    }
  }
  return rounds
})

const currentTotalScore = computed(() => {
  return roundScores.value.reduce((sum, s) => sum + (s.round_total || 0), 0)
})

const completedRounds = computed(() => {
  return roundScores.value.length
})

const canSubmit = computed(() => {
  return filterForm.value.exam_id &&
    filterForm.value.registration_id &&
    filterForm.value.round_number &&
    arrowScores.value.every(s => s !== null && s !== undefined && s !== '')
})

const initArrowScores = () => {
  const count = maxArrowsPerRound.value
  arrowScores.value = Array(count).fill(0)
}

const calculateRoundTotal = () => {
  scoreForm.value.round_total = arrowScores.value.reduce((sum, s) => sum + (Number(s) || 0), 0)
}

const getArrowScoreClass = (score) => {
  const s = Number(score)
  if (s === 10) return 'arrow-perfect'
  if (s >= 8) return 'arrow-good'
  if (s >= 5) return 'arrow-normal'
  return 'arrow-low'
}

const getArrowScore = (row, index) => {
  if (row.arrow_scores_list && row.arrow_scores_list[index] !== undefined) {
    return row.arrow_scores_list[index]
  }
  if (row.arrow_scores) {
    const arr = row.arrow_scores.split(',').map(Number)
    return arr[index] ?? 0
  }
  return 0
}

const loadExams = async () => {
  try {
    const res = await getLevelExams()
    exams.value = res.data
  } catch (e) {
    ElMessage.error('加载考试列表失败')
  }
}

const loadRegistrations = async () => {
  if (!filterForm.value.exam_id) {
    registrations.value = []
    return
  }
  try {
    const res = await getExamRegistrations({ exam_id: filterForm.value.exam_id })
    registrations.value = res.data
  } catch (e) {
    ElMessage.error('加载报名列表失败')
  }
}

const loadRoundScores = async () => {
  if (!filterForm.value.exam_id || !filterForm.value.registration_id) {
    roundScores.value = []
    return
  }
  try {
    const res = await getExamRoundScores({
      exam_id: filterForm.value.exam_id,
      registration_id: filterForm.value.registration_id
    })
    roundScores.value = res.data.sort((a, b) => a.round_number - b.round_number)
  } catch (e) {
    ElMessage.error('加载轮次成绩失败')
  }
}

const onExamChange = () => {
  filterForm.value.registration_id = ''
  filterForm.value.round_number = ''
  roundScores.value = []
  initArrowScores()
  loadRegistrations()
}

const onRegistrationChange = () => {
  filterForm.value.round_number = ''
  initArrowScores()
  loadRoundScores()
}

const onRoundChange = () => {
  if (isEditMode.value) return
  initArrowScores()
}

const createScore = async () => {
  try {
    const data = {
      exam_id: filterForm.value.exam_id,
      registration_id: filterForm.value.registration_id,
      round_number: filterForm.value.round_number,
      arrow_scores: arrowScores.value.map(s => Number(s)),
      round_total: scoreForm.value.round_total,
      notes: scoreForm.value.notes
    }
    await createExamRoundScore(data)
    ElMessage.success('成绩录入成功')
    resetForm()
    loadRoundScores()
  } catch (e) {
    ElMessage.error('录入失败')
  }
}

const editScore = (row) => {
  isEditMode.value = true
  editingScoreId.value = row.id
  filterForm.value.round_number = row.round_number

  const count = maxArrowsPerRound.value
  for (let i = 0; i < count; i++) {
    arrowScores.value[i] = getArrowScore(row, i)
  }
  scoreForm.value.round_total = row.round_total
  scoreForm.value.notes = row.notes || ''
}

const updateScore = async () => {
  try {
    const data = {
      arrow_scores: arrowScores.value.map(s => Number(s)),
      round_total: scoreForm.value.round_total,
      notes: scoreForm.value.notes
    }
    await updateExamRoundScore(editingScoreId.value, data)
    ElMessage.success('修改成功')
    resetForm()
    loadRoundScores()
  } catch (e) {
    ElMessage.error('修改失败')
  }
}

const deleteScore = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除第${row.round_number}轮的成绩吗？`, '提示', { type: 'warning' })
    await deleteExamRoundScore(row.id)
    ElMessage.success('删除成功')
    if (isEditMode.value && editingScoreId.value === row.id) {
      resetForm()
    }
    loadRoundScores()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const cancelEdit = () => {
  resetForm()
}

const resetForm = () => {
  isEditMode.value = false
  editingScoreId.value = null
  filterForm.value.round_number = ''
  scoreForm.value = {
    round_total: 0,
    notes: ''
  }
  initArrowScores()
}

onMounted(() => {
  loadExams()
  initArrowScores()
})
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.filter-card,
.form-card,
.table-card {
  margin-bottom: 20px;
}

.exam-info {
  margin-top: 20px;
}

.arrows-input {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 10px;
}

.arrow-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.arrow-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.score-hint {
  margin-left: 10px;
  color: #999;
  font-size: 13px;
}

.registration-info {
  margin-top: 20px;
}

.arrow-perfect {
  color: #E6A23C;
  font-weight: bold;
  font-size: 16px;
}

.arrow-good {
  color: #67C23A;
  font-weight: bold;
}

.arrow-normal {
  color: #409EFF;
}

.arrow-low {
  color: #F56C6C;
}
</style>
