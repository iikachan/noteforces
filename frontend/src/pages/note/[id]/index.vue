<template>
  <v-main class="pa-0">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8">
          <v-card v-if="note">
            <v-card-title>{{ note.title }}</v-card-title>
            <v-card-subtitle v-if="note.category">
              分类: {{ note.category }}
            </v-card-subtitle>

            <v-card-text>
              <NoteContent :content="note.content" />
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
              <v-spacer />
              <v-switch
                v-model="shared"
                :label="shared ? '已分享' : '未分享'"
                @change="toggleShare"
                inset
                hide-details
                :color="shared ? 'success' : ''"
              />
            </v-card-actions>

            <v-card-subtitle v-if="shared && shareUrl" class="mt-0 mb-3">
              分享链接:
              <a :href="shareUrl" target="_blank">{{ shareUrl }}</a>
            </v-card-subtitle>
          </v-card>

          <v-snackbar v-model="snackbar.show" :timeout="3000" top :color="snackbar.color">
            {{ snackbar.message }}
          </v-snackbar>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import NoteContent from '@/components/NoteContent.vue'

interface NoteDetail {
  noteId: number
  title: string
  content: string
  category?: string
  tags: string[]
  shareToken?: string
}

const route = useRoute()
const router = useRouter()
const note = ref<NoteDetail | null>(null)
const noteId = Number((route.params as { id: string }).id)
const snackbar = ref({ show: false, message: '', color: 'success' })
const shared = ref(false)
const shareUrl = ref('')

const token = localStorage.getItem('token')
if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

async function loadNote() {
  try {
    const res = await axios.get('/note/detail', { params: { noteId } })
    if (res.data.code === 0) {
      note.value = res.data.data
      shared.value = !!note.value?.shareToken
      if (shared.value && note.value?.shareToken) {
        shareUrl.value = window.location.origin + `/share/${note.value.shareToken}`
      }
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
    if (res.data.code === 0) router.push('/')
    else alert(res.data.msg)
  } catch (err: any) {
    alert(err.response?.data?.msg || '删除失败')
  }
}

async function toggleShare() {
  if (!note.value) return
  try {
    if (shared.value) {
      const res = await axios.post('/share/enable', { noteId })
      if (res.data.code === 0 && res.data.data?.shareToken) {
        note.value.shareToken = res.data.data.shareToken
        shareUrl.value = window.location.origin + `/share/${res.data.data.shareToken}`
        showSnackbar('分享已启用，链接已复制', 'success')
        try { await navigator.clipboard.writeText(shareUrl.value) } catch {}
      } else {
        shared.value = false
        showSnackbar(res.data.msg || '分享失败', 'error')
      }
    } else {
      const res = await axios.post('/share/disable', { noteId })
      if (res.data.code === 0) {
        note.value.shareToken = undefined
        shareUrl.value = ''
        showSnackbar('分享已取消', 'success')
      } else {
        shared.value = true
        showSnackbar(res.data.msg || '取消分享失败', 'error')
      }
    }
  } catch (err: any) {
    shared.value = !shared.value
    showSnackbar(err.response?.data?.msg || '操作失败', 'error')
  }
}

function showSnackbar(message: string, color: string = 'success') {
  snackbar.value = { show: true, message, color }
}

onMounted(() => {
  loadNote()
})
</script>

<style scoped>
.v-card-text {
  word-break: break-word;
}
</style>
