// ui/vue3/static/js/MountPoints/__main__.ts

import { createApp, reactive } from "vue";
import App from "../App.vue";

function parseBase64Data(elementId: string): any {
  const element = document.getElementById(elementId);
  if (element) {
    try {
      const content = element.textContent || "";
      return JSON.parse(atob(content.trim()));
    } catch (e) {
      console.error(`Failed to parse ${elementId}:`, e);
      return {};
    }
  }
  return {};
}

function parseJsonData(elementId: string): any {
  const element = document.getElementById(elementId);
  if (element) {
    try {
      const content = element.textContent || "";
      return JSON.parse(content.trim());
    } catch (e) {
      console.error(`Failed to parse ${elementId}:`, e);
      return "";
    }
  }
  return "";
}

const initialStats = parseBase64Data("data-stats");
const initialWhitelist = parseBase64Data("data-whitelist");
const username = parseJsonData("data-username");

const appState = reactive({
  stats: initialStats,
  whitelist: initialWhitelist,
  username: username,
});

const app = createApp(App);

app.provide("appState", appState);

app.mount("#app-root");
