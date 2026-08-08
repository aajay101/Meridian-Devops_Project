import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

import AuthLayout from '@/layouts/AuthLayout.vue'
import AppLayout from '@/layouts/AppLayout.vue'

import LandingPage from '@/views/public/LandingPage.vue'
import LoginPage from '@/views/public/LoginPage.vue'
import RegisterPage from '@/views/public/RegisterPage.vue'

import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import ManageCompanies from '@/views/admin/ManageCompanies.vue'
import CompanyDetail from '@/views/admin/CompanyDetail.vue'
import ManageStudents from '@/views/admin/ManageStudents.vue'
import StudentDetail from '@/views/admin/StudentDetail.vue'
import ManageDrives from '@/views/admin/ManageDrives.vue'
import AdminDriveDetail from '@/views/admin/AdminDriveDetail.vue'
import AllApplications from '@/views/admin/AllApplications.vue'
import ReportsPage from '@/views/admin/ReportsPage.vue'

import CompanyDashboard from '@/views/company/CompanyDashboard.vue'
import CompanyProfile from '@/views/company/CompanyProfile.vue'
import MyDrives from '@/views/company/MyDrives.vue'
import CreateDrive from '@/views/company/CreateDrive.vue'
import EditDrive from '@/views/company/EditDrive.vue'
import CompanyDriveDetail from '@/views/company/CompanyDriveDetail.vue'
import Applicants from '@/views/company/Applicants.vue'

import StudentDashboard from '@/views/student/StudentDashboard.vue'
import StudentProfile from '@/views/student/StudentProfile.vue'
import AvailableDrives from '@/views/student/AvailableDrives.vue'
import StudentDriveDetail from '@/views/student/StudentDriveDetail.vue'
import ApplicationHistory from '@/views/student/ApplicationHistory.vue'
import PlacementHistory from '@/views/student/PlacementHistory.vue'

import NotFound from '@/views/error/NotFound.vue'
import Forbidden from '@/views/error/Forbidden.vue'
import ServerError from '@/views/error/ServerError.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: AuthLayout,
    children: [
      { path: 'login', name: 'Login', component: LoginPage, meta: { requiresAuth: false } },
      { path: 'register', name: 'Register', component: RegisterPage, meta: { requiresAuth: false } }
    ]
  },
  {
    path: '/admin',
    component: AppLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'companies', name: 'ManageCompanies', component: ManageCompanies },
      { path: 'companies/:id', name: 'CompanyDetail', component: CompanyDetail },
      { path: 'students', name: 'ManageStudents', component: ManageStudents },
      { path: 'students/:id', name: 'StudentDetail', component: StudentDetail },
      { path: 'drives', name: 'ManageDrives', component: ManageDrives },
      { path: 'drives/:id', name: 'AdminDriveDetail', component: AdminDriveDetail },
      { path: 'applications', name: 'AllApplications', component: AllApplications },
      { path: 'reports', name: 'ReportsPage', component: ReportsPage }
    ]
  },
  {
    path: '/company',
    component: AppLayout,
    meta: { requiresAuth: true, role: 'company' },
    children: [
      { path: '', redirect: '/company/dashboard' },
      { path: 'dashboard', name: 'CompanyDashboard', component: CompanyDashboard },
      { path: 'profile', name: 'CompanyProfile', component: CompanyProfile },
      { path: 'drives', name: 'MyDrives', component: MyDrives },
      { path: 'drives/new', name: 'CreateDrive', component: CreateDrive },
      { path: 'drives/:id', name: 'CompanyDriveDetail', component: CompanyDriveDetail },
      { path: 'drives/:id/edit', name: 'EditDrive', component: EditDrive },
      { path: 'drives/:id/applicants', name: 'Applicants', component: Applicants }
    ]
  },
  {
    path: '/student',
    component: AppLayout,
    meta: { requiresAuth: true, role: 'student' },
    children: [
      { path: '', redirect: '/student/dashboard' },
      { path: 'dashboard', name: 'StudentDashboard', component: StudentDashboard },
      { path: 'profile', name: 'StudentProfile', component: StudentProfile },
      { path: 'drives', name: 'AvailableDrives', component: AvailableDrives },
      { path: 'drives/:id', name: 'StudentDriveDetail', component: StudentDriveDetail },
      { path: 'applications', name: 'ApplicationHistory', component: ApplicationHistory },
      { path: 'history', name: 'PlacementHistory', component: PlacementHistory }
    ]
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: Forbidden
  },
  {
    path: '/500',
    name: 'ServerError',
    component: ServerError
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (!authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (err) {
      // ignore
    }
  }

  const isAuthenticated = !!authStore.user
  const userRole = authStore.user?.role

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }

  if (to.meta.role && to.meta.role !== userRole) {
    if (isAuthenticated) {
      const roleRoutes = { admin: '/admin/dashboard', company: '/company/dashboard', student: '/student/dashboard' }
      return next(roleRoutes[userRole] || '/login')
    }
    return next('/403')
  }

  if ((to.name === 'Landing' || to.name === 'Login' || to.name === 'Register') && isAuthenticated) {
    const roleRoutes = { admin: '/admin/dashboard', company: '/company/dashboard', student: '/student/dashboard' }
    return next(roleRoutes[userRole] || '/login')
  }

  next()
})

export default router
