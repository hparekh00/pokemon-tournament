import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8080",
});

// export const getBattleLogs = async () => {
//   try {
//     const response = await api.get("/battle-log/list");
//     console.log("calling battle-log/list")
//     return response.data;
//   } catch (error) {
//     console.error("Error fetching battle logs:", error);
//     throw error;
//   }
// };

export default api;
