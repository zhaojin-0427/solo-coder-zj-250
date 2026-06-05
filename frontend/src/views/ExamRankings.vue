<template>
  <div class="page">
    <el-row :gutter="20" class="exam-selector">
      <el-col :span="24">
        <el-card class="selector-card">
          <div class="selector-content">
            <div class="selector-label">
              <el-icon :size="20" color="#409EFF"><Trophy /></el-icon>
              <span>选择考试</span>
            </div>
            <el-select v-model="selectedExamId" placeholder="请选择要查看排名的考试" style="width: 400px" @change="loadRankings">
              <el-option v-for="exam in exams" :key="exam.id" :label="`${exam.name} - ${exam.target_level}`" :value="exam.id" />
            </el-select>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" v-if="examInfo">
      <el-col :span="6" v-for="info in examInfoCards" :key="info.title">
        <el-card class="info-card" shadow="hover">
          <div class="card-content">
            <div class="card-icon" :style="{ background: info.color }">
              <el-icon :size="24" color="#fff">
                <component :is="info.icon" />
              </el-icon>
            </div>
            <div class="card-info">
              <p class="card-title">{{ info.title }}</p>
              <p class="card-value">{{ info.value }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" v-if="statsCards.length > 0">
      <el-col :span="6" v-for="card in statsCards" :key="card.title">
        <el-card class="overview-card" shadow="hover">
          <div class="card-content">
            <div class="card-icon" :style="{ background: card.color }">
              <el-icon :size="24" color="#fff">
                <component :is="card.icon" />
              </el-icon>
            </div>
            <div class="card-info">
              <p class="card-title">{{ card.title }}</p>
              <p class="card-value">{{ card.value }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="ranking-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="18" color="#409EFF"><Rank /></el-icon>
              <span>考试排名榜</span>
            </div>
          </template>
          <el-table :data="rankings" stripe style="width: 100%" v-loading="loading">
            <el-table-column prop="ranking" label="排名" width="100" align="center">
              <template #default="{ row }">
                <div class="ranking-cell">
                  <el-icon v-if="row.ranking === 1" :size="28" color="#FFD700"><GoldMedal /></el-icon>
                  <el-icon v-else-if="row.ranking === 2" :size="28" color="#C0C0C0"><Medal /></el-icon>
                  <el-icon v-else-if="row.ranking === 3" :size="28" color="#CD7F32"><Trophy /></el-icon>
                  <span v-else class="ranking-number">{{ row.ranking }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="member_name" label="会员姓名" width="120" />
            <el-table-column prop="member_level" label="当前等级" width="120" />
            <el-table-column v-for="round in totalRounds" :key="round" :label="`第${round}轮`" width="100" align="center">
              <template #default="{ row }">
                <span :class="getRoundScoreClass(row, round - 1)">{{ row.round_totals[round - 1] ?? '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="total_score" label="总分" width="100" align="center">
              <template #default="{ row }">
                <span class="total-score">{{ row.total_score }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="is_passed" label="是否达标" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_passed ? 'success' : 'danger'" :effect="row.is_passed ? 'dark' : 'light'">
                  {{ row.is_passed ? '达标' : '未达标' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="level_upgraded" label="是否晋级" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.level_upgraded" type="warning" effect="dark">
                  <el-icon :size="12"><Promotion /></el-icon>
                  晋级
                </el-tag>
                <span v-else class="no-upgrade">-</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="18" color="#409EFF"><DataLine /></el-icon>
              <span>前10名考生成绩对比</span>
            </div>
          </template>
          <div ref="barChart" style="height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="18" color="#409EFF"><PieChart /></el-icon>
              <span>达标/未达标人数占比</span>
            </div>
          </template>
          <div ref="pieChart" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getExamRankings, getLevelExams } from '../api'
import * as echarts from 'echarts'

const selectedExamId = ref('')
const exams = ref([])
const rankings = ref([])
const examInfo = ref(null)
const loading = ref(false)

const barChart = ref(null)
const pieChart = ref(null)

let barChartInstance = null
let pieChartInstance = null

const totalRounds = computed(() => {
  if (!examInfo.value) return []
  const rounds = examInfo.value.total_rounds || 0
  return Array.from({ length: rounds }, (_, i) => i + 1)
})

const examInfoCards = computed(() => {
  if (!examInfo.value) return []
  const exam = exams.value.find(e => e.id === selectedExamId.value)
  return [
    { title: '考试名称', value: examInfo.value.exam_name, icon: 'Reading', color: '#409EFF' },
    { title: '目标等级', value: exam?.target_level || '-', icon: 'Medal', color: '#67C23A' },
    { title: '及格分数', value: examInfo.value.pass_score, icon: 'Check', color: '#E6A23C' },
    { title: '总轮数', value: examInfo.value.total_rounds, icon: 'Timer', color: '#F56C6C' }
  ]
})

const statsCards = computed(() => {
  if (rankings.value.length === 0) return []
  const total = rankings.value.length
  const passed = rankings.value.filter(r => r.is_passed).length
  const upgraded = rankings.value.filter(r => r.level_upgraded).length
  const passRate = total > 0 ? ((passed / total) * 100).toFixed(1) + '%' : '0%'
  return [
    { title: '总报名人数', value: total, icon: 'User', color: '#409EFF' },
    { title: '通过人数', value: passed, icon: 'CircleCheck', color: '#67C23A' },
    { title: '通过率', value: passRate, icon: 'TrendCharts', color: '#E6A23C' },
    { title: '晋级人数', value: upgraded, icon: 'Promotion', color: '#F56C6C' }
  ]
})

const getRoundScoreClass = (row, index) => {
  const score = row.round_totals[index]
  if (score == null) return ''
  const avgPerRound = examInfo.value ? examInfo.value.pass_score / examInfo.value.total_rounds : 0
  if (score >= avgPerRound * 1.2) return 'score-excellent'
  if (score >= avgPerRound) return 'score-good'
  return 'score-poor'
}

const loadExams = async () => {
  try {
    const res = await getLevelExams()
    exams.value = res.data
    if (exams.value.length > 0) {
      selectedExamId.value = exams.value[0].id
      await loadRankings()
    }
  } catch (e) {
    ElMessage.error('加载考试列表失败')
  }
}

const loadRankings = async () => {
  if (!selectedExamId.value) return
  loading.value = true
  try {
    const res = await getExamRankings(selectedExamId.value)
    examInfo.value = {
      exam_name: res.data.exam_name,
      pass_score: res.data.pass_score,
      total_rounds: res.data.total_rounds
    }
    rankings.value = res.data.rankings
    await nextTick()
    renderBarChart()
    renderPieChart()
  } catch (e) {
    ElMessage.error('加载排名数据失败')
  } finally {
    loading.value = false
  }
}

const renderBarChart = () => {
  if (!barChart.value || rankings.value.length === 0) return
  if (!barChartInstance) {
    barChartInstance = echarts.init(barChart.value)
  }
  const top10 = rankings.value.slice(0, 10)
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: top10.map(d => d.member_name),
      axisLabel: { fontSize: 11, rotate: 30 }
    },
    yAxis: { type: 'value', name: '总分' },
    series: [{
      type: 'bar',
      data: top10.map(d => d.total_score),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#83bff6' },
          { offset: 1, color: '#409EFF' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '50%',
      label: {
        show: true,
        position: 'top',
        fontSize: 12,
        fontWeight: 'bold',
        color: '#303133'
      }
    }]
  }
  barChartInstance.setOption(option)
}

const renderPieChart = () => {
  if (!pieChart.value || rankings.value.length === 0) return
  if (!pieChartInstance) {
    pieChartInstance = echarts.init(pieChart.value)
  }
  const passed = rankings.value.filter(r => r.is_passed).length
  const failed = rankings.value.length - passed
  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{c}人 ({d}%)' },
      data: [
        { value: passed, name: '达标', itemStyle: { color: '#67C23A' } },
        { value: failed, name: '未达标', itemStyle: { color: '#F56C6C' } }
      ]
    }]
  }
  pieChartInstance.setOption(option)
}

onMounted(() => {
  loadExams()
  window.addEventListener('resize', () => {
    barChartInstance?.resize()
    pieChartInstance?.resize()
  })
})
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.exam-selector {
  margin-bottom: 0;
}

.selector-card {
  border: none;
}

.selector-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.selector-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.info-card,
.overview-card {
  border: none;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-info {
  flex: 1;
}

.card-title {
  color: #909399;
  font-size: 14px;
  margin-bottom: 5px;
}

.card-value {
  color: #303133;
  font-size: 24px;
  font-weight: bold;
}

.ranking-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.ranking-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
}

.ranking-number {
  font-size: 16px;
  font-weight: bold;
  color: #606266;
}

.total-score {
  font-size: 16px;
  font-weight: bold;
  color: #409EFF;
}

.score-excellent {
  color: #67C23A;
  font-weight: bold;
}

.score-good {
  color: #E6A23C;
  font-weight: bold;
}

.score-poor {
  color: #F56C6C;
}

.no-upgrade {
  color: #C0C4CC;
}

.chart-card {
  margin-bottom: 20px;
}
</style>
