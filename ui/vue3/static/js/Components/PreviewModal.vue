<!-- ui/vue3/static/js/Components/PreviewModal.vue -->
<!-- Copyright (c) 2026 Banshee (https://www.banshee.pro) -->
<!-- License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html) -->

<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-2 sm:p-4" @click.self="$emit('close')">
      <div class="bg-slate-800/95 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-lg w-full max-w-4xl max-h-[95vh] sm:max-h-[80vh] flex flex-col modal-content">
        <div class="card-header flex items-center justify-between">
          <h3 class="font-semibold text-white truncate pr-4 text-sm sm:text-base">{{ filename }}</h3>
          <button @click="$emit('close')" class="text-slate-400 hover:text-white flex-shrink-0">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="card-body overflow-auto flex-1">
          <pre class="text-[10px] sm:text-xs text-slate-300 font-mono whitespace-pre-wrap break-all">{{ content }}</pre>
        </div>
        <div class="px-4 sm:px-6 py-3 sm:py-4 border-t border-slate-700/50 flex flex-col sm:flex-row justify-end gap-2">
          <Button variant="primary" :href="`/api/download/${filename}`">Download</Button>
          <Button variant="ghost" @click="$emit('close')">Close</Button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import Button from "./Button.vue";

defineProps<{
  show: boolean;
  filename: string;
  content: string;
}>();

defineEmits<{
  close: [];
}>();
</script>
