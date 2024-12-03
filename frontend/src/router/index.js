import { createRouter, createWebHistory } from "vue-router";

import StartMenu from "../components/StartMenu.vue";
import GameScreen from "../components/GameScreen.vue";
import CreatePokemonScreen from "@/components/CreatePokemonScreen.vue";
import LoginScreen from "@/components/LoginScreen.vue";
import BattleLogsScreen from "@/components/BattleLogsScreen.vue";

const routes = [
  { path: "/", name: "LoginScreen", component: LoginScreen },
  { path: "/start", name: "StartMenu", component: StartMenu },
  { path: "/game", name: "GameScreen", component: GameScreen },
  { path: "/view-battle-logs", name: "BattleLogs", component: BattleLogsScreen },
  { path: "/create-pokemon", name: "CreatePokemonScreen", component: CreatePokemonScreen }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router
