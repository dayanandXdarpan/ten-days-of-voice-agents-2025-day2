import { useState, useEffect } from 'react';
import { type ReceivedChatMessage } from '@livekit/components-react';

interface OrderDetails {
  drink_type?: string;
  size?: string;
  milk?: string;
  extras?: string[];
  name?: string;
  delivery_address?: string;
  payment_method?: string;
  total_price?: number;
  order_id?: string;
}

const DRINK_KEYWORDS = [
  'espresso',
  'americano',
  'latte',
  'cappuccino',
  'mocha',
  'macchiato',
  'flat white',
  'cortado',
  'cold brew',
  'iced coffee',
];

const SIZE_KEYWORDS = ['small', 'medium', 'large'];

const MILK_KEYWORDS = [
  'whole milk',
  'skim milk',
  'oat milk',
  'almond milk',
  'soy milk',
  'coconut milk',
  'whole',
  'skim',
  'oat',
  'almond',
  'soy',
  'coconut',
];

const EXTRAS_KEYWORDS = [
  'extra shot',
  'whipped cream',
  'caramel drizzle',
  'chocolate syrup',
  'vanilla syrup',
  'hazelnut syrup',
  'cinnamon',
  'honey',
];

const PAYMENT_KEYWORDS = [
  'cash on delivery',
  'cash',
  'card',
  'upi',
  'google pay',
  'phonepe',
  'paytm',
];

function extractOrderDetails(messages: ReceivedChatMessage[]): OrderDetails {
  const details: OrderDetails = {
    extras: [],
  };

  // Helper: normalize a single message text by coalescing spelled-out letters
  // (e.g. "D a y a n a n d" -> "Dayanand") and fixing common mis-words
  function normalizeText(raw: string) {
    if (!raw) return raw;
    // simple replacements for frequent mis-transcriptions
    const replacements: Record<string, string> = {
      '\n': ' ',
      'jungson': 'junction',
      'jungtion': 'junction',
      'cats on delivery': 'cash on delivery',
      'cast on delivery': 'cash on delivery',
      'cast on': 'cash on',
    };

    let t = raw.trim();
    // lowercase copy for replacements but keep original case when returning where needed
    let lower = t.toLowerCase();
    for (const [k, v] of Object.entries(replacements)) {
      if (lower.includes(k)) {
        lower = lower.replace(new RegExp(k, 'g'), v);
      }
    }

    // coalesce runs of single-letter tokens into a single word (robust to punctuation)
    const parts = lower.split(/\s+/).filter(Boolean);
    const outParts: string[] = [];
    let run: string[] = [];
    for (let p of parts) {
      // strip non-letter chars for detection (but keep original letters for final assembly)
      const cleaned = p.replace(/[^a-z]/g, '');
      if (cleaned.length === 1) {
        run.push(cleaned);
        continue;
      }
      // flush run if it is long enough to be a spelled-out name/word
      if (run.length >= 3) {
        outParts.push(run.join(''));
      } else if (run.length > 0) {
        outParts.push(...run);
      }
      run = [];
      // push current token (cleaned) to outParts
      outParts.push(cleaned || p);
    }
    if (run.length >= 3) outParts.push(run.join(''));

    // rebuild, collapse whitespace and trim
    const normalized = outParts.join(' ').replace(/\s+/g, ' ').trim();
    return normalized;
  }

  // Scan messages newest -> oldest so later corrections override earlier mentions
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    const raw = msg.message || '';
    const normalized = normalizeText(raw);
    const text = normalized.toLowerCase();
    const isAgent = !msg.from?.isLocal;
    const isUser = !!msg.from?.isLocal;

    // detect if this message is explicitly a correction (strong override)
    const correctionRegex = /(^|\b)(no[, ]|actually[, ]|i meant|i mean|change to|rather|instead|sorry[, ]|make it|make that)\b/i;
    const isCorrection = correctionRegex.test(text);

    // Extract order id from any message; prefer the most recent found
    const foundOrderId =
      raw.match(/order\s*id\s*(?:is|:)\s*([A-Z0-9\-]+)/i) || raw.match(/\b([A-Z]{2,}-\d{8}-\d{1,})\b/);
    if (foundOrderId && foundOrderId[1]) {
      details.order_id = foundOrderId[1];
    }

    // Extract drink type (allow correction to override)
    if (!details.drink_type || isCorrection) {
      for (const drink of DRINK_KEYWORDS) {
        if (text.includes(drink)) {
          details.drink_type = drink
            .split(' ')
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
            .join(' ');
          break;
        }
      }
    }

    // Extract size
    if (!details.size || isCorrection) {
      for (const size of SIZE_KEYWORDS) {
        if (text.includes(size)) {
          details.size = size;
          break;
        }
      }
    }

    // Extract milk
    if (!details.milk || isCorrection) {
      for (const milk of MILK_KEYWORDS) {
        if (text.includes(milk)) {
          details.milk = milk.includes('milk') ? milk : `${milk} milk`;
          break;
        }
      }
    }

    // Extract extras (can be multiple). If correction, prefer current message
    for (const extra of EXTRAS_KEYWORDS) {
      if (text.includes(extra) && !details.extras?.includes(extra)) {
        details.extras?.push(extra);
      }
    }

    // If correction phrase present and this message negates an extra, remove it
    if (isCorrection) {
      // e.g. "no whipped cream" -> remove whipped cream
      for (const extra of EXTRAS_KEYWORDS) {
        const negRegex = new RegExp(`\\bno\\s+${extra.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')}\\b`, 'i');
        if (negRegex.test(text) && details.extras?.includes(extra)) {
          details.extras = details.extras?.filter((e) => e !== extra) || [];
        }
      }
    }

    // Extract payment method
    if (!details.payment_method || isCorrection) {
      for (const payment of PAYMENT_KEYWORDS) {
        if (text.includes(payment)) {
          details.payment_method = payment
            .split(' ')
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
            .join(' ');
          break;
        }
      }
    }

    // Extract name (look for patterns like "my name is X" or standalone/coalesced names)
    if (!details.name || isCorrection) {
      let nameMatch = text.match(/(?:name is|i'm|im)\s+([a-z][a-z\s]{0,40})/i);
      if (nameMatch && nameMatch[1]) {
        const nm = nameMatch[1].trim();
        details.name = nm
          .split(/\s+/)
          .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
          .join(' ');
      } else {
        // fallback: if the message is short and looks like a name (or coalesced spelled letters), accept it
        const words = text.split(/\s+/).filter(Boolean);
        const candidate = words.join(' ');
        // accept candidate if short-ish and alphabetic
        if (candidate && candidate.length >= 2 && candidate.length <= 40 && /^[a-z ]+$/.test(candidate)) {
          // filter out common short words that aren't names
          const invalid = /\b(please|thanks|thank|hello|hi|yes|no|ok|okay|then|on)\b/;
          if (!invalid.test(candidate) && words.length <= 4) {
            details.name = candidate
              .split(/\s+/)
              .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
              .join(' ');
          }
        }
      }
    }

    // Extract address (look for patterns with street, road, area)
    if (!details.delivery_address || isCorrection) {
      if (
        text.includes('street') ||
        text.includes('road') ||
        text.includes('avenue') ||
        text.includes('near') ||
        text.length > 20
      ) {
        if (/\d+/.test(text) || text.includes('near') || text.includes('apartment') || text.includes('junction')) {
          details.delivery_address = normalized; // use normalized text
        }
      }
    }
  }

  // Extract total price from agent messages
  const lastMessages = messages.slice(-10); // Check last 10 messages
  for (const msg of lastMessages.reverse()) {
    const text = msg.message;
    const priceMatch = text.match(/\$(\d+\.\d{2})/);
    if (priceMatch) {
      details.total_price = parseFloat(priceMatch[1]);
      break;
    }
    // Also try to detect order id in recent agent messages in case it appears later
    if (!details.order_id) {
      const orderIdMatch = msg.message.match(/order\s*id\s*(?:is|:)\s*([A-Z0-9\-]+)/i) || msg.message.match(/\b([A-Z]{2,}-\d{8}-\d{1,})\b/);
      if (orderIdMatch && orderIdMatch[1]) {
        details.order_id = orderIdMatch[1];
      }
    }
  }

  return details;
}

export function useOrderDetails(messages: ReceivedChatMessage[]) {
  const [orderDetails, setOrderDetails] = useState<OrderDetails>({
    extras: [],
  });

  useEffect(() => {
    const details = extractOrderDetails(messages);
    // Generate or reuse a shared order id when order looks final
    const isFinal = !!details.drink_type && !!details.size;
    try {
      const storageKey = 'murf_current_order_id';
      const existing = sessionStorage.getItem(storageKey);

      // If backend or agent provided an order_id in messages, prefer and persist it
      if (details.order_id) {
        if (existing !== details.order_id) {
          sessionStorage.setItem(storageKey, details.order_id);
        }
      } else if (isFinal) {
        // If final and no backend order id, reuse or generate a local one
        if (existing) {
          details.order_id = existing;
        } else if (typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function') {
          const bytes = crypto.getRandomValues(new Uint8Array(6));
          const id = Array.from(bytes).map((b) => (b % 36).toString(36)).join('').toUpperCase();
          sessionStorage.setItem(storageKey, id);
          details.order_id = id;
        }
      } else {
        // If not final, remove any lingering order id so a new one can be generated later
        // Keep it if you prefer persistent across session: comment out the next line
        // sessionStorage.removeItem(storageKey);
      }
    } catch (e) {
      // ignore storage/crypto errors
    }
    setOrderDetails(details);
  }, [messages]);

  return orderDetails;
}

