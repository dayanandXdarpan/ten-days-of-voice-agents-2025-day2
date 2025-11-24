import { useEffect } from 'react';
import { type AgentState, useRoomContext, useVoiceAssistant } from '@livekit/components-react';
import { toastAlert } from '@/components/livekit/alert-toast';

function isAgentAvailable(agentState: AgentState) {
  return agentState == 'listening' || agentState == 'thinking' || agentState == 'speaking';
}

export function useConnectionTimeout(timout?: number) {
  // Allow overriding the timeout via a client-side env var for development
  const envTimeout = typeof process !== 'undefined' && process.env.NEXT_PUBLIC_CONNECTION_TIMEOUT_MS
    ? Number(process.env.NEXT_PUBLIC_CONNECTION_TIMEOUT_MS)
    : undefined;

  const timeoutMs = timout ?? envTimeout ?? 20_000;

  const room = useRoomContext();
  const { state: agentState } = useVoiceAssistant();

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (!isAgentAvailable(agentState)) {
        const reason =
          agentState === 'connecting'
            ? 'Agent did not join the room. '
            : 'Agent connected but did not complete initializing. ';

        toastAlert({
          title: 'Session ended',
          description: (
            <p className="w-full">
              {reason}
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://docs.livekit.io/agents/start/voice-ai/"
                className="whitespace-nowrap underline"
              >
                See quickstart guide
              </a>
              .
            </p>
          ),
        });

        // Only disconnect when running a real session — for development you can
        // bump `NEXT_PUBLIC_CONNECTION_TIMEOUT_MS` to avoid premature disconnects.
        try {
          room.disconnect();
        } catch (err) {
          // ignore disconnect errors in dev
          // eslint-disable-next-line no-console
          console.warn('room.disconnect() failed', err);
        }
      }
    }, timout);

    return () => clearTimeout(timeout);
  }, [agentState, room, timeoutMs]);
}
