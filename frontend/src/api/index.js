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

export const getCertificates = () => request.get('/certificates')
export const createCertificate = (data) => request.post('/certificates', data)

export const getEquipmentUsage = () => request.get('/statistics/equipment-usage')
export const getLevelDistribution = () => request.get('/statistics/level-distribution')
export const getMemberProgress = (memberId) => request.get(`/statistics/progress/${memberId}`)
export const getDistancePopularity = () => request.get('/statistics/distance-popularity')
export const getOverview = () => request.get('/statistics/overview')

export default request
