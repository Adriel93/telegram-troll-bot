import { getMemory, saveMemory } from "../lib/memory";
import { askGemini } from "../lib/gemini";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(200).json({ message: "Bot OK" });
  }

  try {
    const body = req.body;

    if (!body.message || !body.message.text) {
      return res.status(200).send("no message");
    }

    const chatId = body.message.chat.id;
    const userMessage = body.message.text;

    // Load memory for this user
    const memory = await getMemory(chatId);

    const fullPrompt = `
Eres un BOT cristiano troll, gracioso, a veces sarcástico pero NUNCA ofensivo.
Responde con humor, pero con fundamento bíblico y cariño.

Memoria del usuario:
${JSON.stringify(memory)}

Mensaje del usuario:
"${userMessage}"

Responde de forma graciosa, breve y cristiana:
`;

    const aiResponse = await askGemini(fullPrompt);

    // Save memory (store last 10 messages)
    const newMemory = [...(memory || []), { user: userMessage, bot: aiResponse }];
    if (newMemory.length > 10) newMemory.shift();
    await saveMemory(chatId, newMemory);

    // Reply to Telegram
    const telegramToken = process.env.TELEGRAM_BOT_TOKEN;
    await fetch(`https://api.telegram.org/bot${telegramToken}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: aiResponse,
      }),
    });

    res.status(200).send("OK");
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
}
