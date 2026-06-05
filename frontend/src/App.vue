<template>
  <el-container class="app-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="32" color="#409EFF"><Aim /></el-icon>
        <h2>射箭馆管理系统</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="menu"
        background-color="#1f2d3d"
        text-color="#fff"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/equipment">
          <el-icon><Goods /></el-icon>
          <span>器材台账</span>
        </el-menu-item>
        <el-menu-item index="/borrow">
          <el-icon><Tickets /></el-icon>
          <span>借用记录</span>
        </el-menu-item>
        <el-menu-item index="/scores">
          <el-icon><EditPen /></el-icon>
          <span>成绩录入</span>
        </el-menu-item>
        <el-sub-menu index="exams-group">
          <template #title>
            <el-icon><Medal /></el-icon>
            <span>等级考试管理</span>
          </template>
          <el-menu-item index="/exams">
            <el-icon><SetUp /></el-icon>
            <span>考试设置</span>
          </el-menu-item>
          <el-menu-item index="/exam-registrations">
            <el-icon><User /></el-icon>
            <span>报名管理</span>
          </el-menu-item>
          <el-menu-item index="/exam-scores">
            <el-icon><Edit /></el-icon>
            <span>轮次成绩录入</span>
          </el-menu-item>
          <el-menu-item index="/exam-rankings">
            <el-icon><Trophy /></el-icon>
            <span>考试排名榜</span>
          </el-menu-item>
          <el-menu-item index="/exam-equipment">
            <el-icon><Tools /></el-icon>
            <span>器材保障看板</span>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-title">{{ pageTitle }}</div>
        <div class="header-user">
          <el-avatar :size="32" style="background-color: #409EFF">管</el-avatar>
          <span style="margin-left: 10px">管理员</span>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/equipment': '器材台账管理',
    '/borrow': '借用记录管理',
    '/scores': '训练成绩录入',
    '/exams': '考试设置管理',
    '/exam-registrations': '考试报名管理',
    '/exam-scores': '轮次成绩录入',
    '/exam-rankings': '考试排名榜',
    '/exam-equipment': '器材保障看板',
    '/statistics': '数据统计分析'
  }
  return titles[route.path] || '射箭馆管理系统'
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.app-container {
  height: 100%;
}

.sidebar {
  background-color: #1f2d3d;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #304156;
}

.logo h2 {
  color: #fff;
  font-size: 18px;
  margin-top: 10px;
}

.menu {
  border-right: none;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  margin-left: 220px;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-user {
  display: flex;
  align-items: center;
  color: #606266;
}

.main {
  margin-left: 220px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
  padding: 20px;
}
</style>
