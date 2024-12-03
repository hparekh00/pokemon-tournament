<template>
    <div class="start-menu">
      <h1>Pokémon Battle</h1>
      <ul>
        <li
          v-for="(option, index) in options"
          :key="index"
          :class="{ selected: index === selectedIndex }"
          @click="handleOptionClick(option)"
          @mouseover="updateIndex(index)"
        >
          <span v-if="index === selectedIndex">></span>
          {{ option }}
        </li>
      </ul>
    </div>
  </template>
  
  <script setup>
    import { ref, onMounted, onBeforeUnmount } from "vue";
    import { useRouter } from "vue-router";
    
    const options = ["Start", "Create Pokémon", "Quit"];
    const selectedIndex = ref(0);
    const router = useRouter();
    const menuSound = new Audio(require("@/assets/menu-sound.mp3"));

    // Check if the user is an admin from localStorage
    const userRole = localStorage.getItem("userRole");

    // Add the "View Battle Logs" option only if the user is admin
    if (userRole === "admin") {
      // options.push("View Battle Logs");
      options.splice(2, 0, "View Battle Logs"); // adding this option right before Quit option
    }

    const playMenuSound = () => {
        menuSound
            .play()
            .then(() => {
                console.log("Menu sound started playing");
            })
            .catch((error) => {
                console.error("Error playing menu sound:", error);
            });
    };
  
    const handleKeydown = (event) => {
        if (event.key === "ArrowDown") {
            selectedIndex.value = (selectedIndex.value + 1) % options.length;
            playMenuSound();
        } else if (event.key === "ArrowUp") {
            selectedIndex.value = (selectedIndex.value - 1 + options.length) % options.length;
            playMenuSound();
        } else if (event.key === "Enter") {
            handleOptionClick(options[selectedIndex.value]);
            playMenuSound();
        }
    };
    
    const updateIndex = (index) => {
        selectedIndex.value = index;
        playMenuSound();
    };
    
    const handleOptionClick = (option) => {
        if (option === "Start") {
            startGame();
        } else if (option === "Create Pokémon") {
            openCreatePokemon();
        } else if (option === "Quit") {
            quitGame();
        } else if (option === "View Battle Logs") {
            openBattleLogs();
        }
    };
  
    const startGame = () => {
        router.push("/game");
    };
    
    const openCreatePokemon = () => {
        router.push("/create-pokemon")
    };
    
    const openBattleLogs = () => {
        router.push("/view-battle-logs")
    };

    const quitGame = () => {
        router.push("/")
    };
    
    onMounted(() => {
        window.addEventListener("keydown", handleKeydown);
    });
    
    onBeforeUnmount(() => {
        window.removeEventListener("keydown", handleKeydown);
        document.body.addEventListener("click", playMenuSound, { once: true });
    });
  </script>
  
  <style scoped>
    .start-menu {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        text-align: center;
        font-family: 'Press Start 2P', sans-serif;
    }
    
    ul {
        list-style: none;
        padding: 0;
    }
    
    li {
        padding: 10px;
        font-size: 1.5em;
        cursor: pointer;
    }
    
    li.selected {
        color: #6b8e23;
        font-weight: bold;
    }
    
    h1 {
        font-size: 4em;
    }
  </style>
  