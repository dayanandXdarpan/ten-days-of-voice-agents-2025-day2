'use client';

import { AnimatePresence, type HTMLMotionProps, motion } from 'motion/react';
import { type ReceivedChatMessage } from '@livekit/components-react';
import { ChatEntry } from '@/components/livekit/chat-entry';

const MotionContainer = motion.create('div');
const MotionChatEntry = motion.create(ChatEntry);

// Motion props may include easing values that the motion/react types are
// stricter about. Cast to `any` to avoid type incompatibilities while
// preserving the runtime behavior.
const CONTAINER_MOTION_PROPS: any = {
  variants: {
    hidden: {
      opacity: 0,
      transition: {
        // use a numeric cubic-bezier easing to satisfy TS types
        ease: [0.22, 1, 0.36, 1],
        duration: 0.3,
        staggerChildren: 0.1,
        staggerDirection: -1,
      },
    },
    visible: {
      opacity: 1,
      transition: {
        delay: 0.2,
        ease: [0.22, 1, 0.36, 1],
        duration: 0.3,
        staggerDelay: 0.2,
        staggerChildren: 0.1,
        staggerDirection: 1,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

const MESSAGE_MOTION_PROPS: any = {
  variants: {
    hidden: {
      opacity: 0,
      y: 10,
    },
    visible: {
      opacity: 1,
      y: 0,
    },
  },
};

interface ChatTranscriptProps {
  hidden?: boolean;
  messages?: ReceivedChatMessage[];
}

export function ChatTranscript({
  hidden = false,
  messages = [],
  ...props
}: ChatTranscriptProps & Omit<HTMLMotionProps<'div'>, 'ref'>) {
  return (
    <AnimatePresence>
      {!hidden && (
        <MotionContainer {...CONTAINER_MOTION_PROPS} {...props}>
          {messages.map(({ id, timestamp, from, message, editTimestamp }: ReceivedChatMessage) => {
            const locale = navigator?.language ?? 'en-US';
            const messageOrigin = from?.isLocal ? 'local' : 'remote';
            const hasBeenEdited = !!editTimestamp;

            return (
              <MotionChatEntry
                key={id}
                locale={locale}
                timestamp={timestamp}
                message={message}
                messageOrigin={messageOrigin}
                hasBeenEdited={hasBeenEdited}
                // ensure each entry animates to visible in case parent animation didn't run
                initial="hidden"
                animate="visible"
                transition={{ duration: 0.18, ease: [0.22, 1, 0.36, 1] }}
                variants={MESSAGE_MOTION_PROPS.variants}
              />
            );
          })}
        </MotionContainer>
      )}
    </AnimatePresence>
  );
}

