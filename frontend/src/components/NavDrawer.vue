<template>
  <v-app-bar color="primary" flat>
    <v-app-bar-nav-icon @click="drawer = !drawer" />
    <v-toolbar-title>{{ title }}</v-toolbar-title>
    <v-spacer />
    <v-menu offset-y>
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

  <v-navigation-drawer v-model="drawer" app temporary>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import { useNoteStore } from '@/stores/note'

interface User {
  id: number
  username: string
  role: string
}

const props = defineProps({
  title: { type: String, default: '' }
})

const noteStore = useNoteStore()
const drawer = ref(false)
const user = ref<User | null>(null)
const categories = ref<string[]>([])

const router = useRouter()
const token = localStorage.getItem('token')
if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

async function loadUser() {
  try {
    const res = await axios.get('/user/me')
    if (res.data.code === 0) user.value = res.data.data
    else router.push('/login')
  } catch {
    router.push('/login')
  }
}

async function loadCategories() {
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
    router.push('/login')
  })
}

function goSettings() { router.push('/user') }
function goAdminUsers() { router.push('/admin/users') }
function goAdminNotes() { router.push('/admin/notes') }

onMounted(() => {
  loadUser()
  loadCategories()
})
</script>

<style scoped>
.v-navigation-drawer {
  width: 240px;
}
</style>
