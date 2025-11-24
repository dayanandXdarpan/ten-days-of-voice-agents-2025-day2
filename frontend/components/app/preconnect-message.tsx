'use client';

import { AnimatePresence, motion } from 'motion/react';
import { type ReceivedChatMessage } from '@livekit/components-react';
// Use a solid high-contrast text span here for legibility on dark backgrounds
import { cn } from '@/lib/utils';

const MotionMessage = motion.create('p');

// Cast to `any` because Framer Motion's `Variants` typing is strict about
// the `transition.ease` shape. We keep the runtime behavior but avoid a
// compile-time type error during `next build`.
const VIEW_MOTION_PROPS: any = {
  variants: {
    visible: {
      opacity: 1,
      transition: {
        // numeric cubic-bezier for ease-in
        ease: [0.42, 0, 1, 1],
        duration: 0.5,
        delay: 0.8,
      },
    },
    hidden: {
      opacity: 0,
      transition: {
        ease: [0.42, 0, 1, 1],
        duration: 0.5,
        delay: 0,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

interface PreConnectMessageProps {
  messages?: ReceivedChatMessage[];
  className?: string;
}

export function PreConnectMessage({ className, messages = [] }: PreConnectMessageProps) {
  return (
    <AnimatePresence>
      {messages.length === 0 && (
        <MotionMessage
          {...VIEW_MOTION_PROPS}
          aria-hidden={messages.length > 0}
          className={cn('pointer-events-none text-center relative z-50', className)}
        >
          <span className="inline-block text-center text-lg sm:text-xl md:text-2xl font-semibold text-white drop-shadow-lg leading-snug bg-black/60 px-4 py-2 rounded-md">
            Agent is listening, ask it a question
          </span>
        </MotionMessage>
      )}
    </AnimatePresence>
  );
}

