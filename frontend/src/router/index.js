import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/Layout.vue'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import Profile from '../views/Profile.vue'          
// 新增导入赛事页面
import EventDetail from '../views/EventDetail.vue'
import EventRegister from '../views/EventRegister.vue'

const routes = [
  {
    path: '/login',
    component: Login
  },
  {
    path: '/register',
    component: Register
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    children: [
      { path: 'home', component: Home },
      { path: 'profile', name: 'Profile', component: Profile },
      // 新增赛事相关路由
      { path: 'event-detail/:id', name: 'EventDetail', component: EventDetail },
      { path: 'event-register/:id', name: 'EventRegister', component: EventRegister }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router