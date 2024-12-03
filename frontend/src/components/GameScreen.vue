<template>
    <div class="game-screen" :class="{ 'quit-active': isQuitScreen }">
      <button class="quit-button" :disabled="!canClickStop" @click="goToStartMenu">STOP</button>

      <button class="sound-toggle" @click="toggleSound">
        <img :src="isMuted ? soundOffIcon : soundOnIcon"/>
      </button>
      
      <div class="battle-pokemon">
        <div class="team team1">
          <img
            v-if="props.pokemonSelected && props.selectedPokemon.team1.length > 0"
            v-for="(pokemon, index) in props.selectedPokemon.team1"
            :key="'team1-' + index"
            :src="getPokemonImage(pokemon)"
            :alt="pokemon"
            class="pokemon-image slide-in-left"
          />
        </div>
        <div class="team team2">
          <img
            v-if="props.pokemonSelected && props.selectedPokemon.team2.length > 0"
            v-for="(pokemon, index) in props.selectedPokemon.team2"
            :key="'team2-' + index"
            :src="getPokemonImage(pokemon)"
            :alt="pokemon"
            class="pokemon-image slide-in-right"
          />
        </div>
      </div>

      <div class="stats-container">
        <div
          class="pokemon-stats"
          v-if="props.selectedPokemon.team1[0]?.name && props.selectedPokemon.team1[0]?.hp"
        >
          <p><strong>{{ props.selectedPokemon.team1[0].name }}</strong></p>
          <p>HP: {{ pokemonCurrentHp[props.selectedPokemon.team1[0].name] || props.selectedPokemon.team1[0].hp }}</p>
        </div>
        <div
          class="pokemon-stats"
          v-if="props.selectedPokemon.team2[0]?.name && props.selectedPokemon.team2[0]?.hp"
        >
          <p><strong>{{ props.selectedPokemon.team2[0].name }}</strong></p>
          <p>HP: {{ pokemonCurrentHp[props.selectedPokemon.team2[0].name] || props.selectedPokemon.team2[0].hp }}</p>
        </div>
        <div
          class="pokemon-stats"
          v-if="props.selectedPokemon.team1[1]?.name && props.selectedPokemon.team1[1]?.hp"
        >
          <p><strong>{{ props.selectedPokemon.team1[1].name }}</strong></p>
          <p>HP: {{ pokemonCurrentHp[props.selectedPokemon.team1[1].name] || props.selectedPokemon.team1[1].hp }}</p>
        </div>
        <div
          class="pokemon-stats"
          v-if="props.selectedPokemon.team2[1]?.name && props.selectedPokemon.team2[1]?.hp"
        >
          <p><strong>{{ props.selectedPokemon.team2[1].name }}</strong></p>
          <p>HP: {{ pokemonCurrentHp[props.selectedPokemon.team2[1].name] || props.selectedPokemon.team2[1].hp }}</p>
        </div>
</div>

      <div class="battle-log">
        <div v-if="isLoading">Starting battle...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else>
          <p v-for="(log, index) in visibleLogs" :key="index">{{ log }}</p>
        </div>
      </div>

      <div v-if="isQuitScreen" class="quit-overlay">
        <button class="quit-button-overlay" @click="navigateToStart">Quit</button>
      </div>

      <!-- View Pokémon Info Button -->
      <button class="info-button" @click="fetchPokemonInfo">View Pokémon Info</button>

      <!-- Pokémon Info Overlay -->
      <div v-if="showPokemonInfo" class="info-overlay">
        <div class="info-overlay-content">
          <button class="close-button" @click="closePokemonInfo">Close</button>

          <!-- Loading indicator -->
          <div v-if="isLoading" class="loading-message">Loading Pokémon Info...</div>

          <!-- Pokémon Info -->
          <div v-else-if="pokemonList.length > 0">
            <div v-for="pokemon in pokemonList" :key="pokemon.name" class="pokemon-card">
              <h3>{{ pokemon.name }}</h3>
              <p><strong>HP:</strong> {{ pokemon.maxHp }}</p>
              <div>
                <h4>Attack Skills:</h4>
                <ul>
                  <li v-for="(damage, skill) in pokemon.attackSkills" :key="skill">
                    {{ skill }}: {{ damage }}
                  </li>
                </ul>
              </div>
              <div>
                <h4>Defense Skills:</h4>
                <ul>
                  <li v-for="(damage, skill) in pokemon.defenseSkills" :key="skill">
                    {{ skill }}: {{ damage }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Error Message -->
          <div v-else-if="error" class="error-message">{{ error }}</div>
        </div>
      </div>
    </div>
</template>

<script setup>
  import { ref, reactive, onBeforeUnmount, nextTick, defineProps, watch } from "vue";
  import { useRouter } from "vue-router";

  const pokemonCurrentHp = reactive({});
  const router = useRouter();
  let currentSong = null;
  const isMuted = ref(false);
  const battleLogs = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  let logInterval = null;
  const visibleLogs = ref([]);
  const isQuitScreen = ref(false);
  const canClickStop = ref(false);
  const showPokemonInfo = ref(false);
  const pokemonList = ref([]);

  const soundOnIcon = require('@/assets/sound-on.png');
  const soundOffIcon = require('@/assets/sound-off-background.png');

  const props = defineProps({
    selectedPokemon: {
      type: Object,
      required: true
    },
    pokemonSelected: {
      type: Boolean,
      required: true,
    },
    pokemonList: {
        type: Array,
        required: true,
    },
  });

  const songs = [
    require("@/assets/battle-1.wav"),
    require("@/assets/battle-2.wav"),
    require("@/assets/battle-3.wav"),
    require("@/assets/battle-4.wav"),
    require("@/assets/battle-5.wav")
  ];

  const fetchBattleLogs = async (battleId) => {
    try {
      const response = await fetch(`http://localhost:6035/battle/${battleId}`, {
        method: "GET",
        credentials: "include",
      });
      if (!response.ok) {
        throw new Error("Failed to fetch battle logs.");
      }
      const data = await response.json();
      battleLogs.value = data.events;
    } catch (err) {
      error.value = err.message;
    }
  };

  const fetchTournamentLogs = async (tournamentId) => {
    try {
      const response = await fetch(`http://localhost:6035/tournament/${tournamentId}`, {
        method: "GET",
        credentials: "include",
      });
      if (!response.ok) {
        throw new Error("Failed to fetch tournament logs.");
      }
      const data = await response.json();

      // Prepare a unified battle log
      battleLogs.value = []; // Reset battleLogs
      const battles = data.events.flatMap((round) => round.events);
      let hasShownWelcome = false;

        for (const battle of battles) {
          // Add "Welcome to the thunderdome!" only at the start of the first round
          if (!hasShownWelcome) {
            battleLogs.value.push("Welcome to the thunderdome!");
            hasShownWelcome = true;
          }

          // Add "Starting tournament round" message before each round
          battleLogs.value.push(`Starting tournament round ${battle.battle_id} with ${battle.loser} and ${battle.winner}`);

          // Fetch logs for each battle_id
          const battleId = battle.battle_id;
          const battleResponse = await fetch(`http://localhost:6035/battle/${battleId}`, {
            method: "GET",
            credentials: "include",
          });
          if (!battleResponse.ok) {
            throw new Error(`Failed to fetch battle logs for battle ${battleId}.`);
          }

          const battleData = await battleResponse.json();

          const filteredEvents = battleData.events.filter((log) => {
            if (log === "Welcome to the thunderdome!" && hasShownWelcome) {
              return false; // Skip the duplicate welcome message
            }
            return true;
          });

          // Add battle logs to the unified log
          battleLogs.value.push(...filteredEvents);

          // Add round winner message after each battle in the round
          battleLogs.value.push(`${battle.winner} has won round ${battle.battle_id}`);
      }

      // Final tournament winner message
      battleLogs.value.push(`${data.winner} has won the tournament!`);
    } catch (err) {
      error.value = err.message;
    }
  };

  const startBattle = async () => {
    try {
      isLoading.value = true;
      error.value = null;
      const seed = parseInt(localStorage.getItem("battleSeed"), 10)
      console.log("Using seed:", seed);

      Object.keys(pokemonCurrentHp).forEach((key) => {
      delete pokemonCurrentHp[key];
      
      });
      
      // Handle 2 pokemon (battle)
      if (props.selectedPokemon.team1.length + props.selectedPokemon.team2.length === 2) {
        const pokemon1 = props.selectedPokemon.team1[0];
        const pokemon2 = props.selectedPokemon.team1[1];

        console.log("pokemon1", pokemon1)
        console.log("pokemon2", pokemon2)

        const response = await fetch("http://localhost:6035/battle", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            pokemon1: pokemon1.name,
            pokemon2: pokemon2.name,
            // seed: Math.floor(Math.random() * 1000),
            seed
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to start the battle.");
        }

        const data = await response.json();

        // Swap team1[1] with team2[0] (image rendering thing)
        props.selectedPokemon.team2[0] = props.selectedPokemon.team1.pop();

        await fetchBattleLogs(data.battle_id);
      }

      // Handle 4 pokemon (tournament)
      else if (props.selectedPokemon.team1.length + props.selectedPokemon.team2.length === 4) {
        const allPokemon = [
          ...props.selectedPokemon.team1.map((p) => p.name),
          ...props.selectedPokemon.team2.map((p) => p.name),
        ];

        const response = await fetch("http://localhost:6035/tournament", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            participants: allPokemon,
            seed: Math.floor(Math.random() * 1000),
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to start the tournament.");
        }

        const data = await response.json();

         // Swap team1[1] with team2[0] (image rendering thing)
        const temp = props.selectedPokemon.team1[1];
        props.selectedPokemon.team1[1] = props.selectedPokemon.team2[0];
        props.selectedPokemon.team2[0] = temp;

        await fetchTournamentLogs(data.tournament_id);
      }

      setTimeout(() => {
        startLogDisplay();
        isLoading.value = false;
      }, 1000);
    } catch (err) {
      error.value = err.message;
      isLoading.value = false;
    }
  };

const startLogDisplay = () => {
  if (logInterval) {
    clearInterval(logInterval);
  }

  visibleLogs.value = []; // Reset visible logs before displaying
  let index = 0; // Start from the beginning of `battleLogs`

  logInterval = setInterval(() => {
    if (index < battleLogs.value.length) {
      const log = battleLogs.value[index];
      visibleLogs.value.push(log); // Add logs incrementally

      // Detect lines with damage information
      const damagePattern = /(\w+) has received (\d+) damage, remaining hp is (\d+)/;
      const match = log.match(damagePattern);

      if (match) {
        const [, name, , currentHp] = match; // Extract Pokémon name and current HP
        pokemonCurrentHp[name] = currentHp; // Update the reactive HP map
      }

      index++;
    } else {
      clearInterval(logInterval); // Stop the interval when all logs are displayed
      canClickStop.value = true;
    }
  }, 300); // Delay per log
};


  const defaultImage = {
  Pikachu: require("@/assets/pikachu.png"),
  Bulbasaur: require("@/assets/bulbasaur.png"),
  Charmander: require("@/assets/charmander.png"),
  Squirtle: require("@/assets/squirtle.png"),
  Snorlax: require("@/assets/snorlax.png"),
  Ditto: require("@/assets/ditto.png"),
  Mew: require("@/assets/mew.png"),
  Geodude: require("@/assets/geodude.png"),
  Jigglypuff: require("@/assets/jigglypuff.png"),
  Butterfree: require("@/assets/butterfree.png"),
  Abra: require("@/assets/abra.png"),
  Lapras: require("@/assets/lapras.png"),
};


  const getPokemonImage = (pokemon) => {
    if (!pokemon || !pokemon.name) {
      return require("@/assets/ditto.png");
    }

    return defaultImage[pokemon.name] || require("@/assets/ditto.png");
  };

  const goToStartMenu = () => {
    battleLogs.value.push("stop acknowledged");
    battleLogs.value.push("simulation terminated");
    visibleLogs.value.push("stop acknowledged");
    visibleLogs.value.push("simulation terminated");
    isQuitScreen.value = true;
  };

  const navigateToStart = () => {
    router.push("/start");
  };

  const fetchPokemonInfo = async () => {
    isLoading.value = true;
    error.value = null;

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
        name: pokemon.name,
        maxHp: pokemon["max hp"],
        attackSkills: pokemon["attack skills"],
        defenseSkills: pokemon["defense skills"],
      }));
    } catch (err) {
      error.value = err.message;
    } finally {
      isLoading.value = false;
      showPokemonInfo.value = true;
    }
  };

  const closePokemonInfo = () => {
    showPokemonInfo.value = false;
  };

  const playRandomSong = () => {
    if (currentSong) {
      currentSong.pause();
      currentSong.currentTime = 0;
    }

    const randomIndex = Math.floor(Math.random() * songs.length);
    currentSong = new Audio(songs[randomIndex]);
    currentSong.loop = true;
    currentSong.volume = 0.5;

    if (!isMuted.value) {
      currentSong.play();
    }
  };

  const toggleSound = () => {
    isMuted.value = !isMuted.value;
    if (isMuted.value) {
      currentSong.pause();
    } else {
      currentSong.play();
    }
  };

  const triggerAnimations = () => {
    nextTick(() => {
      const images = document.querySelectorAll(".pokemon-image");
      images.forEach((img) => {
        img.classList.add("visible");
      });
    });

    playRandomSong();
  };

  watch(
  () => props.pokemonSelected,
    async (newValue) => {
      if (newValue) {
        await startBattle(); 
        await nextTick();
        triggerAnimations();
      }
    },
    { immediate: true }
  );

  watch(
    () => props.selectedPokemon,
    (newValue) => {
      if (newValue.team1 && newValue.team2) {
        pokemon1.value = newValue.team1[0] || { name: "N/A", hp: "N/A" };
        pokemon2.value = newValue.team2[0] || { name: "N/A", hp: "N/A" };
      }
    },
    { immediate: true }
  );

  watch(
    () => props.pokemonSelected,
    (newValue) => {
      if (newValue) {
        canClickStop.value = false;
        startLogDisplay(); 
      }
    },
    { immediate: true }
  );

  onBeforeUnmount(() => {
    if (currentSong) {
      currentSong.pause();
      currentSong.currentTime = 0;
    }
    if (logInterval) {
      clearInterval(logInterval);
    }
  });

</script>
  
<style scoped>
  .game-screen {
    display: flex;
    flex-direction: column;
    height: 100vh;
    position: relative;
    justify-content: flex-end;
  }
  
  .battle-field {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .quit-button {
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

  .pokemon-stats {
    background-color: #eee;
    width: 15%;
    border: 1px solid #ccc;
    border-radius: 3px;
    text-align: center;
    box-shadow: 2px 5px 5px;
    font-family: 'Press Start 2P', sans-serif;
    margin: 1%;
  }

  .battle-pokemon {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1%;
    padding-bottom: 4%;
    margin-top: auto;
  }

  .stats-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    position: absolute;
    top: 20vh; /* distance from battle log */
    left: 0;
    right: 0;
    padding: 0 20px;
    z-index: 10;
  }

  .team {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0 7vw;
  }

  .pokemon-image {
    width: 10vw; /* pokemon size */
    height: auto;
    margin-bottom: 1.5vh;
    opacity: 0;
    transform: translateY(50px);
    transition: transform 1s ease-out, opacity 1s ease-out;
  }
/* Team 1 Pokémon - Slide-in from left, flipped */
  .pokemon-image.slide-in-left {
    transform: translateX(-100%) translateY(0) scaleX(-1);
  }

  .team1 .pokemon-image:last-child.slide-in-left {
    transform: translateX(-110%) translateY(10px) scaleX(-1);
  }

  /* Team 2 Pokémon - Slide-in from right, default orientation */
  .pokemon-image.slide-in-right {
    transform: translateX(100%) translateY(0);
  }

  .team2 .pokemon-image:last-child.slide-in-right {
    transform: translateX(110%) translateY(10px);
  }

  /* Team 1 Pokémon - Final Position */
  .team1 .pokemon-image.visible {
    opacity: 1;
    transform: translateX(0) translateY(0) scaleX(-1);
  }

  .team1 .pokemon-image:last-child.visible {
    transform: translateX(-50%) translateY(10px) scaleX(-1);
  }

  /* Team 2 Pokémon - Final Position */
  .team2 .pokemon-image.visible {
    opacity: 1;
    transform: translateX(0) translateY(0);
  }

  .team2 .pokemon-image:last-child.visible {
    transform: translateX(50%) translateY(10px);
  }

  .sound-toggle {
    position: absolute;
    top: 10px;
    left: 10px;
    background: none;
    border: none;
    cursor: pointer;
  }

  .sound-toggle img {
    width: 30px;
    height: 30px;
  }

  .battle-log {
    background-color: #333;
    color: #fff;
    padding: 10px;
    font-family: "Courier New", Courier, monospace;
    height: 43vh;
    overflow-y: auto;
    width: 100%;
    box-sizing: border-box;
    pointer-events: auto;
    z-index: 10;
  }

  .quit-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8); 
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    pointer-events: none;
  }

  .quit-overlay .quit-button-overlay {
    pointer-events: auto; 
  }

  .quit-button-overlay {
    background-color: #6b8e23;
    color: white;
    border: none;
    padding: 20px 40px;
    font-family: 'Press Start 2P', sans-serif;
    font-size: 20px;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s ease;
  }

  .quit-button-overlay:hover {
    background-color: #556b2f;
  }

  .quit-button-overlay:active {
    transform: scale(0.95);
  }

  body {
    overflow: hidden;
  }

  .game-screen.quit-active > *:not(.battle-log):not(.quit-overlay .quit-button-overlay) {
    pointer-events: none;
  }

  .quit-button:disabled {
    color: gray;
    cursor: not-allowed;
  }

  .loading-message {
    font-size: 18px;
    color: #333;
    text-align: center;
    font-family: 'Press Start 2P', sans-serif;
  }

  .info-button {
    position: absolute;
    bottom: 45vh;
    right: 10px;
    background-color: #6b8e23;
    color: white;
    border: none;
    padding: 10px 20px;
    font-family: 'Press Start 2P', sans-serif;
    font-size: 14px;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s ease;
    z-index: 100;
  }

  .info-button:hover {
    background-color: #556b2f;
  }

  .info-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
  }

  .info-overlay-content {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    width: 80%;
    max-height: 90%;
    overflow-y: auto;
    font-family: 'Press Start 2P', sans-serif;
  }

  .pokemon-card {
    margin-bottom: 20px;
    padding: 15px;
    border: 1px solid #ccc;
    border-radius: 10px;
    background-color: #f9f9f9;
  }

  .pokemon-card h3 {
    margin-top: 0;
    color: #333;
  }

  .close-button {
    display: block;
    margin: 0 auto 20px;
    background-color: #6b8e23;
    color: white;
    border: none;
    padding: 10px 20px;
    font-family: 'Press Start 2P', sans-serif;
    font-size: 14px;
    cursor: pointer;
    border-radius: 5px;
    transition: background-color 0.3s ease;
  }

  .close-button:hover {
    background-color: #556b2f;
  }
  
</style>