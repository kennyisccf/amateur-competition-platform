<template>
  <div
    v-for="(image, index) in backgroundImages"
    :key="image"
    class="auth-bg"
    :style="{
      backgroundImage: `url(${image})`,
      opacity: index === activeBgIndex ? 1 : 0,
      transform: index === activeBgIndex ? 'scale(1.06)' : 'scale(1.03)'
    }"
  />
  <div class="auth-scrim" />
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

let backgroundTimer = null
const backgroundImages = [
  '/login-backgrounds/badminton-login.png',
  '/login-backgrounds/football-login.png',
  '/login-backgrounds/esports-login.png',
  '/login-backgrounds/basketball-login.png',
  '/login-backgrounds/tennis-login.png',
  '/login-backgrounds/tabletennis-login.png',
  '/login-backgrounds/track-login.png',
  '/login-backgrounds/volleyball-login.png',
  '/login-backgrounds/swimming-login.png'
]
const activeBgIndex = ref(Math.floor(Math.random() * backgroundImages.length))

const preloadBackgrounds = () => {
  backgroundImages.forEach((src) => {
    const image = new Image()
    image.src = src
  })
}

const pickNextBackgroundIndex = () => {
  if (backgroundImages.length <= 1) return 0
  let nextIndex = activeBgIndex.value
  while (nextIndex === activeBgIndex.value) {
    nextIndex = Math.floor(Math.random() * backgroundImages.length)
  }
  return nextIndex
}

onMounted(() => {
  preloadBackgrounds()
  backgroundTimer = window.setInterval(() => {
    activeBgIndex.value = pickNextBackgroundIndex()
  }, 6000)
})

onBeforeUnmount(() => {
  if (backgroundTimer) {
    window.clearInterval(backgroundTimer)
    backgroundTimer = null
  }
})
</script>

<style scoped>
.auth-bg,
.auth-scrim {
  position: absolute;
  inset: 0;
}

.auth-bg {
  background-size: cover;
  background-position: center;
  opacity: 0;
  transform: scale(1.03);
  transition: opacity 1.2s ease, transform 6s ease;
  will-change: opacity, transform;
}

.auth-scrim {
  background:
    radial-gradient(circle at 18% 25%, rgba(22, 119, 255, 0.42), transparent 32%),
    linear-gradient(90deg, rgba(5, 16, 38, 0.86) 0%, rgba(5, 16, 38, 0.54) 48%, rgba(5, 16, 38, 0.78) 100%);
  backdrop-filter: saturate(1.08);
}

@media (prefers-reduced-motion: reduce) {
  .auth-bg {
    transition: opacity 0.2s linear;
  }
}
</style>
