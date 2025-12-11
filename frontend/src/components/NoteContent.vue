<template>
  <div ref="contentRef" class="markdown-body" v-html="renderedHtml" />
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
  import { defineProps, nextTick, onMounted, ref, watch } from 'vue'
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
    breaks: true,
  })

  interface Props {
    content: string
  }

  const props = defineProps<Props>()

  const renderedHtml = ref('')
  const contentRef = ref<HTMLElement | null>(null)

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

  function applyHighlight () {
    const root = contentRef.value
    if (!root) return
    const codeBlocks = root.querySelectorAll('pre code')
    for (const block of codeBlocks) {
      try {
        hljs.highlightElement(block as HTMLElement)
      } catch {}
    }
  }

  watch(() => props.content, () => {
    updateRenderedHtml()
  })

  onMounted(() => {
    updateRenderedHtml()
  })
</script>

<style scoped>
.markdown-body {
  padding: 16px; /* 内容内边距 */
  font-size: 16px; /* 正文字体 */
  line-height: 1.8; /* 正文行距 */
  color: #333;
}

.markdown-body p {
  margin: 0 0 16px 0;
  line-height: 1.8;
}

.markdown-body pre {
  padding: 12px; /* 保持原来的代码块内边距 */
  border-radius: 6px;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.04);
  margin: 0 0 16px 0;
  font-size: 0.9em; /* 代码字体保持原大小 */
  line-height: 1.6;
}

.markdown-body code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;
  font-size: 0.9em; /* 保持原大小 */
  background-color: rgba(0, 0, 0, 0.03);
  padding: 2px 6px;
  border-radius: 4px;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  margin: 16px 0 12px 0;
  line-height: 1.4;
}

.markdown-body img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 12px 0;
}

.markdown-body pre code {
  display: block;
  white-space: pre;
}
</style>
