<template>
  <div class="page">
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card class="form-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" color="#409EFF"><EditPen /></el-icon>
              <span>录入训练成绩</span>
            </div>
          </template>
          <el-form :model="scoreForm" label-width="100px">
            <el-form-item label="会员">
              <el-select v-model="scoreForm.member_id" placeholder="请选择会员" style="width: 100%" @change="loadMemberProgress">
                <el-option v-for="m in members" :key="m.id" :label="`${m.name} (${m.tech_level})`" :value="m.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="箭靶距离">
              <el-select v-model="scoreForm.target_distance" placeholder="请选择距离" style="width: 100%">
                <el-option label="10米" :value="10" />
                <el-option label="18米" :value="18" />
                <el-option label="30米" :value="30" />
                <el-option label="50米" :value="50" />
                <el-option label="70米" :value="70" />
              </el-select>
            </el-form-item>
            <el-form-item label="弓型">
              <el-select v-model="scoreForm.bow_type" placeholder="请选择弓型" style="width: 100%">
                <el-option label="反曲弓" value="反曲弓" />
                <el-option label="复合弓" value="复合弓" />
                <el-option label="传统弓" value="传统弓" />
                <el-option label="美式猎弓" value="美式猎弓" />
              </el-select>
            </el-form-item>
            <el-form-item label="箭支数量">
              <el-input-number v-model="scoreForm.arrows_count" :min="6" :max="72" style="width: 100%" />
            </el-form-item>
            <el-form-item label="总成绩">
              <el-input-number v-model="scoreForm.total_score" :min="0" :max="scoreForm.arrows_count * 10" style="width: 100%" />
            </el-form-item>
            <el-form-item label="训练日期">
              <el-date-picker
                v-model="scoreForm.training_date"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="scoreForm.notes" type="textarea" :rows="2" placeholder="训练备注" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" style="width: 100%" @click="submitScore">
                <el-icon><Check /></el-icon> 提交成绩
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="currentMember" class="member-info">
            <el-divider>当前会员信息</el-divider>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="姓名">{{ currentMember.name }}</el-descriptions-item>
              <el-descriptions-item label="技术等级">
                <el-tag type="warning">{{ currentMember.tech_level }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="平均成绩">{{ currentMember.avg_score }} 环</el-descriptions-item>
              <el-descriptions-item label="入馆日期">{{ currentMember.join_date }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card class="table-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" color="#409EFF"><List /></el-icon>
              <span>成绩记录</span>
            </div>
          </template>
          <el-table :data="scores" stripe border>
            <el-table-column prop="member_name" label="会员" width="100" />
            <el-table-column prop="target_distance" label="距离" width="90">
              <template #default="{ row }">{{ row.target_distance }}米</template>
            </el-table-column>
            <el-table-column prop="bow_type" label="弓型" width="100" />
            <el-table-column prop="arrows_count" label="箭数" width="80" />
            <el-table-column prop="total_score" label="总成绩" width="100">
              <template #default="{ row }">
                <span style="font-weight: bold; color: #409EFF">{{ row.total_score }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="avg_per_arrow" label="平均" width="80" />
            <el-table-column prop="training_date" label="日期" />
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
            <el-table-column label="操作" width="80" fixed="right">
              <template #default="{ row }">
                <el-button type="danger" size="small" text @click="deleteScore(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card v-if="progressData.length > 0" class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="20" color="#409EFF"><TrendCharts /></el-icon>
              <span>成绩进步曲线</span>
            </div>
          </template>
          <div ref="progressChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getScores, createScore, deleteScore as delScore, getMembers, getMemberProgress } from '../api'
import * as echarts from 'echarts'

const scores = ref([])
const members = ref([])
const progressData = ref([])
const progressChart = ref(null)
let chartInstance = null

const scoreForm = ref({
  member_id: '',
  target_distance: 18,
  bow_type: '反曲弓',
  arrows_count: 12,
  total_score: 0,
  training_date: new Date().toISOString().split('T')[0],
  notes: ''
})

const currentMember = computed(() => {
  return members.value.find(m => m.id === scoreForm.value.member_id)
})

const loadData = async () => {
  try {
    const [res1, res2] = await Promise.all([getScores(), getMembers()])
    scores.value = res1.data
    members.value = res2.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
}

const loadMemberProgress = async () => {
  if (!scoreForm.value.member_id) {
    progressData.value = []
    return
  }
  try {
    const res = await getMemberProgress(scoreForm.value.member_id)
    progressData.value = res.data
    await nextTick()
    renderChart()
  } catch (e) {
    console.error(e)
  }
}

const renderChart = () => {
  if (!progressChart.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(progressChart.value)
  }
  
  const data = progressData.value
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['单次成绩', '平均成绩'] },
    xAxis: { type: 'category', data: data.map(d => d.date) },
    yAxis: { type: 'value', name: '环数' },
    series: [
      {
        name: '单次成绩',
        type: 'line',
        data: data.map(d => d.score),
        smooth: true,
        itemStyle: { color: '#409EFF' },
        areaStyle: { color: 'rgba(64, 158, 255, 0.1)' }
      },
      {
        name: '平均成绩',
        type: 'line',
        data: data.map(d => d.avg_score),
        smooth: true,
        itemStyle: { color: '#67C23A' },
        lineStyle: { type: 'dashed' }
      }
    ]
  }
  chartInstance.setOption(option)
}

const submitScore = async () => {
  if (!scoreForm.value.member_id) {
    ElMessage.warning('请选择会员')
    return
  }
  try {
    const res = await createScore(scoreForm.value)
    ElMessage.success(`成绩录入成功！当前技术等级：${res.data.tech_level}，平均成绩：${res.data.avg_score}`)
    scoreForm.value.total_score = 0
    scoreForm.value.notes = ''
    loadData()
    loadMemberProgress()
  } catch (e) {
    ElMessage.error('录入失败')
  }
}

const deleteScore = async (id) => {
  try {
    const scoreItem = scores.value.find(s => s.id === id)
    await ElMessageBox.confirm('确认删除该成绩记录吗？', '提示', { type: 'warning' })
    await delScore(id)
    ElMessage.success('删除成功')
    loadData()
    if (scoreItem && scoreItem.member_id === scoreForm.value.member_id) {
      loadMemberProgress()
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => chartInstance?.resize())
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
.form-card, .table-card, .chart-card {
  margin-bottom: 20px;
}
.member-info {
  margin-top: 20px;
}
</style>
