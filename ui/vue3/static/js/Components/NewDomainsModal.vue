<!-- ui/vue3/static/js/Components/NewDomainsModal.vue -->
<!-- Copyright (c) 2026 Banshee (https://www.banshee.pro) -->
<!-- License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html) -->

<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4" @click.self="$emit('skip')">
      <div class="bg-slate-800/95 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-lg w-full max-w-lg modal-content max-h-[90vh] flex flex-col">
        <div class="px-4 sm:px-6 py-3 sm:py-4 border-b border-slate-700/50 flex items-center justify-between">
          <div>
            <h3 class="font-semibold text-white">New Entries Found</h3>
            <p class="text-xs text-slate-400 mt-1">
              <span v-if="domains.length" class="text-orange-400">{{ domains.length }} domains</span>
              <span v-if="domains.length && ips.length"> · </span>
              <span v-if="ips.length" class="text-red-400">{{ ips.length }} IPs</span>
            </p>
          </div>
          <button @click="$emit('skip')" class="text-slate-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-4 sm:p-6 overflow-y-auto flex-1">
          <p class="text-slate-400 text-sm mb-4">Review new entries. Select any legitimate ones to add to whitelist and rebuild.</p>

          <!-- Select All -->
          <div class="flex items-center gap-2 mb-3 pb-3 border-b border-slate-700/50">
            <input type="checkbox" id="selectAll" :checked="selectedItems.length === allItems.length" :indeterminate="selectedItems.length > 0 && selectedItems.length < allItems.length" @change="toggleAll" class="w-4 h-4 rounded border-slate-600 bg-slate-900 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-800" />
            <label for="selectAll" class="text-sm text-slate-300 cursor-pointer"> Select all ({{ selectedItems.length }}/{{ allItems.length }}) </label>
          </div>

          <!-- Domains Section -->
          <div v-if="domains.length" class="mb-4">
            <h4 class="text-xs font-semibold text-orange-400 uppercase mb-2">Domains ({{ domains.length }})</h4>
            <div class="space-y-1 max-h-40 overflow-y-auto">
              <div v-for="domain in domains" :key="domain" class="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-700/30">
                <input type="checkbox" :id="domain" :value="domain" v-model="selectedItems" class="w-4 h-4 rounded border-slate-600 bg-slate-900 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-800 flex-shrink-0" />
                <label :for="domain" class="text-sm text-slate-300 truncate flex-1 cursor-pointer min-w-0">{{ domain }}</label>
                <a :href="`http://${domain}`" target="_blank" rel="noopener noreferrer" @click.stop class="p-1 text-slate-500 hover:text-blue-400 transition-colors flex-shrink-0" title="Open in new tab">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          </div>

          <!-- IPs Section -->
          <div v-if="ips.length">
            <h4 class="text-xs font-semibold text-red-400 uppercase mb-2">IPs ({{ ips.length }})</h4>
            <div class="space-y-1 max-h-40 overflow-y-auto">
              <div v-for="ip in ips" :key="ip" class="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-700/30">
                <input type="checkbox" :id="ip" :value="ip" v-model="selectedItems" class="w-4 h-4 rounded border-slate-600 bg-slate-900 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-800 flex-shrink-0" />
                <label :for="ip" class="text-sm text-slate-300 truncate flex-1 cursor-pointer min-w-0 font-mono">{{ ip }}</label>
                <a :href="`http://${ip}`" target="_blank" rel="noopener noreferrer" @click.stop class="p-1 text-slate-500 hover:text-blue-400 transition-colors flex-shrink-0" title="Open in new tab">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>

        <div class="px-4 sm:px-6 py-3 sm:py-4 border-t border-slate-700/50 flex flex-col sm:flex-row gap-2 sm:justify-end">
          <Button variant="ghost" class="order-2 sm:order-1" @click="$emit('skip')"> Block All & Continue </Button>
          <Button variant="primary" class="order-1 sm:order-2" :disabled="selectedItems.length === 0" @click="addToWhitelist">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Whitelist {{ selectedItems.length }} & Rebuild
          </Button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import Button from "./Button.vue";

const props = defineProps<{
  show: boolean;
  domains: string[];
  ips: string[];
}>();

const emit = defineEmits<{
  skip: [];
  whitelist: [items: string[]];
}>();

const selectedItems = ref<string[]>([]);

const allItems = computed(() => [...props.domains, ...props.ips]);

watch(
  () => props.show,
  (val) => {
    if (val) {
      selectedItems.value = [];
    }
  },
);

function toggleAll() {
  if (selectedItems.value.length === allItems.value.length) {
    selectedItems.value = [];
  } else {
    selectedItems.value = [...allItems.value];
  }
}

function addToWhitelist() {
  emit("whitelist", selectedItems.value);
}
</script>
