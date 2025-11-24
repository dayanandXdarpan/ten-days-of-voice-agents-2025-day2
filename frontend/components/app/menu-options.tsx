'use client';

import { motion, AnimatePresence } from 'motion/react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/livekit/button';

const MotionDiv = motion.create('div');

interface MenuOption {
  label: string;
  value: string;
  category: string;
}

interface MenuOptionsProps {
  options: MenuOption[];
  onOptionSelect: (value: string) => void;
  className?: string;
}

const MENU_DATA = {
  drinks: [
    'Espresso',
    'Americano',
    'Latte',
    'Cappuccino',
    'Mocha',
    'Macchiato',
    'Flat White',
    'Cortado',
    'Cold Brew',
    'Iced Coffee',
  ],
  sizes: ['Small', 'Medium', 'Large'],
  milk: ['Whole Milk', 'Skim Milk', 'Oat Milk', 'Almond Milk', 'Soy Milk', 'Coconut Milk'],
  extras: [
    'Extra Shot',
    'Whipped Cream',
    'Caramel Drizzle',
    'Chocolate Syrup',
    'Vanilla Syrup',
    'Hazelnut Syrup',
    'Cinnamon',
    'Honey',
  ],
  payment: ['Cash on Delivery', 'Card', 'UPI', 'Google Pay', 'PhonePe', 'Paytm'],
};

export function MenuOptions({ options, onOptionSelect, className }: MenuOptionsProps) {
  if (options.length === 0) {
    return null;
  }

  const category = options[0]?.category || 'options';

  return (
    <AnimatePresence>
      <MotionDiv
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2 }}
        className={cn('bg-card/80 backdrop-blur-sm border-border rounded-lg border p-4', className)}
      >
        <h4 className="text-muted-foreground mb-3 text-xs font-semibold uppercase tracking-wide">
          Quick Select - {category}
        </h4>
        <div className="flex flex-wrap gap-2">
          {options.map((option) => (
            <Button
              key={option.value}
              variant="outline"
              size="sm"
              onClick={() => onOptionSelect(option.value)}
              className="bg-background/50 hover:bg-accent hover:text-accent-foreground text-xs transition-colors"
            >
              {option.label}
            </Button>
          ))}
        </div>
      </MotionDiv>
    </AnimatePresence>
  );
}

export function detectMenuCategory(agentMessage: string): MenuOption[] {
  const message = agentMessage.toLowerCase();

  // Detect drink type questions
  if (
    message.includes('what type') ||
    message.includes('what coffee') ||
    message.includes('latte, cappuccino') ||
    message.includes('which drink')
  ) {
    return MENU_DATA.drinks.map((drink) => ({
      label: drink,
      value: drink.toLowerCase(),
      category: 'Drinks',
    }));
  }

  // Detect size questions
  if (message.includes('what size') || message.includes('small, medium, or large')) {
    return MENU_DATA.sizes.map((size) => ({
      label: size,
      value: size.toLowerCase(),
      category: 'Sizes',
    }));
  }

  // Detect milk questions
  if (
    message.includes('what milk') ||
    message.includes('milk would you like') ||
    message.includes('oat, almond')
  ) {
    return MENU_DATA.milk.map((milk) => ({
      label: milk,
      value: milk.toLowerCase(),
      category: 'Milk Options',
    }));
  }

  // Detect extras questions
  if (
    message.includes('add anything') ||
    message.includes('extra') ||
    message.includes('whipped cream')
  ) {
    return MENU_DATA.extras.map((extra) => ({
      label: extra,
      value: extra.toLowerCase(),
      category: 'Extras',
    }));
  }

  // Detect payment questions
  if (message.includes('how would you like to pay') || message.includes('payment')) {
    return MENU_DATA.payment.map((payment) => ({
      label: payment,
      value: payment.toLowerCase(),
      category: 'Payment Methods',
    }));
  }

  return [];
}

