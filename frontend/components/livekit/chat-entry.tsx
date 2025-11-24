import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ChatEntryProps extends React.HTMLAttributes<HTMLLIElement> {
  /** The locale to use for the timestamp. */
  locale: string;
  /** The timestamp of the message. */
  timestamp: number;
  /** The message to display. */
  message: string;
  /** The origin of the message. */
  messageOrigin: 'local' | 'remote';
  /** The sender's name. */
  name?: string;
  /** Whether the message has been edited. */
  hasBeenEdited?: boolean;
}

export const ChatEntry = ({
  name,
  locale,
  timestamp,
  message,
  messageOrigin,
  hasBeenEdited = false,
  className,
  ...props
}: ChatEntryProps) => {
  const time = new Date(timestamp);
  const title = time.toLocaleTimeString(locale, { timeStyle: 'full' });

  const initials = name
    ? name
        .split(' ')
        .map((p) => p[0])
        .slice(0, 2)
        .join('')
        .toUpperCase()
    : messageOrigin === 'local'
    ? 'You'
    : 'AG';

  return (
    <li
      title={title}
      data-lk-message-origin={messageOrigin}
      className={cn('group flex w-full flex-col gap-2', className)}
      {...props}
    >
      <div className={cn('flex items-end gap-3', messageOrigin === 'local' ? 'justify-end' : 'justify-start')}>
        {/* Avatar */}
        <div
          className={cn(
            'flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold',
            messageOrigin === 'local' ? 'order-2 bg-primary text-primary-foreground' : 'order-1 bg-muted/60 text-muted-foreground'
          )}
          aria-hidden
        >
          {initials}
        </div>

        <div className={cn(messageOrigin === 'local' ? 'order-1 text-right' : 'order-2 text-left', 'max-w-[70%]') }>
          <div className="flex items-baseline gap-2">
            {name ? <strong className="text-sm">{name}</strong> : <span className="text-sm font-medium opacity-80">{messageOrigin === 'local' ? 'You' : 'Assistant'}</span>}
            <time className="ml-2 text-xs text-muted-foreground" dateTime={time.toISOString()}>{time.toLocaleTimeString(locale, { timeStyle: 'short' })}</time>
          </div>

          <div
            className={cn(
              'mt-1 rounded-2xl text-sm leading-relaxed wrap-break-word p-3 shadow-sm relative z-60',
              messageOrigin === 'local'
                ? 'bg-accent text-accent-foreground ml-auto'
                : 'bg-card text-foreground mr-auto'
            )}
          >
            {message}
          </div>
        </div>
      </div>
    </li>
  );
};

