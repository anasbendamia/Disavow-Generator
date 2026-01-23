<!-- ui/vue3/static/js/Components/Button.vue -->
<!-- Copyright (c) 2026 Banshee (https://www.banshee.pro) -->
<!-- License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html) -->

<template>
  <component :is="href ? 'a' : 'button'" :href="href" :target="href ? '_blank' : undefined" :rel="href ? 'noopener noreferrer' : undefined" :type="href ? undefined : type" :disabled="disabled || loading" :class="buttonClasses">
    <span v-if="loading" class="spinner"></span>
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    variant?: "primary" | "success" | "danger" | "ghost" | "ghost-danger";
    size?: "sm" | "md" | "lg";
    disabled?: boolean;
    loading?: boolean;
    href?: string;
    type?: "button" | "submit" | "reset";
    fullWidth?: boolean;
  }>(),
  {
    variant: "primary",
    size: "md",
    disabled: false,
    loading: false,
    type: "button",
    fullWidth: false,
  },
);

const variantClasses = {
  primary: "bg-blue-600 hover:bg-blue-700 text-white",
  success: "bg-green-600 hover:bg-green-700 text-white",
  danger: "bg-red-600 hover:bg-red-700 text-white",
  ghost: "bg-slate-700/50 hover:bg-slate-700 text-slate-300",
  "ghost-danger": "bg-slate-700/50 hover:bg-red-500/10 text-red-400 hover:text-red-300",
};

const sizeClasses = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-1.5 text-xs",
  lg: "px-4 py-1.5 text-xs",
};

const buttonClasses = computed(() => ["inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all duration-200", "disabled:opacity-50 disabled:cursor-not-allowed", variantClasses[props.variant], sizeClasses[props.size], props.fullWidth ? "w-full" : ""]);
</script>
