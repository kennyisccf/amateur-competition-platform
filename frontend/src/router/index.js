import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/Layout.vue'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import Profile from '../views/Profile.vue'          
import EventDetail from '../views/EventDetail.vue'
import EventRegister from '../views/EventRegister.vue'
import CreateCompetition from '../views/CreateCompetition.vue'
import Workbench from '../views/Workbench.vue'
import AdminReview from '../views/AdminReview.vue'
import RegistrationManage from '../views/RegistrationManage.vue'
import CompetitionEdit from '../views/CompetitionEdit.vue' 
import Notifications from '../views/Notifications.vue'
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
      { path: 'event-detail/:id', name: 'EventDetail', component: EventDetail },
      { path: 'event-register/:id', name: 'EventRegister', component: EventRegister },
      { path: 'create', name: 'CreateCompetition', component: CreateCompetition },
      { path: 'workbench', name: 'Workbench', component: Workbench },
      { path: 'registration-manage', name: 'RegistrationManage', component: RegistrationManage },
      { path: 'competition-edit/:id', name: 'CompetitionEdit', component: CompetitionEdit }, 
      { path: 'admin-review', name: 'AdminReview', component: AdminReview },
      { path: 'notifications', name: 'Notifications', component: Notifications }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router