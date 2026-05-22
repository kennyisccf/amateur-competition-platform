import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/Layout.vue'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import Profile from '../views/Profile.vue'          
import component from 'element-plus/es/components/tree-select/src/tree-select-option.mjs'

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
      { path: 'profile', name: 'Profile', component: Profile }            // 个人档案
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router