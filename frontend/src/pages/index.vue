<template>
  <v-container>
    <v-btn color="primary" class="mb-4" @click="createNote">创建笔记</v-btn>

    <v-alert
      v-if="!loadingNotes && notesFiltered.length === 0"
      type="info"
      variant="outlined"
    >
      暂无笔记。
    </v-alert>

    <v-row v-else dense>
      <v-col v-for="note in notesFiltered" :key="note.noteId" cols="12" md="4">
        <v-card class="hover-card" @click="openNote(note.noteId)">
          <v-card-title>{{ note.title }}</v-card-title>
          <v-card-text>{{ note.content?.slice(0, 80) }}...</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import { useNoteStore } from '@/stores/note'

interface Note {
  noteId: number
  title: string
  category?: string
  tags: string[]
  content?: string
}

const noteStore = useNoteStore()
const router = useRouter()
const notes = ref<Note[]>([])
const loadingNotes = ref(true)

const token = localStorage.getItem('token')
if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

async function loadNotes() {
  try {
    const res = await axios.get('/note/list')
    if (res.data.code === 0) {
      notes.value = res.data.data.notes.map((n: any) => ({ ...n, content: '' }))
      await Promise.all(
        notes.value.map(async (note: Note) => {
          try {
            const detailRes = await axios.get('/note/detail', {
              params: { noteId: note.noteId }
            })
            if (detailRes.data.code === 0) note.content = detailRes.data.data.content
          } catch {}
        })
      )
    }
  } finally {
    loadingNotes.value = false
  }
}

const notesFiltered = computed(() => {
  if (!noteStore.selectedCategory) return notes.value
  return notes.value.filter(n => n.category === noteStore.selectedCategory)
})

function openNote(id: number) {
  router.push(`/note/${id}`)
}

function createNote() {
  router.push('/note/create')
}

onMounted(() => {
  loadNotes()
})
</script>

<style scoped>
.hover-card {
  transition: 0.2s;
}
.hover-card:hover {
  transform: translateY(-4px);
}
</style>
