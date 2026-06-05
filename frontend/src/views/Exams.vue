<template>
  <div class="page">
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="考试设置" name="exams">
        <el-card class="card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>等级考试列表</span>
              <el-button type="success" @click="showAddExamDialog">
                <el-icon><Plus /></el-icon> 创建考试
              </el-button>
            </div>
          </template>
          <el-table :data="exams" stripe border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="考试名称" min-width="200" />
            <el-table-column prop="target_level" label="目标等级" width="120">
              <template #default="{ row }">
                <el-tag type="warning">{{ row.target_level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="distance_group" label="距离组" width="100" />
            <el-table-column prop="bow_type_restriction" label="弓型限制" width="150" show-overflow-tooltip />
            <el-table-column prop="registration_capacity" label="报名容量" width="100">
              <template #default="{ row }">
                {{ row.registered_count || 0 }}/{{ row.registration_capacity }}
              </template>
            </el-table-column>
            <el-table-column prop="exam_date" label="考试日期" width="120" />
            <el-table-column prop="registration_deadline" label="报名截止" width="120" />
            <el-table-column prop="pass_score" label="及格分数" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="showEditExamDialog(row)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-button type="primary" size="small" @click="showCertBatchDialog(row)">
                  <el-icon><Medal /></el-icon> 批量发证
                </el-button>
                <el-button type="danger" size="small" @click="deleteExam(row)">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="电子证书" name="certificates">
        <el-card class="card">
          <template #header>
            <span>已颁发证书</span>
          </template>
          <el-table :data="certificates" stripe border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="member_name" label="持证人" />
            <el-table-column prop="exam_name" label="考试名称" />
            <el-table-column prop="level" label="等级" width="120">
              <template #default="{ row }">
                <el-tag type="warning">{{ row.level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="成绩" width="100" />
            <el-table-column prop="issue_date" label="颁发日期" />
            <el-table-column prop="certificate_number" label="证书编号" width="220">
              <template #default="{ row }">
                <el-tag type="success">{{ row.certificate_number }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="showCertPreview(row)">
                  <el-icon><View /></el-icon> 预览
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="addExamDialogVisible" title="创建等级考试" width="600px">
      <el-form :model="addExamForm" label-width="120px">
        <el-form-item label="考试名称">
          <el-input v-model="addExamForm.name" placeholder="如：2024年夏季等级考试" />
        </el-form-item>
        <el-form-item label="目标等级">
          <el-select v-model="addExamForm.target_level" style="width: 100%">
            <el-option label="初级射手" value="初级射手" />
            <el-option label="中级射手" value="中级射手" />
            <el-option label="高级射手" value="高级射手" />
            <el-option label="精英射手" value="精英射手" />
            <el-option label="大师射手" value="大师射手" />
          </el-select>
        </el-form-item>
        <el-form-item label="距离组">
          <el-select v-model="addExamForm.distance_group" style="width: 100%">
            <el-option label="10米" value="10米" />
            <el-option label="18米" value="18米" />
            <el-option label="30米" value="30米" />
            <el-option label="50米" value="50米" />
            <el-option label="70米" value="70米" />
          </el-select>
        </el-form-item>
        <el-form-item label="弓型限制">
          <el-select v-model="addExamForm.bow_type_restriction" multiple collapse-tags style="width: 100%" placeholder="不填则不限制">
            <el-option label="反曲弓" value="反曲弓" />
            <el-option label="复合弓" value="复合弓" />
            <el-option label="传统弓" value="传统弓" />
            <el-option label="美式猎弓" value="美式猎弓" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="报名容量">
              <el-input-number v-model="addExamForm.registration_capacity" :min="1" :max="200" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="及格分数">
              <el-input-number v-model="addExamForm.pass_score" :min="60" :max="300" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="考试日期">
              <el-date-picker
                v-model="addExamForm.exam_date"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报名截止">
              <el-date-picker
                v-model="addExamForm.registration_deadline"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="每轮箭数">
              <el-input-number v-model="addExamForm.arrows_per_round" :min="3" :max="12" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="总轮数">
              <el-input-number v-model="addExamForm.total_rounds" :min="1" :max="24" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="考试地点">
          <el-input v-model="addExamForm.exam_location" placeholder="主馆A区/户外靶场" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="addExamForm.status" style="width: 100%">
            <el-option label="报名中" value="报名中" />
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已取消" value="已取消" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addExamDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveExam">{{ isEditMode ? '保存修改' : '创建考试' }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="certBatchDialogVisible" title="批量颁发电子证书" width="500px">
      <div v-if="selectedExam" style="margin-bottom: 20px">
        <el-alert
          :title="`考试：${selectedExam.name}，目标等级：${selectedExam.target_level}，及格分数：${selectedExam.pass_score}`"
          type="info"
          :closable="false"
        />
      </div>
      <el-table :data="passedRegistrations" stripe border @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="member_name" label="考生姓名" />
        <el-table-column prop="total_score" label="考试成绩" width="100" />
        <el-table-column prop="ranking" label="排名" width="80" />
        <el-table-column label="是否达标" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_passed ? 'success' : 'danger'">{{ row.is_passed ? '达标' : '未达标' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="已发证" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.has_certificate" type="info">已发</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
      <el-form :model="certBatchForm" label-width="100px" style="margin-top: 20px">
        <el-form-item label="颁发日期">
          <el-date-picker
            v-model="certBatchForm.issue_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="certBatchDialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="selectedRegistrations.length === 0" @click="batchIssueCerts">
          批量颁发 ({{ selectedRegistrations.length }}人)
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="certDialogVisible" title="颁发电子证书" width="500px">
      <el-form :model="certForm" label-width="100px">
        <el-form-item label="会员">
          <el-select v-model="certForm.member_id" placeholder="请选择会员" style="width: 100%">
            <el-option v-for="m in members" :key="m.id" :label="`${m.name} (${m.tech_level})`" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="certForm.level" style="width: 100%">
            <el-option label="初级射手" value="初级射手" />
            <el-option label="中级射手" value="中级射手" />
            <el-option label="高级射手" value="高级射手" />
            <el-option label="精英射手" value="精英射手" />
            <el-option label="大师射手" value="大师射手" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试成绩">
          <el-input-number v-model="certForm.score" :min="0" :max="300" style="width: 100%" />
        </el-form-item>
        <el-form-item label="颁发日期">
          <el-date-picker
            v-model="certForm.issue_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="certDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="issueCertificate">颁发证书</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="previewDialogVisible" title="电子证书预览" width="600px">
      <div v-if="previewCert" class="certificate">
        <div class="cert-header">
          <h1>射箭技术等级证书</h1>
          <p class="cert-subtitle">ARCHERY TECHNICAL LEVEL CERTIFICATE</p>
        </div>
        <div class="cert-body">
          <p class="cert-text">兹证明</p>
          <h2 class="cert-name">{{ previewCert.member_name }}</h2>
          <p class="cert-text">
            在 {{ previewCert.exam_name }} 中，成绩达到
          </p>
          <el-tag class="cert-level" type="warning" size="large">{{ previewCert.level }}</el-tag>
          <p class="cert-text">
            技术等级标准，特发此证。
          </p>
          <div class="cert-info">
            <div class="info-row">
              <span>考试成绩：</span>
              <span class="highlight">{{ previewCert.score }} 环</span>
            </div>
            <div class="info-row">
              <span>证书编号：</span>
              <span class="highlight">{{ previewCert.certificate_number }}</span>
            </div>
            <div class="info-row">
              <span>颁发日期：</span>
              <span class="highlight">{{ previewCert.issue_date }}</span>
            </div>
          </div>
        </div>
        <div class="cert-footer">
          <p>射箭馆管理中心 颁发</p>
          <div class="seal">
            <p>专</p>
            <p>用</p>
            <p>章</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getLevelExams, createLevelExam, updateLevelExam, deleteLevelExam, getLevelExamDetail,
  getCertificates, createCertificate, batchIssueCertificates, getMembers,
  getExamRegistrations, getExamRankings
} from '../api'

const activeTab = ref('exams')
const exams = ref([])
const certificates = ref([])
const members = ref([])
const passedRegistrations = ref([])
const selectedRegistrations = ref([])

const addExamDialogVisible = ref(false)
const certDialogVisible = ref(false)
const certBatchDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const selectedExam = ref(null)
const previewCert = ref(null)
const isEditMode = ref(false)
const editingExamId = ref(null)

const addExamForm = ref({
  name: '',
  target_level: '初级射手',
  exam_date: '',
  exam_location: '',
  pass_score: 100,
  status: '报名中',
  exam_project: '射箭',
  distance_group: '18米',
  bow_type_restriction: '',
  registration_capacity: 50,
  registration_deadline: '',
  arrows_per_round: 6,
  total_rounds: 12
})

const certForm = ref({
  member_id: '',
  exam_id: '',
  level: '初级射手',
  score: 0,
  issue_date: ''
})

const certBatchForm = ref({
  issue_date: ''
})

const getStatusType = (status) => {
  const types = {
    '报名中': 'primary',
    '进行中': 'warning',
    '已完成': 'success',
    '已取消': 'info'
  }
  return types[status] || 'info'
}

const loadData = async () => {
  try {
    const [res1, res2, res3] = await Promise.all([
      getLevelExams(),
      getCertificates(),
      getMembers()
    ])
    exams.value = res1.data
    certificates.value = res2.data
    members.value = res3.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
}

const showAddExamDialog = () => {
  isEditMode.value = false
  editingExamId.value = null
  addExamForm.value = {
    name: '',
    target_level: '初级射手',
    exam_date: new Date().toISOString().split('T')[0],
    exam_location: '',
    pass_score: 100,
    status: '报名中',
    exam_project: '射箭',
    distance_group: '18米',
    bow_type_restriction: [],
    registration_capacity: 50,
    registration_deadline: new Date().toISOString().split('T')[0],
    arrows_per_round: 6,
    total_rounds: 12
  }
  addExamDialogVisible.value = true
}

const showEditExamDialog = async (row) => {
  try {
    const res = await getLevelExamDetail(row.id)
    isEditMode.value = true
    editingExamId.value = row.id
    const data = res.data
    addExamForm.value = {
      ...data,
      bow_type_restriction: data.bow_type_restriction ? data.bow_type_restriction.split(',') : []
    }
    addExamDialogVisible.value = true
  } catch (e) {
    ElMessage.error('加载考试详情失败')
  }
}

const saveExam = async () => {
  if (!addExamForm.value.name) {
    ElMessage.warning('请填写考试名称')
    return
  }
  if (!addExamForm.value.distance_group) {
    ElMessage.warning('请选择距离组')
    return
  }
  if (!addExamForm.value.exam_date || !addExamForm.value.registration_deadline) {
    ElMessage.warning('请选择考试日期和报名截止日期')
    return
  }
  try {
    const formData = {
      ...addExamForm.value,
      bow_type_restriction: Array.isArray(addExamForm.value.bow_type_restriction) 
        ? addExamForm.value.bow_type_restriction.join(',') 
        : addExamForm.value.bow_type_restriction
    }
    if (isEditMode.value) {
      await updateLevelExam(editingExamId.value, formData)
      ElMessage.success('考试更新成功')
    } else {
      await createLevelExam(formData)
      ElMessage.success('考试创建成功')
    }
    addExamDialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const deleteExam = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该考试吗？相关报名、成绩、预约和证书都将被删除。', '确认删除', {
      type: 'warning'
    })
    await deleteLevelExam(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const showCertBatchDialog = async (exam) => {
  selectedExam.value = exam
  certBatchForm.value.issue_date = new Date().toISOString().split('T')[0]
  selectedRegistrations.value = []
  try {
    const [res1, res2] = await Promise.all([
      getExamRankings(exam.id),
      getCertificates()
    ])
    const rankings = res1.data.rankings
    const certMap = new Map()
    res2.data.forEach(c => {
      if (c.exam_id === exam.id) {
        certMap.set(c.member_id, true)
      }
    })
    passedRegistrations.value = rankings
      .filter(r => r.is_passed)
      .map(r => ({
        ...r,
        has_certificate: certMap.has(r.member_id)
      }))
    certBatchDialogVisible.value = true
  } catch (e) {
    ElMessage.error('加载考生数据失败')
  }
}

const handleSelectionChange = (val) => {
  selectedRegistrations.value = val.filter(v => !v.has_certificate)
}

const batchIssueCerts = async () => {
  if (selectedRegistrations.value.length === 0) {
    ElMessage.warning('请选择要颁发证书的考生')
    return
  }
  try {
    const res = await batchIssueCertificates({
      exam_id: selectedExam.value.id,
      registration_ids: selectedRegistrations.value.map(r => r.registration_id),
      issue_date: certBatchForm.value.issue_date
    })
    ElMessage.success(`成功颁发 ${res.data.count} 张证书`)
    certBatchDialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('批量颁发失败')
  }
}

const showCertDialog = (exam) => {
  selectedExam.value = exam
  certForm.value = {
    member_id: '',
    exam_id: exam.id,
    level: exam.target_level,
    score: exam.pass_score,
    issue_date: new Date().toISOString().split('T')[0]
  }
  certDialogVisible.value = true
}

const issueCertificate = async () => {
  if (!certForm.value.member_id) {
    ElMessage.warning('请选择会员')
    return
  }
  try {
    const res = await createCertificate(certForm.value)
    ElMessage.success(`证书颁发成功！编号：${res.data.certificate_number}`)
    certDialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('颁发失败')
  }
}

const showCertPreview = (cert) => {
  previewCert.value = cert
  previewDialogVisible.value = true
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
.certificate {
  background: linear-gradient(135deg, #fff 0%, #f8f4e8 100%);
  border: 3px solid #b8860b;
  padding: 40px;
  text-align: center;
  position: relative;
}
.cert-header {
  margin-bottom: 30px;
}
.cert-header h1 {
  color: #b8860b;
  font-size: 28px;
  margin-bottom: 5px;
}
.cert-subtitle {
  color: #999;
  font-size: 14px;
  letter-spacing: 3px;
}
.cert-body {
  margin-bottom: 30px;
}
.cert-text {
  color: #666;
  font-size: 16px;
  margin: 10px 0;
}
.cert-name {
  color: #333;
  font-size: 32px;
  margin: 15px 0;
  font-weight: bold;
}
.cert-level {
  margin: 15px 0;
  font-size: 20px;
  padding: 8px 20px;
}
.cert-info {
  margin-top: 30px;
  text-align: left;
  padding: 20px;
  background: rgba(184, 134, 11, 0.05);
  border-radius: 8px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  color: #666;
}
.highlight {
  color: #b8860b;
  font-weight: bold;
}
.cert-footer {
  margin-top: 30px;
  position: relative;
}
.cert-footer p {
  color: #666;
}
.seal {
  position: absolute;
  right: 30px;
  bottom: 0;
  width: 80px;
  height: 80px;
  border: 3px solid #d9534f;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #d9534f;
  font-weight: bold;
  transform: rotate(-15deg);
  opacity: 0.8;
}
.seal p {
  color: #d9534f;
  margin: 2px 0;
}
</style>
