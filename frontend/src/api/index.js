import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 5000
})

export const getMembers = () => request.get('/members')
export const createMember = (data) => request.post('/members', data)

export const getEquipment = () => request.get('/equipment')
export const createEquipment = (data) => request.post('/equipment', data)
export const updateEquipment = (id, data) => request.put(`/equipment/${id}`, data)

export const getBorrowRecords = () => request.get('/borrow-records')
export const createBorrowRecord = (data) => request.post('/borrow-records', data)
export const returnEquipment = (id, data) => request.put(`/borrow-records/${id}/return`, data)

export const getScores = () => request.get('/scores')
export const createScore = (data) => request.post('/scores', data)
export const deleteScore = (id) => request.delete(`/scores/${id}`)

export const getLevelExams = () => request.get('/level-exams')
export const createLevelExam = (data) => request.post('/level-exams', data)
export const updateLevelExam = (id, data) => request.put(`/level-exams/${id}`, data)
export const deleteLevelExam = (id) => request.delete(`/level-exams/${id}`)
export const getLevelExamDetail = (id) => request.get(`/level-exams/${id}`)

export const getExamRegistrations = (params) => request.get('/exam-registrations', { params })
export const checkRegistrationEligibility = (data) => request.post('/exam-registrations/check-eligibility', data)
export const createExamRegistration = (data) => request.post('/exam-registrations', data)
export const updateExamRegistration = (id, data) => request.put(`/exam-registrations/${id}`, data)
export const deleteExamRegistration = (id) => request.delete(`/exam-registrations/${id}`)
export const finalizeRegistration = (id) => request.post(`/exam-registrations/${id}/finalize`)

export const getExamRoundScores = (params) => request.get('/exam-round-scores', { params })
export const createExamRoundScore = (data) => request.post('/exam-round-scores', data)
export const updateExamRoundScore = (id, data) => request.put(`/exam-round-scores/${id}`, data)
export const deleteExamRoundScore = (id) => request.delete(`/exam-round-scores/${id}`)

export const getExamRankings = (examId) => request.get(`/exam-rankings/${examId}`)

export const getCertificates = () => request.get('/certificates')
export const createCertificate = (data) => request.post('/certificates', data)
export const batchIssueCertificates = (data) => request.post('/certificates/batch-issue', data)

export const getExamEquipmentReservations = (params) => request.get('/exam-equipment-reservations', { params })
export const getAvailableEquipmentForExam = (params) => request.get('/exam-equipment-reservations/available', { params })
export const batchReserveEquipment = (data) => request.post('/exam-equipment-reservations/batch-reserve', data)
export const updateExamEquipmentReservation = (id, data) => request.put(`/exam-equipment-reservations/${id}`, data)
export const deleteExamEquipmentReservation = (id) => request.delete(`/exam-equipment-reservations/${id}`)

export const getEquipmentUsage = () => request.get('/statistics/equipment-usage')
export const getLevelDistribution = () => request.get('/statistics/level-distribution')
export const getLevelDistributionWithExams = () => request.get('/statistics/level-distribution-with-exams')
export const getMemberProgress = (memberId) => request.get(`/statistics/progress/${memberId}`)
export const getMemberExamProgress = (memberId) => request.get(`/statistics/exam-progress/${memberId}`)
export const getDistancePopularity = () => request.get('/statistics/distance-popularity')
export const getOverview = () => request.get('/statistics/overview')

export default request
