<template>
    <div class="create-pokemon-screen">
      <h1>Create a New Pokémon</h1>
      <form @submit.prevent="addPokemonToDatabase">
        <label>
          Name:
          <input type="text" v-model="name" placeholder="Enter Pokémon Name" />
        </label>
        <label>
          HP:
          <input type="number" v-model="hp" placeholder="Enter HP Value" />
        </label>

        <!-- Attack Skills -->
        <fieldset>
          <legend>Attack Skills</legend>
          <div v-for="(skill, index) in attackSkills" :key="'attack-' + index" class="skill-row">
            <input
              type="text"
              v-model="skill.name"
              placeholder="Skill Name"
            />
            <input
              type="number"
              v-model="skill.damage"
              placeholder="Damage"
            />
            <button type="button" @click="removeAttackSkill(index)">Remove</button>
          </div>
          <button type="button" @click="addAttackSkill">Add Attack Skill</button>
        </fieldset>

        <!-- Defense Skills -->
        <fieldset>
          <legend>Defense Skills</legend>
          <div v-for="(skill, index) in defenseSkills" :key="'defense-' + index" class="skill-row">
            <input
              type="text"
              v-model="skill.name"
              placeholder="Skill Name"
            />
            <input
              type="number"
              v-model="skill.damage"
              placeholder="Damage"
            />
            <button type="button" @click="removeDefenseSkill(index)">Remove</button>
          </div>
          <button type="button" @click="addDefenseSkill">Add Defense Skill</button>
        </fieldset>
        
        <div class="button-container">
          <button class="menu-button" type="submit">Create</button>
          <button class="menu-button" @click="goBack">Cancel</button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </template>  
  
<script setup>
  import { ref, defineEmits } from "vue";
  import { useRouter } from "vue-router";
  
  const name = ref("");
  const hp = ref("");
  const attackSkills = ref([]);
  const defenseSkills = ref([]);
  const error = ref(null);
  const success = ref(null);
  const router = useRouter();
  const emit = defineEmits(["updatePokemonList"]);

  const addAttackSkill = () => {
    attackSkills.value.push({ name: "", damage: null });
  };

  const removeAttackSkill = (index) => {
    attackSkills.value.splice(index, 1);
  };

  const addDefenseSkill = () => {
    defenseSkills.value.push({ name: "", damage: null });
  };

  const removeDefenseSkill = (index) => {
    defenseSkills.value.splice(index, 1);
  };

  const addPokemonToDatabase = async () => {
    if (!name.value || !hp.value || isNaN(hp.value) || hp.value <= 0) {
      error.value = "Please enter a valid pokemon name and HP.";
      return;
    }

    //add to local storage as well
    const newPokemon = {
      name: name.value.trim(),
      hp: parseInt(hp.value, 10),
      image: require("@/assets/ditto.png")
    };
  
    const pokemonList = JSON.parse(localStorage.getItem("pokemonList"));
    if (pokemonList.some(p => p.name.toLowerCase() === name.value.toLowerCase())) {
        error.value = "A Pokémon with this name already exists!";
        return;
    }
    pokemonList.push(newPokemon);
    localStorage.setItem("pokemonList", JSON.stringify(pokemonList));
    emit("updatePokemonList", pokemonList);

    try {
      const response = await fetch("http://localhost:6035/pokemon", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          name: name.value.trim(),
          max_hp: parseInt(hp.value, 10),
          image: "@/assets/ditto.png",
          attack_skills: Object.fromEntries(
            attackSkills.value.map((skill) => [skill.name, skill.damage])
          ),
          defense_skills: Object.fromEntries(
            defenseSkills.value.map((skill) => [skill.name, skill.damage])
          ),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to add pokemon to the database.");
      }

      success.value = `Pokemon ${name.value} added successfully!`;
      error.value = null;
      router.push("/start");
    } catch (err) {
      error.value = err.message;
      success.value = null;
    }
  };
  
  const goBack = () => {
    error.value = null;
    router.push("/start");
  };
</script>
  
<style scoped>
    .create-pokemon-screen {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        font-family: 'Press Start 2P', sans-serif;
        padding-top: 20%;
    }

    form {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    label {
        margin-bottom: 10px;
    }

    input {
        font-family: 'Press Start 2P', sans-serif;
        font-size: 14px;
        margin-left: 10px;
    }
    
    fieldset {
      border: 2px solid #6b8e23;
      padding: 10px;
      margin: 15px 0;
      width: 100%;
    }

    legend {
      font-family: "Press Start 2P", sans-serif;
      font-size: 16px;
      color: #6b8e23;
    }

    .skill-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
    }

    .button-container {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }

    .menu-button {
        background-color: #6b8e23;
        color: white;
        border: none;
        padding: 10px 20px;
        font-family: 'Press Start 2P', sans-serif;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .menu-button:hover {
        background-color: #98c379;
    }

    .menu-button:active {
        transform: scale(0.95);
    }

    .menu-button:focus {
        outline: 2px solid #ffffff;
        outline-offset: 4px;
    }

    .error {
        color: red;
        margin-top: 10px;
    }
</style>
