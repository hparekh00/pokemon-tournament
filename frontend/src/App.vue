<template>
  <div id="app">
    <RouterView 
      :selectedPokemon="selectedPokemon"
      :pokemonSelected="pokemonSelected"
      :pokemonList="pokemonList"
      @updatePokemonList="handleUpdatePokemonList"
    />
    <PokemonSelectionScreen
      v-if="showSelectionScreen"
      :pokemonList="pokemonList"
      @close="handleSelectionClose"
    />
  </div>
</template>

<script setup>
  import { ref, watch, onMounted } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import PokemonSelectionScreen from "@/components/PokemonSelectionScreen.vue";

  const selectedPokemon = ref({
    team1: [],
    team2: [],
  });
  const showSelectionScreen = ref(false);
  const pokemonSelected = ref(false);
  const pokemonList = ref([]);
  const route = useRoute();
  const router = useRouter();

  const defaultPokemon = [
  { name: "Pikachu", hp: 25 },
  { name: "Bulbasaur", hp: 25 },
  { name: "Charmander", hp: 25 },
  { name: "Squirtle", hp: 25 },
  { name: "Snorlax", hp: 40 },
  { name: "Ditto", hp: 35 },
  { name: "Mew", hp: 25 },
  { name: "Geodude", hp: 25 },
  { name: "Jigglypuff", hp: 25 },
  { name: "Butterfree", hp: 40 },
  { name: "Abra", hp: 25 },
  { name: "Lapras", hp: 25 },
];


  watch(
    () => route.name,
    (newRouteName) => {
      if (newRouteName === "GameScreen") {
        showSelectionScreen.value = true;
        pokemonSelected.value = false;
      } else {
        showSelectionScreen.value = false;
      }
    }
  );

  const handleSelectionClose = (selection) => {
      if (selection) {
          selectedPokemon.value.team1 = selection.team1.map((name) =>
              pokemonList.value.find((pokemon) => pokemon.name === name)
          );
          selectedPokemon.value.team2 = selection.team2.map((name) =>
              pokemonList.value.find((pokemon) => pokemon.name === name)
          );
          console.log("Selected Seed:", selection.seed);
          console.log("Updated selectedPokemon:", selectedPokemon.value);

          pokemonSelected.value = true;
      }
      showSelectionScreen.value = false;
  };

  onMounted(() => {
    localStorage.clear(); //keep an eye on this. could be a problem child
    const storedList = JSON.parse(localStorage.getItem("pokemonList"));
    if (!storedList || storedList.length === 0) {
      localStorage.setItem("pokemonList", JSON.stringify(defaultPokemon));
      pokemonList.value = defaultPokemon;
    } else {
      pokemonList.value = storedList;
    }
    if (router.currentRoute.value.path === "/") {
      router.push("/");
    }
  });

  const handleUpdatePokemonList = (updatedList) => {
    pokemonList.value = updatedList;
    localStorage.setItem("pokemonList", JSON.stringify(updatedList));
  };

</script>