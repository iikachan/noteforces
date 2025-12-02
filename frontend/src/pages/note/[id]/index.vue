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
              <v-card-text class="markdown-body">
                <div ref="contentRef" v-html="renderedHtml"></div>
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
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import NavDrawer from '@/components/NavDrawer.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import typescriptLang from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import cpp from 'highlight.js/lib/languages/cpp'
import java from 'highlight.js/lib/languages/java'
import cssLang from 'highlight.js/lib/languages/css'
import bash from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import 'highlight.js/styles/github.css'

hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('typescript', typescriptLang)
hljs.registerLanguage('ts', typescriptLang)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('cpp', cpp)
hljs.registerLanguage('c++', cpp)
hljs.registerLanguage('java', java)
hljs.registerLanguage('css', cssLang)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('json', json)

marked.setOptions({
  gfm: true,
  breaks: true
})

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
const contentRef = ref<HTMLElement | null>(null)
const renderedHtml = ref('')

const token = localStorage.getItem('token')
if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

async function loadNote() {
  try {
    const res = await axios.get('/note/detail', { params: { noteId } })
    if (res.data.code === 0) {
      note.value = res.data.data
      await updateRenderedHtml()
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

async function updateRenderedHtml() {
  if (!note.value || !note.value.content) {
    renderedHtml.value = ''
    await nextTick()
    applyHighlight()
    return
  }

  const possible = marked.parse(note.value.content) as string | Promise<string>
  let html = ''
  if (possible && typeof (possible as any).then === 'function') {
    try {
      html = await (possible as Promise<string>)
    } catch {
      html = ''
    }
  } else {
    html = String(possible ?? '')
  }

  renderedHtml.value = DOMPurify.sanitize(html)
  await nextTick()
  applyHighlight()
}

function applyHighlight() {
  const root = contentRef.value
  if (!root) return
  const codeBlocks = root.querySelectorAll('pre code')
  codeBlocks.forEach((block) => {
    try {
      hljs.highlightElement(block as HTMLElement)
    } catch {}
  })
}

watch(note, () => {
  updateRenderedHtml()
})

onMounted(() => {
  loadNote()
})
</script>

<style scoped>
.v-card-text {
  word-break: break-word;
}

.markdown-body p {
  margin: 0 0 12px 0;
  line-height: 1.6;
}
.markdown-body pre {
  padding: 12px;
  border-radius: 6px;
  overflow: auto;
  background-color: rgba(0,0,0,0.04);
  margin: 0 0 12px 0;
}
.markdown-body code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;
  font-size: 0.9em;
  background-color: rgba(0,0,0,0.03);
  padding: 2px 6px;
  border-radius: 4px;
}
.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  margin: 12px 0;
}
.markdown-body img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 8px 0;
}

.markdown-body pre code {
  display: block;
  white-space: pre;
}
</style>
