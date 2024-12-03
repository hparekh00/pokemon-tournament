<template>
    <div class="login-screen">
      <h1>Login</h1>
      <form @submit.prevent="handleLogin">
        <label>
          Username:
          <input type="text" v-model="username" placeholder="Enter Username" />
        </label>
        <label>
          Password:
          <input type="password" v-model="password" placeholder="Enter Password" />
        </label>
        <button type="submit">Login</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import { useRouter } from "vue-router";
  
  const username = ref("");
  const password = ref("");
  const error = ref(null);
  const router = useRouter();

  const handleLogin = async () => {
    error.value = null;

    try {
      console.log("Attempting login with:", { username: username.value, password: password.value });
      const response = await fetch("http://localhost:6035/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ username: username.value.trim(), password: password.value })
      });

      if (!response.ok) {
        const result = await response.json();
        console.error("Login failed:", result.error);
        throw new Error(result.error || "Login failed");
      }

      //Add the username to local storage for check in StartMenu
      localStorage.setItem("userRole", username.value.trim());

      router.push("/start");
    } catch (err) {
      error.value = err.message;
    }
  };
  </script>
  
  <style scoped>
  .login-screen {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background-color: #f5f5dc;
    font-family: "Press Start 2P", sans-serif;
    text-align: center;
  }
  
  form {
    display: flex;
    flex-direction: column;
  }
  
  label {
    margin-bottom: 10px;
  }
  
  input {
    padding: 5px;
    font-size: 1em;
    margin-top: 5px;
  }
  
  button {
    margin-top: 10px;
    padding: 10px 20px;
    background-color: #6b8e23;
    color: #fff;
    border: none;
    cursor: pointer;
    font-family: "Press Start 2P", sans-serif;
    text-transform: uppercase;
  }
  
  button:hover {
    background-color: #556b2f;
  }
  
  .error {
    color: red;
    margin-top: 10px;
  }
  </style>
  