export async function askGemini(prompt) {
  const apiKey = process.env.GEMINI_API_KEY;

  const resp = await fetch(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-live:generateContent",
    {
      method: "POST",
      headers: {
        "x-goog-api-key": apiKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [{ text: prompt }],
          },
        ],
      }),
    }
  );

  const data = await resp.json();

  if (data.error) {
    console.error("Gemini error:", data.error);
    return "El Espíritu Santo se distrajo… intenta de nuevo 🙏😂";
  }

  return data.candidates?.[0]?.content?.parts?.[0]?.text || "Amén 🙏😄";
}
