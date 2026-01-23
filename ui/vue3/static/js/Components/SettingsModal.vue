<!-- ui/vue3/static/js/Components/SettingsModal.vue -->
<!-- Copyright (c) 2026 Banshee (https://www.banshee.pro) -->
<!-- License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html) -->

<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4" @click.self="$emit('close')">
      <div class="bg-slate-800/95 backdrop-blur-sm rounded-xl border border-slate-700/50 shadow-lg w-full max-w-md modal-content max-h-[90vh] overflow-y-auto">
        <div class="card-header flex items-center justify-between sticky top-0 bg-slate-800/95 backdrop-blur-sm">
          <h3 class="font-semibold text-white">Account Settings</h3>
          <button @click="$emit('close')" class="text-slate-400 hover:text-white">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="card-body">
          <!-- Messages -->
          <div v-if="error" class="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p class="text-red-400 text-sm">{{ error }}</p>
          </div>

          <form @submit.prevent="saveCredentials" class="space-y-4">
            <!-- Username -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Username</label>
              <input v-model="newUsername" type="text" class="input w-full" placeholder="Enter username" />
            </div>

            <hr class="border-slate-700/50" />

            <!-- Current Password -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Current Password</label>
              <input v-model="currentPassword" type="password" class="input w-full" placeholder="Enter current password" />
            </div>

            <!-- New Password -->
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">New Password</label>
              <input v-model="newPassword" type="password" class="input w-full" placeholder="Enter new password (leave empty to keep current)" />
            </div>

            <!-- Confirm Password -->
            <div v-if="newPassword">
              <label class="block text-sm font-medium text-slate-300 mb-2">Confirm New Password</label>
              <input v-model="confirmPassword" type="password" class="input w-full" placeholder="Confirm new password" />
            </div>

            <p class="text-xs text-slate-500">You will be logged out after saving changes.</p>

            <Button type="submit" variant="primary" full-width :loading="loading" :disabled="!canSave">
              {{ loading ? "Saving..." : "Save & Logout" }}
            </Button>
          </form>
        </div>
        <div class="px-6 py-4 border-t border-slate-700/50 flex justify-end">
          <Button variant="ghost" @click="$emit('close')">Cancel</Button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import axios from "axios";
import Button from "./Button.vue";

const props = defineProps<{
  show: boolean;
  username: string;
}>();

const emit = defineEmits<{
  close: [];
}>();

const loading = ref(false);
const error = ref("");

const newUsername = ref("");
const currentPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

const canSave = computed(() => {
  if (!currentPassword.value) return false;

  const usernameChanged = newUsername.value.trim() !== props.username;
  const passwordChanged = newPassword.value.length > 0;

  if (!usernameChanged && !passwordChanged) return false;

  if (passwordChanged && newPassword.value !== confirmPassword.value) return false;

  if (newUsername.value.trim().length < 3) return false;

  if (passwordChanged && newPassword.value.length < 4) return false;

  return true;
});

watch(
  () => props.show,
  (val) => {
    if (val) {
      newUsername.value = props.username;
      currentPassword.value = "";
      newPassword.value = "";
      confirmPassword.value = "";
      error.value = "";
    }
  },
);

async function saveCredentials() {
  if (!canSave.value) return;

  loading.value = true;
  error.value = "";

  try {
    await axios.post("/api/settings/credentials", {
      current_password: currentPassword.value,
      new_username: newUsername.value.trim(),
      new_password: newPassword.value || null,
    });

    window.location.href = "/login";
  } catch (e: any) {
    error.value = e.response?.data?.error || "Failed to save credentials";
    loading.value = false;
  }
}
</script>
