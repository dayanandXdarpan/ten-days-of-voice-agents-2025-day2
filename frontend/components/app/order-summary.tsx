"use client";

import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

type OrderDetails = {
  drink_type?: string;
  size?: string;
  milk?: string;
  extras?: string[];
  name?: string;
  delivery_address?: string;
  payment_method?: string;
  total_price?: number;
  order_id?: string;
};

interface OrderSummaryProps {
  orderDetails: OrderDetails;
  className?: string;
}

export function OrderSummary({ orderDetails, className }: OrderSummaryProps) {
  const hasAnyDetails = Object.values(orderDetails).some((val) => {
    if (val === undefined || val === null) return false;
    if (Array.isArray(val)) return val.length > 0;
    if (typeof val === "string") return val.trim().length > 0;
    if (typeof val === "number") return true;
    return true;
  });

  if (!hasAnyDetails) return null;
  // Order ID: prefer orderDetails.order_id (shared) otherwise fall back to local generation
  const [orderId, setOrderId] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // If a shared order id is present on orderDetails, use it
    if (orderDetails.order_id) {
      setOrderId(orderDetails.order_id);
      return;
    }

    const isFinal = !!orderDetails.drink_type && !!orderDetails.size;
    if (isFinal && !orderId) {
      try {
        const hasCrypto = typeof crypto !== 'undefined' && typeof crypto.getRandomValues === 'function';
        if (!hasCrypto) return;
        const bytes = crypto.getRandomValues(new Uint8Array(6));
        const id = Array.from(bytes).map((b) => (b % 36).toString(36)).join('').toUpperCase();
        setOrderId(id);
      } catch (e) {
        // ignore; leave orderId null
      }
    }
  }, [orderDetails, orderId]);

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className={cn(
        'bg-card/80 border-border rounded-lg border p-4 shadow-lg backdrop-blur-sm',
        className
      )}
    >
      <h3 className='text-foreground mb-3 text-sm font-semibold tracking-wide uppercase'>📋 Your Order</h3>

      <div className="space-y-2 text-sm">
        {orderDetails.drink_type && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">• Drink:</span>
            <span className="text-foreground font-medium">{orderDetails.drink_type}</span>
          </div>
        )}

        {orderDetails.size && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">📏 Size:</span>
            <span className="text-foreground font-medium capitalize">{orderDetails.size}</span>
          </div>
        )}

        {orderDetails.milk && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">🥛 Milk:</span>
            <span className="text-foreground font-medium capitalize">{orderDetails.milk}</span>
          </div>
        )}

        {orderDetails.extras && orderDetails.extras.length > 0 && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">✨ Extras:</span>
            <span className="text-foreground font-medium">{orderDetails.extras.join(", ")}</span>
          </div>
        )}

        {orderDetails.name && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">👤 Name:</span>
            <span className="text-foreground font-medium">{orderDetails.name}</span>
          </div>
        )}

        {orderDetails.delivery_address && (
          <div className="flex flex-col gap-1">
            <span className="text-muted-foreground">📍 Address:</span>
            <span className="text-foreground text-xs font-medium">{orderDetails.delivery_address}</span>
          </div>
        )}

        {orderDetails.payment_method && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">💳 Payment:</span>
            <span className="text-foreground font-medium">{orderDetails.payment_method}</span>
          </div>
        )}

        {typeof orderDetails.total_price === "number" && orderDetails.total_price > 0 && (
          <div className="border-border mt-3 flex justify-between border-t pt-2">
            <span className="text-foreground font-semibold">💰 Total:</span>
            <span className="text-foreground text-lg font-bold">${orderDetails.total_price.toFixed(2)}</span>
          </div>
        )}

        {/* Order ID and copy button */}
        {orderId && (
          <div className="mt-3 flex items-center justify-between gap-3 border-t pt-3">
            <div className="flex items-center gap-3">
              <span className="text-muted-foreground text-xs">🔖 Order ID</span>
              <span className="font-mono text-sm font-semibold">{orderId}</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(orderId);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  } catch (e) {
                    // fallback
                    void navigator.clipboard?.writeText(orderId).catch(() => {});
                  }
                }}
                className="rounded-md bg-primary px-3 py-1 text-sm text-primary-foreground"
              >
                {copied ? 'Copied' : 'Copy'}
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

