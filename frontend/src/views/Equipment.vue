<template>
  <div class="page">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="器材类型">
          <el-select v-model="filterForm.type" placeholder="全部" clearable style="width: 150px">
            <el-option label="弓" value="弓" />
            <el-option label="箭" value="箭" />
            <el-option label="护具" value="护具" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px">
            <el-option label="可用" value="可用" />
            <el-option label="借用中" value="借用中" />
            <el-option label="维修中" value="维修中" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetFilter">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
          <el-button type="success" @click="showAddDialog">
            <el-icon><Plus /></el-icon> 添加器材
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="filteredEquipment" stripe border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="器材名称" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="typeTagType(row.type)">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="serial_number" label="器材编号" />
        <el-table-column prop="brand" label="品牌" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="buy_date" label="购置日期" />
      </el-table>
    </el-card>

    <el-dialog v-model="addDialogVisible" title="添加器材" width="500px">
      <el-form :model="addForm" label-width="100px">
        <el-form-item label="器材名称">
          <el-input v-model="addForm.name" placeholder="请输入器材名称" />
        </el-form-item>
        <el-form-item label="器材类型">
          <el-select v-model="addForm.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="弓" value="弓" />
            <el-option label="箭" value="箭" />
            <el-option label="护具" value="护具" />
          </el-select>
        </el-form-item>
        <el-form-item label="器材编号">
          <el-input v-model="addForm.serial_number" placeholder="如 BOW-001" />
        </el-form-item>
        <el-form-item label="品牌">
          <el-input v-model="addForm.brand" placeholder="请输入品牌" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="addForm.status" style="width: 100%">
            <el-option label="可用" value="可用" />
            <el-option label="维修中" value="维修中" />
          </el-select>
        </el-form-item>
        <el-form-item label="购置日期">
          <el-date-picker v-model="addForm.buy_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addEquipment">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getEquipment, createEquipment } from '../api'

const equipment = ref([])
const addDialogVisible = ref(false)
const filterForm = ref({ type: '', status: '' })
const addForm = ref({
  name: '',
  type: '',
  serial_number: '',
  brand: '',
  status: '可用',
  buy_date: ''
})

const filteredEquipment = computed(() => {
  return equipment.value.filter(item => {
    if (filterForm.value.type && item.type !== filterForm.value.type) return false
    if (filterForm.value.status && item.status !== filterForm.value.status) return false
    return true
  })
})

const typeTagType = (type) => {
  const map = { '弓': 'primary', '箭': 'success', '护具': 'warning' }
  return map[type] || 'info'
}

const statusTagType = (status) => {
  const map = { '可用': 'success', '借用中': 'warning', '维修中': 'danger' }
  return map[status] || 'info'
}

const loadData = async () => {
  try {
    const res = await getEquipment()
    equipment.value = res.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
}

const resetFilter = () => {
  filterForm.value = { type: '', status: '' }
  loadData()
}

const showAddDialog = () => {
  addForm.value = {
    name: '',
    type: '',
    serial_number: '',
    brand: '',
    status: '可用',
    buy_date: new Date().toISOString().split('T')[0]
  }
  addDialogVisible.value = true
}

const addEquipment = async () => {
  if (!addForm.value.name || !addForm.value.type || !addForm.value.serial_number) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await createEquipment(addForm.value)
    ElMessage.success('添加成功')
    addDialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

onMounted(loadData)
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
.table-card {
  margin-top: 0;
}
</style>
