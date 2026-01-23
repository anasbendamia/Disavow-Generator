<!-- ui/vue3/static/js/Components/ToastNotification.vue -->
<!-- Copyright (c) 2026 Banshee (https://www.banshee.pro) -->
<!-- License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html) -->

<template>
  <Transition name="toast">
    <div v-if="show" class="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:bottom-6 sm:max-w-sm z-[70]">
      <div :class="['px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 w-full', type === 'error' ? 'bg-red-500/90 text-white' : 'bg-green-500/90 text-white']">
        <svg v-if="type === 'error'" class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <span class="text-sm font-medium flex-1">{{ message }}</span>
        <button @click="$emit('close')" class="hover:opacity-70 flex-shrink-0">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean;
  message: string;
  type: "error" | "success";
}>();

defineEmits<{
  close: [];
}>();
</script>
