<!-- ui/vue3/static/js/Components/ConfirmDialog.vue -->
<!-- Copyright (c) 2026 Banshee (https://www.banshee.pro) -->
<!-- License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html) -->

<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[60] p-4">
      <div class="bg-slate-800/95 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-lg w-full max-w-sm modal-content">
        <div class="card-header">
          <h3 class="font-semibold text-white">{{ title }}</h3>
        </div>
        <div class="card-body">
          <p class="text-slate-300 break-words">{{ message }}</p>
        </div>
        <div class="px-6 py-4 border-t border-slate-700/50 flex justify-end gap-3">
          <Button variant="ghost" @click="$emit('confirm', false)">Cancel</Button>
          <Button :variant="confirmVariant" @click="$emit('confirm', true)">{{ confirmText }}</Button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import Button from "./Button.vue";

withDefaults(
  defineProps<{
    show: boolean;
    title: string;
    message: string;
    confirmText?: string;
    confirmVariant?: "primary" | "success" | "danger" | "ghost";
  }>(),
  {
    confirmText: "Confirm",
    confirmVariant: "danger",
  },
);

defineEmits<{
  confirm: [value: boolean];
}>();
</script>
