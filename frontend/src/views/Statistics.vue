<template>
  <div class="page">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="4.8" v-for="card in overviewCards" :key="card.title">
        <el-card class="overview-card" shadow="hover">
          <div class="card-content">
            <div class="card-icon" :style="{ background: card.color }">
              <el-icon :size="28" color="#fff">
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
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="18" color="#409EFF"><Goods /></el-icon>
              <span>器材使用率排行</span>
            </div>
          </template>
          <div ref="usageChart" style="height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="18" color="#409EFF"><User /></el-icon>
              <span>会员等级分布</span>
            </div>
          </template>
          <div ref="levelChart" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="18" color="#409EFF"><TrendCharts /></el-icon>
              <span>成绩进步曲线</span>
              <el-select v-model="selectedMember" placeholder="选择会员" style="margin-left: 15px; width: 150px" @change="loadProgress">
                <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
              </el-select>
            </div>
          </template>
          <div ref="progressChart" style="height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <el-icon :size="18" color="#409EFF"><DataLine /></el-icon>
              <span>热门箭靶距离</span>
            </div>
          </template>
          <div ref="distanceChart" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getEquipmentUsage, getLevelDistribution, getMemberProgress, getDistancePopularity, getOverview, getMembers } from '../api'
import * as echarts from 'echarts'

const usageChart = ref(null)
const levelChart = ref(null)
const progressChart = ref(null)
const distanceChart = ref(null)
const selectedMember = ref('')
const members = ref([])
const progressData = ref([])

let usageChartInstance = null
let levelChartInstance = null
let progressChartInstance = null
let distanceChartInstance = null

const overview = ref({
  member_count: 0,
  equipment_count: 0,
  borrowed_count: 0,
  score_count: 0,
  cert_count: 0
})

const overviewCards = [
  { title: '会员总数', value: overview.value.member_count, icon: 'User', color: '#409EFF' },
  { title: '器材总数', value: overview.value.equipment_count, icon: 'Goods', color: '#67C23A' },
  { title: '借用中', value: overview.value.borrowed_count, icon: 'Tickets', color: '#E6A23C' },
  { title: '成绩记录', value: overview.value.score_count, icon: 'EditPen', color: '#F56C6C' },
  { title: '证书数量', value: overview.value.cert_count, icon: 'Medal', color: '#909399' }
]

const loadData = async () => {
  try {
    const [res1, res2, res3, res4, res5] = await Promise.all([
      getOverview(),
      getEquipmentUsage(),
      getLevelDistribution(),
      getDistancePopularity(),
      getMembers()
    ])
    overview.value = res1.data
    overviewCards[0].value = res1.data.member_count
    overviewCards[1].value = res1.data.equipment_count
    overviewCards[2].value = res1.data.borrowed_count
    overviewCards[3].value = res1.data.score_count
    overviewCards[4].value = res1.data.cert_count
    members.value = res5.data
    if (members.value.length > 0) {
      selectedMember.value = members.value[0].id
    }
    await nextTick()
    renderUsageChart(res2.data)
    renderLevelChart(res3.data)
    renderDistanceChart(res4.data)
    loadProgress()
  } catch (e) {
    ElMessage.error('加载统计数据失败')
  }
}

const loadProgress = async () => {
  if (!selectedMember.value) return
  try {
    const res = await getMemberProgress(selectedMember.value)
    progressData.value = res.data
    await nextTick()
    renderProgressChart()
  } catch (e) {
    console.error(e)
  }
}

const renderUsageChart = (data) => {
  if (!usageChart.value) return
  if (!usageChartInstance) {
    usageChartInstance = echarts.init(usageChart.value)
  }
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: '使用次数' },
    yAxis: {
      type: 'category',
      data: data.slice(0, 10).map(d => `${d.name} (${d.serial_number})`).reverse(),
      axisLabel: { fontSize: 11 }
    },
    series: [{
      type: 'bar',
      data: data.slice(0, 10).map(d => d.usage_count).reverse(),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#83bff6' },
          { offset: 1, color: '#409EFF' }
        ]),
        borderRadius: [0, 4, 4, 0]
      }
    }]
  }
  usageChartInstance.setOption(option)
}

const renderLevelChart = (data) => {
  if (!levelChart.value) return
  if (!levelChartInstance) {
    levelChartInstance = echarts.init(levelChart.value)
  }
  const colors = ['#909399', '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#9c27b0']
  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c}人 ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{c}人' },
      data: data.map((d, i) => ({ value: d.count, name: d.level, itemStyle: { color: colors[i] } }))
    }]
  }
  levelChartInstance.setOption(option)
}

const renderProgressChart = () => {
  if (!progressChart.value || progressData.value.length === 0) return
  if (!progressChartInstance) {
    progressChartInstance = echarts.init(progressChart.value)
  }
  const data = progressData.value
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['单次成绩', '平均成绩'], top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: { type: 'category', data: data.map(d => d.date), axisLabel: { fontSize: 11 } },
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
  progressChartInstance.setOption(option)
}

const renderDistanceChart = (data) => {
  if (!distanceChart.value) return
  if (!distanceChartInstance) {
    distanceChartInstance = echarts.init(distanceChart.value)
  }
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['使用次数', '平均成绩'], top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: { type: 'category', data: data.map(d => d.distance + '米') },
    yAxis: [
      { type: 'value', name: '使用次数' },
      { type: 'value', name: '平均成绩' }
    ],
    series: [
      {
        name: '使用次数',
        type: 'bar',
        data: data.map(d => d.count),
        itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] },
        barWidth: '40%'
      },
      {
        name: '平均成绩',
        type: 'line',
        yAxisIndex: 1,
        data: data.map(d => d.avg_score),
        smooth: true,
        itemStyle: { color: '#F56C6C' },
        lineStyle: { width: 3 }
      }
    ]
  }
  distanceChartInstance.setOption(option)
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', () => {
    usageChartInstance?.resize()
    levelChartInstance?.resize()
    progressChartInstance?.resize()
    distanceChartInstance?.resize()
  })
})
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.stat-cards {
  margin-bottom: 0;
}
.overview-card {
  border: none;
}
.card-content {
  display: flex;
  align-items: center;
  gap: 15px;
}
.card-icon {
  width: 60px;
  height: 60px;
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
  font-size: 28px;
  font-weight: bold;
}
.chart-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
</style>
