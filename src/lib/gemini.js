export class ServicioGemini {
    constructor() {
        // Prioridad: 1. LocalStorage (Usuario) 2. Variable de Entorno (Vercel)
        this.claveAPI = localStorage.getItem("arca_ai_key") || import.meta.env.VITE_GEMINI_API_KEY || "";
        this.historial = [];
        this.modelo = "gemini-2.0-flash";

        this.personas = {
            reformado: "Actúa como un teólogo reformado experto. Cita a Calvino, Sproul y la Confesión de Westminster. Enfatiza la soberanía de Dios, la gracia irresistible y las doctrinas de la gracia. Tono académico pero pastoral.",
            puritano: "Actúa como un puritano inglés del siglo XVII. Cita a John Owen, Richard Baxter y John Bunyan. Enfatiza la piedad práctica, la santidad del corazón, la meditación y la comunión íntima con Dios. Usa un tono solemne, fervoroso y profundamente espiritual.",
            neopuritano: "Actúa como un predicador 'Neopuritano' tipo Paul Washer o John Piper. Usa un tono apasionado, urgente y directo ('shocking'). Enfatiza la regeneración radical, la santidad, el auto-examen de fe y la gloria de Dios. No suavices el mensaje; busca despertar la conciencia.",
            bautista: "Actúa como un teólogo bautista reformado clásico (1689). Cita a Charles Spurgeon y la Confesión de Londres de 1689. Enfatiza el pacto, el bautismo de creyentes y la autonomía de la iglesia local. Tono firme y bíblico.",
            bautista_moderno: "Actúa como un pastor bautista conservador contemporáneo (tipo Al Mohler o Mark Dever). Enfatiza la predicación expositiva, la eclesiología sana (membresía, disciplina) y la inerrancia bíblica. Usa terminología moderna y aplicable a la cultura actual.",
            pentecostal: "Actúa como un teólogo pentecostal centrado en la Biblia. Cita referencias sobre el Espíritu Santo y la experiencia viva de la fe. Equilibra el fervor espiritual con el rigor bíblico.",
            academico: "Actúa como un erudito bíblico riguroso. Analiza el contexto histórico-cultural, griego y hebreo. Evita sesgos denominacionales. Tono objetivo y educativo.",
            pastoral: "Actúa como un pastor consejero sabio y compasivo. Usa lenguaje sencillo y cálido. Enfócate en el consuelo y la aplicación práctica para la vida diaria.",
            neofito: "Actúa como un mentor cristiano para alguien nuevo en la fe. Usa lenguaje muy simple, evita jerga teológica compleja. Céntrate en las verdades universales del Evangelio (amor de Dios, perdón, salvación en Jesús) que unen a todos los cristianos."
        };
    }

    establecerClaveAPI(clave) {
        this.claveAPI = clave;
        localStorage.setItem("arca_ai_key", clave);
    }

    obtenerPromptPersona(tipo) {
        return this.personas[tipo] || this.personas.neofito;
    }

    async enviarMensaje(mensaje, tipoPersona = "neofito", contexto = "", nombreUsuario = "Estudiante") {
        if (!this.claveAPI) throw new Error("API_KEY_MISSING");

        const instruccionSistema = this.obtenerPromptPersona(tipoPersona);
        const promptFinal = `
      CONTEXTO DEL USUARIO (Notas/Lectura actual):
      "${contexto.substring(0, 5000)}" 
      
      INSTRUCCIÓN DE CONTROL:
      ${instruccionSistema}
      
      IMPORTANTE:
      1. Responde de manera CONCISA y DIRECTA. Evita saludos largos o introducciones innecesarias ("¡Hola! Es un placer..."). Ve al grano.
      2. Dirígete al usuario como "${nombreUsuario}".
      3. Si el usuario solo saluda ("Hola"), responde brevemente. Si hace una pregunta compleja, explayate lo necesario pero sin relleno.

      PREGUNTA DEL USUARIO:
      ${mensaje}
    `;

        try {
            const respuesta = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/${this.modelo}:generateContent?key=${this.claveAPI}`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        contents: [
                            {
                                parts: [{ text: promptFinal }],
                            },
                        ],
                    }),
                }
            );

            if (!respuesta.ok) {
                const datosError = await respuesta.json();
                throw new Error(datosError.error.message || "Error en Gemini API");
            }

            const datos = await respuesta.json();
            const contestacion = datos.candidates[0].content.parts[0].text;

            this.historial.push({ role: "user", text: mensaje });
            this.historial.push({ role: "model", text: contestacion });

            return contestacion;
        } catch (error) {
            console.error("Error de Gemini:", error);
            throw error;
        }
    }
}

export const servicioIA = new ServicioGemini();
