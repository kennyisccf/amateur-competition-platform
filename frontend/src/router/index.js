import { createRouter, createWebHistory } from 'vue-router'

const Layout = () => import('../layout/Layout.vue')
const Register = () => import('../views/Register.vue')
const Login = () => import('../views/Login.vue')
const Home = () => import('../views/Home.vue')
const Profile = () => import('../views/Profile.vue')
const Notifications = () => import('../views/Notifications.vue')
const Friends = () => import('../views/Friends.vue')
const EventDetail = () => import('../views/EventDetail.vue')
const EventRegister = () => import('../views/EventRegister.vue')
const CreateCompetition = () => import('../views/CreateCompetition.vue')
const Workbench = () => import('../views/Workbench.vue')
const AdminReview = () => import('../views/AdminReview.vue')
const RegistrationManage = () => import('../views/RegistrationManage.vue')
const CompetitionEdit = () => import('../views/CompetitionEdit.vue')
const Forbidden = () => import('../views/Forbidden.vue')

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
      { path: 'admin-review', name: 'AdminReview', component: AdminReview, meta: { roles: ['ADMIN'] } },
      { path: 'forbidden', name: 'Forbidden', component: Forbidden }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/home'
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
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (userId && isPublic) {
    return '/home'
  }
  const requiredRoles = to.matched.flatMap(record => record.meta.roles ?? [])
  if (requiredRoles.length > 0 && role !== 'ADMIN' && !requiredRoles.includes(role)) {
    return {
      path: '/forbidden',
      query: {
        from: to.fullPath,
        need: [...new Set(requiredRoles)].join(',')
      }
    }
  }
})

export default router
