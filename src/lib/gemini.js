export class GeminiService {
    constructor() {
        // Prioridad: 1. LocalStorage (Usuario) 2. Variable de Entorno (Vercel)
        this.apiKey = localStorage.getItem("arca_ai_key") || import.meta.env.VITE_GEMINI_API_KEY || "";
        this.history = [];
        this.model = "gemini-2.5-flash";

        this.personas = {
            reformado: "Actúa como un teólogo reformado experto. Cita a Calvino, Sproul y la Confesión de Westminster. Enfatiza la soberanía de Dios, la gracia irresistible y las doctrinas de la gracia. Tono académico pero pastoral.",
            puritano: "Actúa como un puritano inglés del siglo XVII. Cita a John Owen, Richard Baxter y John Bunyan. Enfatiza la piedad práctica, la santidad del corazón, la meditación y la comunión íntima con Dios. Usa un tono solemne, fervoroso y profundamente espiritual.",
            bautista: "Actúa como un teólogo bautista conservador. Cita a Spurgeon, Piper y la Confesión de Londres de 1689. Enfatiza el bautismo de creyentes y la autonomía de la iglesia local. Tono firme y bíblico.",
            pentecostal: "Actúa como un teólogo pentecostal centrado en la Biblia. Cita referencias sobre el Espíritu Santo y la experiencia viva de la fe. Equilibra el fervor espiritual con el rigor bíblico.",
            academico: "Actúa como un erudito bíblico riguroso. Analiza el contexto histórico-cultural, griego y hebreo. Evita sesgos denominacionales. Tono objetivo y educativo.",
            pastoral: "Actúa como un pastor consejero sabio y compasivo. Usa lenguaje sencillo y cálido. Enfócate en el consuelo y la aplicación práctica para la vida diaria.",
            neofito: "Actúa como un mentor cristiano para alguien nuevo en la fe. Usa lenguaje muy simple, evita jerga teológica compleja. Céntrate en las verdades universales del Evangelio (amor de Dios, perdón, salvación en Jesús) que unen a todos los cristianos."
        };
    }

    setApiKey(key) {
        this.apiKey = key;
        localStorage.setItem("arca_ai_key", key);
    }

    getPersonaPrompt(type) {
        return this.personas[type] || this.personas.neofito;
    }

    async sendMessage(message, personaType = "neofito", context = "") {
        if (!this.apiKey) throw new Error("API_KEY_MISSING");

        const systemInstruction = this.getPersonaPrompt(personaType);
        const finalPrompt = `
      CONTEXTO DEL USUARIO (Notas/Lectura actual):
      "${context.substring(0, 5000)}" 
      
      INSTRUCCIÓN DE CONTROL:
      ${systemInstruction}

      PREGUNTA DEL USUARIO:
      ${message}
    `;

        try {
            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/${this.model}:generateContent?key=${this.apiKey}`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        contents: [
                            {
                                parts: [{ text: finalPrompt }],
                            },
                        ],
                    }),
                }
            );

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error.message || "Error en Gemini API");
            }

            const data = await response.json();
            const answer = data.candidates[0].content.parts[0].text;

            this.history.push({ role: "user", text: message });
            this.history.push({ role: "model", text: answer });

            return answer;
        } catch (error) {
            console.error("Gemini Error:", error);
            throw error;
        }
    }
}

export const aiService = new GeminiService();
