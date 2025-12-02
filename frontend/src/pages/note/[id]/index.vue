<template>
  <v-app>
    <NavDrawer :title="note?.title || ''" />

    <v-main>
      <v-container>
        <v-row justify="center">
          <v-col cols="12" md="8">

            <v-card v-if="note">
              <v-card-title>{{ note.title }}</v-card-title>
              <v-card-subtitle v-if="note.category">
                分类: {{ note.category }}
              </v-card-subtitle>
              <v-card-text style="white-space: pre-wrap;">
                {{ note.content }}
              </v-card-text>
              <v-card-actions>
                <v-btn color="primary" @click="goEdit">
                  <v-icon left>mdi-pencil</v-icon>
                  编辑
                </v-btn>
                <v-btn color="error" @click="deleteNote">
                  <v-icon left>mdi-delete</v-icon>
                  删除
                </v-btn>
              </v-card-actions>
            </v-card>

          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import NavDrawer from '@/components/NavDrawer.vue'

interface NoteDetail {
  noteId: number
  title: string
  content: string
  category?: string
  tags: string[]
}

const route = useRoute()
const router = useRouter()
const note = ref<NoteDetail | null>(null)
const noteId = Number((route.params as { id: string }).id)

const token = localStorage.getItem('token')
if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

async function loadNote() {
  try {
    const res = await axios.get('/note/detail', { params: { noteId } })
    if (res.data.code === 0) {
      note.value = res.data.data
    } else {
      router.push('/')
    }
  } catch {
    router.push('/')
  }
}

function goEdit() {
  router.push(`/note/${noteId}/edit`)
}

async function deleteNote() {
  if (!confirm('确定要删除该笔记吗？')) return
  try {
    const res = await axios.post('/note/delete', { noteId })
    if (res.data.code === 0) {
      router.push('/')
    } else {
      alert(res.data.msg)
    }
  } catch (err: any) {
    alert(err.response?.data?.msg || '删除失败')
  }
}

onMounted(loadNote)
</script>

<style scoped>
.v-card-text {
  word-break: break-word;
}
</style>
