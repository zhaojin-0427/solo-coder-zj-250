<template>
  <div class="page">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px">
            <el-option label="借用中" value="借用中" />
            <el-option label="已归还" value="已归还" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetFilter">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
          <el-button type="success" @click="showBorrowDialog">
            <el-icon><Plus /></el-icon> 新建借用
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="filteredRecords" stripe border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="member_name" label="会员" />
        <el-table-column prop="equipment_name" label="器材名称" />
        <el-table-column prop="equipment_serial" label="器材编号" />
        <el-table-column prop="borrow_time" label="借用时间" />
        <el-table-column prop="expected_return" label="预期归还" />
        <el-table-column prop="actual_return" label="实际归还" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === '借用中' ? 'warning' : 'success'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === '借用中'"
              type="primary"
              size="small"
              @click="returnEquipment(row.id)"
            >
              归还
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="borrowDialogVisible" title="新建借用" width="500px">
      <el-form :model="borrowForm" label-width="100px">
        <el-form-item label="会员">
          <el-select v-model="borrowForm.member_id" placeholder="请选择会员" style="width: 100%">
            <el-option v-for="m in members" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="器材">
          <el-select v-model="borrowForm.equipment_id" placeholder="请选择器材" style="width: 100%">
            <el-option
              v-for="e in availableEquipment"
              :key="e.id"
              :label="`${e.name} (${e.serial_number})`"
              :value="e.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="借用时间">
          <el-date-picker
            v-model="borrowForm.borrow_time"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="预期归还">
          <el-date-picker
            v-model="borrowForm.expected_return"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="borrowDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createBorrow">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBorrowRecords, createBorrowRecord, returnEquipment as returnEq, getEquipment, getMembers } from '../api'

const records = ref([])
const equipment = ref([])
const members = ref([])
const borrowDialogVisible = ref(false)
const filterForm = ref({ status: '' })
const borrowForm = ref({
  member_id: '',
  equipment_id: '',
  borrow_time: '',
  expected_return: ''
})

const filteredRecords = computed(() => {
  if (!filterForm.value.status) return records.value
  return records.value.filter(r => r.status === filterForm.value.status)
})

const availableEquipment = computed(() => {
  return equipment.value.filter(e => e.status === '可用')
})

const loadData = async () => {
  try {
    const [res1, res2, res3] = await Promise.all([
      getBorrowRecords(),
      getEquipment(),
      getMembers()
    ])
    records.value = res1.data
    equipment.value = res2.data
    members.value = res3.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
}

const resetFilter = () => {
  filterForm.value = { status: '' }
  loadData()
}

const showBorrowDialog = () => {
  const now = new Date()
  const expected = new Date(now.getTime() + 4 * 60 * 60 * 1000)
  borrowForm.value = {
    member_id: '',
    equipment_id: '',
    borrow_time: now.toISOString().replace('T', ' ').substring(0, 19),
    expected_return: expected.toISOString().replace('T', ' ').substring(0, 19)
  }
  borrowDialogVisible.value = true
}

const createBorrow = async () => {
  if (!borrowForm.value.member_id || !borrowForm.value.equipment_id) {
    ElMessage.warning('请选择会员和器材')
    return
  }
  try {
    await createBorrowRecord(borrowForm.value)
    ElMessage.success('借用登记成功')
    borrowDialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('借用登记失败')
  }
}

const returnEquipment = async (id) => {
  try {
    await ElMessageBox.confirm('确认归还该器材吗？', '提示', { type: 'warning' })
    await returnEq(id, {})
    ElMessage.success('归还成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('归还失败')
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
</style>
