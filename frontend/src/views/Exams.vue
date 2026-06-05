<template>
  <div class="page">
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="等级考试" name="exams">
        <el-card class="card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>考试列表</span>
              <el-button type="success" @click="showAddExamDialog">
                <el-icon><Plus /></el-icon> 创建考试
              </el-button>
            </div>
          </template>
          <el-table :data="exams" stripe border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="考试名称" />
            <el-table-column prop="target_level" label="目标等级" width="120">
              <template #default="{ row }">
                <el-tag type="warning">{{ row.target_level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="exam_date" label="考试日期" />
            <el-table-column prop="exam_location" label="考试地点" />
            <el-table-column prop="pass_score" label="及格分数" width="100" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.status === '已完成' ? 'success' : 'primary'">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="showCertDialog(row)">
                  <el-icon><Medal /></el-icon> 颁发证书
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

    <el-dialog v-model="addExamDialogVisible" title="创建等级考试" width="500px">
      <el-form :model="addExamForm" label-width="100px">
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
        <el-form-item label="考试日期">
          <el-date-picker
            v-model="addExamForm.exam_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="考试地点">
          <el-input v-model="addExamForm.exam_location" placeholder="主馆A区/户外靶场" />
        </el-form-item>
        <el-form-item label="及格分数">
          <el-input-number v-model="addExamForm.pass_score" :min="60" :max="150" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="addExamForm.status" style="width: 100%">
            <el-option label="报名中" value="报名中" />
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addExamDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createExam">确定</el-button>
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
          <el-input-number v-model="certForm.score" :min="0" :max="150" style="width: 100%" />
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
import { ElMessage } from 'element-plus'
import { getLevelExams, createLevelExam, getCertificates, createCertificate, getMembers } from '../api'

const activeTab = ref('exams')
const exams = ref([])
const certificates = ref([])
const members = ref([])
const addExamDialogVisible = ref(false)
const certDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const selectedExam = ref(null)
const previewCert = ref(null)

const addExamForm = ref({
  name: '',
  target_level: '初级射手',
  exam_date: '',
  exam_location: '',
  pass_score: 100,
  status: '报名中'
})

const certForm = ref({
  member_id: '',
  exam_id: '',
  level: '初级射手',
  score: 0,
  issue_date: ''
})

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
  addExamForm.value = {
    name: '',
    target_level: '初级射手',
    exam_date: new Date().toISOString().split('T')[0],
    exam_location: '',
    pass_score: 100,
    status: '报名中'
  }
  addExamDialogVisible.value = true
}

const createExam = async () => {
  if (!addExamForm.value.name) {
    ElMessage.warning('请填写考试名称')
    return
  }
  try {
    await createLevelExam(addExamForm.value)
    ElMessage.success('考试创建成功')
    addExamDialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('创建失败')
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
