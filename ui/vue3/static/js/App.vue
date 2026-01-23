<!-- ui/vue3/static/js/App.vue -->
<!-- Copyright (c) 2026 Banshee (https://www.banshee.pro) -->
<!-- License: AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html) -->

<template>
  <div class="min-h-screen">
    <!-- Header -->
    <AppHeader :username="username" @open-settings="showSettings = true" />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-8 overflow-x-hidden">
      <!-- Stats Grid -->
      <div class="grid grid-cols-3 sm:grid-cols-3 md:grid-cols-6 gap-2 sm:gap-4 mb-6 sm:mb-8">
        <div class="stat-card">
          <div class="stat-value text-blue-400">{{ stats.input_files || 0 }}</div>
          <div class="stat-label">Input</div>
        </div>
        <div class="stat-card">
          <div class="stat-value text-purple-400">{{ stats.output_files || 0 }}</div>
          <div class="stat-label">Output</div>
        </div>
        <div class="stat-card">
          <div class="stat-value text-red-400">{{ stats.total_ips || 0 }}</div>
          <div class="stat-label">IPs</div>
        </div>
        <div class="stat-card">
          <div class="stat-value text-orange-400">{{ stats.total_domains || 0 }}</div>
          <div class="stat-label">Domains</div>
        </div>
        <div class="stat-card">
          <div class="stat-value text-cyan-400">{{ stats.total_urls || 0 }}</div>
          <div class="stat-label">URLs</div>
        </div>
        <div class="stat-card">
          <div class="stat-value text-green-400">{{ stats.whitelist_count || 0 }}</div>
          <div class="stat-label">Whitelist</div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="grid lg:grid-cols-3 gap-4 sm:gap-6 w-full max-w-full overflow-hidden">
        <!-- Left Column: Upload & Process -->
        <div class="lg:col-span-2 space-y-4 sm:space-y-6 w-full max-w-full min-w-0 overflow-hidden">
          <!-- Tabs -->
          <div class="flex gap-1 sm:gap-2 border-b border-slate-700/50 pb-2 overflow-x-auto">
            <button @click="activeTab = 'upload'" :class="['px-3 sm:px-4 py-2 rounded-t-lg font-medium transition-colors text-sm whitespace-nowrap', activeTab === 'upload' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white']">Upload</button>
            <button @click="activeTab = 'whitelist'" :class="['px-3 sm:px-4 py-2 rounded-t-lg font-medium transition-colors text-sm whitespace-nowrap', activeTab === 'whitelist' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white']">Whitelist</button>
            <button @click="activeTab = 'history'" :class="['px-3 sm:px-4 py-2 rounded-t-lg font-medium transition-colors text-sm whitespace-nowrap', activeTab === 'history' ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white']">History</button>
          </div>

          <!-- Upload Tab -->
          <div v-if="activeTab === 'upload'" class="card w-full max-w-full">
            <div class="card-body space-y-4 sm:space-y-6 w-full max-w-full">
              <!-- Dropzone -->
              <div @drop="handleDrop" @dragover.prevent="dragOver = true" @dragleave="dragOver = false" :class="['dropzone cursor-pointer', dragOver ? 'drag-over' : '']" @click="($refs.fileInput as HTMLInputElement)?.click()">
                <input ref="fileInput" type="file" multiple accept=".xlsx,.xls,.csv,.txt" class="hidden" @change="handleFileSelect" />
                <svg class="w-10 h-10 sm:w-12 sm:h-12 mx-auto text-slate-500 mb-3 sm:mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="text-slate-300 font-medium text-sm sm:text-base">Drop files here or tap to upload</p>
                <p class="text-slate-500 text-xs sm:text-sm mt-1">.xlsx, .xls, .csv, .txt</p>
              </div>

              <!-- Process Button -->
              <Button variant="primary" size="lg" full-width :loading="processing" :disabled="inputFiles.length === 0" @click="processFiles()">
                <svg v-if="!processing" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                {{ processing ? "Processing..." : "Generate Disavow File" }}
              </Button>

              <!-- Result -->
              <div v-if="lastResult" :class="['p-3 sm:p-4 rounded-lg', lastResult.success ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30']">
                <div v-if="lastResult.success" class="space-y-3">
                  <div class="flex items-center gap-2 text-green-400">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span class="font-medium text-sm sm:text-base">Disavow file generated!</span>
                  </div>
                  <p class="text-xs sm:text-sm text-slate-300 truncate"><span class="text-slate-400">File:</span> {{ lastResult.filename }}</p>
                  <div class="grid grid-cols-4 gap-1 sm:gap-2 text-center text-xs sm:text-sm">
                    <div class="bg-slate-800/50 rounded p-1.5 sm:p-2">
                      <div class="text-base sm:text-lg font-bold text-white">{{ lastResult.stats?.total }}</div>
                      <div class="text-[10px] sm:text-xs text-slate-400">Total</div>
                    </div>
                    <div class="bg-slate-800/50 rounded p-1.5 sm:p-2">
                      <div class="text-base sm:text-lg font-bold text-red-400">{{ lastResult.stats?.ips }}</div>
                      <div class="text-[10px] sm:text-xs text-slate-400">IPs</div>
                    </div>
                    <div class="bg-slate-800/50 rounded p-1.5 sm:p-2">
                      <div class="text-base sm:text-lg font-bold text-orange-400">{{ lastResult.stats?.domains }}</div>
                      <div class="text-[10px] sm:text-xs text-slate-400">Domains</div>
                    </div>
                    <div class="bg-slate-800/50 rounded p-1.5 sm:p-2">
                      <div class="text-base sm:text-lg font-bold text-cyan-400">{{ lastResult.stats?.urls }}</div>
                      <div class="text-[10px] sm:text-xs text-slate-400">URLs</div>
                    </div>
                  </div>
                  <!-- New entries summary -->
                  <div v-if="lastResult.new_entries && lastResult.new_entries.total > 0" class="text-xs sm:text-sm text-slate-400 bg-slate-800/30 rounded p-2 sm:p-3">
                    <div class="font-medium text-slate-300 mb-1">New entries blocked:</div>
                    <div class="flex flex-wrap gap-x-4 gap-y-1">
                      <span v-if="lastResult.new_entries.domains > 0"
                        ><span class="text-orange-400 font-medium">{{ lastResult.new_entries.domains }}</span> domains</span
                      >
                      <span v-if="lastResult.new_entries.ips > 0"
                        ><span class="text-red-400 font-medium">{{ lastResult.new_entries.ips }}</span> IPs</span
                      >
                      <span v-if="lastResult.new_entries.urls > 0"
                        ><span class="text-cyan-400 font-medium">{{ lastResult.new_entries.urls }}</span> URLs</span
                      >
                    </div>
                  </div>
                  <Button variant="success" full-width :href="`/api/download/${lastResult.filename}`">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download
                  </Button>
                </div>
                <div v-else class="text-red-400 text-sm">
                  <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ lastResult.error }}
                </div>
              </div>

              <!-- Input Files List -->
              <div v-if="inputFiles.length > 0" class="w-full max-w-full overflow-hidden">
                <h3 class="text-xs sm:text-sm font-semibold text-slate-400 uppercase mb-2 sm:mb-3">Input Files ({{ inputFiles.length }})</h3>
                <div class="space-y-2">
                  <div v-for="file in inputFiles" :key="file.name" class="file-item">
                    <span class="badge text-[10px] sm:text-xs" :class="file.type === 'XLSX' || file.type === 'XLS' ? 'badge-green' : file.type === 'CSV' ? 'badge-blue' : 'badge-yellow'">
                      {{ file.type }}
                    </span>
                    <span class="file-name">{{ file.name }}</span>
                    <button @click="deleteFile(file.name)" class="text-slate-500 hover:text-red-400 transition-colors p-1">
                      <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Whitelist Tab -->
          <div v-if="activeTab === 'whitelist'" class="card w-full max-w-full">
            <div class="card-body space-y-4 w-full max-w-full overflow-hidden">
              <p class="text-slate-400 text-xs sm:text-sm">Domains in the whitelist will be excluded from the disavow file.</p>
              <div class="flex gap-2">
                <input v-model="newDomain" @keyup.enter="addDomain" type="text" placeholder="example.com" class="input flex-1 min-w-0 text-sm" />
                <Button variant="primary" size="sm" @click="addDomain">Add</Button>
              </div>
              <div v-if="whitelist.length > 0" class="space-y-2 max-h-64 sm:max-h-96 overflow-y-auto">
                <div v-for="domain in whitelist" :key="domain" class="file-item">
                  <span class="file-name">{{ domain }}</span>
                  <button @click="removeDomain(domain)" class="text-slate-500 hover:text-red-400 transition-colors p-1">
                    <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <p v-else class="text-slate-500 text-center py-6 sm:py-8 text-sm">No domains in whitelist</p>
            </div>
          </div>

          <!-- History Tab -->
          <div v-if="activeTab === 'history'" class="card w-full max-w-full">
            <div class="card-body w-full max-w-full overflow-hidden space-y-4">
              <!-- Disclaimer -->
              <div class="flex gap-2 p-2 sm:p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs sm:text-sm text-blue-300">
                <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>We encourage you to keep old disavow files to track new domains/IPs and easily whitelist them for granular management.</span>
              </div>
              <div v-if="outputFiles.length > 0" class="space-y-3">
                <div v-for="file in outputFiles" :key="file.name" class="p-3 sm:p-4 bg-slate-900/50 rounded-lg space-y-2 overflow-hidden">
                  <div class="file-item !p-0 !bg-transparent !rounded-none">
                    <span class="file-name font-medium text-slate-200">{{ file.name }}</span>
                    <span class="text-[10px] sm:text-xs text-slate-500 whitespace-nowrap">{{ formatDate(file.created) }}</span>
                  </div>
                  <div class="flex flex-wrap gap-2 sm:gap-4 text-xs sm:text-sm text-slate-400">
                    <span
                      ><span class="text-red-400">{{ file.ips }}</span> IPs</span
                    >
                    <span
                      ><span class="text-orange-400">{{ file.domains }}</span> Domains</span
                    >
                    <span
                      ><span class="text-cyan-400">{{ file.urls }}</span> URLs</span
                    >
                  </div>
                  <div class="flex flex-wrap gap-2 pt-1 sm:pt-2">
                    <Button variant="ghost" size="sm" :href="`/api/download/${file.name}`">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Download
                    </Button>
                    <Button variant="ghost" size="sm" @click="openPreview(file.name)">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      Preview
                    </Button>
                    <Button variant="ghost-danger" size="sm" @click="deleteOutput(file.name)">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
              <p v-else class="text-slate-500 text-center py-6 sm:py-8 text-sm">No disavow files generated yet</p>
            </div>
          </div>
        </div>

        <!-- Right Column: Quick Info (hidden on mobile, shows in tabs) -->
        <div class="hidden lg:block space-y-6">
          <!-- Instructions -->
          <div class="card">
            <div class="card-header">
              <h3 class="font-semibold text-white text-sm">How to Use</h3>
            </div>
            <div class="card-body space-y-3 text-sm text-slate-400">
              <div class="flex gap-3">
                <span class="flex-shrink-0 w-5 h-5 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-xs font-bold">1</span>
                <p class="text-xs">Upload spam link files</p>
              </div>
              <div class="flex gap-3">
                <span class="flex-shrink-0 w-5 h-5 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-xs font-bold">2</span>
                <p class="text-xs">Add domains to whitelist</p>
              </div>
              <div class="flex gap-3">
                <span class="flex-shrink-0 w-5 h-5 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-xs font-bold">3</span>
                <p class="text-xs">Generate Disavow File</p>
              </div>
              <div class="flex gap-3">
                <span class="flex-shrink-0 w-5 h-5 bg-blue-500/20 text-blue-400 rounded-full flex items-center justify-center text-xs font-bold">4</span>
                <p class="text-xs">Upload to Search Console</p>
              </div>
            </div>
          </div>

          <!-- Last Output -->
          <div v-if="stats.last_output" class="card">
            <div class="card-header">
              <h3 class="font-semibold text-white text-sm">Last Generated</h3>
            </div>
            <div class="card-body">
              <p class="text-xs text-slate-300 truncate">{{ stats.last_output.filename }}</p>
              <p class="text-[10px] text-slate-500 mt-1">{{ formatDate(stats.last_output.created) }}</p>
              <Button variant="primary" size="sm" full-width :href="`/api/download/${stats.last_output.filename}`" class="mt-3">Download Latest</Button>
            </div>
          </div>

          <!-- Links -->
          <div class="card">
            <div class="card-header">
              <h3 class="font-semibold text-white text-sm">Useful Links</h3>
            </div>
            <div class="card-body space-y-2">
              <a href="https://search.google.com/search-console/disavow-links" target="_blank" class="flex items-center gap-2 text-xs text-slate-400 hover:text-white transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Disavow Links Tool
              </a>
              <a href="https://support.google.com/webmasters/answer/2648487" target="_blank" class="flex items-center gap-2 text-xs text-slate-400 hover:text-white transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
                Google Disavow Guide
              </a>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Modals -->
    <PreviewModal :show="!!previewContent" :filename="previewFile" :content="previewContent" @close="closePreview" />

    <SettingsModal :show="showSettings" :username="username" @close="showSettings = false" />

    <ConfirmDialog :show="confirmDialog.show" :title="confirmDialog.title" :message="confirmDialog.message" :confirm-text="confirmDialog.confirmText" :confirm-variant="confirmDialog.confirmVariant" @confirm="handleConfirm" />

    <NewDomainsModal :show="newEntriesModal.show" :domains="newEntriesModal.domains" :ips="newEntriesModal.ips" @skip="handleNewEntriesSkip" @whitelist="handleNewEntriesWhitelist" />

    <ToastNotification :show="toast.show" :message="toast.message" :type="toast.type" @close="toast.show = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, inject, onMounted } from "vue";
import axios from "axios";

import AppHeader from "./Components/AppHeader.vue";
import Button from "./Components/Button.vue";
import ConfirmDialog from "./Components/ConfirmDialog.vue";
import ToastNotification from "./Components/ToastNotification.vue";
import SettingsModal from "./Components/SettingsModal.vue";
import PreviewModal from "./Components/PreviewModal.vue";
import NewDomainsModal from "./Components/NewDomainsModal.vue";
interface Stats {
  input_files: number;
  output_files: number;
  total_ips: number;
  total_domains: number;
  total_urls: number;
  whitelist_count: number;
  last_output: { filename: string; created: string; size: number } | null;
}

interface InputFile {
  name: string;
  size: number;
  modified: string;
  type: string;
}

interface OutputFile {
  name: string;
  size: number;
  created: string;
  ips: number;
  domains: number;
  urls: number;
}

interface ProcessResult {
  success: boolean;
  filename?: string;
  error?: string;
  stats?: { ips: number; domains: number; urls: number; total: number };
  new_entries?: {
    ips: number;
    domains: number;
    urls: number;
    total: number;
    list: { ips: string[]; domains: string[]; urls: string[] };
  };
}

const appState = inject<any>("appState");
const stats = ref<Stats>(appState?.stats || {});
const whitelist = ref<string[]>(appState?.whitelist || []);
const username = ref<string>(appState?.username || "");
const inputFiles = ref<InputFile[]>([]);
const outputFiles = ref<OutputFile[]>([]);
const processing = ref(false);
const activeTab = ref<"upload" | "whitelist" | "history">("upload");
const dragOver = ref(false);
const newDomain = ref("");
const lastResult = ref<ProcessResult | null>(null);
const previewContent = ref("");
const previewFile = ref("");
const showSettings = ref(false);

const newEntriesModal = ref({
  show: false,
  domains: [] as string[],
  ips: [] as string[],
  pendingResult: null as ProcessResult | null,
});

const confirmDialog = ref({
  show: false,
  title: "",
  message: "",
  confirmText: "Delete",
  confirmVariant: "danger" as "primary" | "success" | "danger" | "ghost",
  resolve: null as ((value: boolean) => void) | null,
});

function showConfirm(options: { title: string; message: string; confirmText?: string; confirmVariant?: "primary" | "success" | "danger" | "ghost" }): Promise<boolean> {
  return new Promise((resolve) => {
    confirmDialog.value = {
      show: true,
      title: options.title,
      message: options.message,
      confirmText: options.confirmText || "Delete",
      confirmVariant: options.confirmVariant || "danger",
      resolve,
    };
  });
}

function handleConfirm(result: boolean) {
  if (confirmDialog.value.resolve) {
    confirmDialog.value.resolve(result);
  }
  confirmDialog.value.show = false;
}

const toast = ref({ show: false, message: "", type: "error" as "error" | "success" });

function showToast(message: string, type: "error" | "success" = "error") {
  toast.value = { show: true, message, type };
  setTimeout(() => (toast.value.show = false), 4000);
}

async function fetchStats() {
  try {
    const res = await axios.get("/api/stats");
    stats.value = res.data;
  } catch (e) {
    console.error("Failed to fetch stats:", e);
  }
}

async function fetchFiles() {
  try {
    const [inputRes, outputRes] = await Promise.all([axios.get("/api/files"), axios.get("/api/outputs")]);
    inputFiles.value = inputRes.data;
    outputFiles.value = outputRes.data;
  } catch (e) {
    console.error("Failed to fetch files:", e);
  }
}

async function fetchWhitelist() {
  try {
    const res = await axios.get("/api/whitelist");
    whitelist.value = res.data;
  } catch (e) {
    console.error("Failed to fetch whitelist:", e);
  }
}

function handleDrop(e: DragEvent) {
  e.preventDefault();
  dragOver.value = false;
  if (e.dataTransfer?.files) uploadFiles(e.dataTransfer.files);
}

function handleFileSelect(e: Event) {
  const input = e.target as HTMLInputElement;
  if (input.files) uploadFiles(input.files);
  input.value = "";
}

async function uploadFiles(files: FileList) {
  for (const file of Array.from(files)) {
    const formData = new FormData();
    formData.append("file", file);
    try {
      await axios.post("/api/upload", formData);
    } catch (e: any) {
      showToast(e.response?.data?.error || "Upload failed", "error");
    }
  }
  await fetchFiles();
  await fetchStats();
}

async function deleteFile(filename: string) {
  const confirmed = await showConfirm({
    title: "Delete File",
    message: `Delete "${filename}"?`,
    confirmText: "Delete",
  });
  if (!confirmed) return;
  try {
    await axios.delete(`/api/files/${filename}`);
    await fetchFiles();
    await fetchStats();
  } catch (e) {
    console.error("Failed to delete:", e);
  }
}

async function deleteOutput(filename: string) {
  const confirmed = await showConfirm({
    title: "Delete Disavow File",
    message: `Delete "${filename}"? This action cannot be undone.`,
    confirmText: "Delete",
  });
  if (!confirmed) return;
  try {
    await axios.delete(`/api/outputs/${filename}`);
    await fetchFiles();
    await fetchStats();
  } catch (e) {
    console.error("Failed to delete output:", e);
  }
}

async function processFiles(skipNewDomainsCheck: boolean = false) {
  processing.value = true;
  lastResult.value = null;
  try {
    const res = await axios.post("/api/process");
    const result: ProcessResult = res.data;

    const hasNewEntries = result.new_entries && (result.new_entries.domains > 0 || result.new_entries.ips > 0);
    if (!skipNewDomainsCheck && result.success && hasNewEntries) {
      newEntriesModal.value = {
        show: true,
        domains: result.new_entries!.list.domains,
        ips: result.new_entries!.list.ips,
        pendingResult: result,
      };
    } else {
      lastResult.value = result;
    }
    await fetchFiles();
    await fetchStats();
  } catch (e: any) {
    lastResult.value = { success: false, error: e.response?.data?.error || "Processing failed" };
  }
  processing.value = false;
}

async function handleNewEntriesSkip() {
  lastResult.value = newEntriesModal.value.pendingResult;
  newEntriesModal.value = { show: false, domains: [], ips: [], pendingResult: null };
}

async function handleNewEntriesWhitelist(items: string[]) {
  for (const item of items) {
    await axios.post("/api/whitelist/add", { domain: item });
  }
  await fetchWhitelist();

  if (newEntriesModal.value.pendingResult?.filename) {
    try {
      await axios.delete(`/api/outputs/${newEntriesModal.value.pendingResult.filename}`);
    } catch (e) {
      console.error("Failed to delete output:", e);
    }
  }

  newEntriesModal.value = { show: false, domains: [], ips: [], pendingResult: null };

  await processFiles(true);
}

async function addDomain() {
  if (!newDomain.value.trim()) return;
  try {
    await axios.post("/api/whitelist/add", { domain: newDomain.value });
    newDomain.value = "";
    await fetchWhitelist();
    await fetchStats();
  } catch (e) {
    console.error("Failed to add domain:", e);
  }
}

async function removeDomain(domain: string) {
  const confirmed = await showConfirm({
    title: "Remove Domain",
    message: `Remove "${domain}"?`,
    confirmText: "Remove",
  });
  if (!confirmed) return;
  try {
    await axios.post("/api/whitelist", { domains: whitelist.value.filter((d) => d !== domain) });
    await fetchWhitelist();
    await fetchStats();
  } catch (e) {
    console.error("Failed to remove domain:", e);
  }
}

async function openPreview(filename: string) {
  try {
    const res = await axios.get(`/api/preview/${filename}`);
    previewContent.value = res.data.content;
    previewFile.value = filename;
  } catch (e) {
    console.error("Failed to fetch preview:", e);
  }
}

function closePreview() {
  previewContent.value = "";
  previewFile.value = "";
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString();
}

onMounted(() => fetchFiles());
</script>
