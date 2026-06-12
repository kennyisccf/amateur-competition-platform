import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/Layout.vue'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import Profile from '../views/Profile.vue'          
import Notifications from '../views/Notifications.vue'
import Friends from '../views/Friends.vue'
import EventDetail from '../views/EventDetail.vue'
import EventRegister from '../views/EventRegister.vue'
import CreateCompetition from '../views/CreateCompetition.vue'
import Workbench from '../views/Workbench.vue'
import AdminReview from '../views/AdminReview.vue'
import RegistrationManage from '../views/RegistrationManage.vue'
import CompetitionEdit from '../views/CompetitionEdit.vue' 

const routes = [
  {
    path: '/login',
    component: Login,
    meta: { public: true }
  },
  {
    path: '/register',
    component: Register,
    meta: { public: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/home',
    meta: { requiresAuth: true },
    children: [
      { path: 'home', component: Home },
      { path: 'profile', name: 'Profile', component: Profile },
      { path: 'notifications', name: 'Notifications', component: Notifications },
      { path: 'friends', name: 'Friends', component: Friends },
      { path: 'event-detail/:id', name: 'EventDetail', component: EventDetail },
      { path: 'event-register/:id', name: 'EventRegister', component: EventRegister, meta: { roles: ['PLAYER', 'ORGANIZER', 'ADMIN'] } },
      { path: 'create', name: 'CreateCompetition', component: CreateCompetition, meta: { roles: ['PLAYER', 'ORGANIZER', 'ADMIN'] } },
      { path: 'workbench', name: 'Workbench', component: Workbench, meta: { roles: ['PLAYER', 'ORGANIZER', 'ADMIN'] } },
      { path: 'registration-manage', name: 'RegistrationManage', component: RegistrationManage, meta: { roles: ['PLAYER', 'ORGANIZER', 'ADMIN'] } },
      { path: 'competition-edit/:id', name: 'CompetitionEdit', component: CompetitionEdit, meta: { roles: ['PLAYER', 'ORGANIZER', 'ADMIN'] } },
      { path: 'admin-review', name: 'AdminReview', component: AdminReview, meta: { roles: ['ADMIN'] } }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const userId = localStorage.getItem('user_id')
  const role = localStorage.getItem('role')
  const isPublic = to.matched.some(record => record.meta.public)

  if (!userId && !isPublic) {
    return '/login'
  }
  if (userId && isPublic) {
    return '/home'
  }
  if (to.meta.roles && role !== 'ADMIN' && !to.meta.roles.includes(role)) {
    return '/home'
  }
})

export default router
