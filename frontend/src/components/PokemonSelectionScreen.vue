<template>
  <div class="modal">
    <div class="modal-content">
      <h2>Select Your Pokémon to Battle</h2>

      <div v-if="isLoading">Loading Pokémon...</div>
      <div v-else>
        <div class="teams">
          <div class="team-row">
            <div v-for="(pokemon, index) in localTeam1" :key="'team1-' + index">
              <select v-model="localTeam1[index]">
                <option value="" disabled>Select Pokémon</option>
                <option v-for="p in pokemonList" :key="p._id" :value="p.name">
                  {{ p.name }}
                </option>
              </select>
            </div>
          </div>

          <div v-if="showExtraDropdowns" class="team-row">
            <div v-for="(pokemon, index) in localTeam2" :key="'team2-' + index">
              <select v-model="localTeam2[index]">
                <option value="" disabled>Select Pokémon</option>
                <option v-for="p in pokemonList" :key="p._id" :value="p.name">
                  {{ p.name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Optional Seed Input -->
        <div class="seed-container">
          <label for="seed-input">Optional Seed:</label>
          <input
            id="seed-input"
            type="number"
            v-model="seed"
            placeholder="Enter seed (optional)"
          />
        </div>

        <div class="extra-buttons">
          <button v-if="!showExtraDropdowns" @click="addExtraDropdowns">
            Add Two More Pokémon
          </button>
          <button v-if="showExtraDropdowns" @click="removeExtraDropdowns">
            Remove Extra Pokémon
          </button>
        </div>

        <button @click="confirmSelection">Confirm</button>
        <p v-if="error" class="error">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
    import { ref, onMounted } from "vue";

    const pokemonList = ref([]);
    const localTeam1 = ref(["", ""]); 
    const localTeam2 = ref(["", ""]);
    const isLoading = ref(true);
    const error = ref(null);
    const emit = defineEmits(["close"]);
    const showExtraDropdowns = ref(false);
    const seed = ref("");

    const fetchPokemon = async () => {
      try {
        const response = await fetch("http://localhost:6035/pokemon", {
          method: "GET",
          credentials: "include", 
        });

        if (!response.ok) {
          throw new Error("Failed to fetch Pokémon data.");
        }

        const data = await response.json();
        pokemonList.value = data.map((pokemon) => ({
          _id: pokemon._id,
          name: pokemon.name,
          maxHp: pokemon["max hp"],
          image: pokemon.image,
          attackSkills: pokemon["attack skills"],
          defenseSkills: pokemon["defense skills"],
        }));

        console.log("pokemonList.value", pokemonList.value);

        localTeam1.value = [pokemonList.value[0].name, pokemonList.value[1].name];
        localTeam2.value = [pokemonList.value[2].name, pokemonList.value[3].name];

        console.log("localTeam1.value", localTeam1.value);
        console.log("localTeam2.value", localTeam2.value);
      } catch (err) {
        error.value = err.message;
      } finally {
        isLoading.value = false;
      }
    };

    const addExtraDropdowns = () => {
      showExtraDropdowns.value = true;
    };

    const removeExtraDropdowns = () => {
      showExtraDropdowns.value = false;
      localTeam2.value = ["", ""];
    };

    const confirmSelection = () => {
      const team1 = localTeam1.value.filter((name) => name !== "");
      const team2 = showExtraDropdowns.value ? localTeam2.value.filter((name) => name !== "") : [];

      if (team1.length < 2) {
        error.value = "Please select at least two Pokémon.";
        return;
      }

      if (showExtraDropdowns.value && team2.length < 2) {
        error.value = "Please select two more Pokémon or remove the extra Pokémon.";
        return;
      }

      const seedValue = seed.value || Math.floor(Math.random() * 1000);
      localStorage.setItem("battleSeed", seedValue);
      console.log("Seed saved:", seedValue);

      emit("close", {
        team1,
        team2, // Empty array if extra Pokémon are not selected
        seed: seedValue // Use user-provided or random seed
      });
    };

    onMounted(fetchPokemon);
</script>
  
<style scoped>
  .modal {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 10;
  }

  .modal-content {
      background: white;
      padding: 20px;
      border-radius: 10px;
      text-align: center;
      font-family: 'Press Start 2P', sans-serif;
  }

  .teams {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    padding-top: 4%;
  }

  .team-row {
    display: flex;
    justify-content: center;
    gap: 20px;
  }

  .extra-buttons {
    margin: 20px 0;
  }

  label {
    font-size: 14px;
    margin-bottom: 5px;
  }

  select {
    padding: 5px;
    font-size: 1em;
    font-family: "Press Start 2P", sans-serif;
  }

  button {
    padding: 10px 20px;
    margin-top: 20px;
    font-size: 1em;
    cursor: pointer;
    background-color: #6B8E23;
    color: white;
    border: none;
    border-radius: 5px;
    font-family: 'Press Start 2P', sans-serif;
  }

  button:hover {
    background-color: #556B2F;
  }

  .seed-container {
    margin: 15px 0;
  }

  .seed-container label {
    font-family: "Press Start 2P", sans-serif;
    font-size: 12px;
    margin-right: 10px;
  }

  .seed-container input {
    padding: 5px;
    font-size: 1em;
    font-family: "Press Start 2P", sans-serif;
    width: 100px;
    text-align: center;
  }
</style>
