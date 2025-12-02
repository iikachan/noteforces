<template>
  <v-app-bar app fixed color="primary" flat>
    <v-app-bar-nav-icon v-if="showDrawer" @click="drawer = !drawer" />
    <v-toolbar-title>{{ title }}</v-toolbar-title>
    <v-spacer />
    <v-menu v-if="showUserMenu" offset-y>
      <template #activator="{ props }">
        <v-btn icon v-bind="props">
          <v-icon>mdi-account</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>{{ user?.username }}</v-list-item-title>
            <v-list-item-subtitle>{{ user?.role }}</v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-divider />
        <v-list-item @click="logout">
          <v-list-item-title>退出登录</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>

  <v-navigation-drawer v-if="showDrawer" v-model="drawer" app fixed temporary>
    <v-list>
      <v-list-item-group>
        <v-list-item @click="filterCategory('')">
          <v-list-item-title>所有笔记</v-list-item-title>
        </v-list-item>

        <v-list-item
          v-for="cat in categories"
          :key="cat"
          @click="filterCategory(cat)"
        >
          <v-list-item-title>{{ cat }}</v-list-item-title>
        </v-list-item>
      </v-list-item-group>
    </v-list>

    <v-spacer />

    <v-list>
      <v-divider />
      <v-list-item @click="goSettings">
        <v-list-item-title>用户设置</v-list-item-title>
      </v-list-item>
      <v-list-item v-if="user?.role === 'admin'" @click="goAdminUsers">
        <v-list-item-title>用户管理</v-list-item-title>
      </v-list-item>
      <v-list-item v-if="user?.role === 'admin'" @click="goAdminNotes">
        <v-list-item-title>笔记管理</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from '@/plugins/axios'
import { useNoteStore } from '@/stores/note'

interface User {
  id: number
  username: string
  role: string
}

const props = defineProps({ title: { type: String, default: '' } })
const drawer = ref(false)
const user = ref<User | null>(null)
const categories = ref<string[]>([])
const noteStore = useNoteStore()
const router = useRouter()
const route = useRoute()

// 控制在登录/注册/分享页隐藏抽屉和用户菜单
const showDrawer = computed(() => {
  return !route.path.startsWith('/login') &&
         !route.path.startsWith('/register') &&
         !route.path.startsWith('/share/')
})
const showUserMenu = computed(() => showDrawer.value && !!user.value)

// 设置 axios token
function setToken(token: string | null) {
  if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  else delete axios.defaults.headers.common['Authorization']
}

// 加载用户信息
async function loadUser() {
  const token = localStorage.getItem('token')
  if (!token) {
    user.value = null
    setToken(null)
    return
  }
  setToken(token)
  try {
    const res = await axios.get('/user/me')
    if (res.data.code === 0) user.value = res.data.data
    else user.value = null
  } catch {
    user.value = null
  }
}

// 加载笔记分类
async function loadCategories() {
  if (!user.value) return
  try {
    const res = await axios.get('/note/categories')
    if (res.data.code === 0) categories.value = res.data.data.categories
  } catch {}
}

function filterCategory(cat: string) {
  noteStore.setCategory(cat)
  router.push('/')
  drawer.value = false
}

function logout() {
  axios.post('/user/logout').finally(() => {
    localStorage.removeItem('token')
    user.value = null
    router.push('/login')
  })
}

function goSettings() { router.push('/user') }
function goAdminUsers() { router.push('/admin/users') }
function goAdminNotes() { router.push('/admin/notes') }

onMounted(() => {
  loadUser().then(loadCategories)

  // 监听 localStorage token 变化
  window.addEventListener('storage', (e) => {
    if (e.key === 'token') loadUser().then(loadCategories)
  })

  // 监听登录成功事件
  window.addEventListener('login-success', () => {
    loadUser().then(loadCategories)
  })
})

onUnmounted(() => {
  window.removeEventListener('storage', (e) => {
    if (e.key === 'token') loadUser().then(loadCategories)
  })
  window.removeEventListener('login-success', () => {
    loadUser().then(loadCategories)
  })
})
</script>

<style scoped>
.v-navigation-drawer { width: 240px; }
</style>
