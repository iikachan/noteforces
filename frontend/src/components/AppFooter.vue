<template>
</template>

<script setup lang="ts">
  const items = [
    {
      title: 'Noteforces GitHub',
      icon: `mdi-github`,
      href: 'https://github.com/iikachan/noteforces',
    }
  ]
</script>

<style scoped lang="sass">
  .social-link :deep(.v-icon)
    color: rgba(var(--v-theme-on-background), var(--v-disabled-opacity))
    text-decoration: none
    transition: .2s ease-in-out

    &:hover
      color: rgba(25, 118, 210, 1)
</style>
