<template>
  <v-app>
    <NavDrawer title="新建笔记" />

    <v-main>
      <v-container>
        <NoteForm
          :model-value="form"
          submit-text="创建笔记"
          @submit="onSubmit"
        />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import NavDrawer from '@/components/NavDrawer.vue'
import NoteForm from '@/components/NoteForm.vue'

const router = useRouter()

const form = reactive({
  title: '',
  content: '',
  category: '',
  tags: ''
})

async function onSubmit(data: typeof form) {
  try {
    const payload = { ...data, tags: data.tags.split(',').map(t => t.trim()).filter(t => t) }
    const res = await axios.post('/note/create', payload)
    if (res.data.code === 0) router.push('/')
    else alert(res.data.msg)
  } catch (err: any) {
    alert(err.response?.data?.msg || '创建失败')
  }
}
</script>
