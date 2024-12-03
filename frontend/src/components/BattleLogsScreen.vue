<template>
  <button class="quit-button" @click="goToStartMenu">STOP</button>

  <div class="battle-logs">
    <div class="battle-log">
      <div v-if="isLoading">Starting battle...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <p v-else>
        <ul>
          <li v-for="(log, index) in visibleLogs" :key="index">{{ log }}</li>
        </ul>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const isLoading = ref(false);
const error = ref(null);
const visibleLogs = ref([]);

const fetchBattleLogs = async () => {
  isLoading.value = true;
  try {
    const response = await fetch(`http://localhost:6035/adminLogs`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Failed to fetch battle logs.");
    }

    const data = await response.json();
    console.log(data);
    visibleLogs.value = data.events || []; // Ensure a fallback to an empty array
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
};

// Lifecycle hook to fetch logs on mount
onMounted(() => {
  fetchBattleLogs();
});


const goToStartMenu = () => {
  router.push("/start");
};

</script>

<style scoped>
.battle-log {
  background-color: inherit;
  color: #333;
  padding: 10px;
  font-family: "Courier New", Courier, monospace;
  height: 900px;
  overflow-y: auto;
  width: 100%;
  box-sizing: border-box;
}

.quit-button {
  background-color: inherit;
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 0.9em;
  color: #333;
  border: none;
  background: none;
  cursor: pointer;
}

.quit-button:hover {
  color: #6B8E23;
}
</style>