<template>
  <div
    ref="contentRef"
    :class="['markdown-body', isDark ? 'dark' : 'light']"
    v-html="renderedHtml"
  />
</template>

<script setup lang="ts">
  import DOMPurify from 'dompurify'
  import hljs from 'highlight.js/lib/core'
  import bash from 'highlight.js/lib/languages/bash'
  import cpp from 'highlight.js/lib/languages/cpp'
  import cssLang from 'highlight.js/lib/languages/css'
  import java from 'highlight.js/lib/languages/java'
  import javascript from 'highlight.js/lib/languages/javascript'
  import json from 'highlight.js/lib/languages/json'
  import python from 'highlight.js/lib/languages/python'
  import typescriptLang from 'highlight.js/lib/languages/typescript'
  import { marked } from 'marked'
  import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

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

  marked.setOptions({ gfm: true, breaks: true })

  interface Props { content: string }
  const props = defineProps<Props>()
  const renderedHtml = ref('')
  const contentRef = ref<HTMLElement | null>(null)
  const isDark = ref(
    typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches,
  )

  let mq: MediaQueryList | null = null

  // 动态加载 hljs 样式
  async function loadHljsTheme () {
    const head = document.head
    const prevLink = head.querySelector<HTMLLinkElement>('link[data-hljs-theme]')
    if (prevLink) prevLink.remove()
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.dataset.hljsTheme = 'true'
    link.href = isDark.value
      ? '/node_modules/highlight.js/styles/github-dark.css'
      : '/node_modules/highlight.js/styles/github.css'
    head.append(link)
  }

  // 高亮代码块
  function applyHighlight () {
    const root = contentRef.value
    if (!root) return
    const codeBlocks = root.querySelectorAll('pre code')
    for (const block of codeBlocks) hljs.highlightElement(block as HTMLElement)
  }

  // 渲染 Markdown
  async function updateRenderedHtml () {
    if (!props.content) {
      renderedHtml.value = ''
      await nextTick()
      applyHighlight()
      return
    }
    const possible = marked.parse(props.content) as string | Promise<string>
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

  // 监听系统主题切换
  function handleColorSchemeChange (e: MediaQueryListEvent) {
    isDark.value = e.matches
    loadHljsTheme().then(() => nextTick().then(applyHighlight))
  }

  onMounted(() => {
    loadHljsTheme().then(updateRenderedHtml)
    if (typeof window !== 'undefined' && window.matchMedia) {
      mq = window.matchMedia('(prefers-color-scheme: dark)')
      if ('addEventListener' in mq) mq.addEventListener('change', handleColorSchemeChange)
      else if ('addListener' in mq) // @ts-ignore
        mq.addListener(handleColorSchemeChange)
    }
  })

  onUnmounted(() => {
    if (mq) {
      if ('removeEventListener' in mq) mq.removeEventListener('change', handleColorSchemeChange)
      else if ('removeListener' in mq) // @ts-ignore
        mq.removeListener(handleColorSchemeChange)
      mq = null
    }
  })

  watch(() => props.content, () => updateRenderedHtml())
  watch(isDark, () => loadHljsTheme().then(() => nextTick().then(applyHighlight)))
</script>

<style>
.markdown-body {
  padding: 16px;
  font-size: 16px;
  line-height: 1.7; /* 调整行高让文本更紧凑自然 */
  word-break: break-word; /* 防止长单词撑破布局 */
  color: inherit;
  background-color: inherit;
}

/* 段落 */
.markdown-body p {
  margin: 0 0 12px 0;
}

/* 标题 */
.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  margin: 24px 0 12px 0;
  font-weight: 600;
  line-height: 1.3;
}

/* 列表 */
.markdown-body ul,
.markdown-body ol {
  padding-left: 1.5em;
  margin: 0 0 12px 0;
}
.markdown-body li {
  margin-bottom: 6px;
}

/* 图片 */
.markdown-body img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 12px 0;
  border-radius: 4px; /* 更柔和 */
}

/* 表格 */
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}
.markdown-body th,
.markdown-body td {
  border: 1px solid;
  padding: 6px 12px;
  text-align: left;
}
/* LIGHT mode 表格边框 */
.markdown-body.light th,
.markdown-body.light td {
  border-color: #d0d7de;
}
/* DARK mode 表格边框 */
.markdown-body.dark th,
.markdown-body.dark td {
  border-color: #444c56;
}

/* 高亮代码块 hljs */
.markdown-body.light pre code.hljs,
.markdown-body.light .hljs {
  background: #f6f8fa !important;
  color: #24292e !important;
}
.markdown-body.dark pre code.hljs,
.markdown-body.dark .hljs {
  background: #2d2d2d !important;
  color: #ddd !important;
}

/* 亮色模式 */
.markdown-body.light {
  color: #24292e;
  background-color: #fff;
}
.markdown-body.light pre {
  background-color: #f6f8fa;
}
.markdown-body.light code {
  background-color: rgba(0,0,0,0.03);
}

/* 暗黑模式 */
.markdown-body.dark {
  color: #ddd;
  background-color: #1e1e1e;
}
.markdown-body.dark pre {
  background-color: #2d2d2d;
}
.markdown-body.dark code {
  background-color: rgba(255,255,255,0.05);
}

/* 列表点和数字自然对齐标题 */
.markdown-body ul,
.markdown-body ol {
  padding-left: 1.5em;
  margin-left: 0;
}
</style>
